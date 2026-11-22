# Construcción de dimensiones y hecho en Power Query

El líder ejecuta este procedimiento en Power BI Desktop. Ninguna consulta M de esta
construcción se ha ejecutado aún. La revisión M es estática. Los resultados esperados
se calcularon independientemente con Python 3.14 y `Decimal` sobre los CSV reales,
sin modificar las entradas. Las pruebas sintéticas no acreditan ejecución en Power BI.

## Fuentes y reglas

- **F1:** CSV del portal SERCOP descargados el 21/11/2026, cinco archivos anuales por
  tabla (`releases`, `tender`, `awards`), inventariados en [Fuentes de H2](../h2/fuentes.csv).
- **F2:** [semilla aprobada](../../warehouse/seeds/entity_classification.csv), con las
  decisiones ya aplicadas del [archivo de decisiones](../../warehouse/seeds/entity_classification_decisions.csv).
  La clasificación y sus limitaciones constan en [Semilla de entidades](semilla-entidades.md),
  secciones 3.5, 4.3 y 6. No se cambió la semilla ni se incorporaron nuevas aprobaciones.
- **R1:** [diseño aprobado](diseno-dimensional.md), secciones 6.1 a 6.5 y 9.2:
  grano por `ocid`, fecha `releases.date`, admisión únicamente aprobada, conflictos
  por raíz excluidos, sin SCD tipo 2 en H3, vacío distinto de cero.
- **R2:** guía H3 del profesor, sección 5, pasos 4 a 8: Referencia, selección de
  columnas, Quitar duplicados, índice desde 1, Combinar consultas y desactivar
  la carga de intermedias. R1 fija la excepción mensual `IdTiempo = AAAAMM`.
- **E1:** [modelo-esperado.csv](evidencia/modelo-esperado.csv), generado por
  [expected_model_h3.py](../../scripts/expected_model_h3.py) sobre F1 y F2 el 22/11/2026.
  Todas las cifras de este runbook proceden de E1, salvo los valores de contraste
  identificados expresamente como R1 o F2. Las sumas se expresan en USD.

## Preparación y orden de creación

Se utiliza la copia H3 del archivo H2 y se completan antes las
[transformaciones intermedias](runbook-transformaciones.md). No se duplican ni
se renombran las tres consultas existentes: `Procesos_SERCOP`,
`Licitaciones_SERCOP`, `Adjudicaciones_SERCOP`.

Se conservan los parámetros de texto `RutaDerivados` y `RutaDatosCrudos` del H2.
Se crea **Administrar parámetros > Nuevo parámetro**, nombre `RutaSemillas`, tipo
Texto, con la carpeta local que contiene `entity_classification.csv`. Las rutas
se configuran en los parámetros, no se escriben dentro del código M. Las consultas
nuevas no necesitan volver a leer el catálogo mediante `RutaDatosCrudos`.

En cada paso se crea una consulta con el nombre exacto de la tabla siguiente.
Se abre **Editor avanzado**, se pega el contenido completo del archivo enlazado
y se confirma. Para las referencias se usa clic derecho **Referencia**, nunca
**Duplicar**. La cláusula `Origen` de cada archivo conserva esa dependencia.

| Orden | Consulta y archivo para pegar | Carga | Comprobación antes de seguir |
|---|---|---|---|
| 1 | [Semilla_Entidades](../../reports/powerbi/h3/queries/Semilla_Entidades.pq), consulta en blanco | No | F2: 6.100 compradores distintos, raíz compatible con el patrón; `RaizAprobada` exige tipo único y todas las filas aprobadas |
| 2 | [Origen_Modelo](../../reports/powerbi/h3/queries/Origen_Modelo.pq), referencia a Procesos | No | E1: 1.007.920 filas y `ocid` distintos; las combinaciones monetarias conservan el grano |
| 3 | [ControlAlcance](../../reports/powerbi/h3/queries/ControlAlcance.pq), referencia a Origen_Modelo | No | E1, grupo `control_alcance`: mismas combinaciones de motivo y año; al sumar los años reproduce las exclusiones agregadas de abajo |
| 4 | [DimTiempo](../../reports/powerbi/h3/queries/DimTiempo.pq), consulta en blanco | Sí | E1: 60 filas y claves distintas; enero de 2021 a diciembre de 2025, sin huecos |
| 5 | [DimEntidad](../../reports/powerbi/h3/queries/DimEntidad.pq), referencia a Origen_Modelo | Sí | E1: 587 filas y claves distintas: 586 raíces admitidas más Sin clasificar; una fila por raíz |
| 6 | [DimMetodo](../../reports/powerbi/h3/queries/DimMetodo.pq), referencia a Licitaciones | Sí | E1: 28 filas, claves y pares únicos: 27 pares nacionales más Sin licitación |
| 7 | [FactContratacion](../../reports/powerbi/h3/queries/FactContratacion.pq), referencia a Origen_Modelo | Sí | E1: 275.100 filas y `ocid` distintos, claves sin nulos; suma adjudicada 5.511.799.162,58 y estimada 3.840.396.283,44 |

