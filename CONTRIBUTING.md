# Cómo contribuir

Guía de trabajo del equipo (5 personas). Se basa en la sección 8 de la
[propuesta de arquitectura](docs/PROPUESTA.md).

> **Estado:** la protección de `main`, el CI y las plantillas de PR e issues
> todavía no están configurados. El CI se implementará cuando el repositorio
> tenga código y pruebas que verificar. Hasta entonces, las reglas se cumplen
> por acuerdo del equipo y en la revisión de cada PR, y la regla "el CI debe
> pasar" se sustituye por una verificación manual descrita en el PR.

## Roles por capa

Cada capa tiene una persona responsable. Los roles rotan a mitad del proyecto
para que nadie sea el único que conoce una capa.

| # | Capa | Responsabilidades |
|---|---|---|
| 1 | Fuente y foto | Extracción, manifiesto, reconocimiento de la fuente |
| 2 | Modelo dimensional | Modelo dimensional y transformaciones (dbt, sujeto a D2) |
| 3 | Calidad | Reglas de calidad, pruebas y CI |
| 4 | Visualización | Power BI y tableros |
| 5 | Coordinación | Requerimientos, documentación y coordinación |

**[PENDIENTE]** Asignación de personas a cada rol y fecha de rotación.

## Reglas comunes

Aplican a todo el código y la documentación, con o sin asistentes de IA.

- `main` está protegida: solo cambia mediante PR con al menos una revisión
  aprobada.
- El CI debe pasar antes de fusionar.
- Commits pequeños y descriptivos con
  [Conventional Commits](https://www.conventionalcommits.org/).
- Toda decisión de arquitectura se registra en un ADR (`docs/adr/`).
- Cada tarea es un issue con criterio de aceptación.
- Los cambios de alcance pasan por un ADR y por el líder.
- Cada herramienta nueva necesita una justificación en un ADR.

## Flujo de trabajo

1. **Issue.** Describe la tarea y su criterio de aceptación.
2. **Rama.** Crea una rama desde `main` para ese issue.
3. **Commits.** Pequeños, con Conventional Commits. Ejemplos:
   - `feat(load): ...` para funcionalidad nueva
   - `fix(quality): ...` para corrección de errores
   - `docs(adr): ...` para documentación
   - `test(snapshot): ...` para pruebas
   - `chore: ...` para mantenimiento
4. **PR.** Enlaza el issue, explica qué cambia y cómo se verificó.
5. **Revisión.** Al menos una persona distinta del autor; de preferencia de
   otra capa (revisión cruzada).
6. **Fusión.** Solo con CI en verde y revisión aprobada.

**[PENDIENTE]** Convención de nombres de ramas y estrategia de fusión
(merge, squash o rebase).

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
- Lo que dependa del profesor o de una verificación se marca como
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
