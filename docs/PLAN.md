# Plan de trabajo por hitos

- **Estado:** reemplaza el plan por fases del 10/10/2026. Cambios solo por PR
  aprobado por el líder.
- **Fecha:** 2026-11-03
- **Regla de vigencia:** las instrucciones oficiales son los PDF del profesor,
  guardados localmente en `Instrucciones_Curso/` (ignorada por git). Para cada
  hito manda su guía específica sobre la guía general:
  - `Proyecto Integrador BI ISWD743.pdf`: guía general, requisitos, hitos y
    rúbricas.
  - `Hito 1 - Perfil institucional y preguntas de negocio.pdf`: guía del
    Hito 1.
  - `Hito 2 Adquisición y calidad de datos.pdf` y
    `Hito 3 Modelo dimensional y presentación de avance.pdf` (publicadas el
    20/11/2026), con su texto en `Instrucciones_Curso/_md/`.

  Todo lo anterior (fases 0 a 5, entregables E0, F1-E1, F1-E2, F2 a F5, sus
  fechas y su calendario) **queda sin vigor** salvo que un hito nuevo lo
  retome. El profesor está rediseñando las entregas durante el semestre: este
  plan se revisa cada vez que publique un hito o cambie uno.

## Qué dice el profesor

El proyecto se organiza en seis hitos, cada uno alimenta al siguiente. El
**Hito 1** se revisó el 9 de noviembre de 2026; el **Hito 2** vence el sábado
**21/11/2026** y el **Hito 3** el domingo **22/11/2026**, ambos a las **23:59**
(fechas y hora del líder). Los hitos 4 a 6 no tienen guía
detallada ni fecha; las semanas de la guía son referencia.

| Hito | Semana | Entregable | Estado |
|---|---|---|---|
| H1 | 5 | Perfil del sector + matriz de 3 preguntas (PDF, máx. 6 pp) | **Entregado** (8/11/2026) |
| H2 | 6 | `.pbix` con fuentes conectadas + libro de Excel (Fuentes, Diccionario, Calidad, Cobertura) | **En curso**, vence el sábado 21/11/2026 |
| H3 | 8 | `.pbix` con el modelo dimensional + documento de diseño PDF (máx. 8 pp) + diapositivas PDF; exposición de 10 min | **En curso**, vence el domingo 22/11/2026 |
| H4 | 11 | ETL de un solo comando, carga inicial e incremental, SCD 2, reconciliación | Sin guía detallada ni fecha |
| H5 | 13 | OLAP, tablero en Power BI, modelo analítico en Python | Sin guía detallada ni fecha |
| H6 | 16 | Entrega final y defensa | Sin guía detallada ni fecha |

Reglas que valen para todos los hitos (guía general, secciones 4 y 10):
cada fuente se cita con enlace, fecha de descarga y licencia; el historial de
Git con commits de todos es evidencia de coevaluación; el uso de IA se declara
en el informe (qué se pidió y cómo se verificó); las entregas tardías pierden
10 % por día hábil, hasta 3 días.

## Decisiones tomadas para el Hito 1

- **Caso:** el sector gobierno central completo (Presidencia, ministerios e
  institutos), no una institución. Los GAD y las empresas públicas quedan
  fuera.
- **Ventana de datos:** 2021–2025, años calendario completos.
- **Fuente principal:** datos abiertos de contratación de SERCOP (OCDS).
- **Segunda fuente prevista para el Hito 2:** directorio `gob.ec/instituciones`
  para clasificar entidades. El MEF no se adopta hasta abrir un archivo real.
- **Tres preguntas:** P1 descriptiva, P2 diagnóstica y P3 predictiva, en
  [hito1.md](requirements/hito1.md).

## Trabajo del Hito 1

El entregable es [hito1.md](requirements/hito1.md) convertido en PDF. Cada
persona verifica y cita su parte, y entra por PR pequeño.

| Responsable | Tarea |
|---|---|
| Vladimirjon | Abrir un archivo de SERCOP de 2021 a 2024, registrar la licencia, integrar y entregar |
| Jorge | Marco normativo y entes de control (componente 4) |
| Harry | Indicadores habituales y comprobación de fórmulas de P1 a P3 (componente 7 y matriz) |
| Ismael | Identificación, alcance y misión (componentes 1 y 2) |
| Francis | Actores, procesos y decisores (componentes 3, 5 y 6) y armado del PDF |

Calendario interno (no oficial): secciones en PR el jueves 5/11; integración
y revisión del líder el viernes 6/11; verificación final el sábado 7/11;
margen el domingo 8/11.

## Hitos 2 y 3 (20/11/2026)

El 20/11/2026 el líder recibió las guías detalladas de los hitos 2 y 3
(`Instrucciones_Curso/_md/Hito2.md` y `Hito3.md`, locales). Mandan sobre la guía
general para esos hitos; la diferencia (Power BI y libro de Excel en lugar de
`stg` en PostgreSQL y DDL) está en el [ADR 0005](adr/0005-hitos-2-y-3-power-bi.md)
y sus requisitos, en `requisitos-del-profesor.md` (secciones F y G). No hay
tiempo para repartir tareas por persona: el líder dirige, los agentes ejecutan
y la parte de Power BI Desktop la hace el líder.

| Fecha | Trabajo |
|---|---|
| Vie 20/11 | Descarga de 2021–2025, decisión del formato de conexión, segunda fuente (entidades), perfilado completo; diseño dimensional |
| Sáb 21/11 | Conexión y perfilado en Power BI, libro de Excel, entrega del Hito 2; semilla de clasificación de entidades |
| Dom 22/11 | Transformaciones, dimensiones y hecho, modelo en Power BI, bitácora, PDF de diseño, diapositivas, entrega del Hito 3 |

Las tareas son los issues del milestone **H2** y **H3** de GitHub; el issue de
coordinación («H2/H3 · Coordinación») tiene el mapa con dependencias, ejecutor y
plan de recorte. Hora límite de cada entrega: **23:59** (sábado 21/11 y domingo
22/11). El equipo se llama **Grupo 5** (asignado por el profesor).

## Qué se conserva del trabajo anterior

- **Evidencia de la fuente:** `docs/sources/` (reconocimiento, OCDS,
  entidades).
- **Decisiones técnicas:** los ADR 0001 a 0004, reescritos el 3/11/2026 según
  los PDF.
- **Glosario** y flujo de trabajo (issue, rama, PR).

`deliverables/` ya está reorganizado por hitos (`h1` a `h6`). El resto de la
documentación de `docs/sources/` (reconocimiento, entidades) conserva
referencias a fases anteriores en su historial; son evidencia y no se
reescriben. Los ADR de `docs/adr/` se actualizaron el 3/11/2026 a lo que
piden los PDF y son las decisiones vigentes.
