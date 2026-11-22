// Cargar al modelo. Grano: un ocid admitido del gobierno central con releases.date en 2021-2025.
// ocid es la única columna de texto: dimensión degenerada aprobada, sin tabla propia.
// Rendimiento: se filtra al alcance antes de combinar licitaciones y adjudicaciones (275.100 filas, no 1.007.920).
let
    // Table.Buffer: la tabla se calcula una vez; las guardas no vuelven a leer los CSV.
    #"Procesos en el alcance" = Table.Buffer(Table.SelectRows(Origen_Modelo, each [Motivo] = "En el hecho")),
    #"Licitación única combinada" = Table.NestedJoin(#"Procesos en el alcance", {"ocid"},
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
    Origen = Table.Buffer(Table.RemoveColumns(#"Método sin licitación identificado", {"Detalle"})),
    #"Entidad admitida combinada" = Table.NestedJoin(Origen, {"RUC_13"}, DimEntidad, {"RucRaiz"}, "Entidad", JoinKind.LeftOuter),
    #"Clave de entidad expandida" = Table.ExpandTableColumn(#"Entidad admitida combinada", "Entidad", {"IdEntidad"}),
    #"Método combinado" = Table.NestedJoin(#"Clave de entidad expandida", {"MetodoOCDS", "Procedimiento"},
        DimMetodo, {"MetodoOCDS", "Procedimiento"}, "Metodo", JoinKind.LeftOuter),
    #"Clave de método expandida" = Table.ExpandTableColumn(#"Método combinado", "Metodo", {"IdMetodo"}),
    #"Mes combinado" = Table.NestedJoin(#"Clave de método expandida", {"IdTiempo"}, DimTiempo, {"IdTiempo"},
        "Tiempo", JoinKind.LeftOuter),
    #"Clave de tiempo comprobable expandida" = Table.ExpandTableColumn(#"Mes combinado", "Tiempo", {"IdTiempo"}, {"ClaveTiempo"}),
    #"Claves en memoria" = Table.Buffer(#"Clave de tiempo comprobable expandida"),
    #"Claves sin nulos verificadas" =
        if Table.RowCount(Table.SelectRows(#"Claves en memoria", each
            [IdEntidad] = null or [IdMetodo] = null or [ClaveTiempo] = null)) > 0
        then error "Hecho: clave sin pareja; detener, no imputar ni perder filas."
        else #"Claves en memoria",
    #"Número de procesos agregado" = Table.AddColumn(#"Claves sin nulos verificadas", "NumProcesos", each 1, Int64.Type),
    #"Marca aditiva de ambos importes" = Table.AddColumn(#"Número de procesos agregado", "ProcesoConAmbosImportes",
        each if [MontoAdjudicado] <> null and [ValorEstimado] <> null then 1 else 0, Int64.Type),
    #"Solo claves dimensión degenerada y medidas" = Table.SelectColumns(#"Marca aditiva de ambos importes",
        {"IdTiempo", "IdEntidad", "IdMetodo", "ocid", "MontoAdjudicado", "ValorEstimado", "NumProcesos",
         "NumAdjudicaciones", "ProcesoConAmbosImportes"}),
    #"Tipos finales de medidas y claves" = Table.TransformColumnTypes(#"Solo claves dimensión degenerada y medidas",
        {{"IdTiempo", Int64.Type}, {"IdEntidad", Int64.Type}, {"IdMetodo", Int64.Type}, {"ocid", type text},
         {"MontoAdjudicado", type nullable Decimal.Type}, {"ValorEstimado", type nullable Decimal.Type},
         {"NumAdjudicaciones", Int64.Type}}),
    #"Hecho en memoria para verificar" = Table.Buffer(#"Tipos finales de medidas y claves"),
    #"Filas grano y sumas conservados verificados" =
        if Table.RowCount(#"Hecho en memoria para verificar") <> Table.RowCount(Origen)
            or Table.RowCount(Table.Distinct(#"Hecho en memoria para verificar", {"ocid"})) <> Table.RowCount(Origen)
            or List.Sum(#"Hecho en memoria para verificar"[MontoAdjudicado], Precision.Decimal)
                <> List.Sum(Origen[MontoAdjudicado], Precision.Decimal)
            or List.Sum(#"Hecho en memoria para verificar"[ValorEstimado], Precision.Decimal)
                <> List.Sum(Origen[ValorEstimado], Precision.Decimal)
        then error "Hecho: filas, grano o sumas cambiaron al combinar dimensiones."
        else #"Hecho en memoria para verificar"
in
    #"Filas grano y sumas conservados verificados"
