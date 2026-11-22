/* Adjudicaciones_SERCOP: CSV del portal SERCOP, derivados en data/derivados.
Patrón: sercop-portal-csv-AAAA-sello/awards_AAAA.csv.
Una fila representa una adjudicación de un release.
Descargas: 21/11/2026; sellos: 2021-20261121-145729, 2022-20261121-145742, 2023-20261121-145820, 2024-20261121-150856, 2025-20261121-141748.
Fuente: docs/h2/evidencia/descargas-sercop.csv (type=csv, SHA-256 registrado).
*/
let
    Archivos = {
        "sercop-portal-csv-2021-20261121-145729/awards_2021.csv",
        "sercop-portal-csv-2022-20261121-145742/awards_2022.csv",
        "sercop-portal-csv-2023-20261121-145820/awards_2023.csv",
        "sercop-portal-csv-2024-20261121-150856/awards_2024.csv",
        "sercop-portal-csv-2025-20261121-141748/awards_2025.csv"
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
