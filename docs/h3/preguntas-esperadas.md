# Preguntas esperadas | Hito 3

Respuestas breves para exposición. Los responsables coinciden con los dueños propuestos de cada bloque.

## ¿De dónde vienen los datos y qué tan confiables son?

**Responde: Ismael Freire, bloque Datos y calidad.**

Proceden de las descargas abiertas del portal de contratación pública, estructuradas según OCDS. H2 identificó 1.007.920 procesos y USD 30.952.880.306,92 adjudicados en el universo nacional descargado (`docs/h2/calidad.csv`). La calidad se verificó con controles de cobertura, unicidad, moneda e importes (`docs/h2/calidad.csv`). Son registros administrativos publicados; los controles detectan problemas de estructura, pero no certifican que cada dato publicado refleje toda la realidad contractual. La descarga corresponde al corte documentado en H2 y el portal puede actualizarse.

## ¿Cómo se trataron faltantes y errores?

**Responde: Ismael Freire, bloque Datos y calidad.**

H2 diagnostica faltantes y anomalías sin corregirlos; H3 aplica las reglas definidas en el diseño. Importes ausentes permanecen vacíos, no se imputan como cero. Las adjudicaciones se agregan por `ocid` antes de relacionarse con licitaciones para no multiplicar el estimado (`diseno-dimensional.md`). Procesos fuera de ventana o compradores dudosos quedan fuera del hecho y se conservan en controles de alcance (`controles-esperados.csv`).

## ¿Por qué una sola tabla de hechos?

**Responde: Harry Guajan, bloque Modelo dimensional.**

P1, P2 y P3 se apoyan en medidas agregadas a grano de proceso: método, entidad y fecha caracterizan el proceso. Sumar adjudicaciones dentro del proceso conserva el monto y evita duplicar el valor estimado. El diseño registra 1.801 procesos con varias adjudicaciones en el universo medido, pero ninguna de las preguntas exige analizar cada adjudicación individual (`diseno-dimensional.md`). Por eso `FactContratacion` y tres dimensiones bastan para H3; el análisis individual se puede evaluar en una etapa posterior.

## ¿Cómo se asigna un proceso a un mes y a un año?

**Responde: Harry Guajan, bloque Modelo dimensional.**

Se usa la fecha de `releases.date`, tratada como fecha del proceso. `DimTiempo` trabaja a nivel mensual y cubre 60 meses, de enero de 2021 a diciembre de 2025 (`diseno-dimensional.md`). El año del nombre del archivo no determina el periodo, porque 81.898 procesos de la ventana tienen un año de archivo distinto al de su fecha (`diseno-dimensional.md`).

## ¿Por qué no hay institutos?

**Responde: Johann Pasquel, bloque Demostración y conciliación.**

La regla aprobada exige respaldo para clasificar al comprador como parte del gobierno central. La denominación «instituto» por sí sola no demuestra adscripción ministerial (`semilla-entidades.md`). Por ello, 9.495 procesos y USD 128,24 millones asociados a institutos dudosos quedan fuera del hecho y se contabilizan como no clasificados (cifras de la semilla y confirmación del equipo del 22/11/2026). El hecho contiene cero institutos, según la confirmación de Power BI de esa fecha.

## ¿Qué falta para P3?

**Responde: Jorge Torres, bloque Próximos pasos.**

La pregunta de P3 solicita el monto adjudicado esperado por mes para el primer semestre de 2026 y por tipo de entidad (`docs/requirements/hito1.md`). El modelo permite organizar la serie histórica, pero la página mostrada es descriptiva, no una predicción. Falta construir el pronóstico mensual, separar temporalmente los meses para validación y reportar el WAPE propuesto por el equipo. La pregunta solo será defendible cuando se muestre esa validación junto con sus límites.

## ¿Qué costaría mantenerlo?

**Responde: Jorge Torres, bloque Próximos pasos.**

El costo operativo principal es actualizar las descargas, revisar cambios en la publicación y volver a ejecutar los controles de calidad, cobertura y conciliación por año. También hay que mantener la clasificación de entidades y documentar las decisiones que cambien el alcance (`semilla-entidades.md`, `runbook-modelo.md`). No se dispone de una estimación monetaria ni de horas-persona en la evidencia; por eso no afirmamos un costo numérico. El trabajo actual es académico e independiente, sin infraestructura de producción.

## ¿Qué limitaciones tiene?

**Responde: Francis Bravo, bloque Sector y preguntas.**

El modelo cubre solo 2021–2025, el gobierno central clasificado y los compradores aprobados. Excluye los 14.495 procesos fechados en 2026 y mantiene fuera del hecho casos dudosos, incluidos institutos sin adscripción respaldada (cifras de `diseno-dimensional.md` y `semilla-entidades.md`). El total de H2 es nacional; no debe confundirse con el total del sector. La captura prueba el total descriptivo de Power BI, pero no demuestra el pronóstico P3 ni convierte los datos publicados en una auditoría de cada contrato.
