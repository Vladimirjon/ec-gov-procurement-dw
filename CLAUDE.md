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
- `src/ec_gov_procurement_dw/{extract,load,quality,snapshot}`, `tests/`,
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

## Comandos que existen hoy
```bash
python -I scripts/inspect_sercop_zip.py RUTA.zip --output docs/sources/NUEVO.json
python -I scripts/profile_sercop_fields.py RUTA.zip --output docs/sources/NUEVO.json
```
La salida no sobrescribe archivos (usa un nombre nuevo cada vez). No hay todavía
pruebas, lint ni CI en `main`: llegan con el issue #43. Hasta entonces dilo
explícitamente en lugar de dar un cambio por verificado.

## Hito 1 (convenciones ya decididas)
- Equipo: **Trazabilidad Pública**. Sector: gobierno central. Fecha en formato
  `dd/mm/yy`, la de la entrega.
- Archivo: `Hito1_BravoFreireGuajanPasquelTorres.pdf` (apellidos en orden
  alfabético), máximo 6 páginas sin contar anexos.
- La revisión es el lunes 9/11/2026 en el aula; el equipo cierra el domingo 8/11.
