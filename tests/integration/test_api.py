import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


class TestLicenseEndpoint:
    @pytest.mark.slow
    def test_license_endpoint_success(self):
        """Integration test calling real APIs - slow, skipped by default"""
        resp = client.get("/license/pypi/requests?version=2.31.0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["package"] == "requests"
        assert data["version"] == "2.31.0"
        assert "spdx" in data
        assert "osi_aproved" in data
        assert "dependencies" in data
        assert "vulnerabilities" in data


class TestPyPIProxyEndpoints:
    def test_simple_root(self):
        resp = client.get("/simple/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
    
    @pytest.mark.slow
    def test_simple_package_json_response(self):
        """Integration test with real PyPI API - slow, skipped by default"""
        resp = client.get("/simple/requests/")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/vnd.pypi.simple.v1+json"
        
        data = resp.json()
        assert "name" in data
        assert "files" in data
        assert len(data["files"]) > 0

