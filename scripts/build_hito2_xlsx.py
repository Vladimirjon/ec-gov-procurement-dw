"""Build the Hito 2 Excel workbook with deterministic, standard-library SpreadsheetML OOXML.

Produces deliverables/h2/Proyecto_Grupo5_Hito2.xlsx from the four versioned CSVs:
- docs/h2/fuentes.csv (Template 6.1 + License + SHA-256)
- docs/h2/diccionario.csv (Template 6.2 with grain, roles, units, profilings)
- docs/h2/calidad.csv (Template 6.3 with Q-01..Q-12, Q-E01..Q-E08, S-01..S-04 and 4x6 matrix)
- docs/h2/cobertura.csv (Template 6.4 with P1..P3, availability and decisions)

Only the Python standard library is used (zipfile, xml.etree.ElementTree, csv).
"""

import argparse
import csv
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FUENTES = Path("docs/h2/fuentes.csv")
DEFAULT_DICCIONARIO = Path("docs/h2/diccionario.csv")
DEFAULT_CALIDAD = Path("docs/h2/calidad.csv")
DEFAULT_COBERTURA = Path("docs/h2/cobertura.csv")
DEFAULT_OUTPUT = Path("deliverables/h2/Proyecto_Grupo5_Hito2.xlsx")

FIXED_ZIP_DATETIME = (2026, 11, 21, 0, 0, 0)
MAX_CELL_CHARS = 32767
MAX_SHEET_NAME_LEN = 31

# XML Namespaces
XML_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def sanitize_xml_string(value: str) -> str:
    """Strip XML invalid control characters and validate length."""
    if not isinstance(value, str):
        value = str(value)
    # Valid XML chars: \t, \n, \r, and >= 0x20
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    if len(cleaned) > MAX_CELL_CHARS:
        raise ValueError(f"Cell text exceeds {MAX_CELL_CHARS} chars ({len(cleaned)} chars)")
    if "[VERIFICAR]" in cleaned or "[PENDIENTE]" in cleaned:
        raise ValueError(f"Forbidden placeholder found in cell text: {cleaned[:80]}...")
    return cleaned


def column_letter(col_idx: int) -> str:
    """Convert 1-based column index to Excel column letters (A, B, ..., Z, AA, ...)."""
    result = []
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result.append(chr(65 + remainder))
    return "".join(reversed(result))


def build_content_types_xml(num_sheets: int) -> str:
    """Generate [Content_Types].xml declaring workbook, worksheets and styles."""
    types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Types xmlns="{TYPES_NS}">',
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '  <Default Extension="xml" ContentType="application/xml"/>',
        (
            '  <Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        ),
        (
            '  <Override PartName="/xl/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        ),
    ]
    for idx in range(1, num_sheets + 1):
        types.append(
            f'  <Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    types.append("</Types>")
    return "\n".join(types)


def build_root_rels_xml() -> str:
    """Generate _rels/.rels pointing to xl/workbook.xml."""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_REL_NS}">
  <Relationship Id="rId1" Type="{REL_NS}/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""


def build_workbook_xml(sheet_names: list[str]) -> str:
    """Generate xl/workbook.xml with sheets array."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<workbook xmlns="{XML_NS}" xmlns:r="{REL_NS}">',
        "  <bookViews>",
        '    <workbookView xWindow="0" yWindow="0" windowWidth="24000" windowHeight="14000"/>',
        "  </bookViews>",
        "  <sheets>",
    ]
    for idx, name in enumerate(sheet_names, start=1):
        if len(name) > MAX_SHEET_NAME_LEN:
            raise ValueError(f"Sheet name '{name}' exceeds {MAX_SHEET_NAME_LEN} chars")
        lines.append(f'    <sheet name="{name}" sheetId="{idx}" r:id="rId{idx}"/>')
    lines.append("  </sheets>")
    lines.append("</workbook>")
    return "\n".join(lines)


def build_workbook_rels_xml(num_sheets: int) -> str:
    """Generate xl/_rels/workbook.xml.rels."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Relationships xmlns="{PKG_REL_NS}">',
    ]
    for idx in range(1, num_sheets + 1):
        lines.append(f'  <Relationship Id="rId{idx}" Type="{REL_NS}/worksheet" Target="worksheets/sheet{idx}.xml"/>')
    styles_rid = num_sheets + 1
    lines.append(f'  <Relationship Id="rId{styles_rid}" Type="{REL_NS}/styles" Target="styles.xml"/>')
    lines.append("</Relationships>")
    return "\n".join(lines)


