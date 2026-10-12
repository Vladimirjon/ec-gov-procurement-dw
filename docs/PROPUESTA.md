# Propuesta de arquitectura y estructura: `ec-gov-procurement-dw`

**Estado:** borrador para revisión del equipo · **Autor:** líder de equipo · **Fecha:** 2026-10-06
**Cierre del proyecto:** 2027-01-22 (entrega por etapas)

> Este documento sirve de punto de partida del repositorio nuevo. Se divide en
> una propuesta para el equipo (secciones 1 a 11) y un prompt inicial para
> asistentes de IA (sección 12). Lo marcado como **[CONFIRMAR]** no es una
> decisión: depende de una verificación pendiente o de la aprobación del líder.

---

## 1. Contexto y objetivo

Materia de BI con enfoque en Data Warehouse (HEFESTO + Kimball). El profesor
asignó el sector **Gobierno y Ministerio**, es decir, la **planta central**
del Estado: la **Presidencia de la República**, los **ministerios** y los
**institutos que dependen de los ministerios**. Se espera cubrir **toda la
planta central**, no una muestra de entidades, trabajando con **una foto
(snapshot)** de los datos. **Los GAD quedan fuera** (ni gobiernos
autónomos descentralizados ni sus empresas).

**Objetivo:** construir un Data Warehouse de la contratación pública de la
planta central del Estado ecuatoriano, con evaluación de calidad de datos, cargas batch
e incrementales, pruebas reproducibles y tableros en Power BI. El diseño debe
poder crecer hacia un trabajo profesional o de tesis.

**Fuente prevista:** portal de datos abiertos de contratación pública de
SERCOP (formato OCDS). El proyecto es académico e independiente y no está
afiliado ni respaldado por SERCOP ni por ninguna entidad.

## 2. Alcance

**Dentro:**
- Procesos de contratación de la planta central: Presidencia de la
  República, ministerios e institutos que dependen de los ministerios,
  sobre una foto fija de uno o más años.
- Modelo dimensional (constelación de hechos), ETL, carga batch e
  incremental, pruebas, bitácora de cargas.
- Indicadores de negocio y de calidad de datos.
- Tres tableros en Power BI conectados al DW.

**Fuera (por ahora):**
- Ingesta continua o en tiempo real.
- Microservicios, Kafka, Kubernetes, autenticación de usuarios finales.
- **GAD de cualquier nivel (provincial, cantonal, parroquial) y sus empresas.**
  Esto excluye, por ejemplo, empresas municipales como la Empresa Eléctrica
  Quito.
- Entidades fuera de la planta central tal como la define el alcance.
- Cualquier dato personal más allá de lo que la fuente ya publica.

**Clasificación de entidades.** No se asume que SERCOP indique qué entidades
pertenecen a la planta central. Hay que construir una tabla de clasificación
(entidad, tipo, ministerio del que depende, sector, nivel) a partir de una
fuente oficial, versionada en el repo como semilla. Cada entidad debe
resolverse en una de estas categorías: Presidencia, ministerio, instituto
dependiente de un ministerio, o **fuera de alcance**. Los casos dudosos (por
ejemplo, entidades adscritas con régimen propio) se registran con su
justificación y los decide el líder. **[CONFIRMAR]** la fuente oficial y los
criterios de inclusión.

## 3. Decisiones del equipo

No hay consultas previstas con el profesor: el equipo decide.

| # | Tema | Decisión |
|---|---|---|
| D1 | La foto | La toma el equipo, del portal de datos abiertos de SERCOP (OCDS). El periodo lo fija el líder tras reconocer la fuente (volumen por año). |
| D2 | Herramientas | Libre elección del equipo. Se adopta la pila de la sección 6, con PostgreSQL y dbt. |
| D3 | Calendario | El de la sección 9, con cierre el 2027-01-22. |
| D4 | Idioma | Documentos en español; código y nombres técnicos en inglés. |
| D5 | Rigor | Nivel profesional, para que el trabajo pueda crecer hacia tesis (sección 1). |

## 4. Arquitectura

```
 Fuente           Foto cruda          Staging            Warehouse          Reportes
 ------           ----------          -------            ---------          --------
 SERCOP   -->   data/snapshots  -->  schema stg   -->   schema dw    -->   schema rpt  -->  Power BI
 (OCDS)         (inmutable,          (PostgreSQL,        (dimensiones y     (vistas por
                 con manifiesto       tipado, sin         hechos, claves     dashboard)
                 de checksums)        reglas de           sustitutas)
                                      negocio)
                         \______________ bitácora de cargas y filas rechazadas ______________/
                                         \_____ pruebas y reglas de calidad _____/
```

