# Decisión de arquitectura: Formato de conexión de SERCOP a Power BI (H2-02)

- **Documento:** Evaluación técnica y propuesta de decisión (Issue #60 / H2-02)
- **Fecha:** 21 de noviembre de 2026
- **Estado:** Aprobada la Ruta A por el líder en el chat el 21/11/2026 (tras la prueba en Power BI Desktop de la sección 8)
- **Autoría:** Grupo 5 (primer borrador con asistencia de Gemini 3.8 Flash; correcciones, descargas de 2021 a 2024 y ampliación del análisis con Claude Sonnet 5.5; la prueba en Power BI Desktop la hizo el líder)
- **Referencias:** Guía Hito 2 (secciones 3.1, 5, 8); [ADR 0005](../adr/0005-hitos-2-y-3-power-bi.md); `docs/h2/adquisicion.md`; `docs/sources/reconocimiento.md`; `docs/sources/sercop-2025-portal-csv-summary.json`

---

## 1. Resumen ejecutivo y recomendación firme

Se evaluó la descarga anual 2025 en formato CSV ofrecida por el portal oficial de datos abiertos del SERCOP frente al archivo anual JSON (1,72 GB sin comprimir) y al extractor intermedio de #66.

### Hallazgo principal
El recurso `download?type=csv` del portal **no es un archivo plano único**, sino un archivo comprimido ZIP de **35,09 MB** (`releases_2025.zip`, ~285 MB descomprimido) que empaqueta **8 tablas CSV relacionales normalizadas** según los bloques estructurales de OCDS:
1. `releases_2025.csv` (grano: proceso / `ocid`, 191.440 filas)
2. `tender_2025.csv` (grano: licitación / `ocid`, 186.358 filas)
3. `awards_2025.csv` (grano: adjudicación individual, 184.712 filas)
4. `suppliers_2025.csv` (proveedores por adjudicación, 184.709 filas)
5. `contracts_2025.csv` (contratos, 181.515 filas)
6. `planning_2025.csv` (presupuesto y planificación, 37.821 filas)
7. `extensions_2025.csv` (extensiones declaradas, 7 filas)
8. `metadata_2025.csv` (metadatos del paquete OCDS, 1 fila)

### Recomendación firme: Ruta A (CSV del portal)
Se recomienda adoptar la **Ruta A (CSV del portal)** por las siguientes razones:
1. **Cumple la regla de decisión del issue:** los campos necesarios para las preguntas P1, P2 y P3 (`ocid`, `buyer_id`, `buyer_name`, `date`, `procurementMethod`, `procurementMethodDetails`, `value_amount`, `amount`) están **completos y disponibles** en `releases_2025.csv`, `tender_2025.csv` y `awards_2025.csv`.
2. **Grano nativo perfecto:** `releases_2025.csv` tiene **exactamente una fila por `ocid`** (191.440 filas = 191.440 procesos).
3. **Multiplicidad de adjudicaciones preservada:** `awards_2025.csv` conserva los 300 procesos con adjudicaciones múltiples de forma idéntica a la estructura del JSON, permitiendo agrupar y sumar `amount` por `ocid` para el hecho a grano de proceso.
4. **Cumplimiento estricto de la guía del profesor:** la guía H2 (sección 3.1 y 8) establece taxativamente: *«Prefiere archivos CSV o Excel descargables»* y exige que las consultas de Power BI *«solo tengan pasos de conexión; la limpieza queda para el Hito 3»*. Conectar a CSV nativos del portal mediante el conector `Texto/CSV` o `Carpeta` evita requerir scripts de extracción intermedios en la capa cruda.
5. **Privacidad garantizada:** el CSV del portal no incluye datos de contacto personales (`parties[].contactPoint`), cumpliendo de fábrica la restricción del proyecto.

### Plan de respaldo: Ruta B
La prueba del líder en Power BI Desktop (sección 8) no mostró lentitud ni bloqueos al perfilar `tender_2025.csv` (118,9 MB) sobre «todo el conjunto de datos». Si más adelante apareciera un problema de rendimiento con los años 2021 a 2024, se pasa a la **Ruta B (JSON + extractor del issue #66)**. Ese extractor (`scripts/flatten_sercop_ocds.py`) está en desarrollo y todavía no existe en el repositorio. La Ruta C (JSON directo en Power Query) no se probó: el issue #60 la considera improbable y, con la Ruta A, no hace falta.

---

## 2. Evidencia de la descarga de SERCOP 2025 (formato CSV)

La descarga se realizó el 21 de noviembre de 2026 mediante el script del repositorio `scripts/download_sercop_ocds.ps1`, previa aprobación explícita del líder:

| Parámetro | Valor registrado | Fuente / Verificación |
|---|---|---|
| **Enlace solicitado** | `https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=csv&year=2025&month=0&method=all` | Patrón oficial del portal (todos los meses y tipos) |
| **Estado HTTP** | `200 OK` | Cabecera HTTP de respuesta |
| **Content-Type** | `application/zip` | Cabecera HTTP de respuesta |
| **Content-Disposition** | `attachment; filename=releases_2025.zip` | Nombre asignado por el servidor upstream |
| **Tamaño anunciado** | 35.097.532 bytes | Cabecera `Content-Length` |
| **Bytes recibidos** | 35.097.532 bytes (~35,1 MB) | Coincidencia exacta con `Content-Length` |
| **Hash SHA-256 (ZIP)** | `66FFF557785F9C9592E68B0B9A9D22609C1BE880586E0DEA534617B302F83B0A` | Cálculo SHA-256 en modo streaming (.NET) |
| **Fecha y hora local (Ecuador UTC-5)** | 21/11/2026 14:17:48 (inicio) a 14:17:55 (fin) | Duración: 6,8 segundos de transferencia |
| **Ubicación cruda (solo lectura)** | `data/datos_crudos/sercop-ocds-csv-2025-20261121-141748/releases_2025.zip` | Carpeta local ignorada en Git |
| **Ubicación derivada (extraída)** | `data/derivados/sercop-portal-csv-2025-20261121-141748/` | Extracción sin alterar el ZIP crudo |
| **Fila de procedencia** | `docs/h2/evidencia/descargas-sercop.csv`, fila 7 | Registrada automáticamente por el script |
| **Licencia** | `https://creativecommons.org/licenses/by/3.0/ec/` (CC BY 3.0 Ecuador) | Declarada en metadatos OCDS |

### 2.1. Descargas de 2021 a 2024 (CSV)

Con el visto bueno del líder en el chat (21/11/2026) se descargaron los CSV anuales de 2021 a 2024 con el mismo script y el mismo patrón de enlace (`type=csv`). Cada ZIP crudo está en `data/datos_crudos/sercop-ocds-csv-AAAA-*/`, marcado como de solo lectura, y se extrajo a `data/derivados/sercop-portal-csv-AAAA-*/`. Todos traen las mismas 8 tablas que 2025.

| Año | Bytes recibidos | Content-Length | Hash SHA-256 del ZIP | Hora local de inicio |
|:---:|---:|---:|---|:---:|
| 2021 | 28.761.104 | 28.761.104 | `60A843EFC8CDD78230A3D7C83CC2539AEE2C7E97EC59098EB9D939CADD4A2B61` | 14:57:29 |
| 2022 | 41.920.182 | 41.920.182 | `1229CD3C9BE1BC8C7CF80173939A550FF4E4CDB9631F4BD12633ED6033DA4802` | 14:57:42 |
| 2023 | 37.679.239 | 37.679.239 | `2C334812E8BC99A609125B48149A2B8CA7264271B56440FDD1768D6E31893C02` | 14:58:20 |
| 2024 | 41.439.857 | 41.439.857 | `B14D3AFFD0C40AB8D5B66FA5B9367D6B10B9BAA7C5D314019A40211E2B8114B5` | 15:08:56 |

**Intentos fallidos (se conservan como evidencia, no se borran):**
- **2023, primer intento** (`sercop-ocds-csv-2023-20261121-145750`): la conexión se cortó y se recibieron 27.190.096 de 37.679.239 bytes. El script no reintenta; quedó su fila en `descargas-sercop.csv` (con el hash vacío) y se repitió la descarga en una carpeta nueva.
- **2024, primer intento** (`sercop-ocds-csv-2024-20261121-145834`): el proceso quedó detenido en 9.231.566 bytes durante más de 10 minutos y se terminó a mano. Como el script solo escribe la fila de procedencia al terminar, **este intento no tiene fila** en `descargas-sercop.csv`; su carpeta parcial sigue en `data/datos_crudos/`. Se repitió en una carpeta nueva.
- En ambos casos la causa del corte no se determinó (igual que el corte de 2025 descrito en `docs/h2/adquisicion.md`).

**Integridad y conteo:** los cuatro ZIP válidos pasaron la prueba de integridad de Python (`zipfile.testzip`, sin errores) y contienen 8 archivos cada uno. Las filas de `releases_AAAA.csv` coinciden con la columna «Releases» del JSON de cada año en `docs/h2/adquisicion.md` (sección 3): 167.058 (2021), 212.324 (2022), 217.913 (2023) y 219.185 (2024). En 2023 y 2024 el JSON tiene un paquete más que releases (217.914 y 219.186 paquetes), por eso la comparación se hace con releases.

---

## 3. Estructura de las tablas CSV inspeccionadas

El ZIP fue descomprimido hacia una carpeta derivada sin alterar el archivo original. Las 8 tablas resultantes fueron inspeccionadas mediante el script `scripts/inspect_csv_header.py` (biblioteca estándar de Python, sin dependencias externas; la versión de Python y el SHA-256 del script quedan registrados en cada resumen, `docs/sources/sercop-AAAA-portal-csv-summary.json`). El resumen solo contiene tamaños, hashes, columnas, número de registros y número de campos con salto de línea; las demás cifras de este documento (valores distintos, campos con dato, distribución de adjudicaciones) salieron de un recuento aparte con el módulo `csv` de Python, que no está versionado (ver sección 9):

| Archivo CSV | Tamaño (bytes) | Filas de datos | Columnas | Codificación | Delimitador | Comillas | SHA-256 del archivo |
|---|---:|---:|:---:|:---:|:---:|:---:|---|
| `releases_2025.csv` | 48.256.694 | 191.440 | 8 | UTF-8 | `,` (coma) | `"` | `99B1A2674FEC9E15D5CD755783EEE5D62D143AC14C0D49FD6F1ED535D7962224` |
| `tender_2025.csv` | 118.964.510 | 186.358 | 29 | UTF-8 | `,` (coma) | `"` | `60FA69FE7CC75299F8444BDD1D9F1323BFA1AF3FAEE18804498EC9B16B2AE32A` |
| `awards_2025.csv` | 36.871.647 | 184.712 | 17 | UTF-8 | `,` (coma) | `"` | `4D46D444128E381B454135C968E68B42D9A843AC26D8AF033CF0C506A5FFDC1C` |
| `suppliers_2025.csv` | 34.208.845 | 184.709 | 5 | UTF-8 | `,` (coma) | `"` | `D7986EC51131D00033605F0CEBF464C0F11E615E1C6522994AEBEEFDB35935D0` |
| `contracts_2025.csv` | 35.517.722 | 181.515 | 14 | UTF-8 | `,` (coma) | `"` | `26B0B30B9F11242006919365D0B93D939350847567B6D3BC76702D9E4A3AC697` |
| `planning_2025.csv` | 10.845.742 | 37.821 | 7 | UTF-8 | `,` (coma) | `"` | `2F5BC6125F95BF50A34432E33F396E03BB5FDBA5EA02B1B8E55C718CDE6C27B0` |
| `extensions_2025.csv` | 757 | 7 | 1 | UTF-8 | `,` (coma) | `"` | `9AE0A9EB81D484976FD4F5D8625DDAEF368D74301CF0C7D58B659C2D8E1CA57B` |
| `metadata_2025.csv` | 491 | 1 | 9 | UTF-8 | `,` (coma) | `"` | `AEB58510DE5155BE5409A0B547B0C1C92C62FA89EA77511FDB7AA1223E1394A0` |

**Total de datos descomprimidos:** 284.666.408 bytes (~285 MB frente a los 1,72 GB del JSON descomprimido).
**Conformidad técnica:** todos los archivos son UTF-8 estándar sin BOM, utilizan coma como delimitador y comillas dobles para campos de texto con caracteres especiales o saltos de línea.

---

## 4. Matriz de comparación: Campos de P1 a P3 (JSON vs CSV del portal)

Se contrastaron los campos requeridos para responder las preguntas de negocio P1, P2 y P3 (Hito 1, Parte 2) entre el esquema JSON OCDS y las columnas observadas en las tablas CSV:

| Campo de negocio | Ruta en JSON OCDS | Tabla y columna en CSV | Estado | Grano en CSV | Filas con dato en CSV | % sobre releases | Evidencia medible |
|---|---|---|:---:|---|---:|---:|---|
| **Identificador de proceso** | `ocid` | `releases_2025.csv` → `ocid` | **ESTÁ** | 1 por proceso | 191.440 | 100,0 % | 191.440 valores distintos de `ocid`, 0 nulos |
| **Identificador de entidad** | `buyer.id` | `releases_2025.csv` → `buyer_id` | **ESTÁ** | 1 por proceso | 191.440 | 100,0 % | Formato `EC-RUC-{13}` idéntico al JSON |
| **Nombre de entidad** | `buyer.name` | `releases_2025.csv` → `buyer_name` | **ESTÁ** | 1 por proceso | 191.440 | 100,0 % | Razón social oficial de la entidad |
| **Método general de contratación** | `tender.procurementMethod` | `tender_2025.csv` → `procurementMethod` | **ESTÁ** | 1 por licitación | 186.358 | 97,35 % | 4 valores (`selective`, `direct`, `open`, `limited`) |
| **Detalle del método** | `tender.procurementMethodDetails` | `tender_2025.csv` → `procurementMethodDetails` | **ESTÁ** | 1 por licitación | 186.357 | 97,35 % | Solo 1 licitación con valor vacío en la tabla tender |
| **Importe estimado (E)** | `tender.value.amount` | `tender_2025.csv` → `value_amount` | **ESTÁ** | 1 por licitación | 168.024 | 87,77 % | Numérico; licitaciones sin monto estimado: 18.334 |
| **Importe adjudicado (A)** | `awards[].value.amount` | `awards_2025.csv` → `amount` | **ESTÁ** | 1 por adjudicación | 184.707 | 96,48 % | Numérico; solo 5 adjudicaciones carecen de monto |
| **Fecha de release (candidata)** | `date` | `releases_2025.csv` → `date` | **ESTÁ** | 1 por proceso | 191.440 | 100,0 % | 100 % completa; formato ISO-8601 UTC |
| **Fecha de adjudicación (candidata)** | `awards[].date` | `awards_2025.csv` → `date` | **ESTÁ** | 1 por adjudicación | 28.010 | 14,63 % | Coincide con la baja presencia medida en el JSON |
| **Fecha de inicio de licitación** | `tender.tenderPeriod.startDate` | `tender_2025.csv` → `tenderPeriod_startDate` | **ESTÁ** | 1 por licitación | 32.739 | 17,10 % | Coincide con la baja presencia medida en el JSON |

**Conclusión de campos:** ningún campo necesario para responder las preguntas P1 a P3 se pierde. Todos están presentes con los mismos valores, tipos y niveles de completitud que en el JSON original.

---

## 5. Análisis de grano, volumen y multiplicidad de adjudicaciones

### 5.1. ¿Hay una fila por `ocid`?
- **En `releases_2025.csv`:** **SÍ, exactamente una fila por `ocid`**. Hay 191.440 filas y 191.440 valores distintos de `ocid` (0 duplicados, 0 vacíos). Es la tabla dimensional base del proceso.
- **En `tender_2025.csv`:** **SÍ, exactamente una fila por `ocid`** (186.358 filas = 186.358 `ocid` distintos). Los 5.082 procesos restantes no publicaron bloque `tender` (procedimientos directos o especiales).
- **En `awards_2025.csv`:** **NO hay una fila por `ocid`**, porque su grano es de adjudicación individual (`awards[]`). Hay 184.712 filas correspondientes a 183.098 procesos distintos.

### 5.2. Reconciliación del volumen total (191.440 procesos)
- El contador en vivo del portal al 21/11/2026 reportó **191.440 procedimientos publicados** para el año 2025.
- La descarga JSON del 21/11/2026 contiene **191.440 paquetes**.
- La tabla `releases_2025.csv` contiene **191.440 filas de datos**.
- *Nota sobre la cifra de H1:* el informe de H1 (11/10/2026) reportó 190.619 procesos. La diferencia (+821 procedimientos) se debe a que el portal actualiza sus bases diariamente y acumula los procesos registrados entre octubre y noviembre de 2026. La reconciliación entre JSON y CSV en la fecha de corte actual es del **100,00 %**.

### 5.3. Multiplicidad de adjudicaciones (300 procesos multi-adjudicación)
En `awards_2025.csv`, hay 183.098 procesos con al menos una adjudicación. De ellos:
- **182.798 procesos** tienen exactamente 1 adjudicación (1 fila).
- **Exactamente 300 procesos** tienen más de una adjudicación (1.914 filas en total).

La distribución observada en `awards_2025.csv` es **matemáticamente idéntica** a la distribución obtenida con `inspect_sercop_zip.py` en el JSON:
- 2 adjudicaciones: 143 procesos
- 3 adjudicaciones: 52 procesos
- 4 adjudicaciones: 17 procesos
- 5 adjudicaciones: 18 procesos
- 6 adjudicaciones: 12 procesos
- 7 adjudicaciones: 6 procesos
- 8 adjudicaciones: 5 procesos
- 9 adjudicaciones: 6 procesos
- 10 adjudicaciones: 6 procesos
- 11 adjudicaciones: 7 procesos
- 12 adjudicaciones: 2 procesos
- 13 adjudicaciones: 1 proceso
- 14 adjudicaciones: 2 procesos
- 16 adjudicaciones: 2 procesos
- 17 adjudicaciones: 2 procesos
- 18 adjudicaciones: 2 procesos
- 19 adjudicaciones: 1 proceso
- 20 adjudicaciones: 1 proceso
- 22 adjudicaciones: 2 procesos
- 23 adjudicaciones: 1 proceso
- 24 adjudicaciones: 1 proceso
- 25 adjudicaciones: 3 procesos
- 27 adjudicaciones: 1 proceso
- 33 adjudicaciones: 1 proceso
- 44 adjudicaciones: 1 proceso
- 48 adjudicaciones: 1 proceso
- 64 adjudicaciones: 1 proceso
- 69 adjudicaciones: 1 proceso
- 79 adjudicaciones: 1 proceso
- 233 adjudicaciones: 1 proceso

**Tratamiento dimensional:**  
Para el modelo dimensional (ADR 0005, punto 3), cuyo hecho `FactContratacion` tiene grano de un proceso (`ocid`), el monto adjudicado se obtiene agrupando `awards_2025.csv` por `ocid` y sumando la columna `amount` (`SUM(amount)`). Esto garantiza que no se dupliquen filas del proceso y que el importe refleje el total contratado del procedimiento.

### 5.4. ¿Qué información se pierde en el CSV respecto al JSON?
1. **Datos de partes secundarias (`parties`):** el JSON contiene una lista `parties` con roles adicionales (`tenderer`, `payer`, `procuringEntity`) y datos de contacto (`contactPoint`: teléfono, correo). En el CSV, solo se preservan `buyer_id`/`buyer_name` en `releases`, `procuringEntity_id`/`name` en `tender`, y `id`/`name` de proveedores en `suppliers`. **Impacto:** Ninguno para P1–P3. Por el contrario, esto beneficia al proyecto porque evita filtrar datos personales de contacto en Power Query.
2. **Tablas omitidas en el CSV:** no se incluyen tablas para subastas electrónicas (`auctions`, 15.722 en JSON), ofertas de licitadores (`bids`, 2.763 en JSON), procesos relacionados (`relatedProcesses`, 152.797 en JSON) ni documentos adjuntos. **Impacto:** Ninguno. Ninguna de las tres preguntas de negocio requiere estas entidades.

### 5.5. Hallazgo: campos con salto de línea en `tender`

`tender_AAAA.csv` trae campos de texto con saltos de línea dentro de comillas. Un lector que respeta las comillas (como el módulo `csv` de Python) los trata como parte de un solo registro; uno que las ignora parte ese registro en varias filas. Conteo de campos con salto de línea (campo `fields_with_line_break` de los resúmenes `docs/sources/sercop-AAAA-portal-csv-summary.json`):

| Año | Registros de `tender` | Campos con salto de línea | `releases` | `awards` |
|:---:|---:|---:|---:|---:|
| 2021 | 165.616 | 380 | 0 | 0 |
| 2022 | 203.147 | 358 | 0 | 0 |
| 2023 | 213.841 | 61 | 0 | 0 |
| 2024 | 212.386 | 0 | 0 | 0 |
| 2025 | 186.358 | 1 | 0 | 0 |

**Observado en Power BI Desktop (2025):** `tender_2025` muestra 186.360 filas en el paso «Origen» (antes de promover encabezados), igual que las 186.360 líneas físicas del archivo (1 de encabezado, 186.358 registros y 1 línea extra por el salto de línea). Tras promover encabezados quedan 186.359 filas, una más que los 186.358 registros reales. Esto es coherente con una conexión que ignora las comillas (`QuoteStyle.None`, que es lo que genera por defecto el asistente de Texto/CSV según nuestra inferencia). **No se leyó el valor de `QuoteStyle` en la fórmula** (la captura la mostraba cortada), así que la causa exacta queda como inferencia hasta abrir esa fórmula completa.

**Consecuencia:** en 2021 serían hasta 380 filas de más. Como H2 diagnostica y no corrige, el hallazgo se documenta aquí y se registra en el libro de calidad; en las consultas del issue #63 el parámetro `QuoteStyle=QuoteStyle.Csv` es parte de la conexión (no una limpieza) y debe fijarse en `Licitaciones_SERCOP`.

---

## 6. Comparación de rutas y regla de decisión

| Dimensión | Ruta A: CSV del portal | Ruta B: JSON + extractor (#66) | Ruta C: JSON directo en Power Query |
|---|---|---|---|
| **Formato de origen** | Tablas CSV oficiales (`.zip`, 35 MB) | Archivos CSV planos ad hoc generados desde JSON | JSON crudo anual (1,72 GB por año) |
| **Cumplimiento de guía H2** | **Máximo:** conector `Texto/CSV`, sin código intermedio | Medio: requiere script transformador previo | Bajo: parseo complejo en M |
| **Carga en Power BI Desktop** | Ligera: lectura nativa de CSV en columnas | Ligera: solo columnas elegidas | Crítica: riesgo alto de congelamiento y desbordamiento de RAM |
| **Dependencia de software** | Ninguna: provisto directamente por SERCOP | Depende del extractor del issue #66 (aún no existe en el repositorio) | Ninguna |
| **Trazabilidad y procedencia** | Directa: URL oficial de SERCOP en inventario | Requiere documentar el script y el ZIP de origen | Directa |
| **Grano y fidelidad** | Grano nativo OCDS separado (proceso vs adjudicación) | Grano precalculado en Python | Jerárquico anidado |

### Regla de decisión formal
> **Si `releases_2025.csv` y `tender_2025.csv` se abren en Power BI Desktop en un tiempo razonable (< 60 segundos) y el perfilado sobre «todo el conjunto de datos» es manejable sin colapsar el equipo, se adopta de forma definitiva la RUTA A (CSV del portal).**  
> Si Power BI Desktop se congela o tarda excesivamente en perfilar `tender_2025.csv` (119 MB), se adopta la **RUTA B (JSON + extractor #66)** como respaldo probado.

---

## 7. Impacto en los siguientes issues (#62, #63 y #69)

### En el Issue #62 (Perfilado y diagnóstico de calidad en Power Query):
- El líder perfila en Power BI tres tablas limpias: `releases_2025.csv` (191.440 filas), `tender_2025.csv` (186.358 filas) y `awards_2025.csv` (184.712 filas).
- No es necesario lidiar con pasos de expansión de listas JSON (`Table.ExpandListColumn`) ni registros (`Table.ExpandRecordColumn`), que son los que causan caídas de rendimiento en Power Query.
- Las columnas a evaluar en la pestaña Vista (Calidad, Distribución y Perfil) son directamente los nombres nativos: `buyer_id`, `value_amount`, `amount`, `procurementMethod`, `date`.

### En el Issue #63 (Consultas M de conexión para H2):
- Las consultas M en `reports/powerbi/h2/queries/` contendrán **únicamente los pasos de conexión**, cumpliendo de forma estricta la rúbrica del Hito 2:
  - `Procesos_SERCOP`: `Csv.Document(File.Contents(".../releases_2025.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])` con promoción de encabezados.
  - `Licitaciones_SERCOP`: conexión similar a `tender_2025.csv`.
  - `Adjudicaciones_SERCOP`: conexión similar a `awards_2025.csv`.
  - `QuoteStyle=QuoteStyle.Csv` en las tres conexiones, y de forma obligatoria en `Licitaciones_SERCOP`, por los campos con salto de línea de la sección 5.5.
- La combinación o cruce de licitaciones y adjudicaciones con el proceso queda reservada para el Hito 3, evitando violar la regla de *«solo diagnosticar, no corregir ni transformar en H2»*.

### En el Issue #69 (Diccionario de datos y matriz de cobertura en Excel):
- En la hoja **Fuentes**, la fuente SERCOP se documenta directamente como CSV oficial descargado mediante el conector `Texto/CSV` (o `Carpeta`), registrando la URL oficial y el SHA-256 del ZIP.
- En el **Diccionario de datos**, los nombres de campo descritos son los del CSV oficial (`buyer_id`, `buyer_name`, `value_amount`, `procurementMethod`, `amount`), eliminando discrepancias entre nombres OCDS anidados y columnas planas.
- En la **Matriz de cobertura**, se confirma al 100 % la disponibilidad de todos los campos para P1, P2 y P3.

---

## 8. Runbook para el líder: Prueba de apertura en Power BI Desktop

Este procedimiento debe ser ejecutado por el líder en Power BI Desktop (Windows) para registrar las mediciones pendientes y convalidar la Ruta A.

### Pasos de ejecución:
1. Abrir **Power BI Desktop**.
2. En la cinta **Inicio**, seleccionar **Obtener datos** → **Texto/CSV**.
3. Navegar a la carpeta derivada:  
   `ec-gov-procurement-dw\data\derivados\sercop-portal-csv-2025-20261121-141748\`
4. Seleccionar el archivo `releases_2025.csv` y hacer clic en **Abrir**.
5. En la ventana de vista previa:
   - Verificar que el origen de archivo detectado sea `65001: Unicode (UTF-8)`.
   - Verificar que el delimitador sea `Coma`.
   - Confirmar que los caracteres con tildes y eñes se lean correctamente en `buyer_name`.
   - Hacer clic en **Transformar datos** (NO en Cargar).
6. En el Editor de Power Query:
   - En la barra de estado (esquina inferior izquierda), cambiar la opción predeterminada:  
     *«Generación de perfiles de columna basada en las primeras 1000 filas»* → **«Generación de perfiles de columna basada en todo el conjunto de datos»**.
   - En la pestaña **Vista**, activar **Calidad de columnas**, **Distribución de columnas** y **Perfil de columna**.
   - Evaluar si la navegación y el cálculo de estadísticas responden de forma fluida.
7. Repetir la conexión para `tender_2025.csv` (119 MB) y comprobar si el cálculo del perfil sobre todo el conjunto es manejable.
8. Repetir la conexión para `awards_2025.csv` (37 MB).
9. Completar la siguiente tabla con los resultados reales observados:

### Resultados de la prueba en Power BI Desktop (21/11/2026, registrados por el líder en el chat)

Las mediciones son estimaciones del líder, sin cronómetro. Lo que el líder no anotó queda como «No registrado»; no se inventa.

| Variable evaluada | `releases_2025.csv` (48 MB) | `tender_2025.csv` (119 MB) | `awards_2025.csv` (37 MB) |
|---|---|---|---|
| **Codificación detectada por Power BI** | No registrada (el script detectó `utf-8`) | No registrada (el script detectó `utf-8`) | No registrada (el script detectó `utf-8`) |
| **Delimitador detectado** | Coma: columnas bien separadas en la captura | Coma: columnas bien separadas en la captura | No registrado (el script detectó coma) |
| **Tiempo de carga inicial a Power Query** | Inmediato (vista previa) | Inmediato (vista previa de las primeras 1.000 filas) | No registrado por separado |
| **Tiempo de perfilado «todo el conjunto»** | No registrado; fluido | Hasta unos 60 s en la calidad de columnas (29 columnas); estimación del líder | No registrado |
| **¿El equipo responde de forma fluida (sin colgarse)?** | Sí | Sí | Sí (el líder: «en ningún momento se colgó el equipo») |
| **Memoria RAM ocupada por Power BI** | No registrada | No registrada | No registrada |
| **Filas vistas en Power Query** | 191.440 (coincide con el archivo) | 186.360 en «Origen» y 186.359 tras promover encabezados (el archivo tiene 186.358 registros, ver sección 5.5) | No registrado |

**Perfil de columnas observado (capturas del líder):** en `releases_2025`, `ocid` tiene 191.440 valores distintos y únicos; `buyer_id` tiene 4.973 distintos (504 únicos) y `buyer_name` 3.266 distintos (212 únicos), es decir, hay más identificadores que nombres; `initiationType` tiene un solo valor. En `tender_2025`, `ocid`, `release_id` e `id` tienen 186.359 valores distintos y únicos (la fila de más de la sección 5.5). Son cifras nacionales, sin filtrar por sector.

### Veredicto del líder:
El líder aprobó la Ruta A en el chat el 21/11/2026 («Sí, apruebo Ruta A»).
- [x] **Aprobada Ruta A (CSV del portal):** Power BI Desktop maneja fluidamente las tres tablas y se avanza con esta opción para #62 y #63.
- [ ] **Requiere Ruta B (extractor del issue #66):** el archivo `tender_2025.csv` causa lentitud excesiva y se prefiere conectar a los CSV derivados de #66.

---

## 9. Qué se midió y qué NO se midió

Siguiendo las reglas de honestidad técnica y calidad senior del repositorio:

### Lo que se midió y verificó:
- Petición HTTP real y cabeceras de respuesta del portal SERCOP para el recurso `type=csv` (estado 200) y bytes recibidos iguales al `Content-Length` en las cinco descargas completas (2021 a 2025), con su hash SHA-256 en `docs/h2/evidencia/descargas-sercop.csv`.
- Descompresión controlada en `data/derivados/` sin alterar los ZIP crudos, e integridad de los ZIP válidos con `zipfile.testzip`.
- Tamaños, hashes, columnas, número de registros y número de campos con salto de línea de las 8 tablas de cada año, con `scripts/inspect_csv_header.py` (resúmenes en `docs/sources/sercop-AAAA-portal-csv-summary.json`).
- Prueba de apertura y perfilado de las tres tablas de 2025 en Power BI Desktop por el líder (sección 8).
- Suite del repositorio: `uv sync --locked`, `ruff check`, `ruff format --check` y `pytest` sin fallos al cerrar esta revisión (ver el PR).

### Lo que se midió con un recuento aparte, no versionado:
Estas cifras salieron de un recuento con el módulo `csv` de Python sobre los archivos extraídos de 2025, hecho por Gemini 3.8 Flash y recalculado de forma independiente por Claude Sonnet 5.5 el 21/11/2026 con los mismos resultados. No hay un script del repositorio que las reproduzca, así que quien revise el PR no puede regenerarlas con un comando:
- `ocid` distintos y vacíos en `releases` y `tender` (191.440 y 186.358, sin duplicados ni vacíos).
- Filas con dato en las columnas de P1 a P3 (`procurementMethod`, `procurementMethodDetails`, `value_amount`, `tenderPeriod_startDate`, `amount`, `date`).
- Distribución de adjudicaciones por proceso: 183.098 procesos con adjudicación, 300 con más de una (1.914 filas, máximo 233).
- Que todos los `ocid` de `tender` y `awards` existen en `releases`.

### Lo que NO se midió (queda pendiente y no se inventa):
- **Memoria RAM, codificación y delimitador detectados por Power BI y tiempos exactos:** no se anotaron; solo hay estimaciones del líder.
- **Perfilado en Power BI de 2021 a 2024:** solo se probó 2025. Los CSV de esos años están descargados e inspeccionados con el script, pero no se abrieron en Power BI.
- **Valor de `QuoteStyle` en la conexión generada por Power BI:** no se leyó completo; la causa de la fila de más en `tender_2025` es una inferencia (sección 5.5).
- **Campos de P1 a P3 y grano en 2021 a 2024:** solo se comprobaron en 2025; en 2021 a 2024 se contaron registros y saltos de línea, nada más.
