# Cómo contribuir

Guía de trabajo del equipo (5 personas). Se basa en la sección 8 de la
[propuesta de arquitectura](docs/PROPUESTA.md).

> **Estado:** `main` está protegida y hay plantillas de PR e issues. El CI se
> implementará cuando el repositorio tenga código y pruebas que verificar.
> Hasta entonces, la regla "el CI debe pasar" se sustituye por una
> verificación manual descrita en el PR.

## Roles por capa

Cada capa tiene una persona responsable. Los roles rotan a mitad del proyecto
para que nadie sea el único que conoce una capa.

| # | Capa | Responsabilidades |
|---|---|---|
| 1 | Fuente y foto | Extracción, manifiesto, reconocimiento de la fuente |
| 2 | Modelo dimensional | Modelo dimensional y transformaciones (dbt) |
| 3 | Calidad | Reglas de calidad, pruebas y CI |
| 4 | Visualización | Power BI y tableros |
| 5 | Coordinación | Requerimientos, documentación y coordinación |

**[PENDIENTE]** Asignación de personas a cada rol y fecha de rotación.

## Reglas comunes

Aplican a todo el código y la documentación, con o sin asistentes de IA.

- `main` está protegida: solo cambia mediante PR aprobado por el líder (ver
  [Protección de `main`](#protección-de-main)).
- El CI debe pasar antes de fusionar (cuando exista).
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
   línea el issue se cierra solo al fusionar. Si aún no está listo, ábrelo
   como borrador (draft).
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

Cuando exista CI, se añadirá como verificación obligatoria antes de fusionar.

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

## Uso de asistentes de IA

Opcional y personal. Todo lo que genere un asistente pasa por las mismas
reglas que lo escrito a mano: revisión, pruebas y CI. Nadie debe pegar
secretos, credenciales ni datasets completos en prompts, logs o
documentación. Los asistentes deben seguir [AGENTS.md](AGENTS.md).
