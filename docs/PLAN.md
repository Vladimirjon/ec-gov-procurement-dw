# Plan de trabajo y rotación

- **Estado:** vigente desde su fusión en `main`. Cambios solo por PR aprobado
  por el líder.
- **Fecha:** 2026-10-10
- **Cierre del proyecto:** 2027-01-22

Este plan responde tres preguntas: **qué** hay que entregar, **quién** hace
qué en cada fase y **cómo** rota el trabajo para que todos pasen por todas
las partes del Data Warehouse.

## 1. Cómo leer este plan

- El proyecto avanza por las **fases de HEFESTO** (sección 3). Cada fase
  termina con uno o más **entregables calificados**.
- El trabajo técnico se divide en **carriles**: las etapas del ciclo de vida
  de la ingeniería de datos (sección 2).
- En cada fase, **cada persona tiene una tarea principal en un carril**
  (sección 5). En la fase siguiente cambia de carril (sección 6).
- Cada tarea se convierte en un **issue** asignado, dentro del **milestone**
  de su fase. El trabajo entra a `main` por PR, según
  [CONTRIBUTING.md](../CONTRIBUTING.md).

## 2. Carriles

| Carril | Qué cubre | Etapa del ciclo de vida | Dónde vive en el repo |
|---|---|---|---|
| **Ingesta y fuente** | Conocer la fuente SERCOP (OCDS), extraer los datos, tomar la foto inmutable con su manifiesto y cargarla a staging. Incluye la infraestructura local (PostgreSQL, entorno de Python). | Generación e ingesta | `src/.../extract`, `src/.../snapshot`, `docs/sources/` |
| **Modelado y almacenamiento** | Traducir las preguntas de negocio al modelo dimensional: grano, hechos, dimensiones, SCD. Luego, el diseño físico: tablas, claves, índices y rendimiento. | Almacenamiento y modelado | `docs/design/`, `warehouse/ddl/` |
| **Transformación** | Llevar los datos de staging al DW: limpieza, normalización, campos derivados, claves sustitutas, SCD, carga incremental. Incluye la tabla de clasificación de entidades (datos de referencia). | Transformación | `src/.../load`, `warehouse/dbt/`, `notebooks/` |
| **Calidad y operación** | Que los datos sean confiables y el proceso sea auditable: reglas de calidad, filas rechazadas, bitácora de cargas, pruebas automáticas, reconciliación con la fuente y CI. | Gestión de datos y DataOps (transversales) | `src/.../quality`, `tests/`, `docs/validation/` |
| **Negocio y servicio** | Que el DW responda preguntas reales: requerimientos, usuarios, KPIs, vistas para tableros, Power BI y la documentación que se entrega. | Servir datos | `docs/requirements/`, `docs/dashboards/`, `reports/powerbi/` |

**El carril de Ingesta y fuente es fijo:** lo lleva el líder en todas las
fases, porque es la ruta crítica del proyecto (sin foto no hay DW). Los
otros cuatro carriles rotan entre el resto del equipo.

## 3. Calendario y entregables

Cada entregable lleva el encabezado **Título, Equipo #, Nombres, Fecha**. El
nombre de archivo usa los apellidos del equipo separados por puntos (ver
[deliverables/README.md](../deliverables/README.md)).

