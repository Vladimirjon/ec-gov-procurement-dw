# ec-gov-procurement-dw

Data Warehouse académico sobre la contratación pública del **gobierno central
del Ecuador** (Presidencia de la República, ministerios e institutos que
dependen de ellos), para el proyecto integrador de Business Intelligence
(ISWD743, FIS-EPN). Metodología HEFESTO y modelado dimensional de Kimball.

> Proyecto universitario independiente. No está afiliado ni respaldado por
> SERCOP ni por ninguna entidad pública.

## Instrucciones vigentes

Mandan los dos PDF del profesor: la guía del proyecto y la guía del Hito 1
(guardados localmente en `Instrucciones_Curso/`, ignorada por git). El proyecto
se entrega en seis hitos y hoy solo el **Hito 1** tiene fecha: revisión el
9/11/2026, por confirmar. Los demás hitos pueden cambiar.

- Plan, reparto y calendario: [docs/PLAN.md](docs/PLAN.md)
- Todas las directrices del profesor y su estado:
  [docs/requisitos-del-profesor.md](docs/requisitos-del-profesor.md)
- Borrador del Hito 1: [docs/requirements/hito1.md](docs/requirements/hito1.md)

## Estado actual

Hito 1 en curso. El repositorio contiene documentación, el esqueleto de
carpetas y scripts auxiliares de reconocimiento de SERCOP. Se descargaron
localmente (fuera de Git) el JSON de enero de 2025 y el anual de 2025, y se
midieron su estructura y volumen. Todavía **no** existe:

- código de extracción, carga, transformación ni reglas de calidad;
- base de datos, DDL, vistas ni tableros de Power BI;
- dependencias declaradas, entorno reproducible, pruebas ni CI;
- la carga definitiva del periodo 2021–2025 ni fixtures.

Lo descrito en [Arquitectura prevista](#arquitectura-prevista) es diseño, no
funcionalidad implementada.

## Caso de estudio

- **Sector:** gobierno central completo, no una institución. Quedan fuera los
  GAD y sus empresas, las empresas públicas y otras funciones del Estado.
- **Periodo:** 2021–2025, años calendario completos.
- **Fuente principal:** datos abiertos de contratación pública de SERCOP
  (OCDS). Segunda fuente prevista: directorio `gob.ec/instituciones`, para
  clasificar a las entidades compradoras.
- **Preguntas de negocio del Hito 1:** monto adjudicado por método y tipo de
  entidad (descriptiva), desviación entre valor adjudicado y estimado
  (diagnóstica) y proyección mensual del monto adjudicado (predictiva).

Detalle y justificación: [ADR 0001](docs/adr/0001-alcance.md) y
[reconocimiento de la fuente](docs/sources/reconocimiento.md): **190.619
procesos distintos** en la descarga anual de 2025, coincidentes con el contador
del portal. Los conteos son nacionales, no del gobierno central.

## Arquitectura prevista

```
SERCOP (OCDS) --> data/ --> stg --> ETL --> dw --> OLAP, Power BI, modelo analítico
                  (archivos  (copia  (Python  (hechos,
                   crudos)    cruda)  y SQL)   dimensiones
                                              y vistas)
                         audit: bitácora de cargas y filas rechazadas
```

Principios: los archivos descargados son evidencia inmutable; dimensiones
antes que hechos; cargas idempotentes; cada carga deja bitácora; el tablero
lee solo del esquema `dw`; no se versionan datasets completos ni secretos.
Decisiones: [ADR](docs/adr/README.md).

## Estructura del repositorio

```
├─ AGENTS.md                  # reglas para asistentes de IA
├─ CONTRIBUTING.md            # flujo de trabajo del equipo
├─ LICENSE
├─ .github/                   # CODEOWNERS y plantillas de PR e issues
├─ docs/
│  ├─ PLAN.md                 # plan por hitos y reparto
│  ├─ requisitos-del-profesor.md
│  ├─ uso-de-ia.md            # registro del uso de IA (lo exige el profesor)
│  ├─ glosario.md             # términos del proyecto, cada uno con su fuente
│  ├─ adr/                    # decisiones vigentes
│  ├─ requirements/           # Hito 1 y su insumo
│  ├─ sources/                # observaciones de la fuente
│  ├─ design/  etl/  validation/  dashboards/   # hitos siguientes (vacíos)
├─ src/ec_gov_procurement_dw/ # extract, snapshot, load, quality (vacíos)
├─ warehouse/
│  ├─ ddl/                    # DDL (vacío)
│  └─ seeds/                  # clasificación de entidades (vacío)
├─ notebooks/                 # perfilado, ETL, modelo analítico (vacío)
├─ scripts/                   # auxiliares de reconocimiento; no son el ETL
├─ reports/powerbi/           # tablero (vacío)
├─ tests/                     # unit, integration, fixtures (vacíos)
├─ deliverables/              # entregas por hito (h1 a h6) y plantilla
└─ data/                      # ignorado por git
```

Pendientes: `pyproject.toml`, `compose.yaml` y `Makefile`, que se crean cuando
empiece el Hito 2. El CI se activa cuando haya código que verificar.

## Cómo contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Si usas un asistente de IA, este debe
seguir [AGENTS.md](AGENTS.md) y debes anotar su uso en
[docs/uso-de-ia.md](docs/uso-de-ia.md).

## Licencia

Todos los derechos reservados. Ver [LICENSE](LICENSE). Se puede reconsiderar
una licencia abierta al cierre del proyecto.
