import pytest
from src.domain.license_engine import LicenseEngine
from src.domain.maintenance_engine import MaintenanceEngine
from src.domain.rules_engine import RulesEngine
from src.utils.parsing import extract_version_from_filename, extract_spdx, extract_published_date
from typing import Any


class TestLicenseEngine:
    def test_osi_approved_license(self):
        engine = LicenseEngine()
        # Apache-2.0 is OSI approved
        assert engine.check_license("Apache-2.0") is True
    
    def test_non_osi_approved_license(self):
        engine = LicenseEngine()
        # CC-BY-NC-4.0 is NOT OSI approved
        assert engine.check_license("CC-BY-NC-4.0") is False
    
    def test_invalid_license(self):
        engine = LicenseEngine()
        assert engine.check_license("INVALID-LICENSE") is False


class TestMaintenanceEngine:
    def test_maintained_package(self):
        engine = MaintenanceEngine()
        # Recent date (within 2 years)
        recent_date = "2024-11-29T00:00:00Z"
        assert engine.is_maintained(recent_date) is True
    
    def test_unmaintained_package(self):
        engine = MaintenanceEngine()
        # Old date (more than 2 years ago)
        old_date = "2020-01-01T00:00:00Z"
        assert engine.is_maintained(old_date) is False
    
    def test_none_date(self):
        engine = MaintenanceEngine()
        assert engine.is_maintained(None) is False


class TestRulesEngine:
    @pytest.mark.slow
    def test_decide_with_real_analysis(self):
        """Integration test: RulesEngine calls real APIs"""
        engine = RulesEngine()
        result = engine.decide("requests", "2.31.0", ecosystem="pypi")
        # Should have a decision (allow or block)
        assert result.status in ["allow", "block"]
        assert isinstance(result.reason, str)
        # Should have analysis details
        assert result.details is not None


class TestParsingUtils:
    def test_extract_version_from_whl(self):
        filename = "requests-2.31.0-py3-none-any.whl"
        version = extract_version_from_filename(filename)
        assert version == "2.31.0"
    
    def test_extract_version_from_tar_gz(self):
        filename = "requests-2.31.0.tar.gz"
        version = extract_version_from_filename(filename)
        assert version == "2.31.0"
    
    def test_extract_version_alpha(self):
        filename = "somepackage-1.0.0a1-py3-none-any.whl"
        version = extract_version_from_filename(filename)
        assert version == "1.0.0a1"
    
    def test_extract_spdx_valid(self):
        license_details: list[dict[str, Any]] = [{"spdx": "MIT"}]
        spdx = extract_spdx(license_details)
        assert spdx == "MIT"
    
    def test_extract_spdx_empty(self):
        license_details: list[dict[str, Any]] = []
        spdx = extract_spdx(license_details)
        assert spdx is None
    
    def test_extract_published_date(self):
        date_str = "2024-11-29T12:34:56Z"
        result = extract_published_date(date_str)
        assert result == "2024-11-29"
