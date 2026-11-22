# Guion de la presentación del Hito 3

Presentación de 11 diapositivas (16:9). El texto de cada intervención también está en las notas del orador.

Reparto propuesto (el equipo puede cambiarlo): Francis Bravo 1–4, Ismael Freire 5–7, Harry Guajan 8–9, Johann Pasquel 10 (demo), Jorge Torres 11, que también cubre los próximos pasos. Cada integrante habla 120 segundos.

## Bloque 1. Sector y preguntas (2 min)

### 1. Trazabilidad de la contratación pública del gobierno central · Francis Bravo · 15 s

«Buenas tardes. Somos el Grupo 5. A la derecha está el Palacio de Carondelet, sede del gobierno central, que es el sector que estudiamos: cómo contrata y cuánto adjudica.» Pasar a la siguiente sin detenerse.

### 2. Los datos de contratación son abiertos, pero no permiten leer el gasto por tipo de entidad · Francis Bravo · 40 s

«En cinco años el Estado adjudicó más de treinta mil millones de dólares en un millón de procesos, y todo está publicado como datos abiertos. Pero en bruto: un archivo por año, una fila por transacción, y el mismo comprador escrito hasta de 425 formas. Sobre todo, la fuente no dice qué tipo de entidad compró. Por eso hoy nadie puede responder con esos archivos cuánto contrata el gobierno central, por qué procedimiento ni cuánto se desvía de lo estimado. Ese es el problema que resolvemos.» Cifras: totales de control del Hito 2 (1.007.920 procesos; USD 30.952.880.306,92) y hallazgo Q-13.

### 3. El modelo cubre los ministerios y la Presidencia; los institutos esperan validación · Francis Bravo · 35 s

«El sector es el gobierno central: Presidencia, ministerios e institutos que dependen de ellos. Hoy el modelo tiene 274.787 procesos de ministerios, por 5.470 millones, y 313 de la Presidencia. Los institutos, 9.495 procesos y 128 millones, quedan fuera hasta validar su adscripción: preferimos no mezclar el alcance. Con estos datos deciden tres actores: las entidades al planificar, SERCOP al controlar y el Ministerio de Economía al programar el presupuesto.» Cifras: evidencia del modelo por tipo de entidad; casos dudosos de la semilla.

### 4. Tres preguntas guían el modelo: qué pasó, dónde se desvía y qué viene · Francis Bravo · 30 s

«Sobre una misma línea de tiempo planteamos tres preguntas. P1 describe la historia de 2021 a 2025: cuánto se adjudicó por método y tipo de entidad. P2 diagnostica en ese mismo periodo qué métodos se desvían más de lo estimado. P3 proyecta el primer semestre de 2026. Todo el modelo está construido para responderlas.» Transición: «Ismael explica de dónde salen los datos.»

## Bloque 2. Datos y calidad (2 min)

### 5. Siete fuentes abiertas entran al modelo a través de 21 transformaciones controladas · Ismael Freire · 40 s

«Trabajamos con siete fuentes abiertas. Cinco son los archivos anuales de SERCOP en el estándar internacional de contratación abierta. La sexta es el catálogo institucional del MDEP, que nos dice qué tipo de entidad es cada comprador por su RUC. La séptima, el directorio gob.ec, solo sirve para contrastar nombres. Todo pasa por Power Query, donde aplicamos las 21 acciones del diagnóstico, cada una con su total de control, y llega a Power BI como un modelo de 275.100 procesos.» Cifras: totales de control del Hito 2 y del modelo.

### 6. Cada uno de los 21 hallazgos del diagnóstico tiene su corrección y su total de control · Ismael Freire · 40 s

«En el Hito 2 medimos la calidad con 26 controles en seis dimensiones y 21 dieron hallazgos. En este hito cada uno tiene su paso en Power Query y un total de control antes y después. Tres ejemplos. Hay procesos con varias adjudicaciones: se suman por proceso y la suma de 30.952 millones no cambia. Hay 109.793 licitaciones sin valor estimado: se dejan vacías, porque un vacío no es un cero. Y el comprador aparece escrito de 425 formas: por eso unimos siempre por RUC.» Cifras: calidad del Hito 2 (Q-06, Q-01, Q-13) y bitácora.

### 7. De 1.007.920 procesos nacionales, 275.100 son del gobierno central y las sumas cuadran al centavo · Ismael Freire · 40 s

«Así pasamos del país al sector, sin pérdidas silenciosas. De 1.007.920 procesos, 14.495 tienen fecha de 2026 y quedan fuera de la ventana. Luego salen 669.686 de otras funciones del Estado o de gobiernos locales, y 48.639 dudosos o sin clasificar, entre ellos los 9.495 de institutos. Quedan 275.100 procesos y 5.511,80 millones de dólares. En cada etapa las filas y las sumas cuadran al centavo.» Transición: «Harry presenta el modelo.» Cifras: cadena de totales del cálculo independiente.

## Bloque 3. Modelo dimensional (2 min aquí y 1 min en la diapositiva 11)

### 8. Un hecho a grano de proceso y tres dimensiones responden las tres preguntas · Harry Guajan · 70 s

