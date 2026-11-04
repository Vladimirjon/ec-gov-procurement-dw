# data/

Carpeta local para la foto (snapshot) de datos y sus derivados. **Su contenido
está ignorado por git**; solo se versiona este archivo.

- La foto es evidencia inmutable: no se modifica ni se sobrescribe
  (ver [ADR 0002](../docs/adr/0002-datos-crudos-versionados.md)).
- Los datasets y archivos originales se guardan aquí **localmente**; nunca se
  suben a Git, ni se copian completos a documentación, logs o prompts.
- `reconnaissance/` contiene las descargas utilizadas para conocer la fuente.
  Conserva el original y su hash; una descarga nueva usa otra carpeta.
- Los resúmenes de evidencia revisables, sin registros ni identificadores
  reales, se versionan en `docs/sources/`. El resumen de inspección no sustituye
  el manifiesto de una foto definitiva.
- Los fixtures de prueba (mínimos y sintéticos) van en `tests/fixtures/`.

La foto la toma el equipo del portal de datos abiertos de SERCOP (D1).
**[PENDIENTE]** Periodo, formato (Parquet o JSON) y ubicación del manifiesto
de checksums dentro del repositorio. El periodo se decide en el issue #15
(fase 1) y la foto formal se prepara al inicio de la fase 2, según el plan.
