// Cargar al modelo. Referencia al origen admitido; nombre de una sola fila de semilla por raíz, Q-13.
let
    Origen = Table.SelectRows(Origen_Modelo, each [Motivo] = "En el hecho"),
    #"Solo raíz de entidad" = Table.SelectColumns(Origen, {"RUC_13"}),
    #"Raíces sin duplicados" = Table.Distinct(#"Solo raíz de entidad"),
    #"Nombre único de semilla por raíz" = Table.Distinct(Table.Buffer(Table.Sort(
        Table.SelectRows(Semilla_Entidades, each [RaizAprobada] = true),
        {{"name_source", Order.Ascending}, {"buyer_id", Order.Ascending}})), {"ruc_root"}),
    #"Atributos de semilla combinados" = Table.NestedJoin(#"Raíces sin duplicados", {"RUC_13"},
        #"Nombre único de semilla por raíz", {"ruc_root"}, "Semilla", JoinKind.LeftOuter),
    #"Atributos expandidos" = Table.ExpandTableColumn(#"Atributos de semilla combinados", "Semilla",
        {"entity_name", "entity_type", "parent_entity", "valid_from", "valid_to"},
        {"Entidad", "TipoEntidad", "EntidadRectora", "VigenteDesde", "VigenteHasta"}),
    #"Raíz renombrada" = Table.RenameColumns(#"Atributos expandidos", {{"RUC_13", "RucRaiz"}}),
    #"Tipos etiquetados" = Table.TransformColumns(#"Raíz renombrada", {{"TipoEntidad", each
        Record.Field([presidencia="Presidencia", ministerio="Ministerio", instituto="Instituto"], _), type text}}),
    #"Vigencias informativas tipadas" = Table.TransformColumns(#"Tipos etiquetados",
        {{"VigenteDesde", each if _ = null or _ = "" then null else Date.FromText(_, [Format="yyyy-MM-dd"]), type nullable date},
         {"VigenteHasta", each if _ = null or _ = "" then null else Date.FromText(_, [Format="yyyy-MM-dd"]), type nullable date}}),
    #"Miembro sin clasificar agregado" = Table.InsertRows(#"Vigencias informativas tipadas", 0,
        {[RucRaiz="NO_IDENTIFICADO", Entidad="Sin clasificar", TipoEntidad="Sin clasificar",
          EntidadRectora=null, VigenteDesde=null, VigenteHasta=null]}),
    #"Entidades ordenadas por raíz" = Table.Sort(#"Miembro sin clasificar agregado", {{"RucRaiz", Order.Ascending}}),
    #"Índice desde uno como IdEntidad" = Table.AddIndexColumn(#"Entidades ordenadas por raíz", "IdEntidad", 1, 1, Int64.Type),
    #"Claves únicas verificadas" =
        if Table.RowCount(Table.Distinct(#"Índice desde uno como IdEntidad", {"RucRaiz"}))
            <> Table.RowCount(#"Índice desde uno como IdEntidad")
            or Table.RowCount(Table.Distinct(#"Índice desde uno como IdEntidad", {"IdEntidad"}))
            <> Table.RowCount(#"Índice desde uno como IdEntidad")
        then error "DimEntidad: clave sustituta o raíz duplicada."
        else #"Índice desde uno como IdEntidad"
in
    #"Claves únicas verificadas"