«Seguimos los cuatro pasos de Kimball, que están abajo. El proceso es la contratación pública hasta la adjudicación. El grano: una fila por proceso del gobierno central, identificado por su ocid. Las dimensiones salen de las preguntas: DimTiempo mensual con 60 meses, DimEntidad con 587 compradores y su tipo, y DimMetodo con 28 combinaciones de método y procedimiento. En el centro, FactContratacion con 275.100 filas y solo medidas sumables. La desviación de P2 no se guarda en la tabla: será una medida.» Por qué un solo hecho: las tres preguntas usan el proceso como unidad; un hecho por adjudicación repetiría el estimado.

### 9. El modelo está construido en Power BI con relaciones de uno a varios y filtro único · Harry Guajan · 50 s

«Este es el modelo real en Power BI Desktop. Las tres dimensiones se unen al hecho con relaciones de uno a varios y filtro en una sola dirección, como pide la guía. Las claves están ocultas para que quien arme un informe solo vea atributos con sentido. La medida base es el monto adjudicado. La carga exigió optimizar las consultas y subir la memoria de evaluación, y comprobamos que ningún total cambió.» Transición: «Johann lo muestra funcionando.»

## Bloque 4. Demostración en Power BI (2 min)

### 10. El total del modelo coincide al centavo con un cálculo independiente en Python · Johann Pasquel · 120 s

1) Abrir el .pbix ya cargado en la página de prueba (no recargar datos). 2) «Esta matriz cruza el procedimiento con el año usando la medida Monto adjudicado.» Señalar la fila Total: 463 millones en 2021, 986 en 2022, 1.519 en 2023, 1.308 en 2024 y 1.235 en 2025. 3) Señalar la tarjeta: 5,51 mil millones. 4) «Este total también lo calculamos aparte en Python, año por año, y coincide al centavo: 5.511.799.162,58.» 5) Filtrar un año para mostrar que DimTiempo filtra el hecho. 6) «Esto ya responde en parte P1: el monto por procedimiento y año.» Plan B si Power BI falla: quedarse en esta diapositiva; la captura es la misma página.

## Bloque 3 y 5. Lectura de P1 y próximos pasos (2 min)

### 11. Dos procedimientos concentran el 65 % del monto adjudicado del gobierno central · Jorge Torres · 120 s

«Con lo que acaban de ver ya hay una primera lectura de P1: la subasta inversa electrónica y la compra directa por catálogo concentran casi dos tercios del monto adjudicado del gobierno central en cinco años. ¿Cuánto responde hoy el modelo? P1, en parte, porque falta el tipo instituto. P2 ya tiene los dos importes por proceso; falta la medida de desviación. P3 ya tiene 60 meses de historia; falta el pronóstico y su error. Lo que sigue en el segundo bimestre: validar la adscripción de los 9.495 procesos de institutos, llevar el modelo a PostgreSQL con un ETL de un solo comando, y construir el tablero con la desviación de P2 y el pronóstico de P3. Gracias; quedamos atentos a sus preguntas.» Cifras: matriz de la página de prueba; 1.804.987.010,45 + 1.770.404.336,62 = 64,9 % de 5.511.799.162,58.

## Tiempos

| Diapositiva | Quién | Segundos |
|---|---|---|
| 1. Trazabilidad de la contratación pública del gobierno central | Francis Bravo | 15 |
| 2. Los datos de contratación son abiertos, pero no permiten leer el gasto por tipo de entidad | Francis Bravo | 40 |
| 3. El modelo cubre los ministerios y la Presidencia; los institutos esperan validación | Francis Bravo | 35 |
| 4. Tres preguntas guían el modelo: qué pasó, dónde se desvía y qué viene | Francis Bravo | 30 |
| 5. Siete fuentes abiertas entran al modelo a través de 21 transformaciones controladas | Ismael Freire | 40 |
| 6. Cada uno de los 21 hallazgos del diagnóstico tiene su corrección y su total de control | Ismael Freire | 40 |
| 7. De 1.007.920 procesos nacionales, 275.100 son del gobierno central y las sumas cuadran al centavo | Ismael Freire | 40 |
| 8. Un hecho a grano de proceso y tres dimensiones responden las tres preguntas | Harry Guajan | 70 |
| 9. El modelo está construido en Power BI con relaciones de uno a varios y filtro único | Harry Guajan | 50 |
| 10. El total del modelo coincide al centavo con un cálculo independiente en Python | Johann Pasquel | 120 |
| 11. Dos procedimientos concentran el 65 % del monto adjudicado del gobierno central | Jorge Torres | 120 |
| **Total** | | **600** |

## Plan B de la demo

Si Power BI falla, Johann se queda en la diapositiva 10: la captura es la misma página de prueba y el total está a la derecha.

## Ensayo

- [ ] Dos ensayos completos con cronómetro; cada bloque cierra en su tiempo.
- [ ] Cada integrante abre el `.pbix` una vez antes de exponer y ubica la página de prueba.
- [ ] Ensayo de preguntas por persona sobre su propio bloque, con `preguntas-esperadas.md`.