Principios:
1. **La foto es evidencia.** Nunca se modifica ni se sobrescribe. Todo lo
   derivado se puede regenerar desde ella.
2. **Dimensiones antes que hechos** en cada carga.
3. **Cada carga es idempotente.** Repetirla no duplica datos.
4. **Cada carga deja rastro:** cuántas filas entraron, cuántas se rechazaron y
   por qué.
5. **Los tableros leen solo vistas** del esquema `rpt`, nunca tablas crudas.
6. **No se versionan datasets completos ni secretos.** La foto vive fuera de
   git; en el repo solo van el manifiesto y fixtures mínimos y sintéticos.

### Modelo físico de carga

- **Batch:** carga inicial completa de la foto.
- **Incremental:** carga por particiones de fecha (por ejemplo mes a mes) con
  una marca de control (`batch_id`, fecha de corte). Permite demostrar la
  carga incremental aunque la fuente sea una foto fija.
- **Detección de cambios:** clave natural (`ocid`) más un hash del contenido.
- **Reconciliación:** tras cada carga, comparar conteos y sumas de monto entre
  foto, staging y DW. Es la "validación cruzada con fuentes originales" que
  pide la semana 4.

## 5. Modelo dimensional preliminar

> **Actualización:** para las entregas del curso manda el
> [ADR 0004](adr/0004-alcance-del-modelo.md): un hecho y de 4 a 5
> dimensiones, con la calidad y la bitácora en un esquema `audit`. Esta
> sección queda como visión ampliada.

La visión ampliada es una constelación de hechos que comparte dimensiones.
El [reconocimiento real](sources/reconocimiento.md) distingue la respuesta
resumida de búsqueda (`id`, `ocid`, `year`, `month`, `method`, `internal_type`,
`locality`, `region`, `suppliers`, `buyer`, `amount`, `date`, `title`,
`description`, `budget`) del JSON masivo anidado (`buyer`, `planning`,
`tender`, `awards`, `contracts`, `parties`). No son estructuras equivalentes.

Los nombres `amount`, `budget` y `suppliers` de las tablas preliminares que
siguen son conceptos por mapear. No se ha probado que sean columnas utilizables
directamente desde la descarga: esta distingue montos estimados, presupuestados,
adjudicados y contractuales, y puede contener varias adjudicaciones o contratos
por proceso. El mapeo y las medidas definitivas se resolverán en las fases 1 y 2.

### Hechos

| Hecho | Grano | Medidas | Notas |
|---|---|---|---|
| `fact_contract_process` | un proceso (`ocid`) por carga | `amount`, `budget`, `supplier_count` | `ocid` como dimensión degenerada. Aditivo en `amount`. |
| `fact_process_supplier` | proceso × proveedor | monto asignado, si existe | **[CONFIRMAR]** al observar la estructura de `suppliers`. |
| `fact_quality_check` | proceso × regla × carga | `passed` (0/1), `severity` | Es el diferencial del proyecto. |

### Dimensiones

| Dimensión | Origen | SCD | Atributos clave |
|---|---|---|---|
| `dim_entity` | `buyer` + clasificación | **Tipo 2** | nombre, tipo (Presidencia, ministerio, instituto dependiente), ministerio del que depende, sector |
| `dim_supplier` | `suppliers` | Tipo 1 | nombre, identificador **[CONFIRMAR]** |
| `dim_date` | `date`, `year`, `month` | estática | día, mes, trimestre, año |
| `dim_method` | `method`, `internal_type` | Tipo 1 | procedimiento de contratación |
| `dim_geography` | `locality`, `region` | Tipo 1 | localidad, región |
| `dim_quality_rule` | propia | Tipo 1 | nombre, dimensión de calidad, severidad |
| `dim_load_run` | propia | estática | carga, fecha, versión del código |

`dim_entity` usa SCD tipo 2 porque las entidades de la planta central pueden
cambiar de nombre, fusionarse o pasar de un ministerio a otro. La jerarquía
Presidencia > ministerio > instituto dependiente también permite análisis por
nivel. Se evalúa tipo 1 y tipo 2 como pide la
semana 2.

### Indicadores preliminares **[CONFIRMAR con el equipo]**

- Monto contratado por entidad, año y método.
- Número de procesos por método de contratación.
- Porcentaje de procesos sin proveedor y sin presupuesto.
- Desviación entre `amount` y `budget`.
- Concentración de proveedores por entidad.
- Completitud y consistencia por entidad (calidad de datos).

## 6. Pila tecnológica

