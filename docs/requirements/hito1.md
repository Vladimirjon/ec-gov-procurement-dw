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

- **Ley Orgánica del Sistema Nacional de Contratación Pública (LOSNCP).** La
  Asamblea Nacional aprobó reformas el 7/10/2025 y el **Reglamento General**
  se publicó en el Registro Oficial 193 el 28/10/2025
  ([SERCOP, reformas a la LOSNCP](https://portal.compraspublicas.gob.ec/sercop/reformas-a-la-losncp-mas-transparencia-y-eficiencia-en-las-compras-publicas/)).
  Las reformas buscan simplificar procedimientos, reforzar el control, crear una
  unidad de antilavado y anticorrupción en SERCOP y hacer obligatoria la
  actualización anual del Registro Único de Proveedores.
- **Ley Orgánica de Integridad Pública** (junio de 2025), parte de cuyas
  disposiciones recoge la reforma anterior. **[VERIFICAR]** fecha y texto en el
  Registro Oficial.
- **Transparencia y acceso a la información (LOTAIP).** **[VERIFICAR]** norma
  vigente y su alcance sobre datos abiertos.
- **Política de publicación OCDS de SERCOP**
  ([PDF oficial](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/documentos/politica-publicacion-SERCOP-OCDS.pdf)),
  que rige cómo se publican los datos de contratación.

**Implicación para los datos:** el periodo 2021–2025 cruza la reforma de
octubre de 2025. Los nombres o reglas de los procedimientos pueden cambiar
dentro de 2025; se comprobará al perfilar los datos (Hito 2).

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

- Monto contratado o adjudicado por procedimiento.
- Concentración de la contratación por proveedor.
- Ejecución presupuestaria (MEF).
- Ahorro respecto del presupuesto referencial, que SERCOP reporta en su
  rendición de cuentas. **[VERIFICAR]** abrir el
  [informe preliminar 2025](https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2026/04/Informe_Preliminar_RDC2025_vf.pdf)
  (no se pudo abrir en esta consulta) y citar cifras con su página.

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
| **P1 (descriptiva).** ¿Cómo evolucionó el monto adjudicado por método de contratación entre 2021 y 2025, por año y tipo de entidad (Presidencia, ministerio, instituto)? | Entidades contratantes (órgano requirente) y SERCOP: qué procedimientos priorizar al planificar | Monto adjudicado (USD) = suma de `awards[].value.amount` de los procesos del sector, agrupada por año, método y tipo de entidad | Año, método de contratación, tipo de entidad, entidad | SERCOP, descarga masiva JSON anual; clasificación de entidades con `gob.ec` |
| **P2 (diagnóstica).** ¿Qué métodos de contratación se asocian a mayor desviación entre el valor adjudicado y el valor estimado de la licitación, según el tipo de entidad? | SERCOP: dónde reforzar los controles | Desviación % = (valor adjudicado − valor estimado de la licitación) ÷ valor estimado × 100, por proceso con ambos valores; se resume por método y tipo de entidad | Método, tipo de entidad, año | SERCOP, descarga masiva JSON anual (`tender.value.amount` y `awards[].value.amount`) |
| **P3 (predictiva).** ¿Cuál es el monto adjudicado esperado por mes en el primer semestre de 2026 para cada tipo de entidad? | MEF y entidades contratantes: programar el presupuesto de contratación | Monto mensual proyectado (serie de tiempo), validado con una métrica de error sobre un periodo retenido de 2025 | Mes, tipo de entidad | SERCOP, serie mensual 2021–2025 construida desde la descarga masiva |

**Verificación de datos en la muestra de 2025:** las adjudicaciones con importe
numérico fueron 183.887 de 183.891 (anual), y `tender.value.amount` estuvo
presente en 2.050 de 2.186 procesos de enero de 2025. Son conteos nacionales
sin filtrar por planta central. En 2021 y 2024 el importe estimado de la
licitación estuvo presente en el 88,5 % y el 88,7 % de las licitaciones, y el
importe adjudicado en prácticamente todas las adjudicaciones, igual que en
2025. Los importes adjudicado, estimado y
contractual son magnitudes distintas y no se sustituyen entre sí.

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

## Criterios de aceptación del hito (autocomprobación)

- [ ] El perfil cubre los ocho componentes con datos vigentes y citados.
- [x] El análisis es del sector completo.
- [ ] Marco normativo vigente verificado (faltan LOTAIP, Ley de Integridad
      Pública y base constitucional).
- [x] Tres tomadores de decisión, cada uno con su decisión principal.
- [x] Las tres preguntas cumplen las cinco condiciones de la guía.
- [x] Una descriptiva y una diagnóstica; la tercera es predictiva.
- [x] Cada fuente tiene enlace y fecha de consulta.
- [ ] Todas las marcas **[VERIFICAR]** y **[PENDIENTE]** resueltas.
