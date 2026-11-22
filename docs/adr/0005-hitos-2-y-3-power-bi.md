# ADR 0005: Hitos 2 y 3 en Power BI, convención de nombres y un hecho

- **Estado:** Propuesto (lo acepta o corrige el líder)
- **Fecha:** 2026-11-20
- **Decide:** líder del equipo
- **Referencias:** guía del Hito 2 y guía del Hito 3 del profesor; guía general
  del proyecto, secciones 4, 5 y 7; [ADR 0003](0003-pila-tecnologica.md);
  [ADR 0004](0004-modelo-dimensional.md); `docs/requisitos-del-profesor.md`
  (secciones F y G)

## Contexto

El 20/11/2026 el profesor publicó las guías detalladas de los hitos 2 y 3. Se
entregan el 21 y el 22 de noviembre. Difieren de lo que la guía general decía
para esos hitos (H2: `stg` en PostgreSQL, notebook de perfilado y diccionario en
Excel; H3: matriz de bus, estrella, DDL ejecutado en PostgreSQL y exposición):

- **H2:** `.pbix` con las fuentes conectadas y un libro de Excel (o Word/PDF)
  con Fuentes, Diccionario, Calidad y Cobertura. Se diagnostica, no se corrige.
- **H3:** `.pbix` con el modelo dimensional construido en Power Query,
  documento de diseño en PDF (máximo 8 páginas sin anexos), bitácora de
  transformaciones y diapositivas en PDF; presentación de 10 minutos más 5 de
  preguntas. La convención de nombres de la guía es `Fact…` y `Dim…`.

`AGENTS.md` dice que si algo contradice a un PDF, manda el PDF. Las guías
específicas son más detalladas, traen su propia rúbrica sobre 20 y definen el
insumo del hito siguiente.

## Decisión

1. **Mandan las guías de H2 y H3.** Los hitos 2 y 3 se hacen en Power BI
   Desktop con Power Query y las plantillas de cada guía. PostgreSQL, los
   esquemas `stg`, `dw` y `audit`, el DDL ejecutado y la infraestructura (Docker)
   pasan al Hito 4, cuando el profesor publique su guía. La arquitectura de
   referencia de la guía general (fuentes → `stg` → ETL → `dw` → consumo) no se
   modifica: solo cambia cuándo se construye cada capa.
2. **Nombres:** en el modelo de Power BI se usan `FactContratacion`,
   `DimTiempo`, `DimEntidad` y `DimMetodo` (PascalCase, como la guía). Los
   nombres físicos del DW de H4 siguen el [ADR 0004](0004-modelo-dimensional.md)
   (`fact_contract_process`, `dim_date`, `dim_entity`, `dim_method`). La
   equivalencia es la de esta tabla:

   | Power BI (H3) | DW físico (H4, ADR 0004) |
   |---|---|
   | `FactContratacion` | `fact_contract_process` |
   | `DimTiempo` | `dim_date` |
   | `DimEntidad` | `dim_entity` (SCD tipo 2 en H4) |
   | `DimMetodo` | `dim_method` |

3. **Un hecho, tres dimensiones.** Un solo hecho a grano de proceso de
   contratación (`ocid`) y tres dimensiones (tiempo, entidad, método), como el
   ADR 0004 y las tres preguntas del Hito 1. Un segundo hecho
   (`FactAdjudicacion`, grano: una adjudicación) o una cuarta dimensión solo si
   el diagnóstico de H2 o una pregunta lo exigen. La tabla de hechos no guarda
   tasas ni porcentajes (guía H3, 3.2): guarda numerador y denominador.
4. **El `.pbix` no se versiona en Git** (decisión del líder, 21/11/2026, que
   reemplaza la del 20/11). El de H2 pesa 243 MB y GitHub rechaza archivos de
   más de 100 MB; Git LFS sería infraestructura nueva y no se adopta. Los
   `*.pbix` y las plantillas `*.pbit` están en `.gitignore` y el `.pbix` se
   entrega por el aula virtual. Se versionan las consultas M
   (`reports/powerbi/`), los runbooks, el libro de Excel y la evidencia
   agregada. Los datos crudos y derivados siguen fuera de Git.
5. **Tablas de H2** (el nombre de la tabla es el de la consulta de Power BI):
   `Procesos_SERCOP`, `Licitaciones_SERCOP`, `Adjudicaciones_SERCOP` y
   `Entidades_MDEP` (la cuarta se añadió el 21/11/2026: P2 necesita el importe
   estimado de `tender`). Los contratos
   quedan fuera: P1 a P3 no los usan y solo el 15,33 % de los de 2025 trae
   importe (dato nacional, `reconocimiento.md`). No se cargan datos de contacto
   de personas (decisión D3 de `requisitos-del-profesor.md`).
6. **La desviación porcentual deja de ser una medida del hecho.** El ADR 0004
   (punto 4) la lista entre las medidas previstas; la guía H3 (3.2) prohíbe
   guardar tasas en el hecho. El hecho guarda `MontoAdjudicado` y
   `ValorEstimado` y la desviación se calcula con una medida DAX (bimestre 2).
7. **Segunda fuente:** el ADR 0001 (punto 5) nombra el directorio `gob.ec`. Si el
   cruce medido en H2 lo justifica, la fuente integrable es el catálogo en Excel
   del MDEP (trae RUC); el directorio `gob.ec` queda como apoyo nominal. La
   decisión definitiva consta en el issue H2-03 y se aprueba en el chat.
8. **Regla de fecha de negocio** (pendiente del ADR 0004): se decide con el
   perfilado de H2 (issue H2-04) y se registra aquí o en un ADR nuevo al
   aprobarla el líder.

## Consecuencias

- El ADR 0003 sigue vigente; su pendiente «`compose.yaml` y `Makefile` en el
  Hito 2» pasa al Hito 4.
- El ADR 0004 no se reescribe: sus nombres siguen siendo los del DW físico.
- Power BI Desktop solo funciona en Windows y no se puede automatizar: lo que
  los agentes entregan para Power BI son consultas M y runbooks, y su
  funcionamiento lo confirma quien abre el archivo en Desktop.
- Si el profesor exige el DDL en PostgreSQL en el Hito 3 (guía general), el
  issue opcional de DDL de respaldo lo cubre sin cambiar este ADR.
