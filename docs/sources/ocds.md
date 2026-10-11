# Resumen del Estándar OCDS (Open Contracting Data Standard)


> [!NOTE] Separación de responsabilidades:
> Este documento describe la teoría oficial y el modelo de datos del estándar OCDS. Para ver cómo se aplican estos conceptos en los datos reales publicados por el SERCOP de Ecuador (y qué campos vienen realmente), consultar el documento de reconocimiento de la fuente de la Fase 0 (Issue #9).


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

El **OCID (Open Contracting Identifier)** es el identificador único global para un proceso de contratación de principio a fin. Funciona como la llave primaria que une la información publicada en distintos momentos y lugares (desde la planificación hasta el contrato).

* **Composición:** Todo OCID está formado por dos partes:

  1. Un **prefijo registrado** (ej. `ocds-87sd3t`) asignado exclusivamente por el equipo de Open Contracting a un publicador específico.

  2. El **identificador interno** del proceso de la institución (ej. `OM-DGRMSG-004-13`). ([Fuente oficial: cómo se establece el OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))


  *Resultado:* `ocds-87sd3t-OM-DGRMSG-004-13`.

* **Propósito:** Evitar colisiones. Si la Ciudad A y la Ciudad B tienen internamente un contrato "0005", el prefijo único de cada ciudad garantiza que sus procesos no se mezclen en un sistema global de datos.

* **Sensibilidad:** El OCID distingue strictly entre mayúsculas y minúsculas. ([Fuente oficial: Identificadores / OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))


> [!example] Ejemplo
> En la Ciudad de México, cada vez que se inicia un proceso de licitación o adjudicación directa, la oficina responsable le asigna un identificador.

> Estos se generan a partir de un identificador del departamento responsable de la adquisición, un número de licitación y el año.

> Por ejemplo:  `OM-DGRMSG-004-13`

> Este identificador interno puede intercambiarse con y ser registrado en cualquier otro sistema que procese información sobre el proceso de contratación. Por ejemplo los sistemas que reportan o registran pagos a proveedores.

> Luego, la Ciudad de México registró un prefijo con el Equipo de Soporte de Datos. Se les ha dado el prefijo 'ocds-87sd3t' que se puede agregar a sus identificadores de proceso únicos para dar un 'ocid' globalmente único. P.ej.
> > `ocds-87sd3t-OM-DGRMSG-004-13`

### 2. Identificadores Locales (IDs de Entregas, Adjudicaciones, Contratos e Ítems)


No todos los IDs deben ser únicos a nivel mundial. La mayoría solo necesita ser única *dentro del ámbito de su propio proceso* (dentro del mismo OCID). ([Fuente oficial: Identificadores locales](https://standard.open-contracting.org/latest/es/schema/identifiers/#local-identifiers))


* **ID de Entrega (Release ID):** Debe ser único y consistente para cada "fotografía" de datos publicada dentro de ese proceso. No debe contener el caracter `#`. ([Fuente oficial: ID de Entrega](https://standard.open-contracting.org/latest/es/schema/identifiers/#release-id))

* **IDs de Adjudicaciones y Contratos:** Un contrato debe hacer una referencia cruzada estricta a una adjudicación relacionada usando el campo `awardID`. Múltiples contratos pueden referirse a una misma adjudicación (como en los acuerdos marco). ([Fuente oficial: IDs de Adjudicaciones y Contratos](https://standard.open-contracting.org/latest/es/schema/identifiers/#award-and-contract-ids))

* **IDs de Artículos (`items`), Documentos e Hitos:** Son únicos dentro de su propia matriz. Si una entrega posterior vuelve a usar el mismo ID de ítem (ej. ID "3"), el estándar interpreta que se está actualizando la información de ese artículo existente, sin necesidad de volver a publicar los artículos que no han cambiado. ([Fuente oficial: IDs de Artículo, Documento e Hitos](https://standard.open-contracting.org/latest/es/schema/identifiers/#item-document-and-milestone-ids))


## Manejo del Historial de Datos: Releases y Registros

Los procesos de contratación pública son vivos y cambian constantemente. OCDS captura estos cambios a través de una arquitectura basada en "Entregas" (Releases) y "Registros" (Records).

### Release (Entrega) frente a Release Package (Paquete de Entregas)

El estándar OCDS distingue claramente entre la información del proceso y el contenedor utilizado para transmitirla:

* **Release (Entrega):** Es el objeto de información principal que representa una actualización o una "fotografía" del estado de un proceso de contratación en un momento particular de su ciclo de vida. Contiene los metadatos propios de la entrega (como `ocid`, `id`, `date`, `tag` e `initiationType`) junto con las secciones correspondientes del proceso (`planning`, `tender`, `awards`, `contracts`, `parties`).

* **Release Package (Paquete de Entregas):** Es el contenedor JSON (wrapper) utilizado para publicar y transferir una o más entregas a través de una API o archivo. Incluye metadatos de publicación a nivel de paquete (como `uri`, `publishedDate`, `publisher` y `license`) y una matriz `releases` que contiene los objetos *Release*.

* **Inmutabilidad:** Las entregas son **estrictamente inmutables**. Una vez publicadas, un publicador no debe editarlas. Si hay nueva información o se debe corregir un error, se debe generar un nuevo *release* con una nueva fecha (`date`) y un nuevo ID (`id`).

* **Manejo de campos:** Si un campo se deja de usar, se excluye del archivo. Si un valor que antes existía debe ser eliminado explícitamente, se debe enviar el campo con el valor nulo (`null`).

* **Etiquetas (`tag`):** Cada entrega lleva una etiqueta (como `tender`, `award`, `contract`) para indicar de qué etapa del proceso trae información principal, aunque puede contener datos de etapas anteriores para dar contexto completo.

* **Tipo de Iniciación (`initiationType`):** Se ubica en la raíz del *Release* (junto a `ocid`, `id`, `date` y `tag`). Especifica cómo se inició el proceso de contratación (por ejemplo, mediante una licitación pública usando el valor por defecto `tender`). ([Fuente oficial: Releases](https://standard.open-contracting.org/latest/es/primer/releases_and_records/))


### Record (Registro) y Compiled Release (Entrega Compilada)

El **Record** actúa como un índice maestro que agrupa todos los *releases* asociados a un mismo OCID. Dentro de un Record, encontramos el **Compiled Release**.


* **Compiled Release:** Dado que revisar decenas de entregas inmutables es complejo para un analista, el Compiled Release procesa todas esas entregas cronológicamente y las "fusiona" (merge). El resultado es un único JSON consolidado que muestra el **estado final, más reciente y actualizado** de cada campo del proceso de contratación. ([Fuente oficial: Compiled Release](https://standard.open-contracting.org/latest/es/schema/records_reference/#compiledrelease))


## Organización y Partes Involucradas (`parties`)



A partir de la versión 1.1, OCDS introdujo una sección matriz principal llamada `parties` para registrar a todos los actores (compradores, proveedores, auditores, etc.).

Esto evita repetir los datos de la misma empresa en la licitación, la adjudicación y el contrato. Se declaran una vez en `parties` y luego solo se hace referencia a su `id`.


* **Identificadores de Organización (`identifier`):** Permite describir el identificador legal de la entidad. Cuando se informa, utiliza campos como `scheme` (el prefijo del registro legal, ej. `EC-RUC` o `GB-COH`) e `id` (el número de registro oficial). El objeto `identifier` es opcional en la especificación del esquema de OCDS, por lo que no es estrictamente obligatorio incluirlo en todos los casos.

* **Registros Primarios vs Secundarios:** OCDS prefiere fuertemente identificadores de **Registros Primarios** (el registro mercantil o tributario nacional, como el RUC) porque otorgan estatus legal, por sobre registros secundarios (como bases de datos privadas o listas locales).

* **Roles (`roles`):** A cada organización en `parties` se le asigna uno o más roles desde una lista de códigos oficial (`partyRole`). Ejemplos comunes incluyen:
  * `buyer`: La entidad legal que administra el presupuesto con el que se pagarán los bienes, obras o servicios adquiridos (quien financia la compra).
  * `procuringEntity`: La entidad que gestiona directamente el proceso de licitación o contratación (puede coincidir o no con el `buyer`).
  * `supplier`: El proveedor o contratista adjudicado.
  * `tenderer`: El oferente o participante en la licitación. ([Fuente oficial: Esquema de Partes](https://standard.open-contracting.org/latest/es/schema/reference/#parties))

### Campos de cada parte
([Fuente oficial: Partes involucradas](https://standard.open-contracting.org/latest/es/schema/reference/#parties); [Identificador](https://standard.open-contracting.org/latest/es/schema/reference/#identifier); [Dirección](https://standard.open-contracting.org/latest/es/schema/reference/#address); [Punto de contacto](https://standard.open-contracting.org/latest/es/schema/reference/#contactpoint))

|Campo|Descripción|
|---|---|
|`id`|ID usado para referenciar a la parte desde otras secciones. Estructura sugerida: `{identifier.scheme}-{identifier.id}(-{identificador-del-departamento})`.|
|`name`|Nombre común (puede incluir departamento o sub-unidad involucrada).|
|`identifier`|**Identificador principal**: `scheme`, `id`, `legalName`, `uri`. Permite describir el identificador legal de la entidad (preferir registro primario, p. ej. RUC).|
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

* **Detalles del Proceso:** Incluye las fechas de publicación, inicio y fin del periodo de recepción de ofertas, método de contratación (`procurementMethod`), entre otros. *(Nota: el campo `initiationType` se ubica en el nivel raíz del Release).*

* **Ítems (`items`):** Una lista detallada y estandarizada de los bienes o servicios exactos que se desean adquirir (con nombres, cantidades y clasificaciones estándar).


* **Criterios:** Reglas y criterios de evaluación que se usarán para elegir al ganador. ([Fuente oficial: Esquema de Licitación](https://standard.open-contracting.org/latest/es/schema/reference/#tender))


### 3. Adjudicación (`award`)


Registra la decisión de a quién se le entrega el contrato. Un proceso de contratación puede tener **múltiples adjudicaciones** (por ejemplo, cuando se compra por lotes separados a diferentes proveedores).

* **Proveedores Ganadores:** Vincula a los proveedores elegidos (que deben estar listados en `parties`).

* **Datos Financieros:** Documenta el valor económico final de la oferta ganadora y la fecha oficial de la decisión.

* **Ítems Adjudicados:** Define exactamente cuáles de los ítems solicitados en el `tender` le fueron otorgados a este proveedor en específico. ([Fuente oficial: Esquema de Adjudicación](https://standard.open-contracting.org/latest/es/schema/reference/#award))

### 4. Contrato (`contract`)

Alberga los detalles formales y vinculantes del acuerdo firmado con el proveedor. Es fundamental que **todo contrato haga referencia cruzada a la adjudicación (`awardID`)** que lo originó, ya que múltiples contratos (ej. órdenes de compra) pueden salir de una sola adjudicación marco.

* **Datos del Acuerdo:** Fechas de firma, periodo legal de vigencia (inicio y fin) y el valor final acordado.

* **Implementación (`implementation`):** Esta subsección es crítica para el seguimiento. Permite registrar las **transacciones financieras** (pagos reales realizados al proveedor) y el cumplimiento de hitos durante la ejecución de la obra o servicio, cerrando el ciclo de la contratación abierta. ([Fuente oficial: Esquema de Contrato](https://standard.open-contracting.org/latest/es/schema/reference/#contract))


## Conceptos Avanzados y de Utilidad Futura

Con base en la especificación técnica, existen herramientas adicionales en OCDS que pueden ser útiles para las siguientes fases del Data Warehouse:


### Manejo de Múltiples Idiomas (`language`)

El estándar permite publicar datos en varios idiomas dentro del mismo JSON. Para campos de texto libre (como descripciones), se añade un sufijo con el código de idioma ISO639-1.


* Ejemplo: En lugar de usar solo `description`, se puede enviar `description_es` para el español y `description_en` para el inglés.

* Cada entrega debe declarar un idioma por defecto en la raíz del documento. ([Fuente oficial: Idioma](https://standard.open-contracting.org/latest/es/schema/reference/#language))


### Procesos Relacionados (`relatedProcesses`)

En adquisiciones complejas, una compra no está aislada. El arreglo `relatedProcesses` permite relacionar diferentes `ocid` entre sí. ([Fuente oficial: RelatedProcess](https://standard.open-contracting.org/latest/es/schema/reference/#relatedprocess))

* **Caso de uso:** Vincular compras derivadas de un "Acuerdo Marco" general, o conectar un contrato con un proceso previo de planificación a nivel macro.

### Extensiones del Estándar (`extensions`)

OCDS permite añadir campos que no vienen en el estándar base usando extensiones.

* Ejemplos comunes incluyen: agregar títulos a nivel proceso (`process_title`), dueños beneficiarios o accionistas de las empresas (`shareholders`), escala de la empresa (micro, pyme, grande con `partyScale`), o vincular compras a proyectos específicos de infraestructura. ([Fuente oficial: Entrega, extensiones disponibles](https://standard.open-contracting.org/latest/es/schema/reference/#release))


---

## Estándar vs. fuente real (SERCOP)

Todo lo anterior describe **lo que define el estándar OCDS**. Lo que SERCOP realmente publica (qué campos vienen, cuáles faltan, qué extensiones usa, cómo arma su `ocid`) **no se afirma aquí**: se documenta en el reconocimiento de la fuente de la Fase 0 ([Issue #9](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9)). Completar esa tabla con observaciones verificadas sobre datos reales:

| Concepto del estándar | Qué define OCDS (este documento) | Qué se observa en SERCOP (Issue #9) |
|---|---|---|
| `ocid` | Prefijo registrado + identificador interno | *Por completar* |
| `release` / `tag` | Entrega inmutable con etiqueta de etapa | *Por completar* |
| `compiled release` | Estado más reciente tras fusionar releases | *Por completar* |
| `parties` / identificador | `scheme` + `id`, preferir registro primario | *Por completar* (¿RUC? ¿qué `scheme`?) |
| `planning` / `tender` / `awards` / `contracts` | Bloques y campos del estándar | *Por completar* (campos presentes/ausentes) |
| `implementation` | Transacciones e hitos de ejecución | *Por completar* |
| Extensiones | Opcionales | *Por completar* |

