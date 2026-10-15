# E0 · Contextualización del caso de estudio

**Título:** Contratación pública de la planta central del Estado ecuatoriano · **Responsable del borrador:** Jorge Torres · **Fecha:** 14 de octubre de 2026

## Nombre y giro de la unidad de estudio

La unidad de estudio es la **planta central del Estado ecuatoriano en su papel
de comprador público**: Presidencia de la República, ministerios e institutos
que dependen de los ministerios. Se busca cubrir todas las entidades que
cumplan esa definición, no una muestra. Los gobiernos autónomos
descentralizados (GAD), sus empresas y las demás entidades fuera de la planta
central quedan excluidos. El proyecto es académico e independiente de SERCOP
y de las entidades estudiadas. Esta delimitación procede de la
[propuesta del equipo](../PROPUESTA.md#1-contexto-y-objetivo) y del
[ADR 0001](../adr/0001-alcance.md).

## Área de análisis

El caso se centra en los **procesos de contratación pública** de esas
entidades. La fuente prevista es el portal de datos abiertos de contratación
pública de SERCOP, que publica datos en formato OCDS. El
[reconocimiento de la fuente](../sources/reconocimiento.md#campos-evidencia-y-límites-de-lo-observado)
distingue la respuesta resumida de búsqueda de las descargas JSON anidadas;
no se presume que sus propiedades sean equivalentes. El periodo de la foto
definitiva todavía no está decidido.

## Problema o necesidad

El portal abarca entidades de todo el país, incluidas algunas fuera del caso
de estudio. Para analizar únicamente la planta central se necesita identificar
y justificar qué compradores pertenecen a ella; esa clasificación aún no
tiene fuente oficial ni criterios de inclusión aprobados. Además, la
[inspección de las descargas](../sources/reconocimiento.md#inspección-del-zip-anual-json)
muestra información anidada y procesos con varias adjudicaciones o contratos.
Los valores presupuestados, estimados, adjudicados y contractuales representan
conceptos distintos; no se pueden intercambiar para completar ausencias.
En la descarga anual de reconocimiento de 2025 se contaron 190.619 `ocid`
distintos y 300 releases con varias adjudicaciones. Esos conteos son
**nacionales**, no del subconjunto de la planta central.

La necesidad es disponer de una base analítica con alcance institucional
explícito y reglas verificables para comparar procesos, modalidades e importes
sin duplicar procesos ni ocultar datos faltantes. El Data Warehouse es la
solución prevista por el equipo; todavía no está implementado. La descarga
de reconocimiento tampoco constituye la foto definitiva.

## Preguntas clave para el futuro Data Warehouse

1. ¿Cuántos procesos corresponden a cada entidad compradora incluida y cómo
   se distribuyen entre Presidencia, ministerios e institutos dependientes?
2. ¿Cómo se distribuyen los procesos de cada entidad según el método de
   contratación registrado?
3. ¿Cómo varía la cantidad de procesos entre periodos comparables dentro de
   la foto que se seleccione?
4. ¿Cómo se distribuye el valor de las adjudicaciones registradas entre
   entidades y métodos de contratación?
5. ¿En qué procesos difiere el valor adjudicado del valor estimado de la
   licitación, cuando ambos son comparables?
6. Entre los procesos atribuibles a entidades incluidas, ¿con qué frecuencia
   faltan datos utilizables sobre el método o la fecha y, cuando se confirme
   una adjudicación, sobre su importe?

Estas preguntas orientan los requerimientos posteriores; no establecen
indicadores ni fórmulas. Para responderlas se debe validar la clasificación de
entidades y la utilidad de `buyer.id` y `buyer.name`; decidir el periodo y la
fecha de negocio; comprobar la cobertura de `tender.procurementMethod`; y
definir cómo tratar adjudicaciones múltiples, monedas y estados antes de
comparar importes o calificar su ausencia como incompletitud. Las rutas de
importes observadas se documentan en la
[inspección mensual](../sources/reconocimiento.md#inspección-local-de-la-descarga-mensual-json).
