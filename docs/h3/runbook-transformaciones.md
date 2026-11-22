# Transformaciones de las consultas intermedias

El líder ejecuta este procedimiento en Power BI Desktop. Ninguna consulta M de H3 se ha ejecutado aún. La revisión de los archivos es estática; los controles siguientes se midieron de forma independiente con Python 3.14 y `decimal.Decimal` sobre los cinco CSV anuales de cada tabla. Las pruebas sintéticas no acreditan ejecución de M.

Fuentes: F1, CSV del portal SERCOP descargados el 21/11/2026, inventariados en [Fuentes de H2](../h2/fuentes.csv); diagnóstico [Calidad](../h2/calidad.csv); [diseño dimensional aprobado](diseno-dimensional.md), secciones 6 y 9; guía del profesor H3, secciones 4.1, 4.3 y pasos 1 a 8. El resultado medido está en [controles-esperados.csv](evidencia/controles-esperados.csv). Los controles son nacionales, antes de excluir fechas de 2026 o filtrar gobierno central.

## Preparación y pegado, una consulta por vez

1. Se abre el archivo de H2 y se guarda una copia como `H3MD-BravoFreireGuajanPasquelTorres.pbix`, conforme a la decisión de entrega del 22/11/2026. Se entra en **Transformar datos**. Se conservan los parámetros de texto `RutaDerivados` y `RutaDatosCrudos` del [runbook de conexión](../h2/runbook-power-bi.md). Estas tres consultas usan únicamente `RutaDerivados`; no necesitan leer el catálogo ni crear `Entidades_MDEP` para Q-01 a Q-12.
2. Se selecciona `Procesos_SERCOP`, se abre **Editor avanzado** y se reemplaza su contenido por [Procesos_SERCOP.pq](../../reports/powerbi/h3/queries/Procesos_SERCOP.pq). Se confirma y se espera la evaluación completa. Se conserva exactamente el nombre de la consulta. No se crea otra copia con el mismo nombre.
3. Se comprueban los pasos de Procesos y los controles de esta guía antes de continuar. Después se repite, una por una, con [Licitaciones_SERCOP.pq](../../reports/powerbi/h3/queries/Licitaciones_SERCOP.pq) y [Adjudicaciones_SERCOP.pq](../../reports/powerbi/h3/queries/Adjudicaciones_SERCOP.pq). Se elimina un eventual paso automático **Tipo cambiado** ajeno al código.
4. En cada consulta intermedia se desactiva **Habilitar carga** desde el menú contextual. Se desactiva la detección automática de relaciones. No se incorpora ninguna tabla de origen al modelo. La creación de dimensiones y hecho corresponde al trabajo posterior.
5. Se selecciona **perfil de todo el conjunto de datos**, no las primeras 1.000 filas. Los controles se obtienen evaluando tablas completas. Una vista previa o un recuento truncado no demuestra el total.

Los nombres de carpetas relativos de los `.pq` conservan los sellos de las descargas usadas en H2. Los CSV se leen con UTF-8, encabezados antes de anexar y `QuoteStyle.Csv`. No se cambia ningún archivo fuente. No se usa detección automática del tipo de importe.

## Cómo leer y reproducir los controles

Cada fila del CSV identifica tabla, año del archivo y nombre exacto de paso, con filas y sumas antes/después. `TOTAL` corresponde al anexado. Los pasos que seleccionan columnas, verifican claves o derivan atributos conservan filas y suma. En el primer paso se compara el conjunto leído consigo mismo: no representa una carga previa. Los controles monetarios de pasos aún textuales se calculan convirtiendo una copia del importe con cultura `en-US`, sin modificar el paso de origen. Una suma vacía indica ausencia de importes, no cero. Las filas `Diagnóstico` contienen métricas adicionales; no son pasos M.

La lectura anual que devuelve una lista de tablas (`CSV anuales UTF-8 con saltos entre comillas`) se verifica con las filas anuales de `Cinco años anexados`. La suma de estas filas debe coincidir con `TOTAL`. Los años de este control son los del archivo, no los de `date`.

