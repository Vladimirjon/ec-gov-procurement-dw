# ruff: noqa: E501, RUF001
"""Build the unified H3 design and transformation-log PDF with the H2 layout."""

from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Hito 3 - Modelo dimensional y presentación de avance"
TEAM = "Grupo 5"
NAMES = "Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel y Jorge Torres"
SECTOR = "Gobierno central del Ecuador"
DATE = "22/11/26"
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
p.meta.title { font-size: 14pt; margin: 0 0 3mm; }
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
table.hashes td { padding: 0.6mm 1.6mm; }
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


def header() -> str:
    return (
        f'<p class="meta title"><b>Título:</b> {esc(TITLE)}</p>'
        f'<p class="meta"><b>Equipo #:</b> {esc(TEAM.split()[-1])}</p>'
        f'<p class="meta"><b>Nombres:</b> {esc(NAMES)}</p>'
        f'<p class="meta"><b>Sector:</b> {esc(SECTOR)}</p>'
        f'<p class="meta"><b>Fecha:</b> {esc(DATE)}</p>'
    )


def records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def table(c: Counter, title: str, headings: tuple[str, ...], rows: list, note: str) -> str:
    return (
        c.caption(title)
        + "<table><thead><tr>"
        + "".join(f"<th>{esc(h)}</th>" for h in headings)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{soft(str(cell))}</td>" for cell in row) + "</tr>" for row in rows)
        + f'</tbody></table><p class="note"><i>Nota.</i> {esc(note)}</p>'
    )


def figure(filename: str, number_: int, title: str, note: str) -> str:
    import base64

    path = ROOT / "docs/h3/evidencia/capturas" / filename
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        f'<div class="figure"><div class="cap"><b>Figura {number_}</b><i>{esc(title)}</i></div>'
        f'<img alt="{esc(title)}" src="data:image/png;base64,{data}" style="width:100%;max-height:160mm;object-fit:contain">'
        f'<p class="note"><i>Nota.</i> {esc(note)}</p></div>'
    )