`ControlAlcance` queda como conexión para revisar agregados y no forma parte de la
estrella; podrá cargarse como tabla desconectada al preparar la página de control.
Las tres consultas de origen de H3, la semilla y `Origen_Modelo` mantienen
**Habilitar carga** desactivado. En las cuatro tablas dimensionales y de hecho se
activa y se usa **Cerrar y aplicar** después de revisar todos los controles.

## Comprobaciones por consulta

**Semilla y alcance.** Se busca primero el `buyer_id` completo, después su raíz
validada. Una coincidencia exacta no supera el veto de una raíz con tipos distintos
o con alguna fila sin aprobar (R1, sección 6.5). Los identificadores malformados,
sin coincidencia, propuestos y dudosos se excluyen del hecho. El filtro temporal
se evalúa primero, por lo que cada proceso se cuenta en un único motivo. La
vigencia se conserva como información, sin filtrar procesos por `valid_from` o
`valid_to`. Los institutos sin respaldo permanecen fuera conforme a F2.

**Origen monetario.** La combinación con `Adjudicaciones_SERCOP` utiliza su salida
del paso **Adjudicaciones agrupadas por ocid (suma, conteo)**. Nunca se expande
`awards` fila a fila. El valor estimado queda una sola vez por proceso. Solo el
conteo de adjudicaciones sin filas se convierte en cero; ningún importe se imputa.

**DimTiempo.** El código genera meses consecutivos, no fechas observadas. Se revisan
los extremos `202101` y `202512`, 60 claves distintas y doce meses por año (E1 y R1).
Se conserva `FechaMes` como fecha y `IdTiempo` como entero. La jerarquía esperada es
`Anio > NombreMes`, con `NombreMes` ordenado por `Mes` y `AnioMes` por `IdTiempo`.
La creación de esa jerarquía en la vista de modelo corresponde al siguiente runbook.

**DimEntidad.** Se toma como universo la referencia al origen admitido, se conserva
solo la raíz y se quitan duplicados. El nombre se obtiene de una sola fila de F2 por
raíz: prioridad al catálogo (`name_source = catalogo`) y desempate estable por
`buyer_id`. Así se aplica Q-13 sin unir por nombre. Se añaden las etiquetas
Presidencia, Ministerio e Instituto y la fila Sin clasificar antes de numerar.
`IdEntidad` empieza en 1. La fila Sin clasificar es una salvaguarda, con cero filas
esperadas en el hecho; una clave sin pareja detiene la construcción, no se reasigna.

**DimMetodo.** Se referencia el dominio nacional limpio de Licitaciones, conservando
los dos atributos del método. Los detalles de Catálogo electrónico se truncan antes
de ` en el convenio`; un detalle vacío produce Sin detalle. Se quitan duplicados,
se añade Sin licitación y se ordena antes del índice desde 1. Las etiquetas en español
son la elección aprobada del equipo (R1, sección 9.2), no códigos de la fuente.

**FactContratacion.** Se referencia únicamente el sector admitido y se combina con
cada dimensión, mediante unión externa izquierda. Las expansiones traen solamente
la clave; la clave temporal expandida comprueba pertenencia al calendario. Se
conservan `IdTiempo`, `IdEntidad`, `IdMetodo`, `ocid`, `MontoAdjudicado`,
`ValorEstimado`, `NumProcesos`, `NumAdjudicaciones`, `ProcesoConAmbosImportes`.
`ocid` es la dimensión degenerada aprobada, útil para conciliar procesos sin otra
tabla; es la única columna de texto. La marca de ambos importes es entero 0/1,
cuya suma cuenta procesos, no un booleano ni una tasa. No se conserva `AnioProceso`.

