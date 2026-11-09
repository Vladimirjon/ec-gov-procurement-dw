# Hito 1: Perfil institucional y preguntas de negocio

**Equipo:** Trazabilidad Pública

**Integrantes:** Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel y Jorge Torres

**Sector:** Gobierno central del Ecuador

**Fecha:** 8 de noviembre de 2026

<!-- Fuente del Word: scripts/build_hito1_docx.py lo arma desde este archivo.
     La sección "Criterios de aceptación del hito" no entra en el Word. -->

## Parte 1. Perfil institucional del sector

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

Tabla: Entidades del sector según su categoría

| Categoría | Cifra aproximada | Fuente | Observación |
|---|---|---|---|
| Presidencia de la República | 1 | [gob.ec/instituciones](https://www.gob.ec/instituciones), sección `P`: `Presidencia de la República (PR)` | La Vicepresidencia (`VPR`) consta aparte; el ADR 0001 no la nombra, así que no se cuenta y, por su regla 6, queda fuera de los indicadores hasta clasificarla. |
| Ministerios | 10 carteras en el menú de navegación del portal | [Portal del MDEP](https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/) y [gob.ec/instituciones/M](https://www.gob.ec/instituciones/M) | No es un inventario normativo. `gob.ec` lista 18 entradas porque, junto a los ministerios fusionados en 2026, mantiene carteras previas; su vigencia se verifica en el Hito 2. |
| Institutos | 16 candidatos | [gob.ec/instituciones/I](https://www.gob.ec/instituciones/I) | De 20 entradas: 16 candidatos, 3 de seguridad social y 1 registro de prueba. La inclusión del `INEN` (consta como «Servicio») no está decidida. |

Tabla: Entidades excluidas del sector y su respaldo

| Excluidas | Condición | Respaldo (Constitución) |
|---|---|---|
| **GAD** | Decisión del ADR 0001 | Autonomía política, administrativa y financiera (art. 238) |
| **Empresas públicas** | Decisión del ADR 0001 | Personalidad jurídica y autonomía de gestión (art. 315) |
| **Otras funciones del Estado:** Legislativa, Judicial, Electoral y de Transparencia y Control Social | Decisión del ADR 0001 | Arts. 118, 178, 217 y 204 |
| **Registros de la Propiedad y Cuerpos de Bomberos** | Exclusión provisional (regla 6 del ADR) | Se gestionan en el ámbito municipal o de forma concurrente con el Ejecutivo (arts. 264, num. 13, y 265) |
| **Seguridad social** (`IESS`, `ISSFA`, `ISSPOL`) | Exclusión provisional (regla 6 del ADR) | Art. 292: sus ingresos y egresos quedan fuera del Presupuesto General del Estado (PGE); las [Directrices Proforma 2027](https://www.economicoproductivo.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf) del MEF (pp. 69–70) la tratan como ajena al PGE |

### 2. Misión y servicios

Según el art. 141 de la Constitución, la Presidenta o Presidente de la República
ejerce la Función Ejecutiva y es responsable de la administración pública, que
integran la Presidencia, la Vicepresidencia, los Ministerios de Estado y los
demás organismos necesarios para la rectoría, planificación, ejecución y
evaluación de las políticas públicas nacionales.

**Misión del sector, en palabras del equipo:** conducir la administración
pública nacional, es decir, definir hacia dónde van las políticas del país,
planificarlas, ponerlas en marcha y evaluar sus resultados, y entregar a la
población los bienes y servicios públicos que de ellas se derivan. Cada
ministerio es rector de un área (salud, educación, seguridad, defensa,
infraestructura…) y los institutos aportan servicios técnicos o de investigación.

Para cumplir esa misión estas entidades compran bienes, obras y servicios; esa función de **compradora pública** es la que analiza este proyecto.

### 3. Actores y partes interesadas

Tabla: Actores y partes interesadas de la contratación pública

| Actor | Rol en la contratación | Fuente |
|---|---|---|
| **Entidades contratantes** (Presidencia, ministerios, institutos) | Identifican la necesidad, la incluyen en el Plan Anual de Contratación (PAC) y adjudican (máxima autoridad o su delegado). En los datos son el `buyer`. | LOSNCP, arts. 7, 22 y 30 |
| **Proveedores y contratistas** | Ofertan y ejecutan los contratos; deben estar en el Registro Único de Proveedores (RUP), salvo excepciones. En OCDS: `tenderer` y `supplier`. | LOSNCP, arts. 7 y 19 |
| **SERCOP** | Rector del Sistema Nacional de Contratación Pública (SNCP): administra el RUP y el Portal de Contratación, publica estadísticas, sanciona a proveedores y controla la fase precontractual. | LOSNCP, arts. 9 y 13 |
| **Ente rector de las finanzas públicas** (MEF) | Fija los techos presupuestarios del Presupuesto General del Estado (PGE). Su máxima autoridad integra el Directorio del SNCP, que dicta la política de contratación. | LOSNCP, arts. 9 (núm. 1) y 10; Directrices Proforma 2027, p. 4 |
| **Organismo de control** (Contraloría General del Estado) | Controla el uso de los recursos estatales y, con SERCOP, integra el Subsistema Nacional de Control (sección 4). | Constitución, arts. 211 y 212; LOSNCP, arts. 13 y 14 |
| **Ciudadanía y veedurías** | Usan la información abierta; SERCOP facilita la veeduría ciudadana. | LOSNCP, art. 9 (núm. 3 y 9) |

### 4. Marco normativo y entes de control

Tabla: Marco normativo y entes de control de la contratación pública

| Norma | Situación | Qué establece | Fuente |
|---|---|---|---|
| **Constitución** | Vigente | Art. 288: las compras públicas atienden eficiencia, transparencia, calidad y responsabilidad ambiental y social, y priorizan la producción nacional, en especial la economía popular y solidaria y las micro, pequeñas y medianas empresas. | [Constitución, art. 288](https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf) |
| **LOSNCP** | Vigente con reformas | Reformada en el Cuarto Suplemento del Registro Oficial 140 (7/10/2025). Art. 21: la información del Portal de Contratación Pública se maneja como datos abiertos. | [RO 140](https://www.registroficial.gob.ec/cuarto-suplemento-al-registro-oficial-no-140/); [texto consolidado](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf) |
| **Reglamento General de la LOSNCP** | Vigente con reformas | Decreto 193 (RO 153, 28/10/2025), reformado por los decretos 295 (30/1/2026) y 461 (30/7/2026); SERCOP confirma su aplicación (resolución de 5/11/2026, p. 5). | [RO 153](https://www.registroficial.gob.ec/noveno-suplemento-no-153/); [Decreto 295](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-215-7/); [Decreto 461](https://www.registroficial.gob.ec/tercer-suplemento-no-337/); [resolución](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/11/SERCOP-SERCOP-2026-0546-R.pdf) |
| **LOTAIP** | Vigente | RO 245 (7/2/2023). Art. 19: información mensual de transparencia activa, incluidos los procesos de contratación (numeral 8), en datos abiertos. | [RO 245](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-245/); [texto oficial, pp. 18–20](https://www.asambleanacional.gob.ec/sites/default/files/private/asambleanacional/filesasambleanacionalnameuid-29/Leyes%202013-2017/736-jvelin/ro-245-2do-supl-07-02-2023.pdf) |
| **LOIP** (Integridad Pública) | Sin vigencia general al corte | Publicada el 26/6/2025 (Tercer Suplemento del RO 68). La sentencia 52-25-IN/25 (26/9/2025) la declaró inconstitucional por la forma, con efectos hacia futuro (3/10/2025) y sin excepciones retroactivas para la contratación pública. | [RO 68](https://www.registroficial.gob.ec/tercer-suplemento-no-68/); [sentencia, párr. 343, y auto de aclaración, párrs. 32–33](https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/eyJjYXJwZXRhIjoicm8iLCJ1dWlkIjoiNjk4MGI1YmMtMjM3MS00YmNlLThhZGUtZDEwZTllMzUxMzI0LnBkZiJ9) |
| **Rectoría y control** | Vigentes | SERCOP ejerce la rectoría (LOSNCP, art. 9) y controla la fase precontractual (art. 13). La Contraloría General del Estado (CGE) controla el uso de recursos estatales y dirige la auditoría y el control interno (Constitución, arts. 211–212). Ambos integran el Subsistema Nacional de Control. | [LOSNCP, arts. 13–14](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf); [Constitución, arts. 211–212](https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf) |

**Implicación para 2021–2025.** La disposición transitoria primera de la reforma de octubre de 2025 mantiene la normativa de inicio, presentación o suscripción para los procedimientos, reclamos y contratos anteriores ([LOSNCP, pp. 73–74](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf)), y el auto de aclaración preserva los procesos iniciados bajo la LOIP antes de la sentencia. Por eso no se trata todo 2025 como un único régimen ni se aplican las reglas de 2026 a toda la serie.

### 5. Procesos clave

La cadena de contratación se publica en el estándar OCDS en cuatro etapas:
**planificación, licitación, adjudicación y contrato**
([ocds.md](../sources/ocds.md)). Cada proceso se identifica con un `ocid`.
Un proceso puede tener varias adjudicaciones y contratos.

Tabla: Etapas de la cadena de contratación según OCDS

| Etapa OCDS | Qué ocurre y quién actúa | Qué toman P1 a P3 |
|---|---|---|
| **Planificación** (`planning`) | La entidad justifica la compra y reserva presupuesto; la necesidad alimenta el PAC (LOSNCP, art. 22). | Nada |
| **Licitación** (`tender`) | La entidad y los oferentes definen cómo buscar proveedores: método (`procurementMethod`), plazo de ofertas, ítems y valor estimado (`tender.value`). | Método (P1, P2) y valor estimado (P2) |
| **Adjudicación** (`awards`) | La máxima autoridad o su delegado decide a quién se adjudica (art. 30); puede haber varias adjudicaciones por proceso. | Valor adjudicado (`awards[].value.amount`): P1 a P3 |
| **Contrato** (`contracts`) | La entidad y el proveedor formalizan el acuerdo, que referencia la adjudicación (`awardID`) y puede incluir la ejecución (`implementation`). | Nada: es otra magnitud |

Los arts. 44 a 52 de la LOSNCP regulan los procedimientos (por ejemplo, la
licitación procede cuando no corresponde subasta inversa ni catálogo y el
presupuesto referencial supera USD 10.000, art. 48). Qué publica SERCOP en cada
etapa: [ocds.md](../sources/ocds.md#estándar-vs-fuente-real-sercop).

### 6. Tomadores de decisión

Tabla: Tomadores de decisión y su decisión principal

| Decisor | Decisión principal | Respaldo en la norma o en las funciones oficiales |
|---|---|---|
| **SERCOP** (ente rector) | Qué procedimientos reforzar o controlar y qué alertas priorizar | LOSNCP, art. 9 (rectoría, estadísticas, sanciones: núms. 4 y 10) y art. 13 (control precontractual). La reforma crea alertas tempranas ([boletín 19](https://portal.compraspublicas.gob.ec/sercop/reformas-a-la-losncp-mas-transparencia-y-eficiencia-en-las-compras-publicas/), 28/10/2025). |
| **Entidades contratantes** (órgano requirente y máxima autoridad) | Con qué procedimiento contratar y cuánto planificar contratar | LOSNCP, art. 22: el órgano requirente identifica la necesidad y con ella se forma el PAC; arts. 44 a 52: procedimientos (el 48, la licitación); art. 30: adjudica la máxima autoridad o su delegado. |
| **MEF** (ente rector de las finanzas públicas) | Cuánto presupuesto asignar y cómo programar el gasto en contratación | Directrices Proforma 2027, p. 4, citando el COPLAFIP: art. 74, incisos 8 y 9 (techos presupuestarios y proforma del PGE) y art. 97. Integra el Directorio del SNCP (LOSNCP, art. 10). |

### 7. Indicadores habituales

SERCOP rinde cuentas cada año. Se abrió el
[informe preliminar 2025](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/04/Informe_Preliminar_RDC2025_vf.pdf)
(95 páginas, consultado el 8/11/2026; cifras provisionales). Son cifras **nacionales**, con GAD y empresas públicas: ilustran cómo se
mide el sector, no son cifras del gobierno central.

Tabla: Indicadores de la rendición de cuentas 2025 de SERCOP

| Indicador | Cómo lo calcula SERCOP | Dato 2025 (nacional) | Pág. |
|---|---|---|---|
| Monto adjudicado y su peso | Total adjudicado y su porcentaje del PGE y del PIB | USD 7.318,7 millones; 20,3 % del PGE; 5,5 % del PIB | 12 |
| Monto por procedimiento | Suma de lo adjudicado por tipo de procedimiento | Régimen común: USD 5.181,3 millones en 218.246 procesos; el mayor monto fue de la subasta inversa electrónica (USD 1.549,5 millones) | 16 |
| Ahorro | Presupuesto menos adjudicado en los procesos del régimen común, sin ferias inclusivas | USD 461,4 millones (USD 502,5 millones en 2024) | 13 y 14 |
| Concentración | Participación de las diez principales actividades económicas (CIIU) en el monto | 67,6 % | 14 |

### 8. Fuentes de datos

Tabla: Fuentes de datos públicas del sector

| Fuente y dueño | Formato y periodicidad | Años y licencia | Enlace |
|---|---|---|---|
| Datos abiertos de contratación (OCDS), SERCOP | JSON, CSV y XLSX por año y mes, y API; descargas actualizadas a diario | 2015 en adelante según la API; abiertos 2021, 2024, 2025 y enero 2025. Licencia CC BY 3.0 Ecuador: obliga a enlazar la fuente ([política de SERCOP, p. 8](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf), 3/11/2026) | [Descarga masiva](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) |
| Directorio de instituciones, MINTEL (`gob.ec`) | Páginas web por sección; periodicidad no declarada (3/11/2026) | Vigente 2026. Sin licencia explícita: solo para clasificar entidades, citando el enlace | [gob.ec/instituciones](https://www.gob.ec/instituciones) |

## Parte 2. Matriz de preguntas de negocio

Ventana de análisis: **2021–2025, años calendario completos** (5 periodos). La
fecha que asigna un proceso a un año se fija en el Hito 2 tras medir qué fecha
está más completa en los datos.

Tabla: Matriz de preguntas de negocio

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

## Anexo A. Preguntas candidatas

Tabla: Preguntas candidatas y veredicto

| # | Candidata | Tipo | Veredicto |
|---|---|---|---|
| 1 | Evolución del monto adjudicado por método y tipo de entidad, 2021–2025 | Descriptiva | **P1** |
| 2 | Métodos asociados a mayor desviación entre adjudicado y estimado | Diagnóstica | **P2** |
| 3 | Monto adjudicado esperado por mes en 2026 por tipo de entidad | Predictiva | **P3** |

### Comprobación de las cinco condiciones en P1 a P3

Se contrastó cada pregunta con las cinco condiciones de la guía (sección 3.2).

Tabla: Las cinco condiciones aplicadas a P1, P2 y P3

| Condición | P1 | P2 | P3 |
|---|---|---|---|
| Apoya una decisión concreta de un actor identificado | Cumple: las entidades contratantes y SERCOP deciden qué procedimientos priorizar (sección 6) | Cumple: SERCOP decide dónde reforzar controles (LOSNCP, arts. 9 y 13) | Cumple con salvedad: que los techos de gasto del MEF alcancen al gasto en contratación es inferencia del equipo (sección 6) |
| Es medible | Cumple: suma en USD | Cumple: razón de dos importes en USD, en % | Cumple: pronóstico en USD con error en % (WAPE) |
| Tiene alcance | Cumple: 2021–2025, gobierno central de Ecuador, año × método × tipo de entidad | Cumple tras el ajuste: 2021–2025, gobierno central, método × tipo de entidad | Cumple: primer semestre de 2026, gobierno central, mes × tipo de entidad |
| Responde a datos públicos descargables | Cumple: campos presentes en los tres archivos anuales abiertos; el tipo de entidad depende de la clasificación del Hito 2 | Cumple para el 85,6–87,6 % de los releases (los que traen ambos importes) | Condicionada: depende de la fecha que se elija en el Hito 2 (`awards[].date` solo consta en el 15–18 %) |
| Es analítica | Cumple: tendencia en el tiempo cruzada con dos dimensiones | Cumple: compara métodos y tipos de entidad | Cumple: proyecta una serie en el tiempo |

## Anexo B. Declaración de uso de inteligencia artificial

El equipo usó asistentes de IA para leer y resumir fuentes, redactar borradores,
recalcular conteos y revisar enlaces. La guía del proyecto pide declarar qué se
pidió y cómo se verificó: cada uso consta, por persona y fecha, en el
[registro de uso de IA](../uso-de-ia.md).

## Anexo C. Referencias

- Asamblea Nacional del Ecuador. (2008). *Constitución de la República del Ecuador* (edición de bolsillo). [https://www.asambleanacional.gob.ec/sites/default/files/documents/old/constitucion_de_bolsillo.pdf](https://www.asambleanacional.gob.ec/sites/default/files/documents/old/constitucion_de_bolsillo.pdf) Consultado el 6/11/2026.
- Asamblea Nacional del Ecuador. (2008). *Constitución de la República del Ecuador* (arts. 211, 212 y 288). [https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf](https://www.asambleanacional.gob.ec/documentos/Constitucion-2008.pdf) Consultado el 8/11/2026.
- Asamblea Nacional del Ecuador. (2023). *Ley Orgánica de Transparencia y Acceso a la Información Pública* (Segundo Suplemento del Registro Oficial 245, 7 de febrero de 2023). [https://www.asambleanacional.gob.ec/sites/default/files/private/asambleanacional/filesasambleanacionalnameuid-29/Leyes%202013-2017/736-jvelin/ro-245-2do-supl-07-02-2023.pdf](https://www.asambleanacional.gob.ec/sites/default/files/private/asambleanacional/filesasambleanacionalnameuid-29/Leyes%202013-2017/736-jvelin/ro-245-2do-supl-07-02-2023.pdf) Consultado el 8/11/2026.
- Corte Constitucional del Ecuador. (2025). *Sentencia 52-25-IN/25* y auto de aclaración. [https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/eyJjYXJwZXRhIjoicm8iLCJ1dWlkIjoiNjk4MGI1YmMtMjM3MS00YmNlLThhZGUtZDEwZTllMzUxMzI0LnBkZiJ9](https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/eyJjYXJwZXRhIjoicm8iLCJ1dWlkIjoiNjk4MGI1YmMtMjM3MS00YmNlLThhZGUtZDEwZTllMzUxMzI0LnBkZiJ9) Consultado el 8/11/2026.
- Ministerio de Desarrollo Económico y Productivo. (2026). *Directrices Proforma 2027*. [https://www.economicoproductivo.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf](https://www.economicoproductivo.gob.ec/wp-content/uploads/2026/05/directrices_proforma_2027_vf.pdf) Consultado el 6/11/2026 (pp. 69–70) y el 8/11/2026 (p. 4).
- Ministerio de Desarrollo Económico y Productivo. (s. f.). *Catálogo de instituciones y entidades operativas desconcentradas del sector público*. [https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/](https://www.economicoproductivo.gob.ec/catalogo-de-instituciones-y-entidades-operativas-desconcnetradas-del-sector-publico/) Consultado el 15/10/2026 y el 6/11/2026.
- Ministerio de Economía y Finanzas. (s. f.). Portal institucional, que redirige al del Ministerio de Desarrollo Económico y Productivo. [https://www.finanzas.gob.ec/](https://www.finanzas.gob.ec/) Consultado el 8/11/2026. Informe de ejecución presupuestaria 2019 (ejemplo del formato): [https://www.finanzas.gob.ec/wp-content/uploads/downloads/2020/04/Inf_ejec.presupuestaria_2019.pdf](https://www.finanzas.gob.ec/wp-content/uploads/downloads/2020/04/Inf_ejec.presupuestaria_2019.pdf) Consultado el 8/11/2026.
- Ministerio de Telecomunicaciones y de la Sociedad de la Información. (s. f.). *Instituciones que publican en el Portal* (gob.ec). [https://www.gob.ec/instituciones](https://www.gob.ec/instituciones) Consultado el 15/10/2026, el 3/11/2026 y el 6/11/2026 (secciones [M](https://www.gob.ec/instituciones/M) e [I](https://www.gob.ec/instituciones/I)).
- Registro Oficial. (2025–2026). Cuarto Suplemento del Registro Oficial 140 (LOSNCP), [https://www.registroficial.gob.ec/cuarto-suplemento-al-registro-oficial-no-140/](https://www.registroficial.gob.ec/cuarto-suplemento-al-registro-oficial-no-140/); Noveno Suplemento del Registro Oficial 153 (Decreto 193), [https://www.registroficial.gob.ec/noveno-suplemento-no-153/](https://www.registroficial.gob.ec/noveno-suplemento-no-153/); Decreto 295, [https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-215-7/](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-215-7/); Tercer Suplemento del Registro Oficial 337 (Decreto 461), [https://www.registroficial.gob.ec/tercer-suplemento-no-337/](https://www.registroficial.gob.ec/tercer-suplemento-no-337/); Segundo Suplemento del Registro Oficial 245 (LOTAIP), [https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-245/](https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-245/); Tercer Suplemento del Registro Oficial 68 (LOIP), [https://www.registroficial.gob.ec/tercer-suplemento-no-68/](https://www.registroficial.gob.ec/tercer-suplemento-no-68/). Consultados el 8/11/2026.
- Servicio Nacional de Contratación Pública. (2025). *Ley Orgánica del Sistema Nacional de Contratación Pública: texto consolidado*. [https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2025/12/LOSNCP.pdf) Consultado el 8/11/2026.
- Servicio Nacional de Contratación Pública. (2025, 28 de octubre). *Reformas a la LOSNCP: más transparencia y eficiencia en las compras públicas* (boletín 19). [https://portal.compraspublicas.gob.ec/sercop/reformas-a-la-losncp-mas-transparencia-y-eficiencia-en-las-compras-publicas/](https://portal.compraspublicas.gob.ec/sercop/reformas-a-la-losncp-mas-transparencia-y-eficiencia-en-las-compras-publicas/) Consultado el 8/11/2026.
- Servicio Nacional de Contratación Pública. (2026, 5 de noviembre). *Resolución SERCOP-2026-0546-R*. [https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/11/SERCOP-SERCOP-2026-0546-R.pdf](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/11/SERCOP-SERCOP-2026-0546-R.pdf) Consultado el 8/11/2026.
- Servicio Nacional de Contratación Pública. (2026). *Informe preliminar de rendición de cuentas 2025*. [https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/04/Informe_Preliminar_RDC2025_vf.pdf](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/04/Informe_Preliminar_RDC2025_vf.pdf) Consultado el 8/11/2026.
- Servicio Nacional de Contratación Pública. (s. f.). *Datos abiertos de contratación pública: descarga masiva* (OCDS). [https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) Consultado el 3/11/2026 (archivos de 2021 y 2024) y el 8/11/2026.
- Servicio Nacional de Contratación Pública. (s. f.). *Política de publicación de datos abiertos OCDS*. [https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf) Consultado el 3/11/2026.
- Trazabilidad Pública. (2026). Documentos del equipo: [ADR 0001](https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/adr/0001-alcance.md), [entidades.md](https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/sources/entidades.md), [ocds.md](https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/sources/ocds.md), [reconocimiento.md](https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/sources/reconocimiento.md) y [registro de uso de IA](https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/uso-de-ia.md). Repositorio del proyecto, versión del 8/11/2026.

## Criterios de aceptación del hito (autocomprobación)

- [x] El perfil cubre los ocho componentes con datos vigentes y citados.
- [x] El análisis es del sector completo.
- [x] Marco normativo y entes de control verificados al 8/11/2026 (sección 4),
      con distinción del régimen aplicable a 2021–2025.
- [x] Tres tomadores de decisión, cada uno con su decisión principal.
- [x] Las tres preguntas cumplen las cinco condiciones de la guía.
- [x] Una descriptiva y una diagnóstica; la tercera es predictiva.
- [x] Cada fuente tiene enlace y fecha de consulta.
- [x] Todas las marcas **[VERIFICAR]** y **[PENDIENTE]** resueltas.
