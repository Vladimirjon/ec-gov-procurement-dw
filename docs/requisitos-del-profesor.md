# Requisitos del profesor y estado del equipo

- **Fuente:** `Proyecto Integrador BI ISWD743.pdf` (guía general, 17 pp) y
  `Hito 1 - Perfil institucional y preguntas de negocio.pdf` (10 pp), guardados
  en `Instrucciones_Curso/` (local, ignorada por git). Los PDF mandan; esta
  lista es un resumen propio para trabajar. Se actualiza cuando el profesor
  publique o cambie un hito.
- **Revisada:** 2026-11-03; sección B actualizada el 2026-11-08; secciones F
  y G (guías de los hitos 2 y 3, `Hito 2 Adquisición y calidad de datos.pdf` y
  `Hito 3 Modelo dimensional y presentación de avance.pdf`) añadidas el
  2026-11-20. Las filas de la sección A que mencionan `stg` en PostgreSQL o el
  DDL para H2 y H3 se leen con la contradicción 7 de la sección E.
- **Estado:** ✅ cubierto · ⚠ parcial o pendiente de verificar · ❌ falta ·
  ❓ el profesor se contradice (ver al final).

## A. Requisitos generales del proyecto (guía general)

| # | Directriz | Sección del PDF | Estado | Dónde o qué falta |
|---|---|---|---|---|
| G1 | Un sector asignado (gobierno central), con datos públicos | 2, 3 | ✅ | `hito1.md` |
| G2 | Equipo de 3 a 4; somos 5 | 2 | ✅ | El profesor lo autorizó (dicho por el líder) |
| G3 | Roles sugeridos: líder y analista de negocio, ingeniero de datos (ETL y calidad), modelador, analista y diseñador del tablero. Organizan el trabajo, no la defensa: todos exponen y responden | 2.2 | ⚠ | Ver sección C |
| G4 | Preferir datos abiertos verificables; datos sintéticos solo si son escasos y declarados | 2.3 | ✅ | SERCOP |
| G5 | **Al menos 2 fuentes integrables y 3 periodos** | 4 | ⚠ | SERCOP + catálogo `gob.ec`. Falta confirmar si el catálogo cuenta como fuente integrable |
| G6 | Al menos 10.000 filas en el hecho principal | 4 | ✅ | 190.619 procesos solo en 2025 |
| G7 | 1 hecho, dimensión tiempo, **3 dimensiones conformadas** y una SCD tipo 2 | 4 | ⚠ | ADR 0004 (`dim_entity` SCD 2). Sin diseño definitivo |
| G8 | Un solo comando reconstruye el DW desde cero | 4, 11 | ❌ | Hito 4 |
| G9 | OLAP (roll-up, drill-down, slice, dice, pivot) y un modelo analítico validado (clustering, regresión, clasificación o series) | 4, 5 | ⚠ | P3 (serie de tiempo). Sin OLAP planificado |
| G10 | Power BI con al menos 2 páginas (resumen ejecutivo y detalle) e interactividad | 4 | ⚠ | El plan previo hablaba de 3 tableros; se reduce a lo pedido |
| G11 | Entregables: repo Git, `.pbix`, informe técnico, presentación, resumen de 1 página | 4 | ❌ | Hitos 5 y 6 |
| G12 | Arquitectura: fuentes → `stg` → ETL → `dw` → OLAP, Power BI y modelo en Python. **El tablero lee solo del esquema `dw`**. No se sustituye PostgreSQL ni Power BI; sí se pueden agregar dbt, Airflow, Metabase | 5 | ❓ | Nuestro `rpt` es un esquema aparte; ver decisión D1 |
| G13 | Evidencia: esquemas `stg` y `dw` con DDL versionado, scripts y bitácora, notebooks reproducibles, `.pbix`, historial de Git con commits de todo el equipo | 5 | ⚠ | Se genera hito a hito |
| G14 | Rúbrica de hitos 1 a 5: cumplimiento, calidad técnica, documentación, conexión con el caso | 9.1 | ❓ | Ver sección D |
| G15 | Rúbrica de H6: perfil y preguntas, datos y calidad, modelo, ETL, analítica y tablero, comunicación | 9.2 | ❌ | Hito 6 |
| G16 | Defensa: narrativa para decisores, empezar con la cifra impactante, todos exponen, reconocer limitaciones, plan B con capturas | 8, 11 | ❌ | Hito 6 |
| G17 | Preparar respuestas a: de dónde vienen los datos y su confiabilidad, datos faltantes, costo de mantener el DW, un solo indicador, limitaciones | 8.3 | ⚠ | Parte ya documentada en `reconocimiento.md` |
| G18 | Toda fuente se cita con enlace, fecha de descarga y licencia; un dato sin fuente no entra al DW | 10 | ⚠ | Falta registrar la licencia de SERCOP |
| G19 | Datos personales anonimizados antes de `stg` (LOPDP) | 10 | ⚠ | Ver decisión D3 |
| G20 | Datos internos exigen carta de autorización; datos sintéticos se marcan | 10 | n/a | No se usan |
| G21 | El repositorio Git existe desde el Hito 1 con commits de todos; es evidencia de coevaluación | 10 | ⚠ | Cada persona debe tener commits propios con trabajo real |
| G22 | **El uso de IA se declara en el informe: qué se pidió y cómo se verificó** | 10 | ❌ | Ver decisión D4 |
| G23 | Entregas tardías: −10 % por día hábil, máximo 3 días | 10 | ✅ | Calendario interno con margen |
| G24 | Checklist final: DW reconstruible en otra máquina, `.pbix` limpio, resumen ejecutivo comprensible en 30 s, máx. 6 visuales en el resumen, no usar rojo y verde como único contraste, informe de 1 página, presentación de 18 a 22 min | 7, 11 | ❌ | Hito 6 |

