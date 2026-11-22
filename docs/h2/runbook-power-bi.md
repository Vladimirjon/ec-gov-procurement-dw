# Hito 2: conexión y perfilado en Power BI

Procedimiento para el líder. Las consultas M y este procedimiento **no se han ejecutado ni verificado en Desktop**. Solo se probó 2025 anteriormente; 2021–2024 y la combinación de cinco años siguen sin probarse en Desktop ([decisión de conexión, §8](decision-formato-conexion.md)). No se corrigen datos en H2. `gob.ec` se omite: es apoyo nominal ([fuente de entidades](fuente-entidades.md)).

Versión de Power BI Desktop: __________. Nombre mostrado para calidad de columna(s): __________.

## Integridad antes de conectar

En PowerShell desde la carpeta principal del repositorio, ejecutar lo siguiente. Solo lee archivos; compara cada descarga CSV válida y el Excel con sus registros, evitando los intentos sin hash de 2023 y el duplicado de 2024. Si aparece `False` o falta un archivo, detenerse y anotar el error; no sobrescribir datos.

```powershell
$registros = Import-Csv 'docs/h2/evidencia/descargas-sercop.csv' | Where-Object { $_.url -match 'type=csv' -and $_.sha256 }
$registros += Import-Csv 'docs/h2/evidencia/descargas-entidades.csv' | Where-Object { $_.file_name -eq 'catalogo_instituciones_mdep.xlsx' }
$registros | ForEach-Object {
    $archivo = Join-Path $_.folder $_.file_name
    [pscustomobject]@{ Archivo = $archivo; Coincide = (Get-FileHash -LiteralPath $archivo -Algorithm SHA256).Hash -eq $_.sha256 }
} | Format-Table -AutoSize
```

## Pasos 3 a 12 de la guía

3. En Power BI Desktop, **Inicio > Obtener datos > Texto/CSV**. Elige en `data/derivados/sercop-portal-csv-2025-20261121-141748/` el archivo `releases_2025.csv`.
4. En la vista previa comprueba origen 65001 UTF-8 y delimitador coma. Toma S01. Cancela esta conexión de prueba: los `.pq` se conectan por separado. Si los nombres en tu versión difieren, anótalos en Desvíos.
5. En Inicio abre **Transformar datos** para entrar al Editor de Power Query. Crea dos parámetros de texto con **Administrar parámetros > Nuevo parámetro**: `RutaDerivados` con la ruta de la carpeta `data/derivados` de la carpeta principal y `RutaDatosCrudos` con la ruta de `data/datos_crudos` de la carpeta principal. Son rutas de carpetas, sin comillas. Ambos parámetros son obligatorios y sus valores son las rutas locales completas. Los menús pueden variar por versión.

   Crea una consulta en blanco (Inicio > Nuevo origen > Consulta en blanco; el nombre exacto puede variar), selecciónala y abre **Editor avanzado**. Reemplaza todo el contenido pegando el archivo `reports/powerbi/h2/queries/Procesos_SERCOP.pq`; confirma. Repite con `Licitaciones_SERCOP.pq`, `Adjudicaciones_SERCOP.pq` y `Entidades_MDEP.pq`. Si solicita credenciales para archivos locales, selecciona el acceso apropiado a archivos locales. Si aparece un error copia su texto exacto; no cambies los originales.
6. En Configuración de consulta, asigna a cada consulta exactamente el nombre de su archivo sin `.pq`. Revisa Pasos aplicados: si Desktop agrega **Tipo cambiado**, elimínalo con la X. No agregues filtros ni conversiones. Las tres consultas CSV promueven los encabezados de cada archivo antes de combinarlos. La consulta MDEP solo navega a la hoja: tendrá columnas genéricas como `Column1`; conserva títulos, fila 6 con encabezados y notas al pie (Q-E03). En H3 se propondrá resolver esa estructura; no ahora.
7. En **Vista**, activa Calidad de columna(s), Distribución de columnas y Perfil de columna. Abajo a la izquierda, cambia el perfil de las primeras 1.000 filas a **todo el conjunto de datos**. Espera a que termine; toma S02. El nombre exacto de las opciones depende de la versión.
8. Recorre las columnas utilizadas y registra tipo observado y esperado, vacíos, distintos, mínimo y máximo disponibles en el diccionario. Prioriza `ocid`, `buyer_id`, `buyer_name`, `date` en Procesos; `ocid`, `procurementMethod`, `procurementMethodDetails`, `value_amount`, `value_currency` en Licitaciones; `ocid`, `id`, `amount`, `currency`, `date` en Adjudicaciones; y las columnas correspondientes a sector, entidad, EOD, RUC y nombre en Entidades. Revisa el resto de campos usados en las preguntas. No captures valores de personas o proveedores.
9. Anota el grano de cada consulta (comentario al inicio de cada `.pq`) y comprueba combinaciones repetidas de las claves sin eliminar duplicados. Para MDEP distingue las filas de títulos y notas de los registros reales. Los controles agregados de #62 y el hallazgo Q-E02 son referencia, no sustituyen una comprobación en Desktop.
10. Registra el conteo observado y compáralo con la tabla siguiente. No conviertas vacíos en cero. Para sumar, consulta al líder sobre el control temporal descrito abajo.
11. Registra en el libro de Excel los problemas observados, dimensión, evidencia, impacto y acción propuesta para H3; completa la matriz de cobertura para P1–P3. Anota diferencias y desvíos sin forzarlos.
12. **Cerrar y aplicar** y guarda como `deliverables/h2/Proyecto_Grupo5_Hito2.pbix`. Mide el tamaño antes de añadirlo a Git y avisa al líder si supera ~50 MB; GitHub rechaza archivos mayores de 100 MB. No actives Git LFS ni elimines columnas sin la decisión correspondiente. Los parámetros guardan rutas locales en el `.pbix`; revisa su exposición antes de compartirlo.

