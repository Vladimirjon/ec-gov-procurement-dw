// Cargar al modelo. Diseño 6.2: 60 meses sin huecos, clave AAAAMM, jerarquía Anio > NombreMes.
let
    #"Meses continuos generados" = Table.FromColumns(
        {List.Transform({0..59}, each Date.AddMonths(#date(2021, 1, 1), _))}, {"FechaMes"}),
    #"Fecha mensual tipada" = Table.TransformColumnTypes(#"Meses continuos generados", {{"FechaMes", type date}}),
    #"Año agregado" = Table.AddColumn(#"Fecha mensual tipada", "Anio", each Date.Year([FechaMes]), Int64.Type),
    #"Mes agregado" = Table.AddColumn(#"Año agregado", "Mes", each Date.Month([FechaMes]), Int64.Type),
    #"Clave mensual agregada" = Table.AddColumn(#"Mes agregado", "IdTiempo", each [Anio] * 100 + [Mes], Int64.Type),
    #"Semestre agregado" = Table.AddColumn(#"Clave mensual agregada", "Semestre",
        each if [Mes] <= 6 then 1 else 2, Int64.Type),
    #"Trimestre agregado" = Table.AddColumn(#"Semestre agregado", "Trimestre",
        each Date.QuarterOfYear([FechaMes]), Int64.Type),
    #"Nombre del mes agregado" = Table.AddColumn(#"Trimestre agregado", "NombreMes",
        each Date.MonthName([FechaMes], "es-EC"), type text),
    #"Año mes agregado" = Table.AddColumn(#"Nombre del mes agregado", "AnioMes",
        each Date.ToText([FechaMes], [Format="yyyy-MM", Culture="es-EC"]), type text),
    #"Clave única y cobertura verificadas" =
        if Table.RowCount(#"Año mes agregado") <> 60
            or Table.RowCount(Table.Distinct(#"Año mes agregado", {"IdTiempo"})) <> 60
        then error "DimTiempo: clave duplicada o cobertura mensual incompleta."
        else #"Año mes agregado"
in
    #"Clave única y cobertura verificadas"
