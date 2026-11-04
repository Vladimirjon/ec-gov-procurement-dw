# ADR 0001: Alcance del proyecto

- **Estado:** Aceptado
- **Fecha:** 2026-11-03 (reemplaza la versión del 2026-10-06)
- **Decide:** líder del equipo
- **Referencias:** guía del proyecto y guía del Hito 1 del profesor;
  [hito1.md](../requirements/hito1.md); [entidades.md](../sources/entidades.md)

## Contexto

El profesor asignó el sector **gobierno central**. La guía del Hito 1 pide
analizar el **sector completo**, no una institución en particular, con datos
públicos. La fuente de referencia que la guía sugiere para este sector incluye
las compras públicas de SERCOP.

## Decisión

1. **Sector:** gobierno central completo, es decir, la Presidencia de la
   República, los ministerios y los institutos que dependen de ellos.
2. **Fuera de alcance:** los GAD de cualquier nivel y sus empresas, las
   empresas públicas y las entidades de otras funciones del Estado.
3. **Periodo:** 2021–2025, años calendario completos (cinco periodos).
4. **Fuente principal:** datos abiertos de contratación pública de SERCOP en
   formato OCDS.
5. **Segunda fuente:** el directorio oficial de instituciones `gob.ec`, que
   permite clasificar a las entidades compradoras. Si el profesor no la acepta
   como segunda fuente integrable, se agrega otra fuente de hechos en el
   Hito 2.
6. **Clasificación de entidades:** cada comprador de SERCOP se asigna a una
   categoría: Presidencia, ministerio, instituto dependiente o fuera de
   alcance. Las entidades dudosas quedan fuera de los indicadores hasta
   resolverse. La clasificación es una semilla versionada en
   `warehouse/seeds/`.
7. **Regla de cruce.** El comprador se identifica con `buyer.id` de la
   fuente. En OCDS, `buyer.id` referencia a una organización y puede llevar un
   sufijo de unidad; no es sinónimo del RUC. Orden de unión:
   1. por `buyer.id` completo, sin modificarlo;
   2. si no coincide, por la raíz `EC-RUC-{13 dígitos}` solo si el patrón se
      validó en la semilla;
   3. nunca por `buyer.name`.

   `tender.procuringEntity.id` se conserva como unidad contratante y no se usa
   para clasificar. La clasificación aplicable es la vigente en la fecha del
   proceso (SCD tipo 2 en `dim_entity`).
8. Cualquier cambio de alcance se registra en un ADR nuevo.

## Evidencia

En la descarga de enero de 2025 (2.186 procesos) hay 372 `buyer.id` distintos,
solo 185 con la forma simple `EC-RUC-{13 dígitos}` y 16 raíces asociadas a más
de un `buyer.id`; `tender.procuringEntity.id` difiere de `buyer.id` en 1.929 de
2.141 releases, con la misma raíz en todos. Esta es una muestra y no la foto
definitiva. Detalle en [entidades.md](../sources/entidades.md).

## Pendiente

| Tema | Quién | Cuándo |
|---|---|---|
| Fuente oficial por entidad para la clasificación y sus criterios de inclusión | Líder | Hito 2 |
| Validar la raíz `EC-RUC-{13}` contra el RUC legal en los años 2021–2024 | Líder | Hito 2 |
| Confirmar que la segunda fuente se acepta | Líder | Hito 2 |

## Consecuencias

- Sin la semilla de clasificación no se puede filtrar el sector ni construir la
  jerarquía Presidencia > ministerio > instituto.
- Los cambios de nombre, fusiones o cambios de ministerio se modelan en
  `dim_entity` con SCD tipo 2.
