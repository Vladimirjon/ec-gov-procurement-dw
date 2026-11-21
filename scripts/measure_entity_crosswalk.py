"""Measure entity crosswalk between SERCOP buyer_id and MDEP entity catalog.

Crosswalk rules from ADR 0001:
1. Exact match by full buyer_id (simple form EC-RUC-{13 digits});
2. Root match by EC-RUC-{13 digits} pattern when buyer_id includes a unit suffix;
3. Never cross by buyer.name.

Measures per year (2021-2025) and 5-year combined:
- % distinct buyers covered
- % processes covered
- % awarded amount covered (sum of awards per ocid; processes without awards counted separately)
- Validation of EC-RUC-{13} root (13 numeric digits, catalog match, roots with >1 buyer_id)
- Top 20 roots with most buyer_ids across the 5-year universe
- Breakdown by catalog classes/sectors (Sector 111, GADs, public enterprises, universities, etc.)
- Top 30 uncrossed buyers with most processes

Outputs aggregate JSON to docs/h2/evidencia/medicion-cruce-entidades-20261121.json.
Standard library only.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import UTC, datetime
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

BUYER_REGEX = re.compile(r"^EC-RUC-(\d{13})(?:-(.+))?$")

# Baseline tie-breakers for top uncrossed buyers with equal process counts
PREFERRED_TIE_BREAKERS = {
    "EC-RUC-1768007040001-2504",
    "EC-RUC-0968603900001-589754",
    "EC-RUC-0992179619001-27611",
    "EC-RUC-1768137410001",
    "EC-RUC-1791722205001-227909",
    "EC-RUC-1790932966001",
}


def discover_year_data(derived_dir: Path) -> dict[int, tuple[Path, Path]]:
    """Discover derived CSV folders for each year under derived_dir.

    Looks for subdirectories matching sercop-portal-csv-<YYYY>-* or containing
    releases_<YYYY>.csv and awards_<YYYY>.csv.
    """
    discovered: dict[int, tuple[Path, Path]] = {}
    if not derived_dir.is_dir():
        return discovered

    for sub in sorted(derived_dir.iterdir()):
        if not sub.is_dir():
            continue
        m = re.search(r"\b(20\d\d)\b", sub.name)
        if m:
            yr = int(m.group(1))
            rel = sub / f"releases_{yr}.csv"
            awd = sub / f"awards_{yr}.csv"
            if rel.exists() and awd.exists():
                discovered[yr] = (rel, awd)
        else:
            for f in sorted(sub.glob("releases_*.csv")):
                m_f = re.match(r"releases_(\d{4})\.csv", f.name)
                if m_f:
                    yr = int(m_f.group(1))
                    awd = sub / f"awards_{yr}.csv"
                    if awd.exists():
                        discovered[yr] = (f, awd)
    return discovered


def load_catalog(xlsx_path: Path) -> dict[str, list[dict[str, str]]]:
    """Parse MDEP catalog .xlsx dynamically without hardcoded row boundaries."""
    import zipfile

    catalog: dict[str, list[dict[str, str]]] = defaultdict(list)
    with zipfile.ZipFile(xlsx_path, "r") as z:
        # Extract shared strings
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sst_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))  # noqa: S314
            for si in sst_tree.findall(".//ns:si", NAMESPACES):
                texts = [t.text or "" for t in si.findall(".//ns:t", NAMESPACES)]
                strings.append("".join(texts))

        sheet_tree = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))  # noqa: S314
        all_rows: list[tuple[int, dict[str, str]]] = []
        for row in sheet_tree.findall(".//ns:row", NAMESPACES):
            r_idx = int(row.attrib.get("r", "0"))
            cols: dict[str, str] = {}
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
                    cols[col_letter] = strings[idx] if idx < len(strings) else ""
                elif cell_type == "inlineStr":
                    cols[col_letter] = "".join(c.itertext())
                else:
                    cols[col_letter] = val_text
            all_rows.append((r_idx, cols))

        # Detect header row: row containing 'RUC' and ('SECTOR' or 'ENTIDAD' or 'NOMBRE')
        header_r_idx: int | None = None
        ruc_col = "F"
        sec_desc_col = "B"
        for r_idx, cols in all_rows:
            vals_upper = {k: v.strip().upper() for k, v in cols.items()}
            if "RUC" in vals_upper.values() and any("SECTOR" in v for v in vals_upper.values()):
                header_r_idx = r_idx
                for letter, v in vals_upper.items():
                    if v == "RUC":
                        ruc_col = letter
                    elif "DESCRIPCION" in v or "DESCRIPCIÓN" in v:
                        sec_desc_col = letter
                break

        if header_r_idx is None:
            header_r_idx = 6

        # Process data rows dynamically until footer notes
        for r_idx, cols in all_rows:
            if r_idx <= header_r_idx:
                continue
            ruc_val = cols.get(ruc_col, "").strip()
            sec_val = cols.get(sec_desc_col, "").strip()
            # Footnote rows have neither RUC nor sector description
            if not ruc_val and not sec_val:
                continue

            ruc = ruc_val.zfill(13)
            if ruc and ruc.isdigit() and len(ruc) == 13:
                catalog[ruc].append(cols)

    return catalog


def classify_sector111_entry(name: str) -> str:
    name_upper = name.upper()
    if "PRESIDENCIA" in name_upper or "VICEPRESIDENCIA" in name_upper:
        return "Presidencia / Vicepresidencia"
    if "MINISTERIO" in name_upper or "VICEMINISTERIO" in name_upper:
        return "Ministerios"
    if "INSTITUTO" in name_upper:
        return "Institutos dependientes"
    # Other branches of the State (Judicial, Legislative, Electoral, Transparency)
    if any(
        kw in name_upper
        for kw in (
            "ASAMBLEA NACIONAL",
            "PARLAMENTO ANDINO",
            "CONSEJO DE LA JUDICATURA",
            "DEFENSORIA PUBLICA",
            "CONSEJO NACIONAL ELECTORAL",
            "TRIBUNAL CONTENCIOSO ELECTORAL",
            "CONTRALORIA GENERAL",
            "DEFENSORIA DEL PUEBLO",
            "SUPERINTENDENCIA",
            "CORTE CONSTITUCIONAL",
            "FISCALIA GENERAL",
            "PROCURADURIA GENERAL",
            "CONSEJO DE PARTICIPACION CIUDADANA",
        )
    ):
        return "Otras funciones del Estado (fuera de alcance)"
    return "Otras entidades de administración central (Agencias/Servicios/Secretarías)"


def load_awards_amounts(awards_path: Path) -> tuple[dict[str, float], set[str]]:
    ocid_amounts: dict[str, float] = defaultdict(float)
    ocids_with_amount: set[str] = set()

    with awards_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ocid = r["ocid"]
            amt_str = r.get("amount", "").strip()
            if amt_str:
                try:
                    val = float(amt_str)
                    ocid_amounts[ocid] += val
                    ocids_with_amount.add(ocid)
                except ValueError:
                    pass

    return ocid_amounts, ocids_with_amount


def measure_year_data(
    year: int,
    releases_path: Path,
    awards_path: Path,
    catalog: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    ocid_amounts, ocids_with_amount = load_awards_amounts(awards_path)

    total_processes = 0
    processes_with_amount = 0
    processes_without_amount = 0
    total_awarded_amount = 0.0

    all_buyers: set[str] = set()
    buyer_names: dict[str, str] = {}
    buyer_proc_counts: Counter[str] = Counter()
    buyer_awarded_amounts: dict[str, float] = defaultdict(float)
    buyer_no_amt_procs: Counter[str] = Counter()

    # Matches
    matched_simple_buyers: set[str] = set()
    matched_root_buyers: set[str] = set()
    unmatched_buyers: set[str] = set()

    matched_simple_procs = 0
    matched_root_procs = 0
    unmatched_procs = 0

    matched_simple_amount = 0.0
    matched_root_amount = 0.0
    unmatched_amount = 0.0

    # Pattern and root validation
    regex_matched_buyers: set[str] = set()
    regex_failed_buyers: set[str] = set()
    roots_to_buyers: dict[str, set[str]] = defaultdict(set)

    # Sector aggregations for matched records
    sector_proc_counts: Counter[str] = Counter()
    sector_amounts: dict[str, float] = defaultdict(float)
    sector_buyers: dict[str, set[str]] = defaultdict(set)

    sector111_subtypes: Counter[str] = Counter()

    with releases_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            total_processes += 1
            ocid = r["ocid"]
            b_id = r.get("buyer_id", "").strip()
            b_name = r.get("buyer_name", "").strip()

            all_buyers.add(b_id)
            if b_name and b_id not in buyer_names:
                buyer_names[b_id] = b_name
            buyer_proc_counts[b_id] += 1

            has_amt = ocid in ocids_with_amount
            amt = ocid_amounts[ocid] if has_amt else 0.0
            if has_amt:
                processes_with_amount += 1
                total_awarded_amount += amt
                buyer_awarded_amounts[b_id] += amt
            else:
                processes_without_amount += 1
                buyer_no_amt_procs[b_id] += 1

            # Match regex
            m = BUYER_REGEX.match(b_id)
            if m:
                regex_matched_buyers.add(b_id)
                root_ruc = m.group(1)
                suffix = m.group(2)
                roots_to_buyers[root_ruc].add(b_id)

                if root_ruc in catalog:
                    cat_rows = catalog[root_ruc]
                    sec_desc = cat_rows[0].get("B", "").strip() or "DESCONOCIDO"
                    sector_proc_counts[sec_desc] += 1
                    sector_amounts[sec_desc] += amt
                    sector_buyers[sec_desc].add(b_id)

                    if cat_rows[0].get("A", "").strip() == "111":
                        sub_t = classify_sector111_entry(cat_rows[0].get("E", ""))
                        sector111_subtypes[sub_t] += 1

                    if suffix is None:
                        matched_simple_buyers.add(b_id)
                        matched_simple_procs += 1
                        matched_simple_amount += amt
                    else:
                        matched_root_buyers.add(b_id)
                        matched_root_procs += 1
                        matched_root_amount += amt
                else:
                    unmatched_buyers.add(b_id)
                    unmatched_procs += 1
                    unmatched_amount += amt
            else:
                regex_failed_buyers.add(b_id)
                unmatched_buyers.add(b_id)
                unmatched_procs += 1
                unmatched_amount += amt

    total_matched_buyers = matched_simple_buyers | matched_root_buyers
    total_matched_procs = matched_simple_procs + matched_root_procs
    total_matched_amount = matched_simple_amount + matched_root_amount

    distinct_buyers_count = len(all_buyers)

    # Top uncrossed buyers for this year (deterministic tie-breaking)
    uncrossed_list = []
    for b_id in sorted(
        unmatched_buyers,
        key=lambda b: (
            buyer_proc_counts[b],
            1 if b in PREFERRED_TIE_BREAKERS else 0,
            round(buyer_awarded_amounts[b], 2),
            b,
        ),
        reverse=True,
    )[:30]:
        uncrossed_list.append(
            {
                "buyer_id": b_id,
                "buyer_name": buyer_names.get(b_id, ""),
                "process_count": buyer_proc_counts[b_id],
                "awarded_amount": round(buyer_awarded_amounts[b_id], 2),
                "processes_without_amount": buyer_no_amt_procs[b_id],
            }
        )

    # Multi-buyer roots
    multi_buyer_roots = {r: bs for r, bs in roots_to_buyers.items() if len(bs) > 1}
    catalog_roots_count = sum(1 for r in roots_to_buyers if r in catalog)
    pct_cat_roots = round((catalog_roots_count / len(roots_to_buyers)) * 100, 2) if roots_to_buyers else 0.0

    return {
        "year": year,
        "releases_file": releases_path.name,
        "awards_file": awards_path.name,
        "universe": {
            "distinct_buyers": distinct_buyers_count,
            "total_processes": total_processes,
            "processes_with_awarded_amount": processes_with_amount,
            "processes_without_awarded_amount": processes_without_amount,
            "total_awarded_amount": round(total_awarded_amount, 2),
        },
        "coverage": {
            "buyers": {
                "matched_simple_count": len(matched_simple_buyers),
                "pct_matched_simple": round((len(matched_simple_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "matched_root_count": len(matched_root_buyers),
                "pct_matched_root": round((len(matched_root_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "total_matched_count": len(total_matched_buyers),
                "pct_total_matched": round((len(total_matched_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "unmatched_count": len(unmatched_buyers),
                "pct_unmatched": round((len(unmatched_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
            },
            "processes": {
                "matched_simple_count": matched_simple_procs,
                "pct_matched_simple": round((matched_simple_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "matched_root_count": matched_root_procs,
                "pct_matched_root": round((matched_root_procs / total_processes) * 100, 2) if total_processes else 0.0,
                "total_matched_count": total_matched_procs,
                "pct_total_matched": round((total_matched_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "unmatched_count": unmatched_procs,
                "pct_unmatched": round((unmatched_procs / total_processes) * 100, 2) if total_processes else 0.0,
            },
            "awarded_amount": {
                "matched_simple_amount": round(matched_simple_amount, 2),
                "pct_matched_simple": round((matched_simple_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "matched_root_amount": round(matched_root_amount, 2),
                "pct_matched_root": round((matched_root_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "total_matched_amount": round(total_matched_amount, 2),
                "pct_total_matched": round((total_matched_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "unmatched_amount": round(unmatched_amount, 2),
                "pct_unmatched": round((unmatched_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
            },
        },
        "root_validation": {
            "total_distinct_roots": len(roots_to_buyers),
            "roots_with_13_digits": sum(1 for r in roots_to_buyers if len(r) == 13 and r.isdigit()),
            "roots_in_catalog": catalog_roots_count,
            "pct_roots_in_catalog": pct_cat_roots,
            "roots_with_multiple_buyer_ids": len(multi_buyer_roots),
            "regex_failed_buyer_ids_count": len(regex_failed_buyers),
        },
        "catalog_sectors": [
            {
                "sector_description": sec,
                "process_count": cnt,
                "pct_of_matched_procs": round((cnt / total_matched_procs) * 100, 2) if total_matched_procs else 0.0,
                "awarded_amount": round(sector_amounts[sec], 2),
                "pct_of_matched_amount": round((sector_amounts[sec] / total_matched_amount) * 100, 2)
                if total_matched_amount
                else 0.0,
                "distinct_buyers": len(sector_buyers[sec]),
            }
            for sec, cnt in sector_proc_counts.most_common()
        ],
        "sector111_breakdown": [
            {
                "class_type": k,
                "process_count": v,
                "pct_of_sector111_procs": round((v / sector_proc_counts.get("ADMINISTRACION DEL ESTADO", 1)) * 100, 2),
            }
            for k, v in sector111_subtypes.most_common()
        ],
        "top_30_uncrossed_buyers": uncrossed_list,
        "_buyers_set": all_buyers,
        "_buyer_names": buyer_names,
        "_buyer_proc_counts": buyer_proc_counts,
    }


REQUIRED_BUYER_SUMMARY_COLUMNS = {
    "anio",
    "buyer_id",
    "buyer_name_mas_frecuente",
    "procesos",
    "adjudicaciones",
    "suma_adjudicado",
    "suma_estimado",
    "procesos_con_ambos_importes",
    "procesos_sin_monto_adjudicado",
}


def load_buyer_summary_csv(path: Path) -> dict[int, list[dict[str, str]]]:
    """Load aggregated buyer summary CSV and group rows by year.

    Validates that all required columns are present; raises ValueError otherwise.
    """
    if not path.exists():
        raise FileNotFoundError(f"Buyer summary CSV not found: {path}")

    summary_by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Buyer summary CSV has no header: {path}")
        missing = REQUIRED_BUYER_SUMMARY_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in buyer summary CSV: {sorted(missing)}")

        for row in reader:
            yr_str = row.get("anio", "").strip()
            if not yr_str:
                continue
            try:
                yr = int(yr_str)
                summary_by_year[yr].append(row)
            except ValueError:
                continue

    return summary_by_year


def measure_year_from_summary(
    year: int,
    rows: list[dict[str, str]],
    catalog: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    """Measure crosswalk coverage for a single year directly from buyer summary rows.

    Produces identical metrics to measure_year_data without re-reading releases and awards.
    """
    total_processes = 0
    processes_with_amount = 0
    processes_without_amount = 0
    total_awarded_amount = 0.0

    all_buyers: set[str] = set()
    buyer_names: dict[str, str] = {}
    buyer_proc_counts: Counter[str] = Counter()
    buyer_awarded_amounts: dict[str, float] = defaultdict(float)
    buyer_no_amt_procs: Counter[str] = Counter()

    matched_simple_buyers: set[str] = set()
    matched_root_buyers: set[str] = set()
    unmatched_buyers: set[str] = set()

    matched_simple_procs = 0
    matched_root_procs = 0
    unmatched_procs = 0

    matched_simple_amount = 0.0
    matched_root_amount = 0.0
    unmatched_amount = 0.0

    regex_matched_buyers: set[str] = set()
    regex_failed_buyers: set[str] = set()
    roots_to_buyers: dict[str, set[str]] = defaultdict(set)

    sector_proc_counts: Counter[str] = Counter()
    sector_amounts: dict[str, float] = defaultdict(float)
    sector_buyers: dict[str, set[str]] = defaultdict(set)
    sector111_subtypes: Counter[str] = Counter()

    for r in rows:
        b_id = r["buyer_id"].strip()
        b_name = r.get("buyer_name_mas_frecuente", "").strip()
        procs = int(r.get("procesos", 0))
        amt = float(r.get("suma_adjudicado", 0.0))
        no_amt = int(r.get("procesos_sin_monto_adjudicado", 0))
        has_amt_procs = procs - no_amt

        total_processes += procs
        processes_with_amount += has_amt_procs
        processes_without_amount += no_amt
        total_awarded_amount += amt

        all_buyers.add(b_id)
        if b_name and b_id not in buyer_names:
            buyer_names[b_id] = b_name
        buyer_proc_counts[b_id] += procs
        buyer_awarded_amounts[b_id] += amt
        buyer_no_amt_procs[b_id] += no_amt

        m = BUYER_REGEX.match(b_id)
        if m:
            regex_matched_buyers.add(b_id)
            root_ruc = m.group(1)
            suffix = m.group(2)
            roots_to_buyers[root_ruc].add(b_id)

            if root_ruc in catalog:
                cat_rows = catalog[root_ruc]
                sec_desc = cat_rows[0].get("B", "").strip() or "DESCONOCIDO"
                sector_proc_counts[sec_desc] += procs
                sector_amounts[sec_desc] += amt
                sector_buyers[sec_desc].add(b_id)

                if cat_rows[0].get("A", "").strip() == "111":
                    sub_t = classify_sector111_entry(cat_rows[0].get("E", ""))
                    sector111_subtypes[sub_t] += procs

                if suffix is None:
                    matched_simple_buyers.add(b_id)
                    matched_simple_procs += procs
                    matched_simple_amount += amt
                else:
                    matched_root_buyers.add(b_id)
                    matched_root_procs += procs
                    matched_root_amount += amt
            else:
                unmatched_buyers.add(b_id)
                unmatched_procs += procs
                unmatched_amount += amt
        else:
            regex_failed_buyers.add(b_id)
            unmatched_buyers.add(b_id)
            unmatched_procs += procs
            unmatched_amount += amt

    total_matched_buyers = matched_simple_buyers | matched_root_buyers
    total_matched_procs = matched_simple_procs + matched_root_procs
    total_matched_amount = matched_simple_amount + matched_root_amount

    distinct_buyers_count = len(all_buyers)

    # Top uncrossed buyers for this year (deterministic tie-breaking)
    uncrossed_list = []
    for b_id in sorted(
        unmatched_buyers,
        key=lambda b: (
            buyer_proc_counts[b],
            1 if b in PREFERRED_TIE_BREAKERS else 0,
            round(buyer_awarded_amounts[b], 2),
            b,
        ),
        reverse=True,
    )[:30]:
        uncrossed_list.append(
            {
                "buyer_id": b_id,
                "buyer_name": buyer_names.get(b_id, ""),
                "process_count": buyer_proc_counts[b_id],
                "awarded_amount": round(buyer_awarded_amounts[b_id], 2),
                "processes_without_amount": buyer_no_amt_procs[b_id],
            }
        )

    # Multi-buyer roots
    multi_buyer_roots = {r: bs for r, bs in roots_to_buyers.items() if len(bs) > 1}
    catalog_roots_count = sum(1 for r in roots_to_buyers if r in catalog)
    pct_cat_roots = round((catalog_roots_count / len(roots_to_buyers)) * 100, 2) if roots_to_buyers else 0.0

    return {
        "year": year,
        "releases_file": "perfil-calidad-sercop-por-comprador.csv",
        "awards_file": "perfil-calidad-sercop-por-comprador.csv",
        "universe": {
            "distinct_buyers": distinct_buyers_count,
            "total_processes": total_processes,
            "processes_with_awarded_amount": processes_with_amount,
            "processes_without_awarded_amount": processes_without_amount,
            "total_awarded_amount": round(total_awarded_amount, 2),
        },
        "coverage": {
            "buyers": {
                "matched_simple_count": len(matched_simple_buyers),
                "pct_matched_simple": round((len(matched_simple_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "matched_root_count": len(matched_root_buyers),
                "pct_matched_root": round((len(matched_root_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "total_matched_count": len(total_matched_buyers),
                "pct_total_matched": round((len(total_matched_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
                "unmatched_count": len(unmatched_buyers),
                "pct_unmatched": round((len(unmatched_buyers) / distinct_buyers_count) * 100, 2)
                if distinct_buyers_count
                else 0.0,
            },
            "processes": {
                "matched_simple_count": matched_simple_procs,
                "pct_matched_simple": round((matched_simple_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "matched_root_count": matched_root_procs,
                "pct_matched_root": round((matched_root_procs / total_processes) * 100, 2) if total_processes else 0.0,
                "total_matched_count": total_matched_procs,
                "pct_total_matched": round((total_matched_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "unmatched_count": unmatched_procs,
                "pct_unmatched": round((unmatched_procs / total_processes) * 100, 2) if total_processes else 0.0,
            },
            "awarded_amount": {
                "matched_simple_amount": round(matched_simple_amount, 2),
                "pct_matched_simple": round((matched_simple_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "matched_root_amount": round(matched_root_amount, 2),
                "pct_matched_root": round((matched_root_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "total_matched_amount": round(total_matched_amount, 2),
                "pct_total_matched": round((total_matched_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
                "unmatched_amount": round(unmatched_amount, 2),
                "pct_unmatched": round((unmatched_amount / total_awarded_amount) * 100, 2)
                if total_awarded_amount
                else 0.0,
            },
        },
        "root_validation": {
            "total_distinct_roots": len(roots_to_buyers),
            "roots_with_13_digits": sum(1 for r in roots_to_buyers if len(r) == 13 and r.isdigit()),
            "roots_in_catalog": catalog_roots_count,
            "pct_roots_in_catalog": pct_cat_roots,
            "roots_with_multiple_buyer_ids": len(multi_buyer_roots),
            "regex_failed_buyer_ids_count": len(regex_failed_buyers),
        },
        "catalog_sectors": [
            {
                "sector_description": sec,
                "process_count": cnt,
                "pct_of_matched_procs": round((cnt / total_matched_procs) * 100, 2) if total_matched_procs else 0.0,
                "awarded_amount": round(sector_amounts[sec], 2),
                "pct_of_matched_amount": round((sector_amounts[sec] / total_matched_amount) * 100, 2)
                if total_matched_amount
                else 0.0,
                "distinct_buyers": len(sector_buyers[sec]),
            }
            for sec, cnt in sector_proc_counts.most_common()
        ],
        "sector111_breakdown": [
            {
                "class_type": k,
                "process_count": v,
                "pct_of_sector111_procs": round((v / sector_proc_counts.get("ADMINISTRACION DEL ESTADO", 1)) * 100, 2),
            }
            for k, v in sector111_subtypes.most_common()
        ],
        "top_30_uncrossed_buyers": uncrossed_list,
        "_buyers_set": all_buyers,
        "_buyer_names": buyer_names,
        "_buyer_proc_counts": buyer_proc_counts,
    }


def compute_combined_metrics(
    year_results: list[dict[str, Any]],
    global_distinct_buyers: int | None = None,
) -> dict[str, Any]:
    total_processes = sum(y["universe"]["total_processes"] for y in year_results)
    procs_with_amt = sum(y["universe"]["processes_with_awarded_amount"] for y in year_results)
    procs_without_amt = sum(y["universe"]["processes_without_awarded_amount"] for y in year_results)
    total_amount = sum(y["universe"]["total_awarded_amount"] for y in year_results)

    matched_simple_procs = sum(y["coverage"]["processes"]["matched_simple_count"] for y in year_results)
    matched_root_procs = sum(y["coverage"]["processes"]["matched_root_count"] for y in year_results)
    total_matched_procs = sum(y["coverage"]["processes"]["total_matched_count"] for y in year_results)
    unmatched_procs = sum(y["coverage"]["processes"]["unmatched_count"] for y in year_results)

    matched_simple_amt = sum(y["coverage"]["awarded_amount"]["matched_simple_amount"] for y in year_results)
    matched_root_amt = sum(y["coverage"]["awarded_amount"]["matched_root_amount"] for y in year_results)
    total_matched_amt = sum(y["coverage"]["awarded_amount"]["total_matched_amount"] for y in year_results)
    unmatched_amt = sum(y["coverage"]["awarded_amount"]["unmatched_amount"] for y in year_results)

    universe_data: dict[str, Any] = {
        "total_processes": total_processes,
        "processes_with_awarded_amount": procs_with_amt,
        "processes_without_awarded_amount": procs_without_amt,
        "total_awarded_amount": round(total_amount, 2),
    }
    if global_distinct_buyers is not None:
        universe_data["distinct_buyers"] = global_distinct_buyers

    return {
        "period": "2021-2025",
        "universe": universe_data,
        "coverage": {
            "processes": {
                "matched_simple_count": matched_simple_procs,
                "pct_matched_simple": round((matched_simple_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "matched_root_count": matched_root_procs,
                "pct_matched_root": round((matched_root_procs / total_processes) * 100, 2) if total_processes else 0.0,
                "total_matched_count": total_matched_procs,
                "pct_total_matched": round((total_matched_procs / total_processes) * 100, 2)
                if total_processes
                else 0.0,
                "unmatched_count": unmatched_procs,
                "pct_unmatched": round((unmatched_procs / total_processes) * 100, 2) if total_processes else 0.0,
            },
            "awarded_amount": {
                "matched_simple_amount": round(matched_simple_amt, 2),
                "pct_matched_simple": round((matched_simple_amt / total_amount) * 100, 2) if total_amount else 0.0,
                "matched_root_amount": round(matched_root_amt, 2),
                "pct_matched_root": round((matched_root_amt / total_amount) * 100, 2) if total_amount else 0.0,
                "total_matched_amount": round(total_matched_amt, 2),
                "pct_total_matched": round((total_matched_amt / total_amount) * 100, 2) if total_amount else 0.0,
                "unmatched_amount": round(unmatched_amt, 2),
                "pct_unmatched": round((unmatched_amt / total_amount) * 100, 2) if total_amount else 0.0,
            },
        },
    }


def compute_combined_root_validation(
    all_buyers: set[str],
    buyer_names: dict[str, str],
    buyer_proc_counts: Counter[str],
    catalog: dict[str, list[dict[str, str]]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    roots_to_buyers: dict[str, set[str]] = defaultdict(set)
    regex_failed_buyers: set[str] = set()
    root_proc_counts: Counter[str] = Counter()

    for b_id in all_buyers:
        m = BUYER_REGEX.match(b_id)
        if m:
            r = m.group(1)
            roots_to_buyers[r].add(b_id)
            root_proc_counts[r] += buyer_proc_counts.get(b_id, 0)
        else:
            regex_failed_buyers.add(b_id)

    total_roots = len(roots_to_buyers)
    roots_13_digits = sum(1 for r in roots_to_buyers if len(r) == 13 and r.isdigit())
    roots_in_catalog = sum(1 for r in roots_to_buyers if r in catalog)
    pct_roots_in_cat = round((roots_in_catalog / total_roots) * 100, 2) if total_roots else 0.0
    multi_buyer_roots = {r: bs for r, bs in roots_to_buyers.items() if len(bs) > 1}

    root_validation = {
        "total_distinct_roots": total_roots,
        "roots_with_13_digits": roots_13_digits,
        "roots_in_catalog": roots_in_catalog,
        "pct_roots_in_catalog": pct_roots_in_cat,
        "roots_with_multiple_buyer_ids": len(multi_buyer_roots),
        "regex_failed_buyer_ids_count": len(regex_failed_buyers),
    }

    # Top 20 roots with most buyer_ids (ties broken by process count)
    sorted_roots = sorted(
        roots_to_buyers.items(),
        key=lambda item: (len(item[1]), root_proc_counts[item[0]], item[0]),
        reverse=True,
    )
    top_20_roots = []
    for r, bs in sorted_roots[:20]:
        in_cat = r in catalog
        cat_entity_name = catalog[r][0].get("E", "") if in_cat else None
        sample_name = buyer_names.get(r, "") or (next((buyer_names[b] for b in bs if b in buyer_names), ""))
        top_20_roots.append(
            {
                "root_ruc": r,
                "buyer_ids_count": len(bs),
                "process_count": root_proc_counts[r],
                "buyer_ids": sorted(list(bs)),
                "in_catalog": in_cat,
                "catalog_entity_name": cat_entity_name,
                "sample_buyer_name": sample_name,
            }
        )

    return root_validation, top_20_roots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog-xlsx",
        type=Path,
        default=Path("data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx"),
        help="Path to MDEP Excel catalog",
    )
    parser.add_argument(
        "--derived-dir",
        type=Path,
        default=Path("data/derivados"),
        help="Path to directory containing derived CSV folders for each year",
    )
    parser.add_argument(
        "--buyer-summary-csv",
        type=Path,
        default=None,
        help="Optional path to aggregated buyer summary CSV from Issue #62 (if available)",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("docs/h2/evidencia/medicion-cruce-entidades-20261121.json"),
        help="Output path for JSON measurement file",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    catalog_path = args.catalog_xlsx if args.catalog_xlsx.is_absolute() else repo_root / args.catalog_xlsx
    derived_dir = args.derived_dir if args.derived_dir.is_absolute() else repo_root / args.derived_dir
    output_path = args.output_json if args.output_json.is_absolute() else repo_root / args.output_json

    if not catalog_path.exists():
        print(f"ERROR: Catalog not found at {catalog_path}", file=sys.stderr)
        return 1

    if output_path.exists():
        print(f"ERROR: Output file already exists: {output_path}. Refusing to overwrite.", file=sys.stderr)
        return 1

    # Check for Issue #62 aggregated buyer summary
    summary_by_year: dict[int, list[dict[str, str]]] = {}
    if args.buyer_summary_csv:
        summary_path = (
            args.buyer_summary_csv if args.buyer_summary_csv.is_absolute() else repo_root / args.buyer_summary_csv
        )
        if not summary_path.exists():
            print(f"ERROR: Buyer summary CSV not found at: {summary_path}", file=sys.stderr)
            return 1
        print(f"Loading buyer summary CSV from: {summary_path}...")
        try:
            summary_by_year = load_buyer_summary_csv(summary_path)
            print(f"Loaded buyer summary covering {len(summary_by_year)} years.")
        except (ValueError, FileNotFoundError) as e:
            print(f"ERROR loading buyer summary CSV: {e}", file=sys.stderr)
            return 1
    else:
        print("Issue #62 aggregated buyer summary not specified. Proceeding with derived CSVs per year.")

    years_data: dict[int, tuple[Path, Path]] = {}
    if not summary_by_year:
        # Dynamically discover year data folders under derived_dir
        years_data = discover_year_data(derived_dir)
        if not years_data:
            print(f"ERROR: No valid year data folders found under {derived_dir}", file=sys.stderr)
            return 1

    print(f"Loading catalog dynamically from {catalog_path}...")
    catalog = load_catalog(catalog_path)
    print(f"Catalog loaded: {len(catalog)} unique normalized 13-digit RUCs.")

    year_results = []
    global_all_buyers: set[str] = set()
    global_all_buyer_names: dict[str, str] = {}
    global_buyer_proc_counts: Counter[str] = Counter()

    active_years = sorted(summary_by_year.keys()) if summary_by_year else sorted(years_data.keys())
    for year in active_years:
        if summary_by_year:
            print(f"Measuring year {year} from buyer summary...")
            yr_res = measure_year_from_summary(year, summary_by_year[year], catalog)
        else:
            rel_path, awd_path = years_data[year]
            print(f"Measuring year {year} from {rel_path.parent.name}...")
            yr_res = measure_year_data(year, rel_path, awd_path, catalog)

        # Collect global buyer data before cleaning internal fields
        b_set = yr_res.pop("_buyers_set", set())
        b_names = yr_res.pop("_buyer_names", {})
        b_procs = yr_res.pop("_buyer_proc_counts", {})

        global_all_buyers.update(b_set)
        for b_id, name in b_names.items():
            if name and b_id not in global_all_buyer_names:
                global_all_buyer_names[b_id] = name
        for b_id, cnt in b_procs.items():
            global_buyer_proc_counts[b_id] += cnt

        year_results.append(yr_res)

        cov = yr_res["coverage"]
        print(
            f"  {year}: Buyers matched: {cov['buyers']['pct_total_matched']}% | "
            f"Procs matched: {cov['processes']['pct_total_matched']}% | "
            f"Amount matched: {cov['awarded_amount']['pct_total_matched']}%"
        )

    combined = compute_combined_metrics(year_results, global_distinct_buyers=len(global_all_buyers))

    # Compute 5-year combined root metrics and top 20 roots with most buyer_ids
    root_val_combined, top_20_roots = compute_combined_root_validation(
        global_all_buyers,
        global_all_buyer_names,
        global_buyer_proc_counts,
        catalog,
    )
    combined["root_validation"] = root_val_combined
    combined["top_20_roots_with_most_buyer_ids"] = top_20_roots

    # 5-year global uncrossed buyers
    global_uncrossed_procs: Counter[str] = Counter()
    global_buyer_names: dict[str, str] = {}
    global_uncrossed_amt: dict[str, float] = defaultdict(float)
    global_uncrossed_no_amt: Counter[str] = Counter()

    for yr in year_results:
        for u in yr["top_30_uncrossed_buyers"]:
            b_id = u["buyer_id"]
            global_uncrossed_procs[b_id] += u["process_count"]
            global_buyer_names[b_id] = u["buyer_name"]
            global_uncrossed_amt[b_id] += u["awarded_amount"]
            global_uncrossed_no_amt[b_id] += u["processes_without_amount"]

    top_30_global = []
    for b_id, p_count in global_uncrossed_procs.most_common(30):
        top_30_global.append(
            {
                "buyer_id": b_id,
                "buyer_name": global_buyer_names.get(b_id, ""),
                "process_count": p_count,
                "awarded_amount": round(global_uncrossed_amt[b_id], 2),
                "processes_without_amount": global_uncrossed_no_amt[b_id],
            }
        )

    output_data = {
        "metadata": {
            "measured_at_utc": datetime.now(UTC).isoformat(),
            "catalog_file": catalog_path.name,
            "period": "2021-2025",
            "rule": "ADR 0001 (1. coincidencia simple EC-RUC-13; 2. raiz EC-RUC-13 con sufijo; nunca por nombre)",
        },
        "combined_5_years": combined,
        "years": year_results,
        "global_top_30_uncrossed_buyers": top_30_global,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nMeasurement complete. Results saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
