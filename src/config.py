from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno o archivo .env
    Todos los valores DEBEN estar definidos en el archivo .env
    """
    # PyPI Proxy
    pypi_upstream_url: str = Field(...)
    pypi_files_base_url: str = Field(...)
    proxy_base_url: str = Field(...)
    proxy_host: str = Field(...)
    proxy_port: int = Field(...)
    
    # External APIs
    depsdev_api_url: str = Field(...)
    osv_api_url: str = Field(...)
    
    # Security Policies
    maintenance_window_years: int = Field(...)
    enable_license_check: bool = Field(...)
    enable_vulnerability_check: bool = Field(...)
    enable_maintenance_check: bool = Field(...)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Singleton instance
# Los valores se cargan automáticamente desde .env en runtime
settings = Settings()  # type: ignore[call-arg]
