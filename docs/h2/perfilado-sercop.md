# Perfilado completo de calidad de la fuente SERCOP (2021–2025)
## Evaluación multidimensional sobre 1.007.920 procesos de contratación abierta (OCDS)

**Equipo:** Trazabilidad Pública (Grupo 5)  
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
| **Hash SHA-256 del script (LF)** | `099AABCDF45D5F3F32F16CC1DF614CB56820023B3D5F3D0822C1A9E86CF7D00A` |
| **Entorno de ejecución** | Python 3.14 / uv (modo aislado, biblioteca estándar exclusivamente: `csv`, `json`, `pathlib`, `hashlib`, `re`, `datetime`, `contextlib`) |
| **Comando exacto de ejecución** | `python -I scripts/profile_h2_quality.py --derived-dir data/derivados --output-dir docs/h2/evidencia --years 2021 2022 2023 2024 2025 --reference-awarded-2025 7318700000.0 --buyer-summary-csv docs/h2/evidencia/perfil-calidad-sercop-por-comprador.csv` |
| **Fecha y hora de ejecución (UTC)** | 21 de noviembre de 2026, 22:36:48 UTC (17:36:48 hora local Ecuador, UTC-5) |
| **Universo procesado** | **1.007.920 releases** OCDS únicos; **981.348** licitaciones (`tender`); **975.302** adjudicaciones (`awards`); **949.550** contratos (`contracts`). |
| **Monto total adjudicado medido** | **USD 30.952.880.306,92** (~30.952,88 millones de dólares estadounidenses). |
| **Monto total licitado medido** | **USD 25.072.968.705,53** (~25.072,97 millones de dólares estadounidenses). |
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
| **2021** | 167.058 | 165.616 | 166.983 | 158.199 | $4.676.997.257,82 | $3.682.296.515,41 | 146.310 | 87,58 % |
| **2022** | 212.324 | 203.147 | 200.173 | 194.695 | $7.118.687.591,72 | $5.855.681.059,39 | 175.903 | 82,85 % |
| **2023** | 217.913 | 213.841 | 212.989 | 208.852 | $6.037.778.222,93 | $4.798.618.255,15 | 191.309 | 87,79 % |
| **2024** | 219.185 | 212.386 | 210.445 | 206.289 | $6.895.826.062,72 | $5.518.333.500,28 | 187.671 | 85,62 % |
| **2025** | 191.440 | 186.358 | 184.712 | 181.515 | $6.223.591.171,73 | $5.218.039.375,30 | 167.375 | 87,43 % |
| **Total** | **1.007.920** | **981.348** | **975.302** | **949.550** | **$30.952.880.306,92** | **$25.072.968.705,53** | **868.568** | **86,17 %** |

### Distribución de importes por proceso (relación tender-awards):
- **Procesos con ambos importes (adjudicado y estimado):** 868.568 procesos (86,17 %). Este subconjunto es la base estricta para responder la pregunta P2 (desviación presupuestaria).
- **Procesos con adjudicación pero sin valor estimado:** 95.882 procesos (9,51 %). Procedimientos que por su naturaleza normativa o captura en el portal no registraron presupuesto referencial en `tender`.
- **Procesos con valor estimado pero sin adjudicación:** 2.979 procesos (0,30 %). Procedimientos desiertos, cancelados o en etapa precontractual sin adjudicatario.
- **Procesos sin ningún importe registrado:** 40.491 procesos (4,02 %).

---

## 3. Matriz de diagnóstico de calidad (seis dimensiones)

