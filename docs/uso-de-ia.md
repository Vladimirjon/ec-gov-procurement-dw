# Registro del uso de asistentes de IA

La guía del proyecto (sección 10) exige declarar en el informe el uso de IA:
**qué se pidió y cómo se verificó**. Cada integrante anota aquí sus usos al
terminar cada tarea. No se pegan secretos, credenciales ni datasets completos.

| Fecha | Hito | Persona | Qué se pidió | Cómo se verificó el resultado |
|---|---|---|---|---|
| 2026-11-03 | H1 | Vladimirjon | Lectura de las guías del profesor, borrador del perfil y de la matriz de preguntas, reorganización de la documentación | Se contrastó con los PDF página por página y se abrieron las fuentes citadas; los datos marcados [VERIFICAR] siguen sin verificar |
| 2026-11-03 | H1 | Vladimirjon | Descarga de los ZIP anuales 2021 y 2024 de SERCOP, inspección con los scripts del repositorio, un script nuevo que cuenta campos sin emitir registros, lectura de la licencia en la política de SERCOP y redacción del resultado en `reconocimiento.md` y `hito1.md` | Tamaño recibido contra `Content-Length` y SHA-256 registrado; conteos de 2021 y 2025 contra los del script ya existente (coinciden); anomalía de 2024 reproducida con una segunda lectura; enlace de la licencia abierto (HTTP 200) y texto de la página 8 de la política leído; porcentajes recalculados aparte |
| 2026-11-03 | H1 | Vladimirjon | Entorno con `uv` (`pyproject.toml`, `uv.lock`, Python 3.14), configuración de `ruff` y `pytest`, pruebas con ZIP sintéticos de `inspect_sercop_zip.py` y `profile_sercop_fields.py`, CI en Linux y Windows, Dependabot y actualización de `AGENTS.md`, `CONTRIBUTING.md`, `README.md` y ADR 0003 (issue #43) | `uv sync --locked`, `uv lock --check`, `ruff check`, `ruff format --check` y `pytest` ejecutados en local (96 pruebas pasan; 2 `xfail` estrictas documentan un defecto de los scripts); se rompió a propósito una prueba, una regla de lint, el formato, un script de evidencia y una versión fijada, y cada verificación falló como debía antes de revertir; SHA-256 de los dos scripts igual antes y después; SHA de las acciones y checksums de uv consultados en GitHub; `uv audit` sin vulnerabilidades conocidas; CI ejecutado en el PR |
