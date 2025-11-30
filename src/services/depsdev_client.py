import requests
from typing import Optional, Dict, Any, List
from src.config import settings

class DepsDevClient:
    BASE_URL = settings.depsdev_api_url

    def get_version_info(self, package: str, ecosystem: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        eco = ecosystem.upper()
        if version:
            url = f"{self.BASE_URL}/systems/{eco}/packages/{package}/versions/{version}"
        else:
            url = f"{self.BASE_URL}/systems/{eco}/packages/{package}"
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        return resp.json()

    def get_latest_version(self, package: str, ecosystem: str) -> Optional[Dict[str, Any]]:
        eco = ecosystem.upper()
        url = f"{self.BASE_URL}/systems/{eco}/packages/{package}"
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        data: Dict[str, Any] = resp.json()
        versions: List[Dict[str, Any]] = data.get("versions", [])
        if not versions:
            return None
        version_obj: Dict[str, Any] = {}
        for v in versions:
            if v.get("isDefault"):
                version_obj = v
        
        version_key: Dict[str, Any] = version_obj.get("versionKey", {})
        version_str: Optional[str] = version_key.get("version")
        published_at: Optional[str] = version_obj.get("publishedAt")
        
        return {
            "version": version_str,
            "publishedAt": published_at if published_at else None
        }

    def get_dependencies(self, package: str, ecosystem: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
        if not version:
            latest = self.get_latest_version(package, ecosystem)
            if not latest:
                return []
            version_val: Optional[str] = latest.get("version")
            if not version_val:
                return []
            version = version_val
        
        url = f"https://api.deps.dev/v3/systems/{ecosystem.upper()}/packages/{package}/versions/{version}:dependencies"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            dep_data: Dict[str, Any] = resp.json()
            nodes: List[Dict[str, Any]] = dep_data.get("nodes", [])
            dependencies: List[Dict[str, Any]] = []
            for node in nodes:
                if node.get("relation") == "SELF":
                    continue
                vk: Dict[str, Any] = node.get("versionKey", {})
                dependencies.append({
                    "name": vk.get("name"),
                    "version": vk.get("version"),
                    "relation": node.get("relation")
                })
            return dependencies
        except Exception:
            return []
