"""Build the Hito 1 Word document with deterministic, standard-library OOXML.

Only the project's documented Markdown subset is supported. Paths supplied on the
CLI are relative to the repository root, independently of the working directory.
"""

import argparse
from datetime import UTC, datetime
import os
from pathlib import Path
import posixpath
import re
from urllib.parse import quote, urlsplit, urlunsplit
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


# All dimensions use twips (1/20 pt); font sizes use half-points.
PAGE_WIDTH = 11906
PAGE_HEIGHT = 16838
PAGE_MARGIN = 1021  # 1.8 cm (left and right), rounded to the nearest twip.
PAGE_MARGIN_VERTICAL = 907  # 1.6 cm (top and bottom).
CONTENT_WIDTH = PAGE_WIDTH - 2 * PAGE_MARGIN
BODY_SIZE = 20
TITLE_SIZE = 28
HEADING1_SIZE = 24
HEADING2_SIZE = 22
TABLE_SIZE = 17
NOTE_SIZE = 17
HEADER_SIZE = 20
CODE_SIZE = 16
BODY_AFTER = 60
TABLE_GAP = 90
CELL_VERTICAL_MARGIN = 40
CELL_HORIZONTAL_MARGIN = 90
MAX_WORD_CHARS = 14
WORD_CHAR_TWIPS = 85  # about one character of the table font
FONT = "Times New Roman"
CODE_FONT = "Consolas"
ZIP_DATE = (2026, 11, 8, 0, 0, 0)
DEFAULT_DATE = "2026-11-08T00:00:00Z"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("docs/requirements/hito1.md")
DEFAULT_OUTPUT = Path("deliverables/h1/Hito1_BravoFreireGuajanPasquelTorres.docx")
GITHUB_BASE = "https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
XML = "http://www.w3.org/XML/1998/namespace"
for prefix, namespace in [("w", W), ("r", R), ("cp", CP), ("dc", DC), ("dcterms", DCTERMS), ("xsi", XSI)]:
    ET.register_namespace(prefix, namespace)

INLINE = re.compile(
    r"\\(?:[^\w\s]|_)|`[^`]+`|\[(?:\\.|[^\]\\])+\]\((?:\\.|[^)\\])+\)"
    r"|\*\*(?:\\.|[^\\])+?\*\*|\*(?:\\.|[^*\\])+?\*"
)
SEPARATOR = re.compile(r":?-{3,}:?")


def element(parent, tag, **attributes):
    """Append a WordprocessingML element with qualified attributes."""
    return ET.SubElement(parent, f"{{{W}}}{tag}", {f"{{{W}}}{k}": str(v) for k, v in attributes.items()})