## Totales de control

Origen: [perfilado SERCOP §2](perfilado-sercop.md) y `evidencia/perfil-calidad-sercop-resumen.csv`. Son nacionales y corresponden al año del archivo, que no necesariamente coincide con el año de la fecha del proceso.

| Archivo | Releases | Tender | Awards |
|---|---:|---:|---:|
| 2021 | 167.058 | 165.616 | 166.983 |
| 2022 | 212.324 | 203.147 | 200.173 |
| 2023 | 217.913 | 213.841 | 212.989 |
| 2024 | 219.185 | 212.386 | 210.445 |
| 2025 | 191.440 | 186.358 | 184.712 |
| Total | 1.007.920 | 981.348 | 975.302 |

Suma `awards.amount`: USD 30.952.880.306,92; `tender.value_amount`: USD 25.072.968.705,53. Si no coinciden, revisa primero `QuoteStyle.Csv` en tender, después UTF-8 y el paso Tipo cambiado; registra la diferencia real. Para contingencia de solo 2025, deja constancia del recorte y compara con la fila de 2025 y los importes del CSV de resumen; no afirmes cobertura de cinco años.

Las columnas CSV sin cambio de tipo son texto: sus mínimos y máximos son alfabéticos y no permiten sumar como números. **Solo con aprobación del líder**, se puede crear una consulta temporal `Control_Totales`, deshabilitar su carga (clic derecho sobre la consulta > habilitar carga, si aparece marcada) y pegar el siguiente M en Editor avanzado. Usa copias de las columnas, convierte con cultura `en-US`, preserva errores y nulos, y no carga al modelo. Es una comprobación temporal, no limpieza de las consultas originales; no se ha probado en Desktop. Si hay errores o discrepancias, registrarlos; no sustituirlos por cero.

```powerquery
let
    Convertir = (valores as list) => List.Transform(valores, each if _ = null or _ = "" then null else Number.FromText(_, "en-US")),
    Resultado = #table({"Control", "Filas", "Suma"}, {
        {"Adjudicaciones", Table.RowCount(Adjudicaciones_SERCOP), List.Sum(Convertir(Adjudicaciones_SERCOP[amount]))},
        {"Licitaciones", Table.RowCount(Licitaciones_SERCOP), List.Sum(Convertir(Licitaciones_SERCOP[value_amount]))},
        {"Procesos", Table.RowCount(Procesos_SERCOP), null}
    })
in
    Resultado
```

Para verificar portabilidad, prepara otra carpeta con la misma estructura y los archivos correspondientes, cambia solo `RutaDerivados` y `RutaDatosCrudos`, actualiza en una sesión limpia y comprueba que cargan y mantienen totales. Conserva los originales intactos. Esta prueba requiere ejecutarse en Desktop.

## Capturas

Guárdalas en `docs/h2/evidencia/capturas/`; revisa antes de compartir que no se vean valores de personas o proveedores. Evita `title`, `description` y otras columnas libres que puedan contener datos personales.

1. `S01-vista-previa-utf8.png`: vista previa, codificación y delimitador, sin valores sensibles.
2. `S02-perfil-conjunto-completo.png`: barra de estado con el perfil completo.
3. `S03-procesos-calidad.png`: calidad/distribución/perfil de columnas de identificación de entidad pública.
4. `S04-licitaciones-calidad.png`: calidad/distribución/perfil de método o monto, sin texto libre.
5. `S05-adjudicaciones-calidad.png`: calidad/distribución/perfil de monto, sin proveedores.
6. `S06-entidades-calidad.png`: perfil de una columna de entidad pública del catálogo.
7. `S07-totales.png`: control agregado, si se aprobó y ejecutó, sin datos individuales.

## Desvíos