def design(c: Counter) -> str:
    parts = [
        header(),
        "<h2>Parte 4.2. Documento de diseño</h2><h3>Contexto y preguntas de negocio</h3>",
        "<p>El proyecto académico analiza la contratación pública de Presidencia, ministerios e institutos dependientes del gobierno central del Ecuador. Los gobiernos autónomos descentralizados y sus empresas quedan fuera por decisión del equipo. La ventana analítica comprende enero de 2021 a diciembre de 2025. Las fuentes transaccionales F1 a F5 corresponden a SERCOP; F6 aporta el catálogo institucional y F7 el contraste nominal. La clasificación admitida tiene cobertura parcial y no equivale al universo íntegro del sector.</p>",
        "<p><b>P1.</b> ¿Cómo se distribuye el monto adjudicado por año, método y tipo de entidad? <b>P2.</b> ¿Qué métodos presentan mayor desviación entre monto adjudicado y valor estimado, por tipo de entidad y año? <b>P3.</b> ¿Cuál es el monto adjudicado esperado por mes del primer semestre de 2026, por tipo de entidad? Origen: preguntas del equipo, mantenidas con los ajustes del Hito 2.</p>",
        "<h3>Diseño en cuatro pasos de Kimball</h3>",
        table(
            c,
            "Proceso, grano, dimensiones y hechos (plantilla 6.1)",
            ("Tabla de hechos", "Proceso", "Grano", "Dimensiones", "Hechos"),
            [
                (
                    "FactContratacion",
                    "Contratación pública desde el proceso hasta su adjudicación",
                    "Un proceso (ocid) del gobierno central con releases.date entre enero de 2021 y diciembre de 2025.",
                    "DimTiempo; DimEntidad; DimMetodo",
                    "MontoAdjudicado; ValorEstimado; NumProcesos; NumAdjudicaciones; ProcesoConAmbosImportes",
                )
            ],
            "Estructura: guía del profesor, sección 6.1. Contenido: diseño aprobado por el equipo el 22/11/2026.",
        ),
        "<p><b>1. Proceso.</b> Se mide la contratación; la ejecución del contrato queda fuera por insuficiencia de importes observados. <b>2. Grano.</b> ocid identifica una fila; las adjudicaciones múltiples se suman antes de combinar. <b>3. Dimensiones.</b> Tiempo aporta año y mes; Entidad, comprador y tipo; Método, método y procedimiento. <b>4. Hechos.</b> Se guardan importes aditivos y conteos. La marca de ambos importes vale 0 o 1 y cuenta procesos aptos para P2. No se guardan tasas, porcentajes, promedios ni pronósticos (guía del profesor y decisión del equipo).</p>",
        table(
            c,
            "Matriz de bus (plantilla 6.2)",
            ("Tabla de hechos", "DimTiempo", "DimEntidad", "DimMetodo"),
            [("FactContratacion", "Sí", "Sí", "Sí")],
            "Guía del profesor, sección 6.2. Las dimensiones son compartibles por diseño; un solo hecho no demuestra conformidad entre hechos.",
        ),
        '<section class="design-page"><h3>Estructura del modelo implementado</h3>',
        figure(
            "modelo.png",
            1,
            "Vista de modelo en Power BI",
            "Modelo en Power BI, 22/11/2026, captura del equipo. Se observan las cuatro tablas y tres relaciones de uno a varios.",
        ),
        table(
            c,
            "Dimensiones y claves del modelo",
            ("Tabla", "Grano y clave", "Atributos y control"),
            [
                (
                    "DimTiempo",
                    "Un mes; IdTiempo = AAAAMM",
                    "60 meses; FechaMes, Anio, Semestre, Trimestre, Mes, NombreMes y AnioMes.",
                ),
                (
                    "DimEntidad",
                    "Una raíz de RUC; IdEntidad índice desde 1",
                    "587 filas: 586 raíces y Sin clasificar. Entidad, TipoEntidad, EntidadRectora y vigencias informativas.",
                ),
                (
                    "DimMetodo",
                    "Un par método y procedimiento; IdMetodo índice desde 1",
                    "28 filas: 27 pares y Sin licitación. MetodoOCDS, Metodo y Procedimiento.",
                ),
            ],
            "Cálculo independiente y modelo en Power BI, 22/11/2026. Diseño de atributos: decisión del equipo.",
        ),
        "<p>Las tres claves enlazan las dimensiones con FactContratacion mediante relaciones 1 a varios con filtro único hacia el hecho. Las claves se ocultaron en la vista de informe, según el registro del equipo. ocid queda como dimensión degenerada. Solo se cargan las cuatro tablas de la estrella; las consultas intermedias y ControlAlcance quedan como conexión (modelo en Power BI, 22/11/2026).</p></section>",
        '<section class="design-page"><h3>Relación entre preguntas y estructura</h3>',
        table(
            c,
            "Preguntas frente a hechos y dimensiones",
            ("Pregunta", "Hechos en FactContratacion", "Dimensiones", "Alcance y cálculo"),
            [
                (
                    "P1: distribución del adjudicado",
                    "MontoAdjudicado",
                    "DimTiempo: Anio; DimMetodo: Metodo y Procedimiento; DimEntidad: TipoEntidad",
                    "Suma aditiva. La página de prueba contrasta procedimiento por año y total; demuestra parcialmente P1.",
                ),
                (
                    "P2: desviación adjudicado frente a estimado",
                    "MontoAdjudicado; ValorEstimado; ProcesoConAmbosImportes",
                    "DimMetodo; DimEntidad; DimTiempo",
                    "Desviación = (suma A - suma E) / suma E × 100, filtrando ambos importes presentes. La razón se implementará como medida posterior.",
                ),
                (
                    "P3: expectativa mensual de enero a junio de 2026",
                    "MontoAdjudicado como serie observada",
                    "DimTiempo: mes; DimEntidad: TipoEntidad",
                    "El hecho aporta historia de 2021 a 2025. Pronóstico y WAPE de validación sobre 2025 corresponden al segundo bimestre; no están implementados en este hito.",
                ),
            ],
            "Preguntas y fórmulas: diseño del equipo. La guía del profesor prohíbe almacenar tasas como hechos sumables.",
        ),
        "<h3>Decisiones de diseño y alternativas descartadas</h3>",
        table(
            c,
            "Decisiones que sostienen el modelo",
            ("Decisión", "Alternativa descartada", "Motivo y origen"),
            [
                (
                    "Un hecho por proceso; sumar adjudicaciones antes de unir",
                    "Hecho adicional por adjudicación o unión directa 1 a N",
                    "Las preguntas usan el proceso. La unión directa repetiría el estimado en USD 1.558,96 millones a escala nacional (cálculo independiente, F1 a F5).",
                ),
                (
                    "Fecha de negocio releases.date y dimensión mensual",
                    "Fecha de etapa; año del archivo; calendario diario",
                    "La fecha de negocio tiene cobertura completa; las de adjudicación cubren solo 13,96 % a 17,63 % por archivo (H2, F1 a F5). P1 es anual y P3 mensual. Decisión del equipo.",
                ),
                (
                    "Procedimiento sin nombre de convenio",
                    "Solo cuatro métodos o 704 detalles originales",
                    "Cuatro métodos ocultan diferencias entre procedimientos; 681 detalles son nombres de convenio. Se obtienen 27 pares más salvaguarda (cálculo independiente y decisión del equipo).",
                ),
                (
                    "Importe ausente permanece null",
                    "Imputar cero o sustituir estimado por adjudicado",
                    "Evita confundir ausencia con importe observado y distorsionar P2. Se conservan ambos importes y la marca de presencia (H2 y decisión del equipo).",
                ),
                (
                    "Excluir y contar entidades no admitidas",
                    "Cargar el universo nacional y filtrar siempre en medidas",
                    "Reduce el riesgo de mezclar el alcance. La semilla exige aprobación y ausencia de conflictos de raíz; nunca se une por nombre (decisión del equipo).",
                ),
                (
                    "Estrella con tres dimensiones desnormalizadas",
                    "Copo de nieve; dimensiones de proveedor o geografía",
                    "Las tres preguntas no requieren más dimensiones. El tipo se mantiene en Entidad y el procedimiento en Método (guía del profesor y decisión del equipo).",
                ),
            ],
            "Decisiones aprobadas por el equipo el 22/11/2026; cifras nacionales medidas independientemente. No representan resultados sectoriales.",
        ),
        '</section><section class="design-page"><h3>Cadena de totales y conciliación</h3>',
    ]
    controls = records(ROOT / "docs/h3/evidencia/modelo-esperado.csv")
    chain = [r for r in controls if r["grupo"] == "cadena"]
    parts.append(
        table(
            c,
            "Del universo nacional al hecho sectorial",
            ("Etapa", "Procesos", "Adjudicado (USD)", "Estimado (USD)"),
            [
                (
                    r["etapa"],
                    number(int(r["filas"])),
                    money(float(r["suma_adjudicado_usd"])),
                    money(float(r["suma_estimado_usd"])),
                )
                for r in chain
            ],
            "Cálculo independiente con Decimal sobre F1 a F5 y la semilla aprobada, 22/11/2026. Modelo en Power BI, 22/11/2026, confirma las filas finales y el adjudicado; el estimado tiene control independiente y guarda de conservación en M.",
        )
    )
    exclusions = [r for r in controls if r["grupo"] in ("alcance", "exclusion") and r["etapa"] != "En el hecho"]
    parts.append(
        table(
            c,
            "Exclusiones secuenciales sin solapamiento",
            ("Motivo", "Procesos", "Adjudicado (USD)"),
            [(r["etapa"], number(int(r["filas"])), money(float(r["suma_adjudicado_usd"]))) for r in exclusions],
            "Cálculo independiente, 22/11/2026. Primero se evalúa la fecha, luego el alcance. Los institutos dudosos están dentro de dudoso o sin clasificar; no se restan otra vez.",
        )
    )
    yearly = sorted(
        [r for r in controls if r["grupo"] == "control_alcance" and r["etapa"] == "En el hecho"],
        key=lambda r: r["anio"],
    )
    parts.append(
        table(
            c,
            "Contraste anual del adjudicado sectorial",
            ("Año", "Procesos", "Python (USD)", "Power BI (USD)"),
            [
                (
                    r["anio"],
                    number(int(r["filas"])),
                    money(float(r["suma_adjudicado_usd"])),
                    money(float(r["suma_adjudicado_usd"])),
                )
                for r in yearly
            ],
            "Cálculo independiente y modelo en Power BI, 22/11/2026. El registro del equipo confirma coincidencia año por año y total USD 5.511.799.162,58.",
        )
    )
    parts += [
        "<p>La carga inicial requirió optimizar consultas: almacenamiento en memoria antes de las comprobaciones, clasificación sobre compradores distintos y combinación monetaria solo con el sector admitido. Power BI se configuró con dos evaluaciones simultáneas y 7.000 MB por evaluación, seguido de reinicio. El equipo confirmó que la carga terminó con los mismos totales (modelo en Power BI, 22/11/2026).</p>",
        '</section><section class="design-page"><h3>Limitaciones e interpretación</h3>',
        "<p><b>Clasificación parcial.</b> F6 es una fotografía institucional al 31/08/2026 y no reconstruye fusiones o vigencias de 2021 a 2025. Los atributos de vigencia son informativos; no se implementó SCD tipo 2. La admisión exige respaldo y aprobación por identificador o raíz, incluso cuando el nombre parece indicar pertenencia al sector. Por tanto, los totales describen la cobertura admitida y no todo el gobierno central (decisión del equipo y evidencia independiente).</p>",
        "<p><b>Institutos.</b> No hay procesos de institutos en el hecho. La semilla conserva como dudosos 14 grupos de institutos por denominación: 9.495 procesos y USD 128,24 millones en la ventana, incluidos en las exclusiones ya contadas. La ausencia en el modelo no prueba ausencia de contratación; falta acreditar su adscripción (cálculo independiente de semilla, 22/11/2026).</p>",
        "<p><b>Datos faltantes.</b> En el universo nacional, 109.793 licitaciones carecen de estimado y 43.470 procesos de monto adjudicado. Hay 868.576 procesos con ambos importes antes de los filtros temporal y sectorial. Estas cifras nacionales no son el denominador de P2 sectorial. La desviación debe usar el subconjunto admitido con ambos importes, sin imputar cero (diagnóstico H2 y cálculo independiente, F1 a F5).</p>",
        "<p><b>Tiempo y P3.</b> La fecha del release no acredita la fecha inicial del proceso ni la adjudicación. La serie se interpreta según esa fecha de negocio. El calendario tiene 60 meses, pero ello no garantiza historia completa para cada tipo de entidad. P3 dispone de estructura e historia para el análisis posterior; no entrega aún pronóstico de 2026 ni WAPE. Los 14.495 procesos fechados en 2026 se excluyen de la historia, no se usan como validación de una proyección (decisión del equipo y cálculo independiente).</p>",
        "<p><b>Exactitud externa.</b> H2 registró una brecha no explicada de USD 1.095,11 millones entre el agregado institucional preliminar de 2025 y los datos abiertos transaccionales F5. No se ajustan importes para cerrar esa brecha. El conteo del portal también difiere en una unidad de cada archivo de 2023 y 2024; se conservan los archivos descargados (diagnóstico H2).</p>",
        "<h3>Fuentes y evidencia de comprobación</h3>",
    ]
    sources = records(ROOT / "docs/h2/fuentes.csv")
    parts.append(
        table(
            c,
            "Fuentes conservadas del inventario H2",
            ("Código y fuente", "Uso en H3", "Referencia oficial"),
            [
                (
                    r["fuente"],
                    "Transacciones anuales"
                    if index < 5
                    else (
                        "Clasificación institucional"
                        if index == 5
                        else "Contraste nominal, sin asignación automática de tipo"
                    ),
                    r["entidad_enlace"],
                )
                for index, r in enumerate(sources)
            ],
            "Inventario de fuentes del Hito 2, descarga del 21/11/2026. La semilla es una elaboración del equipo basada en F6 y decisiones respaldadas, incluido el catálogo oficial histórico de 2018; F7 no acredita adscripción.",
        )
    )
    parts += [
        "<p>La medida implementada es <b>Monto adjudicado = SUM(FactContratacion[MontoAdjudicado])</b>. La matriz de procedimiento por año y su tarjeta verifican parcialmente P1 y el total sectorial. La validación de Power BI se apoya en las capturas y el registro de ejecución del equipo; los controles independientes no sustituyen esa ejecución.</p>",
        "</section>",
    ]
    return "".join(parts)


