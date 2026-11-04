# Reconocimiento de la fuente SERCOP

**Consulta:** 11 de octubre de 2026. **Fuente:** portal oficial Contrataciones Abiertas Ecuador – OCDS, administrado por SERCOP.

Este reconocimiento documenta lo que ofrece el portal y una inspección inicial de descargas reales. Incluye conteos y disponibilidad de algunas propiedades; no equivale a una validación completa de calidad ni al diseño del ETL.

## Dónde estamos

- **Trabajo:** [issue #9](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9), reconocimiento de la fuente en fase 0. Se contrastó con la evidencia disponible hasta el 15/10/2026 y se cerró ese día con el PR #24.
- **Comprobado:** accesos publicados, campos reales, descargas JSON mensual y anual, hashes y reconciliación de 190.619 procesos distintos con el contador anual.
- **Límite observado:** la API anuncia 60; dos reinicios consecutivos observados quedaron separados por 61 segundos. El contador no se comportó como exclusivo del cliente y SERCOP no publica su ámbito, por lo que la conclusión se limita a una ventana observable cercana a un minuto.
- **Cierre:** los cinco criterios tienen evidencia y el issue se cerró al integrarse el PR #24.
- **Trabajo del líder adicional en fase 0:** integrar E0 en el issue #14, usando contenido de #10 y plantilla de #13; fecha interna 17 oct. #14 se cerró el 17/10/2026 con el PR #31; el PDF y su subida al curso siguen pendientes del líder. La ruta está en [PLAN.md](../PLAN.md).
- **Fases siguientes:** el periodo definitivo se decide en #15 (fase 1); la foto formal y el manifiesto se preparan al inicio de la fase 2. El docente indicó analizar cinco años o comparar por gobiernos. No se observó en SERCOP un campo de gobierno o administración, por lo que #15 evaluará una delimitación por fechas; `2021–2025` es el candidato inicial de cinco años calendario completos, no una decisión cerrada por este reconocimiento. Estas descargas no son todavía la foto definitiva.

## Inventario y conservación de la evidencia

| Archivo | Finalidad | Estado y uso |
|---|---|---|
| [CSV v1](sercop-api-rate-limit-observations.csv) | Dos mediciones HTTP 429 iniciales, con sus horas y cabeceras registradas | Histórico cerrado. Mezcla las variantes de cabecera de cuota y no tiene hora de recepción. No usarlo para deducir la ventana ni anexarle nuevas filas. |
| [CSV v2](sercop-api-rate-limit-observations-v2.csv) | Seis muestras posteriores, con variantes `RateLimit-*` y `X-RateLimit-*` separadas | Evidencia histórica cerrada en el esquema vigente. Una fila conserva un error local conocido y explicado en el apartado de recuperación. Las nuevas ejecuciones usan otros archivos. |
| [Primer intento v3](sercop-api-rate-limit-observations-v3-9d609acf-6a81-417f-aebd-1064cc78e2b5.csv) | Una consulta con la nueva configuración de traza | Se detuvo por `SocketException` sin capturar respuesta HTTP; las celdas vacías no prueban ausencia de cabeceras en SERCOP. |
| [Captura de cierre v3](sercop-api-rate-limit-observations-v3-95428e1f-807a-4dc5-b0e2-dabcb8d3fdae.csv) | Una consulta controlada del 15/10/2026 con la traza completa | HTTP 200, límite 60 y restantes 0; no anunció política, ventana ni reinicio. No hubo redirección ni error local y el script se detuvo sin repetir. |
| [Resumen anual JSON](sercop-2025-download-observation-67ea5265effd4f98b55338529dce81c0.json) | Conteos, tamaños, hashes y datos de ejecución, sin valores de registros | Captura completa del recorrido anual; no sobrescribirla ni confundirla con un manifiesto de snapshot aprobado. |
| ZIP originales mensual y anual en `data/reconnaissance/` | Evidencia de las descargas inspeccionadas | Locales e ignorados por Git. Hashes y ubicaciones en sus apartados de inspección. |

Los CSV no son duplicados: conservan ejecuciones distintas. Mantenerlos no exige mantener varios lectores ni varias versiones del script. El auxiliar actual escribe el esquema v3 en archivos nuevos; v1 y v2 se consultan como evidencia histórica. No se migran filas antiguas para rellenar cabeceras u horas que no se capturaron. Las verificaciones del script con respuestas sintéticas están descritas como tales; no se mezclan con las muestras reales.

### Esquema de las observaciones HTTP v2

| Columnas | Significado y precaución |
|---|---|
| `run_id`, `sample` | Ejecución y muestra lógica dentro de ella; no prueban cuántas solicitudes físicas pudo realizar el cliente. |
| `request_started_utc`, `response_received_utc` | Hora UTC del cliente antes de la petición y al recibir las cabeceras. La recepción puede estar vacía si no hubo respuesta capturada. |
| `response_date` | Cabecera `Date` del servidor; su reloj no se supone idéntico al del cliente. |
| `request_url`, `http_status` | URL solicitada y estado capturado; un estado recibido puede coexistir con un error local posterior. |
| `rate_limit_limit`, `x_rate_limit_limit` | Valores de `RateLimit-Limit` y `X-RateLimit-Limit`, sin combinar variantes. No se infiere su periodo. |
| `rate_limit_remaining`, `x_rate_limit_remaining` | Valores de `Remaining`; no se presume un contador exclusivo de este cliente. |
| `rate_limit_reset`, `x_rate_limit_reset` | Reinicio anunciado en cada variante. Su interpretación debe separar cabecera estándar y cabecera X. |
| `rate_limit_policy`, `x_rate_limit_policy`, `rate_limit_window`, `x_rate_limit_window` | Cabeceras opcionales observadas; en las capturas disponibles están vacías. |
| `retry_after` | Valor de la cabecera `Retry-After`; la norma y lo observado se distinguen en el apartado de límites. |
| `transport_error` | Nombre histórico de la columna de errores. Puede indicar transporte o procesamiento local de cabeceras; no renombrar ni reinterpretar retrospectivamente sus filas. |

Una celda vacía significa que no se capturó un valor. En una fila sin error puede corresponder a una cabecera ausente; en una fila con error también puede deberse a una captura interrumpida. El CSV no registra caché, URL final ni solicitudes ajenas; no basta para reconstruir la política interna del servidor.

### Traza v3 para las próximas observaciones

La versión v3 conserva las columnas v2 y añade `response_age`,
`response_cache_control`, `response_via`, `response_x_cache`,
`response_request_url`, `redirect_location_present`, `client_allow_redirects`
y `request_cache_control`. Captura cabeceras de caché si están presentes y la
URL asociada a la respuesta del cliente; solo registra la presencia de
`Location`, sin copiar un destino que podría contener credenciales.

El cliente desactiva las redirecciones automáticas y las cookies, y se detiene
ante cualquier estado distinto de 200. Envía `Cache-Control: no-cache` para
solicitar revalidación; esto no acredita que todos los intermediarios obedezcan
la directiva ni que la respuesta provenga directamente del origen. Referencias:
[AllowAutoRedirect](https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.allowautoredirect)
y [RFC 9111, no-cache](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.1.4).
La única respuesta real de SERCOP capturada con v3 es la del cierre del
15/10/2026 (HTTP 200, sin cabeceras de política, ventana ni reinicio). Una muestra
sigue siendo una operación lógica; la traza no mide tráfico ajeno ni el
comportamiento interno de proxies o del servidor.

### Uso de los auxiliares

- `scripts/inspect_sercop_zip.py`: inspección local de un ZIP, sin llamadas a la API. Guarda el resumen en un archivo nuevo mediante `--output`; se detiene ante una estructura no admitida o si cambia el hash del ZIP. El comando anual aparece en su apartado de inspección.
- `scripts/observe_sercop_rate_limit.ps1`: observa el estado y las cabeceras de una consulta GET fija de búsqueda. Parámetros: `Samples` (1–48, predeterminado 10), `InitialDelaySeconds` (0–86400, predeterminado 0), `IntervalMinutes` (1–1440, predeterminado 10) o `IntervalSeconds` (10–86400), `StopAtRemaining` (0–59, predeterminado 10) y `OutputPath` para una ruta nueva. Los dos intervalos son excluyentes. Cada ejecución crea por defecto `sercop-api-rate-limit-observations-v3-<run_id>.csv`; rechaza una salida existente antes de consultar la fuente. Se detiene ante estado distinto de 200, margen de cuota o error. No ejecutar para repetir una medición sin una hipótesis y un resultado esperado claros.

Los auxiliares no implementan `extract`, `snapshot`, staging ni cargas del DW.
La ausencia actual de suite, linter y CI no es un criterio incumplido de #9:
este issue exige reconocimiento y evidencia, no infraestructura del DW. La
verificación aplicable aquí es la sintaxis del auxiliar, la estructura del CSV,
los enlaces, la conservación de evidencia y una consulta HTTP controlada. El
plan vigente ubica el entorno reproducible, las pruebas unitarias y CI en la
fase 3 (24 nov–14 dic), y las pruebas de integración, idempotencia y
reconciliación en la fase 4 (15 dic–8 ene). Adelantar el mínimo de `ruff`,
`pytest` y CI al primer código de `extract`/`snapshot` de la fase 2 requiere
una tarea de coordinación separada; no forma parte de este PR.

### Revisión de conservación y documentación, 11/10/2026

- Se contrastaron en GitHub los criterios del issue #9, las tareas de integración #14 y las dependencias de fase 0. En esa fecha, el PR #21 estaba abierto y conservaba una revisión publicada con cambios pedidos; fue corregido e integrado el 12/10/2026, cerrando #11.
- Los dos CSV conservaron sus hashes durante la revisión: v1, `6D544C72FCA05198A55C38EB74670B102483985021B843906BC88D1F3A92B9A7`; v2, `960EAFE8839D47C837B30106627AE41ACCA1FA44D7EBEE61C15A1DD5FC558ECE`.
- Se comprobó con `git check-ignore` que los ZIP y derivados bajo `data/`, `.env`, `.venv/` y cachés de Python quedan ignorados. `data/README.md`, `.env.example`, los resúmenes/CSV de `docs/sources/` y un nombre de ZIP de entrega bajo `deliverables/` permanecen disponibles para versionar. Los archivos originales descargados no están rastreados; `git ls-files -- data` devuelve únicamente `data/README.md`.
- Se inspeccionaron 31 enlaces locales a archivos en 11 Markdown modificados, sin destinos faltantes. La comprobación de rutas no certifica enlaces externos ni anclas de secciones.
- La sintaxis de ambos auxiliares se analizó sin errores. El cambio de creación de CSV usa una ruta nueva por ejecución y apertura exclusiva con [FileMode.CreateNew](https://learn.microsoft.com/en-us/dotnet/api/system.io.filemode#fields); no se ejecutó una nueva consulta HTTP para comprobar ese cambio. Las lecturas reales anteriores y las comprobaciones históricas con respuestas sintéticas no se presentan como pruebas del nuevo comportamiento de salida.
- `git diff --check` no informó errores de espacios en los cambios rastreados. Git emitió un aviso de conversión LF a CRLF para `.gitignore`. No se añadieron ni ejecutaron pruebas automatizadas o linter; no hay configuración para ellos en este proyecto.

**Revisión posterior del mismo día (estado histórico):** GitHub confirmó que
Harry trabajaba en #11 mediante el PR #21, cuyo último commit consultado era
`1b6ff9ad6057033e3b65fd45f8a12c2fd927e7df`. En ese momento seguían abiertos
la revisión formal y tres conversaciones. El PR fue corregido e integrado el
12/10/2026; su resumen del estándar no aporta una definición de la ventana de
API y no sustituye la evidencia de #9. La lectura del manual público por HTTP
respondió 200: describe `search_ocds` y `record`,
pero no se encontró allí una definición de cuota temporal. La búsqueda de
repositorios públicos tampoco proporcionó configuración verificable de la
API desplegada; no se deduce la cuota a partir de valores predeterminados de
un framework.

**Comprobaciones locales antes de guardar el avance:** el inspector pasó
pruebas temporales con JSON sintético válido e inválido, cortes entre bloques,
conteos anidados, hash del ZIP y rechazo de una salida existente. Su hash
coincide con el registrado en el resumen anual. El observador v3 pasó el
análisis de sintaxis y comprobaciones con un cliente sustituido por un doble
sintético: 200 sin `Retry-After`, cabeceras de caché, parada ante 302, 429, 503,
margen de cuota y error de transporte, omisión del destino de redirección y
rechazo de un archivo ya existente. Se verificaron la configuración del
handler y la directiva de petición, sin comprobarlas contra un servidor real.
Los archivos sintéticos se eliminaron y los hashes históricos v1/v2
permanecieron iguales. Estas comprobaciones ad hoc no configuran una suite,
linter ni CI; no se volvió a recorrer el ZIP anual. El intento real de API
con v3 realizado después se registra por separado en el protocolo de cuota.

## Procedencia y actualización

Las [notas metodológicas oficiales](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/notas-metodologicas) identifican tres fuentes primarias: el Sistema Oficial de Contratación Pública (SOCE), el módulo de Compras Corporativas del Sector Salud y el módulo de Compras Corporativas de Alimentación Escolar. SERCOP indica que transforma los datos a OCDS 1.1, los indexa para búsqueda y descarga, actualiza la información en la noche y actualiza diariamente las descargas masivas.

El portal reúne contratación pública de Ecuador. El alcance de este proyecto es más estrecho: la planta central del Estado y sus ministerios e institutos dependientes; excluye GAD y sus empresas. Por tanto, los totales generales del portal no son automáticamente el volumen que usará el DW. Una ficha de resultado de 2025 incluida en el [buscador oficial](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/procedimientos?local=1&page=1&year=2025) muestra una junta parroquial, señal de que el buscador abarca entidades fuera del alcance del proyecto.

## Formas de acceso observadas

| Vía | Qué ofrece | Evidencia |
|---|---|---|
| Descarga masiva | Filtros por año, mes y tipo; formatos JSON, CSV y XLSX. | [Portal de datos abiertos](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/). En la interfaz, al elegir 2025, todos los meses y todos los tipos, los enlaces visibles apuntan a los recursos `download` con `year=2025`, `month=0` y `method=all`. |
| API de búsqueda | `GET /PLATAFORMA/api/search_ocds`; requiere `year` (2015–año actual) y `search` (mínimo 3 caracteres). `page` es opcional y debe ser mayor a cero; `buyer` y `supplier` son opcionales y requieren mínimo 3 caracteres. | [Documentación oficial de la API](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api). |
| API de registro | `GET /PLATAFORMA/api/record?ocid=...` para consultar un proceso por su `ocid`. | [Documentación oficial de la API](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api). |

Enlaces del filtro 2025 observado (todos los meses y tipos): [JSON](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=json&year=2025&month=0&method=all), [CSV](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=csv&year=2025&month=0&method=all) y [XLSX](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=xlsx&year=2025&month=0&method=all). Son enlaces observados en la interfaz. El líder descargó después los ZIP JSON mensual y anual; los archivos anuales CSV y XLSX no se han descargado. Las inspecciones locales se describen a continuación.

## Campos: evidencia y límites de lo observado

**Fichas reales del buscador:** con el filtro del año 2025 cargado en vivo, la primera página presentó 10 fichas y la paginación indicó 19.062 páginas. Los rótulos visibles fueron `ID`, `FECHA DE PUBLICACIÓN`, `TÍTULO`, `DESCRIPCIÓN`, `PRESUPUESTO`, `ENTIDAD CONTRATANTE` y `TIPO DE CONTRATACIÓN`. Los valores de `ID` usan identificadores con prefijo OCDS. Son campos presentados por la interfaz; no se deben tomar como nombres de propiedades JSON ni como garantía de presencia en todos los registros. El primer lote también incluye una junta parroquial, fuera del alcance del DW.

**Respuesta real de API:** una consulta `search_ocds?year=2025&search=agua&page=1` respondió HTTP 200 con `total=2448`, `page=1`, `pages=245` y 10 elementos en `data`. Los nombres de propiedades del primer elemento fueron `id`, `ocid`, `year`, `month`, `method`, `internal_type`, `locality`, `region`, `suppliers`, `buyer`, `amount`, `date`, `title`, `description` y `budget`. Se guardaron solo nombres y metadatos, no valores del registro. El total corresponde a la palabra clave `agua`, no a todos los procedimientos del año.

**Ejemplo de la documentación de API:** su ejemplo de búsqueda muestra `total`, `page`, `pages` y `data`, con campos como `buyerId`, `buyerName` y `single_provider`, que no aparecieron entre las propiedades del primer elemento observado en vivo. El ejemplo de `/record` presenta un paquete con `uri`, `license` y `records`, y dentro de estos `ocid` y `releases`. No asumir que el ejemplo y cada resultado real tengan el mismo conjunto de propiedades.

## Volumen de 2025

- **Buscador en vivo:** el [filtro 2025](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/procedimientos?local=1&year=2025&page=1) mostró **190.619 procedimientos** al consultar la página el 11/10/2026. Es el total nacional del buscador, no el subconjunto de entidades incluido en este DW.
- **Descarga masiva en vivo:** con 2025, todos los meses y todos los tipos, el contador también mostró **190.619**. Ambas vistas coinciden en la consulta en vivo.
- **Copia indexada:** una captura indexada consultada durante la revisión mostraba 190.306; difiere en 313 del total en vivo. La metodología indica actualizaciones nocturnas, así que la antigüedad de la copia puede explicar la diferencia, pero no se verificó cuándo se generó esa captura.
- **Tamaño anunciado del JSON anual:** el `HEAD` del [enlace JSON 2025](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=json&year=2025&month=0&method=all) respondió HTTP 200, `Content-Type: application/zip` y `Content-Length: 160929006` bytes (160,93 MB decimales). En esa consulta solo se midió la cabecera; la descarga posterior se describe abajo y tiene un tamaño distinto.

## Inspección del ZIP anual JSON

El líder descargó `releases_2025.zip` el 11/10/2026 en `data/reconnaissance/sercop-2025-all-20261011-184252/`. La captura aportada confirma **2025, todos los meses y todos los tipos**, y muestra **190.619 procedimientos** en el contador del portal. El archivo está ignorado por Git.

| Medida | Resultado observado localmente |
|---|---|
| Tamaño del ZIP descargado | 160.930.685 bytes |
| SHA-256 del ZIP | `80201404465D6C212E4AD53C60E6A928CEEBF0EADFB57A0E200805B49A1894A3` |
| Contenido del ZIP | Un archivo: `releases_2025.json` |
| Tamaño del JSON sin comprimir | 1.721.952.613 bytes, aproximadamente 1,72 GB decimales |

El hash calculado localmente coincide con el reportado por el líder. El ZIP tiene 1.679 bytes más que el tamaño anunciado por el `HEAD` anterior. Son observaciones realizadas en momentos distintos; no se identificó la causa de esa diferencia y no se trataron ambos archivos como una misma captura.

**Método del conteo anual:** `scripts/inspect_sercop_zip.py` usa Python 3.13 y solo la biblioteca estándar. Abre el ZIP en modo lectura, decodifica un paquete por vez con `JSONDecoder.raw_decode` y no extrae archivos. Conserva en memoria conjuntos de identificadores para contar los `ocid` y pares (`ocid`, `release.id`) distintos; su memoria crece con esos conjuntos, sin cargar el JSON completo. Un límite de 64 Mi caracteres detiene la lectura si un objeto o fragmento pendiente supera el búfer permitido.

El resumen incluye identificador de ejecución, fechas UTC, versión de Python, hash del script y del ZIP, tamaños, conteos, presencia de campos y comparación opcional con un conteo esperado. No incluye valores de registros ni identificadores reales. Comprueba el hash del ZIP antes y después; si hay un fallo de lectura o cambia el hash, no genera un resumen completo. La salida se crea como archivo nuevo y no sobrescribe evidencias anteriores. El helper admite exactamente una entrada JSON con una lista raíz de paquetes y listas de objetos para releases, adjudicaciones y contratos; se detiene si encuentra una estructura diferente. No valida el esquema OCDS, no clasifica entidades y no certifica cobertura.

La ejecución local del helper sobre el ZIP de enero confirmó los conteos previamente observados: 2.186 paquetes, releases y `ocid` distintos; 2.135 adjudicaciones; 2.106 contratos; 177 contratos con importe numérico; cuatro releases con varias adjudicaciones y dos con varios contratos. El conteo esperado de 2.186 en esa ejecución procede de la inspección mensual anterior, no de un contador mensual del portal. La ejecución final fue `run_id=3b434d50-b9dc-4b2f-8321-7fe26425b44c`, con código de salida 0 y hash del ZIP sin cambios. El intérprete emitió un aviso de localización de su ejecutable en el entorno del agente; no impidió completar la lectura. No hay una suite de pruebas ni linter configurados en el proyecto.

**Resultado anual ejecutado por el líder:** el [resumen de observación](sercop-2025-download-observation-67ea5265effd4f98b55338529dce81c0.json) registra `run_id=fc617c47-4638-4614-899a-3b5b8aaffb32`. La lectura empezó a las 23:53:19,681 UTC y terminó a las 23:53:41,772 UTC del 11/10/2026, con duración de 22,092 segundos. El hash del script registrado coincide con el de la versión local inspeccionada: `9644548AA315BA3A7BB8EE3722DDA30CC210BA032069AE4FC7F8C6A739B8D8DD`.

| Conteo anual | Resultado |
|---|---:|
| Paquetes | 190.619 |
| Releases | 190.619 |
| `ocid` distintos | 190.619 |
| Releases sin `ocid` no vacío | 0 |
| Pares (`ocid`, `release.id`) distintos | 190.619 |
| Objetos de adjudicación | 183.891 |
| Adjudicaciones con importe numérico | 183.887 |
| Objetos de contrato | 180.465 |
| Contratos con importe numérico | 27.666 |
| Releases con varias adjudicaciones | 300 |
| Releases con varios contratos | 270 |

El número de `ocid` distintos coincide con los 190.619 del contador del portal. En esta captura anual cada release tiene un `ocid` distinto. El script registra que el hash del ZIP no cambió durante la inspección. Las distribuciones del resumen son consistentes con los totales: al sumar sus frecuencias se obtienen 190.619 releases y, al ponderarlas por la longitud de cada lista, 183.891 adjudicaciones y 180.465 contratos.

Solo el **15,33 % de los objetos de contrato** tiene importe numérico; 152.799 no lo tienen. Cuatro objetos de adjudicación carecen de importe numérico. Estos conteos no convierten la ausencia en cero ni validan estados, monedas o importes comparables. Son resultados nacionales de este archivo, todavía sin clasificación de entidades de la planta central. La propiedad `buyer` aparece en todos los releases, pero eso no acredita que todos sus identificadores y nombres sean utilizables. La reconciliación del contador tampoco verifica todo el historial de los procesos ni la conformidad del archivo con los esquemas OCDS.

Para reproducir el conteo anual, ejecutar desde la raíz del repositorio, sustituyendo el nombre de salida por uno nuevo en cada captura:

```powershell
python .\scripts\inspect_sercop_zip.py `
    .\data\reconnaissance\sercop-2025-all-20261011-184252\releases_2025.zip `
    --expected-processes 190619 `
    --output .\docs\sources\sercop-2025-download-observation-NUEVO-ID.json
```

Referencias de la implementación: [JSONDecoder.raw_decode](https://docs.python.org/3.13/library/json.html#json.JSONDecoder.raw_decode) y [ZipFile.open](https://docs.python.org/3.13/library/zipfile.html#zipfile.ZipFile.open).

## Inspección local de la descarga mensual JSON

El líder descargó `releases_2025_enero.zip` el 11/10/2026 para continuar el reconocimiento. Una captura de la interfaz aportada por el líder confirma los filtros **año 2025, mes enero y todos los tipos de contratación**. El original se conserva en `data/reconnaissance/sercop-2025-01-20261011-180225/`, ignorado por Git. La inspección abrió el ZIP en modo lectura y analizó el JSON en memoria con `zipfile` y `json` de la biblioteca estándar de Python; no extrajo archivos ni imprimió registros completos.

| Medida | Resultado observado |
|---|---|
| Tamaño del ZIP | 1.140.250 bytes |
| SHA-256 del ZIP, antes y después de la inspección | `9F1D1B2C446927934854EE8C6B51C0FE3957614284E34D4D8C38AD8E16952685` |
| Contenido | Un archivo: `releases_2025_enero.json`, de 13.497.759 bytes sin comprimir |
| Estructura raíz del JSON | Lista de 2.186 objetos de paquete |
| Versión declarada | `1.1` en los 2.186 paquetes |
| Releases | 2.186; exactamente uno por paquete |
| `ocid` presentes y distintos | 2.186 presentes; 2.186 distintos |
| `release.id` presentes y distintos | 2.186 presentes; 2.186 distintos |

Cada paquete contiene `uri`, `license`, `version`, `releases`, `publisher`, `extensions`, `publishedDate` y `publicationPolicy`. El contenido real tiene estructura anidada: no es la lista de propiedades resumidas que devolvió `search_ocds`.

| Sección del release | Releases donde existe la propiedad | Campos hijos observados, seleccionados |
|---|---:|---|
| `buyer` | 2.186 | `id`, `name` |
| `tender` | 2.141 | `id`, `title`, `description`, `procurementMethod`, `procurementMethodDetails`, `value`, `tenderPeriod` |
| `awards` | 2.126 | `id`, `date`, `suppliers`, `value` |
| `contracts` | 2.100 | `id`, `awardID`, `dateSigned`, `period`, `value` |
| `planning` | 257 | `budget`, `rationale` |
| `parties` | 2.186 | `id`, `name`, `identifier`, `roles`, `address`, `contactPoint` |

Estos son conteos de presencia de la propiedad, no una validación de completitud de sus campos ni de listas no vacías. La inspección también encontró `relatedProcesses`, `auctions` y `bids`. No se validó el JSON contra los esquemas de OCDS ni contra sus extensiones; que declare versión 1.1 no acredita conformidad completa.

**Montos observados:** se recorrieron todos los releases y las listas de adjudicaciones y contratos. Las rutas siguientes contienen importes numéricos y una propiedad `currency` con texto no vacío en los casos contados. Todavía no se evaluaron monedas compatibles, signos, estados de adjudicación/contrato ni duplicados de esas listas.

| Ruta del importe numérico | Casos observados | Unidad contada |
|---|---:|---|
| `tender.value.amount` | 2.050 de 2.186 | Releases |
| `planning.budget.amount.amount` | 153 de 2.186 | Releases |
| `awards[].value.amount` | 2.135 de 2.135 | Objetos de adjudicación |
| `contracts[].value.amount` | 177 de 2.106 | Objetos de contrato |

La [referencia oficial OCDS](https://standard.open-contracting.org/latest/en/schema/reference/) distingue el presupuesto reservado en `planning.budget.amount`, el valor máximo estimado de la contratación en `tender.value`, el valor de cada adjudicación en `awards[].value` y el valor de cada contrato en `contracts[].value`. Son conceptos distintos; no se propone sustituir automáticamente uno por otro para completar datos faltantes.

Hay **cuatro** releases con más de una adjudicación: uno con dos, uno con tres y dos con cuatro. Hay dos releases con más de un contrato, ambos con cuatro. El líder reprodujo estos conteos en PowerShell y una lectura independiente del ZIP confirmó 4 y 2; se corrigió el conteo inicial de cinco, que era un error de suma del borrador. Por ello, contar o sumar objetos anidados no equivale a contar procesos. Si se mantiene un hecho por `ocid` y foto, se deberán definir las reglas de agregación y evitar multiplicar filas al combinar ambas listas. La ausencia del valor contractual en 1.929 objetos de contrato es un hallazgo de disponibilidad en esta descarga mensual; no demuestra por sí sola un defecto del estándar ni su frecuencia en toda la fuente.

**Fechas y significado del filtro:** de los 2.186 releases, 1.984 tienen `date` con prefijo `2025-01` y 202 tienen fechas posteriores, hasta septiembre de 2026. Solo 576 paquetes tienen `publishedDate` con prefijo `2025-01`; los demás tienen fechas posteriores, hasta septiembre de 2026. `tender.tenderPeriod.startDate` está presente en 212 releases y todos esos valores empiezan por `2025-01`. Se compararon los prefijos de fecha tal como están publicados, sin convertir zona horaria. Por tanto, el nombre del archivo no permite interpretar todas sus fechas como enero ni identificar de forma concluyente qué atributo usa el filtro mensual. Tampoco una descarga de un release por proceso acredita que se conserve todo su historial. Estos puntos se deben resolver antes de fijar la fecha de negocio y la cobertura de la foto.

La descarga y lectura local mensual resultaron posibles. Esto permite continuar evaluando la vía masiva sin consultas de búsqueda para cada proceso; aún no demuestra que el archivo anual esté completo, que represente exclusivamente la planta central o que contenga todas las medidas requeridas por el DW.

## Límites de la API

La guía oficial especifica parámetros y validaciones de entrada, pero no publica una cuota ni ventana temporal. Dos consultas manuales reales `search_ocds` respondieron HTTP 200 y devolvieron `X-RateLimit-Limit: 60`; sus valores `Remaining` fueron 33 y, después de esperar 60 segundos, 25. No registraron cabeceras de reinicio/ventana. La diferencia entre esos contadores no se atribuye solo a esas dos consultas: otros consumidores pueden compartir la cuota.

La primera observación del script (`run_id=c944079b-c514-41e9-99eb-63ec9d9ce3c7`) y la segunda (`run_id=bd565ca5-397f-4a6e-9117-d631a5a5d632`) respondieron HTTP 429 con límite 60 y restantes 0. En el CSV v1, `rate_limit_reset` combina `RateLimit-Reset` y `X-RateLimit-Reset`, sin indicar cuál de las dos cabeceras aportó el valor; por eso sus números `1791755338` y `1791756240` no se interpretan como fechas. El borrador IETF de `RateLimit-Reset` lo define como segundos hasta el reinicio, mientras que el servidor podría estar usando una convención distinta en `X-RateLimit-Reset` ([IETF RateLimit fields](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers-05#section-5.4)).

Las respuestas v1 reportaron `Retry-After: 14` y `Retry-After: 12`. HTTP define un valor numérico de `Retry-After` como los segundos de espera después de recibir la respuesta ([RFC 9110, sección 10.2.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3)). Aunque esas respuestas estuvieron separadas por unos 15 minutos y los valores `rate_limit_reset` también difirieron en unos 15 minutos, v1 mezclaba las dos variantes de cabecera y no guardaba la hora en que el cliente recibió la respuesta. Por ello, esos datos no bastan para fijar la ventana.

Las dos primeras muestras de v2 (`run_id=06680e44-4169-4e1f-829b-b840034f1bdc` y `run_id=5b590414-694e-4100-9ccd-e0b99f7b2532`) respondieron HTTP 429, con `X-RateLimit-Limit: 60` y `X-RateLimit-Remaining: 0`. `RateLimit-Reset` estaba ausente y `X-RateLimit-Reset` contenía, respectivamente, `1791756723` y `1791756784`. Interpretados como marcas de tiempo Unix UTC, corresponden a 22:12:03 y 22:13:04 del 11/10/2026. En ambas filas, esas horas coinciden con `response_date + Retry-After`: 22:11:55 + 8 s y 22:12:48 + 16 s. Esto respalda interpretar **esta cabecera X** como una fecha/hora de reinicio absoluta; no demuestra la duración de la ventana. La cabecera `Date` del servidor aparece unos 8–9 segundos detrás de la hora de recepción UTC del cliente, así que no conviene comparar ambas horas como si tuvieran el mismo reloj.

Los dos valores de reinicio están separados por 61 segundos. Cada respuesta 429 ocurrió, según `response_date`, antes del reinicio que ella misma anunciaba. Esto permite estudiar las horas de reinicio, pero no basta para establecer la duración o política de la cuota; esta también podría ser compartida con otros consumidores.

**Recuperación observada:** la muestra `run_id=e9097744-f834-44ac-80b7-9c0609d57c6b`, recibida a las 22:18:16 UTC del 11/10/2026, respondió HTTP 200 con `X-RateLimit-Limit: 60` y `X-RateLimit-Remaining: 58`, sin `X-RateLimit-Reset`. Fue posterior al último reinicio anunciado y se recibió unos 5 minutos y 20 segundos después del último 429. La ejecución esperó 60 segundos al comenzar, pero esa espera inicial no equivale al tiempo total entre ambas respuestas ni prueba una ventana de un minuto. Después de registrar estado y contador, el script encontró un fallo local al buscar `Retry-After` ausente en `Content.Headers`; por eso la fila contiene `transport_error=System.Management.Automation.MethodInvocationException`. Ese aviso no invalida el estado y los contadores leídos antes del fallo. La fila se conserva; el script se corrigió para consultar exclusivamente las cabeceras de respuesta y distinguir el aviso de procesamiento local del fallo de transporte. La corrección se comprobó con respuestas sintéticas 200 sin `Retry-After`, 429 con `Retry-After` y un fallo de transporte, sin acceso a SERCOP.

**Medición de cadencia interrumpida:** se ejecutó `.\scripts\observe_sercop_rate_limit.ps1 -Samples 13 -IntervalSeconds 10 -InitialDelaySeconds 20`, con `run_id=1d87374d-4824-4e81-9e2a-5f8c3da90f78`. La primera muestra, recibida a las 22:26:09 UTC del 11/10/2026, respondió HTTP 200 con límite 60 y restantes 2, sin error de registro. El script se detuvo porque `Remaining <= 10`; solo se realizó una de las 13 muestras solicitadas. Por tanto, esta ejecución no permite estimar una cadencia. La diferencia de 58 a 2 respecto a la muestra anterior no puede atribuirse a esta petición ni explica por sí sola si la cuota es compartida, qué tráfico se cuenta o qué ventana se aplica.

**Alcance de la política observada:** la guía oficial de API revisada describe operaciones, parámetros y ejemplos, pero no especifica la unidad temporal, el ámbito del contador ni cómo se reinicia. Para documentar la política como definida por el proveedor se requeriría una referencia técnica oficial, configuración publicada de la implementación o confirmación de SERCOP. Las cabeceras y mediciones permiten documentar el comportamiento externo exigido por este reconocimiento, pero no sustituyen una definición interna del proveedor. No se recomienda repetir la ejecución de cadencia con el contador casi agotado.

**Medición con las ventanas relacionadas cerradas:** el usuario confirmó primero que había usado o mantenido abierto el portal entre las observaciones anteriores, y después que cerró las ventanas relacionadas para ejecutar `.\scripts\observe_sercop_rate_limit.ps1 -Samples 19 -IntervalSeconds 10 -InitialDelaySeconds 120`. En esta ejecución (`run_id=403bae00-1d01-4978-bfcf-9adddd0ab9b9`), del 11/10/2026, la muestra 1 llegó a las 22:41:06,386 UTC con HTTP 200, límite 60 y restantes 15; la muestra 2 llegó a las 22:41:16,441 UTC con HTTP 429, límite 60 y restantes 0. Ambas filas carecen de error local. Las respuestas se separaron por 10,055 segundos y el script se detuvo tras dos de las 19 muestras solicitadas. La primera petición tardó 2,631 segundos y la segunda 0,039; el intervalo de 10 segundos se espera después de recibir la respuesta anterior, por lo que se suma al tiempo de las peticiones.

El 429 reportó `Retry-After: 13` y `X-RateLimit-Reset: 1791758481`, equivalente a las 22:41:21 UTC. Su `Date` fue 22:41:08 UTC, de nuevo compatible con `Date + Retry-After`. La reducción de 15 a 0 entre esas dos respuestas no concuerda con un contador exclusivo que descontara una unidad por cada petición del script. El cierre de ventanas controla una posible fuente de tráfico del usuario; no demuestra que no existan otros consumidores ni identifica el ámbito o la política del contador. Esta ejecución no permite estimar una cadencia de reinicio. Antes de repetir el experimento se requiere aclarar la definición de la cuota y la interpretación de `Remaining`.

**Canales publicados y consulta preparada:** la [política oficial de publicación](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf), página 7, apartado 5, ofrece el [chat de SERCOP](https://asesorvirtual.sercop.gob.ec/webchat/) y el teléfono `1700-737267` para consultas. En la página 8, apartado 7, remite al mismo manual de API ya revisado. El documento examinado no define una cuota temporal. La herramienta web no pudo verificar que el chat estuviera accesible, por lo que se documenta como canal publicado, no como atención comprobada. El [catálogo gubernamental del conjunto](https://www.datosabiertos.gob.ec/dataset/contrataciones-abiertas-ecuador/resource/7d10eb16-45a1-479c-b939-1c7f54a24cef) publica `diego.benavides@sercop.gob.ec`; sus metadatos están fechados el 27/12/2021; el intento posterior del líder fue rechazado, como se registra abajo. Texto técnico inicial preparado antes del intento de contacto descrito más adelante:

> Estamos realizando un proyecto universitario con los datos abiertos OCDS de SERCOP. La API devuelve `X-RateLimit-Limit: 60`, pero no encontramos la ventana temporal en el manual. El 11/10/2026 consultamos `search_ocds?year=2025&search=agua&page=1` mediante un script, con las ventanas del portal cerradas y una espera inicial de 120 segundos. Recibimos HTTP 200 con `X-RateLimit-Remaining: 15` a las 22:41:06 UTC y HTTP 429 con restantes 0 a las 22:41:16 UTC; el script registró esas dos muestras y se detuvo. El 429 indicó `Retry-After: 13` y `X-RateLimit-Reset: 1791758481`. ¿Podrían derivar la consulta al responsable técnico y confirmar: (1) cuota y periodo de `search_ocds` y `record`; (2) a quién se aplica el límite y cómo se calcula `Remaining`; (3) si ambos endpoints y el portal web comparten contador; y (4) si `X-RateLimit-Reset` es una marca de tiempo Unix? Agradecemos documentación vigente o una confirmación escrita. Si este canal no corresponde, agradeceríamos que nos indiquen el contacto actual.

**Reproducción de las observaciones:** v1 y v2 quedan preservados. El esquema actual v3 registra cada variante de cabecera por separado, inicio y recepción del cliente, `Date` del servidor y la traza descrita arriba. El script acepta `-IntervalSeconds` o `-IntervalMinutes`, pero no ambos. Con `-Samples 1` no hay espera entre muestras; la espera inicial predeterminada es cero y se controla mediante `-InitialDelaySeconds`. Se detiene ante estado distinto de 200, el margen configurado de `Remaining` (10 por defecto) o un error, y no reintenta automáticamente ni lee o guarda el cuerpo de respuesta. Las comprobaciones locales con respuestas sintéticas no se añadieron a los CSV de SERCOP. Las primeras ejecuciones se acumularon en los dos archivos históricos; para conservarlos, el script actual crea un CSV nuevo por ejecución y rechaza rutas existentes.

### Cierre controlado del criterio de cuota, 15/10/2026

El [manual oficial de la API](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api),
se consultó nuevamente el 15/10/2026. La página muestra «Fecha de
actualización: 14/10/2026» y continúa sin publicar cantidad, periodo o ámbito
de la cuota.

Se ejecutó una sola muestra con el esquema v3, sin consultas auxiliares ni
reintentos (`run_id=95428e1f-807a-4dc5-b0e2-dabcb8d3fdae`). Respondió HTTP
200 y anunció `X-RateLimit-Limit: 60` y `X-RateLimit-Remaining: 0`. No envió
`RateLimit-Policy`, cabecera de ventana, reinicio o `Retry-After`; tampoco hubo
redirección, error local ni evidencia de caché compartida. El script respetó
el margen y terminó después de esa única solicitud.

La evidencia acumulada permite cerrar el criterio en el sentido literal del
issue —límites **observados**— con esta delimitación:

| Aspecto | Conclusión sustentada | Límite de la conclusión |
|---|---|---|
| Cantidad | El servidor anuncia un límite de 60 mediante `X-RateLimit-Limit` | No equivale a 60 solicitudes disponibles exclusivamente para este cliente |
| Ventana observable | Dos reinicios anunciados consecutivos del 11/10/2026 quedaron separados por 61 segundos; se documenta como una cadencia aproximada de un minuto | No identifica una ventana fija o deslizante ni constituye una garantía contractual |
| Ámbito | La caída de `Remaining` de 15 a 0 entre dos solicitudes del script, y el HTTP 200 con restantes 0 del 15/10/2026, no concuerdan con un contador simple y exclusivo | SERCOP no publica si el contador se comparte por IP, endpoint, portal o infraestructura |

Para el proyecto, la descarga masiva sigue siendo la vía preferida. Si una
fase posterior usa la API, debe serializar solicitudes, detenerse al alcanzar
el margen y, ante HTTP 429, respetar `Retry-After` sin interpretar
`X-RateLimit-Reset` como una duración. Un cambio futuro de la política del
proveedor exigiría una observación nueva; no reabre la evidencia histórica de
este issue.

**Primer intento real con v3:** el 11/10/2026 a las 20:02:40 de Ecuador
(`request_started_utc=2026-10-12T01:02:40.3959572+00:00`) se ejecutó una sola
muestra, con `run_id=9d609acf-6a81-417f-aebd-1064cc78e2b5`. El cliente no
capturó respuesta y registró `System.Net.Sockets.SocketException`; no hay
estado HTTP, hora de recepción ni cabeceras. El script se detuvo y no
programó reintentos. Esto documenta un fallo de transporte, no un 429, una
caída confirmada de SERCOP ni ausencia de política de cuota. Los campos de
configuración del cliente sí constan en el CSV. No procede programar la
captura de recuperación porque no se recibió `Retry-After`. Antes de un nuevo
intento hay que comprobar la conectividad del entorno hacia el sitio oficial,
sin consultar repetidamente el endpoint.

La descarga masiva comprobada permite avanzar sin depender del contador opaco
de la API. La captura fallida se conserva como evidencia histórica y no se usa
para el cierre del criterio.

**Resultado de los intentos de contacto:** el líder envió una consulta desde
su correo institucional de la EPN el 11/10/2026. El servidor rechazó el
destinatario histórico `diego.benavides@sercop.gob.ec` con `550 5.1.1` y
`554 5.5.1`; la consulta no fue entregada y eso no constituye una respuesta
técnica. Gestión Documental respondió después que su correo es exclusivo para
recibir oficios y remitió las consultas generales al chat de SERCOP, la
atención presencial y los canales de denuncias o reclamaciones. El 15/10/2026,
el navegador rechazó la conexión segura al chat porque el certificado de
`asesorvirtual.sercop.gob.ec` aparecía vencido desde hacía 985 días. No se
omitió la advertencia ni se enviaron datos por una conexión insegura. Por
tanto, el proyecto no espera una confirmación técnica de SERCOP para cerrar
#9: conserva la falta de política publicada como limitación y trabaja con la
evidencia externa observada.

## Conclusiones para el proyecto

1. Hay descarga masiva en tres formatos y una API con búsqueda por palabra clave y consulta por `ocid`.
2. El portal transforma y publica datos de más de una fuente primaria; no se debe asumir que todo registro procede únicamente de SOCE.
3. El buscador abarca entidades fuera del alcance del DW, así que antes de usar totales debe definirse cómo identificar la planta central y sus entidades dependientes.
4. Se midió el tamaño comprimido del JSON anual y se observaron propiedades de respuestas API reales. El servidor anunció un límite de 60 y dos reinicios consecutivos quedaron separados por 61 segundos, por lo que se documenta una ventana observable cercana a un minuto. La recuperación de `Remaining` de 0 a 58 quedó confirmada, pero el contador no se comportó como exclusivo del cliente y su ámbito no está publicado. Esta limitación afecta a la planificación de consultas por API; no impide usar la descarga masiva, cuyos límites y contenido se comprueban por separado.
5. El líder descargó el ZIP mensual de enero de 2025. Se verificaron su hash, su estructura JSON y los conteos descritos arriba: 2.186 releases con 2.186 `ocid` distintos. La inspección permite avanzar por la vía masiva, pero no fija el periodo definitivo de la foto ni garantiza todavía la cobertura necesaria. No se espera una confirmación técnica de SERCOP para continuar; cualquier política publicada en el futuro se contrastará como evidencia nueva.
6. La descarga anual de 2025 fue leída localmente y contiene 190.619 `ocid` distintos, coincidentes con el contador de la interfaz. Se midieron 160.930.685 bytes comprimidos y 1.721.952.613 bytes sin comprimir; la lectura por partes tardó 22,092 segundos en la ejecución del líder. Esto demuestra que la vía masiva permite obtener y recorrer este archivo anual en su equipo. El periodo definitivo, la clasificación de entidades, el formato final de la foto y las reglas de negocio siguen pendientes de sus decisiones y fases correspondientes.

## Estado de los criterios del issue #9

| Criterio | Estado de la evidencia |
|---|---|
| Formas de descarga y enlaces | Documentado: descarga masiva y API |
| Campos reales separados de supuestos | Documentado: respuesta de búsqueda y estructura anidada de las descargas |
| Volumen de al menos un año | Medido: ZIP anual 2025, tamaños y 190.619 `ocid` distintos |
| Cantidad de peticiones y ventana de la API | Documentado: límite anunciado de 60 y cadencia observable cercana a un minuto entre reinicios; el ámbito interno no publicado queda expresamente fuera de la conclusión |
| Documento con evidencia mínima, sin datasets completos | Documentado: documento, resúmenes y CSV de cabeceras; ZIP y datos originales ignorados por Git |

Los cinco criterios de aceptación tienen evidencia. El cierre de #9 no afirma
una política contractual ni un contador exclusivo: registra el comportamiento
externo observado y sus límites. El issue se cerró el 15/10/2026 al integrarse
el PR #24.