| Fase | Ventana | Entregable | Formato | Fecha interna |
|---|---|---|---|---|
| 0. Preparación | 10 – 19 oct | E0 · Contextualización de negocio y definición del caso de estudio | PDF, 1–2 páginas | 17 oct |
| 1. Requerimientos | 20 oct – 2 nov | F1-E1 · Descripción del caso y requerimientos del DW | PDF, 1–3 páginas | 30 oct |
| | | F1-E2 · Guía: Diseño Inicial del Modelo Dimensional | PDF (plantilla del curso) | 30 oct |
| 2. Diseño conceptual y lógico | 3 – 23 nov | F2-E1 · Diseño Conceptual – Modelo en Estrella | PDF, 1–3 páginas | 20 nov |
| | | F2-E2 · Diseño Lógico – Diccionario de Datos | Word, 1–3 páginas (plantilla del curso) | 20 nov |
| 3. Diseño físico y ETL | 24 nov – 14 dic | F3-E1 · Diseño Físico de Tablas | `.sql` + PDF con imagen de la BD | 11 dic |
| | | F3-E2 · Proceso ETL | `.ipynb` + su exportación a PDF | 11 dic |
| | | F3-E3 · Documentación del Flujo ETL | Diagrama + 1 página, PDF | 11 dic |
| 4. Carga y pruebas | 15 dic – 8 ene | Carga de Datos y Pruebas | `.zip`: scripts, capturas, bitácora, resumen de validación | 5 ene |
| 5. Visualización y cierre | 9 – 22 ene | Dashboard conectado al DW | `.zip`: 3 reportes, conexión validada, documentación, video | 19 ene |
| | | Presentación del proyecto DW | PDF, exposición de 15 minutos | 19 ene |
| | | Proyecto DW (documento final) | PDF, compilación completa y reproducible | 19 ene |

- La **fecha interna** es 3 días antes del cierre de cada ventana: deja tiempo
  para la revisión del líder y para integrar.
- Si una fecha del curso es anterior a la ventana, manda la fecha del curso:
  se ajusta este plan por PR.
- **Fase 4 cruza las fiestas.** Las cargas y pruebas deben quedar hechas antes
  del **22 de diciembre**; del 2 al 5 de enero solo se documenta y empaqueta.

### Cómo se producen los entregables

1. El contenido se escribe en Markdown dentro del repo (`docs/...`) y entra
   por PR, como el código. Así todo queda revisado y versionado.
2. Quien integra la entrega arma el documento final con la plantilla y el
   encabezado del curso, y lo exporta al formato pedido.
3. El archivo final se guarda en `deliverables/<fase>/` con su nombre oficial.

## 4. Equipo

| Persona | GitHub | Responsabilidad fija |
|---|---|---|
| Vladimirjon (líder) | @Vladimirjon | Carril de Ingesta y fuente; arquitectura; revisión de todos los PR; integración de cada entregable |
| Jorge Torres | @Almejandro04 | Rota de carril cada fase |
| Harry Guajan | @Harry-GNS | Rota de carril cada fase |
| Ismael Freire | @BrandonFreire | Rota de carril cada fase |
| Francis Bravo | @Francis1918 | Rota de carril cada fase |

## 5. Tareas por fase

Formato de cada tarea: **carril · título**, qué hay que hacer y cuándo se
considera terminada. Las dependencias entre tareas van al final de cada fase.

### Fase 0 · Preparación (10 – 19 oct)

Objetivo: entregar E0 y dejar listas las bases para los requerimientos.
Esta fase no forma parte de la rotación.

**Vladimirjon · Reconocimiento de la fuente**
- Investigar el portal de datos abiertos de contratación pública de SERCOP:
  qué formas de descarga existen (masiva por año o API), qué campos traen los
  registros reales, cuánto pesa un año y qué límites tiene la API.
- Documentarlo en `docs/sources/reconocimiento.md`, separando lo **observado**
  de lo **supuesto**.
- Integrar y entregar E0.
- *Terminado cuando:* el documento responde las cuatro preguntas con
  evidencia (fragmentos mínimos, nunca datasets completos) y E0 está entregado.

**Jorge · Borrador de la contextualización (E0)**
- Redactar los cuatro puntos que pide E0:
  - **Nombre y giro:** la planta central del Estado ecuatoriano como comprador
    público.
  - **Área de análisis:** contratación pública.
  - **Problema o necesidad:** por qué hace falta un DW.
  - **Preguntas clave:** entre 5 y 8.
- Partir de las secciones 1 y 2 de [PROPUESTA.md](PROPUESTA.md).
- *Terminado cuando:* cabe en 1–2 páginas, cubre los cuatro puntos y lleva el
  encabezado del curso.