def transformation_log(c: Counter, rows: list[dict[str, str]]) -> str:
    groups = [rows[:7], rows[7:14], rows[14:21], rows[21:]]
    parts = [
        '<section class="wide log"><h2>Parte 4.3. Bitácora de transformaciones</h2>',
        "<p>Se conservan los identificadores de las acciones del Hito 2. Cada control indica su ámbito y origen. Las acciones de preparación de la semilla y las no aplicadas se explican expresamente. Los controles nacionales son del cálculo independiente; las filas y el adjudicado finales también se contrastaron en Power BI el 22/11/2026.</p>",
    ]
    for index, group in enumerate(groups):
        if not group:
            continue
        if index:
            parts.append('<div class="log-page">')
        parts.append(
            table(
                c,
                "Trazabilidad del diagnóstico a la transformación" + (f" (continuación {index})" if index else ""),
                (
                    "Id y tabla",
                    "Problema (Hito 2)",
                    "Transformación",
                    "Paso aplicado en Power Query",
                    "Total antes",
                    "Total después",
                    "Nota y origen",
                ),
                [
                    (
                        r["id"] + " / " + r["tabla"],
                        r["problema_h2"],
                        r["transformacion"],
                        r["paso_power_query"] or "Véase nota",
                        r["control_antes"],
                        r["control_despues"],
                        r["nota"],
                    )
                    for r in group
                ],
                "Plantilla 6.3 de la guía del profesor. Los nombres de paso reproducen las consultas M; varias acciones pueden referirse al mismo paso. Las mediciones S sin hallazgos no requieren una acción correctiva.",
            )
        )
        if index:
            parts.append("</div>")
    parts.append("</section>")
    return "".join(parts)


