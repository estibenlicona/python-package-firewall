import httpx
import logging
from typing import Any
from fastapi import HTTPException
from src.domain.rules_engine import RulesEngine
from src.utils.parsing import extract_version_from_filename
from src.config import settings

logger = logging.getLogger(__name__)

class PyPIProxyService:
    """
    Servicio que hace proxy al índice PEP 503 de PyPI,
    filtrando paquetes según las reglas de negocio.
    """
    def __init__(self) -> None:
        self.rules_engine = RulesEngine()
        self.upstream_base = settings.pypi_upstream_url
        self.local_base = settings.proxy_base_url
        self.url_cache: dict[str, str] = {}
        self.block_reasons: dict[str, list[str]] = {}  # package -> [reasons]

    async def get_filtered_index(self, package: str) -> dict[str, Any]:
        """
        Obtiene el índice PEP 503 del paquete desde PyPI usando JSON (PEP 691).
        Devuelve el índice completo sin filtrar - la validación se hace en el momento
        de la descarga para mayor eficiencia.
        """
        url = f"{self.upstream_base}/{package}/"
        logger.info(f"Forwarding request to PyPI: {url}")
        
        headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 404:
                    logger.warning(f"Package {package} not found on PyPI")
                    raise HTTPException(status_code=404, detail=f"Package {package} not found")
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error fetching {url}: {e}")
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
        
        data = response.json()
        files = data.get("files", [])
        
        # Solo reescribir URLs para que apunten a nuestro proxy
        # No hacemos validación aquí - se hará en stream_package()
        rewritten_files: list[dict[str, Any]] = []
        
        for file_info in files:
            filename = file_info.get("filename")
            url_real = file_info.get("url")
            
            if not filename or not url_real:
                continue
            
            # Guardar URL real en caché
            self.url_cache[filename] = url_real
            
            # Guardar URL para archivo .metadata si existe (PEP 658)
            if file_info.get("data-dist-info-metadata"):
                metadata_filename = f"{filename}.metadata"
                metadata_url = f"{url_real}.metadata"
                self.url_cache[metadata_filename] = metadata_url
            
            # Reescribir URL para que apunte a nuestro proxy
            file_copy = file_info.copy()
            file_copy["url"] = f"{self.local_base}/{filename}"
            rewritten_files.append(file_copy)
        
        logger.info(f"Package {package}: {len(rewritten_files)} files indexed")
        
        return {
            "meta": data.get("meta", {"api-version": "1.0"}),
            "name": package,
            "files": rewritten_files
        }

    async def stream_package(self, filename: str) -> tuple[httpx.Response, httpx.AsyncClient]:
        """
        Obtiene el archivo desde PyPI y retorna la respuesta HTTP completa junto con el cliente.
        VALIDACIÓN LAZY: Analiza la versión justo antes de permitir la descarga.
        Retorna tupla (Response, AsyncClient) para permitir cleanup después del streaming.
        """
        # Obtener URL real desde cache
        real_url = self.url_cache.get(filename)
        
        if not real_url:
            logger.warning(f"URL not in cache for {filename}, constructing standard URL")
            real_url = f"{settings.pypi_files_base_url}/{filename}"
        
        # Extraer package name y version del filename
        # Formato típico: package-version-py3-none-any.whl o package-version.tar.gz
        parts = filename.split("-")
        if len(parts) >= 2:
            package_name = parts[0]
            version = extract_version_from_filename(filename)
            
            if version and version != "unknown":
                logger.info(f"Validating {package_name} version {version} before download...")
                
                # VALIDACIÓN: Ejecutar análisis de seguridad
                decision = self.rules_engine.decide(package_name, version, ecosystem="pypi")
                
                if decision.status == "block":
                    # Guardar razón de bloqueo para auditoría
                    reason_msg = f"Version {version}: {decision.reason}"
                    if package_name not in self.block_reasons:
                        self.block_reasons[package_name] = []
                    if reason_msg not in self.block_reasons[package_name]:
                        self.block_reasons[package_name].append(reason_msg)
                    
                    # Log visual detallado en servidor
                    logger.error(f"""
{'='*80}
🚫 PACKAGE BLOCKED BY SECURITY POLICY
{'='*80}
Package: {package_name}
Version: {version}
Reason:  {decision.reason}
Details: {settings.proxy_base_url.replace('/pypi/packages', '')}/blocked/{package_name}
{'='*80}
                    """)
                    
                    # Formatear mensaje de error detallado para el cliente
                    error_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🚫 PACKAGE BLOCKED BY SECURITY POLICY                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Package: {package_name:<67} ║
║ Version: {version:<67} ║
║                                                                              ║
║ Reason:                                                                      ║
║ {decision.reason[:70]:<70} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ For full details, run:                                                       ║
║   curl {settings.proxy_base_url.replace('/pypi/packages', '')}/blocked/{package_name:<44} ║
║                                                                              ║
║ Or check firewall logs on your proxy server                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
                    """.strip()
                    
                    raise HTTPException(
                        status_code=403,
                        detail=error_message,
                        headers={
                            "X-Block-Reason": decision.reason[:200],
                            "X-Policy-Violation": "true",
                            "X-Blocked-Package": package_name,
                            "X-Blocked-Version": version
                        }
                    )
                
                logger.info(f"ALLOWED: {package_name} {version} - {decision.reason}")
        
        logger.info(f"Streaming {filename} from {real_url}")
        
        # Crear cliente HTTP persistente con keep-alive
        client = httpx.AsyncClient(timeout=60.0)
        
        try:
            # Hacer request sin context manager para mantener conexión abierta
            response = await client.get(real_url, follow_redirects=True)
            
            if response.status_code == 404:
                await client.aclose()
                logger.error(f"File {filename} not found at {real_url}")
                raise HTTPException(status_code=404, detail=f"File {filename} not found")
            
            response.raise_for_status()
            return response, client
            
        except httpx.HTTPStatusError as e:
            await client.aclose()
            logger.error(f"Error streaming {filename}: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            await client.aclose()
            raise
