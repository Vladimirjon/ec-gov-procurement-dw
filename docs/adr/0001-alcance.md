# ADR 0001: Alcance del Data Warehouse

- **Estado:** Propuesto (borrador)
- **Fecha:** 2026-10-06
- **Decide:** líder del equipo
- **Referencias:** [PROPUESTA.md](../PROPUESTA.md), secciones 1, 2, 3 y 10

## Contexto

El profesor asignó el sector **Gobierno y Ministerio**, entendido como la
planta central del Estado ecuatoriano. Se espera cubrir toda la planta central,
no una muestra de entidades, y trabajar sobre una foto (snapshot) de los datos.
La fuente prevista es el portal de datos abiertos de contratación pública de
SERCOP (formato OCDS).

No se asume que la fuente indique qué entidades pertenecen a la planta
central, por lo que el alcance no se puede aplicar con un simple filtro de la
fuente.

## Decisión

1. **Entidades dentro del alcance:**
   - Presidencia de la República.
   - Ministerios.
   - Institutos que dependen de los ministerios.
2. **Cobertura:** toda la planta central, no una muestra.
3. **Periodo:** una foto fija de uno o más años.
4. **Fuera del alcance:**
   - GAD de cualquier nivel (provincial, cantonal, parroquial) y sus
     empresas. Por ejemplo, empresas municipales como la Empresa Eléctrica
     Quito.
   - Cualquier otra entidad fuera de la planta central.
   - Ingesta continua o en tiempo real.
   - Microservicios, Kafka, Kubernetes y autenticación de usuarios finales.
   - Datos personales más allá de lo que la fuente ya publica.
5. **Clasificación de entidades:** se construye una tabla de clasificación a
   partir de una fuente oficial y se versiona en el repositorio como semilla.
   Atributos previstos: entidad, tipo, ministerio del que depende, sector y
   nivel. Cada entidad se resuelve en exactamente una categoría:
   - Presidencia
   - Ministerio
   - Instituto dependiente de un ministerio
   - Fuera de alcance
6. **Casos dudosos** (por ejemplo, entidades adscritas con régimen propio): se
   registran junto a la semilla con su justificación y los decide el líder.
   Mientras no se resuelvan, no se incluyen en los indicadores.

## Pendiente

| Tema | Estado | Quién lo resuelve |
|---|---|---|
| Fuente oficial para la clasificación de entidades | **[PENDIENTE]** | Rol 5 propone, líder aprueba |
| Criterios de inclusión de entidades | **[PENDIENTE]** | Líder |
| Casos dudosos concretos | **[PENDIENTE]** al construir la semilla | Líder |
| Periodo de la foto (ver ADR 0002) | **[PENDIENTE]** tras reconocer la fuente | Líder |
| Atributo de la fuente que identifica a la entidad compradora | **[PENDIENTE]** verificar en `docs/sources/` | Rol 1 (fuente y foto) |

La regla 6 (excluir casos dudosos de los indicadores hasta resolverlos) es una
propuesta de este borrador y también requiere aprobación.

## Consecuencias

- La semilla de clasificación es un artefacto de primer nivel: sin ella no se
  puede filtrar el alcance ni construir la jerarquía Presidencia > ministerio >
  instituto dependiente.
- Los cambios de nombre, fusiones o cambios de ministerio de una entidad se
  modelan en `dim_entity` (SCD tipo 2, ver la sección 5 de la propuesta).
- Cualquier ampliación o reducción del alcance requiere un ADR nuevo y la
  aprobación del líder.
