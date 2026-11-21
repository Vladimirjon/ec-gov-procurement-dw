"""Profile MDEP entity catalog (.xlsx) using standard library zipfile and xml.

Reads OpenXML (.xlsx) directly without third-party dependencies (openpyxl).
Profiles workbook sheets, headers, data rows, completeness, RUC format/uniqueness,
multi-EOD entities, sector distribution, and temporal validity.
Outputs aggregate JSON summary to docs/h2/evidencia/perfil-entidades.json without
copying individual records to the repository.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET


CHUNK_SIZE = 1024 * 1024
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NAMESPACES = {"ns": NS_MAIN, "r": NS_RELS}


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def extract_shared_strings(z: Any) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    sst_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))  # noqa: S314
    strings: list[str] = []
    for si in sst_tree.findall(".//ns:si", NAMESPACES):
        texts = [t.text or "" for t in si.findall(".//ns:t", NAMESPACES)]
        strings.append("".join(texts))
    return strings


def parse_worksheet_rows(
    z: Any, sheet_path: str, shared_strings: list[str]
) -> tuple[dict[str, str], list[tuple[int, dict[str, str]]]]:
    tree = ET.fromstring(z.read(sheet_path))  # noqa: S314
    dim_elem = tree.find("ns:dimension", NAMESPACES)
    dimensions = dim_elem.attrib if dim_elem is not None else {}

    rows_data: list[tuple[int, dict[str, str]]] = []
    for row in tree.findall(".//ns:row", NAMESPACES):
        r_idx = int(row.attrib.get("r", "0"))
        col_vals: dict[str, str] = {}
        for c in row.findall("ns:c", NAMESPACES):
            coord = c.attrib.get("r", "")
            match = re.match(r"([A-Z]+)", coord)
            if not match:
                continue
            col_letter = match.group(1)
            cell_type = c.attrib.get("t")
            val = c.find("ns:v", NAMESPACES)
            val_text = (val.text or "") if val is not None else ""
            if cell_type == "s" and val_text.isdigit():
                idx = int(val_text)
                col_vals[col_letter] = shared_strings[idx] if idx < len(shared_strings) else ""
            elif cell_type == "inlineStr":
                col_vals[col_letter] = "".join(c.itertext())
            else:
                col_vals[col_letter] = val_text
        rows_data.append((r_idx, col_vals))

    return dimensions, rows_data


def profile_catalog(xlsx_path: Path) -> dict[str, Any]:
    file_size = xlsx_path.stat().st_size
    file_sha256 = calculate_sha256(xlsx_path)

    import zipfile

    with zipfile.ZipFile(xlsx_path, "r") as z:
        shared_strings = extract_shared_strings(z)

        # Parse workbook.xml for sheets
        wb_tree = ET.fromstring(z.read("xl/workbook.xml"))  # noqa: S314
        sheets_info = []
        for s in wb_tree.findall(".//ns:sheet", NAMESPACES):
            sheets_info.append(
                {
                    "name": s.attrib.get("name"),
                    "sheetId": s.attrib.get("sheetId"),
                    "rId": s.attrib.get(f"{{{NS_RELS}}}id"),
                }
            )

        # Main worksheet is sheet1
        sheet_path = "xl/worksheets/sheet1.xml"
        dimensions, all_rows = parse_worksheet_rows(z, sheet_path, shared_strings)

    total_rows = len(all_rows)

    # Title rows (1 to 4)
    title_rows = {}
    for r_idx, cols in all_rows:
        if 1 <= r_idx <= 4:
            title_rows[f"row_{r_idx}"] = cols.get("A", "")

    # Header row is row 6
    header_cols = {}
    for r_idx, cols in all_rows:
        if r_idx == 6:
            header_cols = cols
            break

    # Footnote rows are where SECTOR/RUC is empty at the end (rows 3147-3154)
    footnote_rows = []
    data_rows = []
    for r_idx, cols in all_rows:
        if r_idx <= 6:
            continue
        # Footnote rows begin after data records when column F (RUC) and B are empty
        if not cols.get("F", "").strip() and not cols.get("B", "").strip():
            footnote_rows.append({"row": r_idx, "text": cols.get("A", "")})
        else:
            data_rows.append((r_idx, cols))

    total_data_records = len(data_rows)

    # Completeness per column
    col_names = {
        "A": header_cols.get("A", "SECTOR"),
        "B": header_cols.get("B", "DESCRIPCION SECTOR"),
        "C": header_cols.get("C", "ENTIDAD"),
        "D": header_cols.get("D", "EOD"),
        "E": header_cols.get("E", "NOMBRE"),
        "F": header_cols.get("F", "RUC"),
        "G": header_cols.get("G", "PROVINCIA"),
        "H": header_cols.get("H", "CANTÓN"),
        "I": header_cols.get("I", "OBSERVACIONES"),
    }

    column_completeness = {}
    for col, name in col_names.items():
        empty_count = sum(1 for _, r in data_rows if not (r.get(col) or "").strip())
        populated_count = total_data_records - empty_count
        pct_empty = round((empty_count / total_data_records) * 100, 2) if total_data_records > 0 else 0.0
        column_completeness[name] = {
            "column_letter": col,
            "populated_count": populated_count,
            "empty_count": empty_count,
            "pct_empty": pct_empty,
        }

    # RUC analysis
    ruc_raw_lengths: Counter[int] = Counter()
    rucs_raw = []
    rucs_norm = []
    for _, r in data_rows:
        ruc_str = r.get("F", "").strip()
        if ruc_str:
            rucs_raw.append(ruc_str)
            ruc_raw_lengths[len(ruc_str)] += 1
            # Normalize by zero padding up to 13 digits
            rucs_norm.append(ruc_str.zfill(13))

    c_norm = Counter(rucs_norm)
    dups_norm = {k: v for k, v in c_norm.items() if v > 1}

    # Check 001 suffix
    ending_001_count = sum(1 for r in rucs_norm if r.endswith("001"))
    all_numeric = all(r.isdigit() for r in rucs_norm)

    # Multi-EOD entities
    entity_counts: Counter[str] = Counter()
    for _, r in data_rows:
        ent = r.get("C", "").strip()
        if ent:
            entity_counts[ent] += 1

    multi_eod_entities = {k: v for k, v in entity_counts.items() if v > 1}
    max_eod_ent, max_eod_count = entity_counts.most_common(1)[0] if entity_counts else ("", 0)

    # Sector distribution
    sector_counts: Counter[str] = Counter()
    sector_code_map: dict[str, str] = {}
    for _, r in data_rows:
        sec_code = r.get("A", "").strip()
        sec_desc = r.get("B", "").strip()
        sector_counts[sec_desc] += 1
        if sec_desc and sec_code:
            sector_code_map[sec_desc] = sec_code

    sector_distribution = [
        {
            "sector_code": sector_code_map.get(sec, ""),
            "sector_description": sec,
            "record_count": count,
            "pct_of_total": round((count / total_data_records) * 100, 2),
        }
        for sec, count in sector_counts.most_common()
    ]

    # Central government (Sector 111: ADMINISTRACION DEL ESTADO)
    sec_111_rows = [r for _, r in data_rows if r.get("A", "").strip() == "111"]
    sec_111_rucs = {r.get("F", "").strip().zfill(13) for r in sec_111_rows if r.get("F", "").strip()}
    sec_111_entities = {r.get("C", "").strip() for r in sec_111_rows if r.get("C", "").strip()}

    profile_summary = {
        "metadata": {
            "source_file": xlsx_path.name,
            "file_size_bytes": file_size,
            "sha256": file_sha256,
            "profiled_at_utc": datetime.now(UTC).isoformat(),
        },
        "workbook_structure": {
            "sheets": sheets_info,
            "profiled_sheet": "CATÁLOGO",
            "sheet_dimensions": dimensions.get("ref", ""),
            "total_rows_in_sheet": total_rows,
            "title_rows": title_rows,
            "header_row_index": 6,
            "columns": col_names,
            "data_rows_range": {"first_row": 7, "last_row": 3146, "total_records": total_data_records},
            "footnote_rows_range": {
                "first_row": 3147,
                "last_row": 3154,
                "total_footnotes": len(footnote_rows),
                "notes": footnote_rows,
            },
        },
        "column_completeness": column_completeness,
        "ruc_analysis": {
            "total_data_records": total_data_records,
            "non_empty_rucs": len(rucs_raw),
            "empty_rucs": total_data_records - len(rucs_raw),
            "distinct_raw_rucs": len(set(rucs_raw)),
            "all_numeric": all_numeric,
            "raw_lengths": dict(ruc_raw_lengths),
            "raw_12_digits_missing_leading_zero": ruc_raw_lengths.get(12, 0),
            "raw_13_digits": ruc_raw_lengths.get(13, 0),
            "normalized_13_digits_count": len(rucs_norm),
            "distinct_normalized_rucs": len(c_norm),
            "duplicate_normalized_ruc_values": len(dups_norm),
            "records_with_shared_ruc": sum(dups_norm.values()),
            "ending_with_001_count": ending_001_count,
            "pct_ending_with_001": round((ending_001_count / len(rucs_norm)) * 100, 2) if rucs_norm else 0.0,
        },
        "entity_and_eod_analysis": {
            "distinct_entidad_codes": len(entity_counts),
            "entities_with_single_row": len(entity_counts) - len(multi_eod_entities),
            "entities_with_multiple_eod_rows": len(multi_eod_entities),
            "max_eods_for_entity": {"entidad_code": max_eod_ent, "row_count": max_eod_count},
        },
        "sector_distribution": sector_distribution,
        "central_government_sector_111": {
            "sector_code": "111",
            "sector_description": "ADMINISTRACION DEL ESTADO",
            "total_records": len(sec_111_rows),
            "pct_of_catalog_records": round((len(sec_111_rows) / total_data_records) * 100, 2),
            "distinct_entidades": len(sec_111_entities),
            "distinct_rucs": len(sec_111_rucs),
        },
        "temporal_validity": {
            "declared_cut_date": title_rows.get("row_4", ""),
            "has_date_columns": False,
            "has_scd2_intervals": False,
            "observation": (
                "El catalogo es una fotografia estatica del sector publico activa al 31 de agosto de 2026. "
                "No contiene columnas de fecha, periodos de vigencia ni registro historico de fusiones o "
                "escisiones de 2021-2025."
            ),
        },
    }

    return profile_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-xlsx",
        type=Path,
        default=Path("data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx"),
        help="Path to MDEP Excel catalog file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/h2/evidencia/perfil-entidades.json"),
        help="Path to output JSON summary",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    input_path = args.input_xlsx if args.input_xlsx.is_absolute() else repo_root / args.input_xlsx
    output_path = args.output if args.output.is_absolute() else repo_root / args.output

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        return 1

    print(f"Profiling Excel catalog: {input_path}")
    profile = profile_catalog(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Saved aggregate profile to: {output_path}")
    print(f"  Total records: {profile['workbook_structure']['data_rows_range']['total_records']}")
    print(f"  Central Gov (Sector 111): {profile['central_government_sector_111']['total_records']} rows")
    print(f"  Distinct normalized RUCs: {profile['ruc_analysis']['distinct_normalized_rucs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
