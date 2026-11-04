# Instrucciones del repositorio

Proyecto universitario de Data Warehouse (HEFESTO + Kimball) sobre contratación
pública del gobierno central del Ecuador: Presidencia de la República,
ministerios e institutos que dependen de ellos (sector completo). Los GAD y
sus empresas están fuera de alcance. Es académico e independiente; no tiene
relación con SERCOP ni con ninguna entidad.

## Estado actual
Hito 1 en curso. El repositorio tiene documentación, esqueleto de carpetas y
scripts auxiliares de reconocimiento en `scripts/`. No hay ETL del DW,
dependencias declaradas, base de datos, suite de pruebas ni CI. Las descargas
locales de reconocimiento no constituyen todavía la carga definitiva del
periodo.
No afirmes ni documentes funcionalidad que no exista.

## Instrucciones vigentes
Mandan los dos PDF del profesor (guía del proyecto y guía del Hito 1), en
`Instrucciones_Curso/` (local). El plan por fases anterior y sus entregables
(E0, F1 a F5) ya no rigen. Resumen y estado en docs/requisitos-del-profesor.md
y docs/PLAN.md. Si algo de este repositorio contradice un PDF, manda el PDF.

## Orden de lectura
docs/PLAN.md, docs/requisitos-del-profesor.md, README.md y docs/adr/ antes de
cambiar nada. Los ADR de docs/adr/ son las decisiones vigentes.

## Límites
- Los archivos descargados son evidencia: nunca se modifican ni se
  sobrescriben; una nueva descarga es otra versión.
- `extract` no conoce el DW; `load` no conoce la API de la
  fuente; `quality` no depende de Power BI.
- Carga siempre dimensiones antes que hechos. Toda carga es idempotente y
  deja bitácora de filas cargadas y rechazadas.
- Los tableros leen solo del esquema `dw` (las vistas de reporte viven ahí);
  nunca de `stg` ni de la fuente.
- No inventes campos, endpoints ni comportamientos de la fuente. Usa solo lo
  observado y documentado en docs/sources/ o fixtures aprobados.

## Seguridad y datos
- No incluyas secretos, credenciales ni datasets completos en código, prompts,
  logs, pruebas ni documentación.
- Usa fixtures mínimos y sintéticos.

## Cambios que requieren aprobación del líder
Nuevas dependencias, nueva infraestructura o servicios, cambios de alcance o
de arquitectura, y cualquier decisión marcada como [CONFIRMAR] o [PENDIENTE].

## Verificación
Ejecuta las pruebas y el linter relevantes después de cada cambio y reporta el
resultado real, incluidos los fallos. Mientras no estén configurados, dilo
explícitamente en lugar de dar el cambio por verificado.

## Convenciones
Código y nombres técnicos en inglés. Documentos de entrega en español.
Commits con Conventional Commits. El flujo de
trabajo del equipo está en CONTRIBUTING.md.
