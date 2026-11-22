/* Entidades_MDEP: hoja CATÁLOGO del catálogo de instituciones MDEP.
Origen: data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx.
Grano de los registros de datos: una entidad operativa desconcentrada (entidad, EOD).
Descarga: 21/11/2026, según docs/h2/evidencia/descargas-entidades.csv.
La hoja también contiene títulos, encabezados y notas; no se eliminan en H2.
*/
let
    Libro = Excel.Workbook(File.Contents(RutaDatosCrudos & "/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx"), null, true),
    Hoja = Libro{[Item="CATÁLOGO", Kind="Sheet"]}[Data]
in
    Hoja
