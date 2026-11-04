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
de la República, los ministerios y los institutos que dependen de ellos. Quedan
fuera los gobiernos autónomos descentralizados (GAD) y sus empresas, las
empresas públicas y las entidades de otras funciones del Estado.

Tamaño aproximado según el directorio oficial
[gob.ec/instituciones](https://www.gob.ec/instituciones) (consultado el
15/10/2026): una Presidencia, 18 entradas ministeriales y 20 entradas de
institutos (16 institutos públicos sectoriales o de investigación, 3 de
seguridad social y 1 registro de prueba). Las cifras son aproximadas: el
directorio mezcla ministerios vigentes con denominaciones previas a las
fusiones recientes, y la clasificación definitiva de cada entidad sigue en
elaboración ([entidades.md](../sources/entidades.md)).

### 2. Misión y servicios

Estas entidades ejercen la rectoría y ejecutan las políticas del Poder
Ejecutivo y prestan servicios públicos (salud, educación, seguridad,
infraestructura, entre otros). Para ello compran bienes, obras y servicios, y
esa función de **compradora pública** es la que analiza este proyecto.
**[VERIFICAR]** respaldo constitucional (Constitución de la República del
Ecuador, art. 141 sobre la Función Ejecutiva y art. 288 sobre compras
públicas).

### 3. Actores y partes interesadas

- **Entidades contratantes:** Presidencia, ministerios e institutos.
- **Proveedores** de bienes, obras y servicios.
- **SERCOP**, ente rector del Sistema Nacional de Contratación Pública.
- **Ministerio de Economía y Finanzas (MEF)**, que gestiona el presupuesto del
  que sale el gasto de contratación.
- **Organismos de control** y ciudadanía que usa la información abierta.
  **[VERIFICAR]** cuál organismo de control fiscaliza la contratación y su
  base legal.

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

### 6. Tomadores de decisión

| Decisor | Decisión principal |
|---|---|
| **SERCOP** (ente rector) | Qué procedimientos reforzar o controlar y qué alertas priorizar |
| **Áreas de compras de los ministerios** | Con qué procedimiento contratar y cuánto planificar contratar |
| **MEF** | Cuánto presupuesto asignar y cómo programar el gasto en contratación |

Las decisiones son una hipótesis de trabajo derivada de los roles descritos;
**[VERIFICAR]** contra la normativa de cada uno.

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
| Datos abiertos de contratación (OCDS) | SERCOP | JSON, CSV, XLSX por año y mes; API | Descargas actualizadas a diario | 2015 en adelante según la API; abiertos 2025 y enero 2025 | **[PENDIENTE]** registrar los términos; el campo `license` existe en cada paquete | [Descarga masiva](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/) |
| Directorio de instituciones | MINTEL (`gob.ec`) | Páginas web por sección | **[VERIFICAR]** | Vigente 2026 | **[PENDIENTE]** | [gob.ec/instituciones](https://www.gob.ec/instituciones) |

Ejecución presupuestaria del MEF: se encontraron informes en PDF
([ejemplo 2019](https://www.finanzas.gob.ec/wp-content/uploads/downloads/2020/04/Inf_ejec.presupuestaria_2019.pdf)),
pero no se ha confirmado un conjunto descargable por entidad. No se usa como
fuente hasta abrir un archivo real.

**Prueba del archivo realizada:** se descargó y abrió el ZIP anual 2025
(190.619 procesos distintos) y el de enero 2025, con sus campos de monto y de
comprador ([reconocimiento.md](../sources/reconocimiento.md)).
**[PENDIENTE]** abrir al menos un archivo de 2021 a 2024 antes de entregar,
para confirmar que los campos usados existen en esos años.

## Parte 2 · Matriz de preguntas de negocio

Ventana de análisis: **2021–2025, años calendario completos** (5 periodos). La
fecha que asigna un proceso a un año se fija en el Hito 2 tras medir qué fecha
está más completa en los datos.

| Pregunta de negocio | Decisor y decisión | Indicador (fórmula) | Dimensiones | Fuente candidata |
|---|---|---|---|---|
| **P1 (descriptiva).** ¿Cómo evolucionó el monto adjudicado por método de contratación entre 2021 y 2025, por año y tipo de entidad (Presidencia, ministerio, instituto)? | Áreas de compras de los ministerios y SERCOP: qué procedimientos priorizar al planificar | Monto adjudicado (USD) = suma de `awards[].value.amount` de los procesos del sector, agrupada por año, método y tipo de entidad | Año, método de contratación, tipo de entidad, entidad | SERCOP, descarga masiva JSON anual; clasificación de entidades con `gob.ec` |
| **P2 (diagnóstica).** ¿Qué métodos de contratación se asocian a mayor desviación entre el valor adjudicado y el valor estimado de la licitación, según el tipo de entidad? | SERCOP y organismos de control: dónde reforzar los controles | Desviación % = (valor adjudicado − valor estimado de la licitación) ÷ valor estimado × 100, por proceso con ambos valores; se resume por método y tipo de entidad | Método, tipo de entidad, año | SERCOP, descarga masiva JSON anual (`tender.value.amount` y `awards[].value.amount`) |
| **P3 (predictiva).** ¿Cuál es el monto adjudicado esperado por mes en el primer semestre de 2026 para cada tipo de entidad? | MEF y entidades: programar el presupuesto de contratación | Monto mensual proyectado (serie de tiempo), validado con una métrica de error sobre un periodo retenido de 2025 | Mes, tipo de entidad | SERCOP, serie mensual 2021–2025 construida desde la descarga masiva |

**Verificación de datos en la muestra de 2025:** las adjudicaciones con importe
numérico fueron 183.887 de 183.891 (anual), y `tender.value.amount` estuvo
presente en 2.050 de 2.186 procesos de enero de 2025. Son conteos nacionales
sin filtrar por planta central. Los importes adjudicado, estimado y
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
- [ ] Cada fuente tiene enlace y fecha de consulta (faltan licencia y años
      2021–2024).
- [ ] Todas las marcas **[VERIFICAR]** y **[PENDIENTE]** resueltas.
