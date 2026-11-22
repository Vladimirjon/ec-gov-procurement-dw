"""Check Hito 2 workbook cell contents and selected figures against source evidence.

The CSV comparison covers every populated cell created by the workbook generator.
The evidence checks cover only the metrics explicitly listed below; they do not
claim to validate every fact, interpretation, or number in the workbook.
"""

import csv
from decimal import ROUND_HALF_UP, Decimal
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
XLSX_PATH = REPO_ROOT / "deliverables/h2/Proyecto_Grupo5_Hito2.xlsx"
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def load_workbook_cells(path: Path) -> dict[str, dict[str, str]]:
    """Read cell values from inline strings or Excel shared strings by sheet and address."""
    with ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))  # noqa: S314
        relationships = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))  # noqa: S314
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships.findall(f"{{{REL_NS}}}Relationship")}
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))  # noqa: S314
            shared = ["".join(t.text or "" for t in item.findall(".//s:t", NS)) for item in root.findall("s:si", NS)]
        sheets = {}
        for sheet in workbook.findall(".//s:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(zf.read(target))  # noqa: S314
            cells = {}
            for cell in root.findall(".//s:sheetData/s:row/s:c", NS):
                value = cell.find("s:v", NS)
                cell_type = cell.get("t")
                if cell_type == "inlineStr":
                    text = "".join(t.text or "" for t in cell.findall("s:is//s:t", NS))
                elif cell_type == "s" and value is not None:
                    text = shared[int(value.text)]
                else:
                    text = value.text if value is not None and value.text is not None else ""
                if text:
                    cells[cell.attrib["r"]] = text
            sheets[sheet.attrib["name"]] = cells
        return sheets


def _column(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def expected_workbook_cells(root: Path) -> dict[str, dict[str, str]]:
    """Recreate the generator's content without writing a workbook."""
    path = root / "scripts/build_hito2_xlsx.py"
    spec = importlib.util.spec_from_file_location("build_hito2_for_comparison", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generators = {
        "Portada": module.generate_portada_sheet(),
        "Fuentes": module.generate_fuentes_sheet(root / "docs/h2/fuentes.csv"),
        "Diccionario": module.generate_diccionario_sheet(root / "docs/h2/diccionario.csv"),
        "Calidad": module.generate_calidad_sheet(root / "docs/h2/calidad.csv"),
        "Cobertura": module.generate_cobertura_sheet(root / "docs/h2/cobertura.csv"),
    }
    result = {}
    for name, (rows, _widths, _freeze, _merges) in generators.items():
        result[name] = {
            f"{_column(col)}{row}": text
            for row, values in enumerate(rows, 1)
            for col, (text, _style) in enumerate(values, 1)
            if text
        }
    return result


def compare_cells(actual: dict, expected: dict) -> list[str]:
    errors = []
    for sheet in sorted(set(actual) | set(expected)):
        for cell in sorted(set(actual.get(sheet, {})) | set(expected.get(sheet, {}))):
            if actual.get(sheet, {}).get(cell) != expected.get(sheet, {}).get(cell):
                errors.append(f"{sheet}!{cell}: contenido distinto del CSV o generador")
    return errors


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def evidence_checks(root: Path) -> tuple[list[str], int]:
    """Check listed figures in their specific CSV record against versioned evidence."""
    profiles = [
        json.loads((root / f"docs/h2/evidencia/perfil-calidad-sercop-{year}.json").read_text(encoding="utf-8"))
        for year in range(2021, 2026)
    ]
    downloads = _read_csv(root / "docs/h2/evidencia/descargas-sercop.csv")
    entity_downloads = _read_csv(root / "docs/h2/evidencia/descargas-entidades.csv")
    sources = _read_csv(root / "docs/h2/fuentes.csv")
    quality = {row["id"]: row for row in _read_csv(root / "docs/h2/calidad.csv")}
    coverage = {row["pregunta"][:2]: row for row in _read_csv(root / "docs/h2/cobertura.csv")}
    errors = []
    checks = 0

    def require(label: str, condition: bool) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(label)

    def number(value: int) -> str:
        return f"{value:,}".replace(",", ".")

    for index, year in enumerate(range(2021, 2026)):
        matches = [
            r
            for r in downloads
            if r["year"] == str(year) and "type=csv&" in r["url"] and r["sha256"] and r["http_status"] == "200"
        ]
        require(f"Fuentes {year}: descarga CSV única", len(matches) == 1)
        if len(matches) == 1:
            source = sources[index]
            download = matches[0]
            require(f"Fuentes {year}: URL", download["url"] in source["entidad_enlace"])
            require(f"Fuentes {year}: SHA-256", source["sha256"].upper() == download["sha256"].upper())
            releases = profiles[index]["control_totals"]["total_releases"]
            require(f"Fuentes {year}: releases", number(releases) in source["filas_fecha_descarga"])

    for index, url in [(5, entity_downloads[0]["url"]), (6, entity_downloads[1]["url"])]:
        download = next(r for r in entity_downloads if r["url"] == url)
        require(f"Fuentes {index + 1}: URL", url in sources[index]["entidad_enlace"])
        require(f"Fuentes {index + 1}: SHA-256", sources[index]["sha256"].upper() == download["sha256"].upper())

    totals = lambda key: sum(p["control_totals"][key] for p in profiles)  # noqa: E731
    releases = totals("total_releases")
    tenders = totals("total_tender_rows")
    both = totals("processes_with_both_amounts")
    no_award_amount = totals("processes_with_estimate_no_award") + totals("processes_without_any_amount")
    empty_tender = sum(p["completeness"]["tender_value_amount"]["empty"] for p in profiles)
    for label, row, field, value in [
        ("P1 procesos", coverage["P1"], "decision", releases),
        ("P1 licitaciones", coverage["P1"], "decision", tenders),
        ("P1 sin licitación", coverage["P1"], "decision", releases - tenders),
        ("P1 sin monto adjudicado", coverage["P1"], "decision", no_award_amount),
        ("P2 ambos importes", coverage["P2"], "decision", both),
        ("P2 licitaciones sin estimado", coverage["P2"], "decision", empty_tender),
        ("P2 sin monto adjudicado", coverage["P2"], "decision", no_award_amount),
        ("Q-01 licitaciones sin estimado", quality["Q-01"], "problema_evidencia", empty_tender),
        ("S-01 releases", quality["S-01"], "problema_evidencia", releases),
    ]:
        require(label, number(value) in row[field])
    percentage = f"{both / releases * 100:.2f}".replace(".", ",") + " %"
    require("P2 porcentaje nacional", percentage in coverage["P2"]["decision"])
    awards_empty = sum(p["completeness"]["awards_amount"]["empty"] for p in profiles)
    awards_positive = sum(p["completeness"]["awards_amount"]["positive"] for p in profiles)
    amount_row = next(
        r
        for r in _read_csv(root / "docs/h2/diccionario.csv")
        if r["tabla"] == "Adjudicaciones_SERCOP" and r["campo"] == "amount"
    )
    require(
        "Diccionario awards.amount positivos",
        f"{number(awards_positive)} adjudicaciones" in amount_row["observacion_perfil"],
    )
    require("Diccionario awards.amount vacíos", f"{awards_empty} filas vacías" in amount_row["observacion_perfil"])
    require(
        "Diccionario awards.amount vacíos por año",
        all(f"{p['completeness']['awards_amount']['empty']}" in amount_row["observacion_perfil"] for p in profiles),
    )

    accuracy = json.loads(
        (root / "docs/h2/evidencia/exactitud-licitaciones-json-vs-csv.json").read_text(encoding="utf-8")
    )["years"]
    q12 = quality["Q-12"]["problema_evidencia"]
    total = lambda key: sum(y[key] for y in accuracy.values())  # noqa: E731
    require("Q-12 filas de tender", number(total("json_tender_rows")) in q12 and total("json_tender_rows") == tenders)
    require(
        "Q-12 filas solo en un formato",
        total("tender_rows_only_in_json") == 0 and total("tender_rows_only_in_csv") == 0,
    )
    require("Q-12 importes en ambos formatos", total("amount_present_in_both") == tenders - empty_tender)
    require("Q-12 importes idénticos", number(total("amount_identical")) in q12)
    require("Q-12 importes con diferencia de redondeo", number(total("amount_differs_up_to_0_01")) in q12)
    require("Q-12 ninguna diferencia mayor a 0,01", total("amount_differs_more_than_0_01") == 0)
    require("Q-12 método de contratación", total("procurement_method_differs") == 0)
    require(
        "Q-12 detalle solo en espacios",
        total("method_details_differs") == total("method_details_differs_only_in_whitespace") == 796 and "796" in q12,
    )
    require("Q-12 caso de importe 0", total("json_amount_zero_csv_empty") == 1 and total("amount_only_in_csv") == 0)
    for year, stats in accuracy.items():
        difference = Decimal(stats["sum_difference_json_minus_csv"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        shown = f"{difference:+.2f}".replace(".", ",") if year == "2023" else f"{difference:.2f}".replace(".", ",")
        require(f"Q-12 diferencia de suma {year}", shown in q12)
    for date_key in ("release_date", "award_date"):
        months = set().union(*(p["timeliness"][date_key]["monthly_distribution"] for p in profiles))
        complete = all(f"{y}-{m:02d}" in months for y in range(2021, 2026) for m in range(1, 13))
        require(f"60 meses con {date_key}", complete)
    return errors, checks


def main() -> int:
    actual = load_workbook_cells(XLSX_PATH)
    expected = expected_workbook_cells(REPO_ROOT)
    errors = compare_cells(actual, expected)
    evidence_errors, count = evidence_checks(REPO_ROOT)
    errors.extend(evidence_errors)
    print(f"Celdas contrastadas con CSV/generador: {sum(map(len, expected.values()))}")
    print(f"Controles seleccionados contra JSON/CSV de evidencia: {count}")
    print(f"Discrepancias: {len(errors)}")
    for error in errors:
        print(f"- {error}")
    print("Los controles de evidencia son parciales; no verifican todas las cifras ni interpretaciones.")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
