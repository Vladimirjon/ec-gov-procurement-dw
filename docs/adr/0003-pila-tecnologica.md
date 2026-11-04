# ADR 0003: Pila tecnológica

- **Estado:** Aceptado
- **Fecha:** 2026-11-03 (reemplaza la versión del 2026-10-06)
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
| ETL | Python 3.13 (pandas, SQLAlchemy) y SQL | Un solo comando reconstruye el DW |
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
| Archivos de entorno: `pyproject.toml`, `compose.yaml`, `Makefile` | Líder | Hito 2 |
| CI con GitHub Actions y `pre-commit`: se activa cuando haya código que verificar | Líder | Hito 4 |

## Consecuencias

- Docker debe poder ejecutarse en el equipo de cada integrante.
- Power BI Desktop solo funciona en Windows: quien trabaje en el tablero
  necesita ese sistema.
- Hoy no hay `pyproject.toml`, `compose.yaml` ni `Makefile`. Los auxiliares de
  `scripts/` usan Python 3.13 y PowerShell sin dependencias nuevas, y no
  constituyen un entorno reproducible.
