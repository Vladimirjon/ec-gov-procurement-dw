# Guion de la presentación del Hito 3

Presentación de 12 diapositivas (16:9) armada como artefacto; el texto de cada intervención también está en las notas del orador.

Reparto propuesto (el equipo puede cambiarlo): Francis Bravo 1–4, Ismael Freire 5–7, Harry Guajan 8–9, Johann Pasquel 10 (demo), Jorge Torres 11–12. Cada integrante habla 120 segundos.

## Bloque 1. Sector y preguntas (2 min)

### 1. Trazabilidad de la contratación pública del gobierno central · Francis Bravo · 15 s

«Buenas tardes. Somos el Grupo 5. La imagen es el Palacio de Carondelet, sede del gobierno central: el sector que estudiamos. Nuestro proyecto sigue el rastro de cómo ese gobierno contrata.» Pasar a la siguiente sin detenerse.

### 2. Planteamiento del problema · Francis Bravo · 40 s

«En cinco años el Estado adjudicó más de treinta mil millones de dólares en un millón de procesos. Todo está publicado como datos abiertos, pero en bruto: un archivo por año, una fila por transacción, sin decir qué tipo de entidad compró. Con esos archivos un analista del Ministerio de Economía no puede responder cuánto compra el gobierno central, por qué procedimiento ni cuánto se desvía de lo estimado. Ese es el problema que resolvemos.» Cifras: totales de control del Hito 2 (1.007.920 procesos; USD 30.952.880.306,92).

### 3. Alcance y decisores · Francis Bravo · 35 s

«Delimitamos el sector al gobierno central: Presidencia, ministerios e institutos que dependen de ellos; los gobiernos locales y sus empresas quedan fuera. Hoy el modelo tiene 274.787 procesos de ministerios, por 5.470 millones, y 313 de la Presidencia, por 41 millones. Los institutos están en cero a propósito: 9.495 procesos no tienen respaldo suficiente de adscripción y no los mezclamos. Quienes deciden con estos datos son las propias entidades, SERCOP y el Ministerio de Economía.» Cifras: evidencia del modelo por tipo de entidad y año; casos dudosos de la semilla.

### 4. Preguntas de negocio · Francis Bravo · 30 s

«Con esos decisores planteamos tres preguntas sobre una misma línea de tiempo. P1 describe la historia de 2021 a 2025: cuánto se adjudicó por método y tipo de entidad. P2 diagnostica en ese mismo periodo qué métodos se desvían más de lo estimado. P3 proyecta el primer semestre de 2026. Todo el modelo está construido para responderlas.» Transición: «Ismael explica de dónde salen los datos.»

## Bloque 2. Datos y calidad (2 min)

### 5. Fuentes de datos e integración · Ismael Freire · 40 s

«Trabajamos con siete fuentes abiertas. Cinco son los archivos anuales de SERCOP en el estándar internacional de contratación abierta, de 2021 a 2025: un millón de procesos. La sexta es el catálogo institucional del MDEP, que nos dice qué tipo de entidad es cada comprador por su RUC. La séptima, el directorio gob.ec, solo sirve de contraste. Todo pasa por Power Query, donde aplicamos las 21 acciones que salieron del diagnóstico, y llega a Power BI como un modelo de 275.100 procesos.» Cifras: totales de control del Hito 2 y del modelo.

### 6. Diagnóstico de calidad y tratamiento aplicado · Ismael Freire · 40 s

«En el Hito 2 medimos la calidad con 26 controles en seis dimensiones y 21 dieron hallazgos. En este hito cada uno tiene su paso en Power Query, con un total de control antes y después. Tres ejemplos. Unicidad: 1.801 procesos tenían varias adjudicaciones; se suman por proceso y la suma no cambia. Completitud: 109.793 licitaciones no traen valor estimado y se dejan vacías, porque un vacío no es un cero. Consistencia: el mismo comprador aparece escrito de 425 formas, por eso unimos siempre por RUC.» Cifras: calidad del Hito 2 (Q-06, Q-01, Q-13) y bitácora.

### 7. Conciliación: del registro nacional al sector · Ismael Freire · 40 s

«Así pasamos del país al sector, sin pérdidas silenciosas. De 1.007.920 procesos, 14.495 tienen fecha de 2026 y quedan fuera de la ventana. Después salen 669.686 de otras funciones o de gobiernos locales, y 48.639 dudosos o sin clasificar, entre ellos 9.495 de institutos. Quedan 275.100 procesos y 5.511,80 millones de dólares. En cada etapa las filas y las sumas cuadran al centavo.» Transición: «Harry presenta el modelo.» Cifras: cadena de totales del cálculo independiente.

## Bloque 3. Modelo dimensional (2 min aquí y 1 min en la diapositiva 11)

### 8. Modelo dimensional en estrella · Harry Guajan · 70 s

