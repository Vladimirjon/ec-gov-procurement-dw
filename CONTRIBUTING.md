# Cómo contribuir

Guía de trabajo del equipo (5 personas). Se basa en el
[plan por hitos](docs/PLAN.md).

> **Estado:** `main` está protegida y hay plantillas de PR e issues. El CI
> (`.github/workflows/ci.yml`) corre lint y pruebas en Linux y Windows en cada
> PR y en cada push a `main`. Todavía no está marcado como verificación
> obligatoria en la protección de `main`: hasta que el líder lo active, revisa
> que el CI esté en verde antes de pedir la fusión. Lo que el CI no cubre se
> verifica a mano y se describe en el PR.

## Roles y rotación

El trabajo se divide en cinco carriles: Ingesta y fuente, Modelado y
almacenamiento, Transformación, Calidad y operación, y Negocio y servicio.
El líder lleva fijo el carril de Ingesta y fuente; el resto del equipo
cambia de carril en cada fase.

Las tareas de cada persona por fase, las fechas internas y la matriz de
rotación están en [docs/PLAN.md](docs/PLAN.md).

## Reglas comunes

Aplican a todo el código y la documentación, con o sin asistentes de IA.

- `main` está protegida: solo cambia mediante PR aprobado por el líder (ver
  [Protección de `main`](#protección-de-main)).
- El CI debe pasar antes de fusionar.
- Commits pequeños y descriptivos con
  [Conventional Commits](https://www.conventionalcommits.org/).
- Toda decisión de arquitectura se registra en un ADR (`docs/adr/`).
- Cada tarea es un issue con criterio de aceptación.
- Los cambios de alcance pasan por un ADR y por el líder.
- Cada herramienta nueva necesita una justificación en un ADR.

## Flujo de trabajo

1. **Issue.** Ábrelo con la plantilla "Tarea": objetivo y criterio de
   aceptación.
2. **Rama.** Desde `main` actualizada, con el formato
   `tipo/NN-descripcion-corta`, donde `NN` es el número del issue:

   ```bash
   git switch main
   git pull
   git switch -c docs/12-documento-requerimientos
   ```

3. **Commits.** Pequeños, con Conventional Commits. Tipos:
   - `feat(load): ...` para funcionalidad nueva
   - `fix(quality): ...` para corrección de errores
   - `docs(adr): ...` para documentación
   - `test(snapshot): ...` para pruebas
   - `refactor: ...` para cambios sin efecto funcional
   - `chore: ...` para mantenimiento
4. **PR.** Publica la rama y abre el PR contra `main`. El título sigue
   Conventional Commits, porque será el mensaje del commit final. Completa la
   plantilla: issue que cierra y cómo se verificó. Escribe `Closes #NN` en
   inglés: GitHub solo reconoce `Closes`, `Fixes` o `Resolves`, y con esa
   línea el issue se cierra solo al fusionar. Reservar `Closes #NN` para un PR
   que efectivamente cumpla todos los criterios del issue. Para un avance
   parcial, usar `Relacionado con #NN` y enumerar los criterios pendientes.
   Un PR de avance puede revisarse e integrarse si su alcance declarado está
   completo y verificado, aunque el issue siga abierto. Usar borrador (draft)
   cuando el propio PR todavía no esté listo para revisión. La integración de
   un avance no reduce los criterios pendientes ni aprueba decisiones de
   arquitectura fuera de su alcance. Un issue abierto no significa que su
   evidencia local no exista: el estado se actualiza al publicar el avance.
5. **Revisión.** El líder (@Vladimirjon) revisa y aprueba todos los PR.
   Cualquier integrante puede comentar; la revisión cruzada de otra capa es
   bienvenida, pero no reemplaza la aprobación del líder. Todas las
   conversaciones deben quedar resueltas.
6. **Correcciones.** Si haces push después de la aprobación, la aprobación se
   descarta y el PR debe aprobarse de nuevo.
7. **Fusión.** Solo con squash merge: el PR entra a `main` como un único
   commit. GitHub borra la rama remota automáticamente al fusionar.
8. **Limpieza local.**

   ```bash
   git switch main
   git pull
   git fetch --prune
   git branch -d docs/12-documento-requerimientos
   ```

## Verificación local

El entorno se gestiona con [`uv`](https://docs.astral.sh/uv/) (versión 0.13.4
o posterior; `pyproject.toml` lo exige). Desde la raíz del repositorio, en
PowerShell o Git Bash, ejecuta los mismos pasos que el CI:

```bash
uv sync --locked          # crea .venv con Python 3.14 y las versiones de uv.lock
uv run ruff check         # lint
uv run ruff format --check
uv run pytest             # pruebas de tests/
```

Si falta Python 3.14, `uv sync` lo descarga. `--locked` falla si `uv.lock` no
corresponde a `pyproject.toml`: no lo regeneres para que pase. Una dependencia
nueva (`uv add`) cambia los dos archivos y necesita la aprobación del líder.
Para corregir el formato de tus archivos usa `uv run ruff format`; los dos
scripts de evidencia de `scripts/` quedan excluidos a propósito.

## Protección de `main`

Configurada en GitHub; no depende de la buena voluntad de nadie.

| Regla | Efecto |
|---|---|
| PR obligatorio | Nadie del equipo puede hacer push directo a `main`. |
| 1 aprobación de code owner | `.github/CODEOWNERS` asigna todo al líder; sin su aprobación el PR no se fusiona. |
| Aprobación descartada al hacer push | Un cambio posterior a la aprobación exige revisarlo otra vez. |
| Aprobación del último push | Quien hizo el último push no puede ser quien aprueba. |
| Conversaciones resueltas | No se fusiona con comentarios abiertos. |
| Historial lineal | Sin commits de merge en `main`. |
| Sin force push ni borrado | `main` no se reescribe ni se elimina. |
| Solo squash merge | Merge commit y rebase merge están desactivados en el repositorio. |
| Borrado automático de ramas | La rama del PR se elimina al fusionar. |

**Excepción del administrador.** El líder, como dueño del repositorio, puede
saltarse estas reglas. Lo usa solo para fusionar sus propios PR (GitHub no
permite aprobar un PR propio) y nunca para hacer push directo a `main`. En
sus PR pide igual la revisión de un integrante.

El CI todavía no figura como verificación obligatoria; el líder lo añadirá a
estas reglas.

## Definición de hecho

Una tarea está terminada cuando tiene:

- código con pruebas;
- documentación actualizada;
- CI en verde;
- revisión aprobada.

## Decisiones de arquitectura (ADR)

- Un archivo por decisión: `docs/adr/NNNN-titulo-corto.md`, numeración
  correlativa.
- Estados: Propuesto, Aceptado, Reemplazado por ADR NNNN, Descartado.
- Lo que dependa de una verificación o de la aprobación del líder se marca como
  **[PENDIENTE]** y no se trata como decisión.
- Un ADR aceptado no se reescribe; si cambia la decisión, se crea uno nuevo
  que lo reemplace.

## Datos y secretos

- La foto de datos vive fuera de git (`data/` está ignorado).
- Nunca se suben secretos, credenciales ni datasets completos.
- Los fixtures de prueba son mínimos y sintéticos (`tests/fixtures/`).
- Los CSV de cabeceras HTTP y resúmenes de inspección sin registros reales se
  versionan en `docs/sources/`, con su finalidad y limitaciones documentadas.
  No son fixtures de prueba ni entradas del ETL.
- Cada nueva ejecución de observación genera un archivo de evidencia nuevo.
  Las capturas anteriores no se corrigen, fusionan ni sobrescriben para adaptar
  su esquema; una versión histórica se conserva con su advertencia de uso.
- No ignorar globalmente `*.csv`, `*.json` o `*.zip`: esos formatos también se
  usan para metadatos, semillas y entregables. Los datasets originales van en
  `data/`; comprobar `git status` y `git check-ignore` antes de prepararlos.

## Uso de asistentes de IA

Opcional y personal. Todo lo que genere un asistente pasa por las mismas
reglas que lo escrito a mano: revisión, pruebas y CI. Nadie debe pegar
secretos, credenciales ni datasets completos en prompts, logs o
documentación. Los asistentes deben seguir [AGENTS.md](AGENTS.md).
