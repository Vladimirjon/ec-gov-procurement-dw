"""Unit tests for scripts/profile_entity_catalog.py using synthetic .xlsx data."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

from profile_entity_catalog import calculate_sha256, profile_catalog
import pytest


def create_synthetic_catalog_xlsx(path: Path) -> Path:
    """Generate a minimal valid OpenXML spreadsheet (.xlsx) in pure standard library."""
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
        "SECTOR",  # 0
        "DESCRIPCION SECTOR",  # 1
        "ENTIDAD",  # 2
        "EOD",  # 3
        "NOMBRE",  # 4
        "RUC",  # 5
        "PROVINCIA",  # 6
        "CANTÓN",  # 7
        "OBSERVACIONES",  # 8
        "ADMINISTRACION DEL ESTADO",  # 9
        "ENTIDADES DE EDUCACION SUPERIOR",  # 10
        "GOBIERNOS AUTONOMOS DESCENTRALIZADOS MUNICIPALES",  # 11
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
        '  <dimension ref="A1:I12"/>\n'
        "  <sheetData>\n"
        '    <row r="1"><c r="A1" t="inlineStr"><is><t>SUBSECRETARÍA DE PRESUPUESTO</t></is></c></row>\n'
        '    <row r="2"><c r="A2" t="inlineStr"><is><t>DIRECCION NACIONAL</t></is></c></row>\n'
        '    <row r="3"><c r="A3" t="inlineStr"><is><t>CATÁLOGO DE INSTITUCIONES</t></is></c></row>\n'
        '    <row r="4"><c r="A4" t="inlineStr"><is><t>(Actualizado al 31 de Agosto de 2026)</t></is></c></row>\n'
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
        # Row 7: 13 digits RUC
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
        # Row 8: 12 digits RUC (missing leading zero)
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
        # Row 9: EOD under entity 320 with same RUC (duplicate RUC across rows)
        '    <row r="9">\n'
        '      <c r="A9"><v>111</v></c>\n'
        '      <c r="B9" t="s"><v>9</v></c>\n'
        '      <c r="C9"><v>320</v></c>\n'
        '      <c r="D9"><v>1000</v></c>\n'
        '      <c r="E9" t="inlineStr"><is><t>HOSPITAL GENERAL VICENTE CORRAL</t></is></c>\n'
        '      <c r="F9"><v>160016780001</v></c>\n'
        '      <c r="G9"><v>100</v></c>\n'
        '      <c r="H9"><v>100</v></c>\n'
        '      <c r="I9"><v>OBS1</v></c>\n'
        "    </row>\n"
        # Row 10: Higher Education
        '    <row r="10">\n'
        '      <c r="A10"><v>112</v></c>\n'
        '      <c r="B10" t="s"><v>10</v></c>\n'
        '      <c r="C10"><v>170</v></c>\n'
        '      <c r="D10"><v>0</v></c>\n'
        '      <c r="E10" t="inlineStr"><is><t>UNIVERSIDAD NACIONAL DE LOJA</t></is></c>\n'
        '      <c r="F10"><v>1160001720001</v></c>\n'
        '      <c r="G10"><v>1100</v></c>\n'
        '      <c r="H10"><v>1101</v></c>\n'
        '      <c r="I10"><v></v></c>\n'
        "    </row>\n"
        # Row 11: Municipal GAD
        '    <row r="11">\n'
        '      <c r="A11"><v>122</v></c>\n'
        '      <c r="B11" t="s"><v>11</v></c>\n'
        '      <c r="C11"><v>500</v></c>\n'
        '      <c r="D11"><v>0</v></c>\n'
        '      <c r="E11" t="inlineStr"><is><t>GOBIERNO AUTONOMO DESCENTRALIZADO MUNICIPAL DE CUENCA</t></is></c>\n'
        '      <c r="F11"><v>0160000270001</v></c>\n'
        '      <c r="G11"><v>100</v></c>\n'
        '      <c r="H11"><v>101</v></c>\n'
        '      <c r="I11"><v></v></c>\n'
        "    </row>\n"
        # Row 12: Footnote row (empty RUC, empty sector)
        '    <row r="12">\n'
        '      <c r="A12" t="inlineStr"><is><t>FUENTE: Ministerio de Finanzas e-SIGEF</t></is></c>\n'
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
def synthetic_xlsx(tmp_path: Path) -> Path:
    target = tmp_path / "synthetic_catalog.xlsx"
    return create_synthetic_catalog_xlsx(target)


def test_calculate_sha256(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"hello world")
    digest = calculate_sha256(sample)
    # sha256 of 'hello world'
    assert digest == "B94D27B9934D3E08A52E52D7DA7DABFAC484EFE37A5380EE9088F7ACE2EFCDE9"


def test_profile_catalog_structure(synthetic_xlsx: Path):
    profile = profile_catalog(synthetic_xlsx)

    # Metadata
    assert profile["metadata"]["source_file"] == "synthetic_catalog.xlsx"
    assert profile["metadata"]["sha256"] == calculate_sha256(synthetic_xlsx)

    # Structure
    ws = profile["workbook_structure"]
    assert ws["profiled_sheet"] == "CATÁLOGO"
    assert ws["data_rows_range"]["total_records"] == 5
    assert ws["footnote_rows_range"]["total_footnotes"] == 1
    assert "e-SIGEF" in ws["footnote_rows_range"]["notes"][0]["text"]

    # Column completeness
    comp = profile["column_completeness"]
    assert comp["RUC"]["populated_count"] == 5
    assert comp["RUC"]["empty_count"] == 0
    assert comp["OBSERVACIONES"]["empty_count"] == 4

    # RUC analysis
    rucs = profile["ruc_analysis"]
    assert rucs["total_data_records"] == 5
    assert rucs["raw_12_digits_missing_leading_zero"] == 2
    assert rucs["raw_13_digits"] == 3
    assert rucs["normalized_13_digits_count"] == 5
    assert rucs["distinct_normalized_rucs"] == 4
    assert rucs["duplicate_normalized_ruc_values"] == 1
    assert rucs["records_with_shared_ruc"] == 2
    assert rucs["ending_with_001_count"] == 5
    assert rucs["all_numeric"] is True

    # Multi-EOD entities
    ents = profile["entity_and_eod_analysis"]
    assert ents["distinct_entidad_codes"] == 4
    assert ents["entities_with_multiple_eod_rows"] == 1
    assert ents["max_eods_for_entity"]["entidad_code"] == "320"
    assert ents["max_eods_for_entity"]["row_count"] == 2

    # Central government sector 111
    sec111 = profile["central_government_sector_111"]
    assert sec111["total_records"] == 3
    assert sec111["distinct_entidades"] == 2


def test_profile_catalog_cli(synthetic_xlsx: Path, tmp_path: Path):
    out_json = tmp_path / "out_profile.json"
    cmd = [
        sys.executable,
        "-I",
        str(Path(__file__).resolve().parents[2] / "scripts" / "profile_entity_catalog.py"),
        "--input-xlsx",
        str(synthetic_xlsx),
        "--output",
        str(out_json),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert res.returncode == 0
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["workbook_structure"]["data_rows_range"]["total_records"] == 5