| Capa | Elección propuesta | Justificación | Estado |
|---|---|---|---|
| Lenguaje | Python 3.13 | Experiencia previa del líder y ecosistema de datos | Propuesto |
| Gestión de entorno | `uv` | Entornos y dependencias reproducibles | Propuesto |
| Calidad de código | `ruff`, `pytest`, tipado estático | Convenciones y pruebas automáticas | Propuesto |
| Base de datos | PostgreSQL en Docker Compose | Compatible con Power BI | Decidido (D2) |
| Transformación y pruebas | dbt | Pruebas de integridad, documentación y linaje | Decidido (D2) |
| Foto cruda | Parquet o JSON con manifiesto de checksums | Reproducible y verificable | Propuesto |
| Orquestación | CLI primero; Airflow o Dagster después | Evitar complejidad prematura | Fase posterior |
| CI | GitHub Actions + `pre-commit` | Revisión automática en cada PR | Propuesto |
| Documentación | MkDocs Material | Sitio navegable y versionado | Propuesto |
| BI | Power BI Desktop | Lo exige el curso | Confirmado por el curso |

**Qué no se usa:** Kafka, Kubernetes, microservicios. La escalabilidad se
demuestra con diseño y con mediciones (tiempos de carga con volúmenes
crecientes), no con la cantidad de herramientas.

**DDL explícito frente a dbt puro.** La semana 3 pide sentencias
`CREATE TABLE` con claves, índices y nombres consistentes. Opciones: (A) DDL
explícito versionado más dbt para transformaciones y pruebas; (B) dbt con
contratos de modelo y restricciones, exportando el DDL como entregable.
**[CONFIRMAR]** con un spike corto en la fase 2. Recomendación inicial: A.

## 7. Estructura del repositorio

```
ec-gov-procurement-dw/
├─ README.md
├─ AGENTS.md                  # reglas para asistentes de IA (sección 12)
├─ CONTRIBUTING.md            # flujo de trabajo del equipo
├─ pyproject.toml
├─ compose.yaml               # PostgreSQL local
├─ Makefile                   # atajos: setup, test, load, lint
├─ .pre-commit-config.yaml
├─ .github/
│  ├─ workflows/ci.yml
│  ├─ PULL_REQUEST_TEMPLATE.md
│  ├─ ISSUE_TEMPLATE/
│  └─ CODEOWNERS
├─ docs/
│  ├─ requirements/           # semana 1: requerimientos y casos
│  ├─ design/                 # semana 2: modelo conceptual, diccionario
│  ├─ etl/                    # semana 3: flujo y decisiones de carga
│  ├─ validation/             # semana 4: pruebas, KPIs, bitácoras
│  ├─ dashboards/             # semana 5: propósito, KPIs, vistas
│  ├─ adr/                    # decisiones de arquitectura
│  └─ sources/                # observaciones de la fuente
├─ src/ec_gov_procurement_dw/
│  ├─ extract/                # cliente y escritura de la foto
│  ├─ snapshot/               # manifiesto y verificación
│  ├─ load/                   # staging, carga al DW, bitácora
│  ├─ quality/                # reglas de calidad
│  └─ cli.py
├─ warehouse/
│  ├─ ddl/                    # DDL físico (entregable de la semana 3)
│  └─ dbt/                    # modelos, pruebas, semillas de clasificación
├─ reports/powerbi/           # archivos del tablero y lista de vistas
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ fixtures/               # solo mínimos y sintéticos
└─ data/                      # ignorado por git; solo README y manifiestos
```

Límites entre módulos: `extract` y `snapshot` no conocen el DW; `load` no
conoce la API de la fuente; las reglas de `quality` no dependen de Power BI.

## 8. Flujo de trabajo del equipo

**Roles por capa (5 personas), con rotación a mitad del proyecto:**

1. Fuente y foto: extracción, manifiesto, reconocimiento de SERCOP.
2. Modelo dimensional y dbt.
3. Calidad, pruebas y CI.
4. Power BI y dashboards.
5. Requerimientos, documentación y coordinación.

**Reglas comunes (no dependen de ninguna herramienta de IA):**
- `main` protegida: solo se cambia mediante PR con al menos una revisión.
- El CI debe pasar antes de fusionar.
- Commits pequeños y descriptivos (Conventional Commits).
- Toda decisión de arquitectura va en un ADR.
- Cada tarea es un issue con criterio de aceptación.
- **Definición de hecho:** código con pruebas, documentación actualizada,
  CI en verde, revisión aprobada.

**Uso de asistentes de IA:** opcional y personal. Todo lo que genere un
asistente pasa por las mismas reglas que lo escrito a mano. Nadie debe
pegar secretos, credenciales ni datasets completos en prompts, logs o
documentación.

## 9. Mapa curso → entregables → repo (calendario del equipo, D3)