Las guardas de M detienen con `error` si se duplican claves de dimensión o `ocid`,
si una clave del hecho no tiene pareja o si cambian filas o cualquiera de las dos
sumas al combinar dimensiones. Se comparan los totales del origen **ya filtrado**,
no los del origen nacional. El CSV no garantiza por sí mismo que M produzca esos
resultados: la comprobación final se hace en Desktop.

## Cadena de totales y motivos de cada salto

| Etapa, en orden | Filas | Σ MontoAdjudicado | Σ ValorEstimado | Motivo del cambio |
|---|---:|---:|---:|---|
| Nacional descargado | 1.007.920 | 30.952.880.306,92 | 25.072.968.705,53 | Cinco archivos anuales de procesos F1; importes unidos después de agrupar adjudicaciones |
| Sin ocid duplicados | 1.007.920 | 30.952.880.306,92 | 25.072.968.705,53 | No hay repetidos; se comprueba, no se eliminan filas arbitrarias |
| Ventana 2021-2025 | 993.425 | 28.187.165.730,91 | 22.805.452.044,61 | Se excluyen los procesos fechados en 2026 |
| Sector clasificado | 275.100 | 5.511.799.162,58 | 3.840.396.283,44 | Se excluyen fuera de alcance y dudosos o sin clasificar según F2 |
| FactContratacion | 275.100 | 5.511.799.162,58 | 3.840.396.283,44 | Tras combinar dimensiones no deben cambiar filas ni sumas |

Fuente de todas las celdas numéricas: E1, grupo `cadena`. El último salto es el
resultado esperado de una combinación con claves únicas, calculado por Python;
la ejecución y conservación efectiva en M no se han confirmado.

| Exclusión secuencial | Filas | Σ MontoAdjudicado | Σ ValorEstimado |
|---|---:|---:|---:|
| Fuera de la ventana 2021-2025 | 14.495 | 2.765.714.576,01 | 2.267.516.660,92 |
| Fuera del gobierno central | 669.686 | 21.864.546.771,50 | 18.264.813.598,78 |
| Dudoso o sin clasificar | 48.639 | 810.819.796,83 | 700.242.162,39 |

Fuente: E1, grupos `exclusion` y `alcance`. El grupo `control_alcance` contiene
los mismos motivos y años que la consulta M. La suma de sector y exclusiones
reproduce exactamente ambas sumas y las filas nacionales; no hay solapamientos.
Los 43 procesos con comprador malformado señalados por F2 están incluidos en el
grupo dudoso, no constituyen una cuarta exclusión que deba restarse otra vez.

No hay diferencias respecto de R1: coinciden los 993.425 procesos y los
USD 28.187.165.730,91 de la ventana, así como las dimensiones de tiempo y método.
Tampoco hay diferencias con F2, sección 4.3: coinciden las cuatro categorías de
alcance y sus montos adjudicados exactos. Los USD 5.511,80 millones del resumen de
F2 son el redondeo de USD 5.511.799.162,58, no una discrepancia. R1 dejaba sin medir
el tamaño de DimEntidad y el estimado por etapa; E1 aporta esas cifras sin cambiar
las reglas. Las 587 filas de DimEntidad incluyen el miembro de salvaguarda.

## Procesos del hecho por tipo y año

| Año de releases.date | Presidencia | Ministerio | Instituto | Total |
|---|---:|---:|---:|---:|
| 2021 | 29 | 46.248 | 0 | 46.277 |
| 2022 | 132 | 55.155 | 0 | 55.287 |
| 2023 | 84 | 64.361 | 0 | 64.445 |
| 2024 | 28 | 64.006 | 0 | 64.034 |
| 2025 | 40 | 45.017 | 0 | 45.057 |
| Total | 313 | 274.787 | 0 | 275.100 |

Fuente: E1, grupo `tipo_anio`; las sumas y totales son aritmética sobre ese grupo.
Instituto tiene cero procesos admitidos porque F2 conserva esas clasificaciones
como dudosas, no porque se haya probado ausencia de contratación de institutos.

## Alternativa mediante clics

