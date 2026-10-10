# Resumen del Estándar OCDS (Open Contracting Data Standard)

## ¿Qué es OCDS?

Está diseñado para brindar soporte a la publicación de datos de procesos de contratación pública, desde la etapa inicial de planificación hasta la ejecución y finalización del contrato. (Fuente: [Introducción a OCDS](https://standard.open-contracting.org/latest/es/))

> [!NOTE]
> **Separación de responsabilidades:** Este documento describe la teoría oficial del estándar OCDS. Para ver cómo se aplican estos conceptos en los datos reales publicados por el SERCOP de Ecuador, y qué campos vienen realmente, consultar el documento de reconocimiento de la fuente de la Fase 0.

## Conceptos Clave

* **OCID (Open Contracting Identifier):** Es un identificador único y global asignado a un único proceso de contratación de principio a fin. Funciona como una clave principal que permite agrupar toda la información de las distintas etapas de una misma compra bajo un identificador común. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/releases_and_records/#ocid))
* **Release (Lanzamiento/Entrega):** Es un paquete de datos (un objeto JSON) que se publica cada vez que hay una actualización o cambia la información de un proceso de contratación. Los releases son inmutables y forman el historial de cambios del proceso a lo largo del tiempo. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/releases_and_records/#releases))
* **Compiled Release (Entrega Compilada):** Es un único registro consolidado que muestra el estado más reciente y actualizado de un proceso de contratación. Se genera combinando y sobreescribiendo la información de todos los *releases* anteriores asociados a un mismo `ocid`. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/releases_and_records/#compiled-releases))

## Secciones del Proceso de Contratación

El estándar divide la información temporal de una compra pública en las siguientes secciones o bloques principales:

* **Planificación (`planning`):** Contiene información sobre los presupuestos, estudios previos y planes de contratación que se realizan antes de lanzar oficialmente una licitación al mercado. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/contracting_process/#planning))
* **Licitación (`tender`):** Describe cómo se llevará a cabo el proceso de compra. Incluye las fechas de publicación, periodos de recepción de ofertas, el detalle de los bienes o servicios exactos que se buscan (ítems) y los criterios de evaluación. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/contracting_process/#tender))
* **Adjudicación (`award`):** Detalla el resultado del proceso de licitación. Informa a qué proveedor (o proveedores) se le otorgó la compra, la fecha de la decisión y el valor económico de la oferta ganadora. Es posible que existan múltiples adjudicaciones por un solo proceso. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/contracting_process/#award))
* **Contrato (`contract`):** Contiene los detalles legales del acuerdo formal firmado con el proveedor ganador. Incluye fechas de firma, periodo de vigencia, valor final acordado y las condiciones de ejecución. ([Ver documentación](https://standard.open-contracting.org/latest/es/getting_started/contracting_process/#contract))

## Organización y Partes (`parties`)

* **Partes (`parties`):** Es un arreglo (matriz) donde se listan todas las organizaciones, entidades o personas que participan en el proceso de contratación. En lugar de repetir los datos de un proveedor en la licitación y en el contrato, se registran sus datos (nombre, RUC/ID, dirección) una sola vez en la sección `parties`, y en el resto del documento solo se hace referencia a su ID. Cada parte tiene uno o más *roles*, como *comprador* (buyer), *entidad contratante* (procuringEntity) o *proveedor* (supplier). ([Ver documentación](https://standard.open-contracting.org/latest/es/schema/reference/#parties))
