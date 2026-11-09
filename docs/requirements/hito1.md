# Hito 1 · Perfil institucional y preguntas de negocio

**Equipo:** Bravo, Freire, Guajan, Pasquel, Torres (orden por confirmar) ·
**Sector:** Sector público – gobierno central · **Fecha:** por definir

> **Estado: borrador de trabajo.** Las marcas **[VERIFICAR]** señalan datos que
> aún no se abrieron en su fuente oficial; ninguna debe llegar al PDF final
> sin su enlace y fecha de consulta. Este archivo es la fuente en Markdown del
> entregable; el PDF (máximo 6 páginas, nombre
> `Hito1_Apellido1Apellido2ApellidoN.pdf`) se arma desde aquí.
> Las fuentes se consultaron el 27/10/2026 salvo que se indique otra fecha.

## Parte 1 · Perfil institucional del sector (máx. 3 páginas)

### 1. Identificación y alcance

El sector es el **gobierno central** del Ecuador, entendido como la Presidencia
de la República, los ministerios y los institutos que dependen de ellos
([ADR 0001](../adr/0001-alcance.md)). Se analiza el sector completo, no una
institución en particular.

**Tamaño aproximado.** Los candidatos se identificaron en el directorio
oficial [gob.ec/instituciones](https://www.gob.ec/instituciones) (MINTEL). Para
los ministerios se contrastó además el menú de navegación del
[portal del MDEP](https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/). Ambos se consultaron el 15/10/2026 y se volvieron a
abrir el 6/11/2026; el detalle entidad por entidad está en
[entidades.md](../sources/entidades.md).

| Categoría | Cifra aproximada | Fuente (consultada el 15/10 y el 6/11/2026) | Observación |
|---|---|---|---|
| Presidencia de la República | 1 | [gob.ec/instituciones](https://www.gob.ec/instituciones), sección `P`: `Presidencia de la República (PR)` | La `Vicepresidencia de la República (VPR)` consta aparte, en la sección `V`. El ADR 0001 no la nombra, así que no se cuenta y, por su regla 6, queda fuera de los indicadores hasta clasificarla. |
| Ministerios | 10 carteras en el menú de navegación del portal | [Portal del MDEP](https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/) y [gob.ec/instituciones/M](https://www.gob.ec/instituciones/M) | El menú muestra 10 carteras (la décima, «Trabajo y Desarrollo Humano»); no es un inventario normativo. `gob.ec` lista 18 entradas ministeriales porque junto a los ministerios fusionados en 2026 mantiene carteras previas. La vigencia de cada una se verifica con su norma en el Hito 2. |
| Institutos | 16 candidatos | [gob.ec/instituciones/I](https://www.gob.ec/instituciones/I) | De 20 entradas: 16 candidatos, 3 de seguridad social (`IESS`, `ISSPOL`, `ISSFA`) y 1 registro de prueba (`IP2026`). La inclusión del `INEN` (consta como «Servicio», sección `S`) no está decidida. |

Las cifras son aproximadas. `gob.ec` es una fuente base nominal: muestra
nombre, sigla y enlace de cada entidad, pero no acredita que la lista esté
completa ni indica de qué ministerio depende cada instituto. Esa dependencia,
y su vigencia en 2021–2025, se verifica entidad por entidad con su norma de
creación o adscripción antes de incluirla en la clasificación.

**Qué queda fuera y por qué.** Por decisión del ADR 0001 (aceptado) quedan
fuera:

- **GAD**, con autonomía política, administrativa y financiera (Constitución,
  art. 238).
- **Empresas públicas**, con personalidad jurídica y autonomía de gestión
  (art. 315).
- **Otras funciones del Estado:** Legislativa, Judicial, Electoral y de
  Transparencia y Control Social (arts. 118, 178, 217 y 204).

**Exclusión provisional.** Los Registros de la Propiedad, los Cuerpos de
Bomberos y las entidades de seguridad social (`IESS`, `ISSFA`, `ISSPOL`) no
están nombrados en el ADR 0001. Quedan fuera de los indicadores solo de forma
provisional, por la regla 6 del ADR (las entidades dudosas quedan fuera hasta
resolverse). Su clasificación definitiva se decide en el Hito 2
([entidades.md](../sources/entidades.md), sección 5.3). Lo que sustenta la duda:

- **Registros y Bomberos:** se gestionan en el ámbito municipal o de forma
  concurrente con el Ejecutivo (arts. 264, num. 13, y 265).
- **Seguridad social:** el art. 292 excluye del Presupuesto General del Estado
  (PGE) sus ingresos y egresos, y las
  [Directrices Proforma 2027](https://www.economicoproductivo.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf) del MEF (secciones 3.1 y 3.2, p. 69–70;
  consultadas el 6/11/2026) la tratan como entidades que no forman parte del
  PGE. Eso la deja fuera del PGE, pero no resuelve por sí solo su clasificación
  en este proyecto.

Los artículos citados en esta sección y en la siguiente son de la
[Constitución de la República del Ecuador](https://www.asambleanacional.gob.ec/sites/default/files/documents/old/constitucion_de_bolsillo.pdf)
(edición publicada por la Asamblea Nacional, consultada el 6/11/2026).

### 2. Misión y servicios

El art. 141 de la Constitución establece que la Presidenta o Presidente de la
República ejerce la Función Ejecutiva y es responsable de la administración
pública. La integran la Presidencia y la Vicepresidencia, los Ministerios de
Estado y los demás organismos e instituciones necesarios para ejercer, en su
ámbito, la rectoría, la planificación, la ejecución y la evaluación de las
políticas públicas nacionales y de los planes que se crean para ejecutarlas.

**Misión del sector, en palabras del equipo:** conducir la administración
pública nacional, es decir, definir hacia dónde van las políticas del país,
planificarlas, ponerlas en marcha y evaluar sus resultados, y entregar a la
población los bienes y servicios públicos que de ellas se derivan. Cada
ministerio es rector de un área (por ejemplo, salud pública, educación,
seguridad interna, defensa nacional, infraestructura, ambiente y energía, o
desarrollo económico y productivo), y los institutos aportan servicios
técnicos o de investigación en esas áreas.

Para cumplir esa misión, estas entidades compran bienes, obras y servicios.
Esa función de **compradora pública** es la que analiza este proyecto.

### 3. Actores y partes interesadas

| Actor | Rol en la contratación | Fuente |
|---|---|---|
| **Entidades contratantes** (Presidencia, ministerios, institutos) | Identifican la necesidad, la incluyen en el Plan Anual de Contratación (PAC) y adjudican (la máxima autoridad o su delegado). En los datos son el `buyer`. | LOSNCP, arts. 7, 22 y 30 |
| **Proveedores y contratistas** | Ofertan y ejecutan los contratos; deben inscribirse y habilitarse en el Registro Único de Proveedores (RUP), salvo las excepciones que fije el Reglamento. En OCDS: `tenderer` y `supplier`. | LOSNCP, arts. 7 y 19 |
| **SERCOP** | Rector del Sistema Nacional de Contratación Pública (SNCP): administra el RUP y el Portal de Contratación (datos abiertos), publica estadísticas, sanciona a proveedores y controla la fase precontractual. | LOSNCP, arts. 9 y 13 |
| **Ente rector de las finanzas públicas** (MEF) | Fija los techos presupuestarios del Presupuesto General del Estado (PGE). Su máxima autoridad integra el Directorio del SNCP, que dicta la política de contratación. | LOSNCP, arts. 9 (núm. 1) y 10; Directrices Proforma 2027, p. 4 |
| **Organismo de control** (Contraloría General del Estado) | Controla el uso de los recursos estatales y, junto con SERCOP, integra el Subsistema Nacional de Control; su base legal se detalla en la sección 4. | Constitución, arts. 211 y 212; LOSNCP, arts. 13 y 14 |
| **Ciudadanía y veedurías** | Usan la información abierta; SERCOP facilita la veeduría ciudadana. | LOSNCP, art. 9 (núm. 3 y 9) |

**Fuentes (consultadas el 8/11/2026).**
[LOSNCP, texto consolidado publicado por SERCOP](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf),
que incorpora la reforma del Registro Oficial, Cuarto Suplemento Nº 140,
7/10/2025 (numeración vigente; el texto anterior puede numerar distinto).
[Directrices Proforma 2027](https://www.economicoproductivo.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf),
p. 4 (citan los arts. 74 y 97 del COPLAFIP). Las Directrices nombran a este
actor Ministerio de Economía y Finanzas, pero
[finanzas.gob.ec](https://www.finanzas.gob.ec/) redirige al portal del
«Ministerio de Desarrollo Económico y Productivo – MDEP»
([economicoproductivo.gob.ec](https://www.economicoproductivo.gob.ec/));
por eso se usa el término de la ley, «ente rector de las finanzas públicas».

### 4. Marco normativo y entes de control

**Fecha de consulta de todos los enlaces y corte de vigencia: 8/11/2026.**
Se distingue el marco vigente a esa fecha del aplicable a los procesos de
2021–2025.

- **Constitución de la República, vigente.** El art. 288 exige que las compras
  públicas atiendan la eficiencia, transparencia, calidad y responsabilidad
  ambiental y social; da prioridad a la producción nacional, especialmente a
  la economía popular y solidaria y a las micro, pequeñas y medianas unidades
  productivas ([Asamblea Nacional, art. 288](https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf)).
- **LOSNCP, vigente con reformas.** La Ley Orgánica Reformatoria a la LOSNCP
  se publicó en el **Cuarto Suplemento del Registro Oficial 140, de 7/10/2025**
  ([Registro Oficial](https://www.registroficial.gob.ec/cuarto-suplemento-al-registro-oficial-no-140/)).
  El [texto consolidado publicado por SERCOP](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf)
  recoge esa reforma y dispone que la información del Portal de Contratación
  Pública se maneje como datos abiertos (art. 21).
- **Reglamento General de la LOSNCP, vigente con reformas.** Se expidió por
  **Decreto Ejecutivo 193**, publicado en el **Noveno Suplemento del Registro
  Oficial 153, de 28/10/2025** ([Registro Oficial](https://www.registroficial.gob.ec/noveno-suplemento-no-153/)).
  Entre sus reformas posteriores están el
  [Decreto 295, publicado el 30/1/2026](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-215-7/)
  y el [Decreto 461, publicado el 30/7/2026](https://www.registroficial.gob.ec/tercer-suplemento-no-337/).
  Este último sustituye, por ejemplo, las reglas para elegir entre subasta
  inversa electrónica y licitación (art. 14 del decreto, que sustituye el
  art. 74 del Reglamento; [texto oficial, pp. 28–29](https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/eyJjYXJwZXRhIjoicm8iLCJ1dWlkIjoiNTRiYTBmM2UtODUzYy00NTczLWE3YmItZjBkOWM3NjMzYjBkLnBkZiJ9)).
  SERCOP confirma la aplicación del Decreto 193 reformado por el 461 en su
  [resolución de 5/11/2026, p. 5](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/11/SERCOP-SERCOP-2026-0546-R.pdf).
- **LOTAIP, vigente.** La Ley Orgánica de Transparencia y Acceso a la
  Información Pública se publicó en el Segundo Suplemento del Registro
  Oficial 245, de 7/2/2023 ([Registro Oficial](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-245/)).
  Su art. 19 exige información mensual de transparencia activa, incluidos los
  procesos de contratación (numeral 8), en formato de datos abiertos
  ([texto oficial, pp. 18–20](https://www.asambleanacional.gob.ec/sites/default/files/private/asambleanacional/filesasambleanacionalnameuid-29/Leyes%202013-2017/736-jvelin/ro-245-2do-supl-07-02-2023.pdf)).
- **Ley Orgánica de Integridad Pública (LOIP), sin vigencia general al corte.**
  Se publicó el 26/6/2025 en el Tercer Suplemento del Registro Oficial 68
  ([Registro Oficial](https://www.registroficial.gob.ec/tercer-suplemento-no-68/)).
  La sentencia **52-25-IN/25**, de 26/9/2025, declaró su inconstitucionalidad
  por la forma, junto con su Reglamento y normas conexas. Publicada el
  3/10/2025 en la Edición Constitucional 96, tiene efectos generales hacia
  futuro; las excepciones retroactivas no incluyen contratación pública
  ([sentencia, párr. 343, y auto de aclaración, párrs. 32–33](https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/eyJjYXJwZXRhIjoicm8iLCJ1dWlkIjoiNjk4MGI1YmMtMjM3MS00YmNlLThhZGUtZDEwZTllMzUxMzI0LnBkZiJ9)).
- **Rectoría y control, competencias vigentes.** SERCOP ejerce la rectoría
  del sistema (LOSNCP, art. 9) y controla el cumplimiento normativo en la fase
  precontractual (art. 13). La **Contraloría General del Estado (CGE)**
  controla el uso de recursos estatales y dirige el sistema de auditoría
  interna, externa y control interno (Constitución, arts. 211–212). Ambos
  integran el Subsistema Nacional de Control, cada uno dentro de sus
  competencias ([LOSNCP, arts. 13–14](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf);
  [Constitución, arts. 211–212](https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf)).

**Implicación para 2021–2025.** La disposición transitoria primera de la
reforma de octubre de 2025 mantiene la normativa de inicio, presentación o
suscripción, según corresponda, para procedimientos, reclamos y contratos
anteriores ([LOSNCP, pp. 73–74](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf)).
El auto de aclaración citado preserva la continuidad de los procesos
precontractuales iniciados bajo la LOIP antes de publicarse la sentencia, sin
autorizar nuevos procesos bajo esa ley desde esa publicación. Por ello no
corresponde tratar todo 2025 como un único régimen ni trasladar las reglas de
2026 a toda la serie histórica. Como **recomendación analítica para hitos
posteriores**, se propone conservar el procedimiento original de la fuente y
documentar por separado cualquier clasificación homogénea derivada; es una
inferencia metodológica, no una función ya implementada del DW.

### 5. Procesos clave

La cadena de contratación se publica en el estándar OCDS en cuatro etapas:
**planificación, licitación, adjudicación y contrato**
([ocds.md](../sources/ocds.md)). Cada proceso se identifica con un `ocid`.
Un proceso puede tener varias adjudicaciones y contratos.

| Etapa OCDS | Qué ocurre | Quién actúa | Qué toman P1 a P3 |
|---|---|---|---|
| **Planificación** (`planning`) | La entidad justifica la compra y reserva presupuesto; la necesidad alimenta el PAC (LOSNCP, art. 22). | Entidad | Nada |
| **Licitación** (`tender`) | Define cómo buscar proveedores: método (`procurementMethod`), plazo de ofertas, ítems y valor estimado (`tender.value`). | Entidad y oferentes | Método (P1, P2) y valor estimado (P2) |
| **Adjudicación** (`awards`) | Decide a quién se adjudica; la adopta la máxima autoridad o su delegado (art. 30). Puede haber varias por proceso. | Entidad y proveedor adjudicado | Valor adjudicado (`awards[].value.amount`): P1 a P3 |
| **Contrato** (`contracts`) | Formaliza el acuerdo y referencia la adjudicación (`awardID`); puede incluir la ejecución (`implementation`). | Entidad y proveedor | Nada: es otra magnitud |

Los procedimientos que llevan a la adjudicación (catálogo electrónico, subasta
inversa electrónica, licitación, ínfima cuantía y otros) los regulan los arts.
44 a 52 de la LOSNCP; por ejemplo, la licitación procede cuando no
corresponde subasta inversa ni catálogo y el presupuesto referencial supera
USD 10.000 (art. 48). Qué publica SERCOP en cada etapa se comprueba en
[ocds.md](../sources/ocds.md#estándar-vs-fuente-real-sercop):
`implementation` no figura como inspeccionada.

### 6. Tomadores de decisión

| Decisor | Decisión principal | Respaldo en la norma o en las funciones oficiales |
|---|---|---|
| **SERCOP** (ente rector) | Qué procedimientos reforzar o controlar y qué alertas priorizar | LOSNCP, art. 9: rectoría del SNCP, estadísticas y parámetros de resultados (núm. 4) y sanciones a proveedores (núm. 10); art. 13: control de la fase precontractual. La reforma crea alertas tempranas ([boletín 19 de SERCOP](https://portal.compraspublicas.gob.ec/sercop/reformas-a-la-losncp-mas-transparencia-y-eficiencia-en-las-compras-publicas/), 28/10/2025). |
| **Entidades contratantes** (órgano requirente y máxima autoridad) | Con qué procedimiento contratar y cuánto planificar contratar | LOSNCP, art. 22: el órgano requirente identifica la necesidad y con ella se forma el PAC (publicado hasta el 15 de enero); arts. 44 a 52: procedimientos (el 48 fija cuándo corresponde la licitación); art. 30: adjudica la máxima autoridad o su delegado. |
| **MEF** (ente rector de las finanzas públicas) | Cuánto presupuesto asignar y cómo programar el gasto en contratación | Directrices Proforma 2027, p. 4, citando el COPLAFIP: art. 74, incisos 8 y 9 (techos presupuestarios globales, institucionales y de gasto; proforma del PGE) y art. 97. Integra el Directorio del SNCP (LOSNCP, art. 10). |

Consulta del 8/11/2026; fuentes en la sección 3. Es inferencia del
equipo, porque la norma no lo dice, que los techos de gasto del MEF alcancen al
gasto en contratación.

### 7. Indicadores habituales

SERCOP publica cada año su rendición de cuentas. Se abrió el
[informe preliminar 2025](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/04/Informe_Preliminar_RDC2025_vf.pdf)
(95 páginas, consultado el 8/11/2026; cifras provisionales según el propio
informe; las páginas citadas son las del visor de PDF). Sus cifras son de la
contratación pública **nacional**, que incluye GAD y empresas públicas: ilustran
cómo se mide el sector, pero no son cifras del gobierno central.

| Indicador | Cómo lo calcula SERCOP | Dato 2025 (nacional) | Pág. |
|---|---|---|---|
| Monto adjudicado y su peso | Total adjudicado y su porcentaje del PGE y del PIB | USD 7.318,7 millones; 20,3 % del PGE; 5,5 % del PIB | 12 |
| Monto por procedimiento | Suma de lo adjudicado por tipo de procedimiento | Régimen común: USD 5.181,3 millones en 218.246 procesos; el mayor monto fue de la subasta inversa electrónica (USD 1.549,5 millones) | 16 |
| Monto por tipo de compra | Participación de cada tipo en el total adjudicado | Servicios 36,6 %; bienes 30,6 %; obras 27,2 % | 19 |
| Ahorro | Presupuesto menos adjudicado en los procesos del régimen común, sin ferias inclusivas | USD 461,4 millones (USD 502,5 millones en 2024) | 13 y 14 |
| Concentración | Participación de las diez principales actividades económicas (CIIU) en el monto | 67,6 % | 14 |

La guía del Hito 1 (sección 6) también menciona la ejecución presupuestaria del
MEF como indicador típico de este sector. El MEF la publica en informes en PDF
(sección 8) y no se usa mientras no exista un conjunto descargable. De esta
lista, P1 retoma el monto por procedimiento, P2 es el equivalente del ahorro
calculado con campos de la descarga y P3 proyecta el monto adjudicado.

### 8. Fuentes de datos

| Fuente | Dueño | Formato | Periodicidad | Años | Licencia | Enlace |
|---|---|---|---|---|---|---|
| Datos abiertos de contratación (OCDS) | SERCOP | JSON, CSV, XLSX por año y mes; API | Descargas actualizadas a diario | 2015 en adelante según la API; abiertos 2021, 2024, 2025 y enero 2025 | Creative Commons Atribución 3.0 Ecuador: obliga a enlazar la fuente ([política de SERCOP, p. 8](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf), consultada el 3/11/2026) | [Descarga masiva](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) |
| Directorio de instituciones | MINTEL (`gob.ec`) | Páginas web por sección | No declarada en el sitio (consultado el 3/11/2026) | Vigente 2026 | Sin licencia explícita; se usa solo para clasificar entidades, citando el enlace | [gob.ec/instituciones](https://www.gob.ec/instituciones) |

Ejecución presupuestaria del MEF: se encontraron informes en PDF
([ejemplo 2019](https://www.finanzas.gob.ec/wp-content/uploads/downloads/2020/04/Inf_ejec.presupuestaria_2019.pdf)),
pero no se ha confirmado un conjunto descargable por entidad. No se usa como
fuente hasta abrir un archivo real.

**Prueba del archivo realizada:** se descargaron y abrieron los ZIP anuales de
2021, 2024 y 2025 (167.058, 219.185 y 190.619 procesos) y el de enero de 2025.
En los tres años anuales existen el importe adjudicado, el importe estimado de
la licitación, el método de contratación y el comprador; los conteos y el
método están en [reconocimiento.md](../sources/reconocimiento.md). Descarga de
2021 y 2024 el 3/11/2026.

## Parte 2 · Matriz de preguntas de negocio

Ventana de análisis: **2021–2025, años calendario completos** (5 periodos). La
fecha que asigna un proceso a un año se fija en el Hito 2 tras medir qué fecha
está más completa en los datos.

| Pregunta de negocio | Decisor y decisión | Indicador (fórmula) | Dimensiones | Fuente candidata |
|---|---|---|---|---|
| **P1 (descriptiva).** ¿Cómo evolucionó el monto adjudicado por método de contratación entre 2021 y 2025 en el gobierno central, por año y tipo de entidad (Presidencia, ministerio, instituto)? | Entidades contratantes (órgano requirente) y SERCOP: qué procedimientos priorizar al planificar | **Monto adjudicado** = Σ `awards[].value.amount` de los procesos del sector. Numerador: suma de importes adjudicados; sin denominador (es una suma); unidad: USD | Año, método de contratación, tipo de entidad, entidad | SERCOP, [descarga masiva JSON anual](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/); tipo de entidad con el directorio [gob.ec](https://www.gob.ec/instituciones) |
| **P2 (diagnóstica).** ¿Qué métodos de contratación se asocian a mayor desviación porcentual entre el valor adjudicado y el valor estimado de la licitación, según el tipo de entidad, entre 2021 y 2025 en el gobierno central? | SERCOP: dónde reforzar los controles | **Desviación %** = (A − E) ÷ E × 100, con A = Σ `awards[].value.amount` del proceso y E = `tender.value.amount`. Numerador: A − E (USD); denominador: E (USD); unidad: %. Solo procesos con A y E. Por grupo (método × tipo de entidad): (ΣA − ΣE) ÷ ΣE × 100 | Método, tipo de entidad, año | SERCOP, [descarga masiva JSON anual](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) (`tender.value.amount` y `awards[].value.amount`) |
| **P3 (predictiva).** ¿Cuál es el monto adjudicado esperado por mes en el primer semestre de 2026 en el gobierno central, para cada tipo de entidad? | MEF y entidades contratantes: programar el presupuesto de contratación | **Monto mensual proyectado** (USD) = pronóstico de la serie mensual del monto adjudicado de P1, con datos de 2021–2025. Error de validación (**WAPE**, propuesta del equipo) = Σ\|real − proyectado\| ÷ Σ real × 100 sobre los 12 meses retenidos de 2025; numerador y denominador en USD; unidad: % | Mes, tipo de entidad | SERCOP, serie mensual 2021–2025 construida desde la [descarga masiva](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) |

**Campos y cobertura (prueba del archivo).** Se abrieron los ZIP anuales de
2021, 2024 y 2025 ([reconocimiento.md](../sources/reconocimiento.md)). Los
conteos son nacionales, sin filtrar por planta central:

- **P1.** `awards[].value.amount` es numérico en 166.980 de 166.983
  adjudicaciones (2021), 210.439 de 210.445 (2024) y 183.887 de 183.891 (2025),
  siempre en USD. `tender.procurementMethod` toma cuatro valores (`open`,
  `selective`, `limited` y `direct`) y `buyer.id` y `buyer.name` constan en
  todos los releases.
- **P2.** `tender.value.amount` y `awards[].value.amount` coinciden en 146.314,
  187.672 y 166.555 releases: el 87,6 %, el 85,6 % y el 87,4 % de los
  releases de cada año. En 2025, 300 releases tienen más de una adjudicación,
  y A suma todas las de su proceso. Que E equivalga al presupuesto con el que
  SERCOP calcula su ahorro (sección 7) no está verificado.
- **P3.** `release.date` consta en todos los releases, pero el archivo de un
  año trae fechas de otro (el de 2021 trae 18.235 releases con fecha de 2022)
  y `awards[].date` solo consta en el 15–18 % de las adjudicaciones. La fecha
  que asigna el mes se decide en el Hito 2.
- **No son campos de la fuente:** el tipo de entidad (sale de clasificar el
  `buyer` con el directorio `gob.ec`, Hito 2) ni el año y el mes (derivan de la
  fecha elegida). Los importes adjudicado, estimado y contractual son
  magnitudes distintas y no se sustituyen entre sí.

## Anexo A · Preguntas candidatas (lluvia de ideas)

La guía pide partir de al menos ocho preguntas y filtrarlas con las cinco
condiciones (decisión concreta, medible, con alcance, respondible con datos
públicos, analítica). Las tres primeras son las elegidas; las demás se
conservan por si el profesor pide más preguntas en hitos posteriores.

| # | Candidata | Tipo | Veredicto |
|---|---|---|---|
| 1 | Evolución del monto adjudicado por método y tipo de entidad, 2021–2025 | Descriptiva | **P1** |
| 2 | Métodos asociados a mayor desviación entre adjudicado y estimado | Diagnóstica | **P2** |
| 3 | Monto adjudicado esperado por mes en 2026 por tipo de entidad | Predictiva | **P3** |
| 4 | ¿Cómo se concentra la contratación por proveedor en cada tipo de entidad? | Descriptiva | Reserva: depende de que el campo de proveedores se pueda usar sin romper el grano |
| 5 | ¿Qué entidades concentran más procesos con un único oferente? | Diagnóstica | Reserva: requiere confirmar el campo en los datos |
| 6 | ¿Cómo evoluciona el número de procesos por método entre años? | Descriptiva | Reserva: se puede responder con el mismo modelo que P1 |
| 7 | ¿Con qué frecuencia faltan datos de importe, método o fecha, por entidad? | Diagnóstica | Se mueve al informe de calidad del Hito 2: es calidad de datos, no una decisión de negocio |
| 8 | ¿Qué proporción del monto se adjudica por procedimientos de menor control? | Descriptiva | Descartada por ahora: "menor control" no está definido en las fuentes y exigiría una clasificación propia |

### Comprobación de las cinco condiciones en P1 a P3

Se contrastó cada pregunta con las cinco condiciones de la guía (sección 3.2).
Los ajustes que resultaron de esta comprobación ya están en la matriz: «gobierno
central» en las tres preguntas y, en P2, el periodo 2021–2025 y el adjetivo
«porcentual» (sin ellos faltaba el alcance y no se sabía si «desviación» era
absoluta o relativa).

| Condición | P1 | P2 | P3 |
|---|---|---|---|
| Apoya una decisión concreta de un actor identificado | Cumple: las entidades contratantes y SERCOP deciden qué procedimientos priorizar (sección 6) | Cumple: SERCOP decide dónde reforzar controles (LOSNCP, arts. 9 y 13) | Cumple con salvedad: que los techos de gasto del MEF alcancen al gasto en contratación es inferencia del equipo (sección 6) |
| Es medible | Cumple: suma en USD | Cumple: razón de dos importes en USD, en % | Cumple: pronóstico en USD con error en % (WAPE) |
| Tiene alcance | Cumple: 2021–2025, gobierno central de Ecuador, año × método × tipo de entidad | Cumple tras el ajuste: 2021–2025, gobierno central, método × tipo de entidad | Cumple: primer semestre de 2026, gobierno central, mes × tipo de entidad |
| Es respondible con datos públicos descargables | Cumple: campos presentes en los tres archivos anuales abiertos; el tipo de entidad depende de la clasificación del Hito 2 | Cumple para el 85,6–87,6 % de los releases (los que traen ambos importes) | Condicionada: depende de la fecha que se elija en el Hito 2 (`awards[].date` solo consta en el 15–18 %) |
| Es analítica | Cumple: tendencia en el tiempo cruzada con dos dimensiones | Cumple: compara métodos y tipos de entidad | Cumple: proyecta una serie en el tiempo |

## Criterios de aceptación del hito (autocomprobación)

- [ ] El perfil cubre los ocho componentes con datos vigentes y citados.
- [x] El análisis es del sector completo.
- [x] Marco normativo y entes de control verificados al 8/11/2026 (sección 4),
      con distinción del régimen aplicable a 2021–2025.
- [x] Tres tomadores de decisión, cada uno con su decisión principal.
- [x] Las tres preguntas cumplen las cinco condiciones de la guía.
- [x] Una descriptiva y una diagnóstica; la tercera es predictiva.
- [x] Cada fuente tiene enlace y fecha de consulta.
- [ ] Todas las marcas **[VERIFICAR]** y **[PENDIENTE]** resueltas.
