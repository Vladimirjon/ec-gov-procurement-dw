"""Unit tests for scripts/build_entity_seed.py using only invented, synthetic data."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import zipfile

from build_entity_seed import (
    CatalogRow,
    SeedRow,
    aggregate_sercop,
    apply_overrides,
    build_catalog_index,
    check_root_consistency,
    classify_group,
    coverage,
    discover_years,
    doubtful_cases,
    fallback_names_by_root,
    main,
    match_buyer,
    normalize_ruc,
    parse_buyer_id,
    read_catalog,
    read_overrides,
)
import pytest


def cell(ref: str, text: str) -> str:
    return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def write_catalog(path: Path, data: list[tuple[str, str, str, str, str, str]]) -> Path:
    """Minimal .xlsx: four title rows, a blank row, the header on row 6, data rows, footnotes."""
    rows = ["Titulo de prueba", "Otro titulo", "Fecha", "Corte", ""]
    xml_rows = [f'<row r="{i}">{cell(f"A{i}", t)}</row>' for i, t in enumerate(rows, 1) if t]
    header = ["SECTOR", "DESCRIPCION SECTOR", "ENTIDAD", "EOD", "NOMBRE", "RUC"]
    xml_rows.append('<row r="6">' + "".join(cell(f"{c}6", h) for c, h in zip("ABCDEF", header, strict=True)) + "</row>")
    for i, values in enumerate(data, 7):
        xml_rows.append(
            f'<row r="{i}">' + "".join(cell(f"{c}{i}", v) for c, v in zip("ABCDEF", values, strict=True)) + "</row>"
        )
    last = 7 + len(data)
    xml_rows.append(f'<row r="{last}">{cell(f"A{last}", "FUENTE: nota al pie sintetica")}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(xml_rows)
        + "</sheetData></worksheet>"
    )
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return path


# Invented catalog: (sector, description, udaf, eod, name, ruc as stored in the sheet).
CATALOG = [
    ("111", "ADMINISTRACION DEL ESTADO", "20", "9999", "PRESIDENCIA DE LA REPUBLICA - PLANTA CENTRAL", "1700000010001"),
    ("111", "ADMINISTRACION DEL ESTADO", "20", "5", "DIRECCION ZONAL 1 - PRESIDENCIA", "190000020001"),  # 12 digits
    ("111", "ADMINISTRACION DEL ESTADO", "320", "9999", "MINISTERIO DE PRUEBA UNO - PLANTA CENTRAL", "1700000030001"),
    ("111", "ADMINISTRACION DEL ESTADO", "320", "1", "HOSPITAL DE PRUEBA", "1700000040001"),
    ("111", "ADMINISTRACION DEL ESTADO", "360", "9999", "MINISTERIO DE PRUEBA DOS - PLANTA CENTRAL", "1700000050001"),
    ("111", "ADMINISTRACION DEL ESTADO", "130", "9999", "MINISTERIO DE PRUEBA TRES - PLANTA CENTRAL", "1700000060001"),
    ("111", "ADMINISTRACION DEL ESTADO", "130", "6", "DIRECCION DISTRITAL COMPARTIDA", "1700000070001"),
    ("111", "ADMINISTRACION DEL ESTADO", "360", "2", "DIRECCION DISTRITAL COMPARTIDA", "1700000070001"),
    ("111", "ADMINISTRACION DEL ESTADO", "64", "9999", "INSTITUTO DE PRUEBA - PLANTA CENTRAL", "1700000080001"),
    ("111", "ADMINISTRACION DEL ESTADO", "135", "0", "SERVICIO DE PRUEBA", "1700000090001"),
    ("111", "ADMINISTRACION DEL ESTADO", "21", "0", "VICEPRESIDENCIA DE PRUEBA", "1700000100001"),
    ("111", "ADMINISTRACION DEL ESTADO", "1", "0", "ASAMBLEA NACIONAL DE PRUEBA", "1700000110001"),
    ("111", "ADMINISTRACION DEL ESTADO", "592", "0", "SUPERINTENDENCIA DE PRUEBA", "1700000120001"),
    ("122", "GOBIERNOS AUTONOMOS DESCENTRALIZADOS MUNICIPALES", "700", "0", "MUNICIPIO DE PRUEBA", "1700000130001"),
    ("113", "ENTIDADES DE SEGURIDAD SOCIAL", "800", "0", "SEGURO DE PRUEBA", "1700000140001"),
    # Same RUC in a ministry and in a service: the outcome differs, so it is ambiguous.
    ("111", "ADMINISTRACION DEL ESTADO", "320", "7", "UNIDAD AMBIGUA", "1700000150001"),
    ("111", "ADMINISTRACION DEL ESTADO", "135", "3", "UNIDAD AMBIGUA", "1700000150001"),
    # A catalog entity whose name equals a SERCOP name, to prove names never join.
    ("122", "GOBIERNOS AUTONOMOS DESCENTRALIZADOS MUNICIPALES", "701", "0", "NOMBRE COMPARTIDO", "1700000160001"),
]


@pytest.fixture
def catalog_xlsx(tmp_path: Path) -> Path:
    return write_catalog(tmp_path / "catalog.xlsx", CATALOG)


@pytest.fixture
def index(catalog_xlsx: Path):
    rows, _ = read_catalog(catalog_xlsx)
    return build_catalog_index(rows)


def test_parse_buyer_id_exact_suffix_and_malformed() -> None:
    assert parse_buyer_id("EC-RUC-1700000010001") == ("1700000010001", "")
    assert parse_buyer_id("EC-RUC-1700000010001-4521") == ("1700000010001", "4521")
    assert parse_buyer_id(" EC-RUC-1700000010001 ") == ("1700000010001", "")
    for bad in ("EC-RUC-17000000100011", "EC-RUC-170000001000", "EC-RUC-1700000010001PE1", "RUC-1700000010001", ""):
        assert parse_buyer_id(bad) is None


def test_normalize_ruc_pads_twelve_digits_and_rejects_the_rest() -> None:
    assert normalize_ruc("190000020001") == "0190000020001"
    assert normalize_ruc("1700000010001") == "1700000010001"
    assert normalize_ruc("17000000100011") is None
    assert normalize_ruc("17A0000010001") is None
    assert normalize_ruc("") is None


def test_read_catalog_skips_titles_and_footnotes_and_pads_rucs(catalog_xlsx: Path) -> None:
    rows, stats = read_catalog(catalog_xlsx)
    assert stats["rows_loaded"] == len(CATALOG)
    assert stats["rows_padded_ruc"] == 1
    assert {r.ruc for r in rows if r.name == "DIRECCION ZONAL 1 - PRESIDENCIA"} == {"0190000020001"}
    assert all(len(r.ruc) == 13 for r in rows)
    assert not any("nota al pie" in r.name.lower() for r in rows)


def test_read_catalog_without_header_fails(tmp_path: Path) -> None:
    path = tmp_path / "bad.xlsx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>',
        )
    with pytest.raises(ValueError, match="header"):
        read_catalog(path)


@pytest.mark.parametrize(
    ("sector", "name", "entity_type", "status"),
    [
        ("111", "PRESIDENCIA DE LA REPUBLICA - PLANTA CENTRAL", "presidencia", "propuesta"),
        ("111", "MINISTERIO  DE  SALUD - PLANTA CENTRAL", "ministerio", "propuesta"),
        ("111", "INSTITUTO NACIONAL DE PRUEBA", "sin_clasificar", "dudosa"),
        ("111", "ASAMBLEA NACIONAL", "fuera_de_alcance", "aprobada"),
        ("111", "SUPERINTENDENCIA DE BANCOS", "fuera_de_alcance", "propuesta"),
        ("111", "SERVICIO DE RENTAS INTERNAS", "sin_clasificar", "dudosa"),
        ("111", "AGENCIA DE REGULACION", "sin_clasificar", "dudosa"),
        ("122", "MUNICIPIO DE PRUEBA", "fuera_de_alcance", "aprobada"),
        ("211", "EMPRESA PUBLICA DE PRUEBA", "fuera_de_alcance", "aprobada"),
        ("113", "SEGURO DE PRUEBA", "fuera_de_alcance", "propuesta"),
        ("999", "SECTOR DESCONOCIDO", "sin_clasificar", "dudosa"),
    ],
)
def test_classify_group(sector: str, name: str, entity_type: str, status: str) -> None:
    cls = classify_group(sector, name)
    assert (cls.entity_type, cls.status) == (entity_type, status)
    assert cls.source


def test_doubtful_group_carries_a_firm_recommendation() -> None:
    assert classify_group("111", "SERVICIO DE RENTAS INTERNAS").proposed_type == "fuera_de_alcance"
    assert classify_group("111", "INSTITUTO NACIONAL DE PRUEBA").proposed_type == "instituto"
    assert classify_group("111", "VICEPRESIDENCIA DE LA REPUBLICA").proposed_type == "presidencia"
    assert classify_group("111", "CASA MILITAR PRESIDENCIAL - PLANTA CENTRAL").proposed_type == "presidencia"


def test_exact_match_uses_the_catalog_group(index) -> None:
    row = match_buyer("EC-RUC-1700000030001", index, {})
    assert (row.match_type, row.entity_type, row.status) == ("exacta", "ministerio", "propuesta")
    assert row.catalog_udaf == "320"
    assert row.entity_name == "MINISTERIO DE PRUEBA UNO - PLANTA CENTRAL"
    assert row.name_source == "catalogo"
    assert row.source and row.valid_from == "" and row.valid_to == ""


def test_child_row_gets_the_group_head_as_parent(index) -> None:
    row = match_buyer("EC-RUC-1700000040001", index, {})
    assert row.entity_type == "ministerio"
    assert row.parent_entity == "MINISTERIO DE PRUEBA UNO - PLANTA CENTRAL"
    head = match_buyer("EC-RUC-1700000030001", index, {})
    assert head.parent_entity == ""


def test_root_match_for_a_unit_suffix_and_for_padded_rucs(index) -> None:
    unit = match_buyer("EC-RUC-1700000030001-98765", index, {})
    assert unit.match_type == "raiz"
    assert unit.entity_type == "ministerio"
    assert unit.ruc_root == "1700000030001"
    padded = match_buyer("EC-RUC-0190000020001", index, {})
    assert (padded.match_type, padded.entity_type) == ("exacta", "presidencia")


def test_unknown_root_is_unclassified_and_names_come_from_sercop(index) -> None:
    row = match_buyer("EC-RUC-1799999990001", index, {"1799999990001": "NOMBRE SERCOP"})
    assert (row.match_type, row.entity_type, row.status) == ("sin_cruce", "sin_clasificar", "dudosa")
    assert row.entity_name == "NOMBRE SERCOP"
    assert row.name_source == "sercop_nombre_mas_frecuente"


def test_malformed_buyer_id_is_never_matched(index) -> None:
    row = match_buyer("EC-RUC-1700000030001PE1", index, {})
    assert (row.match_type, row.entity_type, row.ruc_root) == ("malformado", "sin_clasificar", "")


def test_buyer_name_never_joins(index) -> None:
    """A SERCOP name equal to a catalog name must not classify a buyer with another RUC."""
    row = match_buyer("EC-RUC-1799999990002", index, {"1799999990002": "NOMBRE COMPARTIDO"})
    assert row.match_type == "sin_cruce"
    assert row.entity_type == "sin_clasificar"
    assert row.catalog_udaf == ""
    # match_buyer has no buyer-name input at all: only the id and a display-only map.
    assert match_buyer("EC-RUC-1700000160001", index, {}).entity_type == "fuera_de_alcance"


def test_ruc_in_two_groups_with_different_outcomes_is_ambiguous(index) -> None:
    row = match_buyer("EC-RUC-1700000150001", index, {})
    assert (row.entity_type, row.status) == ("sin_clasificar", "dudosa")
    assert "varias filas" in row.source or "distintas" in row.note
    assert "320/7" in row.note and "135/3" in row.note


def test_ruc_under_two_ministries_keeps_the_type_but_drops_the_parent(index) -> None:
    row = match_buyer("EC-RUC-1700000070001", index, {})
    assert row.entity_type == "ministerio"
    assert row.parent_entity == ""
    assert "padre no unico" in row.note


def test_catalog_index_has_one_entry_per_ruc(catalog_xlsx: Path) -> None:
    rows, _ = read_catalog(catalog_xlsx)
    assert len(build_catalog_index(rows)) == len({r.ruc for r in rows})


def test_other_state_functions_and_sectors_are_out_of_scope(index) -> None:
    for ruc, status in (("1700000110001", "aprobada"), ("1700000120001", "propuesta"), ("1700000130001", "aprobada")):
        row = match_buyer(f"EC-RUC-{ruc}", index, {})
        assert (row.entity_type, row.status) == ("fuera_de_alcance", status)
    assert match_buyer("EC-RUC-1700000090001", index, {}).status == "dudosa"


def write_overrides(path: Path, rows: list[dict[str, str]]) -> Path:
    cols = ["scope", "key", "entity_type", "decided_on", "decision_note", "parent_entity", "evidence"]
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return path


def test_overrides_apply_by_udaf_and_root_but_not_to_malformed(index, tmp_path: Path) -> None:
    seed = [
        match_buyer("EC-RUC-1700000090001", index, {}),
        match_buyer("EC-RUC-1700000090001-5", index, {}),
        match_buyer("EC-RUC-1700000150001", index, {}),
        match_buyer("EC-RUC-1700000030001PE1", index, {}),
    ]
    path = write_overrides(
        tmp_path / "ov.csv",
        [
            {
                "scope": "udaf",
                "key": "135",
                "entity_type": "fuera_de_alcance",
                "decided_on": "2026-11-22",
                "decision_note": "n1",
            },
            {
                "scope": "ruc_root",
                "key": "1700000150001",
                "entity_type": "ministerio",
                "decided_on": "2026-11-22",
                "decision_note": "n2",
            },
        ],
    )
    applied = apply_overrides(seed, read_overrides(path))
    assert applied == 3  # the ambiguous RUC has no single UDAF, so only its root decision reaches it
    assert [(r.entity_type, r.status) for r in seed[:2]] == [("fuera_de_alcance", "aprobada")] * 2
    assert (seed[2].entity_type, seed[2].status) == ("ministerio", "aprobada")
    assert "2026-11-22" in seed[2].source
    assert (seed[3].entity_type, seed[3].status) == ("sin_clasificar", "dudosa")


def test_institute_by_denomination_is_doubtful_not_in_scope(index) -> None:
    row = match_buyer("EC-RUC-1700000080001", index, {})
    assert (row.entity_type, row.status, row.proposed_type) == ("sin_clasificar", "dudosa", "instituto")
    assert row.catalog_sector == "111" and row.catalog_udaf == "64"


def test_override_keeps_documented_parent_and_evidence_on_an_uncrossed_root(index) -> None:
    seed = [match_buyer("EC-RUC-1799999990001", index, {"1799999990001": "DISTRITO"})]
    ov = {
        "scope": "ruc_root",
        "key": "1799999990001",
        "entity_type": "ministerio",
        "decided_on": "2026-11-22",
        "decision_note": "n",
        "parent_entity": "MINISTERIO DE PRUEBA UNO - PLANTA CENTRAL",
        "evidence": "catalogo oficial sintetico",
    }
    assert apply_overrides(seed, [ov]) == 1
    row = seed[0]
    assert (row.entity_type, row.status, row.proposed_type) == ("ministerio", "aprobada", "")
    assert row.parent_entity == "MINISTERIO DE PRUEBA UNO - PLANTA CENTRAL"
    assert row.source == "decision del lider 2026-11-22; catalogo oficial sintetico"


def test_sector_and_propuesta_scopes_approve_only_what_they_name(index) -> None:
    seed = [
        match_buyer("EC-RUC-1700000140001", index, {}),  # sector 113, fuera, propuesta
        match_buyer("EC-RUC-1700000030001", index, {}),  # ministerio, propuesta
        match_buyer("EC-RUC-1700000080001", index, {}),  # instituto by name, dudosa
        match_buyer("EC-RUC-1700000130001", index, {}),  # sector 122, fuera, aprobada
    ]
    base = {"decided_on": "2026-11-22", "decision_note": "n"}
    rows = [
        {"scope": "sector", "key": "113", "entity_type": "fuera_de_alcance", **base},
        {"scope": "propuesta", "key": "ministerio", "entity_type": "ministerio", **base},
    ]
    assert apply_overrides(seed, rows) == 2
    assert [r.status for r in seed] == ["aprobada", "aprobada", "dudosa", "aprobada"]
    assert seed[2].entity_type == "sin_clasificar"
    assert "decision del lider" in seed[0].source and "decision del lider" not in seed[3].source


def test_conflicting_decisions_for_one_row_fail(index, tmp_path: Path) -> None:
    seed = [match_buyer("EC-RUC-1700000090001", index, {})]
    base = {"decided_on": "d", "decision_note": "n"}
    rows = [
        {"scope": "udaf", "key": "135", "entity_type": "fuera_de_alcance", **base},
        {"scope": "ruc_root", "key": "1700000090001", "entity_type": "ministerio", **base},
    ]
    with pytest.raises(ValueError, match="conflicting"):
        apply_overrides(seed, rows)
    bad = write_overrides(
        tmp_path / "p.csv",
        [{"scope": "propuesta", "key": "ministerio", "entity_type": "instituto", **base}],
    )
    with pytest.raises(ValueError, match="keeps the type"):
        read_overrides(bad)


def test_root_consistency_detects_a_decision_that_splits_a_root(index) -> None:
    seed = [
        match_buyer("EC-RUC-1700000030001", index, {}),
        match_buyer("EC-RUC-1700000030001-5", index, {}),
        match_buyer("EC-RUC-1700000090001", index, {}),
    ]
    assert check_root_consistency(seed) == []
    seed[1].status = "aprobada"
    assert check_root_consistency(seed) == ["1700000030001"]


def test_overrides_reject_unknown_scope_or_type(tmp_path: Path) -> None:
    bad_scope = write_overrides(
        tmp_path / "a.csv",
        [{"scope": "name", "key": "X", "entity_type": "ministerio", "decided_on": "d", "decision_note": "n"}],
    )
    with pytest.raises(ValueError, match="invalid override"):
        read_overrides(bad_scope)
    bad_type = write_overrides(
        tmp_path / "b.csv",
        [{"scope": "udaf", "key": "1", "entity_type": "agencia", "decided_on": "d", "decision_note": "n"}],
    )
    with pytest.raises(ValueError, match="invalid override"):
        read_overrides(bad_type)
    missing = tmp_path / "c.csv"
    missing.write_text("scope,key\nudaf,1\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValueError, match="lacks columns"):
        read_overrides(missing)


def write_year(root: Path, year: int, releases: list[tuple[str, str, str, str]], awards: list[tuple[str, str]]) -> None:
    folder = root / f"sercop-portal-csv-{year}-20260101-000000"
    folder.mkdir(parents=True)
    with (folder / f"releases_{year}.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ocid", "buyer_id", "buyer_name", "date"])
        w.writerows(releases)
    with (folder / f"awards_{year}.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ocid", "amount"])
        w.writerows(awards)


@pytest.fixture
def derived(tmp_path: Path) -> Path:
    root = tmp_path / "derived"
    write_year(
        root,
        2024,
        [
            ("o1", "EC-RUC-1700000030001", "Ministerio Uno", "2024-03-01T00:00:00-05:00"),
            ("o2", "EC-RUC-1700000030001-77", "MINISTERIO  UNO", "2024-04-01T00:00:00-05:00"),
            ("o3", "EC-RUC-1700000090001", "Servicio Uno", "2024-05-01T00:00:00-05:00"),
            ("o4", "EC-RUC-1799999990001", "Fundacion X", "2025-01-10T00:00:00-05:00"),  # date year 2025
        ],
        [("o1", "100.50"), ("o1", "20.00"), ("o2", ""), ("o3", "50")],
    )
    write_year(
        root,
        2025,
        [
            ("o5", "EC-RUC-1700000030001", "Ministerio Uno", "2026-01-05T00:00:00-05:00"),  # out of range
            ("o6", "EC-RUC-1799999990001", "Fundacion X", "2025-02-02T00:00:00-05:00"),
            ("o7", "EC-RUC-1700000030001PE1", "Roto", "2025-02-03T00:00:00-05:00"),
        ],
        [("o5", "999"), ("o6", "10")],
    )
    return root


def test_aggregate_sums_awards_per_process_and_keeps_empty_apart_from_zero(derived: Path) -> None:
    agg, names = aggregate_sercop(discover_years(derived))
    assert agg[(2024, "EC-RUC-1700000030001")] == [1, 1, 120.5]  # two awards of one process are summed
    assert agg[(2024, "EC-RUC-1700000030001-77")] == [1, 0, 0.0]  # empty amount is not zero
    assert (2026, "EC-RUC-1700000030001") in agg  # business year comes from releases.date
    assert agg[(2025, "EC-RUC-1799999990001")] == [2, 1, 10.0]  # file 2024 holds a 2025 process
    assert names["EC-RUC-1700000030001-77"]["MINISTERIO UNO"] == 1


def test_fallback_name_is_the_most_frequent_spelling_with_alphabetical_ties(derived: Path) -> None:
    _, names = aggregate_sercop(discover_years(derived))
    fallback = fallback_names_by_root(names)
    # "Ministerio Uno" appears twice, the normalized "MINISTERIO UNO" once.
    assert fallback["1700000030001"] == "Ministerio Uno"
    assert "1700000030001PE1" not in fallback
    ties = {"EC-RUC-1700000030001": Counter({"B NOMBRE": 1, "A NOMBRE": 1})}
    assert fallback_names_by_root(ties) == {"1700000030001": "A NOMBRE"}


def test_coverage_splits_years_segments_and_excludes_out_of_range_from_the_total(index, derived: Path) -> None:
    agg, names = aggregate_sercop(discover_years(derived))
    fallback = fallback_names_by_root(names)
    seed = [match_buyer(b, index, fallback) for b in sorted({b for _, b in agg})]
    cov = coverage(seed, agg)
    assert set(cov["years"]) == {"2024", "2025", "2026"}
    assert cov["years"]["2024"]["ministerio:propuesta"]["processes"] == 2
    assert cov["years"]["2024"]["ministerio:propuesta"]["awarded_amount"] == 120.5
    assert cov["years"]["2024"]["sin_clasificar:dudosa"]["processes"] == 1
    assert cov["years"]["2025"]["sin_clasificar:sin_cruce"]["processes"] == 2
    assert cov["years"]["2025"]["sin_clasificar:malformado"]["processes"] == 1
    assert cov["years"]["2026"]["ministerio:propuesta"]["processes"] == 1
    total = cov["total_2021_2025"]
    assert total["ministerio:propuesta"]["processes"] == 2  # the 2026 process is not in the 2021-2025 total
    assert sum(v["processes"] for v in total.values()) == 6


def test_doubtful_cases_are_ranked_by_weight_and_skip_approved_rows(index, derived: Path) -> None:
    agg, names = aggregate_sercop(discover_years(derived))
    seed = [match_buyer(b, index, fallback_names_by_root(names)) for b in sorted({b for _, b in agg})]
    cases = doubtful_cases(seed, agg)
    assert [c["kind"] for c in cases] == ["grupo_catalogo", "sin_cruce", "malformado"]
    assert cases[0]["key"] == "135"
    assert cases[0]["proposed_type"] == "fuera_de_alcance"
    assert cases[1]["key"] == "1799999990001"
    assert cases[1]["processes"] == 2
    assert all(c["weight_pct"] > 0 for c in cases)
    assert cases[0]["weight_pct"] >= cases[1]["weight_pct"] >= cases[2]["weight_pct"]
    assert not any(c["key"] == "1700000030001" for c in cases)


def test_main_writes_the_three_outputs_and_refuses_to_overwrite(
    catalog_xlsx: Path, derived: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    args = [
        "--catalog-xlsx",
        str(catalog_xlsx),
        "--derived-dir",
        str(derived),
        "--output-seed",
        str(out / "seed.csv"),
        "--output-coverage",
        str(out / "cov.json"),
        "--output-cases",
        str(out / "cases.csv"),
    ]
    assert main(args) == 0
    with (out / "seed.csv").open(encoding="utf-8", newline="") as f:
        seed = list(csv.DictReader(f))
    keys = [r["buyer_id"] for r in seed]
    assert len(keys) == len(set(keys))
    assert all(r["source"] and r["status"] in {"aprobada", "propuesta", "dudosa"} for r in seed)
    assert all(
        r["entity_type"] in {"presidencia", "ministerio", "instituto", "fuera_de_alcance", "sin_clasificar"}
        for r in seed
    )
    assert all(r["entity_type"] == "sin_clasificar" for r in seed if r["status"] == "dudosa")
    report = json.loads((out / "cov.json").read_text(encoding="utf-8"))
    assert report["seed_rows"] == len(seed)
    assert report["business_date"] == "releases.date"
    assert main(args) == 1  # never overwrites
    assert (out / "seed.csv").read_text(encoding="utf-8").count("\r") == 0


def test_catalog_row_is_immutable() -> None:
    row = CatalogRow("111", "1", "0", "X", "1700000010001")
    with pytest.raises(AttributeError):
        row.ruc = "other"  # type: ignore[misc]
    assert SeedRow("a", "b", "exacta").status == "dudosa"