| Etapa HEFESTO | Entregables del curso | Ubicación | Ventana tentativa |
|---|---|---|---|
| Preparación | Repo, CI, reconocimiento de la fuente, decisión de la foto | raíz, `docs/sources` | 6 a 19 oct |
| 1. Requerimientos | Documento de requerimientos, guía de diseño inicial | `docs/requirements` | 20 oct a 2 nov |
| 2. Diseño conceptual y lógico | Diagrama estrella (PDF), diccionario de datos (Word) | `docs/design` | 3 a 23 nov |
| 3. Diseño físico y ETL | DDL, ETL, diagrama del flujo | `warehouse/ddl`, `src`, `docs/etl` | 24 nov a 14 dic |
| 4. Carga y pruebas | DW cargado, pruebas, bitácoras, KPIs validados | `docs/validation` | 15 dic a 8 ene |
| 5. Visualización y cierre | 3 reportes en Power BI, documentación, video | `reports/powerbi`, `docs/dashboards` | 9 a 22 ene |

Los tres tableros de la semana 5: Visión Ejecutiva, Análisis Operativo y
Detección de Problemas (alertas, rankings y evolución temporal). El tercero
usa `fact_quality_check`.

## 10. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La foto no existe o es difícil de obtener | Verificar en la preparación si hay descargas masivas por año; si no, extraer por API respetando límites. |
| La API limita las peticiones (observado: unas 60) | Foto única, ritmo conservador y reintentos con espera. |
| Sin lista oficial de entidades de la planta central | Construir la clasificación como semilla versionada y documentar la fuente. |
| `suppliers` sin estructura conocida | Observar registros reales antes de diseñar `dim_supplier`. |
| Dependencia de una persona en una capa | Rotación de roles y revisión cruzada de PRs. |
| Exceso de herramientas | Cada pieza nueva requiere una justificación en un ADR. |
| Cambio de alcance a mitad del proyecto | Todo cambio de alcance pasa por ADR y por el líder. |

## 11. Primeras tareas

1. Crear el repositorio, proteger `main` y añadir CI mínimo.
2. Redactar `AGENTS.md` y `CONTRIBUTING.md` a partir de este documento.
3. Escribir los ADR 0001 (alcance), 0002 (foto inmutable) y 0003 (pila).
4. Registrar las decisiones D1 a D5 en los ADR.
5. Reconocer la fuente: campos, volumen para un año, descargas masivas.
6. Redactar el documento de requerimientos (semana 1).

---

## 12. Prompt inicial para asistentes de IA (contenido sugerido de `AGENTS.md`)

```markdown
# Instrucciones del repositorio

Proyecto universitario de Data Warehouse (HEFESTO + Kimball) sobre contratación
pública de la planta central del Estado ecuatoriano: Presidencia de la
República, ministerios e institutos que dependen de los ministerios. Los GAD
y sus empresas están fuera de alcance. Es académico e independiente; no tiene
relación con SERCOP ni con ninguna entidad.

## Orden de lectura
README.md, docs/adr/, docs/design/ y la propuesta de arquitectura antes de
cambiar nada.

## Límites
- La foto de datos es evidencia: nunca se modifica ni se sobrescribe.
- `extract` y `snapshot` no conocen el DW; `load` no conoce la API de la
  fuente; `quality` no depende de Power BI.
- Carga siempre dimensiones antes que hechos. Toda carga es idempotente y
  deja bitácora de filas cargadas y rechazadas.
- Los tableros solo leen vistas del esquema `rpt`.
- No inventes campos, endpoints ni comportamientos de la fuente. Usa solo lo
  observado y documentado en docs/sources/ o fixtures aprobados.

## Seguridad y datos
- No incluyas secretos, credenciales ni datasets completos en código, prompts,
  logs, pruebas ni documentación.
- Usa fixtures mínimos y sintéticos.

## Cambios que requieren aprobación del líder
Nuevas dependencias, nueva infraestructura o servicios, cambios de alcance o
de arquitectura, y cualquier decisión marcada como [CONFIRMAR].

## Verificación
Ejecuta las pruebas y el linter relevantes después de cada cambio y reporta el
resultado real, incluidos los fallos.

## Convenciones
Código y nombres técnicos en inglés. Documentos de entrega en español.
Commits con Conventional Commits.
```

## 13. Nombre del repositorio

**Recomendado:** `ec-gov-procurement-dw`

- Descriptivo: país, sector, dominio y tipo de sistema.
- No incluye "SERCOP", para no sugerir afiliación.
- "gov" cubre la planta central; el nombre no sugiere GAD.
- Alternativa si el alcance crece más allá de contratación: `ec-central-gov-dw`.

Antes de crearlo, verificar que el nombre esté libre en la cuenta u
organización de GitHub elegida.
