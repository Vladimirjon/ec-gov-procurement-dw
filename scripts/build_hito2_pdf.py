# ruff: noqa: E501, RUF001
"""Build the Hito 2 delivery PDF (sections 4.2 to 4.5 of the guide) from the versioned CSVs.

The professor's classroom page asks for one PDF with the four parts and a header
(Titulo, Equipo #, Nombres, Fecha). The content comes from the same files as the
workbook (`docs/h2/{fuentes,diccionario,calidad,cobertura}.csv`) and the control
totals from `docs/h2/evidencia/`, so the PDF and the workbook cannot drift apart.

The script writes an HTML file and prints it to PDF with a locally installed
Chromium browser (Edge or Chrome) in headless mode. Standard library only.

Usage:
    python -I scripts/build_hito2_pdf.py --output deliverables/h2/H2BravoFreireGuajanPasquelTorres.pdf
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Hito 2 - Adquisición y calidad de datos"
TEAM = "Grupo 5"
NAMES = "Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel, Jorge Torres"
SECTOR = "Gobierno central del Ecuador"
DATE = "21/11/26"
BROWSERS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)

CSS = """
:root {
  --ink: #17233b; --ink-2: #3a4660; --muted: #5d6880; --rule: #cfd5e0; --hair: #e4e8ef;
  --paper: #ffffff; --wash: #f4f6fa; --navy: #1d3557; --navy-tint: #e6ebf4;
  --found: #8c1d2f; --found-tint: #f7e7ea; --clear: #17625b; --clear-tint: #e2f1ef;
  --amber: #7a5200; --amber-tint: #fbf0d6;
}
@page { size: A4 landscape; margin: 11mm 14mm 14mm 14mm;
  @bottom-left { content: "Hito 2 · Grupo 5 · Adquisición y calidad de datos"; font: 7.5pt 'Segoe UI Variable Text','Segoe UI',sans-serif; color: #5d6880; }
  @bottom-right { content: counter(page); font: 7.5pt 'Segoe UI Variable Text','Segoe UI',sans-serif; color: #5d6880; } }
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--ink); background: var(--paper); font: 8.3pt/1.38 'Segoe UI Variable Text','Segoe UI',sans-serif;
  font-variant-numeric: tabular-nums; hyphens: manual; }
h1, h2, h3 { font-family: 'Sitka Heading','Sitka Text',Georgia,serif; font-weight: 600; color: var(--navy); margin: 0; text-wrap: balance; }
.mono { font-family: 'Cascadia Mono',Consolas,monospace; font-size: 0.92em; letter-spacing: -0.01em; }
section { break-before: page; }
section.cover { break-before: auto; }

/* Cover */
.cover { height: 178mm; display: grid; grid-template-columns: 1.05fr 1fr; column-gap: 16mm; align-content: stretch; }
.cover-left { display: flex; flex-direction: column; justify-content: space-between; padding-right: 4mm; }
.cover h1 { font-size: 30pt; line-height: 1.08; letter-spacing: -0.015em; max-width: 15ch; margin-top: 6mm; }
.rule { width: 22mm; height: 2.5px; background: var(--found); margin: 7mm 0 8mm; }
.facts { display: grid; grid-template-columns: 24mm 1fr; row-gap: 3.2mm; column-gap: 5mm; margin: 0; font-size: 10pt; }
.facts dt { color: var(--muted); font-weight: 600; }
.facts dd { margin: 0; color: var(--ink); }
.colophon { color: var(--muted); font-size: 8pt; line-height: 1.5; border-top: 1px solid var(--rule); padding-top: 3mm; }
.cover-right { background: var(--wash); border: 1px solid var(--hair); border-radius: 3px; padding: 8mm 9mm; display: flex; flex-direction: column; gap: 6mm; }
.cover-right h3 { font-size: 13pt; margin-bottom: 2.5mm; }
.lead { color: var(--ink-2); margin: 0 0 3mm; max-width: 68ch; }
table.controls { width: 100%; border-collapse: collapse; font-size: 8.8pt; }
table.controls th { text-align: left; font-weight: 600; color: var(--muted); font-size: 7.6pt; padding: 0 0 2mm; border-bottom: 1.2px solid var(--ink); }
table.controls th.num, table.controls td.num { text-align: right; }
table.controls td.num { white-space: nowrap; }
table.controls th:nth-child(2) { width: 22mm; }
table.controls th:nth-child(3) { width: 48mm; }
table.controls td { padding: 2.3mm 0; border-bottom: 1px solid var(--rule); vertical-align: top; }
table.controls td:first-child { font-weight: 600; }
.note { font-size: 8pt; color: var(--muted); margin: 2mm 0 0; line-height: 1.45; }
.rulebox { border-top: 1px solid var(--rule); padding-top: 4mm; color: var(--ink-2); }

dl.toc { display: grid; grid-template-columns: 12mm 1fr; row-gap: 2.2mm; margin: 9mm 0 0; font-size: 9.2pt; }
dl.toc dt { font-family: 'Cascadia Mono',Consolas,monospace; font-weight: 600; color: var(--navy); }
dl.toc dd { margin: 0; color: var(--ink-2); }
dl.toc dd strong { color: var(--ink); }
/* Section heads */
.sec-head { display: flex; justify-content: space-between; align-items: baseline; gap: 10mm; border-bottom: 1.5px solid var(--ink); padding-bottom: 2.2mm; margin-bottom: 3.2mm; }
.sec-head h2 { font-size: 17pt; }
.sec-head p { margin: 0; color: var(--muted); font-size: 8.4pt; max-width: 88mm; text-align: right; line-height: 1.35; }

/* Tables */
table.data { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.data thead { display: table-header-group; }
table.data th { text-align: left; font-weight: 600; font-size: 7.7pt; color: var(--ink-2); background: var(--wash); padding: 1.8mm 2.2mm; border-bottom: 1.2px solid var(--ink); border-top: 1px solid var(--rule); }
table.data td { padding: 1.6mm 2.2mm; vertical-align: top; border-bottom: 1px solid var(--hair); overflow-wrap: anywhere; }
table.data tr { break-inside: avoid; }
table.fuentes td { font-size: 7.8pt; padding-top: 1.5mm; padding-bottom: 1.5mm; }
.tblock { margin-bottom: 3mm; }
.matrix-block { break-inside: avoid; }
td.id { font-family: 'Cascadia Mono',Consolas,monospace; font-weight: 600; font-size: 8.4pt; color: var(--navy); }
.url { color: var(--ink-2); display: block; margin-top: 1mm; font-size: 7.4pt; }
.hash { font-family: 'Cascadia Mono',Consolas,monospace; font-size: 6.6pt; line-height: 1.35; color: var(--ink-2); word-break: break-all; }
.chip { display: inline-block; font-size: 7.3pt; font-weight: 600; line-height: 1; padding: 1.1mm 2mm; border-radius: 2px; white-space: nowrap; background: var(--navy-tint); color: var(--navy); }
.chip.found { background: var(--found-tint); color: var(--found); }
.chip.clear { background: var(--clear-tint); color: var(--clear); }
.chip.amber { background: var(--amber-tint); color: var(--amber); }
.chip.solid { background: var(--navy); color: #fff; }
.chip.line { background: transparent; box-shadow: inset 0 0 0 1px var(--rule); color: var(--ink-2); }
.sub { display: block; color: var(--muted); font-size: 7.6pt; margin-top: 1.2mm; }

/* Dictionary */
.tablehead { display: flex; align-items: baseline; gap: 5mm; padding: 1.5mm 0 2mm; break-after: avoid; }
.tablehead h3 { font-size: 12.5pt; }
.tablehead p { margin: 0; color: var(--ink-2); font-size: 8.4pt; }
td.field { font-family: 'Cascadia Mono',Consolas,monospace; font-weight: 600; font-size: 8.2pt; color: var(--navy); }

/* Findings */
td.dim { white-space: normal; }
tr.finding td.body { font-size: 8.2pt; }
tr.finding.clear td.id { color: var(--clear); }
tr.finding.found td.id { color: var(--found); }
.matrix-title { font-size: 12.5pt; margin: 7mm 0 3mm; break-after: avoid; }
table.matrix { width: 100%; border-collapse: separate; border-spacing: 1.2mm; table-layout: fixed; }
table.matrix th { text-align: left; font-weight: 600; font-size: 7.8pt; color: var(--ink-2); padding: 1.4mm 2mm; }
table.matrix td { padding: 3mm 2.4mm; border-radius: 2px; font-family: 'Cascadia Mono',Consolas,monospace; font-size: 8.6pt; font-weight: 600; }
table.matrix td.rowhead { background: transparent; font-family: 'Segoe UI Variable Text','Segoe UI',sans-serif; color: var(--navy); font-weight: 600; padding-left: 0; }
td.m-found { background: var(--found-tint); color: var(--found); }
td.m-clear { background: var(--clear-tint); color: var(--clear); }
td.m-both { background: linear-gradient(90deg, var(--found-tint) 50%, var(--clear-tint) 50%); color: var(--ink); }
.legend { display: flex; gap: 6mm; margin-top: 3mm; color: var(--ink-2); font-size: 8pt; align-items: center; }

/* Coverage */
td.q { font-family: 'Sitka Text',Georgia,serif; font-size: 9.2pt; font-weight: 600; color: var(--navy); line-height: 1.38; }
td.big { font-size: 8.7pt; }
"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def read_csv(name: str) -> list[dict[str, str]]:
    with open(ROOT / "docs" / "h2" / name, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def money(value: float) -> str:
    whole, _, cents = f"{value:,.2f}".partition(".")
    return "USD " + whole.replace(",", ".") + "," + cents


def control_totals() -> list[tuple[str, str, str, str, str]]:
    """Rows (table, source, rows, sum) taken from the profile evidence, not typed by hand."""
    profiles = [
        json.loads((ROOT / f"docs/h2/evidencia/perfil-calidad-sercop-{y}.json").read_text(encoding="utf-8"))
        for y in range(2021, 2026)
    ]

    def total(key: str) -> float:
        return sum(p["control_totals"][key] for p in profiles)

    entities = json.loads((ROOT / "docs/h2/evidencia/perfil-entidades.json").read_text(encoding="utf-8"))
    records = entities["workbook_structure"]["data_rows_range"]["total_records"]
    return [
        ("Procesos_SERCOP", "releases, 2021–2025", number(int(total("total_releases"))), "—", ""),
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
        ("Entidades_MDEP", "hoja CATÁLOGO", number(records), "—", ""),
    ]


def toc() -> str:
    fuentes_n = len(read_csv("fuentes.csv"))
    dic = read_csv("diccionario.csv")
    tablas = len({r["tabla"] for r in dic})
    cal = read_csv("calidad.csv")
    q = sum(1 for r in cal if r["id"].startswith("Q-"))
    sn = sum(1 for r in cal if r["id"].startswith("S-"))
    preguntas = len(read_csv("cobertura.csv"))
    return (
        '<dl class="toc">'
        f"<dt>4.2</dt><dd><strong>Inventario de fuentes</strong> · {fuentes_n} fuentes</dd>"
        f"<dt>4.3</dt><dd><strong>Diccionario de datos</strong> · {tablas} tablas, {len(dic)} campos</dd>"
        f"<dt>4.4</dt><dd><strong>Diagnóstico de calidad</strong> · {q} hallazgos y {sn} mediciones sin hallazgos</dd>"
        f"<dt>4.5</dt><dd><strong>Matriz de cobertura</strong> · {preguntas} preguntas de negocio</dd>"
        "</dl>"
    )


def cover() -> str:
    rows = "".join(
        f"<tr><td>{esc(t)}<span class='sub'>{esc(s)}</span></td><td class='num mono'>{esc(r)}</td>"
        f"<td class='num mono'>{esc(m)}" + (f"<span class='sub'>{esc(label)}</span>" if label else "") + "</td></tr>"
        for t, s, r, m, label in control_totals()
    )
    return f"""
<section class="cover">
  <div class="cover-left">
    <div>
      <h1>{esc(TITLE)}</h1>
      <div class="rule"></div>
      <dl class="facts">
        <dt>Equipo #</dt><dd>{esc(TEAM)}</dd>
        <dt>Nombres</dt><dd>{esc(NAMES)}</dd>
        <dt>Sector</dt><dd>{esc(SECTOR)}</dd>
        <dt>Fecha</dt><dd>{esc(DATE)}</dd>
      </dl>
      {toc()}
    </div>
    <div class="colophon">Escuela Politécnica Nacional · Facultad de Ingeniería de Sistemas<br>
      Proyecto Integrador de Business Intelligence · Entrega del Hito 2 con las partes 4.2 a 4.5 de la guía</div>
  </div>
  <div class="cover-right">
    <div>
      <h3>Totales de control iniciales</h3>
      <table class="controls">
        <thead><tr><th>Tabla</th><th class="num">Filas</th><th class="num">Suma de la medida</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p class="note">Origen: perfilado de los archivos descargados el 21/11/2026 (docs/h2/evidencia). Son totales
      nacionales y sin ninguna transformación; los comprueba el Hito 3 antes y después de limpiar.</p>
    </div>
    <div class="rulebox"><h3>Regla del hito</h3>
      <p class="lead">Aquí se diagnostica y no se corrige. Cada problema de calidad lleva su evidencia y una acción
      para el Hito 3. Los archivos originales no se modificaron y las consultas de Power BI solo tienen pasos
      de conexión.</p></div>
  </div>
</section>"""


def sec_head(title: str, lead: str) -> str:
    return f'<div class="sec-head"><h2>{esc(title)}</h2><p>{esc(lead)}</p></div>'


def fuentes() -> str:
    cols = (
        '<col style="width:36mm"><col style="width:74mm"><col style="width:24mm"><col style="width:24mm">'
        '<col style="width:38mm"><col style="width:28mm"><col style="width:45mm">'
    )
    body = []
    for r in read_csv("fuentes.csv"):
        entity, _, link = r["entidad_enlace"].partition(" — ")
        body.append(
            f"<tr><td><strong>{esc(r['fuente'])}</strong></td>"
            f"<td>{esc(entity)}<span class='url mono'>{esc(link)}</span></td>"
            f"<td>{esc(r['formato_conector'])}</td><td>{esc(r['periodo_actualizacion'])}</td>"
            f"<td>{esc(r['filas_fecha_descarga'])}</td><td>{esc(r['licencia'])}</td>"
            f"<td class='hash'>{esc(r['sha256'])}</td></tr>"
        )
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "Fuente",
            "Entidad y enlace exacto",
            "Formato / conector",
            "Periodo y actualización",
            "Filas y fecha de descarga",
            "Licencia",
            "SHA-256",
        )
    )
    return (
        "<section>"
        + sec_head(
            "4.2 Inventario de fuentes",
            "Procedencia de cada archivo: entidad, enlace, formato, periodo, filas, fecha y huella SHA-256.",
        )
        + f'<table class="data fuentes"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></section>'
    )


def role_cell(raw: str) -> str:
    kind, _, role = raw.partition(" / ")
    label, _, detail = role.partition(" (")
    detail = detail.rstrip(")")
    chip = "solid" if label.startswith("Medida") else "line"
    shown = "Medida" if label.startswith("Medida") else "Atributo"
    extra = label[len(shown) :].strip()
    note = ", ".join(x for x in (extra, detail) if x)
    sub = f"<span class='sub'>{esc(note)}</span>" if note else ""
    return f"{esc(kind)} <span class='chip {chip}' style='margin-left:1.2mm'>{shown}</span>{sub}"


def diccionario() -> str:
    rows = read_csv("diccionario.csv")
    cols = (
        '<col style="width:50mm"><col style="width:52mm"><col style="width:36mm"><col style="width:38mm">'
        '<col style="width:68mm"><col style="width:23mm">'
    )
    head = "".join(
        f"<th>{h}</th>"
        for h in ("Campo", "Descripción", "Tipo esperado y rol", "Valores válidos", "Observación del perfil", "Unidad")
    )
    blocks, seen = [], []
    for r in rows:
        if r["tabla"] not in seen:
            seen.append(r["tabla"])
    for table in seen:
        group = [r for r in rows if r["tabla"] == table]
        body = "".join(
            f"<tr><td class='field'>{esc(r['campo'])}</td><td>{esc(r['descripcion'])}</td><td>{role_cell(r['tipo_rol'])}</td>"
            f"<td>{esc(r['valores_validos'])}</td><td>{esc(r['observacion_perfil'])}</td><td>{esc(r['unidad'])}</td></tr>"
            for r in group
        )
        blocks.append(
            '<div class="tblock">'
            f'<div class="tablehead"><h3 class="mono">{esc(table)}</h3><p><strong>Grano:</strong> {esc(group[0]["grano"])}</p></div>'
            f'<table class="data dict"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
        )
    return (
        "<section>"
        + sec_head(
            "4.3 Diccionario de datos",
            "Grano de cada tabla y, por campo, descripción, tipo, rol, valores válidos y lo observado al perfilar.",
        )
        + "".join(blocks)
        + "</section>"
    )


def chip_for_id(identifier: str) -> str:
    return "clear" if identifier.startswith("S-") else "found"


def calidad() -> str:
    rows = read_csv("calidad.csv")
    cols = '<col style="width:15mm"><col style="width:42mm"><col style="width:84mm"><col style="width:58mm"><col style="width:67mm">'
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "ID",
            "Tabla y campo · Dimensión",
            "Problema y evidencia medible",
            "Impacto en P1, P2 y P3",
            "Acción para el Hito 3",
        )
    )
    body = []
    for r in rows:
        kind = chip_for_id(r["id"])
        body.append(
            f"<tr class='finding {kind}'><td class='id'>{esc(r['id'])}</td>"
            f"<td><strong>{esc(r['tabla_campo'])}</strong><br><span class='chip {kind}' style='margin-top:1.6mm'>{esc(r['dimension'])}</span></td>"
            f"<td class='body'>{esc(r['problema_evidencia'])}</td><td class='body'>{esc(r['impacto_preguntas'])}</td>"
            f"<td class='body'>{esc(r['accion_h3'])}</td></tr>"
        )
    # matrix: parsed from the generator so the PDF and the workbook share one definition
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_hito2_xlsx as workbook

    sheet_rows = workbook.generate_calidad_sheet(ROOT / "docs/h2/calidad.csv")[0]
    start = next(i for i, row in enumerate(sheet_rows) if row and row[0][0] == "Tabla")
    header = [cell[0] for cell in sheet_rows[start]]
    matrix_body = []
    for row in sheet_rows[start + 1 :]:
        cells = [cell[0] for cell in row]
        tds = [f"<td class='rowhead'>{esc(cells[0])}</td>"]
        for value in cells[1:]:
            has_q, has_s = "Q-" in value, "S-" in value
            css = "m-both" if has_q and has_s else "m-found" if has_q else "m-clear"
            tds.append(f"<td class='{css}'>{esc(value)}</td>")
        matrix_body.append("<tr>" + "".join(tds) + "</tr>")
    matrix = (
        '<div class="matrix-block"><h3 class="matrix-title">Matriz de control: tabla × dimensión de calidad</h3>'
        '<table class="matrix"><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in header) + "</tr></thead>"
        f"<tbody>{''.join(matrix_body)}</tbody></table>"
        '<div class="legend"><span><span class="chip found">Q-nn / Q-Enn</span> problema con evidencia y acción para el Hito 3</span>'
        '<span><span class="chip clear">S-nn</span> dimensión medida sin hallazgos</span></div></div>'
    )
    return (
        "<section>"
        + sec_head(
            "4.4 Diagnóstico de calidad",
            "Seis dimensiones por tabla: cada celda de la matriz remite a un hallazgo o a una medición sin hallazgos.",
        )
        + f'<table class="data"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'
        + matrix
        + "</section>"
    )


def cobertura() -> str:
    rows = read_csv("cobertura.csv")
    cols = '<col style="width:58mm"><col style="width:52mm"><col style="width:42mm"><col style="width:22mm"><col style="width:92mm">'
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
    body = []
    for r in rows:
        chip = {"Sí": "clear", "Parcial": "amber"}.get(r["disponible"], "found")
        body.append(
            f"<tr><td class='q'>{esc(r['pregunta'])}</td><td>{esc(r['campos_necesarios'])}</td><td>{esc(r['tabla_fuente'])}</td>"
            f"<td><span class='chip {chip}'>{esc(r['disponible'])}</span></td><td class='big'>{esc(r['decision'])}</td></tr>"
        )
    return (
        "<section>"
        + sec_head(
            "4.5 Matriz de cobertura",
            "Las tres preguntas del Hito 1 frente a los campos disponibles; el ajuste de cada una se explica.",
        )
        + f'<table class="data"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></section>'
    )


def document() -> str:
    parts = [cover(), fuentes(), diccionario(), calidad(), cobertura()]
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
