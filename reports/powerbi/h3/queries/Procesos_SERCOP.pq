// Consulta intermedia: Habilitar carga desactivado. Fuente F1, CSV del portal usados en H2.
// Q-03, Q-04, Q-10: releases.date como fecha de negocio; clave mensual, no diaria (diseño aprobado).
// Q-07 y Q-08: RUC_13 desde buyer_id; malformados como NO_IDENTIFICADO, sin excluir aquí.
// Q-13 y Q-E*: fuera de alcance, va a #68/#70; no se usa buyer_name para unir.
let
    Archivos = {
        [Anio=2021, Ruta="sercop-portal-csv-2021-20261121-145729/releases_2021.csv"],
        [Anio=2022, Ruta="sercop-portal-csv-2022-20261121-145742/releases_2022.csv"],
        [Anio=2023, Ruta="sercop-portal-csv-2023-20261121-145820/releases_2023.csv"],
        [Anio=2024, Ruta="sercop-portal-csv-2024-20261121-150856/releases_2024.csv"],
        [Anio=2025, Ruta="sercop-portal-csv-2025-20261121-141748/releases_2025.csv"]
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
    // Table.Buffer: la tabla se calcula una vez; las guardas no vuelven a leer los CSV.
    #"Campos para comprobar claves" = Table.Buffer(Table.SelectColumns(
        #"Cinco años anexados", {"ocid", "buyer_id", "buyer_name", "date", "AnioProceso"}
    )),
    #"Claves completas verificadas" =
        if Table.RowCount(Table.SelectRows(#"Campos para comprobar claves", each
            [ocid] = null or Text.Trim([ocid]) = "" or [buyer_id] = null or Text.Trim([buyer_id]) = ""
            or [buyer_name] = null or Text.Trim([buyer_name]) = "" or [date] = null or Text.Trim([date]) = "")) > 0
        then error "S-05: claves vacías; detener y registrar el conteo, sin imputar."
        else #"Campos para comprobar claves",
    #"Unicidad de proceso verificada" =
        if Table.RowCount(Table.Distinct(Table.SelectColumns(#"Claves completas verificadas", {"ocid"})))
            <> Table.RowCount(#"Claves completas verificadas")
        then error "Q-06: ocid duplicados; detener y registrar el conteo, sin borrar filas."
        else #"Claves completas verificadas",
    #"Fecha de negocio desde releases.date" = Table.TransformColumns(
        #"Unicidad de proceso verificada",
        {{"date", each Date.FromText(Text.Start(_, 10), [Format="yyyy-MM-dd", Culture="en-US"]), type date}}
    ),
    #"Año y mes desde la fecha de negocio" = Table.AddColumn(
        #"Fecha de negocio desde releases.date", "IdTiempo", each Date.Year([date]) * 100 + Date.Month([date]), Int64.Type
    ),
    #"Raíz de RUC desde buyer_id" = Table.AddColumn(
        #"Año y mes desde la fecha de negocio", "RUC_13",
        each
            let
                Id = [buyer_id] ?? "",
                Raiz = if Text.Length(Id) >= 20 then Text.Middle(Id, 7, 13) else "",
                Sufijo = if Text.Length(Id) > 20 then Text.Range(Id, 20) else "",
                RaizValida = Text.StartsWith(Id, "EC-RUC-", Comparer.Ordinal)
                    and Text.Length(Raiz) = 13 and Text.Select(Raiz, {"0".."9"}) = Raiz,
                SufijoValido = Sufijo = "" or (Text.StartsWith(Sufijo, "-") and Text.Length(Sufijo) > 1)
            in
                if RaizValida and SufijoValido then Raiz else "NO_IDENTIFICADO",
        type text
    ),
    #"Columnas finales de procesos" = Table.SelectColumns(
        #"Raíz de RUC desde buyer_id", {"ocid", "buyer_id", "RUC_13", "date", "IdTiempo", "AnioProceso"}
    )
in
    #"Columnas finales de procesos"
