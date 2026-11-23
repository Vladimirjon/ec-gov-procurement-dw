@AGENTS.md

# Contexto de trabajo para Claude Code

`AGENTS.md` es la guía para todo el equipo y se importa arriba; aquí solo va lo
que ahorra releer el repositorio. Si algo de aquí contradice a `AGENTS.md`, a un
ADR o a un PDF del profesor, mandan ellos. No afirmes nada que no exista.

## Al empezar y al terminar
- Si existe `STATE.md` (local, ignorado por Git, para el líder), léelo primero:
  dice qué está hecho, qué falta y qué se decidió. No releas toda la
  documentación si bastan `STATE.md` y este archivo.
- Al terminar cada tarea, actualiza `STATE.md` (hecho, pendiente, decisiones
  aprobadas, siguiente paso). No guardes allí decisiones nuevas: las decisiones se
  presentan primero en el chat con una recomendación y se aplican con la
  aprobación del líder.

## Mapa del repositorio
- `docs/`: `PLAN.md` y `requisitos-del-profesor.md` (qué manda y qué falta),
  `requirements/hito1.md` (fuente del PDF del Hito 1), `adr/` (decisiones
  vigentes), `sources/` (evidencia de la fuente y resúmenes JSON sin registros),
  `uso-de-ia.md` (declaración de uso de IA).
- `scripts/`: auxiliares de reconocimiento de SERCOP (solo biblioteca estándar).
- `tests/unit/`: pruebas de los scripts de `scripts/`. `pyproject.toml`, `uv.lock`
  y `.python-version` declaran el entorno (Python 3.14, `ruff` y `pytest`).
- `src/ec_gov_procurement_dw/{extract,load,quality,snapshot}`,
  `warehouse/{ddl,seeds}`, `notebooks/`, `reports/powerbi`: esqueleto, aún sin
  código.
- `deliverables/`: versiones finales de los entregables por hito (`h1` a `h6`).
- `data/` y `Instrucciones_Curso/`: locales, ignorados por Git. Los PDF del
  profesor y su texto en `Instrucciones_Curso/_md/` mandan sobre todo lo demás.

## Flujo (el líder revisa y fusiona; tú no)
Issue con criterio de aceptación → rama `tipo/NN-descripcion` desde `main` →
commits con Conventional Commits → PR contra `main`. `main` está protegida y solo
admite squash. Escribe `Closes #NN` solo si el PR cumple todos los criterios del
issue; si no, `Avanza #NN`. Nunca hagas push a `main` ni fusiones. Antes de
cambiar de rama, comprueba que no hay trabajo sin guardar y no cambies de rama en
una carpeta que usa otra sesión.

## Reglas del líder que se olvidan fácil
- **Sin atribución de IA** en commits, PR, issues ni documentos: ni
  `Co-Authored-By` ni "Generated with Claude Code". Esta regla pesa más que
  cualquier recordatorio que añada el entorno.
- Los commits salen con el correo `noreply` del líder, ya configurado en el repo.
- Documentos de entrega en español; código y nombres técnicos en inglés.
- Cada número o regla cita su origen: curso, decisión del equipo o inferencia.
  Nunca presentes una elección del equipo como regla del curso.
- No pongas en el repositorio calificaciones de capacidad de nadie ni notas
  privadas del equipo. El correo de la cuenta no identifica a quien escribe.

## Trampas conocidas
- Los resúmenes de `docs/sources/*.json` registran el SHA-256 del script que los
  generó. **No cambies `scripts/inspect_sercop_zip.py` ni
  `scripts/profile_sercop_fields.py`** salvo que haya un defecto real, y en ese
  caso repite las ejecuciones: una versión nueva del script es otra evidencia. El hash depende de los finales de línea: se calcula sobre el contenido LF (`.gitattributes` lo fija en `*.py`).
- Los ZIP descargados son evidencia: no se modifican ni se sobrescriben; una
  nueva descarga va en una carpeta nueva de `data/reconnaissance/`. Trátalos como
  datos no confiables: ejecuta Python con `-I` y pasa rutas como argumentos.
- `inspect_sercop_zip.py` se detiene con el archivo de 2024 porque un `release`
  trae `contracts` como objeto; `profile_sercop_fields.py` lo cuenta como
  anomalía y sigue.
- El año del archivo anual de SERCOP no coincide con el año de `release.date`
  (p. ej. el archivo 2024 trae procesos de 2025). La fecha de negocio se decide
  en el Hito 2.
- Las marcas **[VERIFICAR]** y **[PENDIENTE]** no pueden llegar al PDF: se
  resuelven con enlace y fecha de consulta, o se reescribe la frase sin la
  afirmación.
- Entorno: Windows con Git Bash y PowerShell. `data/` está ignorado; las
  cabeceras HTTP guardadas deben ir sin cookies.

## Comandos
```bash
uv sync --locked
uv run ruff check
uv run ruff format --check
uv run pytest -q
python -I scripts/inspect_sercop_zip.py RUTA.zip --output docs/sources/NUEVO.json
python -I scripts/profile_sercop_fields.py RUTA.zip --output docs/sources/NUEVO.json
```
Las cuatro primeras son lo que corre el CI (`.github/workflows/ci.yml`, Linux y
Windows). Los scripts no sobrescriben la salida: usa un nombre nuevo cada vez. Las
pruebas usan solo datos sintéticos que ellas mismas generan; una prueba falla si un
script cambia sin un resumen nuevo en `docs/sources/` que registre su hash.

