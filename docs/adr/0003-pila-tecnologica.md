# ADR 0003: Pila tecnológica

- **Estado:** Propuesto (borrador)
- **Fecha:** 2026-10-06
- **Decide:** líder del equipo
- **Referencias:** [PROPUESTA.md](../PROPUESTA.md), secciones 3 (D2), 6 y 10

## Contexto

El proyecto necesita una pila que permita ETL reproducible, pruebas
automáticas y tableros en Power BI, sin complejidad innecesaria para un equipo
de 5 personas y un plazo de un semestre. Los materiales del curso usan SQL
Server como ejemplo, pero la elección de herramientas es libre (D2).

## Decisión propuesta

| Capa | Elección propuesta | Justificación | Estado |
|---|---|---|---|
| Lenguaje | Python 3.13 | Experiencia previa del líder y ecosistema de datos | Propuesto |
| Gestión de entorno | `uv` | Entornos y dependencias reproducibles | Propuesto |
| Calidad de código | `ruff`, `pytest`, tipado estático | Convenciones y pruebas automáticas | Propuesto |
| Base de datos | PostgreSQL en Docker Compose | Compatible con Power BI | Decidido (D2) |
| Transformación y pruebas | dbt | Pruebas de integridad, documentación y linaje | Decidido (D2) |
| Foto cruda | Parquet o JSON con manifiesto de checksums | Reproducible y verificable | Propuesto (formato pendiente, ver ADR 0002) |
| Orquestación | CLI primero; Airflow o Dagster después | Evitar complejidad prematura | Fase posterior |
| CI | GitHub Actions + `pre-commit` | Revisión automática en cada PR | Fase posterior: se implementa cuando haya código y pruebas que verificar |
| Documentación | MkDocs Material | Sitio navegable y versionado | Propuesto |
| BI | Power BI Desktop | Lo exige el curso | Confirmado por el curso |

**No se usan:** Kafka, Kubernetes ni microservicios. La escalabilidad se
demuestra con diseño y con mediciones (tiempos de carga con volúmenes
crecientes), no con la cantidad de herramientas.

### DDL explícito frente a dbt puro

La semana 3 pide sentencias `CREATE TABLE` con claves, índices y nombres
consistentes. Opciones:

- **A.** DDL explícito versionado en `warehouse/ddl/`, más dbt para
  transformaciones y pruebas.
- **B.** dbt con contratos de modelo y restricciones, exportando el DDL como
  entregable.

Recomendación inicial: **A**. **[PENDIENTE]** Confirmar con un spike corto en
la fase 2.

## Pendiente

| Tema | Estado | Quién lo resuelve |
|---|---|---|
| DDL explícito (A) o dbt puro (B) | **[PENDIENTE]** spike en fase 2 | Rol 2 (modelo dimensional) |
| Herramienta de tipado estático | **[PENDIENTE]** | Líder |
| Aprobación de cada dependencia antes de instalarla | **[PENDIENTE]** | Líder |
| Orquestador (Airflow o Dagster), si llega a hacer falta | Fase posterior, requiere ADR propio | Líder |

Ninguna de estas herramientas está instalada ni configurada todavía. El
repositorio no tiene `pyproject.toml`, `compose.yaml`, `Makefile`,
`.pre-commit-config.yaml` ni CI.

## Consecuencias

- Cambiar PostgreSQL o dbt más adelante exige un ADR nuevo, porque afecta al
  DDL, a la conexión de Power BI y a las pruebas de integridad.
- Docker Compose obliga a que cada integrante pueda ejecutar Docker en su
  equipo.
- Power BI Desktop solo funciona en Windows; quien trabaje en los tableros
  necesita ese sistema operativo.
- Cada herramienta nueva necesita justificación en un ADR.
