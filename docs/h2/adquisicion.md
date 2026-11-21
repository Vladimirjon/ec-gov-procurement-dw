# Adquisición de datos de SERCOP (2021–2025)

Documento de verificación y procedencia de la descarga masiva anual de SERCOP (OCDS) para la ventana 2021–2025, conforme a la guía del Hito 2 (secciones 4.1 y 5) y el Issue #59.

## 1. Procedencia y datos descargados

Las descargas se obtuvieron el 21 de noviembre de 2026 desde el portal oficial de datos abiertos del SERCOP mediante la descarga masiva anual (filtro: todos los meses y todos los tipos de contratación).

- **Fuente:** Servicio Nacional de Contratación Pública (SERCOP) — Portal de Datos Abiertos.
- **Patrón de enlace:** `https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=json&year=AAAA&month=0&method=all`
- **Licencia:** Creative Commons Atribución 3.0 Ecuador (CC BY 3.0 EC), declarada en los metadatos de los paquetes OCDS.
- **Ubicación local de los crudos:** `data/datos_crudos/` en la raíz del repositorio principal (carpeta ignorada por Git; archivos marcados como de solo lectura).
- **Registro de procedencia:** `docs/h2/evidencia/descargas-sercop.csv` (versionado en Git, sin contener datos de registros).

## 2. Verificación de integridad por archivo

Cada archivo fue recibido mediante una única petición GET directa (sin cookies y sin seguir redirecciones automáticas). Se verificó que los bytes recibidos coincidieran exactamente con el valor anunciado en la cabecera `Content-Length` de la misma respuesta HTTP, y se calculó el hash SHA-256 en modo streaming.

| Año | Archivo | Tamaño (bytes) | Content-Length | Estado HTTP | Hash SHA-256 | Fecha y hora (Ecuador UTC-5) |
|:---:|---|:---:|:---:|:---:|---|:---:|
| **2021** | `releases_2021.zip` | 121.106.938 | 121.106.938 | 200 OK | `FDBFD26FF23848BFE600021DC82C7BCE296D1E8CB130E71F520A6B8AA312976C` | 21/11/2026 11:58:39 |
| **2022** | `releases_2022.zip` | 163.854.175 | 163.854.175 | 200 OK | `359A87C2BFB051D9717E681F81BFCB7EA009E03E141E9E65B155A602313DA1FB` | 21/11/2026 12:08:10 |
| **2023** | `releases_2023.zip` | 147.577.990 | 147.577.990 | 200 OK | `2D1EBF54A355F6FF61066E70485B8EB7836F316F309FA2B8ED42E655380972F6` | 21/11/2026 12:14:38 |
| **2024** | `releases_2024.zip` | 160.292.192 | 160.292.192 | 200 OK | `7DAEA57B70E1F2BA0B566E3776519C8BEEFE3FA6C64570ED108090A307F5D20C` | 21/11/2026 12:15:36 |
| **2025** | `releases_2025.zip` | 161.134.697 | 161.134.697 | 200 OK | `392845D71455A2EF687A1E77BC0461DFEEDBBBFBD70F389E6A8E8AE305503BEF` | 21/11/2026 12:47:38 |

**Total descargado:** 753.966.992 bytes (~754 MB).

## 3. Conteo de releases y comparación con el portal

La integridad interna de cada ZIP fue comprobada mediante lectura del archivo JSON contenido con `scripts/profile_sercop_fields.py` (sin modificar el script oficial de reconocimiento). Se obtuvieron los siguientes totales de paquetes y releases OCDS:

| Año | Entrada JSON interna | Paquetes | Releases | Anomalías detectadas | Contador del portal / Observación H1 |
|:---:|---|:---:|:---:|---|---|
| **2021** | `releases_2021.json` | 167.058 | 167.058 | Ninguna | Base de datos histórica cerrada (2021). |
| **2022** | `releases_2022.json` | 212.324 | 212.324 | Ninguna | Primera medición del periodo 2022. |
| **2023** | `releases_2023.json` | 217.914 | 217.913 | Ninguna | 1 paquete con 0 releases (diferencia de 1). |
| **2024** | `releases_2024.json` | 219.186 | 219.185 | 1 anomalía en `contracts` | 1 release con `contracts` como objeto en vez de lista (anomalía documentada en `docs/sources/reconocimiento.md`). |
| **2025** | `releases_2025.json` | 191.440 | 191.440 | Ninguna | Comparación: el portal mostró 190.619 al 11/10/2026. La diferencia (+821 procedimientos) corresponde a la actualización continua del portal entre octubre y noviembre de 2026. |

**Total de releases en la ventana 2021–2025:** 1.007.920 releases.

## 4. Estado de la evidencia cruda

1. Los archivos `.zip` descargados residen exclusivamente en `data/datos_crudos/` dentro de carpetas fechadas al segundo.
2. Cada carpeta contiene su archivo de cabeceras HTTP limpias (`headers-AAAA.txt`), sin almacenar cookies de sesión.
3. Se aplicó el atributo de solo lectura (`IsReadOnly = true`) sobre los ZIPs y cabeceras para prevenir alteraciones accidentales.
4. `.gitignore` garantiza que la carpeta `data/` completa queda fuera del control de versiones de Git.