| Año del archivo | Procesos | Licitaciones | Adjudicaciones antes | Adjudicaciones agrupadas | Suma estimado USD | Suma adjudicado USD |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 167.058 | 165.616 | 166.983 | 164.266 | 3.682.296.515,41 | 4.676.997.257,82 |
| 2022 | 212.324 | 203.147 | 200.173 | 197.726 | 5.855.681.059,39 | 7.118.687.591,72 |
| 2023 | 217.913 | 213.841 | 212.989 | 211.214 | 4.798.618.255,15 | 6.037.778.222,93 |
| 2024 | 219.185 | 212.386 | 210.445 | 208.171 | 5.518.333.500,28 | 6.895.826.062,72 |
| 2025 | 191.440 | 186.358 | 184.712 | 183.098 | 5.218.039.375,30 | 6.223.591.171,73 |
| Total | 1.007.920 | 981.348 | 975.302 | 964.475 | 25.072.968.705,53 | 30.952.880.306,92 |

Origen de todas las celdas: CSV de controles, pasos `Cinco años anexados` y `Adjudicaciones agrupadas por ocid (suma, conteo)`. En adjudicaciones la suma se conserva al agrupar. La atribución anual de los grupos es válida porque la comprobación independiente rechaza un `ocid` compartido entre años.

| Consulta | Pasos aplicados, en orden | Control nacional antes → después |
|---|---|---|
| Procesos | Cinco años anexados; Campos para comprobar claves; Claves completas verificadas; Unicidad de proceso verificada; Fecha de negocio desde releases.date; Año y mes desde la fecha de negocio; Raíz de RUC desde buyer_id; Columnas finales de procesos | Cada paso: 1.007.920 → 1.007.920; sin importe |
| Licitaciones | Cinco años anexados; Campos para limpiar licitaciones; Método sin espacios repetidos ni saltos de línea; Importe estimado decimal anulable; Unicidad de licitación verificada; Moneda solo USD verificada; Importes negativos excluidos; Indicador de importe estimado; Columnas finales de licitaciones | Cada paso: 981.348 → 981.348; USD 25.072.968.705,53 → 25.072.968.705,53 |
| Adjudicaciones | Cinco años anexados; Campos de adjudicación sin importes vacíos de oferta; Importe adjudicado decimal anulable; Unicidad de adjudicación verificada; Moneda solo USD verificada; Importes negativos excluidos | Cada paso: 975.302 → 975.302; USD 30.952.880.306,92 → 30.952.880.306,92 |
| Adjudicaciones | Adjudicaciones agrupadas por ocid (suma, conteo) | 975.302 → 964.475; USD 30.952.880.306,92 → 30.952.880.306,92; suma de NumAdjudicaciones = 975.302 |

Origen: filas `TOTAL` del CSV. La tabla anterior nombra todos los pasos que devuelven tablas; los controles anuales para cada uno están en el CSV. La reducción de 10.827 filas al agrupar no es una exclusión: las adjudicaciones permanecen en el conteo del grupo. Hay 1.801 grupos con más de una adjudicación. Las exclusiones medidas son 0 por duplicados, 0 por moneda y 0 por negativos. Si aparecen claves duplicadas, las consultas detienen la evaluación y no eligen una fila arbitraria.

Controles adicionales medidos en las filas `Diagnóstico` del CSV:

- Q-01: 109.793 estimados vacíos; 0 estimados iguales a cero. `tiene_valor_estimado` es falso solo para null.
- Q-02: 0 importes corregidos y 0 importes ingresados poblados; ambas columnas se descartan.
- Q-06: 25 grupos de adjudicaciones tienen todos sus importes null. `MontoAdjudicado` debe seguir null. Hay 868.576 procesos con ambos importes, contados después de agrupar, sin construir el hecho.
- Q-07: 43 filas producen `NO_IDENTIFICADO`, con reparto 0, 7, 25, 9 y 2 de 2021 a 2025 (filas anuales del CSV). No se excluyen aquí.
- Q-10: 96.393 fechas pertenecen a otro año que el archivo; 14.495 están fuera de 2021 a 2025. Se conservan en estas consultas intermedias; el filtro temporal del hecho corresponde al trabajo posterior.
- Q-11: 16.307 detalles cambian al normalizar todo el espacio repetido, exterior y los saltos. No equivale al hallazgo de 796 diferencias CSV frente a JSON por saltos: aquel contraste tenía otro objeto (Calidad Q-11 y Q-12).
- S-02 y S-05: 0 adjudicaciones sin proceso; 0 vacíos en cada uno de `ocid`, `buyer_id`, `buyer_name`, `date` de Procesos.

