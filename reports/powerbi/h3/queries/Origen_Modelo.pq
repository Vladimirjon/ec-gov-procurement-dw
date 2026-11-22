// Intermedia sin carga. Referencia al origen limpio, con una fila por ocid nacional.
// Diseño 6.5: ventana, coincidencia exacta o raíz, conflicto, admisión y solo después IdEntidad.
let
    // Table.Buffer: la tabla se calcula una vez; las guardas no vuelven a leer los CSV.
    Origen = Table.Buffer(Procesos_SERCOP),
    Semilla = Table.Buffer(Semilla_Entidades),
    #"Semilla por raíz sin duplicados" = Table.Distinct(Table.Buffer(Table.Sort(
        Table.SelectRows(Semilla, each [ruc_root] <> null and [ruc_root] <> ""),
        {{"name_source", Order.Ascending}, {"buyer_id", Order.Ascending}})), {"ruc_root"}),
    #"Comprador exacto combinado" = Table.NestedJoin(Origen, {"buyer_id"}, Semilla, {"buyer_id"},
        "Exacta", JoinKind.LeftOuter),
    #"Raíz combinada como alternativa" = Table.NestedJoin(#"Comprador exacto combinado", {"RUC_13"},
        #"Semilla por raíz sin duplicados", {"ruc_root"}, "PorRaiz", JoinKind.LeftOuter),
    #"Coincidencia exacta antes de raíz" = Table.AddColumn(#"Raíz combinada como alternativa", "Clasificacion",
        each if not Table.IsEmpty([Exacta]) then [Exacta]{0}
             else if not Table.IsEmpty([PorRaiz]) then [PorRaiz]{0}
             else [entity_type="sin_clasificar", status="dudosa", RaizAprobada=false]),
    #"Clasificación expandida" = Table.ExpandRecordColumn(#"Coincidencia exacta antes de raíz", "Clasificacion",
        {"entity_type", "status", "RaizAprobada"}, {"TipoSemilla", "EstadoSemilla", "RaizAprobada"}),
    #"Motivo único de alcance" = Table.AddColumn(#"Clasificación expandida", "Motivo", each
        if [IdTiempo] < 202101 or [IdTiempo] > 202512 then "Fuera de la ventana 2021-2025"
        else if [RUC_13] = "NO_IDENTIFICADO" or [RaizAprobada] <> true or [EstadoSemilla] <> "aprobada"
            then "Dudoso o sin clasificar"
        else if List.Contains({"presidencia", "ministerio", "instituto"}, [TipoSemilla]) then "En el hecho"
        else if [TipoSemilla] = "fuera_de_alcance" then "Fuera del gobierno central"
        else "Dudoso o sin clasificar", type text),
    #"Licitación única combinada" = Table.NestedJoin(#"Motivo único de alcance", {"ocid"},
        Licitaciones_SERCOP, {"ocid"}, "Licitacion", JoinKind.LeftOuter),
    #"Licitación expandida" = Table.ExpandTableColumn(#"Licitación única combinada", "Licitacion",
        {"value_amount", "procurementMethod", "procurementMethodDetails"},
        {"ValorEstimado", "MetodoOCDS", "Detalle"}),
    #"Adjudicaciones ya agrupadas combinadas" = Table.NestedJoin(#"Licitación expandida", {"ocid"},
        Adjudicaciones_SERCOP, {"ocid"}, "Adjudicacion", JoinKind.LeftOuter),
    #"Suma y conteo expandidos" = Table.ExpandTableColumn(#"Adjudicaciones ya agrupadas combinadas", "Adjudicacion",
        {"MontoAdjudicado", "NumAdjudicaciones"}),
    #"Conteo ausente igual a cero verdadero" = Table.ReplaceValue(#"Suma y conteo expandidos", null, 0,
        Replacer.ReplaceValue, {"NumAdjudicaciones"}),
    #"Procedimiento normalizado" = Table.AddColumn(#"Conteo ausente igual a cero verdadero", "Procedimiento", each
        if [MetodoOCDS] = null then "Sin licitación"
        else if [Detalle] = null or [Detalle] = "" then "Sin detalle"
        else if Text.StartsWith([Detalle], "Catálogo electrónico", Comparer.Ordinal)
            then if Text.Contains([Detalle], " en el convenio") then Text.BeforeDelimiter([Detalle], " en el convenio")
                 else [Detalle]
        else [Detalle], type text),
    #"Método sin licitación identificado" = Table.ReplaceValue(#"Procedimiento normalizado", null,
        "Sin licitación", Replacer.ReplaceValue, {"MetodoOCDS"}),
    #"Columnas del origen de modelo" = Table.Buffer(Table.RemoveColumns(#"Método sin licitación identificado",
        {"Exacta", "PorRaiz", "Detalle"})),
    #"Grano nacional conservado verificado" =
        if Table.RowCount(#"Columnas del origen de modelo") <> Table.RowCount(Origen)
            or Table.RowCount(Table.Distinct(#"Columnas del origen de modelo", {"ocid"})) <> Table.RowCount(Origen)
        then error "Combinaciones de origen alteraron el grano ocid."
        else #"Columnas del origen de modelo"
in
    #"Grano nacional conservado verificado"
