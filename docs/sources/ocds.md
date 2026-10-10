# Resumen del Estándar OCDS (Open Contracting Data Standard)

> [!NOTE]
> **Separación de responsabilidades:** Este documento describe la teoría oficial y el modelo de datos del estándar OCDS. Para ver cómo se aplican estos conceptos en los datos reales publicados por el SERCOP de Ecuador (y qué campos vienen realmente), consultar el documento de reconocimiento de la fuente de la Fase 0 (Issue #9).

## ¿Qué es OCDS?

El Estándar de Datos de Contrataciones Abiertas (OCDS) es un estándar global, gratuito y de acceso público que describe cómo publicar datos y documentos relacionados a los procesos de contrataciones públicas (bienes, obras y servicios). 

Se basa en tres conceptos fundamentales:
1. **Contratación Abierta:** La publicación y uso de información accesible y oportuna sobre compras públicas para involucrar a los ciudadanos y al sector privado, mejorando la eficiencia e integridad.
2. **Datos Abiertos:** Datos estructurados que pueden ser utilizados libremente, modificados y compartidos, siendo legibles por máquina.
3. **Estándar de datos:** Un conjunto de reglas que define la estructura y el significado de los datos para resolver ambigüedades.

El OCDS **no es un sistema electrónico de compra ni una base de datos**; es un modelo de datos común estructurado. Su objetivo es proporcionar un formato unificado para que la información de contrataciones pueda cruzarse, analizarse y utilizarse para detectar ineficiencias o banderas rojas de corrupción. ([Fuente oficial: ¿Qué es OCDS?](https://standard.open-contracting.org/latest/es/primer/what/))

---

## El Identificador del Proceso: OCID

Para hacer seguimiento a una compra pública desde que se planea hasta que se finaliza, es vital poder unir todos sus datos. Para ello se utiliza el **OCID (Open Contracting Identifier)**.

* **¿Qué es?:** Es un identificador único global asignado a un único proceso de contratación de principio a fin.
* **¿Cómo se forma?:** Se compone de un prefijo registrado para la agencia o publicador (por ejemplo, `ocds-87sd3t`) unido al identificador interno que usa la institución (por ejemplo, `0005`). Resultando en algo como `ocds-87sd3t-0005`.
* **Propósito:** Garantiza que no haya colisiones de IDs entre diferentes instituciones o países, actuando como la clave principal (Primary Key conceptual) que vincula todas las etapas de una misma compra. ([Fuente oficial: Identificadores / OCID](https://standard.open-contracting.org/latest/es/schema/identifiers/#contracting-process-identifier-ocid))

---

## Historial de Cambios: Releases y Compiled Releases

Los datos de contratación cambian mucho con el tiempo (se publican pliegos, se reciben ofertas, se firma el contrato, hay enmiendas). OCDS maneja esto mediante "entregas" y "registros".

* **Release (Entrega o Lanzamiento):** Es un documento JSON inmutable que se publica cada vez que hay un evento o actualización en el proceso de contratación. Cada *release* representa una "fotografía" de la información en un momento dado. Una colección de entregas de un mismo proceso (mismo `ocid`) constituye su **historial de cambios**. ([Fuente oficial: Releases](https://standard.open-contracting.org/latest/es/primer/releases_and_records/))
  
* **Compiled Release (Entrega Compilada):** Dado que leer todo el historial de *releases* para saber el estado actual es complejo, el estándar define el *Compiled Release*. Es un registro consolidado que contiene el **estado más reciente y actualizado** del proceso de contratación. Se genera combinando automáticamente todos los *releases* anteriores de un mismo `ocid`, sobreescribiendo los valores viejos con los nuevos. ([Fuente oficial: Compiled Release](https://standard.open-contracting.org/latest/es/schema/records_reference/#compiledrelease))

---

## Secciones Clave del Proceso de Contratación

La estructura principal del esquema de OCDS (el JSON) agrupa la información cronológicamente en las siguientes cinco secciones o bloques principales:

### 1. Planificación (`planning`)
Contiene los antecedentes y preparativos antes de lanzar oficialmente una licitación. Permite entender por qué se hace la compra y cómo se financia.
* **Incluye:** La justificación de la compra, información del presupuesto (montos y fuentes de financiamiento), proyectos relacionados (ej. un proyecto de infraestructura), documentos de estudio de viabilidad y los hitos planificados. ([Fuente oficial: Esquema de Planificación](https://standard.open-contracting.org/latest/es/schema/reference/#planning))

### 2. Licitación (`tender`)
Describe cómo se llevará a cabo el proceso de compra para invitar a los proveedores a presentar ofertas.
* **Incluye:** Fechas de publicación y de recepción de ofertas, método de contratación (ej. licitación abierta, adjudicación directa), el detalle exacto de los bienes o servicios que se buscan (matriz de `items`), criterios de evaluación y documentos de los pliegos. ([Fuente oficial: Esquema de Licitación](https://standard.open-contracting.org/latest/es/schema/reference/#tender))

### 3. Adjudicación (`award`)
Detalla el resultado del proceso de evaluación de ofertas. Un mismo proceso puede tener múltiples adjudicaciones (ej. si se divide en lotes entre varios proveedores).
* **Incluye:** El ID de la adjudicación, el proveedor o proveedores ganadores, la fecha en la que se tomó la decisión de adjudicar, el valor económico total adjudicado, y los artículos (`items`) específicos que se le otorgaron a ese proveedor. ([Fuente oficial: Esquema de Adjudicación](https://standard.open-contracting.org/latest/es/schema/reference/#award))

### 4. Contrato (`contract`)
Contiene los detalles legales y formales del acuerdo firmado entre la entidad y el proveedor ganador. Los contratos hacen referencia cruzada a la adjudicación de la que provienen (`awardID`).
* **Incluye:** El ID del contrato, las fechas de firma y de vigencia (inicio y fin), el valor final acordado, y una sub-sección de **Implementación (`implementation`)** que permite hacer seguimiento a las transacciones de pago e hitos de entrega durante la ejecución del contrato. ([Fuente oficial: Esquema de Contrato](https://standard.open-contracting.org/latest/es/schema/reference/#contract))

### 5. Partes Involucradas (`parties`)
Identificar a las organizaciones de manera confiable es vital. Para evitar repetir los datos de una empresa o entidad en múltiples lugares (planeación, licitación, contrato), OCDS agrupa a **todos** los actores en un solo arreglo llamado `parties`.
* **Organización:** Se registran sus datos completos: nombre legal, identificador legal oficial (compuesto por un esquema, ej. `EC-RUC`, y el ID de la empresa), dirección física y punto de contacto.
* **Roles (`roles`):** A cada parte se le asigna uno o más roles oficiales en el proceso. Los más comunes son: comprador (`buyer`), entidad contratante (`procuringEntity`), proveedor (`supplier`), oferente (`tenderer`), pagador (`payer`), entre otros.
* **Uso:** En el resto del documento (por ejemplo en `award`), solo se hace referencia al ID de la parte, lo que mantiene los datos limpios y normalizados. ([Fuente oficial: Esquema de Partes](https://standard.open-contracting.org/latest/es/schema/reference/#parties))
