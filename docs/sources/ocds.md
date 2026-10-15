# Resumen del Estándar OCDS (Open Contracting Data Standard)


> [!NOTE]
> Este documento resume OCDS 1.1, contrastado con la documentación oficial 1.1.5. Las observaciones de SERCOP se mantienen en [reconocimiento.md](reconocimiento.md), correspondiente al [issue #9](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9). La tabla final enlaza esa evidencia y distingue lo observado de lo pendiente.


## ¿Qué es OCDS?

El Estándar de Datos de Contrataciones Abiertas (OCDS) es un estándar global de datos abiertos, gratuito y de acceso público, implementado por más de 30 gobiernos alrededor de todo el mundo. Describe cómo estructurar y publicar datos y documentos relacionados a los procesos de contrataciones de bienes, obras y servicios.

Se sustenta en tres conceptos clave:

1. **Contratación Abierta:** Busca publicar información accesible y oportuna para involucrar a los ciudadanos y al sector privado, mejorando así la eficiencia, efectividad e integridad de las compras públicas.

2. **Datos Abiertos:** Consiste en publicar datos legibles por máquina que cualquier persona pueda utilizar libremente, modificar y compartir.

3. **Estándar de datos:** Define una estructura y un significado común para los datos, resolviendo ambigüedades técnicas y conceptuales.


El OCDS **no es un sistema electrónico de compra ni una base de datos**; es un modelo de datos común que estandariza la recolección, almacenamiento y publicación de datos. Proporciona herramientas, listas de códigos, un mecanismo de extensión y soporte global, permitiendo a los analistas realizar investigaciones profundas sobre transparencia, competencia y valor por el dinero invertido. ([Fuente oficial: ¿Qué es OCDS?](https://standard.open-contracting.org/latest/es/primer/what/))


## Identificadores en OCDS

Para que los datos de contrataciones puedan vincularse correctamente entre diferentes sistemas, OCDS hace un uso riguroso de identificadores tanto globales como locales.

### 1. El Identificador del Proceso de Contratación: OCID (Global)

El **OCID (Open Contracting Identifier)** es el identificador único global para un proceso de contratación de principio a fin. Permite vincular la información del mismo proceso publicada en distintos momentos y lugares, incluidas su planificación y ejecución. ([Fuente oficial: OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))

* **Composición:** Todo OCID está formado por dos partes:

  1. Un **prefijo registrado** (ej. `ocds-87sd3t`) asignado exclusivamente por el equipo de Open Contracting a un publicador específico.

  2. El **identificador interno** del proceso de la institución (ej. `OM-DGRMSG-004-13`). ([Fuente oficial: cómo se establece el OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))


  *Resultado:* `ocds-87sd3t-OM-DGRMSG-004-13`.

* **Propósito:** Evitar colisiones. Si la Ciudad A y la Ciudad B tienen internamente un contrato "0005", el prefijo único de cada ciudad garantiza que sus procesos no se mezclen en un sistema global de datos.

* **Sensibilidad:** El OCID distingue estrictamente entre mayúsculas y minúsculas. ([Fuente oficial: Identificadores / OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))


> **Ejemplo oficial: Ciudad de México.**
> En la Ciudad de México, cada vez que se inicia un proceso de licitación o adjudicación directa, la oficina responsable le asigna un identificador.

> Estos se generan a partir de un identificador del departamento responsable de la adquisición, un número de licitación y el año.

> Por ejemplo:  `OM-DGRMSG-004-13`

> Este identificador interno puede intercambiarse con y ser registrado en cualquier otro sistema que procese información sobre el proceso de contratación. Por ejemplo los sistemas que reportan o registran pagos a proveedores.

> Luego, la Ciudad de México registró un prefijo con el Equipo de Soporte de Datos. Se les ha dado el prefijo 'ocds-87sd3t' que se puede agregar a sus identificadores de proceso únicos para dar un 'ocid' globalmente único. P.ej.
> > `ocds-87sd3t-OM-DGRMSG-004-13`

### 2. Identificadores Locales (IDs de Entregas, Adjudicaciones, Contratos e Ítems)


Los IDs locales tienen distintos ámbitos: los de entregas, adjudicaciones y contratos deben ser únicos dentro del proceso (`ocid`); los de ítems, documentos e hitos, dentro de la lista que los contiene. Deben mantenerse consistentes entre entregas. ([Fuente oficial: Identificadores locales](https://standard.open-contracting.org/latest/es/schema/identifiers/#local-identifiers))


* **ID de Entrega (Release ID):** Debe ser único y consistente para cada "fotografía" de datos publicada dentro de ese proceso. No debe contener el caracter `#`. ([Fuente oficial: ID de Entrega](https://standard.open-contracting.org/latest/es/schema/reference/#release))

* **IDs de Adjudicaciones y Contratos:** Un contrato debe hacer una referencia cruzada estricta a una adjudicación relacionada usando el campo `awardID`. Múltiples contratos pueden referirse a una misma adjudicación (como en los acuerdos marco). ([Fuente oficial: IDs de Adjudicaciones y Contratos](https://standard.open-contracting.org/latest/es/schema/identifiers/#local-identifiers))

* **IDs de Artículos (`items`), Documentos e Hitos:** Son únicos dentro de su propia matriz. Si una entrega posterior vuelve a usar el mismo ID de ítem (ej. ID "3"), el estándar interpreta que se está actualizando la información de ese artículo existente, sin necesidad de volver a publicar los artículos que no han cambiado. ([Fuente oficial: IDs de Artículo, Documento e Hitos](https://standard.open-contracting.org/latest/es/schema/identifiers/#local-identifiers))


## Manejo del Historial de Datos: Releases y Registros

Los procesos de contratación pública son vivos y cambian constantemente. OCDS captura estos cambios a través de una arquitectura basada en "Entregas" (Releases) y "Registros" (Records).

### Release (Entrega) frente a Release Package (Paquete de Entregas)

El estándar OCDS distingue claramente entre la información del proceso y el contenedor utilizado para transmitirla:

* **Release (Entrega):** Es el objeto de información principal que representa una actualización o una "fotografía" del estado de un proceso de contratación en un momento particular de su ciclo de vida. Contiene los metadatos propios de la entrega (como `ocid`, `id`, `date`, `tag` e `initiationType`) junto con las secciones correspondientes del proceso (`planning`, `tender`, `awards`, `contracts`, `parties`).

* **Release Package (Paquete de Entregas):** Es el contenedor JSON (wrapper) utilizado para publicar y transferir una o más entregas a través de una API o archivo. Incluye metadatos de publicación a nivel de paquete (como `uri`, `publishedDate`, `publisher` y `license`) y una matriz `releases` que contiene los objetos *Release*.

* **Inmutabilidad:** Las entregas son **estrictamente inmutables**. Una vez publicadas, un publicador no debe editarlas. Si hay nueva información o se debe corregir un error, se debe generar un nuevo *release* con una nueva fecha (`date`) y un nuevo ID (`id`).

* **Manejo de campos:** Los campos sin valor que no se usan se omiten. Omitir un campo en una entrega posterior no elimina su valor anterior al compilar; para eliminarlo explícitamente se envía `null`. ([Fuente oficial: campos vacíos y eliminación de valores](https://standard.open-contracting.org/latest/es/schema/reference/#release-handling))

* **Etiquetas (`tag`):** Es una lista con una o más etiquetas, como `tender`, `award` o `contract`, que describen el tipo de información publicada. La entrega puede incluir datos de otras etapas para dar contexto. ([Fuente oficial: Release](https://standard.open-contracting.org/latest/es/schema/reference/#release))

* **Tipo de Iniciación (`initiationType`):** Es obligatorio y se ubica en la raíz del *Release*, junto a `ocid`, `id`, `date` y `tag`. En OCDS 1.1 su lista cerrada admite únicamente `tender`; no permite deducir que una compra sea una licitación pública. El procedimiento se describe por separado en `tender.procurementMethod`, que admite `open`, `selective`, `limited` y `direct`. ([Fuente oficial: Release](https://standard.open-contracting.org/latest/es/schema/reference/#release); [listas de códigos](https://standard.open-contracting.org/latest/es/schema/codelists/#initiation-type))


### Record (Registro) y Compiled Release (Entrega Compilada)

El **Record** funciona como un índice de todas las entregas de un proceso identificado por su `ocid`. Las entregas pueden estar incluidas o enlazadas. Se recomienda que el registro incluya un **Compiled Release**; no es obligatorio en su esquema. ([Fuente oficial: estructura del registro](https://standard.open-contracting.org/latest/es/schema/records_reference/#record-structure))


* **Compiled Release:** Es el resultado de fusionar las entregas de un proceso según las reglas de OCDS. Representa el estado más reciente de sus datos al publicar el registro; no significa que el proceso haya terminado ni garantiza que todos sus campos estén completos. ([Fuente oficial: entrega compilada](https://standard.open-contracting.org/latest/es/schema/records_reference/#compiled-release); [reglas de fusión](https://standard.open-contracting.org/latest/es/schema/merging/))


## Organización y Partes Involucradas (`parties`)



A partir de la versión 1.1, OCDS introdujo una sección matriz principal llamada `parties` para registrar a todos los actores (compradores, proveedores, auditores, etc.).

Esto reduce la repetición de los datos de organizaciones. Sus detalles se incluyen en `parties`; otras secciones utilizan referencias mediante `id` y pueden incluir `name`. Cada parte referenciada debe figurar en `parties`. ([Fuente oficial: partes y referencias](https://standard.open-contracting.org/latest/es/schema/reference/#parties))


* **Identificadores de Organización (`identifier`):** Permite describir el identificador legal de la entidad. Cuando se informa, utiliza campos como `scheme` (el prefijo del registro legal, ej. `GB-COH`) e `id` (el número de registro oficial). El objeto `identifier` es opcional en la especificación del esquema de OCDS, por lo que no es estrictamente obligatorio incluirlo en todos los casos.

* **Registros Primarios, Secundarios y de Terceros:** OCDS prefiere identificadores de registros primarios que identifican una entidad legal constituida. Los registros secundarios describen una propiedad, como la inscripción para IVA; las bases de terceros son otra categoría. No se presupone aquí qué registro o `scheme` utiliza SERCOP. ([Fuente oficial: elección del identificador](https://standard.open-contracting.org/latest/es/schema/identifiers/#choosing-an-identifier))

* **Roles (`roles`):** A cada organización en `parties` se le asigna uno o más roles desde una lista de códigos oficial (`partyRole`). Ejemplos comunes incluyen:
  * `buyer`: La entidad cuyo presupuesto se utilizará para pagar los bienes, obras o servicios del contrato. Puede ser distinta de la entidad que gestiona la contratación.
  * `procuringEntity`: La entidad que gestiona directamente el proceso de licitación o contratación (puede coincidir o no con el `buyer`).
  * `supplier`: El proveedor o contratista adjudicado.
  * `tenderer`: El oferente o participante en la licitación. ([Fuente oficial: Esquema de Partes](https://standard.open-contracting.org/latest/es/schema/reference/#parties))

### Campos de cada parte
([Fuente oficial: Partes involucradas](https://standard.open-contracting.org/latest/es/schema/reference/#parties); [Identificador](https://standard.open-contracting.org/latest/es/schema/reference/#identifier); [Dirección](https://standard.open-contracting.org/latest/es/schema/reference/#address); [Punto de contacto](https://standard.open-contracting.org/latest/es/schema/reference/#contactpoint))

|Campo|Descripción|
|---|---|
|`id`|ID usado para referenciar a la parte desde otras secciones. Estructura sugerida: `{identifier.scheme}-{identifier.id}(-{identificador-del-departamento})`.|
|`name`|Nombre común (puede incluir departamento o sub-unidad involucrada).|
|`identifier`|**Identificador principal**: `scheme`, `id`, `legalName`, `uri`. Permite describir el identificador legal de la entidad (preferir registro primario).|
|`additionalIdentifiers`|Identificadores complementarios (ej. un código interno o de IVA, además del legal).|
|`address`|`streetAddress`, `locality`, `region`, `postalCode`, `countryName`.|
|`contactPoint`|`name`, `email`, `telephone`, `faxNumber`, `url`.|
|`roles`|Uno o más roles de la lista abierta `partyRole`.|
|`details`|Clasificación adicional vía extensiones.|

## Secciones del Proceso de Contratación

La estructura del estándar divide la cronología de la compra en cuatro grandes bloques de información (más `parties`). ([Fuente oficial: Estructura de la entrega](https://standard.open-contracting.org/latest/es/schema/reference/#release-structure))

### 1. Planificación (`planning`)

Describe el contexto, los antecedentes y los presupuestos antes de que el proceso salga al mercado.


* **Justificación (`rationale`):** Explica por qué se realiza la compra.

* **Presupuesto (`budget`):** Desglosa el monto reservado, la descripción de la fuente de los fondos y el ID de la partida presupuestaria (ideal para cruzar con sistemas financieros del Estado). También vincula si la compra pertenece a un macro-proyecto (`project`).


* **Hitos (`milestones`) y Documentos (`documents`):** Permite adjuntar estudios de viabilidad, planes de necesidad o fechas límite para preparar la compra. ([Fuente oficial: Esquema de Planificación](https://standard.open-contracting.org/latest/es/schema/reference/#planning))

### 2. Licitación (`tender`)

Documenta las reglas del juego: cómo se buscarán proveedores y qué se está pidiendo.

* **Detalles del Proceso:** Incluye el periodo de recepción de ofertas (`tenderPeriod`), el método de contratación (`procurementMethod`), estado y descripción. Las fechas de publicación de documentos se registran en sus objetos `documents`. El campo `initiationType` pertenece a la raíz del *Release*.

* **Ítems (`items`):** Una lista detallada y estandarizada de los bienes o servicios exactos que se desean adquirir (con nombres, cantidades y clasificaciones estándar).


* **Criterios:** Reglas y criterios de evaluación que se usarán para elegir al ganador. ([Fuente oficial: Esquema de Licitación](https://standard.open-contracting.org/latest/es/schema/reference/#tender))


### 3. Adjudicaciones (`awards`)


Registra la decisión de a quién se le entrega el contrato. Un proceso de contratación puede tener **múltiples adjudicaciones** (por ejemplo, cuando se compra por lotes separados a diferentes proveedores).

* **Proveedores Ganadores:** Vincula a los proveedores elegidos (que deben estar listados en `parties`).

* **Datos Financieros:** Cada objeto puede registrar el valor total de esa adjudicación (`value`) y su fecha (`date`). En acuerdos marco, el valor puede ser el total estimado durante su vigencia o el máximo del acuerdo; no equivale automáticamente al importe contratado ni al pagado.

* **Ítems Adjudicados:** Describe los bienes y servicios adjudicados en ese objeto, con cantidades y clasificaciones. No se presupone una correspondencia uno a uno entre las listas de licitación y adjudicación. ([Fuente oficial: Esquema de Adjudicación](https://standard.open-contracting.org/latest/es/schema/reference/#award))

### 4. Contratos (`contracts`)

Alberga los detalles formales y vinculantes del acuerdo firmado con el proveedor. Es fundamental que **todo contrato haga referencia cruzada a la adjudicación (`awardID`)** que lo originó, ya que múltiples contratos (ej. órdenes de compra) pueden salir de una sola adjudicación marco.

* **Datos del Acuerdo:** Cada objeto puede incluir fecha de firma (`dateSigned`), periodo de vigencia (`period`), estado (`status`) y valor total del contrato (`value`). Este valor se distingue del presupuesto, la estimación de la licitación, la adjudicación y los pagos.

* **Implementación (`implementation`):** Se encuentra dentro de cada contrato. Puede registrar transacciones realizadas (`transactions`), con pagador (`payer`), receptor (`payee`), fecha y valor, además de hitos y documentos de ejecución. En la mayoría de los casos el pagador es el comprador y el receptor el proveedor; esos flujos no deben confundirse con el valor total del contrato. ([Fuente oficial: implementación y transacciones](https://standard.open-contracting.org/latest/es/schema/reference/#implementation))


## Conceptos Avanzados y de Utilidad Futura

Con base en la especificación técnica, existen herramientas adicionales en OCDS que pueden ser útiles para las siguientes fases del Data Warehouse:


### Manejo de Múltiples Idiomas (`language`)

El estándar permite publicar variantes de idioma para campos de texto mediante sufijos con etiquetas BCP47. Se recomiendan códigos ISO639-1 de dos letras minúsculas cuando no haga falta distinguir variantes.


* Ejemplo: con `language: "es"`, el campo `description` contiene el texto en español y `description_en` añade su traducción al inglés.

* La guía recomienda declarar el idioma predeterminado en `language`, en la raíz de la entrega, para interpretar los campos sin sufijo. El esquema permite omitirlo: no aparece entre los campos obligatorios. ([Fuente oficial: idioma](https://standard.open-contracting.org/latest/en/schema/reference/#language); [esquema oficial](https://standard.open-contracting.org/schema/1__1__5/release-schema.json))


### Procesos Relacionados (`relatedProcesses`)

En adquisiciones complejas, una compra no está aislada. El arreglo `relatedProcesses` permite relacionar diferentes `ocid` entre sí. ([Fuente oficial: RelatedProcess](https://standard.open-contracting.org/latest/es/schema/reference/#relatedprocess))

* **Caso de uso:** Vincular compras derivadas de un "Acuerdo Marco" general, o conectar un contrato con un proceso previo de planificación a nivel macro.

### Extensiones del Estándar (`extensions`)

OCDS permite añadir campos y listas de códigos mediante extensiones. Se declaran en la lista `extensions` del paquete mediante las URL de sus archivos `extension.json`; el nombre de una extensión no es necesariamente el nombre del campo que añade. ([Fuente oficial: metadatos del paquete](https://standard.open-contracting.org/latest/es/schema/reference/#package-metadata))

* **Título y descripción del proceso (`process_title`):** Añade `title` y `description` a la raíz de la entrega. ([Extensión oficial](https://extensions.open-contracting.org/en/extensions/process_title/v1.1.5/))
* **Accionistas (`shareholders`):** Añade información sobre propiedad societaria en `parties[].shareholders`. No acredita por sí sola la identificación de los beneficiarios finales. ([Documentación de la extensión](https://extensions.open-contracting.org/en/extensions/shareholders/master/))
* **Escala de la organización (`partyScale`):** Añade `parties[].details.scale`, con códigos para tamaños de empresa definidos según el contexto local. ([Documentación de la extensión](https://extensions.open-contracting.org/en/extensions/partyScale/master/))

Estos ejemplos describen posibilidades del estándar; no afirman que SERCOP utilice esas extensiones.


---

## Estándar vs. fuente real (SERCOP)

Los apartados anteriores describen **lo que define OCDS**. La evidencia de SERCOP procede de [reconocimiento.md](reconocimiento.md), integrado mediante el PR #22 como avance del [issue #9](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9). La tabla siguiente resume esa documentación al 11 de octubre de 2026; no sustituye su evidencia ni una validación de esquemas.

| Concepto | Qué define OCDS | Evidencia documentada de SERCOP y límites |
|---|---|---|
| `ocid` | Identificador global del proceso | La inspección anual documenta 190.619 `ocid` distintos. Son datos nacionales; la clasificación de la planta central sigue pendiente. No certifica el historial completo. |
| Release y paquete | Objeto del proceso y contenedor con `releases` | El JSON mensual tiene una lista raíz de paquetes, con un release por paquete y versión declarada 1.1. La inspección anual cuenta 190.619 paquetes y releases. No acredita conformidad OCDS ni el significado de sus etiquetas `tag`. |
| Compiled release | Estado más reciente obtenido por fusión | No se verificó que las descargas sean entregas compiladas. Un release por `ocid` no demuestra que exista todo su historial. |
| `buyer` y `parties` | Comprador y partes referenciadas | `buyer` aparece en todos los releases anuales; en la inspección mensual se observaron `buyer.id`, `buyer.name` y campos de `parties`, incluido `identifier`. La completitud y los esquemas de identificación siguen sin validarse. |
| `planning`, `tender`, `awards` y `contracts` | Secciones con presupuestos, estimaciones, adjudicaciones y contratos | La inspección mensual documenta sus campos y presencia. Hay procesos con varias adjudicaciones o contratos: contar objetos o combinar listas no equivale a contar procesos. |
| Montos | Presupuesto en `planning.budget.amount`, estimación en `tender.value`, adjudicación en `awards[].value`, contrato en `contracts[].value` y pagos en `contracts[].implementation.transactions[].value` | El reconocimiento distingue esas rutas; numerosos contratos carecen de importe numérico. No convertir ausencia en cero ni sustituir un monto por otro. Monedas, estados y agregación requieren validación posterior. |
| `implementation` | Transacciones, hitos y documentos por contrato | El reconocimiento no documenta una inspección específica de esta sección; no se afirma su presencia, ausencia ni completitud. |
| Extensiones | Campos adicionales declarados en el paquete | En enero se observó `extensions` y propiedades como `auctions` y `bids`. No se validaron sus URL ni los esquemas aplicables, y no se deduce de esos nombres qué extensiones se usan. |

La respuesta resumida de `search_ocds` y el JSON anidado de descarga son estructuras distintas. Sus campos `amount`, `budget` y `suppliers` no se equiparan automáticamente a las rutas OCDS. Las fechas del archivo mensual tampoco permiten fijar por sí solas la fecha de negocio. Estos límites se detallan en [campos observados](reconocimiento.md#campos-evidencia-y-límites-de-lo-observado), [inspección mensual](reconocimiento.md#inspección-local-de-la-descarga-mensual-json) e [inspección anual](reconocimiento.md#inspección-del-zip-anual-json).

La cuota y ventana observadas pertenecen a #9 y se documentan en el
[reconocimiento de SERCOP](reconocimiento.md#límites-de-la-api). Este resumen
del estándar no aporta evidencia adicional ni propone medidas o decisiones
definitivas del DW.
