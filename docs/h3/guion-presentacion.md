# Guion de presentación | Hito 3

**Duración total: 600 segundos (10:00).** Asignación propuesta; el equipo puede cambiarla. Las cifras se citan junto a su origen.

## Diapositiva 1 | 60 s | Francis Bravo

«En el periodo 2021 a 2025, el modelo que construimos registra USD 5.511,80 millones adjudicados en el sector delimitado. Esta cifra resume el avance del Hito 3: pasar del diagnóstico de datos a un modelo que permita analizar contratación por tiempo, entidad y procedimiento. Somos el Grupo 5 y presentamos el modelo dimensional y su prueba en Power BI.» (Origen del total: confirmación de Power BI del 22/11/2026; conciliación anual independiente en Python. La captura `pagina-prueba.png` muestra USD 5.511.799.162,58.)

**Transición:** «Para entender qué responde este modelo, recordemos las tres preguntas de negocio.»

## Diapositiva 2 | 60 s | Francis Bravo

«P1 describe cómo evoluciona el monto adjudicado por método, año y tipo de entidad. P2 compara el valor adjudicado con el estimado para observar desviaciones y orientar controles. P3 pregunta cuánto podría adjudicarse mensualmente durante el primer semestre de 2026 por tipo de entidad. Las decisiones corresponden a entidades contratantes, SERCOP y, para la programación, al MEF. Esa última relación con el presupuesto es una inferencia del equipo, no una atribución normativa.» (Origen de P1 a P3 y actores: `docs/requirements/hito1.md`.)

**Transición:** «Con esas preguntas claras, veamos el universo de datos y qué controles aplicamos.»

## Diapositiva 3 | 60 s | Ismael Freire

«Los datos proceden de las descargas abiertas de contratación pública, organizadas según OCDS. Hito 2 diagnosticó 1.007.920 procesos nacionales y USD 30.952.880.306,92 adjudicados para el conjunto descargado. Dentro de la ventana 2021–2025 hay 993.425 procesos. Son controles nacionales de H2: todavía no representan el sector central filtrado.» (Origen: `docs/h2/calidad.csv`, `docs/h3/evidencia/controles-esperados.csv`.)

**Transición:** «La ventana y la clasificación de compradores determinan qué entra en el indicador.»

## Diapositiva 4 | 60 s | Ismael Freire

«La fecha de negocio es la del proceso, y por eso los 14.495 procesos fechados en 2026 quedan fuera de la ventana 2021–2025. También dejamos fuera institutos cuya adscripción no está respaldada: la evidencia de la semilla registra 9.495 procesos y USD 128,24 millones. Se cuentan en la conciliación, no desaparecen del diagnóstico. Hito 2 identifica faltantes y otros problemas de calidad; Hito 3 aplica reglas explícitas sin convertir un dato ausente en cero.» (Origen: `diseno-dimensional.md`, `semilla-entidades.md`, `controles-esperados.csv`, `docs/h2/calidad.csv`; los 9.495 procesos y USD 128,24 millones son casos dudosos de institutos dentro de los registros sin clasificar.)

**Transición:** «Con esos límites, construimos una estrella de un hecho y tres dimensiones.»

## Diapositiva 5 | 60 s | Harry Guajan

«El grano es un proceso de contratación identificado por `ocid`, dentro del periodo y con comprador aprobado como parte del sector. El hecho guarda sus medidas y claves. Las dimensiones describen tiempo, entidad y método. La vista de modelo que mostramos tiene `FactContratacion` al centro y las tres dimensiones conectadas.» (Origen del grano y diseño: `diseno-dimensional.md`; captura `modelo.png`.)

**Transición:** «La forma importa, pero también importa cómo preservamos los importes.»

## Diapositiva 6 | 60 s | Harry Guajan

«Cuando un proceso tiene varias adjudicaciones, primero sumamos sus importes al nivel del proceso; así evitamos repetir el valor estimado al unir tablas. Si falta un importe, queda vacío. En Power BI se observan tres relaciones de uno a varios y filtro único desde las dimensiones al hecho. Esa estructura facilita segmentar sin guardar tasas como si fueran importes.» (Origen de reglas: `diseno-dimensional.md` y `runbook-modelo.md`; relaciones confirmadas por el equipo el 22/11/2026 y visibles en `modelo.png`.)

**Transición:** «Ahora conciliamos el resultado del modelo con el alcance del sector.»

## Diapositiva 7 | 60 s | Johann Pasquel

