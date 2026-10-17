# Glosario del proyecto

- **Estado:** borrador para revisión del líder. Responde al
  [issue #13](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/13).
- **Fecha:** 2026-10-17

Define los términos que usa todo el equipo en las entregas, los ADR y el
código. Cada término lleva su **fuente**, para que nadie tenga que fiarse de
una definición sin respaldo.

## Cómo leerlo

- Los términos están agrupados por tema y ordenados según su aparición en el
  flujo del proyecto, no alfabéticamente. Usa la búsqueda del navegador.
- Los nombres técnicos van en inglés y entre comillas invertidas, por ejemplo
  `ocid` o `buyer.id`, tal como aparecen en la fuente o en el código.
- Cada definición separa lo que **define el estándar o la teoría** de lo que
  **decidió o midió el proyecto**. Lo medido es evidencia de reconocimiento
  (descargas de 2025), nacional y no la foto definitiva.
- Lo marcado como **[PENDIENTE]** no es una decisión; depende del líder o de
  una verificación posterior. Se conserva igual que en el documento de origen.
- Las fuentes con ruta (`docs/...`) son documentos de este repositorio. Las
  referencias externas se listan en [Referencias](#referencias).

## 1. Contratación pública y alcance

| Término | Definición | Fuente |
|---|---|---|
| **Proceso de contratación** (*contracting process*) | Conjunto de etapas de una compra pública, de principio a fin: planificación (`planning`), licitación (`tender`), adjudicación (`awards`), contrato (`contracts`) y su ejecución (`implementation`). En OCDS se identifica con un `ocid`. En el proyecto es la unidad prevista del hecho principal: un proceso por foto (el grano definitivo es **[PENDIENTE]**). | [ocds.md](sources/ocds.md#secciones-del-proceso-de-contratación) (secciones del proceso); [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Entidad contratante** (comprador, `buyer`) | Organismo público cuyo presupuesto paga la contratación. En OCDS es el rol `buyer`. En el proyecto se identifica por `buyer.id` completo, nunca por `buyer.name`. El buscador de SERCOP muestra el rótulo «ENTIDAD CONTRATANTE»; no se ha verificado a qué propiedad JSON equivale. La definición legal de la LOSNCP no se ha contrastado aquí. | [ocds.md](sources/ocds.md#organización-y-partes-involucradas-parties); [ADR 0001](adr/0001-alcance.md) (decisión 7); [reconocimiento.md](sources/reconocimiento.md#campos-evidencia-y-límites-de-lo-observado) |
| **Unidad contratante** (`tender.procuringEntity`) | Entidad o unidad que gestiona directamente el proceso. Puede ser distinta del comprador. En la muestra de enero de 2025 fue distinta del `buyer.id` en 1.929 de 2.141 releases, con la misma raíz de 13 dígitos. Se conserva como atributo; no es llave de clasificación. | [ocds.md](sources/ocds.md#organización-y-partes-involucradas-parties); [entidades.md](sources/entidades.md) (sección 5) |
| **Proveedor** (`supplier`) | Persona u organización a la que se adjudica el contrato. En OCDS es un rol de `parties` y se vincula desde `awards[].suppliers`. La estructura real de `suppliers` en la fuente se debe observar antes de decidir si `dim_supplier` entra en la estrella. | [ocds.md](sources/ocds.md#organización-y-partes-involucradas-parties); [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Adjudicación** (`awards`) | Decisión de a quién se entrega el contrato. Un proceso puede tener varias (por ejemplo, compras por lotes). Contar adjudicaciones no equivale a contar procesos. En la descarga anual de 2025, 300 releases tienen varias adjudicaciones (dato nacional). | [ocds.md](sources/ocds.md#3-adjudicaciones-awards); [reconocimiento.md](sources/reconocimiento.md#inspección-del-zip-anual-json) |
| **Contrato** (`contracts`) | Acuerdo formal firmado con el proveedor. Hace referencia a la adjudicación que lo originó mediante `awardID`. En la descarga anual de 2025 solo el 15,33 % de los objetos de contrato tiene importe numérico (dato nacional). | [ocds.md](sources/ocds.md#4-contratos-contracts); [reconocimiento.md](sources/reconocimiento.md#inspección-del-zip-anual-json) |
| **Método de contratación** (`tender.procurementMethod`) | Procedimiento por el que se contrata. OCDS 1.1 admite `open`, `selective`, `limited` y `direct`. No se deduce de `initiationType`, que solo admite `tender`. La fuente real trae además `procurementMethodDetails`. | [ocds.md](sources/ocds.md#release-entrega-frente-a-release-package-paquete-de-entregas); [reconocimiento.md](sources/reconocimiento.md#inspección-local-de-la-descarga-mensual-json) |
| **Monto** (presupuesto, estimado, adjudicado, contractual, pagado) | Cinco conceptos distintos que no se intercambian ni se usan para completar ausencias: presupuesto reservado (`planning.budget.amount`), valor estimado de la licitación (`tender.value`), valor adjudicado (`awards[].value`), valor del contrato (`contracts[].value`) y pagos (`contracts[].implementation.transactions[].value`). La ausencia de un monto no se convierte en cero. | [ocds.md](sources/ocds.md#estándar-vs-fuente-real-sercop) (tabla «Montos»); [reconocimiento.md](sources/reconocimiento.md#inspección-local-de-la-descarga-mensual-json) |
| **Planta central** | Alcance institucional del proyecto: Presidencia de la República, ministerios e institutos que dependen de los ministerios. Se busca cubrir toda la planta central, no una muestra. | [ADR 0001](adr/0001-alcance.md); [PROPUESTA.md](PROPUESTA.md#1-contexto-y-objetivo) |
| **GAD** (Gobierno Autónomo Descentralizado) | Gobierno de nivel provincial, cantonal o parroquial, y sus empresas. Quedan **fuera** del alcance. La Constitución los define como las juntas parroquiales rurales, los concejos municipales y metropolitanos y los consejos provinciales y regionales. | [ADR 0001](adr/0001-alcance.md); Constitución de la República del Ecuador, art. 238 ([Referencias](#referencias)) |
| **Clasificación de entidades** (semilla) | Tabla versionada en el repositorio que asigna a cada entidad exactamente una categoría: Presidencia, ministerio, instituto dependiente de un ministerio o fuera de alcance. Se cruza con la fuente por `buyer.id`. Fuente oficial, criterios de inclusión y casos dudosos son **[PENDIENTE]**. | [ADR 0001](adr/0001-alcance.md) (decisiones 5 a 7); [entidades.md](sources/entidades.md) |
| **SERCOP** | Servicio Nacional de Contratación Pública. Administra el portal oficial de datos abiertos de contratación (OCDS) que es la fuente del proyecto. El proyecto es académico e independiente y no tiene relación con SERCOP. | [reconocimiento.md](sources/reconocimiento.md#procedencia-y-actualización); [README.md](../README.md) |

## 2. Estándar OCDS

| Término | Definición | Fuente |
|---|---|---|
| **OCDS** (Open Contracting Data Standard) | Estándar global y abierto que define cómo estructurar y publicar datos de procesos de contratación. No es un sistema de compra ni una base de datos: es un modelo de datos común. SERCOP indica que transforma sus datos a OCDS 1.1. | [ocds.md](sources/ocds.md#qué-es-ocds); [reconocimiento.md](sources/reconocimiento.md#procedencia-y-actualización); [OCDS: ¿Qué es?](https://standard.open-contracting.org/latest/es/primer/what/) |
| **`ocid`** (Open Contracting Identifier) | Identificador único global de un proceso de contratación. Se forma con un prefijo registrado más el identificador interno del publicador, y distingue mayúsculas de minúsculas. En la descarga anual de 2025 hubo 190.619 `ocid` distintos, uno por release (dato nacional). | [ocds.md](sources/ocds.md#1-el-identificador-del-proceso-de-contratación-ocid-global); [reconocimiento.md](sources/reconocimiento.md#inspección-del-zip-anual-json) |
| **Release** (entrega) | Objeto que representa una actualización o «fotografía» del estado de un proceso en un momento dado. Es inmutable: una corrección se publica como un release nuevo, con nueva fecha e `id`. | [ocds.md](sources/ocds.md#release-entrega-frente-a-release-package-paquete-de-entregas) |
| **Release package** (paquete de entregas) | Contenedor JSON que transporta uno o más releases y añade metadatos de publicación (`uri`, `publishedDate`, `publisher`, `license`). El JSON mensual de SERCOP es una lista de paquetes con un release cada uno. | [ocds.md](sources/ocds.md#release-entrega-frente-a-release-package-paquete-de-entregas); [reconocimiento.md](sources/reconocimiento.md#inspección-local-de-la-descarga-mensual-json) |
| **Record** y **compiled release** (registro y entrega compilada) | El *record* indexa todas las entregas de un proceso. El *compiled release* es la fusión de esas entregas según las reglas de OCDS, es decir, el estado más reciente. No se verificó que las descargas de SERCOP sean entregas compiladas. | [ocds.md](sources/ocds.md#record-registro-y-compiled-release-entrega-compilada) |
| **Party** (parte) y roles | Organización registrada en la sección `parties`, con uno o más roles: `buyer`, `procuringEntity`, `supplier`, `tenderer`. Otras secciones la referencian por `id`. | [ocds.md](sources/ocds.md#organización-y-partes-involucradas-parties) |

## 3. Modelado dimensional y metodología

| Término | Definición | Fuente |
|---|---|---|
| **Data Warehouse** (DW) | Base de datos organizada para el análisis, no para registrar transacciones. Integra datos de una o más fuentes en un modelo dimensional. Aquí es el DW de la contratación de la planta central, aún no implementado. | Kimball y Ross (2013), cap. 1; [PROPUESTA.md](PROPUESTA.md#1-contexto-y-objetivo) |
| **HEFESTO** | Metodología para construir un Data Warehouse que sigue cuatro pasos: análisis de requerimientos, análisis de los OLTP (sistemas fuente), modelo lógico del DW e integración de datos. El curso la usa junto con el modelado dimensional de Kimball. | Bernabeu, *HEFESTO* ([Referencias](#referencias)); [README.md](../README.md) |
| **Indicador** (KPI) | Valor medible que responde a una pregunta de negocio. En HEFESTO se identifican las preguntas, luego los indicadores y las perspectivas de análisis. En el proyecto cada KPI lleva su fórmula en palabras y debe poder calcularse con datos que la fuente tiene. Los definitivos son **[PENDIENTE]** de la fase 1. | Bernabeu, *HEFESTO*; [PLAN.md](PLAN.md#fase-1--requerimientos-20-oct--2-nov) (tareas de Jorge); [README.md](../README.md#problema) |
| **Hecho** (*fact*) y tabla de hechos | Registro de un evento o proceso de negocio medible. La tabla de hechos guarda las medidas y las claves hacia las dimensiones. En el proyecto: `fact_contract_process`. | Kimball y Ross (2013), cap. 2; [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Medida** (*measure*) | Valor numérico de un hecho que se agrega: sumas, conteos, promedios. Las medidas definitivas del hecho son **[PENDIENTE]** de la fase 1. | Kimball y Ross (2013), cap. 2; [ADR 0004](adr/0004-alcance-del-modelo.md) (pendientes) |
| **Dimensión** (*dimension*) | Tabla con el contexto descriptivo de los hechos: quién, qué, dónde, cuándo y cómo. HEFESTO las llama *perspectivas de análisis*. Previstas: `dim_date`, `dim_entity`, `dim_method`, `dim_geography` y, si la estructura lo permite, `dim_supplier`. | Kimball y Ross (2013), cap. 2; Bernabeu, *HEFESTO*; [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Grano** (*grain*) | Lo que representa exactamente una fila de la tabla de hechos. Se define antes de elegir dimensiones y medidas, y se enuncia en una sola frase. Grano previsto: un proceso (`ocid`) por foto; el definitivo es **[PENDIENTE]** tras el perfilado. | Kimball y Ross (2013), cap. 2; [ADR 0004](adr/0004-alcance-del-modelo.md); [PLAN.md](PLAN.md#fase-2--diseño-conceptual-y-lógico-3--23-nov) |
| **Esquema en estrella** (*star schema*) | Modelo con una tabla de hechos al centro, rodeada de sus dimensiones. El curso pide, para las entregas, un hecho y de 4 a 5 dimensiones. | Kimball y Ross (2013), cap. 1; [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Dimensión degenerada** | Identificador de la transacción que se guarda en la tabla de hechos sin tabla de dimensión propia. Aquí, `ocid` en `fact_contract_process`. | Kimball y Ross (2013), cap. 2; [ADR 0004](adr/0004-alcance-del-modelo.md) |
| **Clave sustituta** (*surrogate key*) | Clave numérica sin significado de negocio que identifica cada fila de una dimensión, independiente de la clave de la fuente. Se genera en la transformación. | Kimball y Ross (2013), cap. 2; [PLAN.md](PLAN.md#fase-3--diseño-físico-y-etl-24-nov--14-dic) (tareas de Jorge) |
| **SCD** (*Slowly Changing Dimension*, dimensión de cambio lento) | Técnica para tratar atributos de una dimensión que cambian con el tiempo. **Tipo 1** sobrescribe el valor y no conserva historia. **Tipo 2** agrega una fila nueva con su intervalo de vigencia y conserva la historia. En el proyecto `dim_entity` usa tipo 2, porque las entidades cambian de nombre, se fusionan o cambian de ministerio; `dim_supplier` se propone en tipo 1. | Kimball y Ross (2013), cap. 5; [ADR 0001](adr/0001-alcance.md); [PROPUESTA.md](PROPUESTA.md#dimensiones) |

## 4. ETL, datos y operación

| Término | Definición | Fuente |
|---|---|---|
| **ETL** (extracción, transformación y carga) | Proceso que extrae datos de la fuente, los transforma (limpieza, normalización, campos derivados, claves sustitutas) y los carga al DW. En el proyecto se separa en `extract` y `snapshot` (que no conocen el DW), y `load` (que no conoce la API de la fuente). | Kimball y Ross (2013), cap. 19; [AGENTS.md](../AGENTS.md); [PLAN.md](PLAN.md#fase-3--diseño-físico-y-etl-24-nov--14-dic) |
| **Staging** (área de preparación, esquema `stg`) | Zona intermedia donde se cargan los datos de la foto tal como vienen, con tipos pero sin reglas de negocio, antes de pasar al DW. Se puede reconstruir desde la foto. | Kimball y Ross (2013), cap. 1; [PROPUESTA.md](PROPUESTA.md#4-arquitectura); [ADR 0002](adr/0002-foto-inmutable.md) |
| **Foto** (*snapshot*) | Descarga fija de los datos de SERCOP del periodo elegido. Es evidencia: una vez registrada no se modifica ni se sobrescribe; una corrección es otra foto con su propio identificador. Vive en `data/`, fuera de Git. Las descargas de reconocimiento de 2025 no son la foto definitiva; periodo y formato son **[PENDIENTE]**. | [ADR 0002](adr/0002-foto-inmutable.md); [data/README.md](../data/README.md) |
| **Manifiesto** y **checksum** | El manifiesto lista el *checksum* (huella criptográfica) de cada archivo de la foto, para verificar su integridad antes de cada carga. El algoritmo, el contenido y la ubicación del manifiesto son **[PENDIENTE]**. | [ADR 0002](adr/0002-foto-inmutable.md) (decisión 2 y pendientes) |
| **Carga batch** | Carga inicial completa de la foto al DW. | [ADR 0002](adr/0002-foto-inmutable.md) (decisión 5) |
| **Carga incremental** | Carga por particiones de fecha (por ejemplo, mes a mes) sobre la misma foto, con marca de control (`batch_id`, fecha de corte). Detecta cambios con la clave natural `ocid` más un hash del contenido del registro. | [ADR 0002](adr/0002-foto-inmutable.md) (decisiones 6 y 7) |
| **Idempotencia** | Propiedad de una carga: repetirla no duplica datos. Toda carga del proyecto debe cumplirla y dejar bitácora. | [PROPUESTA.md](PROPUESTA.md#4-arquitectura) (principio 3); [AGENTS.md](../AGENTS.md) |
| **Reconciliación** | Comparación de conteos y sumas de monto entre la foto, `stg` y el DW tras cada carga, para validar con la fuente original. Las diferencias deben quedar explicadas. | [ADR 0002](adr/0002-foto-inmutable.md) (decisión 8); [PLAN.md](PLAN.md#fase-4--carga-y-pruebas-15-dic--8-ene) |
| **Bitácora de cargas** (esquema `audit`) | Registro de cada carga y de sus errores. `load_log` guarda proceso, inicio, fin, tabla destino, registros correctos, errores, duración y estado. `load_error` guarda tabla, campo, descripción, fecha, proceso y acción tomada. | [ADR 0004](adr/0004-alcance-del-modelo.md) (decisión 2); [PLAN.md](PLAN.md#fase-3--diseño-físico-y-etl-24-nov--14-dic) |
| **Calidad de datos** | Grado en que los datos sirven para su uso. Las dimensiones de calidad previstas para el catálogo de reglas son completitud (¿están los datos?), validez (¿tienen el formato y rango correctos?), unicidad (¿sin duplicados?) y consistencia (¿coinciden entre sí y con otras fuentes?). | DAMA UK (2013) ([Referencias](#referencias)); [PLAN.md](PLAN.md#fase-2--diseño-conceptual-y-lógico-3--23-nov) (tareas de Francis) |
| **Esquema `rpt`** | Esquema de vistas desde el que leen los tableros de Power BI, una vista por tablero. Los tableros nunca leen tablas crudas ni `stg`. | [PROPUESTA.md](PROPUESTA.md#4-arquitectura) (principio 5); [PLAN.md](PLAN.md#fase-5--visualización-y-cierre-9--22-ene) |

## Referencias

Las verificaciones de este glosario se hicieron contra los documentos del
repositorio. Los enlaces y capítulos externos siguientes no se pudieron abrir
desde el entorno de redacción; conviene comprobarlos antes de fusionar.

- Kimball, R. y Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive
  Guide to Dimensional Modeling* (3.ª ed.). Wiley. Los capítulos citados
  corresponden a esa edición: 1 (introducción a DW/BI y al modelado
  dimensional), 2 (técnicas de modelado dimensional), 5 (compras y conceptos
  básicos de SCD) y 19 (subsistemas de ETL).
- Bernabeu, R. D. *HEFESTO: Data Warehouse, investigación y sistematización de
  conceptos. Metodología para la construcción de un Data Warehouse*. Córdoba,
  Argentina. Versión 1.0:
  <https://www.dataprix.com/files/DWH_Metodologia_HEFESTO-V1.0.pdf>.
- Open Contracting Partnership. *Open Contracting Data Standard 1.1*:
  <https://standard.open-contracting.org/latest/es/>. Las definiciones de
  OCDS de este glosario provienen de [ocds.md](sources/ocds.md), que enlaza
  cada sección oficial.
- DAMA UK (2013). *The Six Primary Dimensions for Data Quality Assessment*.
- Constitución de la República del Ecuador (2008), art. 238 (gobiernos
  autónomos descentralizados).
- **[PENDIENTE]** Contrastar con el texto vigente de la Ley Orgánica del
  Sistema Nacional de Contratación Pública (LOSNCP, art. 6) las definiciones
  legales de entidad contratante y proveedor. La ley fue reformada en 2025 y
  no se confirmó aquí el texto vigente.

## Cómo añadir o corregir un término

1. Abre o usa un issue y trabaja en una rama (ver
   [CONTRIBUTING.md](../CONTRIBUTING.md)).
2. Añade una fila a la tabla del tema que corresponda, con definición y
   fuente. Sin fuente no entra.
3. Separa lo que define el estándar o la teoría de lo que mide o decide el
   proyecto, y marca como **[PENDIENTE]** lo que aún no esté decidido.
4. Si el término cambia una decisión de arquitectura, no lo cambies aquí:
   crea o reemplaza el ADR correspondiente.
