from pathlib import Path
import re


def test_ddl_creates_star_schema() -> None:
    ddl = Path(__file__).resolve().parents[2] / "warehouse" / "ddl" / "001_dw_schema.sql"
    sql = re.sub(r"--[^\n]*", "", ddl.read_text(encoding="utf-8")).lower()

    schemas = re.findall(r"\bcreate\s+schema\s+(?:if\s+not\s+exists\s+)?(\w+)\s*;", sql)
    assert sorted(schemas) == ["audit", "dw", "stg"]

    table_definitions = re.findall(
        r"\bcreate\s+table\s+(?:if\s+not\s+exists\s+)?(\w+\.\w+)\s*\(([^;]*)\)\s*;",
        sql,
    )
    assert sorted(name for name, _ in table_definitions) == [
        "dw.dim_date",
        "dw.dim_entity",
        "dw.dim_method",
        "dw.fact_contract_process",
    ]

    fact = dict(table_definitions)["dw.fact_contract_process"]
    foreign_keys = re.findall(
        r"\bforeign\s+key\s*\(\s*(\w+)\s*\)\s+references\s+(\w+\.\w+)\s*\(\s*(\w+)\s*\)",
        fact,
    )
    assert sorted(foreign_keys) == [
        ("date_id", "dw.dim_date", "date_id"),
        ("entity_id", "dw.dim_entity", "entity_id"),
        ("method_id", "dw.dim_method", "method_id"),
    ]