def xml_bytes(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def split_cells(line):
    # A pipe escaped by an odd number of backslashes is part of the cell.
    cells, current = [], []
    escaped = False
    for character in line.strip()[1:-1]:
        if character == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        escaped = character == "\\" and not escaped
    cells.append("".join(current).strip())
    return cells


def is_table_line(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def parse_markdown(markdown):
    """Return (kind, content) blocks, dropping internal material before validation."""
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    markdown = re.split(r"^##\s+Criterios de aceptación del hito[^\n]*$", markdown, maxsplit=1, flags=re.MULTILINE)[0]
    lines = markdown.splitlines()
    blocks = []
    index = 0
    title_seen = False
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line:
            continue
        heading = re.fullmatch(r"(#{1,3})\s+(.+)", line)
        if heading:
            level, value = len(heading[1]), heading[2]
            if level == 1:
                if not title_seen:
                    blocks.append(("title", value))
                    title_seen = True
            else:
                blocks.append((f"heading{level - 1}", value))
        elif is_table_line(line):
            if index >= len(lines) or not is_table_line(lines[index]):
                raise ValueError("Table is missing its separator row.")
            header = split_cells(line)
            separator = split_cells(lines[index])
            if len(separator) != len(header) or not all(SEPARATOR.fullmatch(cell) for cell in separator):
                raise ValueError("Invalid table separator row.")
            index += 1
            rows = [header]
            while index < len(lines) and is_table_line(lines[index]):
                row = split_cells(lines[index])
                if len(row) != len(header):
                    raise ValueError("Table rows must have the same number of columns.")
                rows.append(row)
                index += 1
            if not blocks or blocks[-1][0] != "paragraph" or not blocks[-1][1].startswith("Tabla: "):
                raise ValueError("Table requires a caption: add 'Tabla: <title>' immediately before it.")
            caption = blocks.pop()[1][7:].strip()
            if not caption:
                raise ValueError("Table caption must not be empty.")
            blocks.append(("table", (caption, rows)))
        elif line.startswith("- "):
            value = line[2:]
            while index < len(lines) and lines[index].startswith("  ") and lines[index].strip():
                value += " " + lines[index].strip()
                index += 1
            blocks.append(("bullet", value))
        else:
            value = line
            while index < len(lines) and lines[index].strip():
                following = lines[index].strip()
                if following.startswith(("#", "- ")) or is_table_line(following):
                    break
                value += " " + following
                index += 1
            if value.startswith("Nota: ") and blocks and blocks[-1][0] == "table":
                blocks.append(("note", value[6:]))
            else:
                blocks.append(("paragraph", value))
    return blocks


def hyperlink_target(target):
    target = re.sub(r"\\([^\w\s]|_)", r"\1", target)
    parts = urlsplit(target)
    if not parts.scheme and not parts.netloc and parts.path.startswith("../"):
        path = posixpath.normpath(posixpath.join("docs/requirements", parts.path))
        parts = urlsplit(GITHUB_BASE + quote(path, safe="/%"))
        original = urlsplit(target)
        parts = parts._replace(query=original.query, fragment=original.fragment)
    return urlunsplit(parts._replace(fragment=quote(parts.fragment, safe="%/-._~!$&'()*+,;=:@?")))


def add_run(parent, text, *, size=BODY_SIZE, bold=False, italic=False, code=False, link=False):
    run = element(parent, "r")
    properties = element(run, "rPr")
    if link:
        element(properties, "rStyle", val="Hyperlink")
    font = CODE_FONT if code else FONT
    element(properties, "rFonts", ascii=font, hAnsi=font, cs=font)
    if bold:
        element(properties, "b")
    if italic:
        element(properties, "i")
    element(properties, "color", val="0563C1" if link else "000000")
    element(properties, "sz", val=CODE_SIZE if code else size)
    element(properties, "szCs", val=CODE_SIZE if code else size)
    if link:
        element(properties, "u", val="single")
    element(properties, "lang", val="es-EC")
    node = element(run, "t")
    node.set(f"{{{XML}}}space", "preserve")
    node.text = text


def add_inline(parent, text, relationships, **formatting):
    cursor = 0
    for match in INLINE.finditer(text):
        if match.start() > cursor:
            add_run(parent, text[cursor : match.start()], **formatting)
        token = match[0]
        if token.startswith("\\"):
            add_run(parent, token[1:], **formatting)
        elif token.startswith("`"):
            add_run(parent, token[1:-1], **{**formatting, "code": True})
        elif token.startswith("["):
            label, target = token[1:].rsplit("](", 1)
            relation_id = f"rId{len(relationships) + 1}"
            ET.SubElement(
                relationships,
                f"{{{REL}}}Relationship",
                Id=relation_id,
                Type=f"{R}/hyperlink",
                Target=hyperlink_target(target[:-1]),
                TargetMode="External",
            )
            link = element(parent, "hyperlink")
            link.set(f"{{{R}}}id", relation_id)
            add_inline(link, label, relationships, **{**formatting, "link": True})
        else:
            delimiter = "**" if token.startswith("**") else "*"
            style = "bold" if delimiter == "**" else "italic"
            add_inline(parent, token[len(delimiter) : -len(delimiter)], relationships, **{**formatting, style: True})
        cursor = match.end()
    if cursor < len(text):
        add_run(parent, text[cursor:], **formatting)


def add_paragraph(
    parent, *, style=None, align="both", keep=False, page_break=False, before=0, after=BODY_AFTER, bullet=False
):
    paragraph = element(parent, "p")
    properties = element(paragraph, "pPr")
    if style:
        element(properties, "pStyle", val=style)
    if keep:
        element(properties, "keepNext")
    if page_break:
        element(properties, "pageBreakBefore")
    if bullet:
        numbering = element(properties, "numPr")
        element(numbering, "ilvl", val=0)
        element(numbering, "numId", val=1)
    element(properties, "spacing", before=before, after=after, line=240, lineRule="auto")
    if not bullet:
        element(properties, "ind", left=0, right=0, firstLine=0)
    element(properties, "jc", val=align)
    return paragraph


def column_widths(rows):
    count = len(rows[0])
    if count * 0.08 > 1:
        raise ValueError("Tables with more than 12 columns cannot satisfy the 8% minimum column width.")
    weights = [max(8, min(60, sum(len(row[column]) for row in rows) / len(rows))) for column in range(count)]
    floor = (CONTENT_WIDTH * 8 + 99) // 100
    # A column should at least fit its longest word (capped, so long code tokens wrap).
    minima = []
    for column in range(count):
        longest = max(len(word) for row in rows for word in row[column].split() or [""])
        needed = min(longest, MAX_WORD_CHARS) * WORD_CHAR_TWIPS + 2 * CELL_HORIZONTAL_MARGIN
        minima.append(max(floor, needed))
    if sum(minima) > CONTENT_WIDTH:
        minima = [floor] * count
    # Constrained proportional allocation: pin undersized columns, then redistribute.
    widths = [0] * count
    active = list(range(count))
    remaining = CONTENT_WIDTH
    while active:
        total = sum(weights[i] for i in active)
        small = [i for i in active if remaining * weights[i] / total < minima[i]]
        if not small:
            for i in active:
                widths[i] = int(remaining * weights[i] / total)
            for i in active[: CONTENT_WIDTH - sum(widths)]:
                widths[i] += 1
            break
        for i in small:
            widths[i] = minima[i]
            remaining -= minima[i]
            active.remove(i)
    return widths


def add_table(body, rows, relationships):
    table = element(body, "tbl")
    properties = element(table, "tblPr")
    element(properties, "tblW", w=CONTENT_WIDTH, type="dxa")
    borders = element(properties, "tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        vertical = side in {"left", "right", "insideV"}
        element(
            borders,
            side,
            val="nil" if vertical else "single",
            sz=2 if side == "insideH" else 8,
            color="7F7F7F" if side == "insideH" else "000000",
        )
    element(properties, "tblLayout", type="fixed")
    margins = element(properties, "tblCellMar")
    for side in ["top", "left", "bottom", "right"]:
        width = CELL_VERTICAL_MARGIN if side in {"top", "bottom"} else CELL_HORIZONTAL_MARGIN
        element(margins, side, w=width, type="dxa")
    # Render cells once: measure visible characters, excluding Markdown syntax and URLs.
    rendered = []
    for row_index, row in enumerate(rows):
        rendered_row = []
        for cell in row:
            paragraph = add_paragraph(ET.Element("container"), align="left", after=0)
            add_inline(paragraph, cell, relationships, size=TABLE_SIZE, bold=row_index == 0)
            rendered_row.append(paragraph)
        rendered.append(rendered_row)
    visible = [["".join(p.itertext()) for p in row] for row in rendered]
    widths = column_widths(visible)
    grid = element(table, "tblGrid")
    for width in widths:
        element(grid, "gridCol", w=width)
    for row_index, row in enumerate(rendered):
        row_element = element(table, "tr")
        row_properties = element(row_element, "trPr")
        element(row_properties, "cantSplit")
        if row_index == 0:
            element(row_properties, "tblHeader")
        for width, paragraph in zip(widths, row, strict=True):
            cell = element(row_element, "tc")
            cell_properties = element(cell, "tcPr")
            element(cell_properties, "tcW", w=width, type="dxa")
            if row_index == 0:
                cell_borders = element(cell_properties, "tcBorders")
                element(cell_borders, "bottom", val="single", sz=6, color="000000")
            cell.append(paragraph)


def make_styles():
    styles = ET.Element(f"{{{W}}}styles")
    defaults = element(styles, "docDefaults")
    run_defaults = element(element(defaults, "rPrDefault"), "rPr")
    element(run_defaults, "rFonts", ascii=FONT, hAnsi=FONT, cs=FONT)
    element(run_defaults, "color", val="000000")
    element(run_defaults, "sz", val=BODY_SIZE)
    element(run_defaults, "szCs", val=BODY_SIZE)
    element(run_defaults, "lang", val="es-EC")
    paragraph_defaults = element(element(defaults, "pPrDefault"), "pPr")
    element(paragraph_defaults, "spacing", after=BODY_AFTER, line=240, lineRule="auto")
    element(paragraph_defaults, "jc", val="both")
    normal = element(styles, "style", type="paragraph", default=1, styleId="Normal")
    element(normal, "name", val="Normal")
    for style_id, name, size in [("Heading1", "Heading 1", HEADING1_SIZE), ("Heading2", "Heading 2", HEADING2_SIZE)]:
        style = element(styles, "style", type="paragraph", styleId=style_id)
        element(style, "name", val=name)
        element(style, "basedOn", val="Normal")
        element(style, "next", val="Normal")
        element(style, "qFormat")
        properties = element(style, "pPr")
        element(properties, "keepNext")
        element(properties, "jc", val="left")
        element(properties, "outlineLvl", val=0 if style_id == "Heading1" else 1)
        properties = element(style, "rPr")
        element(properties, "rFonts", ascii=FONT, hAnsi=FONT, cs=FONT)
        element(properties, "b")
        element(properties, "color", val="000000")
        element(properties, "sz", val=size)
        element(properties, "szCs", val=size)
    hyperlink = element(styles, "style", type="character", styleId="Hyperlink")
    element(hyperlink, "name", val="Hyperlink")
    properties = element(hyperlink, "rPr")
    element(properties, "color", val="0563C1")
    element(properties, "u", val="single")
    return styles


def make_numbering():
    numbering = ET.Element(f"{{{W}}}numbering")
    abstract = element(numbering, "abstractNum", abstractNumId=0)
    element(abstract, "multiLevelType", val="singleLevel")
    level = element(abstract, "lvl", ilvl=0)
    element(level, "start", val=1)
    element(level, "numFmt", val="bullet")
    element(level, "lvlText", val="•")
    element(level, "lvlJc", val="left")
    properties = element(level, "pPr")
    tabs = element(properties, "tabs")
    element(tabs, "tab", val="num", pos=360)
    element(properties, "ind", left=360, hanging=180)
    properties = element(level, "rPr")
    element(properties, "rFonts", ascii=FONT, hAnsi=FONT, cs=FONT)
    instance = element(numbering, "num", numId=1)
    element(instance, "abstractNumId", val=0)
    return numbering


def make_header():
    header = ET.Element(f"{{{W}}}hdr")
    paragraph = add_paragraph(header, align="right", after=0)
    field = element(paragraph, "fldSimple", instr=" PAGE ")
    add_run(field, "1", size=HEADER_SIZE)
    return header


def make_core_properties():
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    date = DEFAULT_DATE if epoch is None else datetime.fromtimestamp(int(epoch), UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = ET.Element(f"{{{CP}}}coreProperties")
    ET.SubElement(core, f"{{{DC}}}title").text = "Hito 1: Perfil institucional y preguntas de negocio"
    ET.SubElement(core, f"{{{DC}}}creator").text = "Trazabilidad Pública"
    for name in ["created", "modified"]:
        ET.SubElement(core, f"{{{DCTERMS}}}{name}", {f"{{{XSI}}}type": "dcterms:W3CDTF"}).text = date
    return core


def build_parts(markdown):
    relationships = ET.Element(f"{{{REL}}}Relationships")
    for name, target in [("styles", "styles.xml"), ("numbering", "numbering.xml"), ("header", "header1.xml")]:
        ET.SubElement(
            relationships,
            f"{{{REL}}}Relationship",
            Id=f"rId{len(relationships) + 1}",
            Type=f"{R}/{name}",
            Target=target,
        )
    document = ET.Element(f"{{{W}}}document")
    body = element(document, "body")
    table_count = 0
    previous = None
    for kind, value in parse_markdown(markdown):
        before = TABLE_GAP if previous == "table" else 0
        if kind == "table":
            caption, rows = value
            table_count += 1
            label = add_paragraph(body, align="left", keep=True, before=before)
            add_run(label, f"Tabla {table_count}", bold=True)
            paragraph = add_paragraph(body, align="left", keep=True)
            add_inline(paragraph, caption, relationships, italic=True)
            add_table(body, rows, relationships)
        else:
            heading = kind in {"heading1", "heading2"}
            title = kind == "title"
            paragraph = add_paragraph(
                body,
                style={"heading1": "Heading1", "heading2": "Heading2"}.get(kind),
                align="center" if title else "left" if heading or kind == "bullet" else "both",
                keep=heading,
                page_break=kind == "heading1" and value.startswith("Anexo"),
                before=before,
                bullet=kind == "bullet",
            )
            if kind == "note":
                add_run(paragraph, "Nota.", size=NOTE_SIZE, italic=True)
                add_inline(paragraph, " " + value, relationships, size=NOTE_SIZE)
            else:
                size = {"title": TITLE_SIZE, "heading1": HEADING1_SIZE, "heading2": HEADING2_SIZE}.get(kind, BODY_SIZE)
                add_inline(paragraph, value, relationships, size=size, bold=heading or title)
        previous = kind
    visible = "".join(body.itertext())
    if any(marker in visible for marker in ["[VERIFICAR]", "[PENDIENTE]"]):
        raise ValueError("Document contains unresolved [VERIFICAR] or [PENDIENTE] markers.")
    section = element(body, "sectPr")
    reference = element(section, "headerReference", type="default")
    reference.set(f"{{{R}}}id", "rId3")
    element(section, "pgSz", w=PAGE_WIDTH, h=PAGE_HEIGHT)
    element(
        section,
        "pgMar",
        top=PAGE_MARGIN_VERTICAL,
        right=PAGE_MARGIN,
        bottom=PAGE_MARGIN_VERTICAL,
        left=PAGE_MARGIN,
        header=567,
        footer=567,
        gutter=0,
    )
    root_relationships = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(
        root_relationships, f"{{{REL}}}Relationship", Id="rId1", Type=f"{R}/officeDocument", Target="word/document.xml"
    )
    ET.SubElement(
        root_relationships,
        f"{{{REL}}}Relationship",
        Id="rId2",
        Type=f"{REL}/metadata/core-properties",
        Target="docProps/core.xml",
    )
    parts = {
        "_rels/.rels": root_relationships,
        "word/document.xml": document,
        "word/styles.xml": make_styles(),
        "word/numbering.xml": make_numbering(),
        "word/header1.xml": make_header(),
        "word/_rels/document.xml.rels": relationships,
        "docProps/core.xml": make_core_properties(),
    }
    content_types = ET.Element(f"{{{CT}}}Types")
    for extension, mime in [
        ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
        ("xml", "application/xml"),
    ]:
        ET.SubElement(content_types, f"{{{CT}}}Default", Extension=extension, ContentType=mime)
    for path, suffix in [
        ("document", "document.main"),
        ("styles", "styles"),
        ("numbering", "numbering"),
        ("header1", "header"),
    ]:
        ET.SubElement(
            content_types,
            f"{{{CT}}}Override",
            PartName=f"/word/{path}.xml",
            ContentType=f"application/vnd.openxmlformats-officedocument.wordprocessingml.{suffix}+xml",
        )
    ET.SubElement(
        content_types,
        f"{{{CT}}}Override",
        PartName="/docProps/core.xml",
        ContentType="application/vnd.openxmlformats-package.core-properties+xml",
    )
    parts["[Content_Types].xml"] = content_types
    return {name: xml_bytes(root) for name, root in parts.items()}


def build_docx(source, output):
    """Validate everything before creating directories or overwriting an artifact."""
    if source.resolve() == output.resolve():
        raise ValueError("Source and output must be different paths.")
    parts = build_parts(source.read_text(encoding="utf-8-sig"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            info = ZipInfo(name, date_time=ZIP_DATE)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0o600 << 16
            archive.writestr(info, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source if args.source.is_absolute() else REPO_ROOT / args.source
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    try:
        build_docx(source, output)
    except (ValueError, OSError, OverflowError) as error:
        raise SystemExit(str(error)) from None
    print(output)


if __name__ == "__main__":
    main()
