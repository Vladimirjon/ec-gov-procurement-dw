// Intermedia sin carga. Referencia al origen limpio, con una fila por ocid nacional y su motivo de alcance.
// Diseño 6.5: ventana, coincidencia exacta o raíz, conflicto, admisión y solo después IdEntidad.
// Rendimiento: la clasificación se calcula sobre los compradores distintos (miles de filas) y se une
// una sola vez a los procesos. Los importes se combinan en FactContratacion, ya filtrado al alcance.
let
    // Table.Buffer: la tabla se calcula una vez; las guardas no vuelven a leer los CSV.
    Origen = Table.Buffer(Procesos_SERCOP),
    Semilla = Table.Buffer(Semilla_Entidades),
    #"Compradores distintos" = Table.Buffer(Table.Distinct(Table.SelectColumns(Origen, {"buyer_id", "RUC_13"}))),
    #"Semilla por raíz sin duplicados" = Table.Distinct(Table.Buffer(Table.Sort(
        Table.SelectRows(Semilla, each [ruc_root] <> null and [ruc_root] <> ""),
        {{"name_source", Order.Ascending}, {"buyer_id", Order.Ascending}})), {"ruc_root"}),
    #"Comprador exacto combinado" = Table.NestedJoin(#"Compradores distintos", {"buyer_id"}, Semilla, {"buyer_id"},
        "Exacta", JoinKind.LeftOuter),
    #"Raíz combinada como alternativa" = Table.NestedJoin(#"Comprador exacto combinado", {"RUC_13"},
        #"Semilla por raíz sin duplicados", {"ruc_root"}, "PorRaiz", JoinKind.LeftOuter),
    #"Coincidencia exacta antes de raíz" = Table.AddColumn(#"Raíz combinada como alternativa", "Clasificacion",
        each if not Table.IsEmpty([Exacta]) then [Exacta]{0}
             else if not Table.IsEmpty([PorRaiz]) then [PorRaiz]{0}
             else [entity_type="sin_clasificar", status="dudosa", RaizAprobada=false]),
    #"Clasificación expandida" = Table.ExpandRecordColumn(#"Coincidencia exacta antes de raíz", "Clasificacion",
        {"entity_type", "status", "RaizAprobada"}, {"TipoSemilla", "EstadoSemilla", "RaizAprobada"}),
    #"Clasificación por comprador" = Table.Buffer(Table.SelectColumns(#"Clasificación expandida",
        {"buyer_id", "TipoSemilla", "EstadoSemilla", "RaizAprobada"})),
    #"Clasificación combinada con procesos" = Table.NestedJoin(Origen, {"buyer_id"},
        #"Clasificación por comprador", {"buyer_id"}, "Clase", JoinKind.LeftOuter),
    #"Clasificación de proceso expandida" = Table.ExpandTableColumn(#"Clasificación combinada con procesos", "Clase",
        {"TipoSemilla", "EstadoSemilla", "RaizAprobada"}),
    #"Motivo único de alcance" = Table.AddColumn(#"Clasificación de proceso expandida", "Motivo", each
        if [IdTiempo] < 202101 or [IdTiempo] > 202512 then "Fuera de la ventana 2021-2025"
        else if [RUC_13] = "NO_IDENTIFICADO" or [RaizAprobada] <> true or [EstadoSemilla] <> "aprobada"
            then "Dudoso o sin clasificar"
        else if List.Contains({"presidencia", "ministerio", "instituto"}, [TipoSemilla]) then "En el hecho"
        else if [TipoSemilla] = "fuera_de_alcance" then "Fuera del gobierno central"
        else "Dudoso o sin clasificar", type text),
    #"Columnas del origen de modelo" = Table.Buffer(#"Motivo único de alcance"),
    #"Grano nacional conservado verificado" =
        if Table.RowCount(#"Columnas del origen de modelo") <> Table.RowCount(Origen)
        then error "La clasificación alteró el grano ocid."
        else #"Columnas del origen de modelo"
in
    #"Grano nacional conservado verificado"
