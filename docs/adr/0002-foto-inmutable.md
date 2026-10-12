# ADR 0002: La foto de datos es inmutable

- **Estado:** Propuesto (borrador)
- **Fecha:** 2026-10-06
- **Decide:** líder del equipo
- **Referencias:** [PROPUESTA.md](../PROPUESTA.md), secciones 3 (D1), 4 y 10

**Decidido (D1):** el equipo toma la foto del portal de datos abiertos de
contratación pública de SERCOP (formato OCDS). No la entrega nadie más.

## Contexto

El proyecto trabaja sobre una foto (snapshot) de los datos de contratación. El
curso pide carga batch e incremental, pruebas reproducibles y validación
cruzada con las fuentes originales (semana 4). Para que los resultados sean
reproducibles y verificables, todo lo que se derive de la foto debe poder
regenerarse desde ella.

## Decisión

1. **La foto es evidencia.** Una vez registrada, nunca se modifica ni se
   sobrescribe. Una corrección o una captura nueva es una foto distinta, con
   su propio identificador.
2. **Manifiesto de checksums.** Cada foto tiene un manifiesto con el checksum
   de cada archivo, para verificar su integridad antes de cada carga.
3. **Fuera de git.** La foto vive en `data/` (ignorado por git). En el
   repositorio solo se versionan el manifiesto y fixtures mínimos y
   sintéticos.
4. **Todo lo derivado es regenerable.** Los esquemas `stg`, `dw` y `rpt` se
   pueden reconstruir completos desde la foto.
5. **Carga batch:** carga inicial completa de la foto.
6. **Carga incremental:** por particiones de fecha sobre la misma foto, con
   una marca de control (`batch_id`, fecha de corte). Así se demuestra la
   carga incremental aunque la fuente sea una foto fija.
7. **Detección de cambios:** clave natural (`ocid`) más un hash del contenido
   del registro.
8. **Reconciliación:** después de cada carga se comparan conteos y sumas de
   monto entre foto, staging y DW.

## Pendiente

| Tema | Estado | Quién lo resuelve |
|---|---|---|
| Periodo de la foto (uno o más años) | **[PENDIENTE]** tras medir el volumen por año | Líder |
| Cómo se obtiene: descarga masiva por año o extracción por API | Descarga masiva JSON anual comprobada en el reconocimiento; decisión final **[PENDIENTE]** | Rol 1 (fuente y foto) |
| Límite de peticiones de la API | Observado `X-RateLimit-Limit: 60`; ventana y ámbito del contador **[PENDIENTE]**. Evidencia en `docs/sources/reconocimiento.md` | Rol 1 |
| Formato de almacenamiento: Parquet o JSON | **[PENDIENTE]** | Líder |
| Contenido del manifiesto, algoritmo de checksum y ubicación en el repo | **[PENDIENTE]** | Líder |
| Tamaño de la partición incremental (la propuesta da "mes a mes" como ejemplo) | **[PENDIENTE]** | Equipo |
| Que `ocid` sea único por proceso dentro de una foto | Verificado en la descarga anual de reconocimiento 2025: 190.619 releases y 190.619 `ocid` distintos. Repetir la comprobación en cada foto definitiva | Rol 1 |
| Campos usados en el hash de contenido | **[PENDIENTE]** tras reconocer la fuente | Roles 1 y 3 |

### Evidencia disponible; decisiones aún pendientes

La [inspección anual](../sources/reconocimiento.md#inspección-del-zip-anual-json)
del 11/10/2026 mide 160.930.685 bytes comprimidos, 1.721.952.613 bytes sin
comprimir y 190.619 procesos distintos. El ZIP está en `data/reconnaissance/`,
ignorado por Git. Es evidencia para decidir, no una aprobación del periodo,
formato, manifiesto ni de este ADR completo. El resumen de inspección registra
hashes y conteos; el manifiesto de la foto definitiva sigue pendiente.

Según el plan, el líder decide el periodo en la fase 1 (issue #15); la toma
formal de la foto y su manifiesto se realiza al inicio de la fase 2.

## Consecuencias

- Ningún proceso de carga escribe en la carpeta de la foto.
- La extracción (`extract`, `snapshot`) queda separada de la carga (`load`):
  la carga solo lee fotos verificadas por su manifiesto.
- Si la API limita las peticiones, se toma una foto única, con ritmo
  conservador y reintentos con espera, en lugar de repetir extracciones.
- Los datos no se pueden compartir por git; cada integrante necesita acceso a
  la foto por un medio aparte. **[PENDIENTE]** Definir ese medio.
