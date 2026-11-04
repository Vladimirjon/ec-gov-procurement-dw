# ADR 0003: Pila tecnológica

- **Estado:** Aceptado
- **Fecha:** 2026-11-03 (reemplaza la versión del 2026-10-06; actualizado el
  mismo día, ver [Actualizaciones](#actualizaciones))
- **Decide:** líder del equipo
- **Referencias:** guía del proyecto, sección 5 (arquitectura de referencia)

## Contexto

La guía del profesor fija la pila: PostgreSQL, Python (pandas y SQLAlchemy)
con SQL, notebooks en Jupyter o Colab, Power BI Desktop y Git. Permite agregar
herramientas como dbt, Airflow o Metabase, pero no sustituir PostgreSQL ni
Power BI.

## Decisión

| Capa | Herramienta | Nota |
|---|---|---|
| Base de datos | PostgreSQL, en Docker Compose | Esquemas `stg`, `dw` y `audit` |
| ETL | Python 3.14 (pandas, SQLAlchemy) y SQL | Un solo comando reconstruye el DW. Antes 3.13; ver [Actualizaciones](#actualizaciones) |
| Perfilado y modelo analítico | Jupyter | Notebooks reproducibles |
| Visualización | Power BI Desktop | Archivo `.pbix` conectado al esquema `dw` |
| Control de versiones | Git y GitHub | Historial con commits de todo el equipo |
| Entorno | `uv` | Dependencias reproducibles |
| Calidad de código | `ruff` y `pytest` | |

**No se usa dbt.** La guía no lo exige, es una herramienta más que aprender y
el DDL explícito versionado en `warehouse/ddl/` cubre lo que pide el Hito 3. La
clasificación de entidades vive en `warehouse/seeds/` como CSV cargado por el
ETL. Tampoco se usan Airflow, MkDocs, Kafka ni Kubernetes.

Las reglas de calidad y la bitácora se escriben en Python y SQL, en el esquema
`audit`.

## Reglas

- Cada herramienta nueva necesita un ADR y la aprobación del líder.
- El DW se debe poder reconstruir desde cero en otra máquina con un solo
  comando (checklist final de la guía).

## Pendiente

| Tema | Quién | Cuándo |
|---|---|---|
| Archivos de entorno: `compose.yaml`, `Makefile` | Líder | Hito 2 |
| `pre-commit` | Líder | Hito 4 |
| Marcar el CI como verificación obligatoria en la protección de `main` | Líder | Al fusionar el issue #43 |

Hecho en el Hito 1 (issue #43): `pyproject.toml`, `uv.lock` y `.python-version`;
CI con GitHub Actions y Dependabot.

## Consecuencias

- Docker debe poder ejecutarse en el equipo de cada integrante.
- Power BI Desktop solo funciona en Windows: quien trabaje en el tablero
  necesita ese sistema.
- `pyproject.toml` y `uv.lock` fijan Python 3.14 y las versiones exactas de
  `ruff` y `pytest`, que son las únicas dependencias (de desarrollo). Aún no
  hay `compose.yaml` ni `Makefile`. Los auxiliares de `scripts/` siguen usando
  solo la biblioteca estándar y PowerShell.
- El CI corre `uv sync --locked`, `ruff check`, `ruff format --check` y
  `pytest` en Linux y Windows en cada PR y en cada push a `main`.

## Actualizaciones

- **2026-11-03 (issue #43, decide el líder).** Python pasa de 3.13 a 3.14.
  Motivo: desde el 1/10/2026 la 3.13 solo recibe parches de seguridad,
  mientras que la 3.14 sigue recibiendo correcciones de errores hasta octubre
  de 2027; además, la máquina del líder ya usa 3.14. Se fija la línea
  (`.python-version` = `3.14`, `requires-python = "==3.14.*"`) y no el parche:
  uv usa el 3.14 más reciente que tenga disponible (en el CI, 3.14.10). El CI,
  que este ADR dejaba para el Hito 4, se adelanta al Hito 1 por decisión del
  líder; `pre-commit` sigue en el Hito 4. Las herramientas no cambian: `uv`,
  `ruff` y `pytest`.