«Seguimos los cuatro pasos de Kimball, abajo en la franja. El proceso es la contratación pública hasta la adjudicación. El grano: una fila por proceso del gobierno central, identificado por su ocid. Las dimensiones responden a las preguntas: DimTiempo mensual con 60 meses, DimEntidad con 587 compradores y su tipo, y DimMetodo con 28 combinaciones de método y procedimiento. En el centro, FactContratacion con 275.100 filas y solo medidas sumables. Las tasas, como la desviación de P2, no se guardan en la tabla: serán medidas.» Por qué un solo hecho: las tres preguntas usan el proceso como unidad; un hecho por adjudicación repetiría el estimado.

### 9. Implementación en Power BI · Harry Guajan · 50 s

«Este es el modelo real en Power BI Desktop. Las tres dimensiones se unen al hecho con relaciones de uno a varios y filtro en una sola dirección, como pide la guía. Las claves están ocultas para que quien arme un informe solo vea atributos con sentido. La medida base es el monto adjudicado. La carga no fue trivial: hubo que optimizar las consultas y subir la memoria de evaluación, y comprobamos que ningún total cambió.» Transición: «Johann lo muestra funcionando.»

## Bloque 4. Demostración en Power BI (2 min)

### 10. Demostración: monto adjudicado por procedimiento y año · Johann Pasquel · 120 s

1) Abrir el .pbix ya cargado en la página de prueba (no recargar datos). 2) «Esta matriz cruza el procedimiento con el año usando la medida Monto adjudicado.» Señalar la fila Total: 463 millones en 2021, 986 en 2022, 1.519 en 2023, 1.308 en 2024 y 1.235 en 2025. 3) Señalar la tarjeta: 5,51 mil millones. 4) «Este total también lo calculamos aparte en Python, año por año, y coincide al centavo: 5.511.799.162,58.» 5) Filtrar un año para mostrar que DimTiempo filtra el hecho. 6) «Esto ya responde en parte P1: el monto por método y año.» Plan B si Power BI falla: quedarse en esta diapositiva; la captura es la misma página.

## Bloque 3 y 5. Resultados preliminares y próximos pasos (2 min)

### 11. Resultados preliminares y estado de las preguntas · Jorge Torres · 60 s

«Con lo que acaban de ver ya hay una primera lectura de P1: dos procedimientos, la subasta inversa electrónica y la compra directa por catálogo, concentran casi dos tercios del monto adjudicado del gobierno central en cinco años. ¿Cuánto responde hoy el modelo? P1, en parte: falta el tipo instituto. P2 ya tiene los dos importes en el hecho; falta la medida de desviación. P3 tiene los 60 meses de historia; falta el pronóstico y su error.» Cifras: matriz de la página de prueba; 1.804.987.010,45 + 1.770.404.336,62 = 64,9 % de 5.511.799.162,58.

### 12. Recomendamos confirmar la adscripción de los institutos antes de medir P2 y P3 · Jorge Torres · 60 s

«Cerramos con una recomendación concreta: antes de medir la desviación y el pronóstico hay que confirmar la adscripción de los institutos. Hoy 9.495 procesos y 128 millones de dólares quedan fuera por falta de respaldo, y por eso el tipo instituto está vacío. En el segundo bimestre el modelo pasa a PostgreSQL con un ETL de un solo comando, se agrega la historia de las entidades y el cubo, y al final el tablero con P2 y P3. Gracias; quedamos atentos a sus preguntas.» Cifras: casos dudosos de la semilla de entidades.

## Tiempos

| Diapositiva | Quién | Segundos |
|---|---|---|
| 1. Trazabilidad de la contratación pública del gobierno central | Francis Bravo | 15 |
| 2. Planteamiento del problema | Francis Bravo | 40 |
| 3. Alcance y decisores | Francis Bravo | 35 |
| 4. Preguntas de negocio | Francis Bravo | 30 |
| 5. Fuentes de datos e integración | Ismael Freire | 40 |
| 6. Diagnóstico de calidad y tratamiento aplicado | Ismael Freire | 40 |
| 7. Conciliación: del registro nacional al sector | Ismael Freire | 40 |
| 8. Modelo dimensional en estrella | Harry Guajan | 70 |
| 9. Implementación en Power BI | Harry Guajan | 50 |
| 10. Demostración: monto adjudicado por procedimiento y año | Johann Pasquel | 120 |
| 11. Resultados preliminares y estado de las preguntas | Jorge Torres | 60 |
| 12. Recomendamos confirmar la adscripción de los institutos antes de medir P2 y P3 | Jorge Torres | 60 |
| **Total** | | **600** |

## Plan B de la demo

Si Power BI falla, Johann se queda en la diapositiva 10: la captura es la misma página de prueba y el total está en el recuadro de la derecha.

## Ensayo

- [ ] Dos ensayos completos con cronómetro; cada bloque cierra en su tiempo.
- [ ] Cada integrante abre el `.pbix` una vez antes de exponer y ubica la página de prueba.
- [ ] Ensayo de preguntas por persona sobre su propio bloque, con `preguntas-esperadas.md`.
- [ ] El `.pbix` abierto en la página de prueba antes de empezar (no recargar datos en vivo).
