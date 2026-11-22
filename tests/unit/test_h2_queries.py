from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUERIES = ROOT / "reports" / "powerbi" / "h2" / "queries"


def test_h2_connection_queries():
    names = {
        "Procesos_SERCOP": "RutaDerivados",
        "Licitaciones_SERCOP": "RutaDerivados",
        "Adjudicaciones_SERCOP": "RutaDerivados",
        "Entidades_MDEP": "RutaDatosCrudos",
    }
    prohibited = (
        "Table.SelectRows",
        "Table.TransformColumnTypes",
        "Table.RemoveColumns",
        "Table.SelectColumns",
        "Table.ReplaceValue",
        "Table.RenameColumns",
    )
    for name, parameter in names.items():
        raw = (QUERIES / f"{name}.pq").read_bytes()
        source = raw.decode("utf-8")
        assert b"\r" not in raw
        assert parameter in source
        assert "C:\\" not in source and "/Users/" not in source
        assert not any(function in source for function in prohibited)
        if parameter == "RutaDerivados":
            assert source.index("Table.PromoteHeaders") < source.index("Table.Combine")
            assert "QuoteStyle=QuoteStyle.Csv" in source
            assert "Encoding=65001" in source
            assert source.count('.csv"') == 5