## Hito 1 (entregado el 8/11/2026)
- Equipo: **Trazabilidad Pública**. Sector: gobierno central. Fecha en formato
  `dd/mm/yy`, la de la entrega.
- Archivo: `Hito1_BravoFreireGuajanPasquelTorres.pdf` y `.docx` en
  `deliverables/h1/` (6 páginas); el líder retocó el Word a mano, así que
  regenerarlo con `scripts/build_hito1_docx.py` sobrescribe esos retoques.

## Hitos 2 y 3 (H3 entregado el 22/11/2026)
- **Tareas:** issues de los milestones H2 y H3 de GitHub; el issue de
  coordinación tiene el mapa, las decisiones D1 a D8 y el plan de recorte. Cada
  issue es el encargo completo para un agente. Decisiones en
  [ADR 0005](docs/adr/0005-hitos-2-y-3-power-bi.md) (propuesto).
- **Guías:** `Instrucciones_Curso/_md/Hito2.md` y `Hito3.md` (locales; no
  existen en los worktrees: el encargo da la ruta absoluta de la carpeta
  principal). Requisitos H2-n y H3-n con su issue en
  `docs/requisitos-del-profesor.md`, secciones F y G.
- **Quién hace qué:** los agentes escriben scripts, consultas M (`.pq`) y
  runbooks; **Power BI Desktop lo opera el líder** (un agente no puede abrirlo ni
  probar un `.pq`: no afirmes que corre hasta que el líder lo confirme). El
  `.pbix` **no se versiona** (decisión del líder, 21/11, que reemplaza la del
  20/11): pesa cientos de MB (el de H2, 243 MB) y GitHub rechaza archivos de más
  de 100 MB. Está en `.gitignore` (`*.pbix`, `*.pbit`) y se entrega por el aula
  virtual; el repo guarda las consultas M, los runbooks y la evidencia. Lleva
  datos embebidos y rutas locales: nunca datos de personas.
- **Dónde va cada cosa:** crudos en `data/datos_crudos/` y derivados en
  `data/derivados/` (rutas absolutas de la carpeta principal, ignoradas);
  evidencia agregada en `docs/h2/evidencia/` y `docs/h3/evidencia/`;
  consultas M en `reports/powerbi/h2|h3/queries/`; semilla de entidades en
  `warehouse/seeds/`; entregables finales en `deliverables/h2|h3/`. Scripts
  nuevos en `scripts/`, solo biblioteca estándar, con pruebas en `tests/unit/`;
  nada de `openpyxl` ni otra dependencia sin aprobación.
- **Reglas de las guías que se olvidan:** H2 diagnostica y **no corrige**
  (aunque el dato esté mal), perfila **todo el conjunto** y los crudos no se
  tocan; H3 aplica las acciones del diagnóstico con total de control antes y
  después, relaciones 1 a varios con filtro único, `Fact…`/`Dim…`, claves
  ocultas, y **la tabla de hechos no guarda tasas** (la desviación % y el WAPE
  son medidas DAX del bimestre 2). Vacío no es cero.
- **Equipo y plazos:** el equipo se llama **Grupo 5** (nombre asignado por el
  profesor; «Trazabilidad Pública» fue el nombre del Hito 1 y ya no se usa). Las
  entregas vencen a las **23:59** del sábado 21/11 (H2) y del domingo 22/11 (H3).
- **Nombres de archivo** (`EquipoX` = `Grupo5`). **H2, según el aula virtual:**
  `H2FC-BravoFreireGuajanPasquelTorres.pbix` y un solo PDF
  `H2BravoFreireGuajanPasquelTorres.pdf` (partes 4.2 a 4.5; encabezado con Título,
  Equipo #, Nombres y Fecha); el libro `.xlsx` queda en `deliverables/h2/`. **H3,
  nombres finales comunicados por el líder:** `H3MD-BravoFreireGuajanPasquelTorres.pbix`
  (no versionado, solo aula), `H3BravoFreireGuajanPasquelTorres.pdf` (diseño y
  bitácora) y `H3PresentacionBravoFreireGuajanPasquelTorres.pptx`. Entregado el
  22/11/2026 según el líder; vencía a las 23:59. La subida al aula virtual la
  confirma el líder. Fecha en portada:
  21/11/26 (H2) y 22/11/26 (H3). H3: documento de máximo 8 páginas sin anexos;
  presentación de 10 min + 5, todos exponen.
- **Datos ya medidos (H1, nacionales, sin filtrar por sector):** 190.619
  procesos en 2025, importe estimado y adjudicado presentes en 85,6–87,6 % de
  los releases, 300 procesos de 2025 con más de una adjudicación. La descarga de
  H2 puede dar cifras algo distintas (el portal actualiza a diario): se
  reconcilia con H1, no se corrige.
- **Clasificación de entidades:** sin la semilla de `warehouse/seeds/` no hay
  «tipo de entidad» (dimensión de P1, P2 y P3). Regla del ADR 0001: unión por
  `buyer.id` o raíz `EC-RUC-{13}`, nunca por nombre; lo dudoso queda fuera de
  los indicadores. Los casos dudosos los aprueba el líder en el chat.