**Harry · Estudio del estándar OCDS**
- Leer la documentación oficial del Open Contracting Data Standard: qué es un
  *release*, qué es un *ocid* y qué contienen las secciones de planificación,
  licitación, adjudicación y contrato.
- Resumirlo en `docs/sources/ocds.md` con enlaces a la documentación oficial.
- *Terminado cuando:* el resumen distingue lo que define el estándar de lo
  que el líder observa en la fuente real, sin mezclarlos.

**Ismael · Fuente oficial de entidades**
- Buscar una fuente oficial que liste la Presidencia, los ministerios y los
  institutos adscritos a cada ministerio.
- Proponerla en `docs/sources/entidades.md` con enlace, fecha de consulta y
  qué tan completa es.
- *Terminado cuando:* hay al menos una fuente oficial propuesta y comparada
  con una alternativa.

**Francis · Plantilla de entregables y glosario**
- Crear el documento base para todas las entregas: encabezado del curso,
  estilos y convención de nombre de archivo. Va en `deliverables/plantilla/`.
- Crear `docs/glosario.md` con los términos del proyecto: proceso de
  contratación, entidad contratante, proveedor, OCDS, ocid, hecho, dimensión,
  grano, SCD, staging, entre otros. Cada uno con su fuente.
- *Terminado cuando:* la plantilla sirve tal cual para E0 y el glosario tiene
  al menos 20 términos con fuente.

Dependencias: Jorge usa los hallazgos del líder para el problema y las
preguntas; el líder integra E0 a partir del 15 de octubre.

#### Ruta del líder en la fase 0

Esta ruta distingue el reconocimiento técnico de la entrega calificada. El
detalle de evidencias y sus limitaciones vive en
[reconocimiento.md](sources/reconocimiento.md); los criterios de cada tarea
se revisan en su issue antes de darla por terminada.

