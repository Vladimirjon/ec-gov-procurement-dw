"""Check generated OOXML using synthetic Markdown only; no Word installation required."""

import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_hito1_docx.py"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}
MARKDOWN = r"""# Synthetic title

<!-- secret [VERIFICAR]
hidden comment -->
## Main heading
### Subheading
Text **bold** and *italic* and `code`, [web](https://example.invalid/a?b=1&c=2)
and [relative](../sources/example.md#sección-útil). Escaped \*literal\* and \_x\_.

- First **item**
  continued here
- Second item

Tabla: *First caption*

| Column | Detail |
|:---|---:|
| **alpha** | pipe \| inside |
| `beta` | [link](https://example.invalid/table) |

Nota: Synthetic *note*.

Following paragraph.

## Anexo A

Tabla: Second caption
| Short | Long text |
|---|---|
| x | This column contains substantially more text |

## Criterios de aceptación del hito (internal)
[PENDIENTE] never exported
"""


def run_builder(tmp_path, markdown=MARKDOWN, output=None, env=None):
    source = tmp_path / "synthetic.md"
    source.write_text(markdown, encoding="utf-8", newline="\n")
    output = output or tmp_path / "nested" / "result.docx"
    result = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--source", str(source), "--output", str(output)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    return result, output


@pytest.fixture
def package(tmp_path):
    result, output = run_builder(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(output)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/numbering.xml",
            "word/header1.xml",
            "word/_rels/document.xml.rels",
            "docProps/core.xml",
        }
        assert required <= set(archive.namelist())
        assert all(info.date_time == (2026, 11, 8, 0, 0, 0) for info in archive.infolist())
        # XML is produced locally from the synthetic fixture, never supplied externally.
        return {name: ET.fromstring(archive.read(name)) for name in archive.namelist()}  # noqa: S314


def text(element):
    return "".join(element.itertext())


def attr(element, name="val"):
    assert element is not None
    return element.get(f"{{{NS['w']}}}{name}")


def paragraph(document, value):
    return next(p for p in document.findall(".//w:p", NS) if text(p) == value)


def test_title_headings_lists_and_exclusions(package):
    document = package["word/document.xml"]
    title = paragraph(document, "Synthetic title")
    assert attr(title.find("w:pPr/w:jc", NS)) == "center"
    assert title.find("w:r/w:rPr/w:b", NS) is not None
    assert attr(title.find("w:r/w:rPr/w:sz", NS)) == "28"
    for value, style in [("Main heading", "Heading1"), ("Subheading", "Heading2"), ("Anexo A", "Heading1")]:
        p = paragraph(document, value)
        assert attr(p.find("w:pPr/w:pStyle", NS)) == style
        assert p.find("w:pPr/w:keepNext", NS) is not None
    assert paragraph(document, "Anexo A").find("w:pPr/w:pageBreakBefore", NS) is not None
    assert "First item continued here" in text(document)
    assert len(document.findall(".//w:numPr", NS)) == 2
    assert attr(package["word/numbering.xml"].find(".//w:numFmt", NS)) == "bullet"
    for excluded in ["secret", "hidden comment", "Criterios", "PENDIENTE", "VERIFICAR"]:
        assert excluded not in text(document)


def test_inline_and_external_relationships(package):
    document = package["word/document.xml"]
    runs = {text(r): r for r in document.findall(".//w:r", NS)}
    assert runs["bold"].find("w:rPr/w:b", NS) is not None
    assert runs["italic"].find("w:rPr/w:i", NS) is not None
    assert attr(runs["code"].find("w:rPr/w:rFonts", NS), "ascii") == "Consolas"
    assert attr(runs["code"].find("w:rPr/w:sz", NS)) == "16"
    assert "*literal* and _x_." in text(document)
    relationships = {r.get("Id"): r for r in package["word/_rels/document.xml.rels"]}
    targets = []
    for link in document.findall(".//w:hyperlink", NS):
        relationship = relationships[link.get(f"{{{NS['r']}}}id")]
        assert relationship.get("TargetMode") == "External"
        assert relationship.get("Type").endswith("/hyperlink")
        targets.append(relationship.get("Target"))
        assert attr(link.find("w:r/w:rPr/w:rStyle", NS)) == "Hyperlink"
    assert "https://example.invalid/a?b=1&c=2" in targets
    assert (
        "https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/sources/example.md#secci%C3%B3n-%C3%BAtil"
        in targets
    )


