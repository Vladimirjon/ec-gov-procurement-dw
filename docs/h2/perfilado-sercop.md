# Perfilado completo de calidad de la fuente SERCOP (2021–2025)
## Evaluación multidimensional sobre 1.007.920 procesos de contratación abierta (OCDS)

**Equipo:** Grupo 5  
**Integrantes:** Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel y Jorge Torres  
**Sector:** Gobierno central del Ecuador  
**Fecha de corte y ejecución:** 21 de noviembre de 2026  
**Entregable:** Hito 2 — Diagnóstico de calidad de la fuente principal (Issue #62)  
**Evidencia agregada:** `docs/h2/evidencia/perfil-calidad-sercop-AAAA.json` (2021 a 2025), `docs/h2/evidencia/perfil-calidad-sercop-resumen.csv` y `docs/h2/evidencia/perfil-calidad-sercop-por-comprador.csv`  

---

## 1. Ficha técnica de la ejecución del perfilado

El diagnóstico de calidad se ejecutó de forma exhaustiva sobre el **100 % de los registros** de la fuente masiva transaccional de SERCOP (cinco años calendario completos, 2021 a 2025), sin recurrir a muestreos parciales de 1.000 filas, en estricto cumplimiento de las secciones 3.2, 3.3, 4.4, 5 (pasos 8 y 10) y 6.3 de la guía del Hito 2.

| Atributo | Detalle técnico |
|---|---|
| **Script ejecutor** | `scripts/profile_h2_quality.py` |
| **Hash SHA-256 del script (LF)** | `F4F0DE2857DE6B143A0DB27CE62E6C67BA2177556444D20451F2ABECB312EB8B` |
| **Entorno de ejecución** | `python -I` (modo aislado, biblioteca estándar exclusivamente: `csv`, `json`, `pathlib`, `hashlib`, `re`, `datetime`, `codecs`, `contextlib`) |
| **Comando exacto de ejecución** | `python -I scripts/profile_h2_quality.py --derived-dir data/derivados --output-dir docs/h2/evidencia --years 2021 2022 2023 2024 2025 --reference-awarded-2025 7318.7 --buyer-summary-csv docs/h2/evidencia/perfil-calidad-sercop-por-comprador.csv` |
| **Fecha y hora de ejecución (UTC)** | 21 de noviembre de 2026, 23:38:39 UTC (18:38:39 hora local Ecuador, UTC-5) |
| **Universo procesado** | **1.007.920 releases** OCDS únicos; **981.348** licitaciones (`tender`); **975.302** adjudicaciones (`awards`); **949.550** contratos (`contracts`). |
| **Monto total adjudicado medido** | **USD 30.952.880.306,92** (~30.952,88 millones de dólares estadounidenses). |
| **Monto total licitado medido** | **USD 25.072.968.705,53** (~25.072,97 millones de dólares estadounidenses). |
| **Unidad de la referencia** | `--reference-awarded-2025` se entrega en **millones de USD** (7318.7 = USD 7.318,7 millones, informe de SERCOP, p. 12). |
| **Protección y privacidad** | Salida 100 % agregada. Cero registros individuales, identificadores `ocid`, cédulas o nombres de personas naturales en los archivos de evidencia versionados. |

### 1.1. Inventario de archivos de entrada leídos y verificación de integridad

Conforme a la decisión de conexión [Ruta A](../h2/decision-formato-conexion.md) aprobada por el líder el 21/11/2026, los datos analizados corresponden a las tablas CSV extraídas de los paquetes OCDS del portal masivo de SERCOP, almacenadas bajo `data/derivados/sercop-portal-csv-AAAA-<sello>/`:

| Año | Archivo | Tamaño (bytes) | Hash SHA-256 | Grano / Rol |
|:---:|---|:---:|---|---|
| **2021** | `releases_2021.csv` | 42.175.432 | `BFDD0DF12D38EA5059A3F2F40126476B18637B65AA1057A3A981DDF26AD1C15C` | 1 release por fila (`ocid`) |
| 2021 | `tender_2021.csv` | 105.549.708 | `55C70E656F622F84002CB1539ED2465C42A03273BEBF8F17682B61BEE1A0434B` | Etapa de licitación / valor estimado |
| 2021 | `awards_2021.csv` | 33.860.225 | `9F70AC70A11D1739C1C6DD8DC70DEB22BCAA1511A30804520B80289A0583AEFA` | Etapa de adjudicación / monto adjudicado |
| 2021 | `contracts_2021.csv` | 31.299.741 | `B5CB8519B40C12096FDC3EBC7A3500F9E65AFF102582AE622903FF641BFB66A1` | Etapa contractual / fecha de suscripción |
| **2022** | `releases_2022.csv` | 53.713.051 | `620122A4A2F40928F6D9A5AC01899116ACCD9B3A6C21F4F2A96ADAAAD3EACFC6` | 1 release por fila (`ocid`) |
| 2022 | `tender_2022.csv` | 131.104.127 | `C34DB365A7B1A7BC1EDAA7844C8B8CD04FF3935AA948E86F4AD8CD6C9350EF93` | Etapa de licitación / valor estimado |
| 2022 | `awards_2022.csv` | 40.945.150 | `E16B95AA33D5595653A4EF9AFDA911B558C5B5F05824668D17428293655BFB16` | Etapa de adjudicación / monto adjudicado |
| 2022 | `contracts_2022.csv` | 39.138.680 | `E33858D70CDFC414E51A8063A0C7A2583381B5E1C4FBA1005F902ACFE7AAF1E0` | Etapa contractual / fecha de suscripción |
| **2023** | `releases_2023.csv` | 54.530.086 | `5E12D2F9EE5813761AECE8B72404274F5C0DE4E59A3C4F97A3E63FA6C1D7628C` | 1 release por fila (`ocid`) |
| 2023 | `tender_2023.csv` | 136.729.553 | `E4A98BBB9436AC43565310398D6C09D5EC4B6EDC03CA5615873353F9D3EE86C6` | Etapa de licitación / valor estimado |
| 2023 | `awards_2023.csv` | 42.461.180 | `905B48E336F981A8687BD8F0988B5A4F160D06D18A94BB6F4D429D908C0A283D` | Etapa de adjudicación / monto adjudicado |
| 2023 | `contracts_2023.csv` | 40.902.482 | `4115D53DDD668432CE0DA90689042C1F6DE172929D2950668FE10BBB47EA49B0` | Etapa contractual / fecha de suscripción |
| **2024** | `releases_2024.csv` | 55.152.909 | `59DC691B193682AF1A65DADC6BE1D73236CEF195DCDCE6C75CB8074C2BFEC3B8` | 1 release por fila (`ocid`) |
| 2024 | `tender_2024.csv` | 136.474.719 | `37715B0156623AA49FB4171B3EC7B025890AAD8529B4D0EA874507DD64D21DA5` | Etapa de licitación / valor estimado |
| 2024 | `awards_2024.csv` | 42.683.917 | `5398288E9BB24835D642EC80AC42F64744ADB6820D729ACA288E077E68A97426` | Etapa de adjudicación / monto adjudicado |
| 2024 | `contracts_2024.csv` | 40.874.548 | `0A855EF7A5616A74D014DFB87EACE0974B3E9D1383603B5A64B50A032C0C1D1F` | Etapa contractual / fecha de suscripción |
| **2025** | `releases_2025.csv` | 48.256.694 | `99B1A2674FEC9E15D5CD755783EEE5D62D143AC14C0D49FD6F1ED535D7962224` | 1 release por fila (`ocid`) |
| 2025 | `tender_2025.csv` | 118.964.510 | `60FA69FE7CC75299F8444BDD1D9F1323BFA1AF3FAEE18804498EC9B16B2AE32A` | Etapa de licitación / valor estimado |
| 2025 | `awards_2025.csv` | 36.871.647 | `4D46D444128E381B454135C968E68B42D9A843AC26D8AF033CF0C506A5FFDC1C` | Etapa de adjudicación / monto adjudicado |
| 2025 | `contracts_2025.csv` | 35.517.722 | `26B0B30B9F11242006919365D0B93D939350847567B6D3BC76702D9E4A3AC697` | Etapa contractual / fecha de suscripción |

---

## 2. Totales de control por año y consolidado 2021–2025

De acuerdo con el paso 10 de la guía del Hito 2, estos totales constituyen el **total de control inicial** antes de cualquier transformación. En el Hito 3 (#69 / H3-03 / H3-06) deberán cuadrar exactamente las filas y sumas monetarias resultantes tras la limpieza:

| Año | Releases (`ocid` únicos) | Filas `tender` | Filas `awards` | Filas `contracts` | Suma `awards.amount` (USD) | Suma `tender.value` (USD) | Procesos con ambos importes | % con ambos importes |
|:---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| **2021** | 167.058 | 165.616 | 166.983 | 158.199 | $4.676.997.257,82 | $3.682.296.515,41 | 146.314 | 87,58 % |
| **2022** | 212.324 | 203.147 | 200.173 | 194.695 | $7.118.687.591,72 | $5.855.681.059,39 | 175.903 | 82,85 % |
| **2023** | 217.913 | 213.841 | 212.989 | 208.852 | $6.037.778.222,93 | $4.798.618.255,15 | 191.312 | 87,79 % |
| **2024** | 219.185 | 212.386 | 210.445 | 206.289 | $6.895.826.062,72 | $5.518.333.500,28 | 187.672 | 85,62 % |
| **2025** | 191.440 | 186.358 | 184.712 | 181.515 | $6.223.591.171,73 | $5.218.039.375,30 | 167.375 | 87,43 % |
| **Total** | **1.007.920** | **981.348** | **975.302** | **949.550** | **$30.952.880.306,92** | **$25.072.968.705,53** | **868.576** | **86,18 %** |

### Distribución de importes por proceso (relación tender-awards):
- **Procesos con ambos importes (adjudicado y estimado):** 868.576 procesos (86,18 %). Este subconjunto es la base estricta para responder la pregunta P2 (desviación presupuestaria).
- **Procesos con adjudicación pero sin valor estimado:** 95.874 procesos (9,51 %). Procedimientos que por su naturaleza normativa o captura en el portal no registraron presupuesto referencial en `tender`.
- **Procesos con valor estimado pero sin adjudicación:** 2.979 procesos (0,30 %). Procedimientos desiertos, cancelados o en etapa precontractual sin adjudicatario.
- **Procesos sin ningún importe registrado:** 40.491 procesos (4,02 %).

---

## 3. Matriz de diagnóstico de calidad (seis dimensiones)

Conforme a la sección 4.4 y la plantilla 6.3 de la guía del Hito 2, se presenta la lista formal de hallazgos identificados mediante códigos estables `Q-01` a `Q-11`. Cada acción propuesta está redactada como tarea técnica transferible a Power Query / ETL en el Hito 3 (#64):

| ID | Tabla · Campo | Dimensión | Evidencia numérica medida (2021–2025) | Impacto en preguntas P1 a P3 | Acción propuesta para H3 (tarea de transformación) |
|---|---|---|---|---|---|
| **Q-01** | `tender · value_amount` | **Completitud** | Ausente en 109.793 licitaciones en los 5 años (11,19 % de las filas de tender; 10,89 % de los releases). Por año: 2021=19.050 (11,50 %), 2022=26.356 (12,97 %), 2023=21.993 (10,28 %), 2024=24.060 (11,33 %), 2025=18.334 (9,84 %). Cero filas contienen el valor 0.0. | **Impacto crítico en P2:** la desviación `(A - E) / E` no se puede calcular en estos procesos. Imputar 0.0 generaría divisiones por cero o distorsiones infinitas. | En Power Query, mantener `tender.value_amount` como numérico anulable. Crear un indicador `tiene_valor_estimado` y documentar que la medida de desviación de P2 filtra solo los 868.576 procesos con ambos importes. |
| **Q-02** | `awards · correctedValue_amount` y `enteredValue_amount` | **Completitud** | **100,0 % de nulos.** Las 975.302 filas de `awards` en los cinco años tienen ambas columnas vacías (0 valores poblados). | **Sin impacto en cálculo:** no es posible contrastar ofertas corregidas con adjudicadas. | En Power Query, eliminar ambas columnas en el paso inicial de selección de campos. |
| **Q-03** | `awards · date`, `tender · tenderPeriod_startDate`, `contracts · dateSigned` | **Completitud** | Cobertura sobre releases inferior al 25 % en los 5 años: `tenderPeriod_startDate` en 17,10 % a 23,40 %; `awards.date` en 13,96 % a 17,63 %; `contracts.dateSigned` en 14,57 % a 19,42 %. En contraste, `releases.date` tiene **100,0 % de cobertura** (1.007.920 filas). | **Impacto alto en P1 y P3:** usar una fecha de etapa dejaría sin fecha a entre el 76,6 % y el 86,0 % de los procesos de cada año (porcentaje de procesos; la cobertura ponderada por importe no se midió). | Adoptar `releases.date` como fecha de negocio vinculada a `DimTiempo` (sujeto a aprobación del líder, §4). Conservar las fechas de etapa como atributos secundarios opcionales. |
| **Q-04** | `releases · date` y fechas de etapa; `awards · amount`, `tender · value_amount` | **Validez** | Cero fechas anteriores a 2015, cero no interpretables y cero `releases.date` posteriores al corte (la máxima de 2025 es 2026-11-21, el día de la descarga). Hay 2 `contracts.dateSigned` posteriores al corte en 2025 (la máxima es 2027-01-06). Cero importes negativos y cero importes iguales a 0 en `awards` y `tender`. | **Impacto menor en P1 y P3:** dos contratos con fecha de firma futura no afectan a la fecha de negocio recomendada (`releases.date`). | Derivar la clave `FechaID` (`YYYYMMDD`) desde `releases.date`; si se usa `contracts.dateSigned` como atributo, marcar las fechas posteriores al corte para auditoría. |
| **Q-05** | `tender · value_currency`, `awards · currency`; codificación de las tablas CSV | **Validez** | **100,0 % de los importes presentes están en USD** (cero monedas extranjeras); la moneda vacía coincide con el importe vacío (p. ej. 19.050 en `tender` 2021). Las 20 tablas `releases`, `tender`, `awards` y `contracts` se decodifican como UTF-8 estricto, sin BOM. `tender_2024.csv` contiene 3 caracteres de reemplazo U+FFFD ya presentes en el origen (medido solo en las tablas `tender`). | **Sin impacto en sumas monetarias.** Riesgo menor de texto dañado en 3 caracteres de `tender_2024`. | En Power Query, importar los CSV con `Csv.Document(..., [Encoding=65001])` y tipificar los importes como número decimal. Una versión previa de este perfil clasificó tres archivos como Windows-1252 por un defecto del script (decodificación por bloques); está corregido y cubierto por una prueba. |
| **Q-06** | `releases · ocid` y `awards · (ocid, id)` | **Unicidad** | Cero `ocid` duplicados dentro de cada año y cero `ocid` compartidos entre años (1.007.920 procesos únicos); cero pares (`ocid`, `release_id`) repetidos en `releases` y `tender`; cero `award.id` repetidos dentro de un proceso. **1.801 procesos** tienen más de una adjudicación (2021=386, 2022=424, 2023=329, 2024=362, 2025=300; el máximo es 268 en un proceso de 2021). Esas adjudicaciones aportan 10.827 filas adicionales (2.717, 2.447, 1.775, 2.274 y 1.614 por año), igual a filas de `awards` menos procesos con adjudicación; el indicador `pares_duplicados` del JSON mide exactamente eso. En `contracts` son 9.358 filas adicionales (2.146, 2.236, 1.601, 2.015 y 1.360). | **Impacto crítico en el modelo (P1 y P2):** un join 1 a N directo entre `tender` y `awards` duplicaría `tender.value_amount`. No se midió si las adjudicaciones múltiples son lotes, ítems u otra causa. | En Power Query, definir el grano de la tabla de hechos a nivel de proceso (`ocid`) agregando `awards` (suma de `amount`) antes de unir, o separar una tabla de adjudicaciones y mantener el importe estimado en el grano de proceso. |
| **Q-07** | `releases · buyer_id` | **Consistencia** | De 1.007.920 filas, 780.471 (77,43 %) tienen forma simple `EC-RUC-{13}` y 227.406 (22,56 %) tienen sufijo `EC-RUC-{13}-{sufijo}`. Hay **43 registros malformados** (2021=0, 2022=7, 2023=25, 2024=9, 2025=2). | **Impacto alto en P1 a P3 (DimEntidad):** el cruce con el catálogo de entidades fallaría en el 22,56 % si se hace por coincidencia exacta. | En Power Query, extraer una columna `RUC_13` (quitar el prefijo `EC-RUC-` y el sufijo) para cruzar por raíz según el ADR 0001. Marcar los 43 malformados como `NO_IDENTIFICADO`. |
| **Q-08** | `tender · procuringEntity_id` vs `releases · buyer_id` | **Consistencia** | Sobre 981.348 filas de `tender`: coinciden de forma exacta 201.249 (20,51 %); coinciden en la raíz de 13 dígitos y difieren en el sufijo 779.657 (79,45 %); distinta raíz, 0; sin uno de los dos identificadores, 442 (0,05 %). | **Impacto bajo en P1 y P2:** la raíz de 13 dígitos es consistente entre ambos campos; solo cambia el sufijo. | Modelar `DimEntidad` desde la raíz de 13 dígitos del `buyer_id`, según la regla del ADR 0001 (unión por `buyer.id` o raíz, nunca por nombre). |
| **Q-09** | `awards · amount` (2025) vs Rendición de Cuentas SERCOP | **Exactitud** | Cifra preliminar publicada por SERCOP (informe 2025, p. 12): USD 7.318,7 millones. Suma medida en los CSV de 2025: **USD 6.223,59 millones**. Diferencia absoluta: **USD 1.095,11 millones** (-14,96 %). **Brecha sin explicar.** Contexto medido (conteos, no importes): 5 adjudicaciones sin monto; 32.244 adjudicaciones con `status` vacío; 4.376 adjudicaciones con fecha de 2026. | **Impacto en P1:** el total del DW difiere del agregado institucional y debe presentarse con esa salvedad. | Incorporar una nota metodológica en el tablero y en el documento de diseño: fuente provisional y nacional frente a datos abiertos transaccionales; la brecha no se explica con los datos disponibles. |
| **Q-10** | `releases · date` vs año del archivo | **Oportunidad** | Entre el **7,57 % y el 11,19 %** de los procesos de cada archivo tienen `releases.date` en un año posterior al del archivo: 2021=18.235 (10,92 %), 2022=23.758 (11,19 %), 2023=19.076 (8,75 %), 2024=20.832 (9,50 %), 2025=14.492 (7,57 %). Ninguno de los 60 meses de 2021 a 2025 está vacío. | **Impacto alto en P3:** agrupar los meses por el año del archivo, y no por la fecha real, desfasa las series. | Usar `releases.date` para asignar el mes y el año de `DimTiempo`; conservar `AnioProceso` (año del archivo) como atributo auxiliar. |
| **Q-11** | `tender · procurementMethodDetails` y `tender · description` | **Validez** (estructura del archivo) | `tender_AAAA.csv` trae campos de texto con saltos de línea dentro de comillas: 380 campos en 2021, 358 en 2022, 61 en 2023, 0 en 2024 y 1 en 2025 (800 en total, cada uno en un registro distinto). Por columna: `procurementMethodDetails` 380, 356, 60, 0 y 0 (796) y `description` 0, 2, 1, 0 y 1 (4). Un registro con salto ocupa más de una línea física del archivo: `tender_2025.csv` tiene 186.360 líneas para 186.358 registros más el encabezado, y `tender_2021.csv` tiene 380 líneas de más (en 2022 son 359 para 358 campos, porque uno trae dos saltos). Fuente: campo `fields_with_line_break` de `docs/sources/sercop-AAAA-portal-csv-summary.json`, contrastado con una lectura propia que respeta las comillas (mismos totales por año); el desglose por columna sale de esa lectura y no está en los resúmenes versionados. | **Impacto en P1 a P3:** un lector que ignora las comillas parte el registro en varias filas e infla el conteo de `tender`. Solo los 4 saltos de `description` (columna 5) caen antes de `value_amount` (columna 9, el importe estimado de P2) y podrían desplazarlo si el registro se parte (inferencia); los 796 de `procurementMethodDetails` (columna 12) caen después. En Power BI Desktop, con `tender_2025` se vieron 186.360 filas en «Origen» y 186.359 tras promover encabezados, una más que los 186.358 registros reales (observación del líder; la causa exacta es una inferencia, ver `decision-formato-conexion.md` §5.5). | En la consulta de conexión de Power Query, fijar `QuoteStyle=QuoteStyle.Csv` (es parte de la conexión, no una limpieza). En H3, normalizar los saltos de línea de `procurementMethodDetails` y de `description`, y comprobar que el conteo de `tender` coincide con el total de control (981.348 filas). |

---

## 4. Recomendación técnica sobre la regla de fecha de negocio (`DimTiempo`)

En cumplimiento del [ADR 0004](../adr/0004-modelo-dimensional.md) y las guías de los hitos 1 y 2, se evaluaron cuantitativamente las cuatro fechas candidatas sobre el universo de 1.007.920 procesos:

### 4.1. Cobertura porcentual comparativa por año

| Fecha candidata | Tabla origen | 2021 | 2022 | 2023 | 2024 | 2025 | Total 2021–2025 | Veredicto técnico |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **`releases.date`** | `releases` | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 % (1.007.920)** | **Candidata recomendada** |
| `tender.tenderPeriod_startDate` | `tender` | 22,01 % | 23,40 % | 18,03 % | 19,51 % | 17,10 % | 19,97 % (201.250) | Inviable como principal (>76 % de procesos sin fecha) |
| `awards.date` | `awards` | 17,63 % | 16,94 % | 14,50 % | 14,99 % | 13,96 % | 16,06 % (161.830) | Inviable como principal (>82 % de procesos sin fecha) |
| `contracts.dateSigned` | `contracts` | 17,57 % | 19,42 % | 15,74 % | 16,73 % | 14,57 % | 16,81 % (169.448) | Inviable como principal (>82 % de procesos sin fecha) |

### 4.2. Análisis del desfase y propuesta de regla para decisión del líder

1. **Hallazgo:** `releases.date` es la fecha del release OCDS; que sea la de la última actualización o publicación es una **inferencia**, no un dato de la fuente. Se midió que entre el 7,57 % y el 11,19 % de los procesos de cada archivo tienen una fecha de un año posterior al del archivo (por ejemplo, 18.235 procesos del archivo de 2021 tienen fecha de 2022).
2. **Recomendación para el líder (a someter en el chat):**
   - **Regla principal de tiempo:** Vincular `FactContratacion[FechaID]` a `DimTiempo[Fecha]` a través de la fecha extraída de `releases.date`. Al tener **100,0 % de completitud**, garantiza que ningún proceso quede huérfano ni excluido del tablero analítico.
   - **Tratamiento del desfase de lote:** Crear en la tabla de hechos el campo `AnioProceso` (derivado del año del archivo OCDS; que corresponda al inicio del procedimiento es una inferencia). De esta forma, el usuario podrá filtrar tanto por año de inicio (`AnioProceso`) como por fecha de ejecución/publicación efectiva (`DimTiempo[Anio]`).

---

## 5. Reconciliación con el reconocimiento del Hito 1

Se contrastaron las cifras obtenidas en este perfilado completo frente a las documentadas en el Hito 1 (`docs/requirements/hito1.md`, líneas 167–180) y en el reconocimiento de la fuente (`docs/sources/reconocimiento.md`, líneas 260–275):

| Métrica | Año | Hito 1 (ZIP JSON crudo, oct/nov 2026) | Hito 2 (CSV masivos, 21/11/2026) | Diferencia | Causa documentada |
|---|:---:|:---:|:---:|:---:|---|
| **Releases / `ocid`** | 2021 | 167.058 | 167.058 | 0 | Coincidencia exacta al 100 %. |
| Releases con tender | 2021 | 165.616 | 165.616 | 0 | Coincidencia exacta al 100 %. |
| Filas de awards | 2021 | 166.983 | 166.983 | 0 | Coincidencia exacta al 100 %. |
| Awards con monto numérico | 2021 | 166.980 | 166.980 | 0 | Coincidencia exacta al 100 % (3 vacíos). |
| Procesos con ambos importes | 2021 | 146.314 | 146.314 | 0 | Coincidencia exacta al 100 %. |
| **Releases / `ocid`** | 2024 | 219.185 | 219.185 | 0 | Coincidencia exacta al 100 %. |
| Filas de awards | 2024 | 210.445 | 210.445 | 0 | Coincidencia exacta al 100 %. |
| Awards con monto numérico | 2024 | 210.439 | 210.439 | 0 | Coincidencia exacta al 100 % (6 vacíos). |
| Procesos con ambos importes | 2024 | 187.672 | 187.672 | 0 | Coincidencia exacta al 100 %. |
| **Releases / `ocid`** | 2025 | **190.619** | **191.440** | **+821** | **Actualización continua del portal.** La descarga de H1 se realizó el 11/10/2026; la descarga de H2 se realizó el 21/11/2026. En 41 días el portal incorporó 821 nuevos procesos. |
| Filas de awards | 2025 | 183.891 | 184.712 | +821 | Actualización continua del portal (+821 adjudicaciones). |
| Procesos con ambos importes | 2025 | 166.555 | 167.375 | +820 | Crecimiento de procesos cerrados con adjudicación (+820). |
| Procesos con multi-adjudicación | 2025 | 300 | 300 | 0 | Coincidencia exacta: 300 procesos tienen más de 1 adjudicación (`hito1.md` L174). |

**Conclusión de reconciliación:** Los datos de 2021 y 2024 reproducen de manera fidedigna los conteos de H1. En 2025, el incremento de 821 procesos evidencia que el portal del SERCOP actualiza dinámicamente los paquetes anuales a medida que se registran procedimientos tardíos. No existe error de descarga ni corrupción de datos; se trabaja con la versión más actualizada al corte del Hito 2.

---

## 6. Exactitud: contraste frente a la cifra oficial publicada de SERCOP 2025

En la rendición de cuentas institucional preliminar del SERCOP (año 2025, p. 12), el organismo rector publicó la cifra oficial consolidada de contratación pública:

- **Monto oficial de referencia:** **USD 7.318,7 millones** ($7.318.700.000,00 USD).
- **Monto total medido en los CSV de 2025:** **USD 6.223,59 millones** ($6.223.591.171,73 USD).
- **Diferencia absoluta:** **USD 1.095,11 millones** ($1.095.108.828,27 USD).
- **Diferencia relativa:** **-14,96 %** respecto a la cifra de rendición de cuentas.

### Contexto medido y brecha sin explicar
La diferencia de USD 1.095,11 millones queda **sin explicar** con los datos disponibles (`unexplained_difference_usd` en el JSON de 2025). Lo medido son conteos, no importes, y no permite repartir la brecha:

1. **Adjudicaciones sin monto:** 5 adjudicaciones de 2025 carecen de importe (`awards.amount` vacío).
2. **Adjudicaciones con `status` vacío:** 32.244 de las 184.712 adjudicaciones de 2025 no traen estado (las demás son `active`).
3. **Adjudicaciones con fecha de 2026:** 4.376 adjudicaciones del archivo de 2025 tienen fecha de adjudicación posterior a 2025.

**Hipótesis (inferencia, sin fuente oficial que la respalde):** el informe de SERCOP es nacional y provisional y podría incluir compras de empresas públicas, GAD, régimen especial o emergencia que no aparecen en la descarga masiva ordinaria. No se verificó.

---

## 7. Qué NO se verificó (límites explícitos de la auditoría)

Para mantener la honestidad técnica exigida en el proyecto, se declaran expresamente los aspectos que quedaron fuera del alcance de este perfilado:

1. **Tablas de planificación y extensiones:** No se auditaron las líneas de detalle presupuestario de `planning_AAAA.csv` ni los prefijos de `extensions_AAAA.csv` más allá de registrar su tamaño físico y hash de integridad.
2. **Identidad de personas naturales en proveedores:** Por razones de estricta protección de datos personales y privacidad, no se perfilaron identificaciones ni nombres de personas naturales adjudicatarias en `suppliers_AAAA.csv`.
3. **Cotejo en línea contra la API de SERCOP:** No se realizaron consultas individuales por `ocid` contra el endpoint `record` de la API de SERCOP para verificar si algún proceso ha sufrido modificaciones posteriores al 21/11/2026.
4. **Ejecución financiera de contratos:** La etapa de pagos y desembolsos reales no se publica en el estándar OCDS de SERCOP; por lo tanto, no se verificó si los contratos formalizados en `contracts_AAAA.csv` se liquidaron financieramente.
5. **Cálculo de ahorro oficial:** No se pudo replicar con exactitud la fórmula con la que el SERCOP estima su "ahorro nacional" (USD 461,4 millones en 2025 según su informe, p. 13), dado que dicho cálculo excluye ferias inclusivas y ciertos procedimientos cuyos criterios de exclusión no están detallados en los metadatos abiertos.
6. **Anomalías del JSON crudo:** la Ruta A usa los CSV del portal, por lo que no se midieron `contracts` como objeto ni paquetes con `releases` vacío (anomalías conocidas del JSON de 2024).