1. Para Entidad se crea **Referencia** de Origen_Modelo y se filtra Motivo = En el
   hecho; se elige solo RUC_13 y se usa **Quitar duplicados**. Se combina con una
   referencia de semilla ordenada por origen del nombre y comprador, reducida a una
   fila por raíz. Se expanden solo los atributos de DimEntidad. Se agrega la fila
   Sin clasificar y se utiliza **Agregar columna > Columna de índice > Desde 1**,
   renombrada IdEntidad. La clasificación previa debe conservar el veto de raíz;
   no se sustituye por una combinación directa que admita todo RUC de la dimensión.
2. Para Método se crea **Referencia** de Licitaciones, se eligen método y detalle,
   se aplica el colapso de convenio con una columna personalizada, se usa
   **Quitar duplicados** y se agrega Sin licitación. Se ordena por el par, se añade
   **Columna de índice > Desde 1** y se renombra IdMetodo. Se agregan las etiquetas
   del diseño. Para Tiempo se pega la generación mensual M en una consulta en blanco.
3. Para el hecho se crea **Referencia** de Origen_Modelo y se filtra En el hecho.
   Con **Inicio > Combinar consultas** se une por RUC_13/RucRaiz a DimEntidad, por
   método y procedimiento a DimMetodo, y por IdTiempo a DimTiempo. Se usa unión
   externa izquierda y **Expandir**, trayendo solo las claves. Se comprueban filas,
   claves sin pareja y ambas sumas antes y después de cada combinación.
4. Se agregan las constantes y la marca entera de ambos importes, se eligen solo las
   nueve columnas finales y se revisan tipos. No se usa Reemplazar null por cero en
   importes. El origen ya debe tener las adjudicaciones agrupadas antes de este paso.
5. Se conserva la carga únicamente de las tres dimensiones y el hecho. Se comparan
   los controles con E1 antes de **Cerrar y aplicar**. Si se usa la interfaz como
   alternativa, se mantienen las guardas del Editor avanzado; las previsualizaciones
   limitadas no sustituyen conteos completos ni comprobaciones de unicidad.

## Capturas y continuación

Se capturan por consulta los pasos aplicados y un control agregado de filas y
claves distintas; para el hecho, además, las sumas antes y después de las
combinaciones y cero claves sin pareja. Se captura el control por motivo y año,
las fechas extremas del calendario y el miembro Sin clasificar sin procesos.
Se registra fecha y valores observados. Se ocultan rutas personales y se evitan
datos de proveedores, contactos o personas; se prefieren agregados.

Si hay una diferencia se detiene la carga y se registra esperado, observado y
diferencia. Se revisan sellos, tipos, semilla aplicada y duplicidad del lado derecho;
no se eliminan errores ni se imputan importes para cuadrar.

Las relaciones y la página de prueba corresponden a `runbook-modelo.md`, trabajo
posterior. Solo se deja la lista esperada según R1: `DimTiempo[IdTiempo]`,
`DimEntidad[IdEntidad]` y `DimMetodo[IdMetodo]` hacia sus columnas homónimas de
`FactContratacion`, cada relación **1 a varios, filtro único dimensión a hecho**.
No se han creado relaciones, jerarquías ni visualizaciones de prueba.

## Reproducción y verificación del patch

La ejecución real utilizó Python 3.14 aislado, con rutas suministradas como argumentos:

```powershell
python -I scripts/expected_model_h3.py "CARPETA_DERIVADOS" `
  "warehouse/seeds/entity_classification.csv" --output "SALIDA_NUEVA.csv"
```

La salida existente nunca se sobrescribe. Se produjo E1 con solo agregados y LF.
El script rechaza fuentes anuales ambiguas, claves duplicadas, raíces de semilla
incompatibles y adjudicaciones o licitaciones sin proceso. Aplica los mismos filtros
de moneda y negativos de las consultas intermedias. Las sumas conservan Decimal y
los importes ausentes permanecen ausentes.

Verificación del 22/11/2026: `uv sync --locked`, `uv run ruff check`, `uv run ruff format --check` y `uv run pytest -q` (223 pruebas) pasan; dos ejecuciones del script sobre F1 y F2 producen el mismo CSV de 43 controles. Ninguna consulta de dimensión ni de hecho se ha ejecutado aún en Power BI: las cifras de este runbook son las esperadas, no las observadas.
