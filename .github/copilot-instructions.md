# Copilot Instructions — python-package-firewall

## Project Purpose
Python Package Firewall implementing PEP 503/691 proxy for PyPI with license validation, vulnerability scanning, and maintenance checks.

## Architecture (Clean Architecture)
```
src/
├── api.py              # FastAPI endpoints (presentation layer)
├── application/        # Use cases & orchestration
│   └── analize_package.py  # Main analysis orchestrator
├── domain/             # Business logic
│   ├── license_engine.py      # SPDX/OSI validation
│   ├── maintenance_engine.py  # 2-year recency checks
│   └── rules_engine.py        # Allow/block decisions
├── services/           # External API clients
│   ├── depsdev_client.py      # deps.dev API
│   ├── osv_client.py          # OSV vulnerability DB
│   └── pypi_proxy_service.py  # PEP 691 proxy logic
└── utils/              # Helpers
    └── parsing.py      # Version/license extraction
```

## Critical Data Flows

### PEP 691 JSON Proxy (`/simple/{package}/`)
1. Client requests package index
2. `PyPIProxyService.get_filtered_index()` fetches JSON from PyPI with header `Accept: application/vnd.pypi.simple.v1+json`
3. For each file: extract version → call `RulesEngine.decide(package, version)` → if blocked, exclude
4. Rewrite URLs: `https://files.pythonhosted.org/...` → `http://127.0.0.1:8000/pypi/packages/<filename>`
5. Return filtered JSON response (not HTML)

### Package Streaming (`/pypi/packages/{filename}`)
- Transparent streaming proxy: PyPI → firewall → pip
- Uses URL cache from previous index request
- No local storage, pure `StreamingResponse`

### Analysis Endpoint (`/license/{ecosystem}/{package}?version=...`)
- Orchestrated by `AnalyzePackage.analyze()`
- Fetches: version info, latest version, dependencies, vulnerabilities
- Returns: license (SPDX + OSI approval), maintenance status, dependencies, CVE aliases

## Type Safety Rules (Pylance Strict Mode)
- **All imports at file top** — never inside functions/classes
- **No nested functions** — all functions at module level
- **Explicit types required**: `dict[str, Any]`, `list[Dict[str, Any]]`, `Optional[str]`
- When working with JSON APIs: use explicit type annotations for all variables
- Example from `osv_client.py`:
  ```python
  data: dict[str, Any] = resp.json()
  vulns: list[dict[str, Any]] = data.get("vulns", [])
  ```

## Key Conventions
- **URL rewriting base**: Always `http://127.0.0.1:8000/pypi/packages/` for local development
- **Ecosystem normalization**: Input lowercase → uppercase for APIs (e.g., `pypi` → `PYPI`)
- **Version extraction regex**: `r'^[a-zA-Z0-9_-]+-([0-9]+(?:\.[0-9]+)*(?:[a-zA-Z0-9._-]*)?)'`
- **Dependency filtering**: Exclude `relation == "SELF"` nodes from deps.dev responses
- **Maintenance window**: 2 years from `latest_version.publishedAt`

## Development Workflow
```bash
# Setup
uv venv
.venv\Scripts\activate
uv pip install -e .

# Run server
uvicorn src.api:app --reload

# Format/Lint (before commit)
ruff check .
ruff format .

# Tests (when implemented)
pytest --maxfail=1 --disable-warnings -q
```

## External API Integration Points
- **deps.dev**: `https://api.deps.dev/v3alpha` (package metadata, dependencies)
  - Use `/systems/{ECOSYSTEM}/packages/{name}/versions/{version}:dependencies` for flat dep list
- **OSV**: `https://api.osv.dev/v1/query` (vulnerability data)
  - Extract only `aliases` from response, return as `list[str]`
- **PyPI Simple API**: `https://pypi.org/simple/{package}/` with JSON header (PEP 691)

## Important Patterns
- **Singleton services**: `proxy = PyPIProxyService()` instantiated once in `api.py`
- **Error propagation**: Use `HTTPException` from FastAPI, not raw exceptions
- **Logging**: Use module-level `logger = logging.getLogger(__name__)` in services
- **Response caching**: `url_cache: dict[str, str]` in `PyPIProxyService` maps filename → real PyPI URL

## Testing Considerations
- Mock external APIs (deps.dev, OSV, PyPI) in unit tests
- Integration tests should verify PEP 691 JSON structure compliance
- Test version extraction with edge cases: `1.0.0a1`, `2.3.4.post1`, `3.0.0rc2`

## Anti-Patterns to Avoid
- ❌ Returning HTML from `/simple/{package}/` (must be JSON per PEP 691)
- ❌ Storing package files locally (always stream)
- ❌ Using `Any` without type narrowing in critical paths
- ❌ Importing inside functions (Pylance strict violation)
- ❌ Calling `extract_published_date()` with `None` (requires `str`)
