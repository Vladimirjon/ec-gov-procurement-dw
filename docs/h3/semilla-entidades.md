# Semilla de clasificación de entidades para DimEntidad

- **Estado:** semilla generada y medida el 22/11/2026, con las decisiones del líder de ese día aplicadas (sección 5.4). Quedan pendientes los casos de las secciones 5.5 y 5.6; mientras tanto siguen `sin_clasificar` y fuera de los indicadores (ADR 0001, regla 6).
- **Fecha:** 22/11/2026. **Equipo:** Grupo 5. **Sector:** gobierno central de Ecuador.
- **Fuente de:** `DimEntidad` y el filtro del sector en Power Query (#70, #71), el diseño de P1, P2 y P3 y la sección de diseño del PDF (#73 y #74).
- **Alcance de esta nota:** la regla de unión, de tipo y de admisión, la semilla, su cobertura y los casos por decidir. La semilla **no se ha probado en Power BI Desktop**: la cobertura se calculó con Python sobre los CSV del portal.

## 1. Resumen

Los 6.100 `buyer_id` distintos de SERCOP (procesos fechados de 2021 a 2026) se cruzaron con el catálogo de instituciones del MDEP por `buyer_id` completo o por la raíz `EC-RUC-{13}`, nunca por nombre. De los 6.100, 5.429 cruzan, 665 no cruzan y 6 están malformados.

**Qué cuenta como «en el sector».** `FactContratacion` admite solo los procesos cuyo comprador es Presidencia, ministerio o instituto **con estado `aprobada`** (diseño dimensional, sección 6.5). Una clasificación `propuesta` o `dudosa` queda fuera. La primera versión de esta nota contaba las propuestas como sector (28,38 % de los procesos y 19,83 % del monto), lo que no corresponde a esa regla; las cifras de abajo ya usan la regla de admisión.

Con la fecha del proceso (`releases.date`) entre 2021 y 2025, de los 993.425 procesos y USD 28.187,17 millones: **27,54 % de los procesos y 19,40 % del monto quedan admitidos en el sector** (273.620 procesos y USD 5.467,46 millones), 64,47 % de los procesos y 74,56 % del monto quedan fuera de alcance y **7,99 % de los procesos y 6,04 % del monto quedan sin clasificar**.

Lo que la semilla **no** resuelve y se declara: 566 casos (74 grupos del catálogo, 486 raíces sin cruce y 6 identificadores malformados) pesan 79.353 procesos y USD 1.703,80 millones. Entre ellos están los institutos (sin respaldo de adscripción: 9.495 procesos y USD 128,24 millones) y los ministerios históricos que no constan en el catálogo (3.366 procesos y USD 52,80 millones). La sección 5 trae los 50 casos más pesados con una recomendación cada uno.

## 2. La regla (párrafo para el PDF y las diapositivas)

**Párrafo para el PDF.** La clasificación de las entidades compradoras sigue una regla de alcance definida por el equipo, no una regla del curso. Cada comprador de SERCOP se identifica por su código `buyer.id`: se une primero por el valor completo y, si no coincide, por la raíz `EC-RUC` de 13 dígitos, nunca por el nombre. La unión se hace contra el catálogo oficial de instituciones del sector público del Ministerio de Economía y Finanzas, con corte al 31 de agosto de 2026. Del catálogo se toman el sector y la denominación de la cabecera de cada grupo presupuestario para proponer el tipo: Presidencia de la República, ministerio (con las unidades que dependen de él en el catálogo) o fuera de alcance (gobiernos autónomos descentralizados, empresas públicas, seguridad social, Policía Nacional y otras funciones del Estado). Solo entran en los indicadores los compradores de Presidencia o de un ministerio con clasificación aprobada. Los institutos, los compradores que no cruzan, los que tienen un identificador malformado y los de grupos que no encajan en ninguna categoría quedan sin clasificar y fuera de los indicadores, y su peso se informa. Entre 2021 y 2025, tomando como fecha la del proceso, el 27,54 % de los procesos y el 19,40 % del monto adjudicado quedan en el sector, y el 7,99 % de los procesos y el 6,04 % del monto quedan sin clasificar.

**Versión para diapositiva.**

- Se une por `buyer.id` completo o por la raíz de 13 dígitos; nunca por nombre.
- El tipo sale del catálogo oficial (corte 31/08/2026) y solo cuenta lo aprobado: Presidencia y ministerios.
- Lo dudoso queda fuera de los indicadores: 7,99 % de los procesos y 6,04 % del monto de 2021 a 2025.

**Origen de la regla:** decisión de alcance del equipo registrada en el ADR 0001 (decisiones 1, 2, 6 y 7). No es una regla del curso. El criterio de tipo por denominación de la cabecera del catálogo es una elección del equipo.

## 3. Cómo se construye

### 3.1. Entradas

| Entrada | Detalle | Origen |
|---|---|---|
| Catálogo de instituciones del MDEP | Hoja `CATÁLOGO`, corte al 31/08/2026; 3.140 filas con RUC; 8 filas de notas al pie omitidas | `docs/h2/fuente-entidades.md` |
| Procesos y adjudicaciones de SERCOP | `releases_AAAA.csv` y `awards_AAAA.csv`, años de archivo 2021 a 2025; fecha de negocio `releases.date`; monto del proceso = suma de sus adjudicaciones, vacío no es cero | decisión del líder del 21/11/2026 |
| Reglas de unión | ADR 0001, decisiones 6 y 7 | ADR 0001 |
| Decisiones del líder | `warehouse/seeds/entity_classification_decisions.csv`, aplicadas con `--overrides` | sección 5.4 |

### 3.2. Unión (sin usar nunca `buyer.name`)

1. **Exacta:** `buyer_id` es igual a `EC-RUC-{13}` de un RUC del catálogo (`match_type = exacta`).
2. **Por raíz:** `buyer_id` lleva sufijo de unidad (`EC-RUC-{13}-sufijo`) y su raíz de 13 dígitos consta en el catálogo (`match_type = raiz`). La raíz solo se acepta si cumple el patrón de 13 dígitos numéricos.
3. **Sin cruce o malformado:** la raíz no consta en el catálogo (`sin_cruce`) o el identificador no tiene la forma `EC-RUC-{13}` (`malformado`). Quedan `sin_clasificar`, estado `dudosa`.

Si un RUC consta en varias filas del catálogo con resultados distintos, queda `sin_clasificar` (ambigüedad). No ocurre en los datos: los 60 RUC repetidos (36 entre los grupos 280 y 315, 24 entre los grupos 130 y 360) son todos ministerios; conservan el tipo, se deja vacío el padre (`parent_entity`) y el grupo (`catalog_udaf`) para que una decisión por grupo no los alcance. El script falla si, tras aplicar decisiones, los `buyer_id` de una misma raíz quedan con clasificaciones distintas, que es la regla 3 de la secuencia de asignación del diseño.

### 3.3. Tipo de entidad propuesto

El catálogo no trae el tipo. Se deduce del sector y de la denominación de la **cabecera** de cada grupo (`ENTIDAD`, con `EOD` 0 o 9999), nunca del nombre de SERCOP. Cada fila del catálogo hereda el tipo de su grupo y, si no es la cabecera, el nombre de la cabecera como `parent_entity`. La tabla muestra el resultado de la regla **antes** de las decisiones del líder.

| Condición en el catálogo | Tipo | Estado | Origen |
|---|---|---|---|
| Sectores 121, 122, 123 (GAD), 211 y 212 (empresas públicas) | `fuera_de_alcance` | `aprobada` | ADR 0001, decisión 2 |
| Sector 111 con cabecera de Asamblea, Judicatura, Corte Constitucional, CNE, TCE, Fiscalía, Defensorías, Contraloría o CPCCS | `fuera_de_alcance` | `aprobada` | ADR 0001, decisión 2 (otras funciones del Estado) |
| Sector 111 con cabecera de Superintendencia, Procuraduría, Parlamento Andino o Secretaría Técnica de la Función de Transparencia | `fuera_de_alcance` | `propuesta` | criterio del equipo |
| Sectores 112 (educación superior), 221 (financieras públicas) y 311 (sociedades con participación pública) | `fuera_de_alcance` | `propuesta` | criterio del equipo |
| Sector 113 (seguridad social) | `fuera_de_alcance` | `propuesta` | Hito 1: exclusión provisional (ADR 0001, regla 6) |
| Sector 111, cabecera «Presidencia de la República» | `presidencia` | `propuesta` | catálogo y ADR 0001, decisión 1 |
| Sector 111, cabecera «Ministerio …» | `ministerio` | `propuesta` | catálogo y ADR 0001, decisión 1 |
| Sector 111, cabecera «Instituto …» | `sin_clasificar` con `proposed_type = instituto` | `dudosa` | la denominación no prueba la adscripción a un ministerio (ADR 0001, decisión 1); falta respaldo |
| Cualquier otro grupo del sector 111 (Servicio, Agencia, Secretaría, Consejo, Policía, registros y similares) | `sin_clasificar` con `proposed_type` | `dudosa` | criterio del equipo; la decisión es del líder |

Esto responde a Q-E07: **no se filtra por `SECTOR == 111`**, que mezcla las cinco funciones del Estado; el sector solo es un dato de entrada de la regla anterior.

### 3.4. Hallazgos de H2 que la semilla aplica

| Hallazgo | Cómo se aplica |
|---|---|
| Q-E01: RUC del catálogo con 12 dígitos | 1.266 RUC se rellenan a 13 con cero a la izquierda; un RUC no numérico o de más de 13 dígitos se descarta |
| Q-E02: RUC repetidos y grano (ENTIDAD, EOD) | 3.140 filas dan 3.080 RUC distintos; se clasifica por RUC y se detectan los resultados contradictorios (ninguno) |
| Q-E03: títulos y notas al pie | se localiza la fila de encabezado (`SECTOR` y `RUC`) y se descartan las filas sin RUC |
| Q-E04: el catálogo es una foto al 31/08/2026 | `valid_from` y `valid_to` quedan vacíos: la fuente no los da, y no se inventan |
| Q-E05: procesos que no cruzan | 665 `buyer_id` sin cruce en la unión (4,17 % de los procesos y 2,59 % del monto de 2021 a 2025); cuatro de ellos, los de dos distritos de salud, se resolvieron por decisión (D1) y quedan 661 sin clasificar (4,02 % y 2,56 %) |
| Q-E06: monto con `buyer_id` con sufijo | la unión por raíz aporta el 20,79 % de los procesos y el 79,08 % del monto; sin esa regla quedaría sin cruzar el 79,08 % del monto |
| Q-E07: el sector 111 mezcla las funciones del Estado | el tipo sale de la cabecera del grupo, no del sector (sección 3.3) |
| Q-E08: seis `buyer_id` malformados | `match_type = malformado`, sin raíz, 43 procesos, siempre fuera de los indicadores |
| Q-13: 425 variantes de escritura del nombre | `entity_name` sale del catálogo; si no cruza, de la grafía más frecuente de SERCOP para la raíz (`name_source`), una sola fila por `buyer_id` |

Las cifras de Q-E05 y Q-E06 de H2 se midieron sobre los 1.007.920 procesos sin acotar la fecha; aquí se acotan a 2021 a 2025 por `releases.date`, por eso difieren en décimas.

### 3.5. Regla de admisión en el sector

Un proceso entra en el sector si el comprador tiene `entity_type` en `presidencia`, `ministerio` o `instituto` **y** `status = aprobada`. `propuesta` y `dudosa` quedan fuera; también `fuera_de_alcance` y todo `sin_clasificar`. Es la misma regla que aplica Power Query en la secuencia de asignación de `IdEntidad` (diseño dimensional, sección 6.5). La cobertura de la sección 4 usa esa regla.

### 3.6. Columnas de `entity_classification.csv`

Una fila por `buyer_id` (6.100, sin duplicados de clave), ordenada por `buyer_id`.

| Columna | Contenido |
|---|---|
| `buyer_id`, `ruc_root` | clave de unión y raíz de 13 dígitos (vacía si está malformado) |
| `match_type` | `exacta`, `raiz`, `sin_cruce` o `malformado` |
| `catalog_sector`, `catalog_udaf`, `catalog_eod` | sector, grupo y unidad del catálogo (vacíos si no cruza; grupo y unidad vacíos si el RUC está en varios grupos) |
| `entity_name`, `name_source` | nombre y su origen: `catalogo` o `sercop_nombre_mas_frecuente` |
| `entity_type` | `presidencia`, `ministerio`, `instituto`, `fuera_de_alcance` o `sin_clasificar` |
| `proposed_type` | recomendación para los grupos dudosos del catálogo; no cuenta como clasificación |
| `parent_entity` | cabecera del grupo, solo cuando es única y la fila no es la cabecera; o el padre acreditado por una decisión |
| `source` | criterio, norma o decisión que respalda la fila, y la foto del catálogo |
| `valid_from`, `valid_to` | vacíos: el catálogo no da vigencia (Q-E04) |
| `status` | `aprobada`, `propuesta` o `dudosa` |
| `note` | aclaración de la fila (por ejemplo, padre no único o RUC fuera del catálogo) |

### 3.7. Reproducir

El script usa solo la biblioteca estándar y no sobrescribe sus salidas: para repetir la corrida, las tres rutas de salida deben ser nuevas. Las rutas de entrada son las de la carpeta principal del repositorio (`data/` está ignorada por Git). Sin `--overrides` la semilla sale con las clasificaciones propuestas y ninguna admitida; con el archivo de decisiones sale la semilla de este documento.

```powershell
python -I scripts/build_entity_seed.py `
  --catalog-xlsx "data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx" `
  --derived-dir data/derivados `
  --overrides warehouse/seeds/entity_classification_decisions.csv `
  --output-seed warehouse/seeds/entity_classification.csv `
  --output-coverage docs/h3/evidencia/cobertura-semilla-entidades-AAAAMMDD.json `
  --output-cases docs/h3/evidencia/casos-dudosos-semilla-entidades-AAAAMMDD.csv
```

La corrida dura unos diez segundos. Las pruebas (`tests/unit/test_build_entity_seed.py`) usan un catálogo y unos CSV inventados y cubren la unión exacta, por raíz, el nombre que nunca une, la ambigüedad, las decisiones (con padre y evidencia) y la coherencia por raíz.

## 4. Resultado

### 4.1. La semilla

| Indicador | Valor |
|---|---|
| Filas | 6.100 (`exacta` 2.731, `raiz` 2.698, `sin_cruce` 665, `malformado` 6) |
| Estados | `aprobada` 4.925, `propuesta` 210, `dudosa` 965 |
| Tipos (compradores) | `fuera_de_alcance` 3.993 (3.783 aprobadas, 210 propuestas), `ministerio` 1.140, `presidencia` 2, `sin_clasificar` 965 |
| RUC del catálogo antes de las decisiones | 3.080 distintos: 4 `presidencia`, 585 `ministerio`, 2.243 `fuera_de_alcance`, 248 dudosos (de ellos 32 institutos por denominación) |
| Procesos por tipo de unión | exacta 75,04 %, raíz 20,79 %, sin cruce 4,17 %, malformado 0,004 % |
| Monto por tipo de unión | exacta 18,33 %, raíz 79,08 %, sin cruce 2,59 % |

Fuente: `docs/h3/evidencia/cobertura-semilla-entidades-20261122.json` y la semilla, 22/11/2026. Las proporciones por tipo de unión se midieron sobre los totales de 2021 a 2025.

### 4.2. Cobertura por tipo y estado, 2021 a 2025

Procesos y monto de SERCOP por tipo de entidad y estado, con el año de `releases.date`. El monto es la suma de las adjudicaciones de cada proceso; de los 993.425 procesos, 42.991 (4,33 %) no tienen importe adjudicado y no suman nada, porque vacío no es cero.

| Tipo y estado | Procesos | % de procesos | Monto adjudicado (USD millones) | % del monto |
|---|---:|---:|---:|---:|
| Presidencia, aprobada | 313 | 0,03 % | 41,12 | 0,15 % |
| Ministerio, aprobada | 273.307 | 27,51 % | 5.426,34 | 19,25 % |
| Fuera de alcance, aprobada | 586.710 | 59,06 % | 18.857,24 | 66,90 % |
| Fuera de alcance, propuesta (no cuenta en el sector) | 53.742 | 5,41 % | 2.158,66 | 7,66 % |
| Sin clasificar: grupo dudoso del catálogo | 39.356 | 3,96 % | 981,77 | 3,48 % |
| Sin clasificar: sin cruce con el catálogo | 39.954 | 4,02 % | 722,00 | 2,56 % |
| Sin clasificar: identificador malformado | 43 | 0,00 % | 0,02 | 0,00 % |
| **Total 2021 a 2025** | **993.425** | **100,00 %** | **28.187,17** | **100,00 %** |

**Admitido en el sector:** Presidencia y ministerio con estado `aprobada`: 273.620 procesos (27,54 %) y USD 5.467,46 millones (19,40 %). Son las cifras que #70 y #71 usarán como control de la etapa 3. Las filas `fuera_de_alcance` con estado `propuesta` (53.742 procesos, 5,41 %; USD 2.158,66 millones, 7,66 %) corresponden a educación superior, financieras públicas, sociedades, superintendencias, Procuraduría y Parlamento Andino: no cambian el sector porque están fuera de todos modos, pero su exclusión sigue sin aprobarse.

### 4.3. Cobertura por año

Porcentaje de los procesos de cada año.

| Año de la fecha del proceso | Procesos | Presidencia | Ministerio | Admitido en el sector | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 148.823 | 0,02 % | 30,96 % | 30,98 % | 60,78 % | 8,23 % |
| 2022 | 206.801 | 0,06 % | 26,51 % | 26,57 % | 65,03 % | 8,40 % |
| 2023 | 222.595 | 0,04 % | 28,74 % | 28,78 % | 62,66 % | 8,56 % |
| 2024 | 217.422 | 0,01 % | 29,28 % | 29,29 % | 63,37 % | 7,33 % |
| 2025 | 197.784 | 0,02 % | 22,63 % | 22,65 % | 69,90 % | 7,45 % |
| 2021-2025 | 993.425 | 0,03 % | 27,51 % | 27,54 % | 64,47 % | 7,99 % |
| 2026 | 14.495 | 0,05 % | 12,87 % | 12,92 % | 82,77 % | 4,30 % |

Porcentaje del monto adjudicado de cada año.

| Año de la fecha del proceso | Monto adjudicado (USD millones) | Presidencia | Ministerio | Admitido en el sector | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 2.468,69 | 0,07 % | 18,55 % | 18,62 % | 76,30 % | 5,08 % |
| 2022 | 5.752,22 | 0,12 % | 16,93 % | 17,05 % | 76,11 % | 6,84 % |
| 2023 | 6.934,07 | 0,13 % | 21,53 % | 21,66 % | 72,17 % | 6,17 % |
| 2024 | 6.626,35 | 0,04 % | 19,58 % | 19,62 % | 73,45 % | 6,93 % |
| 2025 | 6.405,83 | 0,33 % | 18,80 % | 19,13 % | 76,22 % | 4,65 % |
| 2021-2025 | 28.187,17 | 0,15 % | 19,25 % | 19,40 % | 74,56 % | 6,04 % |
| 2026 | 2.765,71 | 0,21 % | 7,56 % | 7,77 % | 88,55 % | 3,68 % |

Detalle de lo que queda sin clasificar.

| Año de la fecha del proceso | Dudosos del catálogo (procesos) | Sin cruce (procesos) | Malformados (procesos) | Dudosos del catálogo (monto) | Sin cruce (monto) | Sin clasificar en total (USD millones) |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 3,99 % | 4,25 % | 0,00 % | 2,55 % | 2,52 % | 125,29 |
| 2022 | 4,08 % | 4,31 % | 0,00 % | 3,34 % | 3,50 % | 393,62 |
| 2023 | 4,08 % | 4,46 % | 0,01 % | 3,70 % | 2,46 % | 427,68 |
| 2024 | 3,62 % | 3,71 % | 0,00 % | 4,57 % | 2,36 % | 459,30 |
| 2025 | 4,05 % | 3,40 % | 0,00 % | 2,60 % | 2,05 % | 297,91 |
| 2021-2025 | 3,96 % | 4,02 % | 0,00 % | 3,48 % | 2,56 % | 1.703,80 |
| 2026 | 2,08 % | 2,23 % | 0,00 % | 2,43 % | 1,25 % | 101,83 |

Los 14.495 procesos con fecha de 2026 no entran en `DimTiempo` (ventana 2021-01 a 2025-12, decisión del diseño dimensional) y no están en los totales de 2021 a 2025; se muestran aparte para que la semilla cubra todos los `buyer_id` descargados. Con la fecha del archivo en lugar de `releases.date` las cifras por año serían otras (Q-10); la fecha de negocio ya está decidida.

La participación admitida en el sector es la más baja en 2025 (22,65 % de los procesos) frente a 26,57 % a 30,98 % en los otros años. La semilla no explica esa diferencia: no se investigó si viene de la fusión de ministerios de 2025 y 2026 o del crecimiento de otras entidades. Queda señalada, no resuelta.

## 5. Casos dudosos

### 5.1. Cómo se eligieron

Un caso es un grupo del catálogo (UDAF), una raíz sin cruce o un identificador malformado. Se ordenan por peso, que es la suma de su participación en los procesos y de su participación en el monto de 2021 a 2025. Hay 566 casos (74 grupos del catálogo, 486 raíces sin cruce, 6 malformados). La lista corta toma los 50 primeros. La columna «Origen» dice si el caso viene de un grupo del catálogo o de una raíz que no cruzó; en este segundo caso el nombre es la grafía más frecuente de SERCOP y sirve solo para sustentar la recomendación, nunca para unir.

**Criterio de las recomendaciones** (elección del equipo, lectura literal de la decisión de alcance 1: «Presidencia, ministerios e institutos que dependen de ellos»): entra solo lo que es Presidencia, ministerio o instituto con dependencia acreditada, o lo que el propio catálogo coloca dentro de su estructura; todo lo demás sale. Una recomendación `dudosa` significa que ninguna fuente revisada acredita la dependencia y clasificar sería inventar.

**Estado de los 50.** Por decisión del líder (sección 5.4, D1), los casos cuya evidencia es solo la denominación o el grupo presupuestario **siguen `dudosa`** aunque la recomendación sea «fuera» o «dentro». La recomendación indica hacia dónde se resolverían cuando haya respaldo.

### 5.2. Lista corta de 50 casos

Peso de la lista: 45.310 procesos (4,56 % de los procesos de 2021 a 2025) y USD 1.487,68 millones (5,28 % del monto). Son el 57,1 % de los procesos y el 87,3 % del monto que queda sin clasificar.

| N° | Caso | Clave | Origen | Procesos | Monto (USD millones) | Recomendación | Bloque |
|---:|---|---|---|---:|---:|---|---|
| 1 | Servicio Nacional de Atención Integral a Personas Privadas de la Libertad y a Adolescentes Infractores | UDAF 578 | catálogo | 461 | 172,37 | fuera | B1 |
| 2 | Servicio de Rentas Internas (SRI) | UDAF 135 | catálogo | 3.800 | 62,03 | fuera | B1 |
| 3 | Dirección General de Registro Civil, Identificación y Cedulación | UDAF 51 | catálogo | 1.063 | 137,01 | fuera | B1 |
| 4 | Cuerpo de Ingenieros del Ejército | RUC 1768007040001 | sin cruce | 2.608 | 89,52 | dudosa | B3 |
| 5 | Hospital de Especialidades de las Fuerzas Armadas No. 1 | UDAF 74 | catálogo | 2.186 | 81,84 | fuera | B3 |
| 6 | Agencia de Regulación y Control Fito y Zoosanitario | UDAF 334 | catálogo | 3.207 | 18,93 | fuera | B1 |
| 7 | Servicio Integrado de Seguridad ECU 911 | UDAF 266 | catálogo | 2.366 | 41,80 | fuera | B1 |
| 8 | Fundación Municipal Guayaquil Siglo XXI | RUC 0992183721001 | sin cruce | 692 | 88,15 | fuera | B6 |
| 9 | Autoridad Aeroportuaria de Guayaquil (fundación municipal) | RUC 0992179619001 | sin cruce | 388 | 89,95 | fuera | B6 |
| 10 | Instituto Nacional de Investigaciones Agropecuarias (INIAP) | UDAF 390 | catálogo | 2.856 | 16,55 | dudosa hasta respaldo | B8 |
| 11 | Casa de la Cultura Ecuatoriana Benjamín Carrión | UDAF 250 | catálogo | 3.080 | 4,95 | fuera | B1 |
| 12 | Instituto Nacional de Estadística y Censos (INEC) | UDAF 64 | catálogo | 2.038 | 14,64 | dudosa hasta respaldo | B8 |
| 13 | Instituto Geográfico Militar | UDAF 72 | catálogo | 773 | 48,19 | dudosa hasta respaldo | B8 |
| 14 | Secretaría Técnica de Gestión Inmobiliaria del Sector Público | RUC 1768146750001 | sin cruce | 622 | 48,87 | fuera | B1 |
| 15 | Fundación Terminal Terrestre de Guayaquil | RUC 0992236574001 | sin cruce | 712 | 44,03 | fuera | B6 |
| 16 | Secretaría Nacional de Gestión de Riesgos | UDAF 34 | catálogo | 1.189 | 25,69 | fuera | B1 |
| 17 | Agencia Nacional de Regulación y Control del Transporte Terrestre | UDAF 69 | catálogo | 244 | 52,41 | fuera | B1 |
| 18 | Corporación para la Seguridad Ciudadana de Guayaquil | RUC 0992457597001 | sin cruce | 334 | 40,87 | fuera | B6 |
| 19 | Instituto Oceanográfico y Antártico de la Armada | UDAF 611 | catálogo | 886 | 24,90 | dudosa hasta respaldo | B8 |
| 20 | Comisión de Tránsito del Ecuador | UDAF 68 | catálogo | 370 | 39,06 | fuera | B1 |
| 21 | Dirección General de Aviación Civil | UDAF 522 | catálogo | 426 | 29,40 | fuera | B1 |
| 22 | Secretaría de Educación Superior, Ciencia, Tecnología e Innovación | RUC 1768157600001 | sin cruce | 294 | 30,40 | fuera | B1 |
| 23 | Aceros Nacionales del Ecuador S.A. (ANDEC) | RUC 0990001340001 | sin cruce | 631 | 20,10 | fuera | B6 |
| 24 | Agencia de Regulación, Control y Vigilancia Sanitaria (ARCSA) | UDAF 217 | catálogo | 1.168 | 2,97 | fuera | B1 |
| 25 | Dirección Nacional de Registros Públicos | UDAF 511 | catálogo | 981 | 8,18 | fuera | B1 |
| 26 | Consejo de Gobierno del Régimen Especial de Galápagos | UDAF 45 | catálogo | 416 | 23,80 | fuera | B1 |
| 27 | Dirección Zonal 8 de la Secretaría Técnica de Gestión Inmobiliaria | RUC 0968604550001 | sin cruce | 371 | 23,14 | fuera | B1 |
| 28 | Servicio Nacional de Aduana del Ecuador (SENAE) | UDAF 136 | catálogo | 420 | 20,33 | fuera | B1 |
| 29 | Fundación Municipal de la Mujer y el Niño de Cuenca | RUC 0190408485001 | sin cruce | 989 | 3,03 | fuera | B6 |
| 30 | Servicio Nacional de Medicina Legal y Ciencias Forenses | UDAF 229 | catálogo | 351 | 20,27 | fuera | B1 |
| 31 | Fundación Museos de la Ciudad | RUC 1792042704001 | sin cruce | 770 | 7,51 | fuera | B6 |
| 32 | Instituto Nacional de Investigación en Salud Pública (INSPI) | UDAF 267 | catálogo | 617 | 10,18 | dudosa hasta respaldo | B8 |
| 33 | Corporación de Promoción Económica CONQUITO | RUC 1791905911001 | sin cruce | 801 | 2,20 | fuera | B6 |
| 34 | Ministerio de Turismo | RUC 1760009020001 | sin cruce | 283 | 15,86 | dentro: ministerio, con respaldo | B4 |
| 35 | Comando de Inteligencia Militar Conjunto de las Fuerzas Armadas | RUC 1768184250001 | sin cruce | 653 | 4,92 | dudosa | B3 |
| 36 | Secretaría Técnica Ecuador Crece Sin Desnutrición Infantil | RUC 1768143140001 | sin cruce | 264 | 15,89 | fuera | B1 |
| 37 | Corporación Registro Civil de Guayaquil | RUC 0992441127001 | sin cruce | 309 | 14,40 | fuera | B6 |
| 38 | FAME S.A. | RUC 1790932966001 | sin cruce | 577 | 5,97 | fuera | B6 |
| 39 | Ministerio del Ambiente, Agua y Transición Ecológica | RUC 1768192860001 | sin cruce | 615 | 4,71 | dentro: ministerio, con respaldo | B4 |
| 40 | Parque Nacional Galápagos | UDAF 330 | catálogo | 282 | 14,15 | fuera | B1 |
| 41 | Instituto de Fomento de las Artes, Innovación y Creatividades | UDAF 303 | catálogo | 720 | 0,86 | dudosa hasta respaldo | B8 |
| 42 | Fundación Teatro Nacional Sucre | RUC 1791984714001 | sin cruce | 584 | 4,22 | fuera | B6 |
| 43 | Agencia de Regulación y Control de las Telecomunicaciones (ARCOTEL) | UDAF 90 | catálogo | 417 | 8,90 | fuera | B1 |
| 44 | Operador Nacional de Electricidad (CENACE) | UDAF 95 | catálogo | 345 | 9,27 | fuera | B1 |
| 45 | Servicio Público para Pago de Accidentes de Tránsito | UDAF 222 | catálogo | 218 | 12,83 | fuera | B1 |
| 46 | Ministerio del Deporte | RUC 1760006350001 | sin cruce | 353 | 7,91 | dentro: ministerio, con respaldo | B4 |
| 47 | Ministerio de Cultura y Patrimonio | RUC 1768135120001 | sin cruce | 223 | 11,26 | dentro: ministerio, con respaldo | B4 |
| 48 | Federación Deportiva del Guayas | RUC 0990057907001 | sin cruce | 374 | 6,73 | fuera | B6 |
| 49 | Fideicomiso Fondo Ambiental para la Protección del Agua | RUC 1791722205001 | sin cruce | 517 | 2,63 | fuera | B6 |
| 50 | Casa Militar Presidencial | UDAF 85 | catálogo | 466 | 3,90 | dentro: presidencia, con respaldo | B7 |

### 5.3. Los bloques y su motivo

| Bloque | Qué reúne | Motivo de la recomendación |
|---|---|---|
| B1 | Organismos del Ejecutivo con figura propia: servicios, agencias, secretarías, consejos, direcciones generales, autoridades, casas, operadores, comisiones y parques | No son Presidencia, ministerio ni instituto por su denominación. El catálogo les da un grupo presupuestario propio y no los coloca bajo ningún ministerio. La sección 5.3 de `docs/sources/entidades.md` dejó abierta esta categoría. |
| B3 | Fuerzas Armadas fuera del grupo del Ministerio de Defensa | El hospital tiene grupo propio: `fuera`, igual que B1. Las dos unidades militares sin cruce quedan `dudosa`: ninguna fuente revisada acredita su dependencia. El grupo del Ministerio de Defensa del catálogo (UDAF 70, 119 filas) sí está dentro como ministerio. |
| B4 | Ministerios históricos cuyo RUC no consta en el catálogo | La denominación de SERCOP es de ministerio y el catálogo del 31/08/2026 no los trae (nota 5 del archivo: excluye RUC pasivos; fusiones de 2025 y 2026, caso ya señalado en `docs/sources/entidades.md`, sección 5.3). Entrarían con respaldo individual (sección 5.6). Su vigencia (`valid_to`) se desconoce. |
| B6 | Fundaciones, corporaciones y empresas locales, federaciones deportivas, sociedades anónimas y un fideicomiso | No son Presidencia, ministerio ni instituto. La mayoría son entes de municipios (GAD, fuera por la decisión de alcance 2) o personas jurídicas privadas. |
| B7 | Casa Militar Presidencial | Órgano de la Presidencia por su denominación; el catálogo le da un grupo propio. La Vicepresidencia recibe la misma recomendación. Entraría con respaldo. |
| B8 | Institutos por denominación | La denominación no prueba la adscripción a un ministerio (ADR 0001, decisión 1). Se resuelven con el decreto o estatuto de adscripción (sección 5.5). |

Peso de cada bloque y recomendación:

| Bloque y recomendación | Casos | Procesos | % de procesos | Monto (USD millones) | % del monto |
|---|---:|---:|---:|---:|---:|
| B1: fuera | 23 | 22.355 | 2,25 % | 822,67 | 2,92 % |
| B3: dudosa | 2 | 3.261 | 0,33 % | 94,44 | 0,34 % |
| B3: fuera | 1 | 2.186 | 0,22 % | 81,84 | 0,29 % |
| B4: dentro: ministerio, con respaldo | 4 | 1.474 | 0,15 % | 39,74 | 0,14 % |
| B6: fuera | 13 | 7.678 | 0,77 % | 329,78 | 1,17 % |
| B7: dentro: presidencia, con respaldo | 1 | 466 | 0,05 % | 3,90 | 0,01 % |
| B8: dudosa hasta respaldo | 6 | 7.890 | 0,79 % | 115,31 | 0,41 % |
| **Los 50 casos** | **50** | **45.310** | **4,56 %** | **1.487,68** | **5,28 %** |

Los otros 516 casos pesan 34.043 procesos (3,43 %) y USD 216,12 millones (0,77 %). Quedan sin clasificar y su peso queda a la vista (limitación declarada, sección 6).

### 5.4. Decisiones del líder del 22/11/2026 y cómo quedaron en la semilla

Las decisiones salieron de la revisión del PR de la primera versión y están en `warehouse/seeds/entity_classification_decisions.csv`. Las citas normativas (COESCOP, LOEI, catálogo de 2018) son las de esa revisión: este documento las registra como evidencia de la decisión y **no se verificaron de forma independiente**.

| N° | Decisión | Cómo quedó |
|---|---|---|
| D1 | Aprobar los dos distritos de salud sin RUC en el catálogo con fuente oficial; mantener `dudosa` todo caso cuya evidencia sea solo la denominación o el grupo presupuestario. | Los RUC 1060040130001 (10D02 Antonio Ante-Otavalo) y 1060014130001 (10D03 Cotacachi) pasan a `ministerio`, `aprobada`, con `parent_entity` igual a la cabecera del Ministerio de Salud Pública y como evidencia el catálogo oficial de instituciones al 31/03/2018. Los demás casos de la lista siguen `dudosa`. |
| D2 | Policía Nacional fuera del alcance vigente. Fundamento: el Código Orgánico de las Entidades de Seguridad Ciudadana y Orden Público (arts. 61 y 63) acredita la dependencia operativa y la rectoría del ministerio, pero el alcance del estudio son Presidencia, ministerios e institutos dependientes. | Los grupos 52, 57 y 58 pasan a `fuera_de_alcance`, `aprobada`. Sustituye el fundamento de la primera versión, que decía que la dependencia no estaba acreditada. |
| D3 | Aprobar por regla y con evidencia: Presidencia, ministerios y exclusiones justificadas. Institutos solo con respaldo de adscripción; excluir al INEVAL. | Presidencia y ministerios pasan a `aprobada`. La seguridad social (sector 113) pasa a `fuera_de_alcance`, `aprobada`. El INEVAL (grupo 214) pasa a `fuera_de_alcance`, `aprobada` (LOEI, art. 67, sin adscripción). Los demás institutos pasan de `propuesta` a `dudosa`. |
| D4 | Dejar pendiente: faltan las raíces y el respaldo individual. | Pendiente. Las raíces están en la sección 5.6. |

Las exclusiones que siguen en `propuesta` (educación superior, financieras públicas, sociedades con participación pública, superintendencias, Procuraduría y Parlamento Andino) no se aprobaron en bloque porque no tienen aún una norma citada; no afectan el sector.

### 5.5. Institutos

Hasta documentar la adscripción de cada uno, los 14 institutos que quedan por denominación son `sin_clasificar` con `proposed_type = instituto`. Pesan 9.495 procesos (0,96 %) y USD 128,24 millones (0,45 %). Para cada uno se necesita el decreto o estatuto que lo adscribe a un ministerio, con su fecha (docs/sources/entidades.md, sección 4, los deja «No verificada»).

| Instituto (cabecera del grupo) | UDAF | Procesos | Monto (USD millones) | Respaldo de adscripción |
|---|---|---:|---:|---|
| INSTITUTO NACIONAL DE INVESTIGACIONES AGROPECUARIAS - I.N.I.A.P. - PLANTA CENTRAL | 390 | 2.856 | 16,55 | pendiente |
| INSTITUTO NACIONAL DE ESTADISTICAS Y CENSOS - PLANTA CENTRAL | 64 | 2.038 | 14,64 | pendiente |
| INSTITUTO OCEANOGRAFICO Y ANTARTICO DE LA ARMADA | 611 | 886 | 24,90 | pendiente |
| INSTITUTO GEOGRAFICO MILITAR | 72 | 773 | 48,19 | pendiente |
| INSTITUTO DE FOMENTO DE LAS ARTES INNOVACION Y CREATIVIDADES - PLANTA CENTRAL | 303 | 720 | 0,86 | pendiente |
| INSTITUTO NACIONAL DE INVESTIGACION EN SALUD PUBLICA INSPI DR LEOPOLDO IZQUIETA PEREZ- PLANTA CENTRAL | 267 | 617 | 10,18 | pendiente |
| INSTITUTO DE INVESTIGACION GEOLOGICO Y ENERGETICO | 427 | 456 | 3,48 | pendiente |
| INSTITUTO NACIONAL DE PATRIMONIO CULTURAL | 141 | 439 | 4,13 | pendiente |
| INSTITUTO NACIONAL DE ECONOMIA POPULAR Y SOLIDARIA - IEPS PLANTA CENTRAL | 274 | 185 | 1,96 | pendiente |
| INSTITUTO NACIONAL DE METEOROLOGIA E HIDROLOGIA -INAMHI | 422 | 184 | 2,07 | pendiente |
| INSTITUTO NACIONAL DE BIODIVERSIDAD | 302 | 154 | 0,59 | pendiente |
| INSTITUTO NACIONAL DE DONACION Y TRANSPLANTES DE ORGANOS TEJIDOS Y CELULAS - INDOT - PLANTA CENTRAL | 326 | 122 | 0,46 | pendiente |
| INSTITUTO DE CINE Y CREACION AUDIOVISUAL | 236 | 38 | 0,00 | pendiente |
| INSTITUTO PUBLICO DE INVESTIGACION DE ACUICULTURA Y PESCA | 473 | 27 | 0,23 | pendiente |

Si todos se aprobaran, el sector admitido subiría en esa misma proporción.

### 5.6. Ministerios históricos sin cruce (D4 pendiente)

Raíces sin cruce cuya denominación en SERCOP dice «Ministerio». Ninguna tiene respaldo individual todavía. Q-E05 pide contrastarlas con fuentes oficiales; la revisión del PR señala decretos de fusión del Ministerio del Ambiente y del de Turismo (Registro Oficial, segundo suplemento 105) que servirían de respaldo, citados allí y sin verificar aquí. Se aprueban por RUC cuando cada una tenga su documento.

| RUC | Denominación en SERCOP | Procesos | Monto (USD millones) | Respaldo individual |
|---|---|---:|---:|---|
| 1768192860001 | MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 615 | 4,71 | pendiente |
| 1768137410001 | MINISTERIO DE LA MUJER Y DERECHOS HUMANOS | 376 | 6,29 | pendiente |
| 1760006350001 | MINISTERIO DEL DEPORTE | 353 | 7,91 | pendiente |
| 1760009020001 | MINISTERIO DE TURISMO | 283 | 15,86 | pendiente |
| 1760009450001 | MINISTERIO DE DESARROLLO URBANO Y VIVIENDA | 239 | 3,01 | pendiente |
| 1768135120001 | MINISTERIO DE CULTURA Y PATRIMONIO | 223 | 11,26 | pendiente |
| 1865043800001 | DIRECCION ZONAL 3 CHIMBORAZO - MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 196 | 0,58 | pendiente |
| 1360088540001 | DIRECCION ZONAL 4 MANABI DEL MINISTERIO DEL AMBIENTE AGUA Y TRANSICION ECOLOGICA | 195 | 0,70 | pendiente |
| 0760053620001 | DIRECCION ZONAL 7 LOJA DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 188 | 0,41 | pendiente |
| 0860050770001 | DIRECCION ZONAL 2 ESMERALDAS DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 164 | 0,18 | pendiente |
| 1960149180001 | DIRECCION ZONAL 10 ZAMORA CHINCHIPE DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 164 | 0,05 | pendiente |
| 1060042770001 | DIRECCION ZONAL 1 IMBABURA DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 117 | 0,17 | pendiente |
| 0160063860001 | DIRECCION ZONAL 6 AZUAY DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 86 | 0,63 | pendiente |
| 2160071900001 | DIRECCIÓN ZONAL 9 DEL MINISTERIO DE AMBIENTE Y AGUA | 74 | 0,08 | pendiente |
| 1560515940001 | DIRECCION ZONAL 8 NAPO MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 70 | 0,62 | pendiente |
| 0968608890001 | DIRECCION ZONAL 5 GUAYAS DEL MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 17 | 0,34 | pendiente |
| 1865037910001 | COORDINACION ZONAL 3 DEL MINISTERIO DE RELACIONES EXTERIORES Y MOVILIDAD HUMANA | 6 | 0,00 | pendiente |

Pesan 3.366 procesos (0,34 %) y USD 52,80 millones (0,19 %). Efecto simulado de aprobar todas (suma de los casos, no una nueva corrida): el sector admitido pasaría a 27,88 % de los procesos y 19,58 % del monto; con los institutos también, a 28,84 % y 20,04 %.

## 6. Límites declarados

- **El catálogo es una foto al 31/08/2026** (Q-E04). No da vigencia: los procesos de 2021 a 2025 se clasifican con la entidad que el catálogo lista hoy. `valid_from` y `valid_to` están vacíos y la vigencia por fecha (SCD tipo 2) queda para el Hito 4.
- **Los institutos no entran en el sector** hasta tener respaldo de adscripción (sección 5.5). La cobertura admitida es, por eso, un piso.
- **Quedan sin clasificar** 7,99 % de los procesos y 6,04 % del monto de 2021 a 2025. De esa parte, los 50 casos de la lista son el 57,1 % de los procesos y el 87,3 % del monto; los otros 516 casos pesan 3,43 % de los procesos y 0,77 % del monto del total.
- **Las raíces sin cruce no tienen tipo en el catálogo.** La denominación de SERCOP sustenta una recomendación, pero la clasificación exige respaldo por RUC.
- **El nombre de las entidades sin cruce** es la grafía más frecuente de SERCOP, no un nombre oficial (Q-13).
- **La semilla incluye 14.495 procesos de 2026** que `DimTiempo` deja fuera; los totales de este documento son de 2021 a 2025.
- **No se probó en Power BI Desktop.** La unión en Power Query y los totales de control con la semilla aplicada se verifican al construir el modelo (#70 y #71), con los controles antes y después que pide la guía.

## 7. Segunda pasada: cómo se registra una decisión

La decisión se escribe en `warehouse/seeds/entity_classification_decisions.csv` y se reaplica con el mismo script, con la opción `--overrides` y salidas nuevas. Cada fila lleva `scope` (`ruc_root`, `udaf`, `sector` o `propuesta`, este último para aprobar todas las filas `propuesta` de un tipo sin cambiarlo), `key`, `entity_type`, `decided_on`, `decision_note` y, opcionales, `parent_entity` (el padre acreditado) y `evidence` (la fuente). Las filas alcanzadas pasan a `aprobada` y su `source` cita la decisión y la evidencia. Un identificador malformado nunca se toca; un RUC que consta en varios grupos solo se decide por `ruc_root`; dos decisiones que den a una fila tipos distintos hacen fallar el script.

## 8. Estado de los criterios del issue #68

| Criterio | Estado |
|---|---|
| La semilla existe, sin duplicados de clave, con `source` y `status` en cada fila | Cumplido: 6.100 filas, clave `buyer_id` única (revisión de la salida y comparación byte a byte de la regeneración por la revisión del PR) |
| La unión nunca usa `buyer.name`; probada | Cumplido: pruebas de unión exacta, por raíz, nombre que no une y ambigüedad |
| Lista de casos dudosos con recomendación; decisión del líder registrada y reflejada en la semilla | **Parcial:** decisiones D1 a D3 reflejadas; faltan D4 (sección 5.6) y el respaldo de los institutos (sección 5.5) |
| Cobertura medida y escrita | Cumplido (sección 4), con la regla de admisión de la sección 3.5 |
| Lo no clasificado queda fuera de los indicadores con su peso a la vista | Cumplido (secciones 4 y 6) |
| La regla en un párrafo con su origen | Cumplido (sección 2) |
| `ruff` y `pytest` en verde | Ver el PR |
