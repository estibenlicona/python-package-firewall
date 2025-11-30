# GitHub Instructions — Python Project

Este documento define las reglas, estándares y buenas prácticas requeridas para contribuir al repositorio.  
Todo Pull Request debe cumplir estas instrucciones antes de ser revisado o aprobado.

---

# 1. Project Structure

La estructura del proyecto debe seguir el siguiente formato:

```
/project_root
│── src/<package_name>/
│── tests/
│── tools/
│── pyproject.toml
│── README.md
│── .gitignore
│── CONTRIBUTING.md
│── GITHUB_INSTRUCTIONS.md
│── LICENSE
```

Reglas:
- Todo el código Python se ubica en `src/<package>/`.
- Los tests deben reflejar la estructura interna del paquete.
- No se permiten scripts Python en la raíz del repositorio.
- Los scripts de mantenimiento deben estar en `tools/`.

---

# 2. Code Style & Formatting

Herramientas obligatorias:
- ruff (lint + formateo)
- black
- isort (solo si no interfiere con reglas de imports estrictos)
- Longitud máxima de línea: 120 caracteres.

Comandos obligatorios antes de hacer commit:

```bash
ruff check .
ruff format .
isort .
```

No se aceptan Pull Requests con errores de linting o formateo.

---

# 3. Tests & Coverage

- Framework obligatorio: pytest.
- Cobertura mínima requerida: 85%.
- Los tests deben ser deterministas, sin dependencias externas sin mock.
- Estructura:
  - tests/unit/
  - tests/integration/

Comando oficial:

```bash
pytest --maxfail=1 --disable-warnings -q
```

---

# 4. Python Requirements

- Python 3.10 o superior.
- Uso obligatorio de pyproject.toml.
- Las dependencias deben fijarse con versiones exactas (no rangos).

---

# 5. Commits & Branch Strategy

Convenciones de commit (Conventional Commits):

```
feat: add license scanner
fix: correct dependency resolver
docs: update usage documentation
refactor: improve metadata parsing
test: add tests for cli
```

Nombres de ramas:

```
feature/<short-name>
bugfix/<short-name>
hotfix/<short-name>
refactor/<short-name>
```

---

# 6. Pull Requests

Reglas:
- Máximo 400 líneas modificadas por PR.
- Cada PR debe abarcar un único objetivo.

Checklist:
- [ ] Código formateado.
- [ ] Tests agregados o actualizados.
- [ ] Cobertura mínima cumplida.
- [ ] Documentación actualizada.
- [ ] No rompe retrocompatibilidad sin justificación.

---

# 7. Security

- No incluir tokens, claves o secretos en el repositorio.
- No usar eval, exec o subprocess inseguros.
- Validación de dependencias antes de merge:

```bash
safety check
```

---

# 8. Versioning

Uso obligatorio de Semantic Versioning (SemVer):

```
MAJOR.MINOR.PATCH
```

---

# 9. Dependency Rules

- Las dependencias deben tener versiones exactas.
- No incluir paquetes vendorizados en el repositorio.
- Verificar licencias antes de incorporar un paquete.
- Evitar el uso de GPL o LGPL en entornos corporativos.

---

# 10. Architecture Standards

Recomendado: Clean Architecture / Ports & Adapters.

El código debe ser modular, desacoplado y testeable.

---

# 11. Documentation

- Es obligatorio incluir docstrings en formato Google o NumPy.
- Todo cambio significativo requiere actualización de documentación.

---

# 12. Code of Conduct

- Respeto en discusiones y revisiones.
- Argumentos basados en criterios técnicos.
- Nadie puede aprobar su propio Pull Request.

---

# 13. GitHub Actions

Pipeline recomendado:

1. Lint
2. Format
3. Tests + Coverage
4. Build
5. Release

---

# 14. Issue Management

Tipos aceptados:
- bug
- feature
- enhancement
- documentation
- security

---

# 15. Code Review

Aspectos a revisar:
- Correctitud funcional
- Legibilidad
- Estructura arquitectónica
- Pruebas incluidas
- Seguridad
- Deuda técnica

---

# 16. Bad Practices (Prohibido)

- Código sin tests.
- Dependencias sin versión fija.
- Impresiones o código comentado en producción.
- Pull Requests excesivamente grandes.
- Módulos con demasiadas responsabilidades.

---

# 17. Reglas estrictas para Python, FastAPI y Pylance

Este bloque establece reglas obligatorias para mantener consistencia, evitar errores y asegurar compatibilidad con Pylance en modo estricto.

## 17.1 Importaciones

- Todos los imports deben estar únicamente al inicio del archivo.
- No agregar imports dentro de funciones, clases, condicionales o bloques internos.
- No dispersar imports en el archivo.
- No reordenar imports si no se solicita explícitamente.
- No duplicar imports.
- Si se requiere un import nuevo, debe agregarse al inicio debajo de los existentes, sin alterar el orden natural.

## 17.2 Funciones

- No se permiten funciones dentro de funciones.
- No generar closures salvo solicitud explícita.
- Todas las funciones deben estar al nivel superior del archivo.
- No mover funciones existentes a contextos anidados.

## 17.3 FastAPI

- Los endpoints deben ser funciones de nivel superior.
- No crear routers, servicios o instancias de FastAPI dentro de funciones.
- No duplicar rutas ni inicializaciones como `app = FastAPI()`.
- Si un endpoint existe, debe modificarse en vez de crear una copia.

## 17.4 Pylance MCP Strict Mode

El código debe ser completamente válido para Pylance estricto:

- Tipos obligatorios en parámetros, retornos y variables cuando aplique.
- Evitar Any innecesarios.
- Evitar patrones dinámicos, introspectivos o que afecten la inferencia.
- Mantener estructuras claras y estáticas.
- Cualquier conflicto entre creatividad y Pylance: prevalece Pylance.

---

# 18. Summary

Estas instrucciones garantizan calidad, mantenibilidad, seguridad y consistencia a largo plazo en el proyecto.