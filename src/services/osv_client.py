import requests
from typing import List, Any
from src.config import settings

class OSVClient:
    BASE_URL = f"{settings.osv_api_url}/query"
    ECOSYSTEM_MAP = {
        "pypi": "PyPI",
    }

    def get_vulnerabilities(self, package: str, ecosystem: str, version: str) -> List[str]:
        eco = self.ECOSYSTEM_MAP.get(ecosystem.lower(), ecosystem.capitalize())
        payload: dict[str, Any] = {
            "package": {"name": package, "ecosystem": eco},
            "version": version
        }
        resp = requests.post(self.BASE_URL, json=payload)
        if resp.status_code != 200:
            return []
        data: dict[str, Any] = resp.json()
        vulns: list[dict[str, Any]] = data.get("vulns", [])
        aliases: list[str] = []
        for vuln in vulns:
            vuln_aliases: list[Any] = vuln.get("aliases", [])
            for alias in vuln_aliases:
                if isinstance(alias, str):
                    aliases.append(alias)
        return aliases
