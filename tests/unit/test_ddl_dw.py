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

    # Columnas, tipos y nulabilidad de las consultas M de reports/powerbi/h3/queries.
    columns = {
        name: re.findall(r"^ {4}(\w+ (?:bigint|text|date|numeric)(?: not null)?)", body, re.M)
        for name, body in table_definitions
    }
    assert columns == {
        "dw.dim_date": [
            "date_id bigint",
            "month_start date not null",
            "year bigint not null",
            "semester bigint not null",
            "quarter bigint not null",
            "month bigint not null",
            "month_name text not null",
            "year_month text not null",
        ],
        "dw.dim_entity": [
            "entity_id bigint",
            "ruc_root text not null",
            "entity_name text not null",
            "entity_type text not null",
            "parent_entity text",
            "valid_from date",
            "valid_to date",
        ],
        "dw.dim_method": [
            "method_id bigint",
            "ocds_method text not null",
            "procedure text not null",
            "method_name text not null",
        ],
        "dw.fact_contract_process": [
            "date_id bigint not null",
            "entity_id bigint not null",
            "method_id bigint not null",
            "ocid text",
            "awarded_amount numeric",
            "estimated_amount numeric",
            "process_count bigint not null",
            "award_count bigint not null",
            "process_with_both_amounts bigint not null",
        ],
    }

    assert all(body.count("primary key") == 1 for _, body in table_definitions)
    fact = dict(table_definitions)["dw.fact_contract_process"]
    assert "ocid text primary key" in fact
    foreign_keys = re.findall(
        r"\bforeign\s+key\s*\(\s*(\w+)\s*\)\s+references\s+(\w+\.\w+)\s*\(\s*(\w+)\s*\)",
        fact,
    )
    assert sorted(foreign_keys) == [
        ("date_id", "dw.dim_date", "date_id"),
        ("entity_id", "dw.dim_entity", "entity_id"),
        ("method_id", "dw.dim_method", "method_id"),
    ]