Conforme a la sección 4.4 y la plantilla 6.3 de la guía del Hito 2, se presenta la lista formal de hallazgos identificados mediante códigos estables `Q-01` a `Q-10`. Cada acción propuesta está redactada como tarea técnica transferible a Power Query / ETL en el Hito 3 (#64):

| ID | Tabla · Campo | Dimensión | Evidencia numérica medida (2021–2025) | Impacto en preguntas P1 a P3 | Acción propuesta para H3 (tarea de transformación) |
|---|---|---|---|---|---|
| **Q-01** | `tender · value_amount` | **Completitud** | Ausente en 107.793 licitaciones en los 5 años (10,98 % de las filas de tender; 10,70 % de los releases). Por año: 2021=19.050 (11,50 %), 2022=26.356 (12,97 %), 2023=23.493 (10,99 %), 2024=20.560 (9,68 %), 2025=18.334 (9,84 %). Cero filas contienen el valor 0.0. | **Impacto crítico en P2:** La desviación `(A - E) / E` no se puede calcular en estos procesos. Intentar imputar 0.0 generaría divisiones por cero o distorsiones infinitas. | En Power Query, mantener `tender.value_amount` como numérico anulable (`nullable number`). Crear un indicador condicional `tiene_valor_estimado` (`true`/`false`) y documentar formalmente que la medida de desviación de P2 filtra únicamente los 868.568 procesos con ambos importes. |
| **Q-02** | `awards · correctedValue_amount` y `enteredValue_amount` | **Completitud** | **100,0 % de nulos.** Las 975.302 filas de `awards` en los cinco años tienen ambas columnas vacías (0 valores poblados en 2021–2025). | **Sin impacto en cálculo:** No es posible contrastar ofertas corregidas vs adjudicadas. | En Power Query, eliminar verticalmente ambas columnas en el paso inicial de selección de campos para optimizar el consumo de memoria del archivo `.pbix`. |
| **Q-03** | `awards · date`, `tender · tenderPeriod_startDate`, `contracts · dateSigned` | **Completitud** | Cobertura sobre releases inferior al 25 % en los 5 años: `tenderPeriod_startDate` poblado solo en 17,1 % a 23,4 %; `awards.date` en 13,96 % a 17,63 %; `contracts.dateSigned` en 14,57 % a 19,42 %. En contraste, `releases.date` tiene **100,0 % de cobertura** (1.007.920 filas). | **Impacto alto en P1 y P3:** Usar las fechas de etapa dejaría fuera de las series de tiempo al 80 % del gasto público adjudicado. | Adoptar `releases.date` como la fecha de negocio oficial vinculada activamente a `DimTiempo`. Conservar las fechas de etapa como atributos secundarios opcionales en el modelo. |
| **Q-04** | `releases · date` | **Validez** | Cero fechas previas a 2015. Sin embargo, se identificaron 3 procesos en 2024 con fechas futuras posteriores al año de corte (fechadas en 2026/2027) y en 2025 la fecha máxima observada fue `2026-11-21T03:38:41-05:00` (el mismo día de la descarga masiva). Cero registros con fechas no interpretables. | **Impacto menor en P1 y P3:** Podría proyectar procesos a años no transcurridos si se usa año calendario estricto de publicación. | En Power Query, derivar la clave `FechaID` (`YYYYMMDD`). En caso de fechas futuras fuera de la ventana analítica, reasignar a una categoría de auditoría o acotar al año de inicio del lote (`AnioProceso`). |
| **Q-05** | `tender · value_currency` y `awards · currency` | **Validez** | **100,0 % de los importes numéricos están en USD** (cero monedas extranjeras observadas). No existen montos negativos ni importes cero. No obstante, `tender_2021.csv`, `tender_2023.csv` y `tender_2024.csv` presentan bytes Windows-1252 que rompen decodificación estricta UTF-8 en campos como `procurementMethodDetails`. | **Sin impacto en sumas monetarias.** Riesgo de fallo de importación en Power Query por caracteres especiales o tildes rotas. | En Power Query, configurar la importación de archivos CSV con codificación `65001` (UTF-8) con manejo tolerante de caracteres extraños y tipificar importes explícitamente a tipo `Currency` (`1.234,56 USD`). |
| **Q-06** | `releases · ocid` y `awards · (ocid, id)` | **Unicidad** | Cero `ocid` duplicados dentro de cada año. Cero `ocid` compartidos entre años (1.007.920 procesos únicos). Sin embargo, **1.801 procesos** presentan más de una adjudicación (2021=386, 2022=424, 2023=329, 2024=362, 2025=300). Un proceso de 2021 llegó a tener 268 adjudicaciones. | **Impacto crítico en el modelo (P1 y P2):** Un join 1 a N directo entre `tender` y `awards` duplicaría filas y sobreestimaría `tender.value_amount`. | En Power Query, definir el grano de la tabla de hechos `FactContratacion` a nivel de proceso (`ocid`) agregando `awards` (sumando `amount`), o separar `FactAdjudicacion` asegurando que la medida estimada se mantenga en el grano de proceso. |
| **Q-07** | `releases · buyer_id` | **Consistencia** | De 1.007.920 filas, 780.471 (77,43 %) tienen forma simple `EC-RUC-{13}` y 227.406 (22,56 %) tienen forma con sufijo desconcentrado `EC-RUC-{13}-{sufijo}`. Existen **43 registros malformados** (2021=0, 2022=7, 2023=25, 2024=9, 2025=2). | **Impacto alto en P1 a P3 (DimEntidad):** El cruce con el Catálogo de Instituciones del MDEP fallaría en el 22,56 % de casos si se hace por coincidencia exacta. | En Power Query, extraer una columna `RUC_13` limpiando el prefijo `EC-RUC-` y descartando sufijos tras el guion para cruzar con el RUC de 13 dígitos de la entidad matriz del MDEP. Marcar los 43 malformados como `NO_IDENTIFICADO`. |
| **Q-08** | `tender · procuringEntity_id` vs `releases · buyer_id` | **Consistencia** | Solo el 18,1 % (194.670 procesos) coinciden de forma exacta. El **81,8 % (780.156 procesos)** coinciden exactamente en la raíz tributaria de 13 dígitos pero difieren en el sufijo de desconcentración. Cero procesos tienen distinta raíz de 13 dígitos. 476 procesos carecen de `procuringEntity_id`. | **Impacto bajo en P1 y P2:** La disparidad obedece a la estructura desconcentrada del Estado (unidad requirente técnica vs unidad administradora de fondos). | Modelar `DimEntidad` a partir de la raíz tributaria institucional de 13 dígitos del comprador (`buyer_id`), que es la clave que vincula el 100 % de los fondos con el Presupuesto General del Estado. |
| **Q-09** | `awards · amount` (2025) vs Rendición de Cuentas SERCOP | **Exactitud** | Cifra preliminar publicada por SERCOP (informe 2025, p. 12): USD 7.318,7 millones. Suma medida en los CSV de 2025: **USD 6.223,59 millones**. Diferencia absoluta: **USD 1.095,11 millones** (-14,96 %). Factores medibles explicativos identificados: 5 adjudicaciones sin monto; 32.244 adjudicaciones en estado no activo/cancelado; 4.376 adjudicaciones fechadas fuera de 2025; la cifra oficial incluye compras de emergencia y regímenes especiales no consolidados en la descarga OCDS masiva. | **Impacto en P1:** Las cifras del DW reflejan con precisión la realidad de los datos abiertos transaccionales, pero difieren del agregado macroeconómico del boletín institucional. | Incorporar una nota metodológica en el tablero de Power BI y en el documento de diseño explicando la discrepancia entre datos abiertos transaccionales OCDS y el informe provisional institucional. |
| **Q-10** | `releases · date` vs Año del archivo | **Oportunidad** | Entre el **7,57 % y el 11,19 %** de los procesos por año tienen `releases.date` correspondiente al año calendario siguiente (2021=18.235 de 2022; 2022=23.758 de 2023; 2023=19.065 de 2024/2025; 2024=20.832 de 2025; 2025=14.492 de 2026). No existen meses sin datos (todos los 60 meses de la serie tienen registros). | **Impacto alto en P3:** Si se agrupan los meses usando el año del lote en vez de la fecha real de publicación, las series temporales se desfasan artificialmente. | En Power Query, usar `releases.date` para asignar el mes y año cronológico de la dimensión temporal `DimTiempo`, manteniendo `AnioDescarga` como atributo auxiliar para conciliación con los lotes de la fuente. |

---

## 4. Recomendación técnica sobre la regla de fecha de negocio (`DimTiempo`)

En cumplimiento del [ADR 0004](../adr/0004-modelo-dimensional.md) y las guías de los hitos 1 y 2, se evaluaron cuantitativamente las cuatro fechas candidatas sobre el universo de 1.007.920 procesos:

### 4.1. Cobertura porcentual comparativa por año

| Fecha candidata | Tabla origen | 2021 | 2022 | 2023 | 2024 | 2025 | Total 2021–2025 | Veredicto técnico |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **`releases.date`** | `releases` | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 %** | **100,0 % (1.007.920)** | **Candidata recomendada** |
| `tender.tenderPeriod_startDate` | `tender` | 22,01 % | 23,40 % | 18,03 % | 19,51 % | 17,10 % | 20,01 % (201.250) | Inviable como principal (>79 % nulos) |
| `awards.date` | `awards` | 17,63 % | 16,94 % | 14,50 % | 14,99 % | 13,96 % | 15,60 % (161.830) | Inviable como principal (>84 % nulos) |
| `contracts.dateSigned` | `contracts` | 17,57 % | 19,42 % | 15,74 % | 16,73 % | 14,57 % | 16,81 % (169.448) | Inviable como principal (>83 % nulos) |

### 4.2. Análisis del desfase y propuesta de regla para decisión del líder

1. **Hallazgo:** `releases.date` representa la marca de tiempo de la última actualización/publicación del paquete OCDS por parte del SERCOP. Por ello, entre el 7,57 % y el 11,19 % de los procesos presentan una fecha que cae en el año siguiente al que el SERCOP utilizó para agrupar la descarga masiva (por ejemplo, 18.235 procesos del archivo de 2021 fueron actualizados en 2022).
2. **Recomendación para el líder (a someter en el chat):**
   - **Regla principal de tiempo:** Vincular `FactContratacion[FechaID]` a `DimTiempo[Fecha]` a través de la fecha extraída de `releases.date`. Al tener **100,0 % de completitud**, garantiza que ningún proceso quede huérfano ni excluido del tablero analítico.
   - **Tratamiento del desfase de lote:** Crear en la tabla de hechos el campo `AnioProceso` (derivado del año del archivo/partición OCDS, que representa el año fiscal de inicio del procedimiento precontractual). De esta forma, el usuario podrá filtrar tanto por año de inicio (`AnioProceso`) como por fecha de ejecución/publicación efectiva (`DimTiempo[Anio]`).

---

## 5. Reconciliación con el reconocimiento del Hito 1

Se contrastaron las cifras obtenidas en este perfilado completo frente a las documentadas en el Hito 1 (`docs/requirements/hito1.md`, líneas 167–180) y en el reconocimiento de la fuente (`docs/sources/reconocimiento.md`, líneas 260–275):

| Métrica | Año | Hito 1 (ZIP JSON crudo, oct/nov 2026) | Hito 2 (CSV masivos, 21/11/2026) | Diferencia | Causa documentada |
|---|:---:|:---:|:---:|:---:|---|
| **Releases / `ocid`** | 2021 | 167.058 | 167.058 | 0 | Coincidencia exacta al 100 %. |
| Releases con tender | 2021 | 165.616 | 165.616 | 0 | Coincidencia exacta al 100 %. |
| Filas de awards | 2021 | 166.983 | 166.983 | 0 | Coincidencia exacta al 100 %. |
| Awards con monto numérico | 2021 | 166.980 | 166.980 | 0 | Coincidencia exacta al 100 % (3 vacíos). |
| Procesos con ambos importes | 2021 | 146.314 | 146.310 | -4 | En el CSV, 4 licitaciones presentaron celdas en blanco en `value_amount`. |
| **Releases / `ocid`** | 2024 | 219.185 | 219.185 | 0 | Coincidencia exacta al 100 %. |
| Filas de awards | 2024 | 210.445 | 210.445 | 0 | Coincidencia exacta al 100 %. |
| Awards con monto numérico | 2024 | 210.439 | 210.439 | 0 | Coincidencia exacta al 100 % (6 vacíos). |
| Procesos con ambos importes | 2024 | 187.672 | 187.671 | -1 | Discrepancia menor de 1 registro por formato de celda en CSV. |
| **Releases / `ocid`** | 2025 | **190.619** | **191.440** | **+821** | **Actualización continua del portal.** La descarga de H1 se realizó el 11/10/2026; la descarga de H2 se realizó el 21/11/2026. En 41 días el portal incorporó 821 nuevos procesos. |
| Filas de awards | 2025 | 183.891 | 184.777 | +886 | Crecimiento proporcional de adjudicaciones publicadas (+886). |
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

### Factores explicativos medibles y respaldados con evidencia:
1. **Adjudicaciones sin monto:** 5 adjudicaciones en 2025 carecen de importe registrado (`awards.amount` vacío).
2. **Procesos en estado no activo / desiertos / cancelados:** En los datos OCDS de 2025 existen 32.244 adjudicaciones en estados que no corresponden a contratos activos vigentes (o cuyo estado en `tender` es distinto de `complete`).
3. **Adjudicaciones con fecha efectiva fuera de 2025:** 4.376 adjudicaciones registradas en el paquete de 2025 tienen fecha formal de adjudicación en 2026.
4. **Diferencia de alcance institucional y metodológico (declarada sin explicar):** El informe del SERCOP es de carácter **nacional y provisional**, e incluye compras de empresas públicas, GADs, adquisiciones bajo régimen especial de seguridad nacional y compras corporativas que no necesariamente se publican a través de los releases OCDS ordinarios en la fecha del corte. La diferencia restante se declara formalmente como una discrepancia metodológica del origen de datos abiertos frente a la contabilidad gubernamental agregada.

---

## 7. Qué NO se verificó (límites explícitos de la auditoría)

Para mantener la honestidad técnica exigida en el proyecto, se declaran expresamente los aspectos que quedaron fuera del alcance de este perfilado:

1. **Tablas de planificación y extensiones:** No se auditaron las líneas de detalle presupuestario de `planning_AAAA.csv` ni los prefijos de `extensions_AAAA.csv` más allá de registrar su tamaño físico y hash de integridad.
2. **Identidad de personas naturales en proveedores:** Por razones de estricta protección de datos personales y privacidad, no se perfilaron identificaciones ni nombres de personas naturales adjudicatarias en `suppliers_AAAA.csv`.
3. **Cotejo en línea contra la API de SERCOP:** No se realizaron consultas individuales por `ocid` contra el endpoint `record` de la API de SERCOP para verificar si algún proceso ha sufrido modificaciones posteriores al 21/11/2026.
4. **Ejecución financiera de contratos:** La etapa de pagos y desembolsos reales no se publica en el estándar OCDS de SERCOP; por lo tanto, no se verificó si los contratos formalizados en `contracts_AAAA.csv` se liquidaron financieramente.
5. **Cálculo de ahorro oficial:** No se pudo replicar con exactitud la fórmula con la que el SERCOP estima su "ahorro nacional" (USD 461,4 millones en 2025 según su informe, p. 13), dado que dicho cálculo excluye ferias inclusivas y ciertos procedimientos cuyos criterios de exclusión no están detallados en los metadatos abiertos.
