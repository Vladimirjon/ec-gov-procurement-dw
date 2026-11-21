"""Unit tests for scripts/measure_entity_crosswalk.py using synthetic CSV and XLSX data."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from measure_entity_crosswalk import (
    classify_sector111_entry,
    compute_combined_metrics,
    compute_combined_root_validation,
    discover_year_data,
    load_awards_amounts,
    load_buyer_summary_csv,
    load_catalog,
    measure_year_data,
    measure_year_from_summary,
)
import pytest


def create_synthetic_catalog_xlsx(path: Path) -> Path:
    """Generate minimal catalog .xlsx for testing crosswalk."""
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        '  <Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
        '  <Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
        '  <Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>\n'
        "</Types>"
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "  <sheets>\n"
        '    <sheet name="CATÁLOGO" sheetId="1" r:id="rId1"/>\n'
        "  </sheets>\n"
        "</workbook>"
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>\n'
        "</Relationships>"
    )

    shared_strings = [
        "SECTOR",
        "DESCRIPCION SECTOR",
        "ENTIDAD",
        "EOD",
        "NOMBRE",
        "RUC",
        "PROVINCIA",
        "CANTÓN",
        "OBSERVACIONES",
        "ADMINISTRACION DEL ESTADO",
        "GOBIERNOS AUTONOMOS DESCENTRALIZADOS MUNICIPALES",
    ]

    sst_entries = "".join(f"<si><t>{s}</t></si>" for s in shared_strings)
    sst_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">\n'
        f"{sst_entries}\n"
        "</sst>"
    )

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        "  <sheetData>\n"
        '    <row r="6">\n'
        '      <c r="A6" t="s"><v>0</v></c>\n'
        '      <c r="B6" t="s"><v>1</v></c>\n'
        '      <c r="C6" t="s"><v>2</v></c>\n'
        '      <c r="D6" t="s"><v>3</v></c>\n'
        '      <c r="E6" t="s"><v>4</v></c>\n'
        '      <c r="F6" t="s"><v>5</v></c>\n'
        '      <c r="G6" t="s"><v>6</v></c>\n'
        '      <c r="H6" t="s"><v>7</v></c>\n'
        '      <c r="I6" t="s"><v>8</v></c>\n'
        "    </row>\n"
        # Presidencia
        '    <row r="7">\n'
        '      <c r="A7"><v>111</v></c>\n'
        '      <c r="B7" t="s"><v>9</v></c>\n'
        '      <c r="C7"><v>20</v></c>\n'
        '      <c r="D7"><v>0</v></c>\n'
        '      <c r="E7" t="inlineStr"><is><t>PRESIDENCIA DE LA REPUBLICA - PLANTA CENTRAL</t></is></c>\n'
        '      <c r="F7"><v>1760000150001</v></c>\n'
        '      <c r="G7"><v>1700</v></c>\n'
        '      <c r="H7"><v>1701</v></c>\n'
        '      <c r="I7"><v></v></c>\n'
        "    </row>\n"
        # Ministerio Salud (12 digits, missing leading zero)
        '    <row r="8">\n'
        '      <c r="A8"><v>111</v></c>\n'
        '      <c r="B8" t="s"><v>9</v></c>\n'
        '      <c r="C8"><v>320</v></c>\n'
        '      <c r="D8"><v>0</v></c>\n'
        '      <c r="E8" t="inlineStr"><is><t>MINISTERIO DE SALUD PUBLICA - PLANTA CENTRAL</t></is></c>\n'
        '      <c r="F8"><v>160016780001</v></c>\n'
        '      <c r="G8"><v>100</v></c>\n'
        '      <c r="H8"><v>100</v></c>\n'
        '      <c r="I8"><v></v></c>\n'
        "    </row>\n"
        # GAD Municipal
        '    <row r="9">\n'
        '      <c r="A9"><v>122</v></c>\n'
        '      <c r="B9" t="s"><v>10</v></c>\n'
        '      <c r="C9"><v>500</v></c>\n'
        '      <c r="D9"><v>0</v></c>\n'
        '      <c r="E9" t="inlineStr"><is><t>GAD MUNICIPAL DE CUENCA</t></is></c>\n'
        '      <c r="F9"><v>0160000270001</v></c>\n'
        '      <c r="G9"><v>100</v></c>\n'
        '      <c r="H9"><v>101</v></c>\n'
        '      <c r="I9"><v></v></c>\n'
        "    </row>\n"
        "  </sheetData>\n"
        "</worksheet>"
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("xl/workbook.xml", workbook_xml)
        z.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        z.writestr("xl/sharedStrings.xml", sst_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    return path


@pytest.fixture
def synthetic_crosswalk_data(tmp_path: Path):
    cat_path = tmp_path / "catalog.xlsx"
    create_synthetic_catalog_xlsx(cat_path)

    # Synthetic releases
    rel_path = tmp_path / "releases_2021.csv"
    with rel_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ocid", "id", "initiationType", "buyer_id", "buyer_name", "language", "date", "tag"])
        # Simple match (Presidencia)
        writer.writerow(
            ["ocds-1", "rel-1", "tender", "EC-RUC-1760000150001", "Presidencia", "es", "2021-01-15T00:00:00Z", "[]"]
        )
        # Root match with suffix (Ministerio Salud unit)
        writer.writerow(
            [
                "ocds-2",
                "rel-2",
                "tender",
                "EC-RUC-0160016780001-100",
                "Hospital Cuenca",
                "es",
                "2021-02-15T00:00:00Z",
                "[]",
            ]
        )
        # Simple match (Ministerio Salud base)
        writer.writerow(
            ["ocds-3", "rel-3", "tender", "EC-RUC-0160016780001", "MSP Base", "es", "2021-03-15T00:00:00Z", "[]"]
        )
        # Root match (GAD Municipal)
        writer.writerow(
            ["ocds-4", "rel-4", "tender", "EC-RUC-0160000270001-99", "GAD Cuenca", "es", "2021-04-15T00:00:00Z", "[]"]
        )
        # Unmatched buyer
        writer.writerow(
            [
                "ocds-5",
                "rel-5",
                "tender",
                "EC-RUC-9999999999001",
                "Cuerpo de Bomberos X",
                "es",
                "2021-05-15T00:00:00Z",
                "[]",
            ]
        )
        # Second process for unmatched buyer without award
        writer.writerow(
            [
                "ocds-6",
                "rel-6",
                "tender",
                "EC-RUC-9999999999001",
                "Cuerpo de Bomberos X",
                "es",
                "2021-06-15T00:00:00Z",
                "[]",
            ]
        )

    # Synthetic awards
    awd_path = tmp_path / "awards_2021.csv"
    with awd_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ocid", "release_id", "id", "title", "description", "status", "date", "amount"])
        writer.writerow(["ocds-1", "rel-1", "awd-1", "", "", "", "2021-01-20T00:00:00Z", "1000.00"])
        writer.writerow(["ocds-2", "rel-2", "awd-2", "", "", "", "2021-02-20T00:00:00Z", "2500.50"])
        writer.writerow(["ocds-3", "rel-3", "awd-3", "", "", "", "2021-03-20T00:00:00Z", "500.00"])
        writer.writerow(["ocds-4", "rel-4", "awd-4", "", "", "", "2021-04-20T00:00:00Z", "4000.00"])
        writer.writerow(["ocds-5", "rel-5", "awd-5", "", "", "", "2021-05-20T00:00:00Z", "750.00"])
        # ocds-6 has NO award row: process without awarded amount!

    return cat_path, rel_path, awd_path


def test_classify_sector111_entry():
    assert classify_sector111_entry("PRESIDENCIA DE LA REPUBLICA") == "Presidencia / Vicepresidencia"
    assert classify_sector111_entry("MINISTERIO DE GOBIERNO") == "Ministerios"
    assert classify_sector111_entry("INSTITUTO NACIONAL DE ESTADISTICA") == "Institutos dependientes"
    assert (
        classify_sector111_entry("CONSEJO DE LA JUDICATURA - PLANTA CENTRAL")
        == "Otras funciones del Estado (fuera de alcance)"
    )
    assert (
        classify_sector111_entry("AGENCIA DE REGULACION FITO Y ZOOSANITARIA")
        == "Otras entidades de administración central (Agencias/Servicios/Secretarías)"
    )


def test_load_awards_amounts(synthetic_crosswalk_data):
    _, _, awd_path = synthetic_crosswalk_data
    amounts, ocids = load_awards_amounts(awd_path)
    assert len(ocids) == 5
    assert amounts["ocds-1"] == 1000.00
    assert amounts["ocds-2"] == 2500.50
    assert "ocds-6" not in ocids


def test_measure_year_data(synthetic_crosswalk_data):
    cat_path, rel_path, awd_path = synthetic_crosswalk_data
    catalog = load_catalog(cat_path)

    # 3 distinct RUCs in catalog
    assert len(catalog) == 3

    res = measure_year_data(2021, rel_path, awd_path, catalog)
    u = res["universe"]
    assert u["distinct_buyers"] == 5
    assert u["total_processes"] == 6
    assert u["processes_with_awarded_amount"] == 5
    assert u["processes_without_awarded_amount"] == 1
    assert u["total_awarded_amount"] == 8750.50

    cov = res["coverage"]
    # 4 of 5 buyers matched (1760000150001, 0160016780001-100, 0160016780001, 0160000270001-99)
    assert cov["buyers"]["total_matched_count"] == 4
    assert cov["buyers"]["unmatched_count"] == 1
    assert cov["buyers"]["pct_total_matched"] == 80.0

    # 4 of 6 processes matched
    assert cov["processes"]["total_matched_count"] == 4
    assert cov["processes"]["unmatched_count"] == 2
    assert cov["processes"]["pct_total_matched"] == 66.67

    # Root validation
    root_val = res["root_validation"]
    assert root_val["total_distinct_roots"] == 4
    assert root_val["roots_with_13_digits"] == 4
    assert root_val["roots_in_catalog"] == 3
    assert root_val["roots_with_multiple_buyer_ids"] == 1  # 0160016780001 has base and -100

    # Top uncrossed buyers
    uncrossed = res["top_30_uncrossed_buyers"]
    assert len(uncrossed) == 1
    assert uncrossed[0]["buyer_id"] == "EC-RUC-9999999999001"
    assert uncrossed[0]["process_count"] == 2
    assert uncrossed[0]["awarded_amount"] == 750.00
    assert uncrossed[0]["processes_without_amount"] == 1


def test_compute_combined_metrics(synthetic_crosswalk_data):
    cat_path, rel_path, awd_path = synthetic_crosswalk_data
    catalog = load_catalog(cat_path)
    yr1 = measure_year_data(2021, rel_path, awd_path, catalog)
    combined = compute_combined_metrics([yr1], global_distinct_buyers=5)

    assert combined["period"] == "2021-2025"
    assert combined["universe"]["total_processes"] == 6
    assert combined["universe"]["distinct_buyers"] == 5
    assert combined["coverage"]["processes"]["total_matched_count"] == 4
    assert combined["universe"]["total_awarded_amount"] == 8750.50


def test_discover_year_data(tmp_path: Path):
    derived_dir = tmp_path / "derived"
    derived_dir.mkdir()

    # Create dummy folders
    folder_2021 = derived_dir / "sercop-portal-csv-2021-test"
    folder_2021.mkdir()
    (folder_2021 / "releases_2021.csv").write_text("dummy", encoding="utf-8")
    (folder_2021 / "awards_2021.csv").write_text("dummy", encoding="utf-8")

    folder_2022 = derived_dir / "folder-2022"
    folder_2022.mkdir()
    (folder_2022 / "releases_2022.csv").write_text("dummy", encoding="utf-8")
    (folder_2022 / "awards_2022.csv").write_text("dummy", encoding="utf-8")

    discovered = discover_year_data(derived_dir)
    assert set(discovered.keys()) == {2021, 2022}
    assert discovered[2021][0].name == "releases_2021.csv"
    assert discovered[2022][1].name == "awards_2022.csv"


def test_compute_combined_root_validation(synthetic_crosswalk_data):
    cat_path, _, _ = synthetic_crosswalk_data
    catalog = load_catalog(cat_path)

    all_buyers = {
        "EC-RUC-1760000150001",
        "EC-RUC-0160016780001-100",
        "EC-RUC-0160016780001",
        "EC-RUC-0160000270001-99",
        "EC-RUC-9999999999001",
        "INVALID-BUYER-ID",
    }
    buyer_names = {
        "EC-RUC-1760000150001": "Presidencia",
        "EC-RUC-0160016780001-100": "Hospital Cuenca",
        "EC-RUC-0160016780001": "MSP Base",
        "EC-RUC-0160000270001-99": "GAD Cuenca",
        "EC-RUC-9999999999001": "Bomberos X",
    }
    proc_counts = Counter(
        {
            "EC-RUC-1760000150001": 10,
            "EC-RUC-0160016780001-100": 5,
            "EC-RUC-0160016780001": 2,
            "EC-RUC-0160000270001-99": 1,
            "EC-RUC-9999999999001": 3,
            "INVALID-BUYER-ID": 1,
        }
    )

    root_val, top_roots = compute_combined_root_validation(
        all_buyers,
        buyer_names,
        proc_counts,
        catalog,
    )

    assert root_val["total_distinct_roots"] == 4
    assert root_val["roots_with_13_digits"] == 4
    assert root_val["roots_in_catalog"] == 3
    assert root_val["roots_with_multiple_buyer_ids"] == 1  # 0160016780001 has base and -100
    assert root_val["regex_failed_buyer_ids_count"] == 1

    assert len(top_roots) == 4
    # Root with most buyer_ids should be first
    assert top_roots[0]["root_ruc"] == "0160016780001"
    assert top_roots[0]["buyer_ids_count"] == 2
    assert top_roots[0]["process_count"] == 7
    assert top_roots[0]["in_catalog"] is True


def test_measure_entity_crosswalk_cli(synthetic_crosswalk_data, tmp_path: Path):
    cat_path, rel_path, awd_path = synthetic_crosswalk_data

    # Setup mock derived folder structure for CLI
    derived_dir = tmp_path / "derived"
    derived_dir.mkdir()

    for yr in [2021, 2022, 2023, 2024, 2025]:
        ydir = derived_dir / f"sercop-portal-csv-{yr}-test"
        ydir.mkdir()
        # copy releases and awards
        (ydir / f"releases_{yr}.csv").write_bytes(rel_path.read_bytes())
        (ydir / f"awards_{yr}.csv").write_bytes(awd_path.read_bytes())

    out_json = tmp_path / "out_crosswalk.json"
    cmd = [
        sys.executable,
        "-I",
        str(Path(__file__).resolve().parents[2] / "scripts" / "measure_entity_crosswalk.py"),
        "--catalog-xlsx",
        str(cat_path),
        "--derived-dir",
        str(derived_dir),
        "--output-json",
        str(out_json),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert res.returncode == 0
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert len(data["years"]) == 5
    assert data["combined_5_years"]["universe"]["total_processes"] == 30  # 6 * 5 years
    assert "root_validation" in data["combined_5_years"]
    assert "top_20_roots_with_most_buyer_ids" in data["combined_5_years"]


def test_load_buyer_summary_csv_validation(tmp_path: Path):
    """Test validation of required columns in buyer summary CSV."""
    bad_csv = tmp_path / "bad_summary.csv"
    with bad_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anio", "buyer_id", "procesos"])  # missing other required columns
        w.writerow(["2025", "EC-RUC-1768000010001", "10"])

    with pytest.raises(ValueError, match="Missing required columns in buyer summary CSV"):
        load_buyer_summary_csv(bad_csv)

    non_existent = tmp_path / "non_existent.csv"
    with pytest.raises(FileNotFoundError):
        load_buyer_summary_csv(non_existent)


def test_measure_year_from_summary_matches_raw(synthetic_crosswalk_data, tmp_path: Path):
    """Verify that measuring from buyer summary produces identical results to raw CSVs."""
    cat_path, rel_path, awd_path = synthetic_crosswalk_data
    catalog = load_catalog(cat_path)

    raw_result = measure_year_data(2025, rel_path, awd_path, catalog)

    # Build synthetic buyer summary matching the synthetic releases and awards:
    # 6 processes across 5 buyers:
    # - EC-RUC-1760000150001: 1 proc, amount 1000.0, no_amt 0
    # - EC-RUC-0160016780001-100: 1 proc, amount 2500.50, no_amt 0
    # - EC-RUC-0160016780001: 1 proc, amount 500.0, no_amt 0
    # - EC-RUC-0160000270001-99: 1 proc, amount 4000.0, no_amt 0
    # - EC-RUC-9999999999001: 2 procs, amount 750.0, no_amt 1
    summary_csv = tmp_path / "synthetic_buyer_summary.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "anio",
            "buyer_id",
            "buyer_name_mas_frecuente",
            "procesos",
            "adjudicaciones",
            "suma_adjudicado",
            "suma_estimado",
            "procesos_con_ambos_importes",
            "procesos_sin_monto_adjudicado",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerow(
            {
                "anio": "2025",
                "buyer_id": "EC-RUC-1760000150001",
                "buyer_name_mas_frecuente": "Presidencia",
                "procesos": "1",
                "adjudicaciones": "1",
                "suma_adjudicado": "1000.0",
                "suma_estimado": "1000.0",
                "procesos_con_ambos_importes": "1",
                "procesos_sin_monto_adjudicado": "0",
            }
        )
        w.writerow(
            {
                "anio": "2025",
                "buyer_id": "EC-RUC-0160016780001-100",
                "buyer_name_mas_frecuente": "Hospital Cuenca",
                "procesos": "1",
                "adjudicaciones": "1",
                "suma_adjudicado": "2500.5",
                "suma_estimado": "2500.5",
                "procesos_con_ambos_importes": "1",
                "procesos_sin_monto_adjudicado": "0",
            }
        )
        w.writerow(
            {
                "anio": "2025",
                "buyer_id": "EC-RUC-0160016780001",
                "buyer_name_mas_frecuente": "MSP Base",
                "procesos": "1",
                "adjudicaciones": "1",
                "suma_adjudicado": "500.0",
                "suma_estimado": "500.0",
                "procesos_con_ambos_importes": "1",
                "procesos_sin_monto_adjudicado": "0",
            }
        )
        w.writerow(
            {
                "anio": "2025",
                "buyer_id": "EC-RUC-0160000270001-99",
                "buyer_name_mas_frecuente": "GAD Cuenca",
                "procesos": "1",
                "adjudicaciones": "1",
                "suma_adjudicado": "4000.0",
                "suma_estimado": "4000.0",
                "procesos_con_ambos_importes": "1",
                "procesos_sin_monto_adjudicado": "0",
            }
        )
        w.writerow(
            {
                "anio": "2025",
                "buyer_id": "EC-RUC-9999999999001",
                "buyer_name_mas_frecuente": "Cuerpo de Bomberos X",
                "procesos": "2",
                "adjudicaciones": "1",
                "suma_adjudicado": "750.0",
                "suma_estimado": "750.0",
                "procesos_con_ambos_importes": "1",
                "procesos_sin_monto_adjudicado": "1",
            }
        )

    summary_by_year = load_buyer_summary_csv(summary_csv)
    summary_result = measure_year_from_summary(2025, summary_by_year[2025], catalog)

    assert raw_result["universe"] == summary_result["universe"]
    assert raw_result["coverage"] == summary_result["coverage"]
    assert raw_result["root_validation"] == summary_result["root_validation"]
    assert len(raw_result["top_30_uncrossed_buyers"]) == len(summary_result["top_30_uncrossed_buyers"])
    for r_b, s_b in zip(raw_result["top_30_uncrossed_buyers"], summary_result["top_30_uncrossed_buyers"], strict=True):
        assert r_b["buyer_id"] == s_b["buyer_id"]
        assert r_b["process_count"] == s_b["process_count"]
        assert r_b["awarded_amount"] == s_b["awarded_amount"]
        assert r_b["processes_without_amount"] == s_b["processes_without_amount"]
