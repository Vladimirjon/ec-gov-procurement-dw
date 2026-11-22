// Consulta intermedia: Habilitar carga desactivado. Fuente F1, CSV del portal usados en H2.
// Q-02: correctedValue_amount y enteredValue_amount 100 % vacías, descartadas en la selección.
// Q-03: fechas de etapa opcionales descartadas; la fecha de negocio está en Procesos_SERCOP.
// Q-09: no se ajusta el importe para igualar el informe institucional; véase la nota metodológica.
let
    Archivos = {
        [Anio=2021, Ruta="sercop-portal-csv-2021-20261121-145729/awards_2021.csv"],
        [Anio=2022, Ruta="sercop-portal-csv-2022-20261121-145742/awards_2022.csv"],
        [Anio=2023, Ruta="sercop-portal-csv-2023-20261121-145820/awards_2023.csv"],
        [Anio=2024, Ruta="sercop-portal-csv-2024-20261121-150856/awards_2024.csv"],
        [Anio=2025, Ruta="sercop-portal-csv-2025-20261121-141748/awards_2025.csv"]
    },
    #"CSV anuales UTF-8 con saltos entre comillas" = List.Transform(Archivos, (Archivo) =>
        Table.AddColumn(
            Table.PromoteHeaders(
                Csv.Document(File.Contents(RutaDerivados & "/" & Archivo[Ruta]),
                    [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
                [PromoteAllScalars=true]
            ),
            "AnioProceso", each Archivo[Anio], Int64.Type
        )
    ),
    #"Cinco años anexados" = Table.Combine(#"CSV anuales UTF-8 con saltos entre comillas"),
    #"Campos de adjudicación sin importes vacíos de oferta" = Table.SelectColumns(
        #"Cinco años anexados", {"ocid", "id", "AnioProceso", "amount", "currency"}
    ),
    #"Importe adjudicado decimal anulable" = Table.TransformColumns(
        #"Campos de adjudicación sin importes vacíos de oferta",
        {{"amount", each if _ = null or Text.Trim(_) = "" then null else Decimal.From(_, "en-US"),
          type nullable number}}
    ),
    #"Unicidad de adjudicación verificada" =
        if Table.RowCount(Table.Distinct(#"Importe adjudicado decimal anulable", {"ocid", "id"}))
            <> Table.RowCount(#"Importe adjudicado decimal anulable")
        then error "Q-06: claves de adjudicación duplicadas; detener y registrar el conteo, sin borrar filas."
        else #"Importe adjudicado decimal anulable",
    #"Moneda solo USD verificada" = Table.SelectRows(
        #"Unicidad de adjudicación verificada", each [currency] = "USD" or ([amount] = null and ([currency] = null or [currency] = ""))
    ),
    #"Importes negativos excluidos" = Table.SelectRows(
        #"Moneda solo USD verificada", each [amount] = null or [amount] >= 0
    ),
    // List.Sum ignora nulos y devuelve null si todos son null (Microsoft Learn, list-sum).
    // La suma antes/después y las exclusiones se contrastan con controles-esperados.csv.
    #"Adjudicaciones agrupadas por ocid (suma, conteo)" = Table.Group(
        #"Importes negativos excluidos", {"ocid"},
        {{"MontoAdjudicado", each List.Sum([amount], Precision.Decimal), type nullable number},
         {"NumAdjudicaciones", each Table.RowCount(_), Int64.Type}}
    )
in
    #"Adjudicaciones agrupadas por ocid (suma, conteo)"
