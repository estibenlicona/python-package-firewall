# python-package-firewall

🛡️ **Python Package Firewall** - Proxy transparente para PyPI con validación de seguridad (PEP 503/691 compatible).

Bloquea automáticamente paquetes con:
- ❌ Vulnerabilidades conocidas (CVE)
- ❌ Licencias no aprobadas por OSI
- ❌ Falta de mantenimiento (>2 años sin actualizaciones)

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/estibenlicona/python-package-firewall.git
cd python-package-firewall

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -e .
```

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto (puedes copiar `.env.example`):

```bash
# PyPI Proxy Configuration
PYPI_UPSTREAM_URL=https://pypi.org/simple
PYPI_FILES_BASE_URL=https://files.pythonhosted.org/packages
PROXY_BASE_URL=http://127.0.0.1:8000/pypi/packages
PROXY_HOST=127.0.0.1
PROXY_PORT=8000

# External APIs
DEPSDEV_API_URL=https://api.deps.dev/v3alpha
OSV_API_URL=https://api.osv.dev/v1

# Security Policies
MAINTENANCE_WINDOW_YEARS=2
ENABLE_LICENSE_CHECK=true
ENABLE_VULNERABILITY_CHECK=true
ENABLE_MAINTENANCE_CHECK=true
```

## 🎯 Uso

### Iniciar el servidor

```bash
uvicorn src.api:app --reload
```

El proxy estará disponible en `http://127.0.0.1:8000`

### Usar como índice de pip

```bash
# Instalar paquete usando el firewall
pip install requests --index-url http://127.0.0.1:8000/simple/

# Bloquear instalación de paquetes vulnerables
pip install keras==3.11.2 --index-url http://127.0.0.1:8000/simple/
# ❌ ERROR: HTTP error 403 - Vulnerabilities found: CVE-2025-12060, CVE-2025-9905, CVE-2025-49655
```

### Configurar pip permanentemente

```bash
# Editar ~/.pip/pip.conf (Linux/Mac) o %APPDATA%\pip\pip.ini (Windows)
[global]
index-url = http://127.0.0.1:8000/simple/
```

## 📡 Endpoints

### **PEP 691 Simple API (compatible con pip)**
- `GET /simple/` — Índice raíz (HTML)
- `GET /simple/{package}/` — Índice JSON del paquete (PEP 691)
- `GET /pypi/packages/{filename}` — Descarga de archivos .whl/.tar.gz con validación lazy

### **Auditoría**
- `GET /blocked/{package}` — Consulta razones de bloqueo de un paquete

**Ejemplo:**
```bash
curl http://127.0.0.1:8000/blocked/keras
```

**Respuesta:**
```json
{
  "package": "keras",
  "status": "blocked",
  "blocked_versions": 1,
  "reasons": [
    "Version 3.11.2: Vulnerabilities found: CVE-2025-12060, CVE-2025-9905, CVE-2025-49655"
  ],
  "message": "All versions of this package are blocked by firewall policy."
}
```

## 🏗️ Arquitectura (Clean Architecture)

```
src/
├── api.py                          # FastAPI endpoints (presentation)
├── config.py                       # Pydantic settings (.env)
├── domain/                         # Business logic
│   ├── license_engine.py           # OSI approval validation
│   ├── maintenance_engine.py       # 2-year maintenance check
│   └── rules_engine.py             # Policy enforcement
├── services/                       # External integrations
│   ├── depsdev_client.py           # deps.dev API client
│   ├── osv_client.py               # OSV vulnerability DB
│   ├── package_info_fetcher.py     # Package metadata fetcher
│   └── pypi_proxy_service.py       # PEP 691 proxy logic
└── utils/                          # Utilities
    └── parsing.py                  # Version/license/date parsing
```

## 🧪 Pruebas

```bash
# Tests rápidos (sin llamadas a APIs)
pytest -v -m "not slow"

# Todos los tests (incluye integraciones)
pytest -v

# Con cobertura
pytest --cov=src --cov-report=html
```

## 🛠️ Desarrollo

### Formato y lint

```bash
# Auto-formatear código
ruff format .

# Verificar errores
ruff check .

# Type checking (Pylance strict mode)
# Configurado en .vscode/settings.json
```

### Políticas de seguridad

Puedes deshabilitar validaciones específicas en `.env`:

```bash
ENABLE_VULNERABILITY_CHECK=false  # Permitir CVEs
ENABLE_LICENSE_CHECK=false        # Permitir licencias no-OSI
ENABLE_MAINTENANCE_CHECK=false    # Permitir paquetes abandonados
```

## 🔒 Características de seguridad

### **Validación Lazy (eficiente)**
- ✅ Índice de paquetes devuelto instantáneamente
- ✅ Validación solo cuando pip intenta descargar
- ✅ Evita 50+ llamadas API innecesarias

### **Detección de vulnerabilidades**
- Consulta OSV (Open Source Vulnerabilities)
- Bloquea automáticamente versiones con CVEs

### **Validación de licencias**
- Solo permite licencias aprobadas por OSI
- Valida SPDX identifiers

### **Mantenimiento**
- Bloquea paquetes sin actualizaciones en 2+ años
- Configurable vía `MAINTENANCE_WINDOW_YEARS`

## 📊 Flujo de validación

```
pip install requests
     ↓
1. GET /simple/requests/  → ✅ 200 OK (índice JSON completo)
     ↓
2. GET /pypi/packages/requests-2.32.5.whl.metadata
     ↓
3. RulesEngine.decide("requests", "2.32.5")
     ├─ PackageInfoFetcher → deps.dev + OSV
     ├─ LicenseEngine → OSI approval check
     ├─ MaintenanceEngine → 2-year window check
     └─ Decision: "allow" / "block"
     ↓
4a. ✅ ALLOW → Stream desde PyPI
4b. ❌ BLOCK → HTTP 403 + reason
```

## 🌐 APIs externas utilizadas

- **deps.dev** (`https://api.deps.dev/v3alpha`) - Metadata de paquetes
- **OSV** (`https://api.osv.dev/v1`) - Base de datos de vulnerabilidades
- **PyPI Simple API** (`https://pypi.org/simple`) - Índices de paquetes (PEP 691)

## 📝 Licencia

MIT
