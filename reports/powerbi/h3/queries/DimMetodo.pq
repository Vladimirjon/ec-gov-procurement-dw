// Cargar al modelo. Referencia a todas las licitaciones limpias: dominio nacional del diseño, 27 pares y sin licitación.
let
    Origen = Licitaciones_SERCOP,
    #"Solo columnas del método" = Table.SelectColumns(Origen, {"procurementMethod", "procurementMethodDetails"}),
    #"Procedimiento colapsado sin convenio" = Table.TransformColumns(#"Solo columnas del método",
        {{"procurementMethodDetails", each if _ = null or _ = "" then "Sin detalle"
          else if Text.StartsWith(_, "Catálogo electrónico", Comparer.Ordinal) and Text.Contains(_, " en el convenio")
          then Text.BeforeDelimiter(_, " en el convenio") else _, type text}}),
    #"Columnas renombradas" = Table.RenameColumns(#"Procedimiento colapsado sin convenio",
        {{"procurementMethod", "MetodoOCDS"}, {"procurementMethodDetails", "Procedimiento"}}),
    #"Métodos sin duplicados" = Table.Distinct(#"Columnas renombradas"),
    #"Códigos conocidos verificados" =
        if Table.RowCount(Table.SelectRows(#"Métodos sin duplicados", each
            not List.Contains({"open", "selective", "direct", "limited"}, [MetodoOCDS]))) > 0
        then error "DimMetodo: código no previsto en el diseño."
        else #"Métodos sin duplicados",
    #"Miembro sin licitación agregado" = Table.InsertRows(#"Códigos conocidos verificados", 0,
        {[MetodoOCDS="Sin licitación", Procedimiento="Sin licitación"]}),
    #"Etiqueta en español agregada" = Table.AddColumn(#"Miembro sin licitación agregado", "Metodo", each
        if [MetodoOCDS] = "Sin licitación" then "Sin licitación" else
        Record.Field([open="Abierto", selective="Selectivo", limited="Limitado", direct="Directo"], [MetodoOCDS]), type text),
    #"Métodos ordenados" = Table.Sort(#"Etiqueta en español agregada",
        {{"MetodoOCDS", Order.Ascending}, {"Procedimiento", Order.Ascending}}),
    #"Índice desde uno como IdMetodo" = Table.AddIndexColumn(#"Métodos ordenados", "IdMetodo", 1, 1, Int64.Type),
    #"Claves únicas verificadas" =
        if Table.RowCount(Table.Distinct(#"Índice desde uno como IdMetodo", {"IdMetodo"}))
            <> Table.RowCount(#"Índice desde uno como IdMetodo")
            or Table.RowCount(Table.Distinct(#"Índice desde uno como IdMetodo", {"MetodoOCDS", "Procedimiento"}))
            <> Table.RowCount(#"Índice desde uno como IdMetodo")
        then error "DimMetodo: clave sustituta o par duplicado."
        else #"Índice desde uno como IdMetodo"
in
    #"Claves únicas verificadas"
