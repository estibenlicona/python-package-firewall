from typing import Any

from src.services.depsdev_client import DepsDevClient
from src.services.osv_client import OSVClient
from src.utils.parsing import extract_published_date, extract_spdx


class PackageInfoFetcher:
    """
    Servicio que recopila información de un paquete desde fuentes externas
    (deps.dev, OSV) para que el RulesEngine pueda tomar decisiones.
    """
    
    def __init__(self):
        self.depsdev = DepsDevClient()
        self.osv = OSVClient()

    def fetch_info(self, package: str, version: str | None = None, ecosystem: str = "pypi") -> dict[str, Any]:
        """
        Recopila información del paquete desde APIs externas.
        NO toma decisiones - solo obtiene datos.
        """
        # Info de la última versión
        latest_version = self.depsdev.get_latest_version(package, ecosystem)
        latest_published_at = None
        if latest_version:
            latest_published_at = latest_version.get("publishedAt")
        
        # Si no se especifica versión, usar la última
        if not version and latest_version:
            version = latest_version.get("version")
        
        # Info de la versión específica
        info = self.depsdev.get_version_info(package, ecosystem, version)
        if not info:
            return {"error": "Package or version not found"}
        
        # Licencia
        license_details = info.get("licenseDetails", [])
        spdx = extract_spdx(license_details)
        
        # Fecha de publicación
        published_at_value = info.get("publishedAt")
        published_at = extract_published_date(published_at_value) if isinstance(published_at_value, str) else None
        
        # Vulnerabilidades
        vulns: list[str] = []
        if version:
            vulns = self.osv.get_vulnerabilities(package, ecosystem, version)
        
        return {
            "package": package,
            "version": version,
            "published_at": published_at,
            "spdx": spdx,
            "latest_version": latest_version,
            "latest_published_at": latest_published_at,
            "vulnerabilities": vulns
        }
