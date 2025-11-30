from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from src.services.pypi_proxy_service import PyPIProxyService

app = FastAPI()
proxy = PyPIProxyService()

@app.get("/simple/", response_class=HTMLResponse)
async def pypi_simple_root():
    """
    Endpoint raíz del índice PEP 503.
    Devuelve HTML básico vacío para compatibilidad.
    """
    return "<html><body></body></html>"

@app.get("/simple/{package}/")
async def pypi_proxy(package: str):
    """
    Endpoint PEP 691 compatible para pip.
    Devuelve el índice completo - la validación se hace en el momento de descarga.
    """
    data = await proxy.get_filtered_index(package)
    
    return JSONResponse(
        content=data,
        media_type="application/vnd.pypi.simple.v1+json"
    )

@app.get("/blocked/{package}")
async def check_blocked_status(package: str) -> dict[str, str | int | list[str]]:
    """
    Endpoint de auditoría para consultar por qué un paquete fue bloqueado.
    Retorna detalles sobre las versiones bloqueadas y razones.
    """
    blocked_reasons = proxy.block_reasons.get(package)
    
    if not blocked_reasons:
        return {
            "package": package,
            "status": "not_blocked",
            "message": "This package has not been blocked or hasn't been requested yet."
        }
    
    return {
        "package": package,
        "status": "blocked",
        "blocked_versions": len(blocked_reasons),
        "reasons": blocked_reasons,
        "message": "All versions of this package are blocked by firewall policy."
    }

@app.get("/pypi/packages/{filename}")
async def download_package(filename: str):
    """
    Endpoint para descargar archivos .whl, .tar.gz y .metadata desde PyPI.
    Hace streaming transparente sin almacenar localmente.
    
    Flujo:
    1. pip solicita: GET /pypi/packages/<filename>
    2. Este endpoint valida con RulesEngine (lazy validation)
    3. Obtiene Response de PyPI con headers originales
    4. Hace streaming: PyPI → firewall → pip
    5. NO se almacena nada en disco
    """
    # Obtener Response de PyPI (ya validado por RulesEngine)
    response, client = await proxy.stream_package(filename)
    
    try:
        # Leer todo el contenido y cerrar la conexión inmediatamente
        content = await response.aread()
    finally:
        await client.aclose()
    
    # Extraer headers importantes de la respuesta original
    headers = {
        "content-disposition": f'attachment; filename="{filename}"',
    }
    
    # Preservar Content-Type original
    content_type = response.headers.get("content-type", "application/octet-stream")
    
    # Retornar contenido completo
    return Response(
        content=content,
        media_type=content_type,
        headers=headers
    )
