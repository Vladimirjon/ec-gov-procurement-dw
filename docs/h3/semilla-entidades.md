# Semilla de clasificación de entidades para DimEntidad

- **Estado:** semilla generada y medida el 22/11/2026, con las decisiones D1 a D6 de ese día aplicadas (sección 5.4). Lo que no se pudo respaldar queda `sin_clasificar` y fuera de los indicadores (ADR 0001, regla 6), con su peso a la vista y la acción para el Hito 4 (sección 6).
- **Fecha:** 22/11/2026. **Equipo:** Grupo 5. **Sector:** gobierno central de Ecuador.
- **Fuente de:** `DimEntidad` y el filtro del sector en Power Query (#70, #71), el diseño de P1, P2 y P3 y la sección de diseño del PDF (#73 y #74).
- **Alcance de esta nota:** la regla de unión, de tipo y de admisión, la semilla, su cobertura y los casos que quedan por respaldar. La semilla **no se ha probado en Power BI Desktop**: la cobertura se calculó con Python sobre los CSV del portal.

## 1. Resumen

Los 6.100 `buyer_id` distintos de SERCOP (procesos fechados de 2021 a 2026) se cruzaron con el catálogo de instituciones del MDEP por `buyer_id` completo o por la raíz `EC-RUC-{13}`, nunca por nombre. De los 6.100, 5.429 cruzan, 665 no cruzan y 6 están malformados.

**Qué cuenta como «en el sector».** `FactContratacion` admite solo los procesos cuyo comprador es Presidencia, ministerio o instituto **con estado `aprobada`** (diseño dimensional, sección 6.5). Una clasificación `propuesta` o `dudosa` queda fuera. La primera versión de esta nota contaba las propuestas como sector (28,38 % de los procesos y 19,83 % del monto), lo que no correspondía a esa regla.

Con la fecha del proceso (`releases.date`) entre 2021 y 2025, de los 993.425 procesos y USD 28.187,17 millones: **27,69 % de los procesos y 19,55 % del monto quedan admitidos en el sector** (275.100 procesos y USD 5.511,80 millones), 67,41 % de los procesos y 77,57 % del monto quedan fuera del gobierno central y **4,90 % de los procesos y 2,88 % del monto quedan sin clasificar**.

Lo que queda sin clasificar: 502 casos (16 grupos del catálogo, 480 raíces sin cruce y 6 identificadores malformados) que pesan 48.639 procesos y USD 810,82 millones. Entre ellos están los institutos sin respaldo de adscripción (9.495 procesos y USD 128,24 millones) y las raíces cuya denominación dice «Ministerio» y no constan en el catálogo oficial de 2018 (1.886 procesos y USD 8,46 millones). La sección 5 trae los 50 casos más pesados con su recomendación.

## 2. La regla (párrafo para el PDF y las diapositivas)

**Párrafo para el PDF.** La clasificación de las entidades compradoras sigue una regla de alcance definida por el equipo, no una regla del curso. Cada comprador de SERCOP se identifica por su código `buyer.id`: se une primero por el valor completo y, si no coincide, por la raíz `EC-RUC` de 13 dígitos, nunca por el nombre. La unión se hace contra el catálogo oficial de instituciones del sector público del Ministerio de Economía y Finanzas, con corte al 31 de agosto de 2026. Del catálogo se toman el sector y la denominación de la cabecera de cada grupo presupuestario para determinar el tipo: Presidencia de la República, ministerio (con las unidades que dependen de él en el catálogo) o fuera de alcance (gobiernos autónomos descentralizados, empresas públicas, seguridad social, Policía Nacional, otras funciones del Estado y organismos con figura propia como servicios, agencias y secretarías). Solo entran en los indicadores los compradores de Presidencia o de un ministerio con clasificación aprobada. Los institutos, mientras no se acredite su adscripción a un ministerio, y los compradores que no cruzan con el catálogo o tienen un identificador malformado quedan sin clasificar y fuera de los indicadores, y su peso se informa. Entre 2021 y 2025, tomando como fecha la del proceso, el 27,69 % de los procesos y el 19,55 % del monto adjudicado quedan en el sector, y el 4,90 % de los procesos y el 2,88 % del monto quedan sin clasificar.

**Versión para diapositiva.**

- Se une por `buyer.id` completo o por la raíz de 13 dígitos; nunca por nombre.
- El tipo sale del catálogo oficial (corte 31/08/2026) y solo cuenta lo aprobado: Presidencia y ministerios.
- Lo dudoso queda fuera de los indicadores: 4,90 % de los procesos y 2,88 % del monto de 2021 a 2025.

**Origen de la regla:** decisión de alcance del equipo registrada en el ADR 0001 (decisiones 1, 2, 6 y 7). No es una regla del curso. El criterio de tipo por denominación de la cabecera del catálogo y la lectura de la categoría de instituto (decisión D5) son elecciones del equipo.

## 3. Cómo se construye

### 3.1. Entradas

| Entrada | Detalle | Origen |
|---|---|---|
| Catálogo de instituciones del MDEP | Hoja `CATÁLOGO`, corte al 31/08/2026; 3.140 filas con RUC; 8 filas de notas al pie omitidas | `docs/h2/fuente-entidades.md` |
| Procesos y adjudicaciones de SERCOP | `releases_AAAA.csv` y `awards_AAAA.csv`, años de archivo 2021 a 2025; fecha de negocio `releases.date`; monto del proceso = suma de sus adjudicaciones, vacío no es cero | decisión del líder del 21/11/2026 |
| Reglas de unión | ADR 0001, decisiones 6 y 7 | ADR 0001 |
| Decisiones del 22/11/2026 | `warehouse/seeds/entity_classification_decisions.csv`, aplicadas con `--overrides` | sección 5.4 |

### 3.2. Unión (sin usar nunca `buyer.name`)

1. **Exacta:** `buyer_id` es igual a `EC-RUC-{13}` de un RUC del catálogo (`match_type = exacta`).
2. **Por raíz:** `buyer_id` lleva sufijo de unidad (`EC-RUC-{13}-sufijo`) y su raíz de 13 dígitos consta en el catálogo (`match_type = raiz`). La raíz solo se acepta si cumple el patrón de 13 dígitos numéricos.
3. **Sin cruce o malformado:** la raíz no consta en el catálogo (`sin_cruce`) o el identificador no tiene la forma `EC-RUC-{13}` (`malformado`). Quedan `sin_clasificar`, estado `dudosa`, salvo que una decisión por RUC los resuelva con respaldo.

Si un RUC consta en varias filas del catálogo con resultados distintos, queda `sin_clasificar` (ambigüedad). No ocurre en los datos: los 60 RUC repetidos (36 entre los grupos 280 y 315, 24 entre los grupos 130 y 360) son todos ministerios; conservan el tipo, se deja vacío el padre (`parent_entity`) y el grupo (`catalog_udaf`) para que una decisión por grupo no los alcance. El script falla si, tras aplicar decisiones, los `buyer_id` de una misma raíz quedan con clasificaciones distintas, que es la regla 3 de la secuencia de asignación del diseño.

### 3.3. Tipo de entidad propuesto

El catálogo no trae el tipo. Se deduce del sector y de la denominación de la **cabecera** de cada grupo (`ENTIDAD`, con `EOD` 0 o 9999), nunca del nombre de SERCOP. Cada fila del catálogo hereda el tipo de su grupo y, si no es la cabecera, el nombre de la cabecera como `parent_entity`. La tabla muestra el resultado de la regla **antes** de aplicar las decisiones.

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
| Cualquier otro grupo del sector 111 (Servicio, Agencia, Secretaría, Consejo, Policía, registros y similares) | `sin_clasificar` con `proposed_type` | `dudosa` | criterio del equipo |

Esto responde a Q-E07: **no se filtra por `SECTOR == 111`**, que mezcla las cinco funciones del Estado; el sector solo es un dato de entrada de la regla anterior.

### 3.4. Hallazgos de H2 que la semilla aplica

| Hallazgo | Cómo se aplica |
|---|---|
| Q-E01: RUC del catálogo con 12 dígitos | 1.266 RUC se rellenan a 13 con cero a la izquierda; un RUC no numérico o de más de 13 dígitos se descarta |
| Q-E02: RUC repetidos y grano (ENTIDAD, EOD) | 3.140 filas dan 3.080 RUC distintos; se clasifica por RUC y se detectan los resultados contradictorios (ninguno) |
| Q-E03: títulos y notas al pie | se localiza la fila de encabezado (`SECTOR` y `RUC`) y se descartan las filas sin RUC |
| Q-E04: el catálogo es una foto al 31/08/2026 | `valid_from` y `valid_to` quedan vacíos: la fuente no los da, y no se inventan |
| Q-E05: procesos que no cruzan | 665 `buyer_id` sin cruce en la unión (4,17 % de los procesos y 2,59 % del monto de 2021 a 2025); 15 de ellos, de ocho raíces resueltas con el catálogo de 2018 (D1 y D4), pasan a `ministerio`; el resto sigue sin clasificar |
| Q-E06: monto con `buyer_id` con sufijo | la unión por raíz aporta el 20,79 % de los procesos y el 79,08 % del monto; sin esa regla quedaría sin cruzar el 79,08 % del monto |
| Q-E07: el sector 111 mezcla las funciones del Estado | el tipo sale de la cabecera del grupo, no del sector (sección 3.3) |
| Q-E08: seis `buyer_id` malformados | `match_type = malformado`, sin raíz, 43 procesos, siempre fuera de los indicadores |
| Q-13: 425 variantes de escritura del nombre | `entity_name` sale del catálogo; si no cruza, de la grafía más frecuente de SERCOP para la raíz (`name_source`), una sola fila por `buyer_id` |

Las cifras de Q-E05 y Q-E06 de H2 se midieron sobre los 1.007.920 procesos sin acotar la fecha; aquí se acotan a 2021 a 2025 por `releases.date`, por eso difieren en décimas.

### 3.5. Regla de admisión en el sector

El control asigna un motivo por proceso y evalúa primero la ventana 2021 a 2025. Dentro de la ventana, «En el hecho» exige una raíz válida y una clasificación `aprobada` de tipo `presidencia`, `ministerio` o `instituto`. «Fuera del gobierno central» exige `fuera_de_alcance` con estado `aprobada`. «Dudoso o sin clasificar» reúne todo lo demás: propuestas, dudosos, raíces sin cruce e identificadores malformados. Es la misma regla que aplica Power Query en la secuencia de asignación de `IdEntidad` (diseño dimensional, sección 6.5). La evidencia reproducible está en `coverage.control_alcance` del [JSON de cobertura](evidencia/cobertura-semilla-entidades-20261122.json).

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
| `status` | `aprobada` o `dudosa` en la semilla entregada (`propuesta` solo aparece sin `--overrides`) |
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

La corrida dura unos diez segundos. Las pruebas (`tests/unit/test_build_entity_seed.py`) usan un catálogo y unos CSV inventados y cubren la unión exacta, por raíz, el nombre que nunca une, la ambigüedad, las decisiones (con padre, evidencia y los cuatro alcances), la coherencia por raíz y la conciliación por motivo.

## 4. Resultado

### 4.1. La semilla

| Indicador | Valor |
|---|---|
| Filas | 6.100 (`exacta` 2.731, `raiz` 2.698, `sin_cruce` 665, `malformado` 6) |
| Estados | `aprobada` 5.380, `dudosa` 720 |
| Tipos (compradores) | `fuera_de_alcance` 4.227, `ministerio` 1.151, `presidencia` 2, `sin_clasificar` 720 |
| RUC del catálogo antes de las decisiones | 3.080 distintos: 4 `presidencia`, 585 `ministerio`, 2.243 `fuera_de_alcance`, 248 dudosos (de ellos 32 institutos por denominación) |
| Procesos por tipo de unión | exacta 75,04 %, raíz 20,79 %, sin cruce 4,17 %, malformado 0,004 % |
| Monto por tipo de unión | exacta 18,33 %, raíz 79,08 %, sin cruce 2,59 % |

Fuente: `docs/h3/evidencia/cobertura-semilla-entidades-20261122.json` y la semilla, 22/11/2026. Las proporciones por tipo de unión se midieron sobre los totales de 2021 a 2025.

### 4.2. Cobertura por tipo y estado, 2021 a 2025

Procesos y monto de SERCOP por tipo de entidad y estado, con el año de `releases.date`. El monto es la suma de las adjudicaciones de cada proceso; de los 993.425 procesos, 42.991 (4,33 %) no tienen importe adjudicado y no suman nada, porque vacío no es cero.

| Tipo y estado | Procesos | % de procesos | Monto adjudicado (USD millones) | % del monto |
|---|---:|---:|---:|---:|
| Presidencia, aprobada | 313 | 0,03 % | 41,12 | 0,15 % |
| Ministerio, aprobada | 274.787 | 27,66 % | 5.470,68 | 19,41 % |
| Fuera de alcance, aprobada | 669.686 | 67,41 % | 21.864,55 | 77,57 % |
| Sin clasificar: grupo dudoso del catálogo | 10.122 | 1,02 % | 133,13 | 0,47 % |
| Sin clasificar: sin cruce con el catálogo | 38.474 | 3,87 % | 677,66 | 2,40 % |
| Sin clasificar: identificador malformado | 43 | 0,00 % | 0,02 | 0,00 % |
| **Total 2021 a 2025** | **993.425** | **100,00 %** | **28.187,17** | **100,00 %** |

### 4.3. Control esperado para #70 y #71

Totales que debe reproducir el modelo en la etapa 3, antes y después de combinar con las dimensiones. «En el hecho» es lo admitido en el sector: 275.100 procesos y USD 5.511,80 millones. La última fila reconcilia con el total nacional descargado en H2 (1.007.920 procesos y USD 30.952.880.306,92).

| Motivo de `ControlAlcance` | Procesos | % de procesos 2021-2025 | Monto adjudicado (USD) | % del monto 2021-2025 |
|---|---:|---:|---:|---:|
| En el hecho | 275.100 | 27,69 % | 5.511.799.162,58 | 19,55 % |
| Fuera del gobierno central | 669.686 | 67,41 % | 21.864.546.771,50 | 77,57 % |
| Dudoso o sin clasificar | 48.639 | 4,90 % | 810.819.796,83 | 2,88 % |
| **Total en la ventana 2021-2025** | **993.425** | **100,00 %** | **28.187.165.730,91** | **100,00 %** |
| Fuera de la ventana 2021-2025 (fecha de 2026) | 14.495 | | 2.765.714.576,01 | |
| **Total nacional descargado** | **1.007.920** | | **30.952.880.306,92** | |

### 4.4. Cobertura por año

Porcentaje de los procesos de cada año.

| Año de la fecha del proceso | Procesos | Presidencia | Ministerio | Admitido en el sector | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 148.823 | 0,02 % | 31,08 % | 31,10 % | 63,71 % | 5,19 % |
| 2022 | 206.801 | 0,06 % | 26,67 % | 26,73 % | 68,04 % | 5,23 % |
| 2023 | 222.595 | 0,04 % | 28,91 % | 28,95 % | 65,84 % | 5,21 % |
| 2024 | 217.422 | 0,01 % | 29,44 % | 29,45 % | 65,96 % | 4,59 % |
| 2025 | 197.784 | 0,02 % | 22,76 % | 22,78 % | 72,91 % | 4,31 % |
| 2021-2025 | 993.425 | 0,03 % | 27,66 % | 27,69 % | 67,41 % | 4,90 % |
| 2026 | 14.495 | 0,05 % | 12,93 % | 12,98 % | 84,40 % | 2,62 % |

Porcentaje del monto adjudicado de cada año.

| Año de la fecha del proceso | Monto adjudicado (USD millones) | Presidencia | Ministerio | Admitido en el sector | Fuera de alcance | Sin clasificar |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 2.468,69 | 0,07 % | 18,70 % | 18,77 % | 78,53 % | 2,71 % |
| 2022 | 5.752,22 | 0,12 % | 17,03 % | 17,15 % | 79,02 % | 3,83 % |
| 2023 | 6.934,07 | 0,13 % | 21,78 % | 21,91 % | 75,31 % | 2,78 % |
| 2024 | 6.626,35 | 0,04 % | 19,70 % | 19,74 % | 77,53 % | 2,74 % |
| 2025 | 6.405,83 | 0,33 % | 18,95 % | 19,28 % | 78,39 % | 2,33 % |
| 2021-2025 | 28.187,17 | 0,15 % | 19,41 % | 19,55 % | 77,57 % | 2,88 % |
| 2026 | 2.765,71 | 0,21 % | 7,59 % | 7,80 % | 90,85 % | 1,35 % |

Detalle de lo que queda sin clasificar.

| Año de la fecha del proceso | Dudosos del catálogo (procesos) | Sin cruce (procesos) | Malformados (procesos) | Dudosos del catálogo (monto) | Sin cruce (monto) | Sin clasificar en total (USD millones) |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 1,06 % | 4,14 % | 0,00 % | 0,33 % | 2,38 % | 66,83 |
| 2022 | 1,07 % | 4,15 % | 0,00 % | 0,43 % | 3,40 % | 220,09 |
| 2023 | 0,91 % | 4,29 % | 0,01 % | 0,57 % | 2,21 % | 192,88 |
| 2024 | 1,03 % | 3,55 % | 0,00 % | 0,49 % | 2,24 % | 181,45 |
| 2025 | 1,04 % | 3,27 % | 0,00 % | 0,44 % | 1,90 % | 149,57 |
| 2021-2025 | 1,02 % | 3,87 % | 0,00 % | 0,47 % | 2,40 % | 810,82 |
| 2026 | 0,45 % | 2,17 % | 0,00 % | 0,13 % | 1,22 % | 37,33 |

Los 14.495 procesos con fecha de 2026 no entran en `DimTiempo` (ventana 2021-01 a 2025-12, decisión del diseño dimensional) y no están en los totales de 2021 a 2025; se muestran aparte para que la semilla cubra todos los `buyer_id` descargados. Con la fecha del archivo en lugar de `releases.date` las cifras por año serían otras (Q-10); la fecha de negocio ya está decidida.

La participación admitida en el sector es la más baja en 2025 (22,78 % de los procesos) frente a 26,73 % a 31,10 % en los otros años. La semilla no explica esa diferencia: no se investigó si viene de la fusión de ministerios de 2025 y 2026 o del crecimiento de otras entidades. Queda señalada, no resuelta.

## 5. Casos que quedan sin clasificar

### 5.1. Cómo se eligieron

Un caso es un grupo del catálogo (UDAF), una raíz sin cruce o un identificador malformado. Se ordenan por peso, que es la suma de su participación en los procesos y de su participación en el monto de 2021 a 2025. Quedan 502 casos (16 grupos del catálogo, 480 raíces sin cruce, 6 malformados). La lista corta toma los 50 primeros. La columna «Origen» dice si el caso viene de un grupo del catálogo o de una raíz que no cruzó; en este segundo caso el nombre es la grafía más frecuente de SERCOP y sirve solo para sustentar la recomendación, nunca para unir.

**Criterio de las recomendaciones** (elección del equipo, lectura literal de la decisión de alcance 1: «Presidencia, ministerios e institutos que dependen de ellos»): entra solo lo que es Presidencia, ministerio o instituto con dependencia acreditada, o lo que el propio catálogo coloca dentro de su estructura; todo lo demás sale. Una recomendación `dudosa` significa que ninguna fuente revisada acredita la dependencia y clasificar sería inventar. Una raíz sin cruce solo se clasifica con respaldo individual por RUC (decisión D6); las recomendaciones de esta lista indican hacia dónde se resolverían cuando exista ese respaldo, y mientras tanto siguen `dudosa`.

### 5.2. Lista corta de 50 casos

Peso de la lista: 30.002 procesos (3,02 % de los procesos de 2021 a 2025) y USD 735,44 millones (2,61 % del monto). Son el 61,7 % de los procesos y el 90,7 % del monto que queda sin clasificar.

| N° | Caso | Clave | Origen | Procesos | Monto (USD millones) | Recomendación | Bloque |
|---:|---|---|---|---:|---:|---|---|
| 1 | CUERPO DE INGENIEROS DEL EJERCITO | RUC 1768007040001 | sin cruce | 2.608 | 89,52 | dudosa | B3 |
| 2 | GUAYAQUIL SIGLO XXI, FUNDACIÓN MUNICIPAL PARA LA REGENERACIÓN URBANA | RUC 0992183721001 | sin cruce | 692 | 88,15 | fuera | B6 |
| 3 | AUTORIDAD AEROPORTUARIA DE GUAYAQUIL FUNDACION DE LA M.I MUNICIPALIDAD DE GUAYAQUIL | RUC 0992179619001 | sin cruce | 388 | 89,95 | fuera | B6 |
| 4 | INSTITUTO NACIONAL DE INVESTIGACIONES AGROPECUARIAS - I.N.I.A.P. - PLANTA CENTRAL | UDAF 390 | catálogo | 2.856 | 16,55 | dudosa hasta respaldo | B8 |
| 5 | INSTITUTO NACIONAL DE ESTADISTICAS Y CENSOS - PLANTA CENTRAL | UDAF 64 | catálogo | 2.038 | 14,64 | dudosa hasta respaldo | B8 |
| 6 | INSTITUTO GEOGRAFICO MILITAR | UDAF 72 | catálogo | 773 | 48,19 | dudosa hasta respaldo | B8 |
| 7 | SECRETARÍA TÉCNICA DE GESTIÓN INMOBILIARIA DEL SECTOR PÚBLICO | RUC 1768146750001 | sin cruce | 622 | 48,87 | fuera | B1 |
| 8 | FUNDACION TERMINAL TERRESTRE DE GUAYAQUIL | RUC 0992236574001 | sin cruce | 712 | 44,03 | fuera | B6 |
| 9 | CORPORACION PARA LA SEGURIDAD CIUDADANA DE GUAYAQUIL | RUC 0992457597001 | sin cruce | 334 | 40,87 | fuera | B6 |
| 10 | INSTITUTO OCEANOGRAFICO Y ANTARTICO DE LA ARMADA | UDAF 611 | catálogo | 886 | 24,90 | dudosa hasta respaldo | B8 |
| 11 | SECRETARIA DE EDUCACION SUPERIOR, CIENCIA, TECNOLOGIA E INNOVACION | RUC 1768157600001 | sin cruce | 294 | 30,40 | fuera | B1 |
| 12 | ACERIAS NACIONALES DEL ECUADOR SOCIEDAD ANONIMA (A.N.D.E.C.) | RUC 0990001340001 | sin cruce | 631 | 20,10 | fuera | B6 |
| 13 | DIRECCIÓN ZONAL ZONA 8 - SECRETARIA TÉCNICA DE GESTIÓN INMOBILIARIA DEL SECTOR PÚBLICO | RUC 0968604550001 | sin cruce | 371 | 23,14 | fuera | B1 |
| 14 | FUNDACION MUNICIPAL DE LA MUJER Y EL NIÑO DE CUENCA | RUC 0190408485001 | sin cruce | 989 | 3,03 | fuera | B6 |
| 15 | FUNDACION MUSEOS DE LA CIUDAD | RUC 1792042704001 | sin cruce | 770 | 7,51 | fuera | B6 |
| 16 | INSTITUTO NACIONAL DE INVESTIGACION EN SALUD PUBLICA INSPI DR LEOPOLDO IZQUIETA PEREZ- PLANTA CENTRAL | UDAF 267 | catálogo | 617 | 10,18 | dudosa hasta respaldo | B8 |
| 17 | CORPORACION DE PROMOCION ECONOMICA CONQUITO | RUC 1791905911001 | sin cruce | 801 | 2,20 | fuera | B6 |
| 18 | COMANDO DE INTELIGENCIA MILITAR CONJUNTO DE LAS FUERZAS ARMADAS | RUC 1768184250001 | sin cruce | 653 | 4,92 | dudosa | B3 |
| 19 | SECRETARIA TECNICA ECUADOR CRECE SIN DESNUTRICION INFANTIL | RUC 1768143140001 | sin cruce | 264 | 15,89 | fuera | B1 |
| 20 | CORPORACION REGISTRO CIVIL DE GUAYAQUIL | RUC 0992441127001 | sin cruce | 309 | 14,40 | fuera | B6 |
| 21 | FAME S.A. | RUC 1790932966001 | sin cruce | 577 | 5,97 | fuera | B6 |
| 22 | MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | RUC 1768192860001 | sin cruce | 615 | 4,71 | dentro: ministerio, con respaldo | B4 |
| 23 | INSTITUTO DE FOMENTO DE LAS ARTES INNOVACION Y CREATIVIDADES - PLANTA CENTRAL | UDAF 303 | catálogo | 720 | 0,86 | dudosa hasta respaldo | B8 |
| 24 | FUNDACION TEATRO NACIONAL SUCRE | RUC 1791984714001 | sin cruce | 584 | 4,22 | fuera | B6 |
| 25 | FEDERACION DEPORTIVA DEL GUAYAS | RUC 0990057907001 | sin cruce | 374 | 6,73 | fuera | B6 |
| 26 | FIDEICOMISO MERCANTIL FONDO AMBIENTAL PARA LA PROTECCION DE LAS CUENCAS Y AGUA - FONAG | RUC 1791722205001 | sin cruce | 517 | 2,63 | fuera | B6 |
| 27 | CASA MILITAR PRESIDENCIAL - PLANTA CENTRAL | UDAF 85 | catálogo | 466 | 3,90 | dentro: presidencia, con respaldo | B7 |
| 28 | CONCENTRACIÓN DEPORTIVA DE PICHINCHA | RUC 1791827929001 | sin cruce | 437 | 4,54 | fuera | B6 |
| 29 | DIRECCION ZONAL - ZONA 4 - SECRETARIA TECNICA DE GESTION INMOBILIARIA DEL SECTOR PUBLICO | RUC 1360086090001 | sin cruce | 350 | 6,89 | fuera | B1 |
| 30 | INSTITUTO NACIONAL DE PATRIMONIO CULTURAL | UDAF 141 | catálogo | 439 | 4,13 | dudosa hasta respaldo | B8 |
| 31 | EMPRESA PUBLICA MUNICIPAL DE TURISMO, PROMOCION CIVICA Y RELACIONES INTERNACIONALES DE GUAYAQUIL,EP | RUC 0968603900001 | sin cruce | 333 | 7,10 | fuera | B6 |
| 32 | INSTITUTO DE INVESTIGACION GEOLOGICO Y ENERGETICO | UDAF 427 | catálogo | 456 | 3,48 | dudosa hasta respaldo | B8 |
| 33 | CORPORACIÓN AEROPORTUARIA DE CUENCA | RUC 0190335852001 | sin cruce | 345 | 6,57 | fuera | B6 |
| 34 | ALDEAS INFANTILES SOS ECUADOR | RUC 1790174417001 | sin cruce | 550 | 0,74 | fuera | B6 |
| 35 | NUCLEO DE SOLCA MACH | RUC 1791818881001 | sin cruce | 444 | 2,71 | fuera | B6 |
| 36 | CUERPO DE BOMBEROS DE SAMBORONDON | RUC 0968529080001 | sin cruce | 422 | 3,21 | fuera | B6 |
| 37 | COORDINACIÓN ZONAL 9 - SENESCYT | RUC 1768193160001 | sin cruce | 497 | 1,02 | fuera | B1 |
| 38 | GOBIERNO AUTONOMO DESCENTRALIZADO PARROQUIAL RURAL DE SEVILLA DON BOSCO | RUC 1460016370001 | sin cruce | 394 | 3,48 | fuera | B6 |
| 39 | AGENCIA DE REGULACIÓN Y CONTROL DE ENERGÍA Y RECURSOS NATURALES NO RENOVABLES | RUC 1768193080001 | sin cruce | 344 | 4,72 | fuera | B1 |
| 40 | EXPLOCEN C.A. | RUC 1790326136001 | sin cruce | 314 | 5,42 | fuera | B6 |
| 41 | HOGAR MIGUEL LEON DE LA CIUDAD DE CUENCA | RUC 0190160890001 | sin cruce | 473 | 0,47 | fuera | B6 |
| 42 | SECRETARIA NACIONAL DE PLANIFICACION | RUC 1768192510001 | sin cruce | 232 | 5,44 | fuera | B1 |
| 43 | CEFAS-PATRONATO DEL GAPMS | RUC 1460024040001 | sin cruce | 358 | 1,49 | fuera | B6 |
| 44 | FEDERACION DEPORTIVA DE MANABI | RUC 1391719868001 | sin cruce | 348 | 1,72 | fuera | B6 |
| 45 | COORDINACION ZONAL 6 - SENESCYT | RUC 0360032780001 | sin cruce | 385 | 0,37 | fuera | B1 |
| 46 | COORDINACION ZONAL 1 - SENESCYT | RUC 1060039630001 | sin cruce | 294 | 1,58 | fuera | B1 |
| 47 | FUNDACION NIÑOS CON DESTINO EN LAS MANOS DE DIOS | RUC 1792170826001 | sin cruce | 334 | 0,20 | fuera | B6 |
| 48 | FEDERACION DEPORTIVA DE IMBABURA | RUC 1091708988001 | sin cruce | 270 | 1,28 | fuera | B6 |
| 49 | FUNDACION CALASANZ | RUC 1791825314001 | sin cruce | 299 | 0,16 | fuera | B6 |
| 50 | EMPRESA PUBLICA DE CONSTRUCCIONES DEL GOBIERNO AUTONOMO DESCENTRALIZADO PROVINCIAL DEL GUAYAS, CONSTRUGUAYAS E.P. | RUC 0968591120001 | sin cruce | 223 | 2,26 | fuera | B6 |

### 5.3. Los bloques y su motivo

| Bloque | Qué reúne | Motivo de la recomendación |
|---|---|---|
| B1 | Secretarías, coordinaciones y direcciones zonales de organismos del Ejecutivo con figura propia, sin RUC en el catálogo | No son Presidencia, ministerio ni instituto por su denominación (decisión D5). Sus equivalentes con RUC en el catálogo ya se resolvieron como `fuera_de_alcance`. |
| B3 | Unidades militares sin RUC en el catálogo | Quedan `dudosa`: ninguna fuente revisada acredita su dependencia. El grupo del Ministerio de Defensa del catálogo (UDAF 70, 119 filas) sí está dentro como ministerio. |
| B4 | Ministerios históricos cuyo RUC no consta en el catálogo | La denominación de SERCOP es de ministerio y el catálogo del 31/08/2026 no lo trae (nota 5 del archivo: excluye RUC pasivos). El catálogo oficial de 2018 tampoco trae su RUC. Entraría con un decreto de creación o fusión (sección 5.6). |
| B6 | Fundaciones, corporaciones, empresas, federaciones deportivas, bomberos, GAD parroquiales y otras personas jurídicas sin RUC en el catálogo | No son Presidencia, ministerio ni instituto: son entes de municipios (GAD, fuera por la decisión de alcance 2), organizaciones privadas o bomberos (Hito 1, exclusión provisional). |
| B7 | Casa Militar Presidencial | Órgano de la Presidencia por su denominación; el catálogo le da un grupo propio. La Vicepresidencia recibe la misma recomendación. Entraría con respaldo. |
| B8 | Institutos por denominación | La denominación no prueba la adscripción a un ministerio (ADR 0001, decisión 1). Se resuelven con el decreto o estatuto de adscripción (sección 5.5). |

Peso de cada bloque y recomendación:

| Bloque y recomendación | Casos | Procesos | % de procesos | Monto (USD millones) | % del monto |
|---|---:|---:|---:|---:|---:|
| B1: fuera | 10 | 3.653 | 0,37 % | 138,33 | 0,49 % |
| B3: dudosa | 2 | 3.261 | 0,33 % | 94,44 | 0,34 % |
| B4: dentro: ministerio, con respaldo | 1 | 615 | 0,06 % | 4,71 | 0,02 % |
| B6: fuera | 28 | 13.222 | 1,33 % | 371,13 | 1,32 % |
| B7: dentro: presidencia, con respaldo | 1 | 466 | 0,05 % | 3,90 | 0,01 % |
| B8: dudosa hasta respaldo | 8 | 8.785 | 0,88 % | 122,93 | 0,44 % |
| **Los 50 casos** | **50** | **30.002** | **3,02 %** | **735,44** | **2,61 %** |

Los otros 452 casos pesan 18.637 procesos (1,88 %) y USD 75,38 millones (0,27 %). Quedan sin clasificar y su peso queda a la vista (sección 6).

### 5.4. Decisiones del 22/11/2026 y cómo quedaron en la semilla

Las decisiones D1 a D3 salieron de la revisión del PR de la primera versión; D4 a D6 las tomó el asistente el 22/11/2026 por delegación del líder («toma las decisiones para cerrar este issue»). Todas están en `warehouse/seeds/entity_classification_decisions.csv` y se revierten borrando su fila. Las citas del COESCOP y de la LOEI son las de la revisión y **no se verificaron de forma independiente**. El catálogo oficial de instituciones al 31/03/2018 sí se leyó directamente de su PDF oficial para D1 y D4.

| N° | Decisión | Cómo quedó |
|---|---|---|
| D1 | Aprobar los dos distritos de salud sin RUC en el catálogo de 2026, con fuente oficial. | Los RUC 1060040130001 (10D02 Antonio Ante-Otavalo) y 1060014130001 (10D03 Cotacachi) constan en el catálogo de 2018 bajo el grupo 320 (Ministerio de Salud Pública). Pasan a `ministerio`, `aprobada`, con ese ministerio como `parent_entity`. |
| D2 | Policía Nacional fuera del alcance vigente (COESCOP, arts. 61 y 63: rectoría del ministerio, pero el alcance son Presidencia, ministerios e institutos dependientes). | Los grupos 52, 57 y 58 pasan a `fuera_de_alcance`, `aprobada`. |
| D3 | Aprobar Presidencia, ministerios y exclusiones justificadas; institutos solo con respaldo de adscripción; excluir al INEVAL. | Presidencia y ministerios pasan a `aprobada`. La seguridad social (sector 113) y el INEVAL (grupo 214, LOEI art. 67 sin adscripción) pasan a `fuera_de_alcance`, `aprobada`. Las exclusiones restantes (educación superior, financieras públicas, sociedades con participación pública, superintendencias, Procuraduría y Parlamento Andino) también pasan a `aprobada`: ninguna es Presidencia, ministerio ni instituto. Los institutos pasan de `propuesta` a `dudosa`. |
| D4 | Aprobar las raíces históricas con respaldo individual. | Seis raíces constan en el catálogo de 2018 con el mismo RUC y pasan a `ministerio`, `aprobada`: Turismo (UDAF 510), Deporte (148), Cultura y Patrimonio (150), Desarrollo Urbano y Vivienda (550), el actual Ministerio de la Mujer y Derechos Humanos (UDAF 61, entonces Ministerio de Justicia, Derechos Humanos y Cultos) y la Coordinación Zonal 3 de Relaciones Exteriores (UDAF 120). El Ministerio del Ambiente, Agua y Transición Ecológica y sus 11 direcciones zonales no constan en 2018: siguen `dudosa` (sección 5.6). |
| D5 | Lectura de la categoría de instituto (el ADR dejó abierto si incluye otras entidades adscritas, `docs/sources/entidades.md`, sección 5.3). | La categoría se limita a institutos con adscripción verificada. Servicios, agencias, secretarías, consejos, registros y similares que constan en el catálogo pasan a `fuera_de_alcance`, `aprobada`. Siguen `dudosa` los institutos, la Vicepresidencia y la Casa Militar Presidencial (recomendados como `presidencia` con respaldo). |
| D6 | Raíces sin cruce con el catálogo. | Solo se clasifican con respaldo individual por RUC (D1 y D4). Las demás, incluidas las fundaciones y federaciones evidentes por su nombre, siguen `dudosa`: el nombre no es respaldo. La acción para el Hito 4 está en la sección 6. |

### 5.5. Institutos

Hasta documentar la adscripción de cada uno, los 14 institutos que quedan por denominación son `sin_clasificar` con `proposed_type = instituto`. Pesan 9.495 procesos (0,96 %) y USD 128,24 millones (0,45 %). Para cada uno se necesita el decreto o estatuto que lo adscribe a un ministerio, con su fecha (`docs/sources/entidades.md`, sección 4, los deja «No verificada»).

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

### 5.6. Raíces con denominación de ministerio que siguen sin respaldo

Raíces sin cruce cuya denominación en SERCOP dice «Ministerio» y que no constan ni en el catálogo de 2026 ni en el de 2018. Q-E05 pide contrastarlas con fuentes oficiales; la revisión del PR señala decretos de fusión del Ministerio del Ambiente y del de Turismo (Registro Oficial, segundo suplemento 105), citados allí y sin verificar aquí. Se aprueban por RUC cuando cada una tenga su documento.

| RUC | Denominación en SERCOP | Procesos | Monto (USD millones) | Respaldo individual |
|---|---|---:|---:|---|
| 1768192860001 | MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 615 | 4,71 | pendiente |
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

Pesan 1.886 procesos (0,19 %) y USD 8,46 millones (0,03 %). Efecto simulado de aprobarlas todas (suma de los casos, no una nueva corrida): el sector admitido pasaría a 27,88 % de los procesos y 19,58 % del monto; con los institutos también, a 28,84 % y 20,04 %.

## 6. Límites declarados

- **El catálogo es una foto al 31/08/2026** (Q-E04). No da vigencia: los procesos de 2021 a 2025 se clasifican con la entidad que el catálogo lista hoy. `valid_from` y `valid_to` están vacíos y la vigencia por fecha (SCD tipo 2) queda para el Hito 4.
- **Los institutos no entran en el sector** hasta tener respaldo de adscripción (sección 5.5). La cobertura admitida es, por eso, un piso.
- **Quedan sin clasificar** 4,90 % de los procesos y 2,88 % del monto de 2021 a 2025. De esa parte, los 50 casos de la lista son el 61,7 % de los procesos y el 90,7 % del monto; los otros 452 casos pesan 1,88 % de los procesos y 0,27 % del monto del total.
- **Las raíces sin cruce no tienen tipo en el catálogo.** La acción para el Hito 4 es contrastarlas con una fuente de RUC activo o con los decretos de creación, y aprobarlas por RUC con el archivo de decisiones.
- **El nombre de las entidades sin cruce** es la grafía más frecuente de SERCOP, no un nombre oficial (Q-13).
- **La semilla incluye 14.495 procesos de 2026** que `DimTiempo` deja fuera; los totales de este documento son de 2021 a 2025.
- **No se probó en Power BI Desktop.** La unión en Power Query y los totales de control con la semilla aplicada se verifican al construir el modelo (#70 y #71), con los controles antes y después que pide la guía.

## 7. Segunda pasada: cómo se registra una decisión

La decisión se escribe en `warehouse/seeds/entity_classification_decisions.csv` y se reaplica con el mismo script, con la opción `--overrides` y salidas nuevas. Cada fila lleva `scope` (`ruc_root`, `udaf`, `sector`, `propuesta` para aprobar todas las filas `propuesta` de un tipo sin cambiarlo, o `proposed` para resolver los grupos dudosos del catálogo cuya recomendación es ese tipo), `key`, `entity_type`, `decided_on`, `decision_note` y, opcionales, `parent_entity` (el padre acreditado) y `evidence` (la fuente). Las filas alcanzadas pasan a `aprobada` y su `source` cita la decisión y la evidencia. Un identificador malformado nunca se toca; un RUC que consta en varios grupos solo se decide por `ruc_root`; dos decisiones que den a una fila tipos distintos hacen fallar el script.

## 8. Estado de los criterios del issue #68

| Criterio | Estado |
|---|---|
| La semilla existe, sin duplicados de clave, con `source` y `status` en cada fila | Cumplido: 6.100 filas, clave `buyer_id` única (revisión de la salida y comparación byte a byte de la regeneración por la revisión del PR) |
| La unión nunca usa `buyer.name`; probada | Cumplido: pruebas de unión exacta, por raíz, nombre que no une y ambigüedad |
| Lista de casos dudosos con recomendación; decisión registrada y reflejada en la semilla | Cumplido: decisiones D1 a D6 del 22/11/2026 en el archivo de decisiones y aplicadas; lo que no tiene respaldo queda `dudosa` con su acción para el Hito 4 |
| Cobertura medida y escrita | Cumplido (sección 4), con la regla de admisión de la sección 3.5 |
| Lo no clasificado queda fuera de los indicadores con su peso a la vista | Cumplido (secciones 4 y 6) |
| La regla en un párrafo con su origen | Cumplido (sección 2) |
| `ruff` y `pytest` en verde | Ver el PR |
