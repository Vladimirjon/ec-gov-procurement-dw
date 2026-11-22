// Consulta intermedia: Habilitar carga desactivado. Fuente F1, CSV del portal usados en H2.
// Q-01 y Q-12: los 109.793 importes vacíos quedan null; no se recupera el 0 del JSON de 2025.
// Q-11: QuoteStyle.Csv conserva los registros con saltos entre comillas.
// description no se conserva: no interviene en las dimensiones ni en el hecho.
// Q-08: el comprador se obtiene de Procesos_SERCOP.buyer_id, nunca de procuringEntity ni por nombre.
let
    Archivos = {
        [Anio=2021, Ruta="sercop-portal-csv-2021-20261121-145729/tender_2021.csv"],
        [Anio=2022, Ruta="sercop-portal-csv-2022-20261121-145742/tender_2022.csv"],
        [Anio=2023, Ruta="sercop-portal-csv-2023-20261121-145820/tender_2023.csv"],
        [Anio=2024, Ruta="sercop-portal-csv-2024-20261121-150856/tender_2024.csv"],
        [Anio=2025, Ruta="sercop-portal-csv-2025-20261121-141748/tender_2025.csv"]
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
    #"Campos para limpiar licitaciones" = Table.SelectColumns(
        #"Cinco años anexados",
        {"ocid", "release_id", "AnioProceso", "value_amount", "value_currency",
         "procurementMethod", "procurementMethodDetails"}
    ),
    NormalizarTexto = (Valor as nullable text) as nullable text =>
        if Valor = null then null
        else Text.Combine(
            List.Select(Text.SplitAny(Valor, " #(tab)#(cr)#(lf)" & Character.FromNumber(160)), each _ <> ""), " "
        ),
    #"Método sin espacios repetidos ni saltos de línea" = Table.TransformColumns(
        #"Campos para limpiar licitaciones",
        {{"procurementMethodDetails", NormalizarTexto, type nullable text}}
    ),
    #"Importe estimado decimal anulable" = Table.TransformColumns(
        #"Método sin espacios repetidos ni saltos de línea",
        {{"value_amount", each if _ = null or Text.Trim(_) = "" then null else Decimal.From(_, "en-US"),
          type nullable number}}
    ),
    #"Unicidad de licitación verificada" =
        if Table.RowCount(Table.Distinct(#"Importe estimado decimal anulable", {"ocid"}))
            <> Table.RowCount(#"Importe estimado decimal anulable")
        then error "Q-06 y S-04: ocid duplicados en licitaciones; detener y registrar, sin borrar filas."
        else #"Importe estimado decimal anulable",
    #"Moneda solo USD verificada" = Table.SelectRows(
        #"Unicidad de licitación verificada", each [value_currency] = "USD" or ([value_amount] = null and ([value_currency] = null or [value_currency] = ""))
    ),
    #"Importes negativos excluidos" = Table.SelectRows(
        #"Moneda solo USD verificada", each [value_amount] = null or [value_amount] >= 0
    ),
    #"Indicador de importe estimado" = Table.AddColumn(
        #"Importes negativos excluidos", "tiene_valor_estimado", each [value_amount] <> null, type logical
    ),
    #"Columnas finales de licitaciones" = Table.SelectColumns(
        #"Indicador de importe estimado",
        {"ocid", "value_amount", "tiene_valor_estimado", "procurementMethod", "procurementMethodDetails"}
    )
in
    #"Columnas finales de licitaciones"