«El hecho contiene 275.100 filas. No contiene institutos: los casos dudosos se excluyeron y permanecen contabilizados en el control de alcance. La medida suma USD 5.511.799.162,58, y coincide con el cálculo independiente realizado año por año en Python. Las 14.495 filas de 2026 también quedan fuera del modelo por la ventana acordada.» (Origen: cifras de filas y conciliación confirmadas en Power BI el 22/11/2026; controles de alcance y periodo: `controles-esperados.csv`; semilla: `semilla-entidades.md`.)

**Transición:** «Veamos ahora la página de prueba en funcionamiento.»

## Diapositiva 8 | 60 s | Johann Pasquel

«En la página de prueba tenemos el procedimiento en las filas, el año en las columnas y la medida Monto adjudicado en los valores. El total visible es USD 5.511.799.162,58. Voy a señalar la tarjeta y después el total general de la matriz; ambos permiten comprobar el mismo resultado.» (Origen: captura `pagina-prueba.png` y confirmación de Power BI del 22/11/2026.)

### Demo paso a paso en Power BI Desktop (incluida en los 60 s)

1. Tener abierto el `.pbix` final en la página de prueba antes de iniciar; señalar la pestaña de la página.
2. Señalar la matriz y leer su estructura: `Procedimiento` en filas y años 2021–2025 en columnas.
3. Señalar la tarjeta **Monto adjudicado** y leer el total subyacente: USD 5.511.799.162,58. El visual puede abreviarlo como 5,51bn.
4. Señalar el total general de la matriz: USD 5.511.799.162,58; aclarar que coincide con la tarjeta y con el cálculo anual independiente en Python.
5. Seleccionar un año en el encabezado de la matriz solo si la interacción está lista; señalar que la selección filtra los procedimientos y luego limpiar la selección. No cambiar consultas ni refrescar durante la presentación.

**Plan B:** si Power BI falla, compartir `docs/h3/evidencia/capturas/pagina-prueba.png`. Señalar los años, el total de la matriz y la tarjeta; leer USD 5.511.799.162,58. Para explicar relaciones, cambiar a `docs/h3/evidencia/capturas/modelo.png`. Decir claramente que se está mostrando la captura de la prueba, no una interacción en vivo.

**Transición:** «La prueba permite leer P1; no pretende responder por sí sola el pronóstico P3.»

## Diapositiva 9 | 60 s | Jorge Torres

«En la matriz se aprecia la distribución del monto por procedimiento y año. El total coincide con la tarjeta y con la verificación independiente año por año. Esta página demuestra una lectura descriptiva para P1; no es todavía un pronóstico. P3 necesita una serie mensual, una validación temporal y una medida de error que permita juzgar el resultado antes de usarlo para programar.» (Origen del total y la conciliación: confirmación de Power BI del 22/11/2026; imagen: `pagina-prueba.png`; alcance de P3: `docs/requirements/hito1.md`.)

**Transición:** «Cierro con la recomendación para llevar este avance a una entrega defendible.»

## Diapositiva 10 | 60 s | Jorge Torres

«Recomendamos resolver y documentar primero los casos dudosos de entidades, manteniendo visible cuánto queda excluido. Después, validar el pronóstico mensual de P3 con una separación temporal y reportar su error; solo entonces usarlo para apoyar la programación. Mantendremos la conciliación por año como control de cambios. Así el siguiente avance amplía el análisis sin ocultar las limitaciones de cobertura.» (Origen: regla y casos por resolver en `semilla-entidades.md`; validación de P3 y métrica propuesta en `docs/requirements/hito1.md`; recomendación del equipo.)

## Control de tiempo

| Diapositiva | Segundos | Acumulado |
|---|---:|---:|
| 1 | 60 | 60 |
| 2 | 60 | 120 |
| 3 | 60 | 180 |
| 4 | 60 | 240 |
| 5 | 60 | 300 |
| 6 | 60 | 360 |
| 7 | 60 | 420 |
| 8 (incluye demo) | 60 | 480 |
| 9 | 60 | 540 |
| 10 | 60 | 600 |
| **Total** | **600** | **10:00** |

## Lista de ensayo

- [ ] Hacer dos ensayos completos con cronómetro; respetar los 600 segundos.
- [ ] Cada integrante abre el `.pbix` una vez antes de exponer y comprueba la página de prueba.
- [ ] Ensayar la demo y el plan B con las dos capturas guardadas localmente.
- [ ] Leer en voz alta los importes y practicar la transición entre cada bloque.
