# E0 · Contextualización de negocio y definición del caso de estudio

**Título:** Contextualización de negocio y definición del caso de estudio ·
**Borrador original:** Jorge Torres, 14 de octubre de 2026 · **Integración
para la entrega (#14):** 17 de octubre de 2026

> **Histórico.** E0 ya no es un entregable: el profesor reemplazó las fases
> anteriores por seis hitos (ver [PLAN.md](../PLAN.md)). Este texto se conserva
> como insumo para el [Hito 1](hito1.md). Su Word y su carpeta de entrega se
> eliminaron; siguen en el historial de Git.

## Nombre y giro de la empresa

La unidad de estudio es la planta central del Estado ecuatoriano: la
Presidencia de la República, los ministerios y los institutos que dependen de
ellos. Se la analiza en su función de compradora pública, de modo que el giro
relevante es la contratación pública: los procesos de compra que estas
entidades realizan y que el Servicio Nacional de Contratación Pública
(SERCOP) difunde como datos abiertos. El caso corresponde al sector Gobierno
y Ministerio y cubre todas las entidades que cumplen esa definición, no una
muestra. Quedan excluidos los gobiernos autónomos descentralizados (GAD), sus
empresas y cualquier entidad ajena a la planta central. Los casos dudosos,
como los institutos con régimen propio, se resolverán con criterios de
inclusión documentados. El trabajo es académico e independiente de SERCOP y de
las entidades estudiadas. La delimitación vigente está en el
[ADR 0001](../adr/0001-alcance.md).

## Área de análisis a desarrollar

El área de análisis es la contratación pública, con el proceso de contratación
como unidad de observación. Cada proceso se examina según su entidad
compradora, su método de contratación, sus fechas y sus importes
presupuestado, estimado, adjudicado y contractual. La fuente es el portal de
datos abiertos de SERCOP (s. f.-a), que según su nota metodológica integra el
Sistema Oficial de Contratación Pública y los módulos de compras corporativas
de salud y de alimentación escolar, los transforma al Estándar de Datos de
Contrataciones Abiertas (OCDS, por sus siglas en inglés) 1.1 y actualiza a
diario las descargas masivas. OCDS organiza cada proceso en planificación,
licitación, adjudicación y contrato, y distingue la entidad compradora
(*buyer*) de la unidad que gestiona el proceso (*procuringEntity*; Open
Contracting Partnership, s. f.). El análisis se hará sobre una captura fija
(*snapshot*) de varios años. El periodo se decidirá en la fase de
requerimientos (issue #15); el candidato inicial es 2021–2025, cinco años
calendario completos. El
[reconocimiento de la fuente](../sources/reconocimiento.md#campos-evidencia-y-límites-de-lo-observado)
distingue la respuesta resumida de búsqueda de las descargas JSON anidadas y
no presume que sus propiedades sean equivalentes.

## Problema o necesidad del negocio

Los datos de contratación son públicos, pero no permiten analizar la planta
central sin un tratamiento previo. El reconocimiento de las descargas de 2025
(SERCOP, s. f.-b) mostró cuatro brechas. La primera es de alcance: el portal
reúne compradores de todo el país, por ejemplo una junta parroquial, y no
indica cuáles integran la planta central. Los directorios oficiales abiertos
revisados tampoco registran de qué ministerio depende cada instituto, y varias
carteras se fusionaron recientemente, de modo que la pertenencia cambia en el
tiempo. Delimitarla exige una clasificación de entidades basada en una fuente
oficial y en criterios de inclusión que aún no están aprobados
([entidades.md](../sources/entidades.md)). La segunda es de identificación: en
la descarga de enero de 2025 (2.186 procesos) hubo 372 identificadores de
comprador distintos, solo 185 con la forma simple de RUC más 13 dígitos, y
nombres asociados a más de un identificador, por lo que el nombre no sirve
como llave de cruce ([ADR 0001](../adr/0001-alcance.md), decisión 7).

La tercera es de granularidad: la descarga anual contiene 190.619 procesos
distintos, de los cuales 300 tienen varias adjudicaciones y 270 varios
contratos, por lo que contar objetos en lugar de procesos genera duplicados.
La cuarta es de comparabilidad: los importes presupuestado, estimado,
adjudicado y contractual son magnitudes distintas que no se sustituyen entre
sí, y su cobertura es desigual, pues 27.666 de 180.465 contratos (15,33 %)
registran un importe numérico, frente a 183.887 de 183.891 adjudicaciones. Sin
resolver estas brechas, una consulta directa cuenta dos veces un proceso,
mezcla importes de distinto significado o incluye compradores ajenos al caso.
Los conteos son nacionales y provienen de descargas de reconocimiento;
todavía no corresponden a la planta central. Las cifras y su método están en
la [inspección del ZIP anual](../sources/reconocimiento.md#inspección-del-zip-anual-json).

La necesidad es contar con una base analítica de alcance institucional
explícito y reglas verificables para deduplicar procesos y tratar los datos
ausentes, que permita comparar procesos, métodos de contratación e importes
sin repetir en cada consulta la delimitación institucional ni la depuración,
con resultados reproducibles. Se propone un Data Warehouse dimensional,
construido con la metodología HEFESTO (Bernabeu, 2009) y el modelado de
Kimball y Ross (2013), que aún no ha sido implementado.

## Preguntas clave que busca responder

1. ¿Cuántos procesos de contratación corresponden a cada entidad compradora
   incluida y cómo se distribuyen entre la Presidencia, los ministerios y los
   institutos dependientes?
2. ¿Cómo se distribuyen los procesos de cada entidad según el método de
   contratación registrado?
3. ¿Cómo evoluciona el número de procesos entre periodos comparables dentro de
   la captura seleccionada?
4. ¿Cómo se distribuye el valor adjudicado entre entidades y métodos de
   contratación?
5. ¿En qué procesos difiere el valor adjudicado del valor estimado de la
   licitación, cuando ambos son comparables?
6. ¿Con qué frecuencia faltan datos utilizables (método, fecha o, cuando
   existe adjudicación, importe) en los procesos de las entidades incluidas?

Responderlas exige validar la clasificación de entidades y el uso del
identificador del comprador, fijar el periodo y la fecha de análisis,
comprobar la cobertura del método de contratación y definir el tratamiento de
adjudicaciones múltiples, monedas y estados. Los indicadores y sus fórmulas se
definirán en la fase de requerimientos. Las rutas de importes observadas se
documentan en la
[inspección mensual](../sources/reconocimiento.md#inspección-local-de-la-descarga-mensual-json).

## Referencias

Bernabeu, R. D. (2009). *Data warehousing: Investigación y sistematización de
conceptos. HEFESTO: Metodología propia para la construcción de un data
warehouse* (versión 1.0).
<https://www.dataprix.com/files/DWH_Metodologia_HEFESTO-V1.0.pdf>

Kimball, R., y Ross, M. (2013). *The data warehouse toolkit: The definitive
guide to dimensional modeling* (3.ª ed.). Wiley.

Open Contracting Partnership. (s. f.). *Estándar de Datos de Contrataciones
Abiertas* (versión 1.1.5). <https://standard.open-contracting.org/latest/es/>

Servicio Nacional de Contratación Pública. (s. f.-a). *Notas metodológicas*
[Portal de datos abiertos]. Recuperado el 11 de octubre de 2026, de
<https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/notas-metodologicas>

Servicio Nacional de Contratación Pública. (s. f.-b). *Descarga masiva de
datos abiertos: Año 2025 (descargas anual y de enero)* [Conjunto de datos].
Recuperado el 11 de octubre de 2026, de
<https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/>
