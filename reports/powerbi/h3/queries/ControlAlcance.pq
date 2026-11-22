// Control agregado sin relaciones ni carga. Cuenta procesos por motivo y año de negocio.
// Los importes por motivo están en modelo-esperado.csv (Python); aquí no se combinan para no recargar el modelo.
let
    Origen = Origen_Modelo,
    #"Año de negocio agregado" = Table.AddColumn(Origen, "Anio", each Date.Year([date]), Int64.Type),
    #"Exclusiones y admisiones contadas sin solaparse" = Table.Group(#"Año de negocio agregado", {"Motivo", "Anio"},
        {{"NumProcesos", each Table.RowCount(_), Int64.Type}})
in
    #"Exclusiones y admisiones contadas sin solaparse"
