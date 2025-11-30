from typing import Optional

from spdx_license_list import LICENSES, License


class LicenseEngine:
    def check_license(self, identifier: str) -> bool:
        data: Optional[License] = LICENSES.get(identifier)
        if not data:
            return False
        return data.osi_approved or False