`List.Sum([amount], Precision.Decimal)` suma solo valores no null y devuelve null cuando no hay ninguno, según [Microsoft Learn, List.Sum](https://learn.microsoft.com/en-us/powerquery-m/list-sum), consultado el 22/11/2026. No se usa `?? 0`. El conteo se obtiene con `Table.RowCount`, incluyendo las filas sin importe. Puede comprobarse aisladamente en una consulta temporal sin carga con `List.Sum({null, null}, Precision.Decimal)`, cuyo resultado documentado es null. Esta comprobación en Desktop aún no está ejecutada.

Para medir un paso interno se puede duplicar temporalmente la consulta, desactivar su carga y cambiar únicamente su cláusula final `in` por el paso elegido. Para grupos anuales se filtra `AnioProceso` antes de agrupar en esa copia, pues el resultado agrupado ya no conserva el año. Se usa **Transformar > Contar filas** para filas; otra referencia al mismo paso permite seleccionar la columna numérica y **Transformar > Estadísticas > Suma**. Para pasos textuales se convierte la copia con configuración regional Inglés (Estados Unidos). Nunca se suman importes de texto. Las copias temporales se eliminan al terminar y no se incorporan al modelo.

## Capturas y discrepancias

Se registra una captura por consulta con los pasos aplicados visibles y un control agregado de filas y sumas, antes y después de los filtros y del agrupado. En adjudicaciones se capturan además los grupos distintos, la suma de `NumAdjudicaciones` y los 25 grupos con monto vacío, mostrando solo sus conteos. Se registra fecha, consulta, paso y resultado observado. Se ocultan parámetros, barra de fórmulas con rutas, paneles que muestren carpetas personales y cualquier celda de personas, proveedores o contactos. Se prefieren tablas de agregados sin identificadores.

Si un control difiere, se detiene el avance al modelo y se registra el valor esperado, el observado y la diferencia exacta. Se revisan primero sellos y cinco archivos por tabla, `QuoteStyle.Csv`, UTF-8 y configuración regional; después los tipos, errores de conversión, duplicados y filtros. No se quitan errores ni se imputan ceros para cuadrar. Los negativos y las monedas rechazadas se cuentan por separado, en ese orden de pasos (primero moneda, luego negativos entre los retenidos). Una duplicidad exige contar las claves repetidas y resolver la fuente antes de continuar, sin ejecutar Quitar duplicados indiscriminadamente.

Q-09 exige conservar la salvedad metodológica: Calidad registra una brecha sin explicar de USD 1.095,11 millones entre el informe institucional preliminar de 2025 y los CSV transaccionales. No se ajustan los importes para eliminarla. Q-12 registra un caso de 2025 con cero en JSON y vacío en CSV: permanece vacío y fuera de la desviación de P2. Este trabajo no repite la comparación con JSON; la evidencia es el diagnóstico de H2.

## Alternativa mediante la interfaz

Se trabaja sobre referencias o copias de respaldo del archivo H2, conservando las fuentes originales. Los nombres de menús pueden variar con la versión.

1. Se conecta cada CSV anual con UTF-8 y tratamiento CSV de comillas. Se promueven encabezados por archivo y se agrega `AnioProceso` con el año del archivo. **Inicio > Anexar consultas > Tres o más tablas** combina los cinco años por origen. Se renombran los pasos como en la tabla de controles.
2. Se eligen las columnas mínimas. En Procesos se conserva temporalmente `buyer_name` para medir vacíos y después se retira. En Licitaciones se descartan `title`, `description` y fechas de etapa. En Adjudicaciones se descartan también `correctedValue_amount` y `enteredValue_amount`. Se convierten los blancos de importe en null y se cambia el tipo con configuración regional Inglés (Estados Unidos), conservando errores visibles. Para `date` se toma el texto inicial `AAAA-MM-DD` y se convierte a Fecha, sin cambio de zona horaria.
3. Se usa **Referencia** para un control de claves; **Agrupar por > Recuento de filas** identifica duplicados por `ocid` en Procesos y Licitaciones, y por `(ocid, id)` en Adjudicaciones. **Quitar duplicados** solo sirve para una referencia de claves distintas y su conteo; no elimina adjudicaciones múltiples ni sustituye la revisión de duplicados. La fuente conserva sus filas. Con la descarga actual, la diferencia es cero (CSV de controles).
4. En las tablas monetarias se filtra USD o moneda vacía acompañada de importe null; después se retienen importes no negativos o null. Se anotan ambos conteos de rechazo. Para métodos se reemplazan tabuladores, CR, LF y espacios no separables por espacio, se recortan extremos y se compactan espacios repetidos. **Limpiar** por sí solo no garantiza espacios entre palabras.
5. En Adjudicaciones se usa **Agrupar por > Avanzado**, clave `ocid`, suma de `amount` como `MontoAdjudicado` y recuento de filas como `NumAdjudicaciones`. Se revisa en la fórmula que la suma sea `List.Sum([amount], Precision.Decimal)` y el conteo incluya todos los registros. Se conserva exactamente el nombre del paso obligatorio.
6. En Procesos, **Agregar columna > Fecha > Año/Mes** toma la fecha de negocio y una columna personalizada calcula `IdTiempo = Año * 100 + Mes`. Se extraen los 13 dígitos tras `EC-RUC-`, validando prefijo, dígitos y sufijo; un identificador malformado produce `NO_IDENTIFICADO`. No se usa una extracción ciega de caracteres.
7. **Referencia**, selección de columnas y **Quitar duplicados** sobre la clave de negocio, seguidos de **Columna de índice > Desde 1**, son el punto de partida de dimensiones. **Combinar consultas** permite traer sus claves al hecho. Estos pasos pertenecen a la construcción posterior del modelo, no se ejecutan como parte de este encargo. Una combinación de medidas solo se hace después del agrupado de adjudicaciones.

## Puntos de enganche con el modelo

| Destino posterior | Columnas intermedias | Regla del diseño aprobado |
|---|---|---|
| DimTiempo | Procesos.`date`, `IdTiempo` | Clave mensual AAAAMM; `AnioProceso` es solo auxiliar; fechas fuera de 2021 a 2025 se contarán antes de excluirse del hecho |
| DimEntidad | Procesos.`buyer_id`, `RUC_13` | Coincidencia completa o raíz con semilla; raíz enlaza con `RucRaiz`; nunca por nombre; clasificación y exclusiones pertenecen a #68/#70 |
| DimMetodo | Licitaciones.`procurementMethod`, `procurementMethodDetails` | Normalización de espacio ya aplicada; colapso de convenios a procedimiento y miembro Sin licitación pertenecen a #70 |
| FactContratacion | `ocid` de las tres consultas | Procesos como lado base; unir Licitaciones única y Adjudicaciones agrupada sin multiplicar filas |
| Medidas del hecho | Licitaciones.`value_amount`, `tiene_valor_estimado`; Adjudicaciones.`MontoAdjudicado`, `NumAdjudicaciones` | Renombrar value_amount a ValorEstimado, derivar NumProcesos y ProcesoConAmbosImportes en #70; sin tasas |

## Reproducción independiente y estado de verificación

Desde la raíz de la copia, con la ruta de derivados de la carpeta principal como argumento:

```powershell
python -I scripts/expected_controls_h3.py RUTA_DERIVADOS --output docs/h3/evidencia/NUEVO_CONTROL.csv
python -I tests/unit/test_expected_controls_h3.py
uv sync --locked
uv run ruff check
uv run ruff format --check
uv run pytest -q
```

La salida nunca sobrescribe un archivo existente; una nueva medición usa un nombre nuevo. La prueba de CLI comprueba esta protección y genera cinco años sintéticos. Se probaron también varias adjudicaciones, grupos íntegramente null, cero real, identificador malformado, fecha distinta del año del archivo, saltos entre comillas, duplicados y exclusiones monetarias. Resultado local: ocho pruebas sintéticas pasan con Python aislado. El script sobre datos reales reprodujo todas las cifras objetivo sin diferencias.

La sincronización de `uv` falló por acceso al caché; con caché dentro de la copia falló la descarga por restricción de red. Ruff y pytest del entorno existente tampoco pudieron ejecutarse por permisos de lectura/ejecución. No hay resultado satisfactorio de lint, formato ni suite completa. Estos cuatro comandos deben repetirse en un entorno con permisos antes de integrar. La ejecución de las consultas M y la comparación observada en Power BI corresponden al líder y aún no están verificadas.
