from dataclasses import dataclass
from typing import Any
from src.config import settings

@dataclass
class Decision:
    status: str  # "allow" | "block"
    reason: str = ""
    details: dict[str, Any] | None = None

class RulesEngine:
    def __init__(self) -> None:
        # Lazy import para evitar ciclos
        self._fetcher: Any = None
        self._license_engine: Any = None
        self._maintenance_engine: Any = None
    
    @property
    def fetcher(self) -> Any:
        """Lazy loading de PackageInfoFetcher"""
        if self._fetcher is None:
            from src.services.package_info_fetcher import PackageInfoFetcher
            self._fetcher = PackageInfoFetcher()
        return self._fetcher
    
    @property
    def license_engine(self) -> Any:
        """Lazy loading de LicenseEngine"""
        if self._license_engine is None:
            from src.domain.license_engine import LicenseEngine
            self._license_engine = LicenseEngine()
        return self._license_engine
    
    @property
    def maintenance_engine(self) -> Any:
        """Lazy loading de MaintenanceEngine"""
        if self._maintenance_engine is None:
            from src.domain.maintenance_engine import MaintenanceEngine
            self._maintenance_engine = MaintenanceEngine()
        return self._maintenance_engine
    
    def decide(self, package: str, version: str, ecosystem: str = "pypi") -> Decision:
        """
        Evalúa si una versión de un paquete debe ser permitida o bloqueada
        según las políticas de seguridad configuradas.
        """
        # Recopilar información del paquete
        info: dict[str, Any] = self.fetcher.fetch_info(package, version, ecosystem)
        
        error_value: Any = info.get("error")
        if error_value:
            return Decision("allow", "Package version not found in analysis", info)
        
        reasons: list[str] = []
        
        # 1. Validación de vulnerabilidades
        if settings.enable_vulnerability_check:
            vulns: Any = info.get("vulnerabilities", [])
            if vulns:
                vuln_list = ", ".join(str(v) for v in vulns[:3])  # Primeras 3 CVEs
                reasons.append(f"Vulnerabilities found: {vuln_list}")
        
        # 2. Validación de licencia
        if settings.enable_license_check:
            spdx: Any = info.get("spdx")
            if spdx:
                osi_approved = self.license_engine.check_license(spdx)
                if not osi_approved:
                    reasons.append(f"Non-OSI approved license: {spdx}")
            else:
                reasons.append("No license information found")
        
        # 3. Validación de mantenimiento
        if settings.enable_maintenance_check:
            latest_published_at: Any = info.get("latest_published_at")
            maintained = self.maintenance_engine.is_maintained(latest_published_at)
            if not maintained:
                reasons.append(f"Package not maintained (>{settings.maintenance_window_years} years)")
        
        # Decisión final
        if reasons:
            return Decision("block", "; ".join(reasons), info)
        
        return Decision("allow", "All security checks passed", info)
