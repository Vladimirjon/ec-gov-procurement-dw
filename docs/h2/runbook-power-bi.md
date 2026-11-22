# Hito 2: conexión y perfilado en Power BI

Procedimiento para el líder. El líder ejecutó las cuatro consultas en Desktop y comprobó los totales combinados 2021–2025 el 21/11/2026. La actualización desde otra ubicación no se probó (decisión del líder, ver Cierre del #63). No se corrigen datos en H2. `gob.ec` se omite: es apoyo nominal ([fuente de entidades](fuente-entidades.md)).

Versión instalada de Power BI Desktop: 2.159.1231.0 (paquete de Microsoft Store, verificado el 21/11/2026). En la interfaz observada: **Column quality**, **Column distribution** y **Column profile**.

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
12. Antes de cerrar, en **Archivo > Opciones y configuración > Opciones > Archivo actual > Carga de datos** desmarca la detección automática de relaciones (en la interfaz en inglés: *Autodetect new relationships after data is loaded*). **Cerrar y aplicar** y guarda como `deliverables/h2/Proyecto_Grupo5_Hito2.pbix`. Después abre la **Vista de modelo** y, si Desktop creó relaciones, elimínalas: H2 solo conecta y diagnostica; las relaciones se diseñan en H3 (relaciones 1 a varios con filtro único). Anota en Ejecución y desvíos cuántas había. El `.pbix` **no se versiona** (decisión del líder, 21/11/2026; está en `.gitignore`): se entrega por el aula virtual. Los parámetros guardan rutas locales dentro del `.pbix`; no lo compartas fuera del curso.

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

Las columnas CSV sin cambio de tipo son texto: sus mínimos y máximos son alfabéticos y no permiten sumar como números. **Solo con aprobación del líder**, se puede crear una consulta temporal `Control_Totales`, deshabilitar su carga (clic derecho sobre la consulta > habilitar carga, si aparece marcada) y pegar el siguiente M en Editor avanzado. Usa copias de las columnas, convierte con cultura `en-US`, preserva errores y nulos, y no carga al modelo. Es una comprobación temporal, no limpieza de las consultas originales; se comprobó en Desktop con una consulta temporal equivalente y dos decimales para comparar. Si hay errores o discrepancias, registrarlos; no sustituirlos por cero.

Consulta temporal `Control_Filas` (misma regla: carga deshabilitada, no es limpieza), usada para S02:

```powerquery
let
    Resultado = #table({"Tabla", "Filas"}, {
        {"Procesos", Table.RowCount(Procesos_SERCOP)},
        {"Licitaciones", Table.RowCount(Licitaciones_SERCOP)},
        {"Adjudicaciones", Table.RowCount(Adjudicaciones_SERCOP)}
    })
in
    Resultado
```

Consulta temporal `Control_Totales`, usada para S03:

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

1. `S01-vista-previa-utf8.png`: vista previa, codificación y delimitador.
2. `S02-control-filas.png`: conteos agregados de las tres tablas SERCOP.
3. `S03-control-totales.png`: sumas agregadas de adjudicado y estimado.
Perfil de conjunto completo: no hay capturas publicadas. El líder lo realizó y lo declaró el 21/11/2026 (Calidad de columna, Distribución y Perfil de columna con «todo el conjunto de datos»); las capturas originales muestran rutas personales y el líder decidió no publicarlas. S01 a S03 son la evidencia gráfica del repositorio.

Si en el futuro se agrega una captura, debe mostrar solo la tabla y no el panel Queries (muestra el valor de los parámetros de ruta, con el nombre de usuario). S02 y S03 ya publicadas tienen esos valores tapados.

## Ejecución y desvíos registrados

- El líder conectó las cuatro consultas, activó el perfil completo, aplicó los cambios y guardó el PBIX el 21/11/2026. Las capturas guardadas muestran la vista previa UTF-8 (`S01`), los tres conteos (`S02`) y las dos sumas (`S03`). Las consultas temporales `Control_Filas` y `Control_Totales` aparecen sin carga en el editor.
- Perfil completo: el líder lo activó y lo declaró hecho el 21/11/2026; las capturas originales se descartaron para publicación porque muestran parte de una ruta personal (decisión del líder: no publicarlas). S02 y S03 mostraban el comienzo de las rutas en el panel de parámetros; se taparon antes de subirlas (el archivo original sigue solo en el equipo del líder).
- Power BI creó tres relaciones automáticas al aplicar, verificadas en la plantilla `.pbit` y en la Vista de modelo: `Licitaciones_SERCOP.ocid` a `Procesos_SERCOP.ocid` (uno a uno, filtro en ambas direcciones), `Adjudicaciones_SERCOP.ocid` a `Procesos_SERCOP.ocid` y `Adjudicaciones_SERCOP.release_id` a `Licitaciones_SERCOP.release_id` (cardinalidad no definida). No son un diseño validado: H3 define relaciones 1 a varios con filtro único. El líder las eliminó y guardó el `.pbix` el 21/11/2026 (declaración del líder; el revisor no puede abrir el `.pbix`).
- Verificación estática con la plantilla `.pbit` exportada por el líder el 21/11/2026 (sin datos, parámetros sin valor): las cuatro consultas coinciden con los `.pq` del repositorio (la de Procesos sin el comentario inicial), todas leen las rutas desde `RutaDerivados` y `RutaDatosCrudos` (sin rutas fijas) y no tienen el paso «Tipo cambiado»; además están las consultas temporales `Control_Filas` y `Control_Totales`. Esto no sustituye una actualización real en otra carpeta.  El catálogo MDEP conserva columnas genéricas y filas de títulos y notas.
- PBIX guardado: 243.078.890 bytes. Supera el límite de 100 MB de GitHub: por decisión del líder (21/11/2026) no se versiona y se entrega por el aula virtual. El tiempo no se cronometró. Los parámetros guardan rutas personales en el archivo.
- El perfil del catálogo completo incluye títulos, encabezados y notas; sus porcentajes no son exclusivamente de los registros institucionales.

## Cobertura de P1 a P3

La matriz de preguntas está en `docs/requirements/hito1.md`, Parte 2 y las cabeceras se comprobaron en los CSV de cada año:

| Pregunta | Campos disponibles en las fuentes conectadas | Limitación |
|---|---|---|
| P1 | `releases`: `ocid`, `buyer_id`, `date`; `tender`: `ocid`, `procurementMethod`; `awards`: `ocid`, `amount`; catálogo MDEP | El tipo de entidad y la clasificación de gobierno central no están resueltos. |
| P2 | Los anteriores y `tender.value_amount` | Hay importes ausentes; unir y agrupar adjudicaciones corresponde a H3. |
| P3 | `releases.date`, `buyer_id` y `awards.amount` | La fecha de negocio, la serie mensual y la clasificación histórica requieren resolución posterior. |

El catálogo de 2026 no ofrece por sí solo la jerarquía ni la vigencia histórica para clasificar el gobierno central ([fuente-entidades.md](fuente-entidades.md), secciones 6 y 7). La disponibilidad de campos no demuestra que ya se puedan responder las preguntas en el modelo.

## Cierre del #63 (decisiones del líder, 21/11/2026)

Criterios del issue que se cumplen: consultas conectadas solo con pasos de conexión y con nombre claro; originales intactos (6 SHA-256 coinciden); filas y sumas coinciden con #62; rutas como parámetros (verificado en la plantilla `.pbit`); capturas sin valores de personas; runbook con desvíos anotados.

Criterios que el líder dispensó:

1. El `.pbix` no se versiona (243.078.890 bytes; GitHub rechaza más de 100 MB). Está en `.gitignore` y se entrega por el aula virtual.
2. Prueba de actualización desde otra carpeta: no se hace; la portabilidad es un criterio del issue, no de la guía del profesor, y queda verificada de forma estática.
3. Capturas de perfil de conjunto completo: no se publican; el líder declara que el perfilado se hizo con todo el conjunto.

La revisión y aprobación del PR las hace el líder (la protección de `main` exige una aprobación).