def test_tables_captions_notes_and_geometry(package):
    document = package["word/document.xml"]
    body = document.find("w:body", NS)
    tables = body.findall("w:tbl", NS)
    assert len(tables) == 2
    usable = 11906 - 2 * 1021
    for number, table in enumerate(tables, 1):
        position = list(body).index(table)
        label, caption = body[position - 2 : position]
        assert text(label) == f"Tabla {number}"
        assert label.find("w:r/w:rPr/w:b", NS) is not None
        assert caption.find("w:r/w:rPr/w:i", NS) is not None
        assert label.find("w:pPr/w:keepNext", NS) is not None
        assert caption.find("w:pPr/w:keepNext", NS) is not None
        assert attr(table.find("w:tblPr/w:tblW", NS), "w") == str(usable)
        widths = [int(attr(c, "w")) for c in table.findall("w:tblGrid/w:gridCol", NS)]
        assert sum(widths) == usable
        assert min(widths) >= usable * 0.08
        assert table.find("w:tr/w:trPr/w:tblHeader", NS) is not None
        for row in table.findall("w:tr", NS):
            assert row.find("w:trPr/w:cantSplit", NS) is not None
            assert [int(attr(c, "w")) for c in row.findall("w:tc/w:tcPr/w:tcW", NS)] == widths
        borders = table.find("w:tblPr/w:tblBorders", NS)
        assert attr(borders.find("w:top", NS), "sz") == "8"
        assert attr(borders.find("w:bottom", NS), "sz") == "8"
        assert attr(borders.find("w:insideH", NS), "sz") == "2"
        assert attr(borders.find("w:insideV", NS)) == "nil"
    note = paragraph(document, "Nota. Synthetic note.")
    assert note.find("w:r/w:rPr/w:i", NS) is not None
    assert attr(note.find("w:pPr/w:spacing", NS), "before") == "90"
    assert "pipe | inside" in text(tables[0])
    assert attr(paragraph(document, "Following paragraph.").find("w:pPr/w:spacing", NS), "before") == "0"
    assert attr(paragraph(document, "Anexo A").find("w:pPr/w:spacing", NS), "before") == "0"


def test_page_header_styles_and_metadata(package):
    document = package["word/document.xml"]
    section = document.find("w:body/w:sectPr", NS)
    assert attr(section.find("w:pgSz", NS), "w") == "11906"
    assert attr(section.find("w:pgSz", NS), "h") == "16838"
    assert section.find("w:headerReference", NS) is not None
    assert section.find("w:footerReference", NS) is None
    header = package["word/header1.xml"]
    assert attr(header.find("w:p/w:fldSimple", NS), "instr").strip() == "PAGE"
    assert attr(header.find("w:p/w:pPr/w:jc", NS)) == "right"
    styles = package["word/styles.xml"]
    assert attr(styles.find("w:docDefaults/w:rPrDefault/w:rPr/w:lang", NS)) == "es-EC"
    for style_id, size in [("Heading1", "24"), ("Heading2", "22")]:
        style = styles.find(f"w:style[@w:styleId='{style_id}']", NS)
        assert attr(style.find("w:rPr/w:sz", NS)) == size
        assert attr(style.find("w:rPr/w:color", NS)) == "000000"
    core = package["docProps/core.xml"]
    assert core.find("dc:creator", NS).text == "Trazabilidad Pública"


def test_relationship_targets_exist_and_content_types_cover_parts(package):
    for rel_path, base in [("_rels/.rels", ""), ("word/_rels/document.xml.rels", "word/")]:
        for relationship in package[rel_path]:
            if relationship.get("TargetMode") != "External":
                assert base + relationship.get("Target") in package
    content_types = package["[Content_Types].xml"]
    covered = {node.get("PartName", "").lstrip("/") for node in content_types}
    assert {name for name in package if name.endswith(".xml") and name != "[Content_Types].xml"} <= covered


