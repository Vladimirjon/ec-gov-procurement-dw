# ruff: noqa: E501, RUF001
"""Build the Hito 2 delivery PDF (sections 4.2 to 4.5 of the guide) from the versioned CSVs.

The classroom page asks for one PDF with the four parts and the header Titulo, Equipo #,
Nombres and Fecha. The layout follows the Hito 1 document (serif text, "Tabla N" captions,
tables with horizontal rules only). The content comes from the same files as the workbook
(`docs/h2/{fuentes,diccionario,calidad,cobertura}.csv`) and the control totals from
`docs/h2/evidencia/`, so the PDF and the workbook cannot drift apart.

The script writes an HTML file and prints it to PDF with a locally installed Chromium
browser (Edge or Chrome) in headless mode. Standard library only.

Usage:
    python -I scripts/build_hito2_pdf.py --output deliverables/h2/H2BravoFreireGuajanPasquelTorres.pdf
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Hito 2 - Adquisición y calidad de datos"
TEAM = "Grupo 5"
NAMES = "Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel y Jorge Torres"
SECTOR = "Gobierno central del Ecuador"
DATE = "21/11/26"
BROWSERS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)

CSS = """
@page { size: A4; margin: 18mm 20mm 18mm 20mm;
  @top-right { content: counter(page); font: 10pt 'Times New Roman',Times,serif; color: #000; } }
@page wide { size: A4 landscape; margin: 16mm 16mm 16mm 16mm;
  @top-right { content: counter(page); font: 10pt 'Times New Roman',Times,serif; color: #000; } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: #000; font: 10.6pt/1.32 'Times New Roman',Times,serif; text-align: justify; hyphens: manual; }
.wide { page: wide; }
h1 { font-size: 16pt; text-align: center; margin: 0 0 4mm; }
h2 { font-size: 12.5pt; margin: 6mm 0 2mm; break-after: avoid; text-align: left; }
h3 { font-size: 10.6pt; margin: 4mm 0 1mm; break-after: avoid; text-align: left; }
p { margin: 0 0 2.4mm; }
p.meta { margin: 0 0 1mm; text-align: left; }
code, .mono { font-family: Consolas,'Cascadia Mono',monospace; font-size: 0.86em; }
.cap { break-after: avoid; break-inside: avoid; margin: 3mm 0 1.2mm; text-align: left; }
.cap b { display: block; }
.cap i { display: block; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 8.2pt; line-height: 1.25; text-align: left; border-top: 1px solid #000; border-bottom: 1px solid #000; margin: 0 0 3mm; }
thead { display: table-header-group; }
th { font-weight: 700; padding: 1.3mm 1.6mm; border-bottom: 1px solid #000; vertical-align: bottom; }
td { padding: 1mm 1.6mm; vertical-align: top; border-bottom: 0.6pt solid #bdbdbd; overflow-wrap: anywhere; }
tr:last-child td { border-bottom: 0; }
tr { break-inside: avoid; }
td.id, td.field { font-weight: 700; }
td.field { font-family: Consolas,'Cascadia Mono',monospace; font-size: 0.95em; }
.hash { font-family: Consolas,'Cascadia Mono',monospace; font-size: 7.4pt; word-break: break-all; }
.num { text-align: right; white-space: nowrap; }
.url { display: block; font-family: Consolas,'Cascadia Mono',monospace; font-size: 7.2pt; margin-top: 0.8mm; }
.sub { display: block; font-size: 7.8pt; font-style: italic; margin-top: 0.6mm; }
table.wide-table { font-size: 8.3pt; }
td.m { font-family: Consolas,'Cascadia Mono',monospace; font-size: 8.8pt; }
td.s { font-style: italic; }
.note { font-size: 8.8pt; margin: 0 0 3mm; text-align: left; }
ul { margin: 0 0 2.4mm; padding-left: 5mm; }
li { margin: 0 0 1.2mm; }
"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def soft(text: str) -> str:
    """Escape text and allow line breaks at camelCase and underscore boundaries instead of mid-word."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=_)(?=\w)", "<wbr>", esc(text))


def read_csv(name: str) -> list[dict[str, str]]:
    with open(ROOT / "docs" / "h2" / name, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def money(value: float) -> str:
    whole, _, cents = f"{value:,.2f}".partition(".")
    return "USD " + whole.replace(",", ".") + "," + cents


class Counter:
    def __init__(self) -> None:
        self.n = 0

    def caption(self, title: str) -> str:
        self.n += 1
        return f'<div class="cap"><b>Tabla {self.n}</b><i>{esc(title)}</i></div>'


def control_totals() -> list[tuple[str, str, str, str, str]]:
    """Rows (table, source, rows, sum, label) taken from the profile evidence, not typed by hand."""
    profiles = [
        json.loads((ROOT / f"docs/h2/evidencia/perfil-calidad-sercop-{y}.json").read_text(encoding="utf-8"))
        for y in range(2021, 2026)
    ]

    def total(key: str) -> float:
        return sum(p["control_totals"][key] for p in profiles)

    entities = json.loads((ROOT / "docs/h2/evidencia/perfil-entidades.json").read_text(encoding="utf-8"))
    records = entities["workbook_structure"]["data_rows_range"]["total_records"]
    return [
        ("Procesos_SERCOP", "releases, 2021–2025", number(int(total("total_releases"))), "No aplica", ""),
        (
            "Licitaciones_SERCOP",
            "tender, 2021–2025",
            number(int(total("total_tender_rows"))),
            money(total("sum_tender_value_amount")),
            "valor estimado",
        ),
        (
            "Adjudicaciones_SERCOP",
            "awards, 2021–2025",
            number(int(total("total_awards_rows"))),
            money(total("sum_awards_amount")),
            "monto adjudicado",
        ),
        ("Entidades_MDEP", "hoja CATÁLOGO", number(records), "No aplica", ""),
    ]


def header() -> str:
    return (
        f"<h1>{esc(TITLE)}</h1>"
        f'<p class="meta"><b>Equipo #:</b> {esc(TEAM)}</p>'
        f'<p class="meta"><b>Nombres:</b> {esc(NAMES)}</p>'
        f'<p class="meta"><b>Sector:</b> {esc(SECTOR)}</p>'
        f'<p class="meta"><b>Fecha:</b> {esc(DATE)}</p>'
        '<p style="margin-top:4mm">El presente documento contiene el inventario de fuentes, el diccionario de datos, el diagnóstico de calidad y la matriz de cobertura del Hito 2 (apartados 4.2 a 4.5 de la guía). Las fuentes se encuentran conectadas en el archivo <code>.pbix</code> entregado, cuyas consultas contienen únicamente pasos de conexión. El hito es de carácter diagnóstico: los archivos originales no fueron modificados y cada problema identificado se acompaña de su evidencia medible y de una acción para el Hito 3.</p>'
    )


def fuentes(c: Counter) -> str:
    rows = read_csv("fuentes.csv")
    body, hashes = [], []
    for r in rows:
        entity, sep, rest = r["entidad_enlace"].partition(": http")
        link = "http" + rest if sep else ""
        body.append(
            f"<tr><td><b>{esc(r['fuente'])}</b></td><td>{esc(entity)}<span class='url'>{esc(link)}</span></td>"
            f"<td>{esc(r['formato_conector'])}</td><td>{esc(r['periodo_actualizacion'])}</td>"
            f"<td>{esc(r['filas_fecha_descarga'])}</td><td>{esc(r['licencia'])}</td></tr>"
        )
        hashes.append(f"<tr><td>{esc(r['fuente'])}</td><td class='hash'>{esc(r['sha256'])}</td></tr>")
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "Fuente",
            "Entidad y enlace exacto",
            "Formato y conector",
            "Periodo y actualización",
            "Filas y fecha de descarga",
            "Licencia",
        )
    )
    widths = "".join(f'<col style="width:{w}%">' for w in (16, 29, 12, 13, 17, 13))
    totals = "".join(
        f"<tr><td><b>{esc(t)}</b><span class='sub'>{esc(s)}</span></td><td class='num mono'>{esc(r)}</td>"
        f"<td class='num mono'>{esc(m)}" + (f"<span class='sub'>{esc(label)}</span>" if label else "") + "</td></tr>"
        for t, s, r, m, label in control_totals()
    )
    return (
        "<h2>Parte 1. Inventario de fuentes</h2>"
        f"<p>El inventario comprende {len(rows)} fuentes: los cinco archivos anuales de contratación abierta de SERCOP (2021 a 2025, formato CSV), el catálogo institucional del MDEP y el directorio <code>gob.ec</code>, utilizado únicamente como contraste de nombres. Los archivos se descargaron el 21/11/2026 y se conservaron sin modificación; las huellas SHA-256 de la Tabla 2 permiten verificar su integridad.</p>"
        + c.caption("Fuentes de datos: procedencia, formato y periodo")
        + f"<table><colgroup>{widths}</colgroup><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
        + c.caption("Huella SHA-256 de cada archivo descargado")
        + f"<table><colgroup><col style='width:34%'><col style='width:66%'></colgroup><thead><tr><th>Fuente</th><th>SHA-256</th></tr></thead><tbody>{''.join(hashes)}</tbody></table>"
        + "<h3>Totales de control iniciales</h3>"
        + "<p>Previo a cualquier transformación se registró el número de filas de cada tabla y la suma de su medida principal. Los totales son nacionales, no incluyen filtros y constituyen la referencia de control para el Hito 3.</p>"
        + c.caption("Totales de control por tabla (2021–2025)")
        + "<table><colgroup><col style='width:40%'><col style='width:18%'><col style='width:42%'></colgroup>"
        "<thead><tr><th>Tabla</th><th class='num'>Filas</th><th class='num'>Suma de la medida</th></tr></thead>"
        f"<tbody>{totals}</tbody></table>"
    )


def role_cell(raw: str, unit: str) -> str:
    kind, _, role = raw.partition(" / ")
    label, _, detail = role.partition(" (")
    detail = detail.rstrip(")")
    is_measure = label.startswith("Medida")
    shown = "<b>Medida</b>" if is_measure else "Atributo"
    extra = ", ".join(
        x for x in (label[len("Medida") :].strip() if is_measure else label[len("Atributo") :].strip(), detail) if x
    )
    lines = f"{esc(kind)}<span class='sub'>{shown}" + (f" ({esc(extra)})" if extra else "") + "</span>"
    if unit == "USD":
        lines += f"<span class='sub'>Unidad: {esc(unit)}</span>"
    return lines


def diccionario(c: Counter) -> str:
    rows = read_csv("diccionario.csv")
    head = "".join(
        f"<th>{h}</th>"
        for h in ("Campo", "Descripción", "Tipo esperado y rol", "Valores válidos", "Observación del perfil")
    )
    widths = "".join(f'<col style="width:{w}%">' for w in (16, 20, 17, 14, 33))
    tables = []
    for table in dict.fromkeys(r["tabla"] for r in rows):
        group = [r for r in rows if r["tabla"] == table]
        body = "".join(
            f"<tr><td class='field'>{soft(r['campo'])}</td><td>{esc(r['descripcion'])}</td><td>{role_cell(r['tipo_rol'], r['unidad'])}</td>"
            f"<td>{esc(r['valores_validos'])}</td><td>{esc(r['observacion_perfil'])}</td></tr>"
            for r in group
        )
        tables.append(
            c.caption(f"{table}: {group[0]['grano'][0].lower() + group[0]['grano'][1:].rstrip('.')}")
            + f"<table><colgroup>{widths}</colgroup><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
        )
    return (
        '<h2 style="break-before: page">Parte 2. Diccionario de datos</h2>'
        f"<p>El diccionario comprende las {len(set(r['tabla'] for r in rows))} tablas utilizadas por las preguntas P1 a P3, nombradas como las consultas de Power BI. Para cada tabla se define el grano, es decir, lo que representa una fila. El rol de cada campo se clasifica como <i>medida</i>, cuando se suma o se promedia, o como <i>atributo</i>, cuando se emplea para filtrar o agrupar. Las tasas, como la desviación porcentual, no se almacenan como medidas de la tabla de hechos: se calculan posteriormente mediante medidas.</p>"
        + "".join(tables)
    )


def calidad(c: Counter) -> str:
    rows = read_csv("calidad.csv")
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "ID",
            "Tabla y campo",
            "Dimensión",
            "Problema y evidencia medible",
            "Impacto en P1, P2 y P3",
            "Acción para el Hito 3",
        )
    )
    widths = "".join(f'<col style="width:{w}%">' for w in (5.5, 15.5, 8.5, 31, 19.5, 20))
    body = "".join(
        f"<tr class='finding'><td class='id'>{esc(r['id'])}</td><td><b>{soft(r['tabla_campo'])}</b></td><td>{esc(r['dimension'])}</td>"
        f"<td>{esc(r['problema_evidencia'])}</td><td>{esc(r['impacto_preguntas'])}</td><td>{esc(r['accion_h3'])}</td></tr>"
        for r in rows
    )
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_hito2_xlsx as workbook

    sheet_rows = workbook.generate_calidad_sheet(ROOT / "docs/h2/calidad.csv")[0]
    start = next(i for i, row in enumerate(sheet_rows) if row and row[0][0] == "Tabla")
    header_cells = [cell[0] for cell in sheet_rows[start]]
    matrix_body = []
    for row in sheet_rows[start + 1 :]:
        cells = [cell[0] for cell in row]
        tds = [f"<td><b>{soft(cells[0])}</b></td>"]
        tds += [f"<td class='m{' s' if value.startswith('S-') else ''}'>{esc(value)}</td>" for value in cells[1:]]
        matrix_body.append("<tr>" + "".join(tds) + "</tr>")
    q = sum(1 for r in rows if r["id"].startswith("Q-"))
    s = sum(1 for r in rows if r["id"].startswith("S-"))
    return (
        '<div class="wide"><h2>Parte 3. Diagnóstico de calidad</h2>'
        f"<p>Se evaluaron las seis dimensiones de calidad (completitud, validez, exactitud, consistencia, unicidad y oportunidad) en cada tabla. "
        f"El diagnóstico registra {q} hallazgos con evidencia, identificados como <code>Q-nn</code> (SERCOP) y <code>Q-Enn</code> (catálogo de entidades), "
        f"y {s} mediciones sin hallazgos, identificadas como <code>S-nn</code>. La columna de acción constituye el listado de tareas del Hito 3; "
        "en este hito no se corrigió ningún dato. "
        "El perfilado se realizó sobre todo el conjunto de datos y no sobre una muestra: en Power Query, la calidad, la distribución y el perfil de columna se calcularon con la opción «todo el conjunto de datos» en lugar de las primeras 1.000 filas, "
        "y las cifras del diccionario y del diagnóstico se obtuvieron con una lectura completa de los 1.007.920 procesos, 981.348 licitaciones y 975.302 adjudicaciones de 2021 a 2025 y de los 3.140 registros del catálogo.</p>"
        + c.caption("Hallazgos de calidad, evidencia, impacto y acción propuesta")
        + f"<table class='wide-table'><colgroup>{widths}</colgroup><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
        + c.caption("Matriz de control: tabla por dimensión de calidad")
        + "<table class='wide-table'><thead><tr>"
        + "".join(f"<th>{esc(h)}</th>" for h in header_cells)
        + f"</tr></thead><tbody>{''.join(matrix_body)}</tbody></table>"
        + "<p class='note'>Cada celda remite a un hallazgo (<code>Q-nn</code>, <code>Q-Enn</code>) o, en cursiva, a una medición sin hallazgos (<code>S-nn</code>).</p></div>"
    )


def cobertura(c: Counter) -> str:
    rows = read_csv("cobertura.csv")
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "Pregunta de negocio",
            "Campos necesarios",
            "Tabla y fuente",
            "¿Disponible?",
            "Decisión y justificación",
        )
    )
    widths = "".join(f'<col style="width:{w}%">' for w in (20, 16, 18, 11, 35))
    body = "".join(
        f"<tr><td><b>{esc(r['pregunta'].split('.', 1)[0])}.</b>{esc(r['pregunta'].split('.', 1)[1])}</td><td>{esc(r['campos_necesarios'])}</td>"
        f"<td>{soft(r['tabla_fuente'])}</td><td><b>{esc(r['disponible'])}</b></td><td>{esc(r['decision'])}</td></tr>"
        for r in rows
    )
    return (
        "<h2>Parte 4. Matriz de cobertura</h2>"
        "<p>La matriz contrasta cada pregunta del Hito 1 con los campos requeridos y determina si los datos obtenidos permiten responderla. Los campos necesarios están presentes en las fuentes conectadas; en las tres preguntas la disponibilidad es parcial, las tres se mantienen y la columna de decisión documenta el ajuste aplicado.</p>"
        + c.caption("Cobertura de las preguntas P1, P2 y P3")
        + f"<table><colgroup>{widths}</colgroup><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
        + "<h3>Conclusión</h3>"
        "<p>Los campos que requieren P1, P2 y P3 están disponibles en las fuentes conectadas, por lo que las tres preguntas se mantienen con los ajustes registrados en la tabla anterior: el tipo de entidad se obtiene al clasificar los compradores en el Hito 3, la fecha de negocio es releases.date (hallazgo Q-10) y P2 se calcula sobre los procesos que tienen ambos importes (86,18 % del total), sin tratar los vacíos como cero.</p>"
    )


def document() -> str:
    c = Counter()
    parts = [header(), fuentes(c), diccionario(c), calidad(c), cobertura(c)]
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>{esc(TITLE)} · {esc(TEAM)}</title><style>{CSS}</style></head><body>{''.join(parts)}</body></html>"
    )


def find_browser() -> str:
    for candidate in BROWSERS:
        if Path(candidate).exists():
            return candidate
    found = shutil.which("msedge") or shutil.which("chrome")
    if found:
        return found
    raise SystemExit("No se encontró Edge ni Chrome para imprimir el PDF")


def wait_for_pdf(path: Path, timeout: float = 120.0) -> None:
    """The headless browser can return before the PDF is on disk: wait until its size is stable."""
    deadline = time.monotonic() + timeout
    last = -1
    while time.monotonic() < deadline:
        size = path.stat().st_size if path.exists() else -1
        if size > 0 and size == last:
            return
        last = size
        time.sleep(1.0)
    raise SystemExit(f"El navegador no escribió {path} a tiempo")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--html", type=Path, help="also keep the intermediate HTML here")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error(f"{args.output} already exists; use a new name or delete it first")
    page = document()
    tmp = tempfile.mkdtemp(prefix="hito2pdf-")
    try:
        source = Path(tmp) / "hito2.html"
        source.write_text(page, encoding="utf-8", newline="\n")
        if args.html:
            shutil.copyfile(source, args.html)
        command = [
            find_browser(),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={Path(tmp) / 'profile'}",
            f"--print-to-pdf={args.output.resolve()}",
            source.as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603
        wait_for_pdf(args.output)
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"PDF escrito en {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
