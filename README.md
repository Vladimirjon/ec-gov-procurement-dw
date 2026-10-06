# ec-gov-procurement-dw

Data Warehouse académico sobre la contratación pública de la **planta central
del Estado ecuatoriano**, diseñado con la metodología HEFESTO y el modelado
dimensional de Kimball.

> Proyecto universitario independiente (materia de Business Intelligence).
> No está afiliado ni respaldado por SERCOP ni por ninguna entidad pública.

## Estado actual

**Fase: preparación.** El repositorio contiene solo el esqueleto de carpetas y
la documentación de planificación. Todavía **no** existe:

- código de extracción, carga, transformación ni reglas de calidad;
- base de datos, DDL, modelos dbt, vistas ni tableros de Power BI;
- dependencias declaradas, entorno reproducible, pruebas ni CI;
- una foto (snapshot) de datos ni fixtures.

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
- Modelo dimensional (constelación de hechos), ETL, carga batch e
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

Fuente prevista: el portal de datos abiertos de contratación pública de SERCOP
(formato OCDS). **[PENDIENTE]** Los campos, el volumen y la forma de descarga
aún no se han verificado en este repositorio; las observaciones se
documentarán en [`docs/sources/`](docs/sources/).

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
├─ docs/
│  ├─ PROPUESTA.md            # propuesta de arquitectura
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
│  └─ dbt/                    # sujeto a D2 (vacío)
├─ reports/powerbi/           # tableros (vacío)
├─ tests/                     # unit, integration, fixtures (vacíos)
└─ data/                      # ignorado por git
```

Pendientes de aprobación del líder: `pyproject.toml`, `compose.yaml`,
`Makefile`, `.pre-commit-config.yaml` y `.github/` (plantillas y
`CODEOWNERS`). El CI se implementará más adelante, cuando haya código y
pruebas que verificar.

## Decisiones pendientes con el profesor

| # | Pregunta |
|---|---|
| D1 | ¿Qué es "la foto"? ¿La entrega el profesor o la toma el equipo? ¿De qué periodo? |
| D2 | ¿Se acepta PostgreSQL y herramientas como dbt? |
| D3 | ¿Fechas exactas de cada etapa hasta el cierre? |
| D4 | ¿Idioma de los entregables? |
| D5 | ¿Cuánto pesa la parte "profesional o tesis" en la evaluación? |

## Calendario

Entrega por etapas HEFESTO; cierre del proyecto el **22 de enero**. Las
ventanas por etapa son tentativas hasta resolver D3 (ver la sección 9 de la
[propuesta](docs/PROPUESTA.md)).

## Cómo contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Si usas un asistente de IA, este debe
seguir [AGENTS.md](AGENTS.md).

## Licencia

Todos los derechos reservados. Ver [LICENSE](LICENSE). Se puede reconsiderar
una licencia abierta al cierre del proyecto.