def build_styles_xml() -> str:
    """Generate xl/styles.xml with required fonts, fills, borders, and cellXfs.

    Style indices (s):
    0: Normal text (Calibri 10pt)
    1: Header (Bold white text, dark blue fill #1F4E79, center/middle, wrapText)
    2: Data cell (Normal text, thin gray border, left/top, wrapText)
    3: Data cell bold (Bold text, thin gray border, left/top, wrapText)
    4: Code / ID cell (Consolas 9pt, thin gray border, center/top)
    5: Data cell centered (Normal text, thin gray border, center/top, wrapText)
    6: Status 'Parcial' cell (Bold text, soft yellow fill #FFF2CC, center/top, wrapText)
    7: Status 'Disponible' cell (Bold text, soft green fill #E2EFDA, center/top, wrapText)
    8: Cover Title (Calibri 14pt Bold, dark blue font #1F4E79)
    9: Section Subtitle (Calibri 11pt Bold, light blue fill #D9E1F2, thin border)
    10: Metadata label (Calibri 10pt Bold, light gray fill #F2F2F2, thin border)
    11: Metadata value (Calibri 10pt, thin border, wrapText)
    12: Matrix header (Calibri 10pt Bold, light blue fill #D9E1F2, center/middle, thin border)
    13: Matrix cell (Calibri 10pt, center/middle, thin border)
    """
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="{XML_NS}">
  <fonts count="6">
    <font>
      <sz val="10"/>
      <color theme="1"/>
      <name val="Calibri"/>
      <family val="2"/>
    </font>
    <font>
      <b/>
      <sz val="10"/>
      <color theme="1"/>
      <name val="Calibri"/>
      <family val="2"/>
    </font>
    <font>
      <b/>
      <sz val="14"/>
      <color rgb="FF1F4E79"/>
      <name val="Calibri"/>
      <family val="2"/>
    </font>
    <font>
      <b/>
      <sz val="11"/>
      <color rgb="FF1F4E79"/>
      <name val="Calibri"/>
      <family val="2"/>
    </font>
    <font>
      <b/>
      <sz val="10"/>
      <color rgb="FFFFFFFF"/>
      <name val="Calibri"/>
      <family val="2"/>
    </font>
    <font>
      <sz val="9"/>
      <color theme="1"/>
      <name val="Consolas"/>
      <family val="3"/>
    </font>
  </fonts>
  <fills count="7">
    <fill>
      <patternFill patternType="none"/>
    </fill>
    <fill>
      <patternFill patternType="gray125"/>
    </fill>
    <fill>
      <patternFill patternType="solid">
        <fgColor rgb="FF1F4E79"/>
        <bgColor indexed="64"/>
      </patternFill>
    </fill>
    <fill>
      <patternFill patternType="solid">
        <fgColor rgb="FFF2F2F2"/>
        <bgColor indexed="64"/>
      </patternFill>
    </fill>
    <fill>
      <patternFill patternType="solid">
        <fgColor rgb="FFD9E1F2"/>
        <bgColor indexed="64"/>
      </patternFill>
    </fill>
    <fill>
      <patternFill patternType="solid">
        <fgColor rgb="FFE2EFDA"/>
        <bgColor indexed="64"/>
      </patternFill>
    </fill>
    <fill>
      <patternFill patternType="solid">
        <fgColor rgb="FFFFF2CC"/>
        <bgColor indexed="64"/>
      </patternFill>
    </fill>
  </fills>
  <borders count="2">
    <border>
      <left/>
      <right/>
      <top/>
      <bottom/>
      <diagonal/>
    </border>
    <border>
      <left style="thin">
        <color rgb="FFD9D9D9"/>
      </left>
      <right style="thin">
        <color rgb="FFD9D9D9"/>
      </right>
      <top style="thin">
        <color rgb="FFD9D9D9"/>
      </top>
      <bottom style="thin">
        <color rgb="FFD9D9D9"/>
      </bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="14">
    <!-- 0: Normal -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <!-- 1: Table Header -->
    <xf numFmtId="0" fontId="4" fillId="2" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center" wrapText="1"/>
    </xf>
    <!-- 2: Data cell normal -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="top" wrapText="1"/>
    </xf>
    <!-- 3: Data cell bold -->
    <xf numFmtId="0" fontId="1" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="top" wrapText="1"/>
    </xf>
    <!-- 4: Code / ID cell -->
    <xf numFmtId="0" fontId="5" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="top"/>
    </xf>
    <!-- 5: Data cell centered -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="top" wrapText="1"/>
    </xf>
    <!-- 6: Status Parcial -->
    <xf numFmtId="0" fontId="1" fillId="6" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="top" wrapText="1"/>
    </xf>
    <!-- 7: Status Disponible -->
    <xf numFmtId="0" fontId="1" fillId="5" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="top" wrapText="1"/>
    </xf>
    <!-- 8: Cover Title -->
    <xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 9: Section Subtitle -->
    <xf numFmtId="0" fontId="3" fillId="4" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center" wrapText="1"/>
    </xf>
    <!-- 10: Metadata label -->
    <xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 11: Metadata value -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center" wrapText="1"/>
    </xf>
    <!-- 12: Matrix header -->
    <xf numFmtId="0" fontId="1" fillId="4" borderId="1" xfId="0"
        applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center" wrapText="1"/>
    </xf>
    <!-- 13: Matrix cell -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center" wrapText="1"/>
    </xf>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>"""


def build_worksheet_xml(
    rows_data: list[list[tuple[str, int]]],
    col_widths: list[float],
    freeze_row: int = 1,
    merge_ranges: list[str] | None = None,
) -> str:
    """Build a complete worksheet XML document obeying strict OpenXML child ordering."""
    total_rows = len(rows_data)
    max_cols = max((len(r) for r in rows_data), default=1)
    end_col = column_letter(max_cols)
    dimension_ref = f"A1:{end_col}{max(total_rows, 1)}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{XML_NS}" xmlns:r="{REL_NS}">',
        f'  <dimension ref="{dimension_ref}"/>',
        "  <sheetViews>",
        '    <sheetView tabSelected="0" workbookViewId="0">',
    ]

    if freeze_row > 0:
        lines.append(
            f'      <pane ySplit="{freeze_row}" topLeftCell="A{freeze_row + 1}" '
            'activePane="bottomLeft" state="frozen"/>'
        )

    lines.extend(
        [
            "    </sheetView>",
            "  </sheetViews>",
            '  <sheetFormatPr defaultRowHeight="15"/>',
        ]
    )

    if col_widths:
        lines.append("  <cols>")
        for col_idx, width in enumerate(col_widths, start=1):
            lines.append(f'    <col min="{col_idx}" max="{col_idx}" width="{width:.2f}" customWidth="1"/>')
        lines.append("  </cols>")

    lines.append("  <sheetData>")
    for row_idx, row in enumerate(rows_data, start=1):
        if not row:
            lines.append(f'    <row r="{row_idx}"/>')
            continue
        lines.append(f'    <row r="{row_idx}">')
        for col_idx, (text, style_idx) in enumerate(row, start=1):
            coord = f"{column_letter(col_idx)}{row_idx}"
            clean_text = sanitize_xml_string(text)
            escaped_text = clean_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Use inlineStr with xml:space="preserve"
            lines.append(
                f'      <c r="{coord}" t="inlineStr" s="{style_idx}">'
                f'<is><t xml:space="preserve">{escaped_text}</t></is></c>'
            )
        lines.append("    </row>")
    lines.append("  </sheetData>")

    if merge_ranges:
        lines.append(f'  <mergeCells count="{len(merge_ranges)}">')
        for mrange in merge_ranges:
            lines.append(f'    <mergeCell ref="{mrange}"/>')
        lines.append("  </mergeCells>")

    lines.append('  <pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>')
    lines.append("</worksheet>")
    return "\n".join(lines)


def generate_portada_sheet() -> tuple[list[list[tuple[str, int]]], list[float], int, list[str]]:
    """Generate Portada (Cover) worksheet data."""
    rows: list[list[tuple[str, int]]] = []
    col_widths = [24.0, 48.0, 40.0]
    merges: list[str] = []

    # Row 1: Title
    rows.append([("PROYECTO INTEGRADOR DE BUSINESS INTELLIGENCE — FIS-EPN", 8)])
    merges.append("A1:C1")

    # Row 2: Subtitle
    rows.append([("Hito 2: Adquisición y calidad de datos — Documentación y diagnóstico oficial", 3)])
    merges.append("A2:C2")

    # Row 3: Blank
    rows.append([])

    # Rows 4-9: Project metadata card
    rows.append([("Equipo:", 10), ("Grupo 5", 11), ("", 11)])
    merges.append("B4:C4")
    rows.append([("Sector asignado:", 10), ("Gobierno central del Ecuador", 11), ("", 11)])
    merges.append("B5:C5")
    rows.append([("Fecha de entrega:", 10), ("21/11/26", 11), ("", 11)])
    merges.append("B6:C6")
    rows.append(
        [
            ("Integrantes:", 10),
            ("Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel, Jorge Torres", 11),
            ("", 11),
        ]
    )
    merges.append("B7:C7")
    rows.append(
        [
            ("Entregables oficiales:", 10),
            ("Proyecto_Grupo5_Hito2.pbix (Power BI Desktop) y Proyecto_Grupo5_Hito2.xlsx (Libro de cuatro partes)", 11),
            ("", 11),
        ]
    )
    merges.append("B8:C8")

    # Row 9: Blank
    rows.append([])

    # Row 10: Section Subtitle
    rows.append(
        [
            ("Estructura del libro de Excel (Cuatro partes de la Guía del Hito 2):", 9),
            ("", 9),
            ("", 9),
        ]
    )
    merges.append("A10:C10")

    # Rows 11-16: Table of contents
    rows.append([("Hoja / Sección", 1), ("Nombre de la plantilla", 1), ("Contenido y alcance metodológico", 1)])
    rows.append(
        [
            ("Hoja 1: Portada", 3),
            ("Identificación institucional", 2),
            ("Nombre del equipo (Grupo 5), sector (gobierno central), fecha (21/11/26) y metadatos", 2),
        ]
    )
    rows.append(
        [
            ("Hoja 2: Fuentes", 3),
            ("Plantilla 6.1: Inventario de fuentes", 2),
            (
                "Fichas de procedencia: SERCOP 2021-2025 (5 archivos CSV), catálogo MDEP y directorio gob.ec, "
                "con licencias y SHA-256",
                2,
            ),
        ]
    )
    rows.append(
        [
            ("Hoja 3: Diccionario", 3),
            ("Plantilla 6.2: Diccionario de datos", 2),
            (
                "Grano de cada tabla y diccionario de campos con descripción, tipo/rol, valores válidos, "
                "perfil numérico y unidad",
                2,
            ),
        ]
    )
    rows.append(
        [
            ("Hoja 4: Calidad", 3),
            ("Plantilla 6.3: Diagnóstico de calidad", 2),
            (
                "Diagnóstico en seis dimensiones: hallazgos Q-01..Q-11, Q-E01..Q-E08, S-01..S-04 y "
                "Matriz Tabla × Dimensión",  # noqa: RUF001
                2,
            ),
        ]
    )
    rows.append(
        [
            ("Hoja 5: Cobertura", 3),
            ("Plantilla 6.4: Matriz de cobertura", 2),
            ("Evaluación de viabilidad para P1, P2 y P3, delimitación de alcance, universos y decisiones de ajuste", 2),
        ]
    )

    # Row 17: Blank
    rows.append([])

    # Row 18: Core rule notice
    rows.append(
        [
            (
                "Regla metodológica del Hito 2: Este hito es estrictamente diagnóstico y no realiza "
                "transformaciones ni limpieza de datos. Cada acción propuesta constituye la especificación "
                "de tareas que se ejecutarán en Power Query durante el Hito 3.",
                2,
            )
        ]
    )
    merges.append("A18:C18")

    return rows, col_widths, 0, merges


def generate_fuentes_sheet(
    fuentes_csv_path: Path,
) -> tuple[list[list[tuple[str, int]]], list[float], int, list[str]]:
    """Generate Fuentes worksheet data from fuentes.csv."""
    rows: list[list[tuple[str, int]]] = []
    col_widths = [26.0, 48.0, 24.0, 28.0, 36.0, 30.0, 66.0]

    headers = [
        "Fuente",
        "Entidad y enlace exacto",
        "Formato / conector",
        "Periodo y actualización",
        "Filas y fecha de descarga",
        "Licencia",
        "SHA-256",
    ]
    rows.append([(h, 1) for h in headers])

    with open(fuentes_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                [
                    (r["fuente"], 3),
                    (r["entidad_enlace"], 2),
                    (r["formato_conector"], 5),
                    (r["periodo_actualizacion"], 2),
                    (r["filas_fecha_descarga"], 2),
                    (r["licencia"], 2),
                    (r["sha256"], 4),
                ]
            )

    return rows, col_widths, 1, []


def generate_diccionario_sheet(
    diccionario_csv_path: Path,
) -> tuple[list[list[tuple[str, int]]], list[float], int, list[str]]:
    """Generate Diccionario worksheet grouped by table with its grain header."""
    rows: list[list[tuple[str, int]]] = []
    col_widths = [22.0, 36.0, 24.0, 32.0, 48.0, 16.0]
    merges: list[str] = []

    # Read CSV rows grouped by table
    tables: dict[str, dict] = {}
    with open(diccionario_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tbl = r["tabla"]
            if tbl not in tables:
                tables[tbl] = {"grano": r["grano"], "fields": []}
            tables[tbl]["fields"].append(r)

    field_headers = [
        "Campo",
        "Descripción",
        "Tipo esperado / rol",
        "Valores válidos",
        "Observación del perfil",
        "Unidad",
    ]

    for tbl_name, tbl_data in tables.items():
        if rows:
            rows.append([])  # blank row separation

        # Section header for Table and Grain
        row_num = len(rows) + 1
        header_text = f"Tabla: {tbl_name}  ·  Grano: {tbl_data['grano']}"
        rows.append([(header_text, 9), ("", 9), ("", 9), ("", 9), ("", 9), ("", 9)])
        merges.append(f"A{row_num}:F{row_num}")

        # Field table header
        rows.append([(h, 1) for h in field_headers])

        # Fields data
        for f in tbl_data["fields"]:
            # If measure, highlight role
            is_measure = "Medida" in f["tipo_rol"]
            role_style = 3 if is_measure else 2
            rows.append(
                [
                    (f["campo"], 4 if f["campo"].islower() or "_" in f["campo"] else 3),
                    (f["descripcion"], 2),
                    (f["tipo_rol"], role_style),
                    (f["valores_validos"], 2),
                    (f["observacion_perfil"], 2),
                    (f["unidad"], 5),
                ]
            )

    return rows, col_widths, 0, merges


def generate_calidad_sheet(
    calidad_csv_path: Path,
) -> tuple[list[list[tuple[str, int]]], list[float], int, list[str]]:
    """Generate Calidad worksheet with findings table and Table x Dimension matrix."""
    rows: list[list[tuple[str, int]]] = []
    col_widths = [10.0, 26.0, 16.0, 52.0, 38.0, 48.0, 20.0]
    merges: list[str] = []

    # Section 1 Header
    rows.append(
        [
            ("1. Diagnóstico de calidad multidimensional (Hallazgos Q-01..Q-11, Q-E01..Q-E08 y S-01..S-04)", 9),
            ("", 9),
            ("", 9),
            ("", 9),
            ("", 9),
            ("", 9),
        ]
    )
    merges.append("A1:F1")

    headers = [
        "ID",
        "Tabla · Campo",
        "Dimensión",
        "Problema y evidencia medible",
        "Impacto en las preguntas (P1, P2, P3)",
        "Acción propuesta para el Hito 3",
    ]
    rows.append([(h, 1) for h in headers])

    with open(calidad_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            id_val = r["id"]
            rows.append(
                [
                    (id_val, 4),
                    (r["tabla_campo"], 3),
                    (r["dimension"], 5),
                    (r["problema_evidencia"], 2),
                    (r["impacto_preguntas"], 2),
                    (r["accion_h3"], 2),
                ]
            )

    # Section 2: Table x Dimension Matrix
    rows.append([])  # blank row separation
    matrix_title_row = len(rows) + 1
    rows.append(
        [
            ("2. Matriz de control: Tabla × Dimensión de calidad de datos", 9),  # noqa: RUF001
            ("", 9),
            ("", 9),
            ("", 9),
            ("", 9),
            ("", 9),
            ("", 9),
        ]
    )
    merges.append(f"A{matrix_title_row}:G{matrix_title_row}")

    matrix_headers = [
        "Tabla",
        "Completitud",
        "Validez",
        "Consistencia",
        "Unicidad",
        "Exactitud",
        "Oportunidad",
    ]
    rows.append([(h, 12) for h in matrix_headers])

    # Pre-defined mapping matching the findings across the 4 queries
    matrix_rows = [
        (
            "Procesos_SERCOP",
            "Q-03",
            "Q-04, Q-E08",
            "Q-07",
            "Q-06",
            "S-01",
            "Q-10",
        ),
        (
            "Licitaciones_SERCOP",
            "Q-01",
            "Q-04, Q-05, Q-11",
            "Q-08",
            "S-04",
            "Q-12",
            "Q-03",
        ),
        (
            "Adjudicaciones_SERCOP",
            "Q-02, Q-03",
            "Q-04, Q-05",
            "S-02",
            "Q-06",
            "Q-09",
            "S-03",
        ),
        (
            "Entidades_MDEP",
            "Q-E05",
            "Q-E01, Q-E03",
            "Q-E06",
            "Q-E02",
            "Q-E07",
            "Q-E04",
        ),
    ]

    for tbl_name, comp, val, cons, unic, exac, oport in matrix_rows:
        rows.append(
            [
                (tbl_name, 3),
                (comp, 13),
                (val, 13),
                (cons, 13),
                (unic, 13),
                (exac, 13),
                (oport, 13),
            ]
        )

    return rows, col_widths, 0, merges


def generate_cobertura_sheet(
    cobertura_csv_path: Path,
) -> tuple[list[list[tuple[str, int]]], list[float], int, list[str]]:
    """Generate Cobertura worksheet data from cobertura.csv."""
    rows: list[list[tuple[str, int]]] = []
    col_widths = [32.0, 36.0, 24.0, 16.0, 56.0]

    headers = [
        "Pregunta de negocio",
        "Campos necesarios",
        "Tabla / fuente",
        "¿Disponible?",
        "Decisión y justificación metodológica",
    ]
    rows.append([(h, 1) for h in headers])

    with open(cobertura_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            disp = r["disponible"]
            disp_style = 6 if disp == "Parcial" else (7 if disp == "Sí" else 2)
            rows.append(
                [
                    (r["pregunta"], 3),
                    (r["campos_necesarios"], 2),
                    (r["tabla_fuente"], 5),
                    (disp, disp_style),
                    (r["decision"], 2),
                ]
            )

    return rows, col_widths, 1, []


def build_workbook(
    fuentes_csv: Path,
    diccionario_csv: Path,
    calidad_csv: Path,
    cobertura_csv: Path,
    output_xlsx: Path,
) -> None:
    """Orchestrate sheet generation and pack into deterministic .xlsx zip."""
    sheet_generators = [
        ("Portada", generate_portada_sheet()),
        ("Fuentes", generate_fuentes_sheet(fuentes_csv)),
        ("Diccionario", generate_diccionario_sheet(diccionario_csv)),
        ("Calidad", generate_calidad_sheet(calidad_csv)),
        ("Cobertura", generate_cobertura_sheet(cobertura_csv)),
    ]

    sheet_names = [name for name, _ in sheet_generators]
    num_sheets = len(sheet_names)

    # Prepare package parts in memory
    files: dict[str, str] = {
        "[Content_Types].xml": build_content_types_xml(num_sheets),
        "_rels/.rels": build_root_rels_xml(),
        "xl/workbook.xml": build_workbook_xml(sheet_names),
        "xl/_rels/workbook.xml.rels": build_workbook_rels_xml(num_sheets),
        "xl/styles.xml": build_styles_xml(),
    }

    for idx, (_name, (rows_data, col_widths, freeze_row, merges)) in enumerate(sheet_generators, start=1):
        sheet_xml = build_worksheet_xml(rows_data, col_widths, freeze_row, merges)
        files[f"xl/worksheets/sheet{idx}.xml"] = sheet_xml

    # Verify all generated XMLs are well-formed before writing to ZIP
    for path, content in files.items():
        try:
            ET.fromstring(content)  # noqa: S314
        except ET.ParseError as err:
            raise ValueError(f"Malformed XML generated for {path}: {err}") from err

    # Ensure output parent directory exists
    output_xlsx.parent.mkdir(parents=True, exist_ok=True)

    # Write deterministic ZIP
    with ZipFile(output_xlsx, mode="w", compression=ZIP_DEFLATED) as zf:
        for file_path in sorted(files.keys()):
            content_bytes = files[file_path].encode("utf-8")
            zinfo = ZipInfo(filename=file_path, date_time=FIXED_ZIP_DATETIME)
            zinfo.compress_type = ZIP_DEFLATED
            zf.writestr(zinfo, content_bytes)

    print(f"Generated {output_xlsx} ({output_xlsx.stat().st_size:,} bytes, {num_sheets} sheets)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fuentes-csv", type=Path, default=REPO_ROOT / DEFAULT_FUENTES)
    parser.add_argument("--diccionario-csv", type=Path, default=REPO_ROOT / DEFAULT_DICCIONARIO)
    parser.add_argument("--calidad-csv", type=Path, default=REPO_ROOT / DEFAULT_CALIDAD)
    parser.add_argument("--cobertura-csv", type=Path, default=REPO_ROOT / DEFAULT_COBERTURA)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    for p, name in [
        (args.fuentes_csv, "Fuentes CSV"),
        (args.diccionario_csv, "Diccionario CSV"),
        (args.calidad_csv, "Calidad CSV"),
        (args.cobertura_csv, "Cobertura CSV"),
    ]:
        if not p.is_file():
            print(f"Error: {name} not found at {p}", file=sys.stderr)
            return 1

    try:
        build_workbook(
            fuentes_csv=args.fuentes_csv,
            diccionario_csv=args.diccionario_csv,
            calidad_csv=args.calidad_csv,
            cobertura_csv=args.cobertura_csv,
            output_xlsx=args.output,
        )
    except Exception as exc:
        print(f"Error generating workbook: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
