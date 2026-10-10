# Resumen del Estándar OCDS (Open Contracting Data Standard)

> [!NOTE]
> **Separación de responsabilidades:** Este documento describe la teoría oficial y el modelo de datos del estándar OCDS. Para ver cómo se aplican estos conceptos en los datos reales publicados por el SERCOP de Ecuador (y qué campos vienen realmente), consultar el documento de reconocimiento de la fuente de la Fase 0 (Issue #9).

## ¿Qué es OCDS?

El Estándar de Datos de Contrataciones Abiertas (OCDS) es un estándar global de datos abiertos, gratuito y de acceso público, implementado por más de 30 gobiernos alrededor de todo el mundo. Describe cómo estructurar y publicar datos y documentos relacionados a los procesos de contrataciones de bienes, obras y servicios. 

Se sustenta en tres conceptos clave:
1. **Contratación Abierta:** Busca publicar información accesible y oportuna para involucrar a los ciudadanos y al sector privado, mejorando así la eficiencia, efectividad e integridad de las compras públicas.
2. **Datos Abiertos:** Consiste en publicar datos legibles por máquina que cualquier persona pueda utilizar libremente, modificar y compartir.
3. **Estándar de datos:** Define una estructura y un significado común para los datos, resolviendo ambigüedades técnicas y conceptuales.

El OCDS **no es un sistema electrónico de compra ni una base de datos**; es un modelo de datos común que estandariza la recolección, almacenamiento y publicación de datos. Proporciona herramientas, listas de códigos, un mecanismo de extensión y soporte global, permitiendo a los analistas realizar investigaciones profundas sobre transparencia, competencia y valor por el dinero invertido. ([Fuente oficial: ¿Qué es OCDS?](https://standard.open-contracting.org/latest/es/primer/what/))

---

## Identificadores en OCDS

Para que los datos de contrataciones puedan vincularse correctamente entre diferentes sistemas, OCDS hace un uso riguroso de identificadores tanto globales como locales.

### 1. El Identificador del Proceso de Contratación: OCID (Global)

El **OCID (Open Contracting Identifier)** es el identificador único global para un proceso de contratación de principio a fin. Funciona como la llave primaria que une la información publicada en distintos momentos y lugares (desde la planificación hasta el contrato).

* **Composición:** Todo OCID está formado por dos partes: 
  1. Un **prefijo registrado** (ej. `ocds-87sd3t`) asignado exclusivamente por el equipo de Open Contracting a un publicador específico.
  2. El **identificador interno** del proceso de la institución (ej. `OM-DGRMSG-004-13`).
  *Resultado:* `ocds-87sd3t-OM-DGRMSG-004-13`.
* **Propósito:** Evitar colisiones. Si la Ciudad A y la Ciudad B tienen internamente un contrato "0005", el prefijo único de cada ciudad garantiza que sus procesos no se mezclen en un sistema global de datos.
* **Sensibilidad:** El OCID distingue estrictamente entre mayúsculas y minúsculas. ([Fuente oficial: Identificadores / OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))

### 2. Identificadores Locales (IDs de Entregas, Adjudicaciones, Contratos e Ítems)

No todos los IDs deben ser únicos a nivel mundial. La mayoría solo necesita ser única *dentro del ámbito de su propio proceso* (dentro del mismo OCID).
* **ID de Entrega (Release ID):** Debe ser único y consistente para cada "fotografía" de datos publicada dentro de ese proceso. No debe contener el caracter `#`.
* **IDs de Adjudicaciones y Contratos:** Un contrato debe hacer una referencia cruzada estricta a una adjudicación relacionada usando el campo `awardID`. Múltiples contratos pueden referirse a una misma adjudicación (como en los acuerdos marco).
* **IDs de Artículos (`items`), Documentos e Hitos:** Son únicos dentro de su propia matriz. Si una entrega posterior vuelve a usar el mismo ID de ítem (ej. ID "3"), el estándar interpreta que se está actualizando la información de ese artículo existente, sin necesidad de volver a publicar los artículos que no han cambiado.

---

## Manejo del Historial de Datos: Releases y Registros

Los procesos de contratación pública son vivos y cambian constantemente. OCDS captura estos cambios a través de una arquitectura basada en "Entregas" (Releases) y "Registros" (Records).

### Release (Entrega)
Un **Release** es un paquete de datos JSON que representa una fotografía de la información en un momento particular en la vida de un proceso de contratación. 
* **Inmutabilidad:** Las entregas son **estrictamente inmutables**. Una vez publicadas, un publicador no debe editarlas. Si hay nueva información o se debe corregir un error, se debe generar un nuevo *release* con una nueva fecha (`date`) y un nuevo ID (`id`).
* **Manejo de campos:** Si un campo se deja de usar, se excluye del archivo. Si un valor que antes existía debe ser eliminado explícitamente, se debe enviar el campo con el valor nulo (`null`).
* **Etiquetas (`tag`):** Cada entrega lleva una etiqueta (como `tender`, `award`, `contract`) para indicar de qué etapa del proceso trae información principal, aunque puede contener datos de etapas anteriores para dar contexto completo. ([Fuente oficial: Releases](https://standard.open-contracting.org/latest/es/primer/releases_and_records/))

### Record (Registro) y Compiled Release (Entrega Compilada)
El **Record** actúa como un índice maestro que agrupa todos los *releases* asociados a un mismo OCID. Dentro de un Record, encontramos el **Compiled Release**.
* **Compiled Release:** Dado que revisar decenas de entregas inmutables es complejo para un analista, el Compiled Release procesa todas esas entregas cronológicamente y las "fusiona" (merge). El resultado es un único JSON consolidado que muestra el **estado final, más reciente y actualizado** de cada campo del proceso de contratación. ([Fuente oficial: Compiled Release](https://standard.open-contracting.org/latest/es/schema/records_reference/#compiledrelease))

---

## Organización y Partes Involucradas (`parties`)

A partir de la versión 1.1, OCDS introdujo una sección matriz principal llamada `parties` para registrar a todos los actores (compradores, proveedores, auditores, etc.). 
Esto evita repetir los datos de la misma empresa en la licitación, la adjudicación y el contrato. Se declaran una vez en `parties` y luego solo se hace referencia a su `id`.

* **Identificadores de Organización:** Identificar legalmente a una entidad es vital para la transparencia. OCDS exige un identificador compuesto por un `scheme` (el prefijo del registro legal, ej. `GB-COH` para el registro de empresas británico) y un `id` (el número de registro oficial de la empresa). 
* **Registros Primarios vs Secundarios:** OCDS prefiere fuertemente identificadores de **Registros Primarios** (el registro mercantil o tributario nacional, como el RUC) porque otorgan estatus legal, por sobre registros secundarios (como bases de datos privadas o listas locales).
* **Roles (`roles`):** A cada organización en `parties` se le asigna un rol desde una lista oficial. Ejemplos incluyen `buyer` (quien pone el presupuesto), `procuringEntity` (la entidad que gestiona el proceso), `supplier` (el proveedor ganador) o `tenderer` (el oferente). ([Fuente oficial: Esquema de Partes](https://standard.open-contracting.org/latest/es/schema/reference/#parties))

---

## Secciones del Proceso de Contratación

La estructura del estándar divide la cronología de la compra en cuatro grandes bloques de información.

### 1. Planificación (`planning`)
Describe el contexto, los antecedentes y los presupuestos antes de que el proceso salga al mercado.
* **Justificación (`rationale`):** Explica por qué se realiza la compra.
* **Presupuesto (`budget`):** Desglosa el monto reservado, la descripción de la fuente de los fondos y el ID de la partida presupuestaria (ideal para cruzar con sistemas financieros del Estado). También vincula si la compra pertenece a un macro-proyecto (`project`).
* **Hitos (`milestones`) y Documentos (`documents`):** Permite adjuntar estudios de viabilidad, planes de necesidad o fechas límite para preparar la compra. ([Fuente oficial: Esquema de Planificación](https://standard.open-contracting.org/latest/es/schema/reference/#planning))

### 2. Licitación (`tender`)
Documenta las reglas del juego: cómo se buscarán proveedores y qué se está pidiendo.
* **Detalles del Proceso:** Incluye las fechas de publicación, inicio y fin del periodo de recepción de ofertas, y el tipo de proceso de iniciación (`initiationType`).
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
* Cada entrega debe declarar un idioma por defecto en la raíz del documento.

### Procesos Relacionados (`relatedProcesses`)
En adquisiciones complejas, una compra no está aislada. El arreglo `relatedProcesses` permite relacionar diferentes `ocid` entre sí. 
* **Caso de uso:** Vincular compras derivadas de un "Acuerdo Marco" general, o conectar un contrato con un proceso previo de planificación a nivel macro.

### Extensiones del Estándar (`extensions`)
OCDS permite añadir campos que no vienen en el estándar base usando extensiones. 
* Ejemplos comunes incluyen: agregar títulos a nivel proceso (`process_title`), dueños beneficiarios o accionistas de las empresas (`shareholders`), escala de la empresa (micro, pyme, grande con `partyScale`), o vincular compras a proyectos específicos de infraestructura.

