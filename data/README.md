# data/

Carpeta local para la foto (snapshot) de datos y sus derivados. **Su contenido
está ignorado por git**; solo se versiona este archivo.

- La foto es evidencia inmutable: no se modifica ni se sobrescribe
  (ver [ADR 0002](../docs/adr/0002-foto-inmutable.md)).
- No se suben aquí datasets completos, datos reales ni secretos.
- Los fixtures de prueba (mínimos y sintéticos) van en `tests/fixtures/`.

**[PENDIENTE]** Origen y periodo de la foto (D1), formato (Parquet o JSON) y
ubicación del manifiesto de checksums dentro del repositorio.
