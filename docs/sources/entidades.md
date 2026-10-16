# Fuentes oficiales para la clasificación de entidades de la planta central

**Consulta:** 15 de octubre de 2026. **Propósito:** evaluar y proponer fuentes oficiales del Estado ecuatoriano que permitan clasificar a las entidades compradoras de SERCOP en las cuatro categorías definidas en el [ADR 0001](../adr/0001-alcance.md): Presidencia de la República, ministerios, institutos dependientes de un ministerio y entidades fuera de alcance.

Este documento presenta únicamente lo observado en las fuentes oficiales consultadas y su comparación para construir la semilla de clasificación en la fase 1. Los criterios definitivos de inclusión y la resolución de casos dudosos permanecen como **[PENDIENTE]** de aprobación del líder, conforme al [ADR 0001](../adr/0001-alcance.md).

## 1. Fuentes oficiales evaluadas

Se propone una fuente principal por su cobertura nominal abierta y se contrasta con tres alternativas complementarias verificadas el 15 de octubre de 2026:

| Rol en la propuesta | Nombre oficial del catálogo o portal | Entidad administradora | Enlace verificado | Fecha de consulta | Vigencia o actualización observada | Formato de publicación |
|---|---|---|---|---|---|---|
| **Fuente principal propuesta** | Directorio de Instituciones que publican en el Portal Único de Trámites Ciudadanos (`gob.ec`) | Ministerio de Telecomunicaciones y de la Sociedad de la Información (MINTEL) – Subsecretaría de Gobierno Electrónico y Registro Civil | [Directorio general](https://www.gob.ec/instituciones), [sección M (Ministerios)](https://www.gob.ec/instituciones/M), [sección I (Institutos)](https://www.gob.ec/instituciones/I) | 15/10/2026 | Vigente en 2026 (incluye carteras fusionadas en 2026 y registros activos del año en curso) | Directorio web HTML con filtro e índice alfabético (`A`–`V`) |
| **Alternativa 1 (rectoría fiscal y cabecera ejecutiva)** | Catálogo de Instituciones y Entidades Operativas Desconcentradas del Sector Público y Directrices Proforma 2027 | Ministerio de Economía y Finanzas (MEF) / Ministerio de Desarrollo Económico y Productivo (MDEP) | [Catálogo web](https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/) y [Directrices Proforma 2027 (PDF)](https://www.finanzas.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf) | 15/10/2026 | Mayo de 2026 (ciclo presupuestario vigente 2026–2027) | Página web HTML y documento normativo PDF (tablas maestras detalladas residen en el sistema interno eSIGEF) |
| **Alternativa 2 (datos abiertos)** | Catálogo de Organizaciones del Portal Nacional de Datos Abiertos | Presidencia de la República / MINTEL | [Catálogo de conjuntos](https://www.datosabiertos.gob.ec/dataset/) e [índice de organizaciones](https://www.datosabiertos.gob.ec/organization/) | 15/10/2026 | 12/10/2026 (última actualización observada en conjuntos publicados) | Portal CKAN con metadatos y descargas en JSON, CSV y XLSX |
| **Alternativa 3 (rectoría laboral y portales sectoriales)** | Directorio de Instituciones Públicas (Capacitación 2026) e Instituciones Relacionadas por ministerio | Ministerio del Trabajo y Desarrollo Humano (MT) / Ministerio de Ambiente y Energía (MAE) | [Instituciones MT](https://www.trabajo.gob.ec/instituciones-publicas/), [Matriz 2026 (XLS)](https://www.trabajo.gob.ec/wp-content/uploads/2026/03/matriz_catalogo_digital_de_capacitaciones_2026-consolidado.xls) e [Instituciones relacionadas MAE](https://www.ambienteyenergia.gob.ec/instituciones-relacionadas/) | 15/10/2026 | Marzo de 2026 (catálogo consolidado MT) | Tabla web HTML y hoja de cálculo `.xls` |

## 2. Detalle de lo observado en la fuente principal (`gob.ec/instituciones`)

El directorio [`gob.ec/instituciones`](https://www.gob.ec/instituciones) organiza las entidades públicas en secciones alfabéticas (`A` a `V`). En cada entrada muestra tres datos observados: **nombre oficial**, **sigla entre paréntesis** y **enlace a la ficha institucional**.

Respecto a las cuatro categorías del [ADR 0001](../adr/0001-alcance.md), se observa lo siguiente:

1. **Presidencia de la República:** registrada en la sección `P` como `Presidencia de la República (PR)` (en la sección `V` consta además `Vicepresidencia de la República (VPR)`).
2. **Ministerios:** en [`gob.ec/instituciones/M`](https://www.gob.ec/instituciones/M) aparecen **18 entradas ministeriales**. Coexisten los ministerios resultantes de fusiones recientes (`Ministerio de Ambiente y Energía (MAE)`, `Ministerio de Desarrollo Económico y Productivo (MDEP)`, `Ministerio de Educación, Deporte y Cultura (MINEDEC)`, `Ministerio de Desarrollo Humano (MDH)`, `Ministerio de Infraestructura y Tecnología (MIT)`) con denominaciones ministeriales previas que aún mantienen fichas de trámites activas (`MAGP`, `MC`, `MIDENA`, `MDG`, `MPCEI`, `MREMH`, `MSP`, `MINTEL`, `MT`, `MINTUR`, `MD`, `MDI` y `MCPGAD`).
3. **Institutos:** en [`gob.ec/instituciones/I`](https://www.gob.ec/instituciones/I) aparecen **20 entradas**: 16 institutos públicos sectoriales/de investigación, 3 institutos de seguridad social (`IESS`, `ISSPOL`, `ISSFA`) y 1 registro de prueba (`Institución prueba 2026 (IP2026)`). Adicionalmente, en la sección `S` consta el `Servicio Ecuatoriano de Normalización (INEN)`.
4. **Fuera de alcance:** el directorio lista explícitamente Gobiernos Autónomos Descentralizados en la sección `G` (68 GAD observados), Registros de la Propiedad en `R` (39), empresas públicas nacionales y municipales en `E` (27, como `EP PETROECUADOR`, `CELEC EP`, `CNEL`, `EMAPAO-EP`), Cuerpos de Bomberos en `C` y entidades de otras funciones del Estado (`Asamblea Nacional`, `Consejo de la Judicatura`, `CNE`, `Fiscalía General del Estado`, `Defensoría del Pueblo`, superintendencias).

## 3. Comparación entre la fuente propuesta y las alternativas

| Criterio | Fuente principal: `gob.ec/instituciones` | Alternativa 1: Catálogo y Directrices MEF / MDEP | Alternativa 2: `datosabiertos.gob.ec` (CKAN) | Alternativa 3: Directorio MT y portales sectoriales |
|---|---|---|---|---|
| **Completitud (cobertura de la planta central)** | **Alta a nivel nominal.** Cubre Presidencia, 18 entradas de ministerios, 19 institutos reales y más de 150 entidades fuera de alcance (GAD, empresas públicas, otras funciones). | **Parcial en web pública / completa en sistema interno.** La vista web pública muestra la cabecera ejecutiva vigente (10 ministerios activos, Vicepresidencia y 3 secretarías/centros), pero el catálogo detallado de entidades e institutos reside en el sistema autenticado eSIGEF y no se publica como archivo abierto. | **Parcial (sesgada por publicación).** Incluye solo a las ~98 instituciones que han publicado datasets en CKAN (por ejemplo, `IPIAP`, `IEPS`, `INEN`, `SERCOP`), omitiendo ministerios o institutos sin datasets activos en ese portal. | **Baja / sectorial.** El listado de capacitación del MT incluye solo 24 instituciones participantes; los portales como `ambienteyenergia.gob.ec` cubren únicamente su propio sector. |
| **Actualización (fusiones ministeriales 2026)** | **Acumulativa (sin depurar históricos).** Incluye los nuevos ministerios fusionados de 2026, pero conserva en la misma lista a los ministerios e institutos absorbidos (`MC`, `MD`, `MINTUR`, `ICCA`, `IFAIC`). | **Alta y depurada en cabecera.** La navegación oficial de `economicoproductivo.gob.ec` y `presidencia.gob.ec` refleja exactamente la estructura vigente de 10 carteras de Estado en 2026 (`MAE`, `MIDENA`, `MDEP`, `MINEDEC`, `MDG`, `MIT`, `MDI`, `MREMH`, `MSP`, `MT`), descartando carteras fusionadas. | **Mixta.** Aunque hay datasets actualizados en octubre de 2026, los nombres de las organizaciones conservan denominaciones previas a escisiones o fusiones recientes. | **Mixta.** Refleja denominaciones de 2026 en el MT, pero difiere entre su tabla web y su archivo `.xls` de marzo de 2026. |
| **Identificadores para cruzar con SERCOP (`buyer.id`, `buyer.name`)** | **Solo nombre oficial y sigla.** No publica RUC (`buyer.id`) ni código institucional MEF. | **Solo nombre oficial en la vista web pública.** Los códigos institucionales y RUC asociados a Unidades Ejecutoras pertenecen al sistema interno eSIGEF. | **Nombre y `slug` de organización.** No expone RUC ni código MEF en el índice de organizaciones. | **Nombre oficial, sigla y dominio web/correo institucional** en el archivo `.xls` y portales sectoriales; sin RUC. |
| **Relación padre-hijo (ministerio del que depende cada instituto)** | **No la muestra.** Es un directorio alfabético plano; las fichas individuales tampoco declaran en un campo estructurado el ministerio rector. | **No en la vista pública abierta.** La jerarquía presupuestaria completa está restringida a eSIGEF. | **No la muestra.** Lista horizontal de organizaciones sin atributo de entidad padre. | **Parcial por sector.** Los portales individuales de cada ministerio, estatutos orgánicos y acuerdos ministeriales sí declaran qué entidades están adscritas a esa cartera. |

## 4. Evaluación del criterio de dependencia ministerial (relación ministerio → instituto)

**Hallazgo observado:** ninguna de las fuentes generales de acceso público abierto (`gob.ec/instituciones`, `datosabiertos.gob.ec` ni la vista pública de `economicoproductivo.gob.ec`) expone un campo o tabla relacional que indique directamente de qué ministerio depende cada instituto adscrito.

- En [`gob.ec/instituciones/I`](https://www.gob.ec/instituciones/I), los institutos aparecen en una lista alfabética plana al mismo nivel que los ministerios de la sección `M`. Al inspeccionar fichas individuales como [`gob.ec/inamhi`](https://www.gob.ec/inamhi), se describe la misión institucional pero no existe un metadato con el ministerio de adscripción.
- Para establecer de qué ministerio depende cada instituto con respaldo oficial, es necesario complementar el listado nominal de `gob.ec/instituciones/I` con **fuentes normativas y portales sectoriales** (páginas de "Instituciones Relacionadas" de cada ministerio, estatutos orgánicos por procesos y decretos/acuerdos de creación o fusión, junto con la estructura vigente de 10 ministerios observada en `economicoproductivo.gob.ec`).

### Registro de institutos observados en `gob.ec/instituciones/I` y su adscripción de referencia

La siguiente tabla separa estrictamente el **nombre y sigla observados** en [`gob.ec/instituciones/I`](https://www.gob.ec/instituciones/I) de la **dependencia ministerial o clasificación sugerida** mediante cruce normativo/sectorial (sujeta a validación y aprobación del líder en la fase 1):

| # | Nombre observado en `gob.ec/instituciones/I` | Sigla observada | Muestra dependencia en `gob.ec` | Ministerio rector o clasificación de referencia (cruce normativo) | Observación para la semilla (`[PENDIENTE]` de aprobación) |
|---:|---|---|---|---|---|
| 1 | Instituto Geográfico Militar | `IGM` | No | Ministerio de Defensa Nacional (`MIDENA`) | Instituto adscrito al sector defensa. |
| 2 | Instituto Oceanográfico y Antártico de la Armada | `INOCAR` | No | Ministerio de Defensa Nacional (`MIDENA`) | Instituto adscrito al sector defensa (dominio `.mil.ec` en catálogo MT). |
| 3 | Instituto Nacional de Biodiversidad | `INABIO` | No | Ministerio de Ambiente y Energía (`MAE`) | Instituto adscrito al sector ambiental. |
| 4 | Instituto Nacional de Meteorología e Hidrología | `INAMHI` | No | Ministerio de Ambiente y Energía (`MAE`) | Instituto adscrito al sector hidrometeorológico/ambiental. |
| 5 | Instituto de Investigación Geológico y Energético | `IIGE` | No | Ministerio de Ambiente y Energía (`MAE`) | Instituto adscrito al sector geológico/energético. |
| 6 | Instituto Nacional de Donación y Trasplante de Órganos, Tejidos y Células | `INDOT` | No | Ministerio de Salud Pública (`MSP`) | Instituto adscrito al sector salud. |
| 7 | Instituto Nacional de Investigación en Salud Pública Dr. Leopoldo Izquieta Pérez | `INSPI` | No | Ministerio de Salud Pública (`MSP`) | Instituto adscrito al sector salud. |
| 8 | Instituto Nacional de Investigaciones Agropecuarias | `INIAP` | No | Ministerio de Agricultura, Ganadería y Pesca (`MAGP`) / `MDEP` | Confirmar ministerio vigente en 2026 tras fusión productiva. |
| 9 | Instituto Público de Investigación de Acuicultura y Pesca | `IPIAP` | No | Ministerio de Desarrollo Económico y Productivo (`MDEP`) / `MPCEI` | Instituto adscrito al sector acuícola/pesquero. |
| 10 | Instituto Nacional de Economía Popular y Solidaria | `IEPS` | No | Ministerio de Desarrollo Humano (`MDH`) / `MT` | Confirmar cartera rectora vigente en 2026. |
| 11 | Instituto Nacional de Evaluación Educativa | `INEVAL` | No | Ministerio de Educación, Deporte y Cultura (`MINEDEC`) | Entidad del sector educativo; confirmar si entra como instituto dependiente o régimen autónomo. |
| 12 | Instituto Nacional de Patrimonio Cultural | `INPC` | No | Ministerio de Educación, Deporte y Cultura (`MINEDEC` / ex `MC`) | Sector cultura, fusionado en `MINEDEC`. |
| 13 | Instituto de Cine y Creación Audiovisual | `ICCA` | No | Ministerio de Educación, Deporte y Cultura (`MINEDEC` / ex `MC`) | Fusionado históricamente en `IFCI`; sigue listado en `gob.ec`. |
| 14 | Instituto de Fomento a la Creatividad y la Innovación | `IFCI` | No | Ministerio de Educación, Deporte y Cultura (`MINEDEC` / ex `MC`) | Instituto adscrito al sector cultura. |
| 15 | Instituto de Fomento de las Artes, Innovación y Creatividades | `IFAIC` | No | Ministerio de Educación, Deporte y Cultura (`MINEDEC` / ex `MC`) | Denominación histórica vinculada a `IFCI`; sigue listado en `gob.ec`. |
| 16 | Instituto Nacional de Estadística y Censos | `INEC` | No | Presidencia de la República (`PR` / Planificación) | Adscrito a la rama de planificación (integrada en Presidencia). Confirmar categoría en el [ADR 0001](../adr/0001-alcance.md). |
| 17 | Instituto Ecuatoriano de Seguridad Social | `IESS` | No | Fuera de alcance (Seguridad Social) | Entidad autónoma con presupuesto fuera del PGE ([Directrices MEF](https://www.finanzas.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf)). |
| 18 | Instituto de Seguridad Social de la Policía Nacional | `ISSPOL` | No | Fuera de alcance (Seguridad Social) | Entidad autónoma de seguridad social, fuera del PGE. |
| 19 | Instituto de Seguridad Social de las Fuerzas Armadas | `ISSFA` | No | Fuera de alcance (Seguridad Social) | Entidad autónoma de seguridad social, fuera del PGE. |
| 20 | Institución prueba 2026 | `IP2026` | No | Fuera de alcance (registro técnico de prueba) | Registro de prueba observado en `gob.ec/instituciones/I`; debe excluirse. |

*Nota:* El `Servicio Ecuatoriano de Normalización (INEN)` aparece en la sección `S` de `gob.ec`, aunque conserva su sigla histórica de instituto y está adscrito al sector productivo (`MDEP` / ex `MPCEI`).

## 5. Recomendación de uso y puntos `[PENDIENTE]` para el líder

1. **Combinación recomendada para construir la semilla en fase 1:**
   - Usar **`gob.ec/instituciones`** como fuente base nominal (por listar de forma abierta la Presidencia, ministerios, institutos y entidades fuera de alcance con sus nombres y siglas).
   - Usar la cabecera institucional del **MEF / MDEP (`economicoproductivo.gob.ec`) y `presidencia.gob.ec`** para distinguir los **10 ministerios vigentes en 2026** de las carteras históricas pre-fusión que siguen apareciendo en `gob.ec/instituciones/M` y en descargas de SERCOP.
   - Documentar la columna de ministerio rector de cada instituto mediante **estatutos orgánicos / portales ministeriales**, dado que ninguna fuente abierta general publica ese vínculo de forma relacional.
2. **Cruce con `buyer.id` y `buyer.name` de SERCOP:** como se documenta en [reconocimiento.md](reconocimiento.md), los releases de SERCOP incluyen `buyer.id` y `buyer.name`. Dado que las fuentes oficiales abiertas consultadas no publican el RUC junto al catálogo jerárquico, la semilla `entity_classification.csv` de la fase 1 deberá vincularse inicialmente a partir de los valores reales de `buyer.id` y `buyer.name` observados en la fuente de SERCOP.
3. **Casos dudosos detectados (`[PENDIENTE]` de decisión del líder según [ADR 0001](../adr/0001-alcance.md)):**
   - **Ministerios fusionados (pre-2026 vs. 2026):** si los procesos de ministerios absorbidos (`MC`, `MD`, `MINTUR`, `MPCEI`, `MAGP`) se mantienen con su nombre original en la categoría `Ministerio` y cómo se agrupan frente a las 10 carteras vigentes.
   - **Institutos de Seguridad Social (`IESS`, `ISSFA`, `ISSPOL`):** aunque llevan la palabra "Instituto" en `gob.ec/instituciones/I`, son entidades autónomas fuera del Presupuesto General del Estado; se recomienda clasificarlos como `Fuera de alcance`.
   - **Secretarías, Agencias de Regulación (`ARCSA`, `ARCOTEL`, `ANT`, `ARCONEL`, etc.) y Servicios Nacionales (`SERCOP`, `SRI`, `SENAE`, `INEN`, `SECAP`):** definir si la categoría 3 se restringe literalmente a entidades con denominación de "Instituto" o si abarca otras entidades adscritas a ministerios.
   - **Entidades Operativas Desconcentradas (EOD):** hospitales, direcciones distritales o zonales que compran en SERCOP con RUC propio pero forman parte de un ministerio.

## 6. Estado de los criterios del issue #12

| Criterio del issue #12 | Estado en este documento |
|---|---|
| Al menos una fuente oficial propuesta, con enlace y fecha de consulta | Cumplido: `gob.ec/instituciones` (consultada el 15/10/2026), con enlaces verificados en la sección 1 |
| Comparada con una alternativa: qué tan completa y actualizada es cada una | Cumplido: comparada en la sección 3 con tres alternativas (MEF/MDEP, `datosabiertos.gob.ec` y MT/portales sectoriales) |
| Indica si la fuente muestra de qué ministerio depende cada instituto | Cumplido: la sección 4 documenta que los directorios generales abiertos no muestran esa relación y detalla cómo suplirla con fuentes normativas |
| Está en `docs/sources/entidades.md` | Cumplido: ubicado en `docs/sources/entidades.md` |