| Orden | Tarea | Qué debe completar el líder |
|---|---|---|
| 1 | [#9 · Reconocer la fuente](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9) | Los cinco criterios tienen evidencia. Revisar e integrar el PR de cierre, limitado al comportamiento externo observado de la cuota; la política interna y el ámbito del contador no se presentan como confirmados por SERCOP. |
| 2 | Coordinar las entradas para E0 | #10 (contextualización) y #11/PR #21 (resumen OCDS) ya están integrados. Revisar la propuesta de entidades de #12 y la plantilla/glosario de #13 cuando estén disponibles, y usar los hallazgos comprobados de #9 para orientar las preguntas de negocio. |
| 3 | [#14 · Integrar y entregar E0](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/14) | Armar el PDF de 1–2 páginas con los cuatro puntos, título y encabezado del curso; comprobar nombre, guardarlo en `deliverables/fase0/` por PR y subirlo al curso. Fecha interna 17 oct. |
| Transversal | Revisión y decisiones del equipo | Revisar los PR según el plazo de 48 horas. Evaluar la propuesta de entidades de Ismael en [#12](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/12). Conservar las decisiones de arquitectura pendientes hasta su aprobación explícita. |

**Estado consultado el 15/10/2026:** #10 y #11 están cerrados; sus cambios se
integraron en `main` mediante los PR #23 y #21, respectivamente. #9 y #14
siguen abiertos. El cierre de #9 está preparado localmente en la rama
`docs/09-completar-limite-api-sercop` y aún no tiene PR. #12 y #13 siguen
abiertos. No hay todavía un PDF E0 final ni evidencia de su subida al curso.
Esto no sustituye la consulta del trabajo que los compañeros tengan en sus
ramas o PR.

**Frontera entre fases:** decidir el periodo definitivo de la foto corresponde
al líder en [#15](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/15),
fase 1. La indicación docente es analizar cinco años o comparar por gobiernos;
como SERCOP no expone un campo de gobierno, #15 evaluará el periodo por fechas,
con `2021–2025` como candidato inicial de cinco años calendario completos.
Tomar y registrar la foto formal con manifiesto corresponde al inicio de la
fase 2. El reconocimiento actual no exige implementar staging, DW, ETL,
clasificación completa de entidades ni tableros.

### Fase 1 · Requerimientos (20 oct – 2 nov)

Objetivo: F1-E1 (documento de requerimientos de 9 secciones) y F1-E2 (Guía
de Diseño Inicial). Las secciones se escriben en `docs/requirements/`.

**Vladimirjon · Ingesta y fuente: fuentes de datos y periodo de la foto**
- Escribir la sección 6, "Fuentes de datos identificadas".
- Extraer una muestra pequeña para comprobar que la extracción funciona.
- Recomendar el periodo de la foto según el volumen medido.
- *Terminado cuando:* la sección 6 está escrita, la muestra se puede repetir
  con un comando y el periodo está decidido y registrado en el ADR 0002.

**Jorge · Negocio y servicio: objetivos, procesos, KPIs y prioridades**
- Escribir las secciones del documento de requerimientos:
  - 1, objetivos del negocio;
  - 3, procesos relevantes;
  - 5, KPIs preliminares, cada uno con su fórmula en palabras;
  - 8, priorización (imprescindible, importante, deseable).
- *Terminado cuando:* cada KPI responde al menos una pregunta clave de E0 y
  se puede calcular con datos que la fuente tiene de verdad.

**Harry · Modelado: Guía de Diseño Inicial (F1-E2)**
- Completar la plantilla oficial del curso:
  - proceso de negocio y grano;
  - hechos (medidas);
  - 4–5 dimensiones con sus atributos;
  - qué dimensión cambia en el tiempo (SCD);
  - fuentes y sus limitaciones;
  - tres preguntas de negocio que el modelo debe responder.
- Respetar el ADR 0004: 1 hecho + 4–5 dimensiones.
- *Terminado cuando:* cada sección de la plantilla está completa y es
  coherente con los KPIs de Jorge.

**Ismael · Calidad: problemas de datos, requerimientos no funcionales y restricciones**
- Escribir las secciones del documento de requerimientos:
  - 2, problemas actuales en el manejo de datos, solo los observados en la
    fuente;
  - 7, requerimientos funcionales y no funcionales: calidad,
    reproducibilidad, rendimiento y seguridad;
  - 9, restricciones de tiempo, sistemas y seguridad.
- *Terminado cuando:* cada problema citado tiene evidencia en
  `docs/sources/` y cada requerimiento es verificable.

**Francis · Transformación: usuarios clave y lista de entidades v1**
- Escribir la sección 4, "Usuarios clave": 3 o 4 perfiles simulados, cada uno
  con rol, necesidad, preguntas que se hace y frecuencia de uso.
- Con la fuente oficial que encontró Ismael, armar la primera versión de la
  tabla de clasificación: Presidencia y ministerios con nombre oficial y
  siglas, en `warehouse/dbt/seeds/entity_classification.csv`.
- *Terminado cuando:* los perfiles cubren al menos un usuario estratégico y
  uno operativo, y la lista tiene a todos los ministerios vigentes con su
  fuente.

Dependencias: Harry y Jorge acuerdan juntos el grano y los KPIs en la
primera semana. El líder integra F1-E1 y F1-E2 desde el 28 de octubre.

### Fase 2 · Diseño conceptual y lógico (3 – 23 nov)

Objetivo: F2-E1 (modelo en estrella) y F2-E2 (diccionario de datos). Antes de
pasar a la fase 3, el diseño se valida con los usuarios clave simulados.

**Vladimirjon · Ingesta y fuente: foto completa y prueba de conexión**
- Tomar la foto del periodo elegido con su manifiesto de checksums, usando un
  script reproducible en `src/.../extract` y `src/.../snapshot`.
- Probar la conexión de Power BI con PostgreSQL usando una tabla de prueba.
- *Terminado cuando:* la foto se puede verificar con su manifiesto y Power BI
  lee la tabla de prueba.

**Jorge · Modelado: modelo conceptual en estrella (F2-E1)**
- Diseñar el modelo:
  - la tabla de hechos con su grano, medidas y claves;
  - de 4 a 5 dimensiones con sus atributos y jerarquías (Presidencia >
    ministerio > instituto; año > trimestre > mes > día);
  - las relaciones entre tablas;
  - la estrategia SCD de cada dimensión.
- Dibujarlo en draw.io o dbdiagram.io.
- Hacer la validación con los perfiles de usuario de la fase 1.
- *Terminado cuando:* el diagrama cabe en el PDF, el grano se enuncia en una
  sola frase y cada KPI de la fase 1 se puede calcular con el modelo.

**Harry · Transformación: perfilado y mapeo fuente → destino**
- Perfilar la foto: nulos, valores distintos, rangos y formatos de cada campo
  que se va a usar, en un notebook dentro de `notebooks/`.
- Escribir el mapeo en `docs/design/mapeo.md`: para cada columna del DW, el
  campo de origen, la regla de transformación y el tratamiento de nulos.
- Definir cómo se detecta un cambio en `dim_entity` (SCD 2).
- *Terminado cuando:* ninguna columna del modelo queda sin origen observado o
  regla documentada.

**Ismael · Negocio y servicio: diccionario de datos (F2-E2) y fórmulas de KPIs**
- Llenar la plantilla oficial del diccionario para cada tabla del modelo de
  Jorge: campo, tipo, PK, FK, clave sustituta y descripción, en snake_case.
- Escribir `docs/design/kpis.md`: para cada KPI, la tabla, los campos y la
  agregación con que se calcula.
- *Terminado cuando:* el diccionario coincide exactamente con el diagrama y
  cada KPI tiene su fórmula sobre el modelo.

**Francis · Calidad: catálogo de reglas de calidad v1**
- A partir del perfilado de Harry y de la sección 2 de requerimientos,
  escribir `docs/design/reglas-calidad.md` con una tabla de reglas.
- Cada regla lleva: identificador, descripción, dimensión de calidad
  (completitud, validez, unicidad o consistencia), campo, severidad y un
  ejemplo de dato que la incumple.
- *Terminado cuando:* hay al menos una regla por cada campo usado en los KPIs.

Dependencias: el modelo de Jorge se cierra a mitad de fase (13 nov); después
Ismael completa el diccionario. Harry necesita la foto del líder en la
primera semana.

### Fase 3 · Diseño físico y ETL (24 nov – 14 dic)

Objetivo: F3-E1 (DDL), F3-E2 (ETL en notebook) y F3-E3 (diagrama del flujo).

**Vladimirjon · Ingesta y fuente: infraestructura y carga a staging**
- Montar PostgreSQL local con Docker Compose y declarar el entorno de Python
  reproducible.
- Cargar la foto al esquema `stg` de forma idempotente, con su `batch_id`.
- *Terminado cuando:* cualquiera del equipo levanta la base y carga staging
  con los comandos del README.

**Jorge · Transformación: ETL de staging al DW (F3-E2)**
- Implementar la transformación:
  - normalizar nombres, fechas, decimales y mayúsculas;
  - derivar campos, por ejemplo la diferencia entre monto y presupuesto;
  - generar las claves sustitutas;
  - aplicar SCD 2 en `dim_entity`;
  - cargar primero las dimensiones y después los hechos.
- El notebook entregable en `notebooks/` ejecuta el proceso de principio a
  fin y muestra sus resultados.
- *Terminado cuando:* el notebook corre de cero sobre una base limpia y las
  tablas del DW quedan llenas.

**Harry · Calidad: control de errores, pruebas y CI**
- Crear el esquema `audit` con dos tablas:
  - `load_log`: proceso, inicio, fin, tabla destino, registros correctos,
    errores, duración y estado;
  - `load_error`: tabla, campo, descripción, fecha, proceso y acción tomada.
- Enviar las filas inválidas a `load_error`.
- Escribir pruebas unitarias de las transformaciones.
- Activar el CI en GitHub Actions: ya hay código que verificar.
- *Terminado cuando:* una fila inválida a propósito termina en `load_error`,
  las pruebas pasan y el CI corre en cada PR.

**Ismael · Modelado: diseño físico de tablas (F3-E1)**
- Escribir en `warehouse/ddl/` los `CREATE TABLE` de la base, staging,
  dimensiones, hechos y auditoría:
  - claves primarias y foráneas;
  - índices sobre las claves foráneas y la fecha;
  - `DECIMAL` para montos;
  - nombres consistentes con el diccionario.
- Generar la imagen de la base para el PDF.
- *Terminado cuando:* el script corre sin errores sobre el PostgreSQL del
  proyecto y coincide con el diccionario.

**Francis · Negocio y servicio: diagrama del flujo ETL (F3-E3)**
- Dibujar en draw.io el flujo Fuente → Foto → Staging → Transformaciones → DW
  (más `audit`), indicando métodos (batch, SQL, función Python), campos clave y
  control de errores.
- Escribir la explicación de una página.
- *Terminado cuando:* cada caja del diagrama corresponde a un paso real del
  código, y así lo confirman el líder, Jorge y Harry.

Dependencias: Ismael entrega el DDL en la primera semana, porque Jorge y
Harry cargan sobre esas tablas. Francis empieza en la segunda semana, con el
flujo ya construido.

### Fase 4 · Carga y pruebas (15 dic – 8 ene)

Objetivo: el DW cargado y validado, con la carpeta de entrega completa.
**Cargas y pruebas terminadas antes del 22 de diciembre.**

**Vladimirjon · Ingesta y fuente: carga batch e incremental**
- Ejecutar la carga completa inicial.
- Ejecutar la carga incremental por particiones mensuales, con `batch_id`,
  fecha de corte y detección de cambios por `ocid` más un hash del contenido.
- *Terminado cuando:* las dos cargas quedan registradas en `audit.load_log`
  sin duplicar datos.

**Jorge · Calidad: pruebas de consistencia y reconciliación**
- Validar la integridad referencial, las unidades y formatos, y los
  duplicados.
- Reconciliar conteos y sumas de monto entre la foto, staging y el DW.
- Registrar los resultados de las reglas de calidad.
- *Terminado cuando:* cada prueba tiene resultado documentado y las
  diferencias de la reconciliación están explicadas.

**Harry · Negocio y servicio: validación de KPIs y documento resumen**
- Escribir la consulta SQL de cada KPI y comparar el resultado con la fuente.
- Llenar la bitácora de validación: KPI, valor calculado, valor esperado,
  estado y observaciones.
- Redactar el documento resumen de validación.
- *Terminado cuando:* todos los KPIs de la fase 1 tienen fila en la bitácora.

**Ismael · Transformación: idempotencia y orden de carga**
- Volver a ejecutar las cargas y demostrar que no duplican datos.
- Demostrar con `load_log` que las dimensiones se cargan antes que los hechos.
- Reunir las capturas como evidencia.
- *Terminado cuando:* hay evidencia antes y después de una re-ejecución, con
  conteos idénticos.

**Francis · Modelado: tiempos de carga y armado de la entrega**
- Ejecutar el script de carga con volúmenes crecientes (lo prepara el líder),
  registrar los tiempos y graficarlos.
- Organizar las capturas y armar la carpeta `.zip` con el nombre oficial.
- *Terminado cuando:* la tabla de tiempos tiene al menos tres volúmenes y la
  carpeta contiene los cuatro elementos que pide el curso.

### Fase 5 · Visualización y cierre (9 – 22 ene)

Objetivo: tres tableros conectados al DW, la presentación y el documento final.

**Vladimirjon · Ingesta y fuente: conexión validada e integración final**
- Conectar Power BI al DW con un usuario de solo lectura sobre el esquema
  `rpt`, en modo importación.
- Integrar el documento final reproducible.
- *Terminado cuando:* los tres tableros se actualizan desde el DW y el
  documento final permite reproducir el proyecto desde cero.

**Jorge · Vistas `rpt` y tablero Visión Ejecutiva**
- Crear una vista SQL por tablero.
- Construir el tablero estratégico: KPIs globales, tendencias y filtros por
  periodo y región.
- *Terminado cuando:* los tres tableros leen solo vistas `rpt`, y el
  ejecutivo responde las preguntas clave de E0.

**Harry · Tablero Detección de Problemas**
- Construir el tablero operacional: alertas y desviaciones, rankings top y
  bottom, evolución temporal con formato condicional y resultados de calidad
  de datos.
- *Terminado cuando:* cada alerta tiene su regla documentada.

**Ismael · Tablero Análisis Operativo**
- Construir el tablero táctico: desempeño por ministerio y entidad, y
  comparativos por método de contratación.
- *Terminado cuando:* los filtros funcionan entre visuales y cada gráfico
  tiene un título que dice qué pregunta responde.

**Francis · Documentación de tableros, video y presentación base**
- Documentar cada tablero: propósito, KPIs, vistas usadas y filtros.
- Escribir el guion y editar el video corto.
- Preparar las diapositivas base de la presentación de 15 minutos.
- *Terminado cuando:* la documentación cubre los tres tableros y el video
  es corto, como pide el curso (proponemos un máximo de 5 minutos).

## 6. Matriz de rotación

| Persona | F0 Preparación | F1 Requerimientos | F2 Diseño | F3 Físico y ETL | F4 Carga y pruebas | F5 Visualización |
|---|---|---|---|---|---|---|
| Vladimirjon | Ingesta y fuente | Ingesta y fuente | Ingesta y fuente | Ingesta y fuente | Ingesta y fuente | Conexión e integración final |
| Jorge | Contextualización | Negocio y servicio | Modelado | Transformación | Calidad | Vistas y tablero ejecutivo |
| Harry | Estándar OCDS | Modelado | Transformación | Calidad | Negocio y servicio | Tablero de problemas |
| Ismael | Fuente de entidades | Calidad | Negocio y servicio | Modelado | Transformación | Tablero operativo |
| Francis | Plantilla y glosario | Transformación | Calidad | Negocio y servicio | Modelado | Documentación y video |

Entre las fases 1 y 4, cada persona pasa una vez por cada uno de los cuatro
carriles rotativos, y en cada fase los cuatro carriles tienen responsable.

## 7. Traspaso entre fases

Al cerrar cada fase, quien deja un carril:

1. Escribe una **nota de traspaso** como comentario en el issue de quien
   entra: qué hizo, qué quedó pendiente, qué decisiones tomó y dónde están.
2. Queda como **consultor** de ese carril durante la fase siguiente:
   responde dudas y puede comentar los PR del carril.

## 8. Ritmo de trabajo

- **Reunión semanal de 30 minutos** (día por definir): qué hice, qué haré y
  qué me bloquea. El resto se coordina en los issues.
- **Fecha interna 3 días antes** de cada cierre (sección 3).
- **PR pequeños**, una tarea o una parte de ella, y como máximo 2 PR
  abiertos por persona.
- **Revisión del líder en 48 horas** como máximo.
- **Un bloqueo de más de 2 días se avisa** en el issue y en la reunión; no
  se espera a la fecha de entrega.
- **Cada tarea empieza con su issue**: si no hay issue, no hay trabajo.

## 9. Riesgos del plan

| Riesgo | Mitigación |
|---|---|
| La foto se retrasa y bloquea el diseño | La foto se toma al inicio de la fase 2; en la fase 1 basta una muestra. |
| Power BI no conecta con PostgreSQL | Prueba de conexión en la fase 2, no en enero. |
| Las fiestas frenan la fase 4 | Cargas y pruebas cerradas antes del 22 de diciembre. |
| La revisión del líder se convierte en cuello de botella | PR pequeños y plazo de revisión de 48 horas. |
| El traspaso pierde contexto | Nota de traspaso y consultor del carril saliente. |
| El modelo crece más de lo que pide el curso | ADR 0004: 1 hecho + 4–5 dimensiones en las entregas. |
