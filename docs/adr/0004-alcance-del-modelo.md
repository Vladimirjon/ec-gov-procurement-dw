# ADR 0004: Alcance del modelo dimensional en las entregas

- **Estado:** Propuesto (borrador)
- **Fecha:** 2026-10-10
- **Decide:** líder del equipo
- **Referencias:** [PROPUESTA.md](../PROPUESTA.md), sección 5;
  [PLAN.md](../PLAN.md)
- **Modifica:** la sección 5 de la propuesta (constelación de 3 hechos y 7
  dimensiones)

## Contexto

La propuesta plantea una constelación: `fact_contract_process`,
`fact_process_supplier` y `fact_quality_check`, con siete dimensiones. El
material del curso para la fase 2 pide lo contrario:

- evitar más de una tabla de hechos por esquema en esa etapa;
- considera ideal **1 hecho y de 3 a 5 dimensiones**;
- los entregables de diseño tienen de 1 a 3 páginas.

Además, la fase 4 del curso pide tablas de logs y de errores dentro del DW,
con columnas definidas. Ese es el lugar natural de la calidad de datos y de
la bitácora de cargas.

## Decisión

1. **Estrella principal (entregas de las fases 1 a 3):** un solo hecho y
   entre 4 y 5 dimensiones.
   - Hecho: `fact_contract_process`. Grano previsto: un proceso de
     contratación (`ocid`) por foto. `ocid` va como dimensión degenerada.
   - Dimensiones: `dim_date`, `dim_entity` (SCD tipo 2), `dim_method`,
     `dim_geography` y, si la estructura de `suppliers` lo permite sin romper
     el grano, `dim_supplier`.
2. **Esquema `audit` (fase 4):** la bitácora y la calidad salen del modelo
   dimensional de negocio y pasan a un esquema de auditoría:
   - `load_log`: id, proceso, inicio, fin, tabla destino, registros
     correctos, errores, duración y estado.
   - `load_error`: id, tabla, campo, descripción, fecha y hora, proceso y
     acción tomada.
   - Resultados de las reglas de calidad (lo que antes era
     `fact_quality_check` y `dim_quality_rule`), que alimentan el tablero de
     Detección de Problemas.
3. **`fact_process_supplier` queda como extensión opcional**, solo si sobra
   tiempo después de la fase 4 y la estructura de `suppliers` lo justifica.

## Pendiente

| Tema | Estado | Quién lo resuelve |
|---|---|---|
| Grano definitivo del hecho | **[PENDIENTE]** tras el perfilado (fase 2) | Responsable de Modelado |
| Si `dim_supplier` entra en la estrella o se aplaza | **[PENDIENTE]** al observar `suppliers` | Responsable de Modelado, con el líder |
| Medidas definitivas del hecho | **[PENDIENTE]** fase 1, Guía de Diseño Inicial | Responsable de Modelado |

## Consecuencias

- Los entregables de diseño quedan dentro de lo que pide el curso y caben en
  1–3 páginas.
- La calidad de datos no se pierde: se entrega en la fase 4, como pide el
  curso, y se ve en el tablero de Detección de Problemas.
- La sección 5 de la propuesta queda como visión ampliada; ante una
  diferencia, manda este ADR.
