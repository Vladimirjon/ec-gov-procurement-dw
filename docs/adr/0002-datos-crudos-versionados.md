# ADR 0002: Datos crudos versionados y cargas reproducibles

- **Estado:** Aceptado
- **Fecha:** 2026-11-03 (reemplaza «La foto de datos es inmutable», 2026-10-06)
- **Decide:** líder del equipo
- **Referencias:** guía del proyecto, secciones 5 y 7 (Hito 2) y 10

## Contexto

La guía del profesor pide que `stg` sea una copia cruda y versionada de cada
fuente, sin transformar, con fecha de carga. También pide guardar la fecha de
descarga de cada archivo, porque los portales abiertos cambian, y exige que
cada fuente se cite con enlace, fecha de descarga y licencia. El portal de
SERCOP actualiza las descargas a diario y el tamaño de un mismo archivo anual
difirió entre dos consultas, así que una descarga es una captura en un momento
dado.

## Decisión

1. **Los archivos descargados son evidencia.** Se guardan fuera de git, en
   `data/`. Nunca se modifican ni se sobrescriben. Una nueva descarga es una
   versión nueva, con su propia fecha.
2. **Registro de descargas.** Cada archivo tiene su URL, fecha de descarga,
   tamaño y SHA-256. El registro (sin datos) sí se versiona en el repositorio.
3. **`stg` es la copia cruda.** Conserva los campos de las fuentes sin
   transformarlos y con la fecha de carga. Solo se cargan los campos que
   responden las preguntas de negocio. No se cargan los datos de contacto de
   personas.
4. **Todo lo derivado se regenera** desde `stg`: el esquema `dw` se puede
   reconstruir completo con un solo comando.
5. **Carga inicial e incremental.** La inicial carga todo el periodo. La
   incremental carga por partición mensual, con `batch_id` y fecha de corte.
6. **Detección de cambios:** clave natural (`ocid`) más un hash del contenido.
7. **Idempotencia y bitácora.** Repetir una carga no duplica datos. Cada carga
   registra filas leídas, cargadas y rechazadas en el esquema `audit`.
8. **Reconciliación.** Tras cada carga se comparan conteos y sumas de monto
   entre la fuente, `stg` y `dw`, y se explican las diferencias.
9. **Dimensiones antes que hechos** en cada carga.

## Pendiente

| Tema | Quién | Cuándo |
|---|---|---|
| Formato de almacenamiento de los archivos (JSON original o convertido) | Líder | Hito 2 |
| Campos usados en el hash de contenido | Roles de ingeniería de datos | Hito 2 |
| Verificar que `ocid` es único por proceso en los años 2021–2024 (en 2025 hay 190.619 releases y 190.619 `ocid` distintos) | Líder | Hito 2 |
| Cómo comparten el equipo los archivos, que están fuera de git | Líder | Hito 2 |

## Consecuencias

- Ningún proceso de carga escribe en `data/`.
- Los datos no se comparten por git. Hay que definir un medio aparte.
- Los archivos de un año completo son grandes (el JSON de 2025 pesa unos 1,7 GB
  sin comprimir), y no se midió aún el tamaño de 2021 a 2024.
