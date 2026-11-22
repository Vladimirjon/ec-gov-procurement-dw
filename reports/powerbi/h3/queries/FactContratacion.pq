// Cargar al modelo. Grano: un ocid admitido del gobierno central con releases.date en 2021-2025.
// ocid es la única columna de texto: dimensión degenerada aprobada, sin tabla propia.
let
    Origen = Table.SelectRows(Origen_Modelo, each [Motivo] = "En el hecho"),
    #"Entidad admitida combinada" = Table.NestedJoin(Origen, {"RUC_13"}, DimEntidad, {"RucRaiz"}, "Entidad", JoinKind.LeftOuter),
    #"Clave de entidad expandida" = Table.ExpandTableColumn(#"Entidad admitida combinada", "Entidad", {"IdEntidad"}),
    #"Método combinado" = Table.NestedJoin(#"Clave de entidad expandida", {"MetodoOCDS", "Procedimiento"},
        DimMetodo, {"MetodoOCDS", "Procedimiento"}, "Metodo", JoinKind.LeftOuter),
    #"Clave de método expandida" = Table.ExpandTableColumn(#"Método combinado", "Metodo", {"IdMetodo"}),
    #"Mes combinado" = Table.NestedJoin(#"Clave de método expandida", {"IdTiempo"}, DimTiempo, {"IdTiempo"},
        "Tiempo", JoinKind.LeftOuter),
    #"Clave de tiempo comprobable expandida" = Table.ExpandTableColumn(#"Mes combinado", "Tiempo", {"IdTiempo"}, {"ClaveTiempo"}),
    #"Claves sin nulos verificadas" =
        if Table.RowCount(Table.SelectRows(#"Clave de tiempo comprobable expandida", each
            [IdEntidad] = null or [IdMetodo] = null or [ClaveTiempo] = null)) > 0
        then error "Hecho: clave sin pareja; detener, no imputar ni perder filas."
        else #"Clave de tiempo comprobable expandida",
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
    #"Filas grano y sumas conservados verificados" =
        if Table.RowCount(#"Tipos finales de medidas y claves") <> Table.RowCount(Origen)
            or Table.RowCount(Table.Distinct(#"Tipos finales de medidas y claves", {"ocid"})) <> Table.RowCount(Origen)
            or List.Sum(#"Tipos finales de medidas y claves"[MontoAdjudicado], Precision.Decimal)
                <> List.Sum(Origen[MontoAdjudicado], Precision.Decimal)
            or List.Sum(#"Tipos finales de medidas y claves"[ValorEstimado], Precision.Decimal)
                <> List.Sum(Origen[ValorEstimado], Precision.Decimal)
        then error "Hecho: filas, grano o sumas cambiaron al combinar dimensiones."
        else #"Tipos finales de medidas y claves"
in
    #"Filas grano y sumas conservados verificados"
