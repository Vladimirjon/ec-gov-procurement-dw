# ADR 0001: Alcance del Data Warehouse

- **Estado:** Propuesto (borrador)
- **Fecha:** 2026-10-06
- **Decide:** líder del equipo
- **Referencias:** [PROPUESTA.md](../PROPUESTA.md), secciones 1, 2, 3 y 10;
  [entidades.md](../sources/entidades.md)

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
7. **Entidad compradora y regla de cruce:** la entidad compradora se identifica
   con `buyer.id` de la fuente. En OCDS, `buyer.id` es la referencia a una
   organización y puede incluir un sufijo de unidad; no se trata como
   sinónimo del RUC. La clasificación se asigna en este orden:
   1. Unión exacta por `buyer.id` completo, conservado sin modificar.
   2. Si no hay coincidencia exacta, correspondencia por la raíz
      `EC-RUC-{13 dígitos}`, solo si el patrón fue validado en la semilla.
   3. Nunca por `buyer.name`.

   Se aplica la clasificación vigente en la fecha del proceso (SCD tipo 2 en
   `dim_entity`). `tender.procuringEntity.id` se conserva como unidad
   contratante y no es llave de clasificación. La entidad sin clasificación
   aprobada queda fuera de los indicadores (regla 6). Evidencia en la muestra
   local de enero de 2025, que no es la foto definitiva: 372 `buyer.id`
   distintos, solo 185 con la forma simple `EC-RUC-{13 dígitos}` y 16 raíces
   asociadas a más de un `buyer.id`; `tender.procuringEntity.id` distinto de
   `buyer.id` en 1.929 de 2.141 releases, con la misma raíz en todos. Detalle
   en [entidades.md](../sources/entidades.md).

## Pendiente

| Tema | Estado | Quién lo resuelve |
|---|---|---|
| Fuente oficial para la clasificación de entidades | Propuesta aceptada ([entidades.md](../sources/entidades.md)): `gob.ec/instituciones` como fuente base nominal para descubrir candidatos. Cada clasificación se sustenta con su norma o fuente oficial; las adscripciones hoy `No verificada` se resuelven al construir la semilla **[PENDIENTE]** | Líder |
| Criterios de inclusión de entidades | **[PENDIENTE]** | Líder |
| Casos dudosos concretos | **[PENDIENTE]** al construir la semilla | Líder |
| Periodo de la foto (ver ADR 0002) | **[PENDIENTE]** tras reconocer la fuente | Líder |
| Atributo de la fuente que identifica a la entidad compradora | Definido en la decisión 7: `buyer.id` completo, con la raíz `EC-RUC-{13}` como respaldo validado. Sigue **[PENDIENTE]** validar sobre la foto definitiva que esa raíz corresponde al RUC legal, qué sufijos son unidades del mismo comprador y la correspondencia con `parties`; ver el reconocimiento en `docs/sources/` | Rol 1 (fuente y foto) |

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