## B. Hito 1 (guía del Hito 1)

| # | Directriz | Estado | Dónde o qué falta |
|---|---|---|---|
| H1-1 | El objeto de estudio es el **sector completo**, no una institución | ✅ | `hito1.md` |
| H1-2 | PDF de máximo 6 páginas sin contar anexos; perfil de 1 a 3 páginas | ✅ | PDF entregable de 6 páginas: perfil 3, Parte 2 en la 4 y anexos en la 5 y 6 (8/11/2026) |
| H1-3 | Al inicio: nombre del equipo, sector y fecha | ✅ | Equipo Trazabilidad Pública, sector gobierno central y fecha 08/11/26 |
| H1-4 | Los 8 componentes: identificación y alcance, misión y servicios, actores, marco normativo y entes de control, procesos clave, tomadores de decisión, indicadores habituales, fuentes | ✅ | Los ocho componentes sin marcas [VERIFICAR] ni [PENDIENTE] (el script falla si aparece alguna) |
| H1-5 | Cuántas instituciones tiene el sector, aproximado y con fuente | ✅ | `gob.ec` y menú del portal del MDEP, cifras aproximadas con fuente y fecha |
| H1-6 | Marco normativo y entes **vigentes** | ✅ | Sección 4 verificada el 8/11/2026 (#36) |
| H1-7 | De 2 a 3 tomadores de decisión con su decisión principal | ✅ | Sección 6, con respaldo normativo (#39) |
| H1-8 | Indicadores que el sector ya usa y fuentes públicas encontradas | ✅ | Informe de rendición de cuentas 2025 de SERCOP abierto; cifras con página (sección 7, #37) |
| H1-9 | Cada dato relevante con fuente citada (sitio oficial, ley, informe), con enlace y fecha de consulta | ⚠ | Se completa en las tareas #35 a #39 |
| H1-10 | Redactar con palabras propias, citando; no copiar de un sitio | ⚠ | Revisar al integrar |
| H1-11 | Matriz de **3** preguntas con: pregunta (indicador, periodo, alcance), decisor y decisión, tipo, indicador con fórmula, dimensiones, fuente candidata con enlace | ✅ | `hito1.md` |
| H1-12 | Al menos una descriptiva y una diagnóstica; la tercera puede ser predictiva | ✅ | P1, P2, P3 |
| H1-13 | Cada pregunta cumple las 5 condiciones: apoya una decisión, es medible, tiene alcance, es respondible con datos públicos, es analítica | ✅ | Anexo A, «Comprobación de las cinco condiciones» (#37); P3 queda condicionada a la fecha del Hito 2 |
| H1-14 | Cada pregunta se expresa como "medida por dimensiones" (la estrella empieza aquí) | ✅ | Indicadores y dimensiones separados |
| H1-15 | Hacer una lluvia de ideas de al menos 8 preguntas candidatas y filtrar a 3 | ✅ | Anexo A: ocho candidatas y las tres elegidas |
| H1-16 | **Prueba del archivo:** descargar y abrir un archivo de cada fuente candidata y anotar los años disponibles | ✅ | ZIP anuales de SERCOP 2021, 2024 y 2025 y el mensual de enero de 2025 abiertos; el directorio `gob.ec` se consultó en la web |
| H1-17 | Preferir fuentes descargables (CSV o Excel) a tablas dentro de un PDF; buscar series de varios años | ⚠ | SERCOP sí; MEF solo en PDF por ahora |
| H1-18 | Repositorio Git con la estructura de carpetas del proyecto | ✅ | Existe |
| H1-19 | Entrega al aula virtual con el nombre `Hito1_Apellido1Apellido2ApellidoN.pdf` | ❓ | Se usa el nombre de la ficha del hito (`Hito1_BravoFreireGuajanPasquelTorres`, en `.docx` y luego en `.pdf`); el paso 10 de la guía menciona otro |
| H1-20 | Rúbrica sobre 20: cumplimiento 4, perfil 5, calidad de preguntas 6, viabilidad con datos 5 | — | Se usa de lista de control |

## C. Roles con 5 personas

La guía sugiere 4 roles y aclara que los roles organizan el trabajo, no la
defensa. Con 5 personas se mantienen los 4 roles y el rol que más trabajo
concentra (ingeniería de datos: staging, ETL y calidad) se divide en dos:

| Rol (guía del profesor) | Cobertura en el equipo |
|---|---|
| Líder de proyecto y analista de negocio | 1 persona: el líder. Integra los entregables, revisa los PR y lleva las preguntas de negocio |
| Ingeniero de datos (ETL y calidad) | **2 personas:** una en ingesta y carga a `stg` (extracción, foto, staging), otra en transformación, calidad y reconciliación (ETL, bitácora, pruebas) |
| Modelador del data warehouse | 1 persona: matriz de bus, estrella, DDL |
| Analista y diseñador del tablero | 1 persona: OLAP, Power BI y modelo analítico |

Propuesta de continuidad: **los roles se fijan al empezar el Hito 2** (cuando
haya guía), se rotan una sola vez al inicio del segundo bimestre (Hito 4) y
cada persona tiene en cada hito una tarea con commits propios, porque el
historial de Git es evidencia de coevaluación. El Hito 1 no usa roles: se
reparte por componentes del documento (ver [PLAN.md](PLAN.md)).

## D. Decisiones tomadas para cubrir los requisitos

| # | Decisión | Motivo |
|---|---|---|
| D1 | Las vistas de reporte viven en el esquema `dw`; no existe un esquema `rpt` aparte. El tablero lee solo `dw` | G12 pide que el tablero lea solo del esquema `dw` |
| D2 | Hito 1: 3 preguntas núcleo más un anexo con 8 candidatas filtradas | H1 pide 3; la guía general pide 5 a 8; la lluvia de ideas del paso 5 cubre ambas |
| D3 | Los campos de contacto de las partes (`contactPoint`: nombres, correos, teléfonos) no se cargan a `stg`. Los identificadores de proveedores personas naturales se seudonimizan en el ETL | G19 y la regla de cargar solo lo que responde preguntas (Hito 2) |
| D4 | Se mantiene `docs/uso-de-ia.md` con qué se pidió a un asistente y cómo se verificó, por persona y por hito. Se crea antes del Hito 1 | G22. No hay atribución de IA en commits ni PR; la declaración va en el informe |
| D5 | El número de tableros baja de 3 a lo pedido: 2 páginas mínimo (ejecutivo y detalle) | G10 |
| D6 | `PROPUESTA.md` se eliminó. Los ADR 0001 a 0004 se reescribieron y están aceptados con lo que piden los PDF; el ADR 0002 pasó a `0002-datos-crudos-versionados.md` y el 0004 a `0004-modelo-dimensional.md` | Los PDF mandan; los ADR viejos contradecían a los PDF (dbt, `rpt`, foto con manifiesto) |

## E. Contradicciones del propio profesor (para preguntarle solo estas)

1. **Preguntas:** la guía general pide 5 a 8 y el Hito 1 pide 3. *Propuesta: 3
   en el Hito 1 más un anexo de candidatas.*
2. **Nombre del archivo del Hito 1:** `Hito1_Apellido1Apellido2ApellidoN.pdf` en
   la ficha y `Proyecto_EquipoX_Hito1` en el paso 10. *Propuesta: el de la
   ficha.*
3. **Caso:** la guía general habla de "una institución concreta" y el Hito 1 de
   "el sector completo". *Propuesta: sector completo.*
4. **Puntaje de los hitos 1 a 5:** la guía general dice sobre 10 y su tabla
   suma 20; el Hito 1 dice 20. El H6 se menciona sobre 25 y su tabla suma 20.
   *Propuesta: 20.*
5. **Duración de la defensa:** 15 + 5 minutos (sección 8), 20 + 10 (Hito 6) y
   18 a 22 al ensayar (checklist). *Propuesta: 20 minutos más preguntas.*
6. **Dimensiones conformadas con un solo hecho:** se pide 1 hecho y 3
   dimensiones conformadas. *Propuesta: es válido con un hecho; si se agrega un
   segundo hecho, las dimensiones se comparten.*
7. **Hitos 2 y 3: guía general frente a guías específicas (20/11/2026).** La
   guía general pide para H2 `stg` en PostgreSQL, notebook de perfilado y
   diccionario en Excel, y para H3 matriz de bus, estrella y DDL ejecutado; las
   guías específicas piden `.pbix` con Power Query y un libro de Excel (H2) y
   `.pbix` con el modelo, documento de diseño PDF y diapositivas (H3).
   *Propuesta (ADR 0005, D1): mandan las guías específicas; PostgreSQL, `stg` y
   DDL pasan al Hito 4. El DDL de respaldo es un issue opcional.*
8. **Nombre de los archivos de H2 y H3:** `Proyecto_EquipoX_Hito2.pbix` y
   `..._Hito3.pbix`, sin definir `X`. *Resuelto por el líder el 20/11: el
   profesor asignó el nombre «Grupo 5», así que `X` = `Grupo5`
   (`Proyecto_Grupo5_Hito2`).*
9. **Hora límite de las entregas del 21 y 22/11:** las guías no la indican.
   *Resuelto por el líder el 20/11: 23:59 de cada día.*

## F. Hito 2 (guía del Hito 2, 20/11/2026): requisitos y dónde se cubren

La guía manda; esta tabla es un resumen propio. Estado: ❌ falta · ⚠ en curso ·
✅ cubierto. «Issue» es el código del título del issue de GitHub (milestone H2).

| # | Directriz (sección de la guía) | Estado | Issue |
|---|---|---|---|
| H2-1 | `.pbix` con las fuentes de las tres preguntas conectadas; ≥1 conjunto de datos por pregunta; consulta con nombre claro; solo pasos de conexión (4.1) | ❌ | H2-05 |
| H2-2 | Archivos originales sin modificar en `datos_crudos` (4.1, 5, 9) | ❌ | H2-01 |
| H2-3 | Inventario: entidad, enlace exacto, formato y conector, periodo, frecuencia, filas y fecha de descarga (4.2) | ❌ | H2-01, H2-03, H2-06 |
| H2-4 | Diccionario: grano de cada tabla en una frase; por campo descripción, tipo, valores válidos, rol (medida o atributo) y observación del perfil (4.3) | ❌ | H2-06 |
| H2-5 | Perfilado sobre **todo el conjunto**, no las primeras 1000 filas (3.3, 5) | ❌ | H2-04, H2-05 |
| H2-6 | Diagnóstico: tabla y campo, dimensión de calidad, evidencia medible, impacto en las preguntas, acción para H3 (4.4); seis dimensiones revisadas (3.2) | ❌ | H2-04, H2-06 |
| H2-7 | Matriz de cobertura de las tres preguntas; si una no se puede responder, se ajusta y se explica (4.5) | ❌ | H2-06 |
| H2-8 | Total de control inicial por tabla (filas y suma de la medida) (5, paso 10) | ❌ | H2-04 |
| H2-9 | Libro con equipo, sector y fecha al inicio (6) | ❌ | H2-06 |
| H2-10 | No se corrige nada en H2; la limpieza es de H3 (1, 5, 9) | ⚠ | todos |
| H2-11 | Entrega `Proyecto_EquipoX_Hito2.pbix` + libro con Fuentes, Diccionario, Calidad y Cobertura (ficha) el 21/11/2026 | ❌ | H2-07 |

## G. Hito 3 (guía del Hito 3, 20/11/2026): requisitos y dónde se cubren

| # | Directriz (sección de la guía) | Estado | Issue |
|---|---|---|---|
| H3-1 | Acciones del diagnóstico de H2 aplicadas en Power Query y documentadas, con total de control antes y después (4.1, 4.3, 5) | ❌ | H3-03, H3-06 |
| H3-2 | Cuatro pasos de Kimball por tabla de hechos: proceso, grano, dimensiones y hechos, en ese orden (3.1, 4.2) | ❌ | H3-01 |
| H3-3 | Matriz de bus (4.2, 6.2) | ❌ | H3-01 |
| H3-4 | Al menos un hecho y tres dimensiones, una de ellas de tiempo (4.1) | ❌ | H3-04 |
| H3-5 | Claves únicas en las dimensiones; relaciones de uno a varios con filtro único (4.1, 5) | ❌ | H3-04, H3-05 |
| H3-6 | Convención `Fact…`/`Dim…`, columnas de clave ocultas, grano en la descripción de la tabla (4.1, 8) | ❌ | H3-05 |
| H3-7 | La tabla de hechos solo tiene claves y medidas; no guarda tasas ni porcentajes (3.2, 7) | ❌ | H3-01, H3-04 |
| H3-8 | Totales de control cuadran: filas del hecho = filas de origen y la suma de la medida no cambia (5, 7) | ❌ | H3-03, H3-04 |
| H3-9 | Página de prueba con una matriz o gráfico simple que responde al menos una pregunta (4.1) | ❌ | H3-05 |
| H3-10 | Documento de diseño PDF (máx. 8 pp sin anexos): cuatro pasos, matriz de bus, captura de la vista de modelo, tabla pregunta → hechos y dimensiones (4.2) | ❌ | H3-07 |
| H3-11 | Bitácora: problema, transformación, nombre del paso en Power Query y total de control (4.3, 6.3) | ❌ | H3-06 |
| H3-12 | Presentación de 10 minutos más 5 de preguntas con la estructura de 6.4; presentan todos; demostración en Power BI (4.4) | ❌ | H3-08 |
| H3-13 | Nombre del equipo, sector y fecha en la portada del documento y en la primera diapositiva (6) | ❌ | H3-07, H3-08 |
| H3-14 | Entrega `Proyecto_EquipoX_Hito3.pbix`, documento PDF y diapositivas PDF el 22/11/2026 (ficha) | ❌ | H3-09 |
| H3-15 | (Guía general) DDL del esquema `dw` ejecutado en PostgreSQL | ❓ | H3-10 (opcional) |
