// Control agregado sin relaciones; solo conexión durante la construcción.
let
    Origen = Origen_Modelo,
    #"Año de negocio agregado" = Table.AddColumn(Origen, "Anio", each Date.Year([date]), Int64.Type),
    #"Exclusiones y admisiones contadas sin solaparse" = Table.Group(#"Año de negocio agregado", {"Motivo", "Anio"},
        {{"NumProcesos", each Table.RowCount(_), Int64.Type},
         {"MontoAdjudicado", each List.Sum([MontoAdjudicado], Precision.Decimal), type nullable Decimal.Type},
         {"ValorEstimado", each List.Sum([ValorEstimado], Precision.Decimal), type nullable Decimal.Type}})
in
    #"Exclusiones y admisiones contadas sin solaparse"
