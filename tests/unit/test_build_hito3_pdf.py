import csv
from pathlib import Path

import build_hito3_pdf as module


def test_document_has_header_parts_and_required_tables(monkeypatch):
    monkeypatch.setattr(module, "figure", lambda *args: '<div class="figure">Synthetic model image</div>')
    page = module.document()
    assert "<b>Título:</b> Hito 3 - Modelo dimensional y presentación de avance</p>" in page
    for label in ("Equipo #:", "Nombres:", "Fecha:"):
        assert f"<b>{label}</b>" in page
    for text in (
        "22/11/26",
        "Parte 4.2. Documento de diseño",
        "Parte 4.3. Bitácora de transformaciones",
        "plantilla 6.1",
        "plantilla 6.2",
        "P1:",
        "P2:",
        "P3:",
        "Tabla 1",
    ):
        assert text in page
    assert page.count("<table>") >= 10
    for banned in ("[VERIFICAR]", "[PENDIENTE]", "el líder", "\u2014", "\u2013", ".csv", ".md", ".py", "docs/"):
        assert banned not in page


def test_log_uses_supplied_synthetic_rows():
    row = dict.fromkeys(
        (
            "id",
            "tabla",
            "problema_h2",
            "transformacion",
            "paso_power_query",
            "control_antes",
            "control_despues",
            "nota",
        ),
        "synthetic",
    )
    row.update(id="Q-91", control_antes="100", control_despues="99", paso_power_query="A & B")
    page = module.transformation_log(module.Counter(), [row])
    assert "Q-91" in page and "100" in page and "99" in page
    assert "A &amp; B" in page
    assert "Parte 4.3." in page


def test_every_step_in_log_exists_in_versioned_queries():
    import re

    root = Path(__file__).resolve().parents[2]
    steps = set()
    for path in (root / "reports/powerbi/h3/queries").glob("*.pq"):
        steps.update(re.findall(r'^\s*#"([^"]+)"\s*=', path.read_text(encoding="utf-8"), re.M))
    with (root / "docs/h3/bitacora-transformaciones.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for step in row["paso_power_query"].split("; "):
            assert step in steps, (row["id"], step)
