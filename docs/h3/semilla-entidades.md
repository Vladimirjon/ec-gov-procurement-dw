# Semilla de clasificación de entidades para DimEntidad

- **Estado:** propuesta. La semilla se generó y se midió el 22/11/2026. Los casos dudosos (sección 5) esperan la decisión del líder en el chat; hasta entonces quedan `sin_clasificar` y fuera de los indicadores (ADR 0001, regla 6).
- **Fecha:** 22/11/2026. **Equipo:** Grupo 5. **Sector:** gobierno central de Ecuador.
- **Fuente de:** `DimEntidad` y el filtro del sector en Power Query (#70, #71), el diseño de P1, P2 y P3 y la sección de diseño del PDF (#73 y #74).
- **Alcance de esta nota:** la regla de unión y de tipo, la semilla, su cobertura y los casos por decidir. La semilla **no se ha probado en Power BI Desktop**: la cobertura se calculó con Python sobre los CSV del portal.

## 1. Resumen

Los 6.100 `buyer_id` distintos de SERCOP (procesos fechados de 2021 a 2026) se cruzaron con el catálogo de instituciones del MDEP por `buyer_id` completo o por la raíz `EC-RUC-{13}`, nunca por nombre. De los 6.100, 5.429 cruzan (2.731 por valor exacto y 2.698 por raíz), 665 no cruzan y 6 están malformados.

Con la fecha del proceso (`releases.date`) entre 2021 y 2025, los 993.425 procesos quedan así: **28,38 % en el sector** (Presidencia, ministerio o instituto), 62,54 % fuera de alcance y **9,08 % sin clasificar**. En monto adjudicado (USD 28.187,17 millones): 19,83 % en el sector, 73,38 % fuera y **6,79 % sin clasificar**.

Lo que la semilla **no** resuelve y se declara: 557 casos (63 grupos del catálogo, 488 raíces sin cruce y 6 identificadores malformados) pesan 90.216 procesos y USD 1.914,71 millones en 2021 a 2025. La sección 5 trae los 50 más pesados con una recomendación firme cada uno; juntos cubren el 64,5 % de los procesos y el 89,7 % del monto que quedó sin clasificar.

## 2. La regla (párrafo para el PDF y las diapositivas)

**Párrafo para el PDF.** La clasificación de las entidades compradoras sigue una regla de alcance definida por el equipo, no una regla del curso. Cada comprador de SERCOP se identifica por su código `buyer.id`: se une primero por el valor completo y, si no coincide, por la raíz `EC-RUC` de 13 dígitos, nunca por el nombre. La unión se hace contra el catálogo oficial de instituciones del sector público del Ministerio de Economía y Finanzas, con corte al 31 de agosto de 2026. Del catálogo se toman el sector y la denominación de la cabecera de cada grupo presupuestario para asignar el tipo: Presidencia de la República, ministerio (con las unidades que dependen de él en el catálogo), instituto (por su denominación) o fuera de alcance (gobiernos autónomos descentralizados, empresas públicas, seguridad social, educación superior y otras funciones del Estado). Los compradores que no cruzan, que tienen un identificador malformado o que pertenecen a un grupo que no encaja en ninguna categoría quedan sin clasificar y fuera de los indicadores, y su peso se informa. Entre 2021 y 2025, tomando como fecha la del proceso, el 28,38 % de los procesos y el 19,83 % del monto adjudicado quedan en el sector, y el 9,08 % de los procesos y el 6,79 % del monto quedan sin clasificar.

**Versión para diapositiva.**

- Se une por `buyer.id` completo o por la raíz de 13 dígitos; nunca por nombre.
- El tipo sale del catálogo oficial (corte 31/08/2026): Presidencia, ministerio, instituto o fuera de alcance.
- Lo dudoso queda fuera de los indicadores: 9,08 % de los procesos y 6,79 % del monto de 2021 a 2025.

**Origen de la regla:** decisión de alcance del equipo registrada en el ADR 0001 (decisiones 1, 2, 6 y 7). No es una regla del curso. El criterio de tipo por denominación de la cabecera del catálogo es una elección del equipo, propuesta aquí y pendiente de aprobación (sección 5).

## 3. Cómo se construye

### 3.1. Entradas

| Entrada | Detalle | Origen |
|---|---|---|
| Catálogo de instituciones del MDEP | Hoja `CATÁLOGO`, corte al 31/08/2026; 3.140 filas con RUC; 8 filas de notas al pie omitidas | `docs/h2/fuente-entidades.md` |
| Procesos y adjudicaciones de SERCOP | `releases_AAAA.csv` y `awards_AAAA.csv`, años de archivo 2021 a 2025; fecha de negocio `releases.date`; monto del proceso = suma de sus adjudicaciones, vacío no es cero | decisión del líder del 21/11/2026 |
| Reglas de unión | ADR 0001, decisiones 6 y 7 | ADR 0001 |

### 3.2. Unión (sin usar nunca `buyer.name`)

1. **Exacta:** `buyer_id` es igual a `EC-RUC-{13}` de un RUC del catálogo (`match_type = exacta`).
2. **Por raíz:** `buyer_id` lleva sufijo de unidad (`EC-RUC-{13}-sufijo`) y su raíz de 13 dígitos consta en el catálogo (`match_type = raiz`). La raíz solo se acepta si cumple el patrón de 13 dígitos numéricos.
3. **Sin cruce o malformado:** la raíz no consta en el catálogo (`sin_cruce`) o el identificador no tiene la forma `EC-RUC-{13}` (`malformado`). Quedan `sin_clasificar`, estado `dudosa`.

Si un RUC consta en varias filas del catálogo con tipos distintos, queda `sin_clasificar` (ambigüedad). No ocurre en los datos: los 60 RUC repetidos (36 entre los grupos 280 y 315, 24 entre los grupos 130 y 360) son todos ministerios; conservan el tipo, se deja vacío el padre (`parent_entity`) y el grupo (`catalog_udaf`) para que una decisión por grupo no los alcance.

### 3.3. Tipo de entidad

El catálogo no trae el tipo. Se deduce del sector y de la denominación de la **cabecera** de cada grupo (`ENTIDAD`, con `EOD` 0 o 9999), nunca del nombre de SERCOP. Cada fila del catálogo hereda el tipo de su grupo y, si no es la cabecera, el nombre de la cabecera como `parent_entity`.

| Condición en el catálogo | Tipo | Estado | Origen |
|---|---|---|---|
| Sectores 121, 122, 123 (GAD), 211 y 212 (empresas públicas) | `fuera_de_alcance` | `aprobada` | ADR 0001, decisión 2 |
| Sector 111 con cabecera de Asamblea, Judicatura, Corte Constitucional, CNE, TCE, Fiscalía, Defensorías, Contraloría o CPCCS | `fuera_de_alcance` | `aprobada` | ADR 0001, decisión 2 (otras funciones del Estado) |
| Sector 111 con cabecera de Superintendencia, Procuraduría, Parlamento Andino o Secretaría Técnica de la Función de Transparencia | `fuera_de_alcance` | `propuesta` | criterio del equipo |
| Sectores 112 (educación superior), 221 (financieras públicas) y 311 (sociedades con participación pública) | `fuera_de_alcance` | `propuesta` | criterio del equipo |
| Sector 113 (seguridad social) | `fuera_de_alcance` | `propuesta` | Hito 1: exclusión provisional (ADR 0001, regla 6) |
| Sector 111, cabecera «Presidencia de la República» | `presidencia` | `propuesta` | catálogo y ADR 0001, decisión 1 |
| Sector 111, cabecera «Ministerio …» | `ministerio` | `propuesta` | catálogo y ADR 0001, decisión 1 |
| Sector 111, cabecera «Instituto …» | `instituto` | `propuesta` | criterio del equipo; la dependencia de un ministerio no está verificada |
| Cualquier otro grupo del sector 111 (Servicio, Agencia, Secretaría, Consejo, Policía, registros y similares) | `sin_clasificar` con `proposed_type` | `dudosa` | criterio del equipo; la decisión es del líder |

Esto responde a Q-E07: **no se filtra por `SECTOR == 111`**, que mezcla las cinco funciones del Estado; el sector solo es un dato de entrada de la regla anterior.

### 3.4. Hallazgos de H2 que la semilla aplica

| Hallazgo | Cómo se aplica |
|---|---|
| Q-E01: RUC del catálogo con 12 dígitos | 1.266 RUC se rellenan a 13 con cero a la izquierda; un RUC no numérico o de más de 13 dígitos se descarta |
| Q-E02: RUC repetidos y grano (ENTIDAD, EOD) | 3.140 filas dan 3.080 RUC distintos; se clasifica por RUC y se detectan los tipos contradictorios (ninguno) |
| Q-E03: títulos y notas al pie | se localiza la fila de encabezado (`SECTOR` y `RUC`) y se descartan las filas sin RUC |
| Q-E04: el catálogo es una foto al 31/08/2026 | `valid_from` y `valid_to` quedan vacíos: la fuente no los da, y no se inventan |
| Q-E05: procesos que no cruzan | 665 `buyer_id` sin cruce: 4,17 % de los procesos y 2,59 % del monto de 2021 a 2025 |
| Q-E06: monto con `buyer_id` con sufijo | la unión por raíz aporta el 20,79 % de los procesos y el 79,08 % del monto; sin esa regla quedaría sin cruzar el 79,08 % del monto |
| Q-E08: seis `buyer_id` malformados | `match_type = malformado`, sin raíz, 43 procesos, siempre fuera de los indicadores |
| Q-13: 425 variantes de escritura del nombre | `entity_name` sale del catálogo; si no cruza, de la grafía más frecuente de SERCOP para la raíz (`name_source`), una sola fila por `buyer_id` |

Las cifras de Q-E05 y Q-E06 de H2 se midieron sobre los 1.007.920 procesos sin acotar la fecha; aquí se acotan a 2021 a 2025 por `releases.date`, por eso difieren en décimas.

### 3.5. Columnas de `entity_classification.csv`

Una fila por `buyer_id` (6.100, sin duplicados de clave), ordenada por `buyer_id`.

| Columna | Contenido |
|---|---|
| `buyer_id`, `ruc_root` | clave de unión y raíz de 13 dígitos (vacía si está malformado) |
| `match_type` | `exacta`, `raiz`, `sin_cruce` o `malformado` |
| `catalog_udaf`, `catalog_eod` | grupo y unidad del catálogo (vacíos si no cruza o si el RUC está en varios grupos) |
| `entity_name`, `name_source` | nombre y su origen: `catalogo` o `sercop_nombre_mas_frecuente` |
| `entity_type` | `presidencia`, `ministerio`, `instituto`, `fuera_de_alcance` o `sin_clasificar` |
| `proposed_type` | recomendación para los grupos dudosos del catálogo; no cuenta como clasificación |
| `parent_entity` | cabecera del grupo, solo cuando es única y la fila no es la cabecera |
| `source` | criterio, norma o decisión que respalda la fila, y la foto del catálogo |
| `valid_from`, `valid_to` | vacíos: el catálogo no da vigencia (Q-E04) |
| `status` | `aprobada`, `propuesta` o `dudosa` |
| `note` | aclaración de la fila (por ejemplo, padre no único o RUC fuera del catálogo) |

Para los indicadores cuentan las filas con `entity_type` en `presidencia`, `ministerio` o `instituto`. Todo `sin_clasificar` queda fuera y se cuenta aparte.

### 3.6. Reproducir

El script usa solo la biblioteca estándar y no sobrescribe sus salidas: para repetir la corrida, las tres rutas de salida deben ser nuevas. Las rutas de entrada son las de la carpeta principal del repositorio (`data/` está ignorada por Git).

```powershell
python -I scripts/build_entity_seed.py `
  --catalog-xlsx "data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx" `
  --derived-dir data/derivados `
  --output-seed warehouse/seeds/entity_classification.csv `
  --output-coverage docs/h3/evidencia/cobertura-semilla-entidades-AAAAMMDD.json `
  --output-cases docs/h3/evidencia/casos-dudosos-semilla-entidades-AAAAMMDD.csv
```

La corrida dura unos diez segundos. Las pruebas (`tests/unit/test_build_entity_seed.py`) usan un catálogo y unos CSV inventados y cubren la unión exacta, por raíz, el nombre que nunca une y la ambigüedad.

## 4. Resultado

### 4.1. La semilla

| Indicador | Valor |
|---|---|
| Filas | 6.100 (`exacta` 2.731, `raiz` 2.698, `sin_cruce` 665, `malformado` 6) |
| Estados | `aprobada` 3.425, `propuesta` 1.621, `dudosa` 1.054 |
| Tipos (compradores) | `fuera_de_alcance` 3.846, `ministerio` 1.136, `instituto` 62, `presidencia` 2, `sin_clasificar` 1.054 |
| `sin_clasificar` | 383 de grupos dudosos del catálogo, 665 sin cruce, 6 malformados |
| RUC del catálogo | 3.080 distintos: 4 `presidencia`, 585 `ministerio`, 32 `instituto`, 2.243 `fuera_de_alcance`, 216 dudosos |
| Procesos por tipo de unión | exacta 75,04 %, raíz 20,79 %, sin cruce 4,17 %, malformado 0,004 % |
| Monto por tipo de unión | exacta 18,33 %, raíz 79,08 %, sin cruce 2,59 % |

Fuente: `docs/h3/evidencia/cobertura-semilla-entidades-20261122.json` y el recuento de la semilla, 22/11/2026.

### 4.2. Cobertura por tipo, 2021 a 2025

Procesos y monto de SERCOP por tipo de entidad, con el año de `releases.date`. El monto es la suma de las adjudicaciones de cada proceso; de los 993.425 procesos, 42.991 (4,33 %) no tienen importe adjudicado y no suman nada, porque vacío no es cero.

| Tipo de entidad | Procesos | % de procesos | Monto adjudicado (USD millones) | % del monto |
|---|---:|---:|---:|---:|
| Presidencia | 313 | 0,03 % | 41,12 | 0,15 % |
| Ministerio | 271.856 | 27,37 % | 5.417,74 | 19,22 % |
| Instituto | 9.759 | 0,98 % | 130,81 | 0,46 % |
| Fuera de alcance | 621.281 | 62,54 % | 20.682,79 | 73,38 % |
| Sin clasificar: grupo dudoso del catálogo | 48.768 | 4,91 % | 1.184,08 | 4,20 % |
| Sin clasificar: sin cruce con el catálogo | 41.405 | 4,17 % | 730,61 | 2,59 % |
| Sin clasificar: identificador malformado | 43 | 0,00 % | 0,02 | 0,00 % |
| **Total 2021 a 2025** | **993.425** | **100,00 %** | **28.187,17** | **100,00 %** |

### 4.3. Cobertura por año

Porcentaje de los procesos de cada año.

| Año de la fecha del proceso | Procesos | Presidencia | Ministerio | Instituto | En el sector (suma) | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 148.823 | 0,02 % | 30,68 % | 1,03 % | 31,73 % | 58,68 % | 9,59 % |
| 2022 | 206.801 | 0,06 % | 26,37 % | 1,04 % | 27,47 % | 63,00 % | 9,52 % |
| 2023 | 222.595 | 0,04 % | 28,61 % | 0,83 % | 29,47 % | 60,66 % | 9,87 % |
| 2024 | 217.422 | 0,01 % | 29,15 % | 1,00 % | 30,16 % | 61,52 % | 8,32 % |
| 2025 | 197.784 | 0,02 % | 22,55 % | 1,05 % | 23,61 % | 68,19 % | 8,19 % |
| 2021-2025 | 993.425 | 0,03 % | 27,37 % | 0,98 % | 28,38 % | 62,54 % | 9,08 % |
| 2026 | 14.495 | 0,05 % | 12,84 % | 0,43 % | 13,32 % | 81,01 % | 5,67 % |

Porcentaje del monto adjudicado de cada año.

| Año de la fecha del proceso | Monto adjudicado (USD millones) | Presidencia | Ministerio | Instituto | En el sector (suma) | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 2.468,69 | 0,07 % | 18,53 % | 0,32 % | 18,92 % | 75,23 % | 5,85 % |
| 2022 | 5.752,22 | 0,12 % | 16,91 % | 0,41 % | 17,44 % | 74,80 % | 7,76 % |
| 2023 | 6.934,07 | 0,13 % | 21,49 % | 0,56 % | 22,18 % | 70,69 % | 7,13 % |
| 2024 | 6.626,35 | 0,04 % | 19,55 % | 0,50 % | 20,08 % | 72,42 % | 7,49 % |
| 2025 | 6.405,83 | 0,33 % | 18,77 % | 0,43 % | 19,53 % | 75,28 % | 5,19 % |
| 2021-2025 | 28.187,17 | 0,15 % | 19,22 % | 0,46 % | 19,83 % | 73,38 % | 6,79 % |
| 2026 | 2.765,71 | 0,21 % | 7,54 % | 0,13 % | 7,89 % | 87,94 % | 4,18 % |

Detalle de lo que queda sin clasificar.

| Año de la fecha del proceso | Dudosos del catálogo (procesos) | Sin cruce (procesos) | Malformados (procesos) | Dudosos del catálogo (monto) | Sin cruce (monto) | Sin clasificar en total (USD millones) |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 5,05 % | 4,53 % | 0,00 % | 3,31 % | 2,54 % | 144,39 |
| 2022 | 5,07 % | 4,45 % | 0,00 % | 4,24 % | 3,52 % | 446,24 |
| 2023 | 5,26 % | 4,60 % | 0,01 % | 4,63 % | 2,50 % | 494,69 |
| 2024 | 4,48 % | 3,83 % | 0,00 % | 5,10 % | 2,40 % | 496,62 |
| 2025 | 4,71 % | 3,48 % | 0,00 % | 3,12 % | 2,08 % | 332,76 |
| 2021-2025 | 4,91 % | 4,17 % | 0,00 % | 4,20 % | 2,59 % | 1.914,71 |
| 2026 | 3,41 % | 2,26 % | 0,00 % | 2,91 % | 1,27 % | 115,56 |

Los 14.495 procesos con fecha de 2026 no entran en `DimTiempo` (ventana 2021-01 a 2025-12, decisión del diseño dimensional) y no están en los totales de 2021 a 2025; se muestran aparte para que la semilla cubra todos los `buyer_id` descargados. Con la fecha del archivo en lugar de `releases.date` las cifras por año serían otras (Q-10); la fecha de negocio ya está decidida.

La participación en el sector baja en 2025 (23,61 % de los procesos) frente a 2021 a 2024 (27,47 % a 31,73 %). La semilla no explica esa caída: no se investigó si viene de la fusión de ministerios de 2025 y 2026 o del crecimiento de otras entidades. Queda señalada, no resuelta.

## 5. Casos dudosos

### 5.1. Cómo se eligieron

Un caso es un grupo del catálogo (UDAF), una raíz sin cruce o un identificador malformado. Se ordenan por peso, que es la suma de su participación en los procesos y de su participación en el monto de 2021 a 2025. Hay 557 casos (63 grupos del catálogo, 488 raíces sin cruce, 6 malformados). La lista corta toma los 50 primeros. La columna «Origen» dice si el caso viene de un grupo del catálogo o de una raíz que no cruzó; en este segundo caso el nombre es la grafía más frecuente de SERCOP y sirve solo para sustentar la recomendación, nunca para unir.

**Criterio de las recomendaciones** (elección del equipo, lectura literal de la decisión de alcance 1: «Presidencia, ministerios e institutos que dependen de ellos»): entra solo lo que es Presidencia, ministerio o instituto, o lo que el propio catálogo coloca dentro de su estructura; todo lo demás sale. Una recomendación `dudosa` significa que ninguna fuente revisada acredita la dependencia y clasificar sería inventar.

### 5.2. Lista corta de 50 casos

Peso de la lista: 58.154 procesos (5,85 % de los procesos de 2021 a 2025) y USD 1.717,81 millones (6,09 % del monto).

| N° | Caso | Clave | Origen | Procesos | Monto (USD millones) | Recomendación | Bloque |
|---:|---|---|---|---:|---:|---|---|
| 1 | Policía Nacional (Comandancia General y sus unidades) | UDAF 52 | catálogo | 15.028 | 247,77 | fuera | B2 |
| 2 | Servicio Nacional de Atención Integral a Personas Privadas de la Libertad y a Adolescentes Infractores | UDAF 578 | catálogo | 461 | 172,37 | fuera | B1 |
| 3 | Servicio de Rentas Internas (SRI) | UDAF 135 | catálogo | 3.800 | 62,03 | fuera | B1 |
| 4 | Dirección General de Registro Civil, Identificación y Cedulación | UDAF 51 | catálogo | 1.063 | 137,01 | fuera | B1 |
| 5 | Cuerpo de Ingenieros del Ejército | RUC 1768007040001 | sin cruce | 2.608 | 89,52 | dudosa | B3 |
| 6 | Dirección Nacional de Salud de la Policía Nacional | UDAF 58 | catálogo | 2.951 | 65,32 | fuera | B2 |
| 7 | Hospital de Especialidades de las Fuerzas Armadas No. 1 | UDAF 74 | catálogo | 2.186 | 81,84 | fuera | B3 |
| 8 | Agencia de Regulación y Control Fito y Zoosanitario | UDAF 334 | catálogo | 3.207 | 18,93 | fuera | B1 |
| 9 | Servicio Integrado de Seguridad ECU 911 | UDAF 266 | catálogo | 2.366 | 41,80 | fuera | B1 |
| 10 | Fundación Municipal Guayaquil Siglo XXI | RUC 0992183721001 | sin cruce | 692 | 88,15 | fuera | B6 |
| 11 | Autoridad Aeroportuaria de Guayaquil (fundación municipal) | RUC 0992179619001 | sin cruce | 388 | 89,95 | fuera | B6 |
| 12 | Casa de la Cultura Ecuatoriana Benjamín Carrión | UDAF 250 | catálogo | 3.080 | 4,95 | fuera | B1 |
| 13 | Secretaría Técnica de Gestión Inmobiliaria del Sector Público | RUC 1768146750001 | sin cruce | 622 | 48,87 | fuera | B1 |
| 14 | Fundación Terminal Terrestre de Guayaquil | RUC 0992236574001 | sin cruce | 712 | 44,03 | fuera | B6 |
| 15 | Secretaría Nacional de Gestión de Riesgos | UDAF 34 | catálogo | 1.189 | 25,69 | fuera | B1 |
| 16 | Agencia Nacional de Regulación y Control del Transporte Terrestre | UDAF 69 | catálogo | 244 | 52,41 | fuera | B1 |
| 17 | Corporación para la Seguridad Ciudadana de Guayaquil | RUC 0992457597001 | sin cruce | 334 | 40,87 | fuera | B6 |
| 18 | Comisión de Tránsito del Ecuador | UDAF 68 | catálogo | 370 | 39,06 | fuera | B1 |
| 19 | Dirección Nacional de la Policía Judicial | UDAF 57 | catálogo | 928 | 17,46 | fuera | B2 |
| 20 | Dirección General de Aviación Civil | UDAF 522 | catálogo | 426 | 29,40 | fuera | B1 |
| 21 | Secretaría de Educación Superior, Ciencia, Tecnología e Innovación | RUC 1768157600001 | sin cruce | 294 | 30,40 | fuera | B1 |
| 22 | Aceros Nacionales del Ecuador S.A. (ANDEC) | RUC 0990001340001 | sin cruce | 631 | 20,10 | fuera | B6 |
| 23 | Agencia de Regulación, Control y Vigilancia Sanitaria (ARCSA) | UDAF 217 | catálogo | 1.168 | 2,97 | fuera | B1 |
| 24 | Dirección Nacional de Registros Públicos | UDAF 511 | catálogo | 981 | 8,18 | fuera | B1 |
| 25 | Consejo de Gobierno del Régimen Especial de Galápagos | UDAF 45 | catálogo | 416 | 23,80 | fuera | B1 |
| 26 | Dirección Zonal 8 de la Secretaría Técnica de Gestión Inmobiliaria | RUC 0968604550001 | sin cruce | 371 | 23,14 | fuera | B1 |
| 27 | Servicio Nacional de Aduana del Ecuador (SENAE) | UDAF 136 | catálogo | 420 | 20,33 | fuera | B1 |
| 28 | Fundación Municipal de la Mujer y el Niño de Cuenca | RUC 0190408485001 | sin cruce | 989 | 3,03 | fuera | B6 |
| 29 | Servicio Nacional de Medicina Legal y Ciencias Forenses | UDAF 229 | catálogo | 351 | 20,27 | fuera | B1 |
| 30 | Fundación Museos de la Ciudad | RUC 1792042704001 | sin cruce | 770 | 7,51 | fuera | B6 |
| 31 | Dirección Distrital 10D02 Antonio Ante-Otavalo (Salud) | RUC 1060040130001 | sin cruce | 747 | 6,97 | dentro: ministerio | B5 |
| 32 | Corporación de Promoción Económica CONQUITO | RUC 1791905911001 | sin cruce | 801 | 2,20 | fuera | B6 |
| 33 | Ministerio de Turismo | RUC 1760009020001 | sin cruce | 283 | 15,86 | dentro: ministerio | B4 |
| 34 | Comando de Inteligencia Militar Conjunto de las Fuerzas Armadas | RUC 1768184250001 | sin cruce | 653 | 4,92 | dudosa | B3 |
| 35 | Secretaría Técnica Ecuador Crece Sin Desnutrición Infantil | RUC 1768143140001 | sin cruce | 264 | 15,89 | fuera | B1 |
| 36 | Corporación Registro Civil de Guayaquil | RUC 0992441127001 | sin cruce | 309 | 14,40 | fuera | B6 |
| 37 | FAME S.A. | RUC 1790932966001 | sin cruce | 577 | 5,97 | fuera | B6 |
| 38 | Ministerio del Ambiente, Agua y Transición Ecológica | RUC 1768192860001 | sin cruce | 615 | 4,71 | dentro: ministerio | B4 |
| 39 | Parque Nacional Galápagos | UDAF 330 | catálogo | 282 | 14,15 | fuera | B1 |
| 40 | Dirección Distrital 10D03 Cotacachi (Salud) | RUC 1060014130001 | sin cruce | 704 | 1,64 | dentro: ministerio | B5 |
| 41 | Fundación Teatro Nacional Sucre | RUC 1791984714001 | sin cruce | 584 | 4,22 | fuera | B6 |
| 42 | Agencia de Regulación y Control de las Telecomunicaciones (ARCOTEL) | UDAF 90 | catálogo | 417 | 8,90 | fuera | B1 |
| 43 | Operador Nacional de Electricidad (CENACE) | UDAF 95 | catálogo | 345 | 9,27 | fuera | B1 |
| 44 | Servicio Público para Pago de Accidentes de Tránsito | UDAF 222 | catálogo | 218 | 12,83 | fuera | B1 |
| 45 | Ministerio del Deporte | RUC 1760006350001 | sin cruce | 353 | 7,91 | dentro: ministerio | B4 |
| 46 | Ministerio de Cultura y Patrimonio | RUC 1768135120001 | sin cruce | 223 | 11,26 | dentro: ministerio | B4 |
| 47 | Federación Deportiva del Guayas | RUC 0990057907001 | sin cruce | 374 | 6,73 | fuera | B6 |
| 48 | Fideicomiso Fondo Ambiental para la Protección del Agua | RUC 1791722205001 | sin cruce | 517 | 2,63 | fuera | B6 |
| 49 | Casa Militar Presidencial | UDAF 85 | catálogo | 466 | 3,90 | dentro: presidencia | B7 |
| 50 | Ministerio de la Mujer y Derechos Humanos | RUC 1768137410001 | sin cruce | 376 | 6,29 | dentro: ministerio | B4 |

### 5.3. Los bloques y su motivo

| Bloque | Qué reúne | Motivo de la recomendación |
|---|---|---|
| B1 | Organismos del Ejecutivo con figura propia: servicios, agencias, secretarías, consejos, direcciones generales, autoridades, casas, operadores, comisiones y parques | No son Presidencia, ministerio ni instituto por su denominación. El catálogo les da un grupo presupuestario propio y no los coloca bajo ningún ministerio. La sección 5.3 de `docs/sources/entidades.md` dejó abierta esta categoría. |
| B2 | Policía Nacional (3 casos) | Tiene grupo propio en el catálogo (Comandancia General) y no figura bajo ningún ministerio. Su dependencia legal no está verificada en las fuentes del repositorio. |
| B3 | Fuerzas Armadas fuera del grupo del Ministerio de Defensa | El hospital tiene grupo propio: `fuera`, igual que B1. Las dos unidades militares sin cruce quedan `dudosa`: ninguna fuente revisada acredita su dependencia. El grupo del Ministerio de Defensa del catálogo (UDAF 70, 119 filas) sí queda dentro como ministerio. |
| B4 | Ministerios históricos cuyo RUC no consta en el catálogo | La denominación de SERCOP es de ministerio y el catálogo del 31/08/2026 no los trae (nota 5 del archivo: excluye RUC pasivos; fusiones de 2025 y 2026, caso ya señalado en `docs/sources/entidades.md`, sección 5.3). Se aprueban por RUC. Su vigencia (`valid_to`) se desconoce. |
| B5 | Direcciones distritales de salud sin RUC en el catálogo | El catálogo trae 74 direcciones distritales de salud bajo el Ministerio de Salud Pública (UDAF 320); estas dos tienen la misma forma y no constan. Se aprueban por RUC, con ese ministerio como padre. |
| B6 | Fundaciones, corporaciones y empresas locales, federaciones deportivas, sociedades anónimas y un fideicomiso | No son Presidencia, ministerio ni instituto. La mayoría son entes de municipios (GAD, fuera por la decisión de alcance 2) o personas jurídicas privadas. |
| B7 | Casa Militar Presidencial | Órgano de la Presidencia por su denominación; el catálogo le da un grupo propio. La Vicepresidencia (puesto 120, 161 procesos, USD 0,99 millones) recibe la misma recomendación. |

Peso de cada bloque y recomendación:

| Bloque y recomendación | Casos | Procesos | % de procesos | Monto (USD millones) | % del monto |
|---|---:|---:|---:|---:|---:|
| B1: fuera | 23 | 22.355 | 2,25 % | 822,67 | 2,92 % |
| B2: fuera | 3 | 18.907 | 1,90 % | 330,55 | 1,17 % |
| B3: dudosa | 2 | 3.261 | 0,33 % | 94,44 | 0,34 % |
| B3: fuera | 1 | 2.186 | 0,22 % | 81,84 | 0,29 % |
| B4: dentro: ministerio | 5 | 1.850 | 0,19 % | 46,03 | 0,16 % |
| B5: dentro: ministerio | 2 | 1.451 | 0,15 % | 8,61 | 0,03 % |
| B6: fuera | 13 | 7.678 | 0,77 % | 329,78 | 1,17 % |
| B7: dentro: presidencia | 1 | 466 | 0,05 % | 3,90 | 0,01 % |
| **Los 50 casos** | **50** | **58.154** | **5,85 %** | **1.717,81** | **6,09 %** |

Los otros 507 casos pesan 32.062 procesos (3,23 %) y USD 196,89 millones (0,70 %). Quedan sin clasificar y su peso queda a la vista (limitación declarada, sección 6). Doce de ellos son ministerios históricos y direcciones zonales del Ministerio del Ambiente sin cruce (1.516 procesos, USD 6,77 millones) que recibirían la recomendación de B4 por analogía.

### 5.4. Decisiones que se piden al líder

| N° | Decisión | Recomendación | Efecto |
|---|---|---|---|
| D1 | Aprobar las recomendaciones de los 50 casos (B1 a B7). | Aprobar. | Los casos «dentro» pasan a `ministerio` o `presidencia`; los «fuera» pasan a `fuera_de_alcance`; las `dudosa` siguen fuera de los indicadores. |
| D2 | Policía Nacional (B2, 18.907 procesos, USD 330,55 millones). | `fuera`, por la misma razón que B1. La alternativa es `dentro` como `ministerio` si el líder acepta su dependencia de un ministerio; subiría el sector en 1,90 puntos de procesos y 1,17 de monto. | Es el caso de mayor peso. |
| D3 | Aprobar el criterio de las filas `propuesta`: ministerio por cabecera, instituto por denominación, Presidencia, y los `fuera_de_alcance` que no vienen del ADR (educación superior, seguridad social, financieras, sociedades, superintendencias, Procuraduría, Parlamento Andino). | Aprobar. Los institutos quedan con la salvedad de que su dependencia no está verificada. | 1.621 filas pasan de `propuesta` a `aprobada`. |
| D4 | Extender B4 por analogía a los 12 casos restantes (ministerios históricos y direcciones zonales del Ministerio del Ambiente sin cruce). | Aprobar. | 1.516 procesos y USD 6,77 millones más en el sector. |

Efecto simulado de aprobar B4, B5 y B7 (suma de los casos, no una nueva corrida): el sector pasaría del 28,38 % al 28,76 % de los procesos y del 19,83 % al 20,04 % del monto; con D4, al 28,91 % y al 20,06 %. Lo demás de la lista cambia el tipo a `fuera_de_alcance` sin mover el sector.

## 6. Límites declarados

- **El catálogo es una foto al 31/08/2026** (Q-E04). No da vigencia: los procesos de 2021 a 2025 se clasifican con la entidad que el catálogo lista hoy. `valid_from` y `valid_to` están vacíos y la vigencia por fecha (SCD tipo 2) queda para el Hito 4.
- **Los institutos se identifican por su denominación.** El catálogo no dice de qué ministerio dependen; la dependencia no se verificó con norma (`docs/sources/entidades.md`, sección 4).
- **Quedan sin clasificar** 9,08 % de los procesos y 6,79 % del monto de 2021 a 2025. De esa parte, los 50 casos de la lista son el 64,5 % de los procesos y el 89,7 % del monto; los otros 507 casos pesan 3,23 % de los procesos y 0,70 % del monto del total.
- **Las raíces sin cruce no tienen tipo en ninguna fuente revisada.** La denominación de SERCOP sustenta una recomendación, pero la clasificación exige la decisión del líder por RUC.
- **El nombre de las entidades sin cruce** es la grafía más frecuente de SERCOP, no un nombre oficial (Q-13).
- **La semilla incluye 14.495 procesos de 2026** que `DimTiempo` deja fuera; los totales de este documento son de 2021 a 2025.
- **No se probó en Power BI Desktop.** La unión en Power Query y los totales de control con la semilla aplicada se verifican al construir el modelo.

## 7. Segunda pasada: cómo queda registrada la decisión del líder

La decisión se escribe en un archivo de decisiones y se reaplica con el mismo script, con la opción `--overrides` y salidas nuevas. Cada fila lleva `scope` (`udaf` para un grupo del catálogo o `ruc_root` para una raíz), `key`, `entity_type`, `decided_on` y `decision_note`. Las filas alcanzadas pasan a `aprobada` y su `source` cita la decisión. Un identificador malformado nunca se toca; un RUC que consta en varios grupos solo se decide por `ruc_root`. La decisión del líder en el chat y el archivo de decisiones se commitean juntos; mientras eso no ocurra, este issue queda abierto.

## 8. Estado de los criterios del issue #68

| Criterio | Estado |
|---|---|
| La semilla existe, sin duplicados de clave, con `source` y `status` en cada fila | Cumplido: 6.100 filas, clave `buyer_id` única (prueba y revisión de la salida) |
| La unión nunca usa `buyer.name`; probada | Cumplido: pruebas de unión exacta, por raíz, nombre que no une y ambigüedad |
| Lista de casos dudosos con recomendación; decisión del líder registrada y reflejada en la semilla | **Pendiente:** la lista y las recomendaciones están (sección 5); falta la decisión del líder y la segunda pasada |
| Cobertura medida y escrita | Cumplido (sección 4) |
| Lo no clasificado queda fuera de los indicadores con su peso a la vista | Cumplido (secciones 4 y 6) |
| La regla en un párrafo con su origen | Cumplido (sección 2) |
| `ruff` y `pytest` en verde | Ver el PR |
