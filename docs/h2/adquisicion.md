# Adquisición de datos de SERCOP (2021–2025)

Documento de verificación y procedencia de la descarga masiva anual de SERCOP (OCDS) para la ventana 2021–2025, conforme a la guía del Hito 2 (secciones 4.1 y 5) y el Issue #59.

## 1. Procedencia y datos descargados

Las descargas se obtuvieron el 21 de noviembre de 2026 desde el portal oficial de datos abiertos del SERCOP mediante la descarga masiva anual (filtro: todos los meses y todos los tipos de contratación).

- **Fuente:** Servicio Nacional de Contratación Pública (SERCOP) — Portal de Datos Abiertos.
- **Patrón de enlace:** `https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=json&year=AAAA&month=0&method=all`
- **Licencia:** Creative Commons Atribución 3.0 Ecuador (CC BY 3.0 EC), declarada en los metadatos de los paquetes OCDS.
- **Ubicación local de los crudos:** `data/datos_crudos/` en la raíz del repositorio principal (carpeta ignorada por Git; archivos marcados como de solo lectura).
- **Registro de procedencia:** `docs/h2/evidencia/descargas-sercop.csv` (versionado en Git, sin contener datos de registros, con rutas relativas a la raíz del repositorio).
- **User-Agent:** Las peticiones enviaron una cabecera `User-Agent` de navegador (Google Chrome sobre Windows) para evitar que el servidor web del SERCOP cierre o interrumpa la conexión durante la transferencia de archivos de gran volumen (~120 a 160 MB cada uno). No se consultó ni se superó ningún límite de uso documentado; en 2025 el script sufrió un corte de conexión cuya causa no se determinó.

## 2. Verificación de integridad por archivo

Los archivos correspondientes a los años **2021 a 2024** se descargaron con el script `scripts/download_sercop_ocds.ps1` mediante una única petición GET directa por año (utilizando `HttpClient` de .NET, sin cookies y sin seguir redirecciones automáticas), calculando el hash SHA-256 en modo streaming y verificando que los bytes recibidos coincidieran exactamente con el valor anunciado en la cabecera `Content-Length` de la misma respuesta HTTP.

El archivo del año **2025** no fue descargado por dicho script, sino mediante `curl` (`curl.exe` con volcado de cabeceras `-D headers-2025.txt` y salida directa al archivo `releases_2025.zip`). El motivo: el script en PowerShell sufrió una interrupción de conexión durante la transferencia de los 161 MB de 2025 desde el portal de SERCOP; para asegurar la descarga completa sin nuevos cortes de buffer se recurrió a `curl` en terminal. Por esta razón, `headers-2025.txt` contiene el volcado crudo emitido por `curl` (que incluye la cabecera `Docker-Distribution-Api-Version: backend` duplicada por el servidor upstream y un orden de cabeceras distinto al estructurado por .NET `HttpClient`), y su fila en `docs/h2/evidencia/descargas-sercop.csv` se completó a mano con horas aproximadas (por ello sus marcas de tiempo terminan en `.0000000`). No obstante, los bytes recibidos (161.134.697), el `Content-Length` (161.134.697) y el hash SHA-256 (`392845D71455A2EF687A1E77BC0461DFEEDBBBFBD70F389E6A8E8AE305503BEF`) fueron recalculados en una revisión independiente el 21/11/2026 (modelo Claude Sonnet 5.5), confirmando que son los valores reales y que coinciden con el archivo preservado.

| Año | Archivo | Tamaño (bytes) | Content-Length | Estado HTTP | Hash SHA-256 | Fecha y hora (Ecuador UTC-5) | Método |
|:---:|---|:---:|:---:|:---:|---|:---:|---|
| **2021** | `releases_2021.zip` | 121.106.938 | 121.106.938 | 200 OK | `FDBFD26FF23848BFE600021DC82C7BCE296D1E8CB130E71F520A6B8AA312976C` | 21/11/2026 11:58:39 | Script PowerShell |
| **2022** | `releases_2022.zip` | 163.854.175 | 163.854.175 | 200 OK | `359A87C2BFB051D9717E681F81BFCB7EA009E03E141E9E65B155A602313DA1FB` | 21/11/2026 12:08:10 | Script PowerShell |
| **2023** | `releases_2023.zip` | 147.577.990 | 147.577.990 | 200 OK | `2D1EBF54A355F6FF61066E70485B8EB7836F316F309FA2B8ED42E655380972F6` | 21/11/2026 12:14:38 | Script PowerShell |
| **2024** | `releases_2024.zip` | 160.292.192 | 160.292.192 | 200 OK | `7DAEA57B70E1F2BA0B566E3776519C8BEEFE3FA6C64570ED108090A307F5D20C` | 21/11/2026 12:15:36 | Script PowerShell |
| **2025** | `releases_2025.zip` | 161.134.697 | 161.134.697 | 200 OK | `392845D71455A2EF687A1E77BC0461DFEEDBBBFBD70F389E6A8E8AE305503BEF` | 21/11/2026 12:47:38 | curl (horas aprox.) |

**Total descargado:** 753.966.992 bytes (~754 MB).

## 3. Conteo de releases y comparación con el portal

La integridad interna de cada ZIP fue comprobada mediante lectura del archivo JSON contenido con `scripts/profile_sercop_fields.py` (sin modificar el script oficial de reconocimiento). Se obtuvieron los siguientes totales de paquetes y releases OCDS:

| Año | Entrada JSON interna | Paquetes | Releases | Anomalías detectadas | Contador del portal (21/11/2026) / Observación H1 |
|:---:|---|:---:|:---:|---|---|
| **2021** | `releases_2021.json` | 167.058 | 167.058 | Ninguna | Portal: 167.058 procedimientos publicados (consultado el 21/11/2026) |
| **2022** | `releases_2022.json` | 212.324 | 212.324 | Ninguna | Portal: 212.324 procedimientos publicados (consultado el 21/11/2026) |
| **2023** | `releases_2023.json` | 217.914 | 217.913 | 1 paquete con 0 releases (diferencia de 1) | Portal: 217.914 procedimientos publicados (consultado el 21/11/2026) |
| **2024** | `releases_2024.json` | 219.186 | 219.185 | 1 anomalía en `contracts` (1 release con contracts como objeto en vez de lista, según `reconocimiento.md`) | Portal: 219.186 procedimientos publicados (consultado el 21/11/2026) |
| **2025** | `releases_2025.json` | 191.440 | 191.440 | Ninguna | Comparación con H1: el portal reportó 190.619 al 11/10/2026 frente a 191.440 actuales (+821 procedimientos; actualización continua del portal). Portal: 191.440 procedimientos publicados (consultado el 21/11/2026). |

**Total de releases en la ventana 2021–2025:** 1.007.920 releases.

**Nota (inferencia, no afirmación del portal):** el contador del portal ("Procedimientos de Contratación Publicados", anotado por el líder desde la pantalla el 21/11/2026) coincide exactamente con el número de **paquetes** de cada ZIP en los cinco años; difiere en 1 del número de **releases** en 2023 y 2024 (1 paquete sin releases y 1 release con `contracts` como objeto, ya descritos arriba). No es una diferencia de descarga y no se corrige nada.

## 4. Estado de la evidencia cruda

1. Los archivos `.zip` descargados residen exclusivamente en `data/datos_crudos/` dentro de subcarpetas fechadas al segundo (con rutas relativas en la evidencia).
2. Cada carpeta contiene su archivo de cabeceras HTTP limpias (`headers-AAAA.txt`), sin almacenar cookies de sesión.
3. Se aplicó el atributo de solo lectura (`IsReadOnly = true`) sobre los ZIPs y cabeceras para prevenir alteraciones accidentales.
4. `.gitignore` garantiza que la carpeta `data/` completa queda fuera del control de versiones de Git.

## 5. Cómo se probó el script

Antes de realizar las descargas de producción, el comportamiento del script `scripts/download_sercop_ocds.ps1` fue evaluado mediante un arnés de pruebas sintéticas locales en PowerShell (`run-download-tests.ps1`, 27 aserciones) contra un servidor HTTP sintético en Python (`mockserver.py`):

1. **Casos evaluados:**
   - **Caso 1 (Descarga exitosa, HTTP 200):** Verifica la finalización con código de salida 0, creación de una carpeta única fechada, guardado del ZIP y del archivo de cabeceras sin cookies (`Set-Cookie` filtrado), coincidencia exacta de bytes recibidos contra `Content-Length`, registro de la fila correspondiente en el CSV de evidencia (con ruta relativa y SHA-256) y aplicación del atributo de solo lectura (`IsReadOnly = true`).
   - **Caso 2 (Discrepancia en `Content-Length`):** Un servidor simulado anuncia en cabecera 100 bytes más que los transferidos en el cuerpo. Verifica que el script falle con código de salida distinto de 0, emita el mensaje de error de discrepancia, registre en el CSV tanto el tamaño anunciado como el real, y preserve el archivo incompleto en disco como evidencia de auditoría sin descartarlo.
   - **Caso 3 (Error HTTP distinto de 200):** Simula una respuesta HTTP 404 Not Found. Verifica que el script falle con código de salida distinto de 0, registre el estado HTTP 404 en el CSV, conserve las cabeceras de respuesta y no guarde un ZIP inválido con el cuerpo de error.
   - **Caso 4 (Carpeta de destino preexistente):** Verifica que si ya existe una subcarpeta con el mismo nombre y segundo en el destino, el script aborte de inmediato por colisión sin iniciar la descarga ni sobrescribir archivos existentes.

2. **Alcance y límites de las pruebas sintéticas:**
   - **Qué cubren:** La lógica de control de flujo del script, la validación estricta de integridad HTTP, el filtrado de cookies, el registro de evidencia en el CSV con rutas relativas y la protección contra sobrescritura.
   - **Qué no cubren:** Las condiciones reales de red pública (latencia, fluctuaciones de ancho de banda, caídas de socket TCP o reinicios forzados por el servidor de SERCOP durante transferencias prolongadas de más de 100 MB).
   - **Ubicación del arnés:** El arnés de pruebas sintéticas (`run-download-tests.ps1`, `mockserver.py`) vive fuera del repositorio (en la carpeta temporal de OpenCode), por lo que no existen pruebas automáticas de PowerShell integradas en el pipeline de CI del repositorio (el CI valida el entorno Python con `ruff` y `pytest`). No se utilizan rutas absolutas para referenciarlo.

3. **Prueba real contra el portal:**
   La validación funcional en el entorno real de SERCOP se llevó a cabo con la descarga del año **2021** (primer archivo de la ventana descargado en producción, 121.106.938 bytes, HTTP 200, validando el comportamiento del portal y registrando las cabeceras reales).
