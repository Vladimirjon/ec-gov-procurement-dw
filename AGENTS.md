# Instrucciones del repositorio

Proyecto universitario de Data Warehouse (HEFESTO + Kimball) sobre contratación
pública de la planta central del Estado ecuatoriano: Presidencia de la
República, ministerios e institutos que dependen de los ministerios. Los GAD
y sus empresas están fuera de alcance. Es académico e independiente; no tiene
relación con SERCOP ni con ninguna entidad.

## Estado actual
El repositorio está en fase de preparación: solo hay esqueleto de carpetas y
documentación. No hay código, dependencias, base de datos, pruebas ni CI. No
afirmes ni documentes funcionalidad que no exista.

## Orden de lectura
README.md, docs/adr/, docs/design/ y la propuesta de arquitectura
(docs/PROPUESTA.md) antes de cambiar nada.

## Límites
- La foto de datos es evidencia: nunca se modifica ni se sobrescribe.
- `extract` y `snapshot` no conocen el DW; `load` no conoce la API de la
  fuente; `quality` no depende de Power BI.
- Carga siempre dimensiones antes que hechos. Toda carga es idempotente y
  deja bitácora de filas cargadas y rechazadas.
- Los tableros solo leen vistas del esquema `rpt`.
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
Código y nombres técnicos en inglés. Documentos de entrega en español
(sujeto a la decisión D4). Commits con Conventional Commits. El flujo de
trabajo del equipo está en CONTRIBUTING.md.
