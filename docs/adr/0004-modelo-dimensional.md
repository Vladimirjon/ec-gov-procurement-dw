# ADR 0004: Modelo dimensional

- **Estado:** Aceptado
- **Fecha:** 2026-11-03 (reemplaza «Alcance del modelo dimensional en las
  entregas», 2026-10-10)
- **Decide:** líder del equipo
- **Referencias:** guía del proyecto, secciones 4 y 5; guía del Hito 1

## Contexto

El profesor exige como mínimo una tabla de hechos, la dimensión tiempo, tres
dimensiones conformadas y una dimensión con SCD tipo 2. Pide un esquema `stg` y
un esquema `dw`, y que el tablero lea solo de `dw`. También pide bitácora de
cargas y reconciliación con la fuente. Cada pregunta del Hito 1 se expresa como
una medida por dimensiones.

## Decisión

1. **Esquemas:** `stg` (copia cruda), `dw` (hechos, dimensiones y vistas de
   reporte) y `audit` (bitácora de cargas, filas rechazadas y resultados de
   las reglas de calidad). **No existe un esquema `rpt`.** El tablero lee solo
   `dw`, por medio de vistas con prefijo `v_`.
2. **Un hecho:** `fact_contract_process`. Grano previsto: un proceso de
   contratación (`ocid`) por periodo de análisis, con `ocid` como dimensión
   degenerada. El grano definitivo se enuncia en una frase al perfilar los
   datos.
3. **Dimensiones:**
   - `dim_date`: tiempo (día, mes, trimestre, año).
   - `dim_entity`: entidad compradora y su clasificación; **SCD tipo 2**.
   - `dim_method`: método de contratación.
   - Una cuarta, `dim_geography` o `dim_supplier`, según lo que se pueda usar
     sin romper el grano. El mínimo del profesor son tres conformadas; se
     confirma al diseñar la estrella (Hito 3).
4. **Medidas previstas:** monto adjudicado, valor estimado de la licitación y
   desviación porcentual. Son magnitudes distintas y no se sustituyen entre sí.
   Un proceso puede tener varias adjudicaciones y contratos, y no se debe
   multiplicar filas al combinarlos.
5. **Tablero:** Power BI con dos páginas como mínimo (resumen ejecutivo y
   detalle) e interactividad.
6. Un segundo hecho solo se agrega si lo justifica una pregunta, y comparte
   las dimensiones.

## Pendiente

| Tema | Quién | Cuándo |
|---|---|---|
| Grano y medidas definitivas | Modelador | Hito 3 |
| Cuarta dimensión | Modelador, con el líder | Hito 3 |
| Fecha que asigna un proceso a un periodo: se compara la cobertura de `date`, `awards[].date`, `contracts[].dateSigned` y `tender.tenderPeriod.startDate` | Ingeniería de datos | Hito 2 |

## Consecuencias

- La calidad de datos y la bitácora salen del modelo de negocio y viven en
  `audit`.
- Los nombres técnicos (`fact_`, `dim_`, `v_`) siguen en inglés,
  como el resto del código.
