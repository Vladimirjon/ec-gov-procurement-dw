# Hito 2: adquisición y calidad de datos

Esta carpeta reúne la documentación del Hito 2 que sí se versiona: lo que se puede
leer sin abrir los archivos crudos y sin datos de personas. Los ZIP descargados
viven fuera de Git, en `data/datos_crudos/` de la carpeta principal (ignorada),
porque son evidencia local y pesan cientos de MB.

## Contenido

| Ruta | Qué contiene |
|---|---|
| `evidencia/descargas-sercop.csv` | Una fila por ZIP anual descargado: año, URL exacta, estado HTTP, fecha y hora de la descarga en hora de Ecuador, bytes recibidos, `Content-Length` de la misma respuesta, SHA-256, nombre del archivo, carpeta y licencia. Lo escribe `scripts/download_sercop_ocds.ps1`; no lleva valores de registros. |
| `adquisicion.md` | Qué se descargó, cómo se verificó la integridad de cada ZIP, el número de releases por año y su comparación con el contador del portal. |

## De dónde sale

- Guía del profesor del Hito 2, secciones 4.1 y 5, pasos 1 y 2: los archivos
  originales se guardan sin modificar en una carpeta «datos_crudos».
- Issue #59 (H2-01) del repositorio: encargo, salidas y criterios de aceptación.
- Patrón de enlace y licencia: `docs/sources/reconocimiento.md`.
