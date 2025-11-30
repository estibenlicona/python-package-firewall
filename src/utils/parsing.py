from typing import Optional, Any
import re


def extract_published_date(published_at: str) -> Optional[str]:
    """Devuelve la fecha en formato corto YYYY-MM-DD o None."""
    if published_at and len(published_at) >= 10:
        return published_at[:10]
    return None

def extract_spdx(license_details: list[dict[str, Any]]) -> Optional[str]:
    """Devuelve el spdx de la primera licencia si existe."""
    if license_details:
        spdx: Any = license_details[0].get("spdx")
        if isinstance(spdx, str):
            return spdx
    return None

def extract_version_from_filename(filename: str) -> Optional[str]:
    """Extrae la versión de un archivo .whl o .tar.gz."""
    # Pattern matches: package_name-version-...
    # Stops at first dash after version or file extension
    pattern = r'^[a-zA-Z0-9_-]+-([0-9]+(?:\.[0-9]+)*(?:[a-zA-Z0-9._]*?)?)-'
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    
    # Fallback for tar.gz files: package-version.tar.gz
    pattern_tar = r'^[a-zA-Z0-9_-]+-([0-9]+(?:\.[0-9]+)*(?:[a-zA-Z0-9._]*?)?)\.'
    match_tar = re.match(pattern_tar, filename)
    if match_tar:
        return match_tar.group(1)
    
    return None
