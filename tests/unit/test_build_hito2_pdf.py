import importlib.util
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_hito2_pdf", ROOT / "scripts" / "build_hito2_pdf.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_document_has_the_header_and_the_four_parts_asked_by_the_classroom():
    page = module.document()
    assert "Hito 2 - Adquisición y calidad de datos" in page
    for label in ("Equipo #", "Nombres", "Fecha"):
        assert f"<dt>{label}</dt>" in page
    for heading in (
        "4.2 Inventario de fuentes",
        "4.3 Diccionario de datos",
        "4.4 Diagnóstico de calidad",
        "4.5 Matriz de cobertura",
    ):
        assert f"<h2>{heading}</h2>" in page


def test_every_csv_row_reaches_the_pdf_and_the_matrix_is_complete():
    page = module.document()
    findings = len(module.read_csv("calidad.csv"))
    assert page.count("<tr class='finding") == findings
    assert page.count("class='m-") == 24  # 4 tables x 6 dimensions
    assert "No medida" not in page
    for marker in ("[VERIFICAR]", "[PENDIENTE]"):
        assert marker not in page
    dictionary_rows = len(module.read_csv("diccionario.csv"))
    assert len(re.findall(r"<td class='field'>", page)) == dictionary_rows


def test_control_totals_come_from_the_profile_evidence():
    totals = {row[0]: row for row in module.control_totals()}
    assert totals["Procesos_SERCOP"][2] == "1.007.920"
    assert totals["Licitaciones_SERCOP"][2] == "981.348"
    assert totals["Adjudicaciones_SERCOP"][2] == "975.302"
    assert totals["Adjudicaciones_SERCOP"][3] == "USD 30.952.880.306,92"
    assert totals["Licitaciones_SERCOP"][3] == "USD 25.072.968.705,53"
