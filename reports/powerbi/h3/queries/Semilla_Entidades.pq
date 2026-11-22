// Intermedia sin carga. La semilla ya contiene las decisiones aprobadas; no se reaplican.
let
    Origen = Table.PromoteHeaders(Csv.Document(
        File.Contents(RutaSemillas & "/entity_classification.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]),
    #"Columnas de clasificación" = Table.SelectColumns(Origen,
        {"buyer_id", "ruc_root", "entity_name", "name_source", "entity_type", "parent_entity",
         "valid_from", "valid_to", "status"}),
    #"Clave de comprador única verificada" =
        if Table.RowCount(Table.Distinct(#"Columnas de clasificación", {"buyer_id"}))
            <> Table.RowCount(#"Columnas de clasificación")
        then error "Semilla: buyer_id duplicado."
        else #"Columnas de clasificación",
    RaizValida = (Id as text) as text =>
        let
            Raiz = if Text.Length(Id) >= 20 then Text.Middle(Id, 7, 13) else "",
            Sufijo = if Text.Length(Id) > 20 then Text.Range(Id, 20) else ""
        in
            if Text.StartsWith(Id, "EC-RUC-", Comparer.Ordinal) and Text.Length(Raiz) = 13
                and Text.Select(Raiz, {"0".."9"}) = Raiz
                and (Sufijo = "" or (Text.StartsWith(Sufijo, "-") and Text.Length(Sufijo) > 1))
            then Raiz else "",
    #"Patrón y raíz de semilla verificados" =
        if Table.RowCount(Table.SelectRows(#"Clave de comprador única verificada",
            each RaizValida([buyer_id]) <> ([ruc_root] ?? ""))) > 0
        then error "Semilla: raíz incompatible con buyer_id."
        else #"Clave de comprador única verificada",
    #"Conflictos por raíz resueltos como dudosos" = Table.Group(
        Table.SelectRows(#"Patrón y raíz de semilla verificados", each [ruc_root] <> null and [ruc_root] <> ""),
        {"ruc_root"}, {{"RaizAprobada", each List.Count(List.Distinct([entity_type])) = 1
            and List.AllTrue(List.Transform([status], each _ = "aprobada")), type logical}}),
    #"Estado de raíz combinado" = Table.NestedJoin(#"Patrón y raíz de semilla verificados", {"ruc_root"},
        #"Conflictos por raíz resueltos como dudosos", {"ruc_root"}, "EstadoRaiz", JoinKind.LeftOuter),
    #"Estado de raíz expandido" = Table.ExpandTableColumn(#"Estado de raíz combinado", "EstadoRaiz",
        {"RaizAprobada"}, {"RaizAprobada"})
in
    #"Estado de raíz expandido"