@pytest.mark.parametrize("explicit_paths", [False, True])
def test_cli_paths_are_relative_to_script_repository(tmp_path, explicit_paths):
    # A synthetic repository avoids reading or writing the actual delivery paths.
    repo = tmp_path / "repository"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    copied_script = scripts / SCRIPT.name
    copied_script.write_bytes(SCRIPT.read_bytes())
    source = repo / "docs" / "requirements" / "hito1.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Synthetic document\n", encoding="utf-8", newline="\n")
    output = repo / "deliverables" / "h1" / "Hito1_BravoFreireGuajanPasquelTorres.docx"
    arguments = []
    if explicit_paths:
        arguments = ["--source", "docs/requirements/hito1.md", "--output", "custom/result.docx"]
        output = repo / "custom" / "result.docx"
    result = subprocess.run(
        [sys.executable, "-I", str(copied_script), *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(output)
    assert zipfile.is_zipfile(output)


def test_widths_are_proportional_with_a_real_minimum(tmp_path):
    wide = "x" * 200
    result, output = run_builder(
        tmp_path,
        "# Title\n\nTabla: Widths\n| A | B | C | D |\n|---|---|---|---|\n"
        f"| a | {wide} | {wide} | {wide} |\n\nAfter table.\n",
    )
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))  # noqa: S314 - synthetic output
    widths = [int(attr(c, "w")) for c in document.findall(".//w:tblGrid/w:gridCol", NS)]
    assert sum(widths) == 9864
    assert widths[0] == 790  # ceil(8% of 9864); redistribute remaining width proportionally.
    assert max(widths[1:]) - min(widths[1:]) <= 1
    following = paragraph(document, "After table.")
    assert attr(following.find("w:pPr/w:spacing", NS), "before") == "90"


@pytest.mark.parametrize(
    ("markdown", "message"),
    [
        ("Tabla: Empty\n| a | b |\n|---|---|\n| a |\n", "same number"),
        ("Tabla: Invalid\n| a | b |\n|--|---|\n", "separator"),
    ],
)
def test_malformed_tables_fail_before_writing(tmp_path, markdown, message):
    result, output = run_builder(tmp_path, markdown)
    assert result.returncode != 0
    assert message in result.stderr.lower()
    assert not output.exists()


@pytest.mark.parametrize("marker", ["[VERIFICAR]", "[PENDIENTE]", "**[VERI**FICAR]"])
@pytest.mark.parametrize("existing", [False, True])
def test_unresolved_markers_never_write(tmp_path, marker, existing):
    output = tmp_path / "result.docx"
    if existing:
        output.write_bytes(b"previous artifact")
    result, _ = run_builder(tmp_path, f"# Title\n\n{marker}\n", output)
    assert result.returncode != 0
    assert "unresolved" in result.stderr.lower()
    if existing:
        assert output.read_bytes() == b"previous artifact"
    else:
        assert not output.exists()


def test_table_without_caption_fails(tmp_path):
    result, output = run_builder(tmp_path, "# Title\n\n| a | b |\n|---|---|\n| x | y |\n")
    assert result.returncode != 0
    assert "caption" in result.stderr.lower()
    assert not output.exists()


def test_reproducibility_and_source_date_epoch(tmp_path):
    env = {**os.environ, "SOURCE_DATE_EPOCH": "0"}
    first, output = run_builder(tmp_path, env=env)
    assert first.returncode == 0, first.stderr
    original = output.read_bytes()
    second, _ = run_builder(tmp_path, env=env)
    assert second.returncode == 0, second.stderr
    assert output.read_bytes() == original
    with zipfile.ZipFile(output) as archive:
        core = ET.fromstring(archive.read("docProps/core.xml"))  # noqa: S314 - locally generated synthetic XML
        assert core.find("dcterms:created", NS).text == "1970-01-01T00:00:00Z"
        assert core.find("dcterms:modified", NS).text == "1970-01-01T00:00:00Z"
