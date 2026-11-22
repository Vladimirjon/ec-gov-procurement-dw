"""Unit tests for scripts/build_hito2_xlsx.py.

Validates deterministic SpreadsheetML OOXML generation with synthetic inputs
and tests production deliverables/h2/Proyecto_Grupo5_Hito2.xlsx integrity.
Only the Python standard library is used; no Excel installation required.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_hito2_xlsx.py"
REPO_ROOT = Path(__file__).resolve().parents[2]

XML_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

spec = importlib.util.spec_from_file_location("compare_hito2", REPO_ROOT / "scripts" / "compare_hito2_xlsx_sources.py")
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def make_synthetic_csvs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    fuentes = tmp_path / "fuentes.csv"
    fuentes.write_text(
        "fuente,entidad_enlace,formato_conector,periodo_actualizacion,filas_fecha_descarga,licencia,sha256\n"
        '"F1. Sercop 2021","SERCOP — https://example.com/2021","CSV / Texto/CSV","2021, anual",'
        '"100 filas; 21/11/2026","CC BY 3.0 Ec","AABB1122"\n'
        '"F2. Sercop 2022","SERCOP — https://example.com/2022","CSV / Texto/CSV","2022, anual",'
        '"150 filas; 21/11/2026","CC BY 3.0 Ec","CCDD3344"\n',
        encoding="utf-8",
        newline="\n",
    )

    diccionario = tmp_path / "diccionario.csv"
    diccionario.write_text(
        "tabla,grano,campo,descripcion,tipo_rol,valores_validos,observacion_perfil,unidad\n"
        '"Procesos_SERCOP","Una fila = un proceso","ocid","ID de proceso","Texto / Atributo (clave)",'
        '"ocds-...","100 distintos","Identificador"\n'
        '"Procesos_SERCOP","Una fila = un proceso","amount","Monto total","Número decimal / Medida del hecho",'
        '"> 0","100 válidos","USD"\n',
        encoding="utf-8",
        newline="\n",
    )

    calidad = tmp_path / "calidad.csv"
    calidad.write_text(
        "id,tabla_campo,dimension,problema_evidencia,impacto_preguntas,accion_h3\n"
        '"Q-01","tender · value_amount","Completitud","Ausente en 10 casos (10 %)","Impacto en P2",'
        '"Filtrar en Power Query"\n'
        '"S-01","releases · ocid","Exactitud","Sin hallazgos de exactitud: 100 % coincidente","Sin impacto",'
        '"Mantener total"\n',
        encoding="utf-8",
        newline="\n",
    )

    cobertura = tmp_path / "cobertura.csv"
    cobertura.write_text(
        "pregunta,campos_necesarios,tabla_fuente,disponible,decision\n"
        '"P1. Pregunta descriptiva","ocid, amount","Procesos_SERCOP","Sí","Se mantiene"\n'
        '"P2. Pregunta diagnóstica","amount, value_amount","Procesos_SERCOP","Parcial","Se ajusta universo"\n',
        encoding="utf-8",
        newline="\n",
    )

    return fuentes, diccionario, calidad, cobertura


def test_build_hito2_xlsx_synthetic_success(tmp_path: Path):
    fuentes, diccionario, calidad, cobertura = make_synthetic_csvs(tmp_path)
    output_xlsx = tmp_path / "test_output.xlsx"

    cmd = [
        sys.executable,
        "-I",
        str(SCRIPT),
        "--fuentes-csv",
        str(fuentes),
        "--diccionario-csv",
        str(diccionario),
        "--calidad-csv",
        str(calidad),
        "--cobertura-csv",
        str(cobertura),
        "--output",
        str(output_xlsx),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert output_xlsx.is_file()
    assert zipfile.is_zipfile(output_xlsx)

    with zipfile.ZipFile(output_xlsx, "r") as zf:
        members = zf.namelist()
        expected_members = [
            "[Content_Types].xml",
            "_rels/.rels",
            "xl/workbook.xml",
            "xl/_rels/workbook.xml.rels",
            "xl/styles.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
            "xl/worksheets/sheet3.xml",
            "xl/worksheets/sheet4.xml",
            "xl/worksheets/sheet5.xml",
        ]
        for em in expected_members:
            assert em in members, f"Missing member {em} in generated .xlsx"

        # Check all XML are well-formed
        for m in members:
            data = zf.read(m)
            try:
                root = ET.fromstring(data)  # noqa: S314
                assert root is not None
            except ET.ParseError as err:
                pytest.fail(f"Invalid XML in {m}: {err}")

        # Check styles count
        styles_root = ET.fromstring(zf.read("xl/styles.xml"))  # noqa: S314
        cell_xfs = styles_root.find("s:cellXfs", XML_NS)
        assert cell_xfs is not None
        style_count = int(cell_xfs.attrib["count"])
        assert style_count >= 14

        # Check sheet names in workbook.xml
        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))  # noqa: S314
        sheets_elem = wb_root.find("s:sheets", XML_NS)
        assert sheets_elem is not None
        sheet_nodes = sheets_elem.findall("s:sheet", XML_NS)
        assert len(sheet_nodes) == 5
        sheet_names = [s.attrib["name"] for s in sheet_nodes]
        assert len(sheet_names) == len(set(sheet_names)), "Duplicate sheet names found"
        for name in sheet_names:
            assert len(name) <= 31, f"Sheet name '{name}' exceeds 31 characters"

        # Check style index validity across all worksheets
        for idx in range(1, 6):
            ws_root = ET.fromstring(zf.read(f"xl/worksheets/sheet{idx}.xml"))  # noqa: S314
            cells = ws_root.findall(".//s:c", XML_NS)
            for c in cells:
                if "s" in c.attrib:
                    s_idx = int(c.attrib["s"])
                    assert 0 <= s_idx < style_count, f"Invalid style index {s_idx} in sheet{idx}"
                # Check character limit
                text_elems = c.findall(".//s:t", XML_NS)
                for t in text_elems:
                    text_content = t.text or ""
                    assert len(text_content) <= 32767, f"Text exceeds Excel limit: {text_content[:50]}..."
                    assert "[VERIFICAR]" not in text_content
                    assert "[PENDIENTE]" not in text_content


def test_build_hito2_xlsx_rejects_forbidden_placeholders(tmp_path: Path):
    fuentes, diccionario, _calidad, cobertura = make_synthetic_csvs(tmp_path)
    # Inject [VERIFICAR] in calidad.csv
    bad_calidad = tmp_path / "bad_calidad.csv"
    bad_calidad.write_text(
        "id,tabla_campo,dimension,problema_evidencia,impacto_preguntas,accion_h3\n"
        '"Q-01","tender · value_amount","Completitud","Ausente [VERIFICAR] dato","Impacto","Accion"\n',
        encoding="utf-8",
        newline="\n",
    )
    output_xlsx = tmp_path / "bad_output.xlsx"
    cmd = [
        sys.executable,
        "-I",
        str(SCRIPT),
        "--fuentes-csv",
        str(fuentes),
        "--diccionario-csv",
        str(diccionario),
        "--calidad-csv",
        str(bad_calidad),
        "--cobertura-csv",
        str(cobertura),
        "--output",
        str(output_xlsx),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "Forbidden placeholder" in proc.stderr or "Forbidden placeholder" in proc.stdout


def test_build_hito2_xlsx_missing_input_file(tmp_path: Path):
    output_xlsx = tmp_path / "missing_output.xlsx"
    cmd = [
        sys.executable,
        "-I",
        str(SCRIPT),
        "--fuentes-csv",
        str(tmp_path / "non_existent.csv"),
        "--output",
        str(output_xlsx),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "not found" in proc.stderr or "not found" in proc.stdout


def test_build_hito2_xlsx_production_workbook():
    """Verify that deliverables/h2/Proyecto_Grupo5_Hito2.xlsx is structurally sound and conforms to all rules."""
    prod_xlsx = REPO_ROOT / "deliverables" / "h2" / "Proyecto_Grupo5_Hito2.xlsx"
    assert prod_xlsx.is_file(), f"Production workbook {prod_xlsx} does not exist"

    with zipfile.ZipFile(prod_xlsx, "r") as zf:
        members = zf.namelist()
        for expected in [
            "[Content_Types].xml",
            "_rels/.rels",
            "xl/workbook.xml",
            "xl/_rels/workbook.xml.rels",
            "xl/styles.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
            "xl/worksheets/sheet3.xml",
            "xl/worksheets/sheet4.xml",
            "xl/worksheets/sheet5.xml",
        ]:
            assert expected in members

        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))  # noqa: S314
        sheets = [s.attrib["name"] for s in wb_root.findall(".//s:sheet", XML_NS)]
        assert sheets == ["Portada", "Fuentes", "Diccionario", "Calidad", "Cobertura"]

        # 1. Portada checks: Equipo, Sector, Fecha
        cells = compare.load_workbook_cells(prod_xlsx)
        portada_xml = " ".join(cells["Portada"].values())
        assert "Grupo 5" in portada_xml
        assert "Gobierno central" in portada_xml
        assert "21/11/26" in portada_xml

        # 2. Fuentes checks: 5 sercop years + MDEP + gob.ec
        fuentes_xml = " ".join(cells["Fuentes"].values())
        for year in ["2021", "2022", "2023", "2024", "2025"]:
            assert f"SERCOP — Contratación Abierta (OCDS) {year}" in fuentes_xml
        assert "MDEP — Catálogo Institucional e-SIGEF" in fuentes_xml
        assert "MINTEL — Directorio gob.ec" in fuentes_xml
        assert "CC BY 3.0 EC" in fuentes_xml
        assert "6A7AD388D0B1B4D4C71C7BD82BDB78C4A43B24E84EF8C1E6584DE0662E88AEAA" in fuentes_xml

        # 3. Diccionario checks: 4 tables, grain, units
        diccionario_xml = " ".join(cells["Diccionario"].values())
        assert "Tabla: Procesos_SERCOP" in diccionario_xml
        assert "Tabla: Licitaciones_SERCOP" in diccionario_xml
        assert "Tabla: Adjudicaciones_SERCOP" in diccionario_xml
        assert "Tabla: Entidades_MDEP" in diccionario_xml
        assert "USD" in diccionario_xml
        assert "ocid" in diccionario_xml
        assert "value_amount" in diccionario_xml
        assert "amount" in diccionario_xml
        assert "Medida del hecho" in diccionario_xml

        # 4. Calidad checks: Q-01..Q-11, Q-E01..Q-E08, S-01..S-04, matrix
        calidad_xml = " ".join(cells["Calidad"].values())
        for i in range(1, 12):
            assert f"Q-{i:02d}" in calidad_xml
        for i in range(1, 9):
            assert f"Q-E{i:02d}" in calidad_xml
        for i in range(1, 5):
            assert f"S-{i:02d}" in calidad_xml
        assert "Matriz de control: Tabla × Dimensión" in calidad_xml  # noqa: RUF001

        # 5. Cobertura checks: P1, P2, P3
        cobertura_xml = " ".join(cells["Cobertura"].values())
        assert "P1. ¿Cómo evolucionó" in cobertura_xml
        assert "P2. ¿Qué métodos" in cobertura_xml
        assert "P3. ¿Cuál es el monto" in cobertura_xml
        assert "868.576" in cobertura_xml

        # Ensure no forbidden marks across all files
        for m in members:
            text = zf.read(m).decode("utf-8", errors="replace")
            assert "[VERIFICAR]" not in text
            assert "[PENDIENTE]" not in text


def test_compare_detects_wrong_cell_even_if_value_exists_elsewhere():
    expected = {"Calidad": {"D3": "10", "D4": "20"}}
    actual = {"Calidad": {"D3": "20", "D4": "10"}}
    assert len(compare.compare_cells(actual, expected)) == 2


def test_reader_supports_shared_and_inline_strings(tmp_path: Path):
    path = tmp_path / "shared.xlsx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Calidad" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>',
        )
        zf.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<si><r><t>Texto </t></r><r><t>compartido</t></r></si></sst>",
        )
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row><c r="A1" t="s"><v>0</v></c>'
            '<c r="B1" t="inlineStr"><is><t>Texto directo</t></is></c></row></sheetData></worksheet>',
        )
    assert compare.load_workbook_cells(path) == {"Calidad": {"A1": "Texto compartido", "B1": "Texto directo"}}


def test_evidence_comparison_detects_a_changed_source(tmp_path: Path):
    """A source change must be detected even when the workbook text is unchanged."""
    for relative in [
        "docs/h2/fuentes.csv",
        "docs/h2/calidad.csv",
        "docs/h2/cobertura.csv",
        "docs/h2/diccionario.csv",
        "docs/h2/evidencia/descargas-sercop.csv",
        "docs/h2/evidencia/descargas-entidades.csv",
        "docs/h2/evidencia/exactitud-licitaciones-json-vs-csv.json",
        *(f"docs/h2/evidencia/perfil-calidad-sercop-{year}.json" for year in range(2021, 2026)),
    ]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, destination)
    errors, _ = compare.evidence_checks(tmp_path)
    assert errors == []
    accuracy = tmp_path / "docs/h2/evidencia/exactitud-licitaciones-json-vs-csv.json"
    accuracy_data = json.loads(accuracy.read_text(encoding="utf-8"))
    accuracy_data["years"]["2025"]["amount_identical"] += 1
    accuracy.write_text(json.dumps(accuracy_data), encoding="utf-8", newline="\n")
    errors, _ = compare.evidence_checks(tmp_path)
    assert "Q-12 importes idénticos" in errors
    accuracy_data["years"]["2025"]["amount_identical"] -= 1
    accuracy.write_text(json.dumps(accuracy_data), encoding="utf-8", newline="\n")
    profile = tmp_path / "docs/h2/evidencia/perfil-calidad-sercop-2021.json"
    data = json.loads(profile.read_text(encoding="utf-8"))
    data["control_totals"]["processes_with_both_amounts"] += 1
    profile.write_text(json.dumps(data), encoding="utf-8", newline="\n")
    errors, _ = compare.evidence_checks(tmp_path)
    assert "P2 ambos importes" in errors
