# ec-gov-procurement-dw

Data Warehouse académico sobre la contratación pública de la **planta central
del Estado ecuatoriano**, diseñado con la metodología HEFESTO y el modelado
dimensional de Kimball.

> Proyecto universitario independiente (materia de Business Intelligence).
> No está afiliado ni respaldado por SERCOP ni por ninguna entidad pública.

## Estado actual

**Fase: preparación.** El repositorio contiene el esqueleto de carpetas,
documentación y scripts auxiliares de reconocimiento de SERCOP. Se descargaron
localmente el JSON de enero y el anual de 2025, fuera de Git, y se midieron
estructura, volumen y algunas limitaciones. Todavía **no** existe:

- código de extracción, carga, transformación ni reglas de calidad;
- base de datos, DDL, modelos dbt, vistas ni tableros de Power BI;
- dependencias declaradas, entorno reproducible, pruebas ni CI;
- una foto definitiva aprobada con manifiesto ni fixtures.

Todo lo descrito en [Arquitectura prevista](#arquitectura-prevista) es un
diseño propuesto, no funcionalidad implementada.

## Problema

La contratación pública de la planta central se publica como datos abiertos,
pero analizarla exige integrar procesos, entidades compradoras y proveedores en
un modelo orientado al análisis, y saber qué tan confiables son esos datos.
El proyecto busca responder preguntas como:

- ¿Cuánto contrata cada entidad, por año y por método de contratación?
- ¿Cuántos procesos hay por método de contratación?
- ¿Qué porcentaje de procesos no tiene proveedor o presupuesto registrado?
- ¿Cuánto se desvía el monto contratado del presupuesto?
- ¿Qué tan concentrados están los proveedores por entidad?
- ¿Qué tan completos y consistentes son los datos de cada entidad?

**[PENDIENTE]** Los indicadores definitivos los confirma el equipo en la
etapa de requerimientos.

## Alcance

**Dentro:**

- Procesos de contratación de la planta central: **Presidencia de la
  República**, **ministerios** e **institutos que dependen de los
  ministerios**, sobre una foto fija de uno o más años.
- Toda la planta central, no una muestra de entidades.
- Modelo dimensional (un hecho y de 4 a 5 dimensiones en las entregas, según
  el [ADR 0004](docs/adr/0004-alcance-del-modelo.md)), ETL, carga batch e
  incremental, pruebas y bitácora de cargas.
- Indicadores de negocio y de calidad de datos.
- Tres tableros en Power BI conectados al DW.

**Fuera:**

- **GAD de cualquier nivel (provincial, cantonal, parroquial) y sus
  empresas.**
- Cualquier otra entidad fuera de la planta central.
- Ingesta continua o en tiempo real.
- Microservicios, Kafka, Kubernetes y autenticación de usuarios finales.
- Datos personales más allá de lo que la fuente ya publica.

**Clasificación de entidades.** No se asume que la fuente indique qué
entidades pertenecen a la planta central. El equipo construirá una tabla de
clasificación versionada como semilla, en la que cada entidad será
Presidencia, ministerio, instituto dependiente de un ministerio o fuera de
alcance. **[PENDIENTE]** Fuente oficial y criterios de inclusión.

Detalle y justificación: [ADR 0001](docs/adr/0001-alcance.md).

## Fuente de datos

Fuente: el portal de datos abiertos de contratación pública de SERCOP (OCDS).
El [reconocimiento](docs/sources/reconocimiento.md) documenta los enlaces de
descarga y API, campos reales y la lectura del ZIP anual de 2025: **190.619
`ocid` distintos**, coincidentes con el contador del portal; 160.930.685 bytes
comprimidos y 1.721.952.613 bytes sin comprimir.

La API anuncia un límite de 60 y las observaciones muestran reinicios con una
cadencia cercana a un minuto, pero el ámbito del contador no está publicado y
no se comportó como una cuota exclusiva del cliente. Siguen pendientes la
clasificación de entidades y las decisiones de periodo/formato de la foto. Los
conteos son nacionales; no representan todavía el subconjunto de la planta
central.

### Dónde estamos y qué le toca al líder

- [Issue #9: reconocimiento de la fuente](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/9):
  cerrado el 15/10/2026 con el PR #24; sus cinco criterios tienen evidencia.
  Estado detallado en
  [reconocimiento.md](docs/sources/reconocimiento.md#estado-de-los-criterios-del-issue-9).
- [Issue #14: integrar y entregar E0](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/14):
  integrar el contenido de Jorge (#10), la plantilla de Francis (#13) y los
  hallazgos de la fuente; fecha interna **17 de octubre**. Ver la
  [ruta del líder en fase 0](docs/PLAN.md#ruta-del-líder-en-la-fase-0).
- El periodo definitivo de la foto pertenece al
  [issue #15, fase 1](https://github.com/Vladimirjon/ec-gov-procurement-dw/issues/15).
  La indicación docente es analizar cinco años o comparar por gobiernos. Como
  SERCOP no expone un campo de gobierno o administración, #15 evaluará el
  periodo por fechas; `2021–2025` es el candidato inicial por ser cinco años
  calendario completos, no una decisión aprobada todavía.
  La toma formal de la foto con manifiesto pertenece al inicio de la fase 2;
  las descargas de reconocimiento no sustituyen esas decisiones.

## Arquitectura prevista

```
SERCOP (OCDS) --> data/snapshots --> stg --> dw --> rpt --> Power BI
                  (foto inmutable)    (staging) (hechos y   (vistas)
                                                 dimensiones)
```

Principios: la foto es evidencia inmutable; dimensiones antes que hechos;
cargas idempotentes; cada carga deja bitácora; los tableros solo leen vistas
del esquema `rpt`; no se versionan datasets completos ni secretos.

Detalle: [propuesta de arquitectura](docs/PROPUESTA.md),
[ADR 0002](docs/adr/0002-foto-inmutable.md) y
[ADR 0003](docs/adr/0003-pila-tecnologica.md).

## Estructura del repositorio

```
├─ AGENTS.md                  # reglas para asistentes de IA
├─ CONTRIBUTING.md            # flujo de trabajo del equipo
├─ LICENSE
├─ .github/                   # CODEOWNERS y plantillas de PR e issues
├─ docs/
│  ├─ PLAN.md                 # plan de trabajo, tareas y rotación
│  ├─ PROPUESTA.md            # propuesta de arquitectura
│  ├─ glosario.md             # términos del proyecto, cada uno con su fuente
│  ├─ adr/                    # decisiones de arquitectura
│  ├─ requirements/           # semana 1
│  ├─ design/                 # semana 2
│  ├─ etl/                    # semana 3
│  ├─ validation/             # semana 4
│  ├─ dashboards/             # semana 5
│  └─ sources/                # observaciones de la fuente
├─ src/ec_gov_procurement_dw/ # extract, snapshot, load, quality (vacíos)
├─ warehouse/
│  ├─ ddl/                    # DDL físico (vacío)
│  └─ dbt/                    # modelos y pruebas dbt (vacío)
├─ notebooks/                 # notebooks entregables: perfilado, ETL (vacío)
├─ scripts/                   # auxiliares de reconocimiento; no son el ETL del DW
├─ reports/powerbi/           # tableros (vacío)
├─ tests/                     # unit, integration, fixtures (vacíos)
├─ deliverables/              # versiones finales de cada entrega
└─ data/                      # ignorado por git
```

Pendientes de aprobación del líder: `pyproject.toml`, `compose.yaml`,
`Makefile` y `.pre-commit-config.yaml`. El CI se implementará más adelante,
cuando haya código y pruebas que verificar.

## Decisiones del equipo

| # | Tema | Decisión |
|---|---|---|
| D1 | La foto | La toma el equipo, de SERCOP (OCDS). Periodo **[PENDIENTE]** tras reconocer la fuente. |
| D2 | Herramientas | Libres; se adopta PostgreSQL y dbt ([ADR 0003](docs/adr/0003-pila-tecnologica.md)). |
| D3 | Calendario | El de la sección 9 de la [propuesta](docs/PROPUESTA.md). |
| D4 | Idioma | Documentos en español; código y nombres técnicos en inglés. |
| D5 | Rigor | Nivel profesional, con proyección a tesis. |

## Calendario

Entrega por etapas HEFESTO; cierre del proyecto el **22 de enero de 2027**.

| Etapa | Ventana |
|---|---|
| Preparación | 10 a 19 oct |
| 1. Requerimientos | 20 oct a 2 nov |
| 2. Diseño conceptual y lógico | 3 a 23 nov |
| 3. Diseño físico y ETL | 24 nov a 14 dic |
| 4. Carga y pruebas | 15 dic a 8 ene |
| 5. Visualización y cierre | 9 a 22 ene |

## Cómo contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Si usas un asistente de IA, este debe
seguir [AGENTS.md](AGENTS.md).

## Licencia

Todos los derechos reservados. Ver [LICENSE](LICENSE). Se puede reconsiderar
una licencia abierta al cierre del proyecto.
