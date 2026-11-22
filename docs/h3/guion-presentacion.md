# Guion de la presentación del Hito 3

Seis diapositivas: una portada y una por integrante. Cada integrante habla 120 segundos; Francis presenta también la portada. El texto está en las notas del orador.

## 1. Trazabilidad de la contratación pública · Francis Bravo · 10 s

«Buenas tardes. Somos el Equipo 5 y les presentamos el avance de nuestro modelo sobre la contratación pública del gobierno central, construido con los datos abiertos de SERCOP.» Pasar a la siguiente sin detenerse.

## 2. El Estado publica cada compra, pero no dice cuánto gasta el gobierno central · Francis Bravo · 110 s

«En cinco años el Estado adjudicó más de treinta mil millones de dólares en un millón de procesos, y todo está publicado como datos abiertos. Pero en bruto: un archivo por año, una fila por transacción, y sin decir qué tipo de entidad compró. Por eso hoy no se puede responder cuánto gasta el gobierno central. Nuestro sector es ese gobierno central: Presidencia, ministerios e institutos adscritos. Planteamos tres preguntas. P1: cómo evolucionó el monto adjudicado por método y tipo de entidad, que sirve a las entidades para planificar. P2: qué métodos se desvían más de lo estimado, que sirve a SERCOP para reforzar controles. Y P3: cuánto se adjudicará por mes en el primer semestre de 2026, que sirve al Ministerio de Economía para programar el presupuesto.» Transición: «Ismael cuenta cómo convertimos esos datos en algo confiable.» Cifras: totales de control del Hito 2.

## 3. Un millón de registros abiertos, depurados con 21 correcciones que se pueden verificar · Ismael Freire · 120 s

«Los datos salen de este portal de SERCOP: cinco archivos anuales en el estándar internacional de contratación abierta. Para saber qué tipo de entidad es cada comprador usamos el catálogo institucional del MDEP, uniendo siempre por RUC y nunca por nombre, porque el mismo comprador aparece escrito de 425 formas. En el Hito 2 encontramos 21 problemas de calidad; en este hito cada uno tiene su corrección en Power Query y un total de control antes y después. Dos ejemplos: los procesos con varias adjudicaciones se suman por proceso sin cambiar el total, y las 109.793 licitaciones sin valor estimado se dejan vacías, porque un vacío no es un cero. De 1.007.920 procesos nacionales, 993.425 caen entre 2021 y 2025 y 275.100 son del gobierno central. Nada se pierde sin contarse: las sumas cuadran al centavo.» Transición: «Harry explica el modelo.» Cifras: cadena de totales y bitácora (Q-06, Q-01, Q-13).

## 4. Un hecho por proceso y tres dimensiones bastan para responder las tres preguntas · Harry Guajan · 120 s

«Seguimos los cuatro pasos de Kimball. El proceso de negocio es la contratación pública hasta la adjudicación. El grano es una fila por proceso del gobierno central, identificado por su ocid; las adjudicaciones de un mismo proceso se suman antes de entrar. Las dimensiones salen de las preguntas: DimTiempo con 60 meses, DimEntidad con 587 compradores y su tipo de entidad, y DimMetodo con 28 combinaciones de método y procedimiento. En el centro, FactContratacion con 275.100 filas y solo medidas sumables: monto adjudicado, valor estimado y conteos. La desviación de P2 no se guarda en la tabla, será una medida. Esto es lo que ven en la captura: el modelo real en Power BI, con tres relaciones de uno a varios y filtro en una sola dirección. Usamos un solo hecho porque las tres preguntas miran el proceso como unidad.» Transición: «Johann lo muestra funcionando.»

## 5. El modelo en Power BI y un cálculo independiente dan el mismo total, al centavo · Johann Pasquel · 120 s

1) Abrir el .pbix ya cargado en la página de prueba (no recargar datos). 2) «Esta matriz cruza el procedimiento con el año usando la medida Monto adjudicado.» Señalar la fila Total: 463 millones en 2021, 986 en 2022, 1.519 en 2023, 1.308 en 2024 y 1.235 en 2025. 3) Señalar la tarjeta: 5,51 mil millones. 4) «Este total también lo calculamos aparte en Python, año por año, y coincide al centavo: 5.511.799.162,58.» 5) Filtrar un año para mostrar que DimTiempo filtra el hecho. 6) «Esto ya responde en parte P1: el monto por procedimiento y año.» Plan B si Power BI falla: quedarse en esta diapositiva; la captura es la misma página.

## 6. Dos procedimientos concentran casi dos tercios del monto adjudicado · Jorge Torres · 120 s

«Con lo que acaban de ver ya hay una primera lectura de P1: la subasta inversa electrónica y la compra directa por catálogo concentran casi dos tercios del monto adjudicado del gobierno central en cinco años; los contratos entre entidades públicas suman otro 10 %. Para el segundo bimestre quedan tres pasos. Primero, validar la adscripción de 9.495 procesos de institutos, por 128 millones, que hoy dejamos fuera por no tener respaldo. Segundo, medir la desviación entre adjudicado y estimado para responder P2; el hecho ya tiene los dos importes. Tercero, pronosticar el primer semestre de 2026 para P3 y validarlo con el error WAPE. Todo eso, sobre PostgreSQL con un ETL de un solo comando. Gracias; quedamos atentos a sus preguntas.» Cifras: matriz de la página de prueba; otros 20 procedimientos = 5.511,80 − 1.805,0 − 1.770,4 − 580,1 = 1.356,3.

## Tiempos

| Diapositiva | Quién | Segundos |
|---|---|---|
| 1. Trazabilidad de la contratación pública | Francis Bravo | 10 |
| 2. El Estado publica cada compra, pero no dice cuánto gasta el gobierno central | Francis Bravo | 110 |
| 3. Un millón de registros abiertos, depurados con 21 correcciones que se pueden verificar | Ismael Freire | 120 |
| 4. Un hecho por proceso y tres dimensiones bastan para responder las tres preguntas | Harry Guajan | 120 |
| 5. El modelo en Power BI y un cálculo independiente dan el mismo total, al centavo | Johann Pasquel | 120 |
| 6. Dos procedimientos concentran casi dos tercios del monto adjudicado | Jorge Torres | 120 |
| **Total** | | **600** |

## Plan B de la demo

Si Power BI falla, Johann se queda en su diapositiva: la captura es la misma página de prueba.