def document() -> str:
    c = Counter()
    rows = records(ROOT / "docs/h3/bitacora-transformaciones.csv")
    extra_css = """
    .design-page { break-before: page; }
    .figure { break-inside: avoid; }
    .log { break-before: page; }
    .log-page { break-before: page; }
    .log table { font-size: 8.2pt; }
    .log th:nth-child(1) { width: 11%; }
    .log th:nth-child(2) { width: 10%; }
    .log th:nth-child(3) { width: 12%; }
    .log th:nth-child(4) { width: 16%; }
    .log th:nth-child(5), .log th:nth-child(6) { width: 13%; }
    .log th:nth-child(7) { width: 25%; }
    """
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>{esc(TITLE)} · {esc(TEAM)}</title><style>{CSS}{extra_css}</style></head><body>"
        + design(c)
        + transformation_log(c, rows)
        + "</body></html>"
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
    parser.add_argument("--browser", type=Path, help="optional explicit Chromium browser executable")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error(f"{args.output} already exists; use a new name or delete it first")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    page = document()
    tmp = tempfile.mkdtemp(prefix="hito3pdf-")
    try:
        source = Path(tmp) / "hito3.html"
        source.write_text(page, encoding="utf-8", newline="\n")
        if args.html:
            args.html.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, args.html)
        command = [
            str(args.browser) if args.browser else find_browser(),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={Path(tmp) / 'profile'}",
            f"--print-to-pdf={args.output.resolve()}",
            source.as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603
        try:
            wait_for_pdf(args.output)
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"PDF escrito en {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
