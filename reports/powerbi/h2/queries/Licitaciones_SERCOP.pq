/* Licitaciones_SERCOP: CSV del portal SERCOP, derivados en data/derivados.
Patrón: sercop-portal-csv-AAAA-sello/tender_AAAA.csv.
Una fila representa la licitación de un release.
Descargas: 21/11/2026; sellos: 2021-20261121-145729, 2022-20261121-145742, 2023-20261121-145820, 2024-20261121-150856, 2025-20261121-141748.
Fuente: docs/h2/evidencia/descargas-sercop.csv (type=csv, SHA-256 registrado).
*/
let
    Archivos = {
        "sercop-portal-csv-2021-20261121-145729/tender_2021.csv",
        "sercop-portal-csv-2022-20261121-145742/tender_2022.csv",
        "sercop-portal-csv-2023-20261121-145820/tender_2023.csv",
        "sercop-portal-csv-2024-20261121-150856/tender_2024.csv",
        "sercop-portal-csv-2025-20261121-141748/tender_2025.csv"
    },
    Tablas = List.Transform(Archivos, each
        Table.PromoteHeaders(
            Csv.Document(File.Contents(RutaDerivados & "/" & _),
                [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            [PromoteAllScalars=true]
        )
    ),
    Combinadas = Table.Combine(Tablas)
in
    Combinadas
