"""Profile SERCOP quality across the six dimensions for H2.

Measures completeness, validity, uniqueness, consistency, accuracy, and timeliness
for the 2021-2025 derived CSV files of SERCOP OCDS portal data.
Logical tables:
- Procesos_SERCOP (grain: ocid) = releases + tender
- Adjudicaciones_SERCOP (grain: award of a process) = awards
Also inspects contracts candidate dates and control totals.

Standard library only. Executable with python -I.
Outputs aggregate JSON per year, consolidated summary CSV, and buyer summary CSV.
Does NOT report individual records, ocids, personal names, or contact data.
"""

from __future__ import annotations

import argparse
import codecs
from collections import Counter, defaultdict
import contextlib
import csv
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


CHUNK_SIZE = 1024 * 1024
BUYER_ID_REGEX = re.compile(r"^EC-RUC-(\d{13})(?:-(.+))?$")
EXPECTED_PROCUREMENT_METHODS = {"selective", "direct", "open", "limited"}
CUTOFF_DATE = datetime(2026, 11, 21, 23, 59, 59, tzinfo=UTC)
MIN_VALID_YEAR = 2015

# Fields to profile per column (Step 8 of Hito 2 guide)
KEY_FIELDS_BY_TABLE: dict[str, list[str]] = {
    "releases": ["ocid", "buyer_id", "buyer_name", "date"],
    "tender": [
        "procurementMethod",
        "procurementMethodDetails",
        "value_amount",
        "value_currency",
        "status",
        "tenderPeriod_startDate",
    ],
    "awards": [
        "id",
        "status",
        "date",
        "amount",
        "currency",
        "correctedValue_amount",
        "enteredValue_amount",
    ],
    "contracts": [
        "id",
        "status",
        "dateSigned",
        "amount",
        "currency",
    ],
}


def calculate_sha256(path: Path) -> str:
    """Calculate the SHA-256 digest of a file in streaming binary chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def compute_script_sha256(script_path: Path) -> str:
    """Calculate script SHA-256 normalized to LF line endings."""
    content = script_path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def detect_encoding(path: Path) -> str:
    """Detect file encoding using standard library heuristics."""
    with path.open("rb") as stream:
        leading_bytes = stream.read(4)
        if leading_bytes.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        stream.seek(0)
        # Incremental decoder: a multibyte character split across two chunks
        # must not be reported as invalid UTF-8.
        decoder = codecs.getincrementaldecoder("utf-8")()
        try:
            for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                decoder.decode(chunk)
            decoder.decode(b"", final=True)
            return "utf-8"
        except UnicodeDecodeError:
            return "windows-1252"


def parse_iso_datetime(val: str) -> tuple[datetime | None, str]:
    """Parse ISO datetime string, returning (datetime_obj, status_code).

    status_code can be: 'valid', 'unparseable', 'empty'.
    """
    clean = val.strip()
    if not clean:
        return None, "empty"
    try:
        # Standard OCDS ISO format YYYY-MM-DDTHH:MM:SS...
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt, "valid"
    except ValueError:
        pass
    except TypeError:
        pass

    # Attempt date only YYYY-MM-DD
    if len(clean) >= 10 and clean[4] == "-" and clean[7] == "-":
        try:
            dt = datetime.fromisoformat(clean[:10]).replace(tzinfo=UTC)
            return dt, "valid"
        except ValueError:
            pass
        except TypeError:
            pass
    return None, "unparseable"


def discover_year_data(derived_dir: Path) -> dict[int, dict[str, Path]]:
    """Discover derived CSV tables for each year under derived_dir.

    Looks for subdirectories matching sercop-portal-csv-<YYYY>-* or containing
    releases_<YYYY>.csv, tender_<YYYY>.csv, awards_<YYYY>.csv, contracts_<YYYY>.csv.
    """
    discovered: dict[int, dict[str, Path]] = {}
    if not derived_dir.is_dir():
        return discovered

    for sub in sorted(derived_dir.iterdir()):
        if not sub.is_dir():
            continue
        m = re.search(r"\b(20\d\d)\b", sub.name)
        yr = int(m.group(1)) if m else None

        tables: dict[str, Path] = {}
        if yr is not None:
            for tbl in ["releases", "tender", "awards", "contracts", "suppliers", "planning", "extensions", "metadata"]:
                candidate = sub / f"{tbl}_{yr}.csv"
                if candidate.exists():
                    tables[tbl] = candidate
        else:
            for f in sorted(sub.glob("releases_*.csv")):
                m_f = re.match(r"releases_(\d{4})\.csv", f.name)
                if m_f:
                    yr = int(m_f.group(1))
                    for tbl in [
                        "releases",
                        "tender",
                        "awards",
                        "contracts",
                        "suppliers",
                        "planning",
                        "extensions",
                        "metadata",
                    ]:
                        cand = sub / f"{tbl}_{yr}.csv"
                        if cand.exists():
                            tables[tbl] = cand
                    break

        if yr is not None and "releases" in tables and "awards" in tables:
            discovered[yr] = tables

    return discovered


class FieldProfiler:
    """Helper to collect profiling metrics for a specific column."""

    def __init__(self, table: str, field_name: str, is_numeric: bool = False, is_date: bool = False):
        self.table = table
        self.field_name = field_name
        self.is_numeric = is_numeric
        self.is_date = is_date
        self.total_rows = 0
        self.empty_count = 0
        self.populated_count = 0
        self.distinct_values: set[str] = set()
        self.value_frequencies: Counter[str] = Counter()
        self.min_numeric: float | None = None
        self.max_numeric: float | None = None
        self.min_date: str | None = None
        self.max_date: str | None = None

    def add(self, val: str) -> None:
        self.total_rows += 1
        clean = val.strip()
        if not clean:
            self.empty_count += 1
            return

        self.populated_count += 1
        self.distinct_values.add(clean)

        if len(self.distinct_values) <= 100:
            self.value_frequencies[clean] += 1

        if self.is_numeric:
            try:
                num = float(clean)
                if self.min_numeric is None or num < self.min_numeric:
                    self.min_numeric = num
                if self.max_numeric is None or num > self.max_numeric:
                    self.max_numeric = num
            except ValueError:
                pass

        if self.is_date:
            dt, status = parse_iso_datetime(clean)
            if status == "valid" and dt is not None:
                iso_str = dt.isoformat()
                if self.min_date is None or iso_str < self.min_date:
                    self.min_date = iso_str
                if self.max_date is None or iso_str > self.max_date:
                    self.max_date = iso_str

    def to_dict(self) -> dict[str, Any]:
        distinct_count = len(self.distinct_values)
        res: dict[str, Any] = {
            "table": self.table,
            "field": self.field_name,
            "total_rows": self.total_rows,
            "empty_count": self.empty_count,
            "populated_count": self.populated_count,
            "distinct_count": distinct_count,
            "completeness_pct": round((self.populated_count / self.total_rows * 100), 2)
            if self.total_rows > 0
            else 0.0,
        }
        if self.is_numeric:
            res["min"] = self.min_numeric
            res["max"] = self.max_numeric
        if self.is_date:
            res["min_date"] = self.min_date
            res["max_date"] = self.max_date

        if distinct_count <= 30 and self.field_name not in {"ocid", "id", "release_id", "awardID"}:
            res["distribution"] = dict(self.value_frequencies.most_common(30))
        return res


def profile_candidate_date(
    date_strings: list[str],
    file_year: int,
) -> dict[str, Any]:
    """Profile candidate dates: completeness, validity, opportunity, monthly distribution."""
    total = len(date_strings)
    populated = 0
    empty = 0
    unparseable = 0
    before_2015 = 0
    future = 0
    after_file_year = 0
    valid_range = 0
    monthly_dist: Counter[str] = Counter()
    min_date: str | None = None
    max_date: str | None = None

    for s in date_strings:
        clean = s.strip()
        if not clean:
            empty += 1
            continue

        populated += 1
        dt, status = parse_iso_datetime(clean)
        if status == "unparseable" or dt is None:
            unparseable += 1
            continue

        iso_str = dt.isoformat()
        if min_date is None or iso_str < min_date:
            min_date = iso_str
        if max_date is None or iso_str > max_date:
            max_date = iso_str

        yr = dt.year
        mo_str = f"{dt.year:04d}-{dt.month:02d}"
        monthly_dist[mo_str] += 1

        if yr < MIN_VALID_YEAR:
            before_2015 += 1
        elif dt > CUTOFF_DATE:
            future += 1
        else:
            valid_range += 1

        if yr > file_year:
            after_file_year += 1

    return {
        "total_evaluated": total,
        "populated": populated,
        "empty": empty,
        "completeness_pct": round((populated / total * 100), 2) if total > 0 else 0.0,
        "unparseable": unparseable,
        "before_2015": before_2015,
        "future": future,
        "after_file_year": after_file_year,
        "pct_after_file_year": round((after_file_year / populated * 100), 2) if populated > 0 else 0.0,
        "valid_range": valid_range,
        "min_date": min_date,
        "max_date": max_date,
        "monthly_distribution": dict(sorted(monthly_dist.items())),
    }


def profile_year(
    year: int,
    table_paths: dict[str, Path],
    reference_awarded_2025: float = 7318.7,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Execute complete six-dimension profiling for a single year."""
    csv.field_size_limit(10 * 1024 * 1024)

    # Profilers for key fields
    field_profilers: dict[str, dict[str, FieldProfiler]] = {
        "releases": {
            "ocid": FieldProfiler("releases", "ocid"),
            "buyer_id": FieldProfiler("releases", "buyer_id"),
            "buyer_name": FieldProfiler("releases", "buyer_name"),
            "date": FieldProfiler("releases", "date", is_date=True),
        },
        "tender": {
            "procurementMethod": FieldProfiler("tender", "procurementMethod"),
            "procurementMethodDetails": FieldProfiler("tender", "procurementMethodDetails"),
            "value_amount": FieldProfiler("tender", "value_amount", is_numeric=True),
            "value_currency": FieldProfiler("tender", "value_currency"),
            "status": FieldProfiler("tender", "status"),
            "tenderPeriod_startDate": FieldProfiler("tender", "tenderPeriod_startDate", is_date=True),
        },
        "awards": {
            "id": FieldProfiler("awards", "id"),
            "status": FieldProfiler("awards", "status"),
            "date": FieldProfiler("awards", "date", is_date=True),
            "amount": FieldProfiler("awards", "amount", is_numeric=True),
            "currency": FieldProfiler("awards", "currency"),
            "correctedValue_amount": FieldProfiler("awards", "correctedValue_amount", is_numeric=True),
            "enteredValue_amount": FieldProfiler("awards", "enteredValue_amount", is_numeric=True),
        },
        "contracts": {
            "id": FieldProfiler("contracts", "id"),
            "status": FieldProfiler("contracts", "status"),
            "dateSigned": FieldProfiler("contracts", "dateSigned", is_date=True),
            "amount": FieldProfiler("contracts", "amount", is_numeric=True),
            "currency": FieldProfiler("contracts", "currency"),
        },
    }

    # Tracking data structures for cross-table relations and grain
    # Releases:
    releases_count = 0
    releases_ocid_counts: Counter[str] = Counter()
    releases_pairs: set[tuple[str, str]] = set()
    releases_pairs_dups = 0
    buyer_info_by_ocid: dict[str, tuple[str, str]] = {}  # ocid -> (buyer_id, buyer_name)
    buyer_names_by_buyer_id: dict[str, Counter[str]] = defaultdict(Counter)
    buyer_ids_by_buyer_name: dict[str, Counter[str]] = defaultdict(Counter)
    buyer_id_formats: Counter[str] = Counter()  # 'simple', 'suffix', 'malformed'
    release_date_strings: list[str] = []

    # Tender:
    tender_count = 0
    tender_ocid_counts: Counter[str] = Counter()
    tender_pairs: set[tuple[str, str]] = set()
    tender_pairs_dups = 0
    tender_data_by_ocid: dict[str, dict[str, Any]] = {}
    procurement_methods_counts: Counter[str] = Counter()
    procurement_details_by_method: dict[str, set[str]] = defaultdict(set)
    tender_date_strings: list[str] = []
    tender_value_currencies: Counter[str] = Counter()
    tender_value_num_categories: Counter[str] = Counter()  # 'positive', 'zero', 'negative', 'non_numeric', 'empty'
    tender_sum_value_amount = 0.0

    # Awards:
    awards_count = 0
    awards_ocid_counts: Counter[str] = Counter()
    awards_pairs: set[tuple[str, str]] = set()
    awards_pairs_dups = 0
    award_ids_by_ocid: dict[str, set[str]] = defaultdict(set)
    dup_award_ids_within_proc = 0
    awards_data_by_ocid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    award_date_strings: list[str] = []
    award_currencies: Counter[str] = Counter()
    award_amount_num_categories: Counter[str] = Counter()  # 'positive', 'zero', 'negative', 'non_numeric', 'empty'
    awards_sum_amount = 0.0
    awards_sum_corrected = 0.0
    awards_sum_entered = 0.0
    amount_vs_corrected_diff = 0
    amount_vs_entered_diff = 0
    amount_vs_corrected_both_present = 0
    amount_vs_entered_both_present = 0
    awards_status_counts: Counter[str] = Counter()
    tender_status_counts: Counter[str] = Counter()

    # Contracts:
    contracts_count = 0
    contracts_ocid_counts: Counter[str] = Counter()
    contracts_pairs: set[tuple[str, str]] = set()
    contracts_pairs_dups = 0
    contracts_date_strings: list[str] = []
    contracts_currencies: Counter[str] = Counter()
    contracts_status_counts: Counter[str] = Counter()
    contracts_sum_amount = 0.0

    # 1. READ RELEASES
    rel_path = table_paths["releases"]
    rel_enc = detect_encoding(rel_path)
    with rel_path.open("r", encoding=rel_enc, newline="", errors="replace") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            releases_count += 1
            ocid = row.get("ocid", "").strip()
            rel_id = row.get("id", "").strip()
            buyer_id = row.get("buyer_id", "").strip()
            buyer_name = row.get("buyer_name", "").strip()
            dt_str = row.get("date", "").strip()

            releases_ocid_counts[ocid] += 1
            pair = (ocid, rel_id)
            if pair in releases_pairs:
                releases_pairs_dups += 1
            else:
                releases_pairs.add(pair)

            buyer_info_by_ocid[ocid] = (buyer_id, buyer_name)
            if buyer_id:
                buyer_names_by_buyer_id[buyer_id][buyer_name] += 1
                m = BUYER_ID_REGEX.match(buyer_id)
                if not m:
                    buyer_id_formats["malformed"] += 1
                elif m.group(2):
                    buyer_id_formats["suffix"] += 1
                else:
                    buyer_id_formats["simple"] += 1
            else:
                buyer_id_formats["empty"] += 1

            if buyer_name:
                buyer_ids_by_buyer_name[buyer_name][buyer_id] += 1

            release_date_strings.append(dt_str)

            # Profile fields
            for col in KEY_FIELDS_BY_TABLE["releases"]:
                if col in row:
                    field_profilers["releases"][col].add(row[col])

    # 2. READ TENDER
    ten_path = table_paths.get("tender")
    if ten_path and ten_path.exists():
        ten_enc = detect_encoding(ten_path)
        with ten_path.open("r", encoding=ten_enc, newline="", errors="replace") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                tender_count += 1
                ocid = row.get("ocid", "").strip()
                rel_id = row.get("release_id", "").strip()
                status = row.get("status", "").strip()
                pe_id = row.get("procuringEntity_id", "").strip()
                pe_name = row.get("procuringEntity_name", "").strip()
                pm = row.get("procurementMethod", "").strip()
                pmd = row.get("procurementMethodDetails", "").strip()
                va_str = row.get("value_amount", "").strip()
                vc = row.get("value_currency", "").strip()
                tp_start = row.get("tenderPeriod_startDate", "").strip()

                tender_ocid_counts[ocid] += 1
                pair = (ocid, rel_id)
                if pair in tender_pairs:
                    tender_pairs_dups += 1
                else:
                    tender_pairs.add(pair)

                tender_status_counts[status] += 1
                procurement_methods_counts[pm] += 1
                if pm:
                    procurement_details_by_method[pm].add(pmd)
                tender_value_currencies[vc] += 1
                tender_date_strings.append(tp_start)

                val_num: float | None = None
                if not va_str:
                    tender_value_num_categories["empty"] += 1
                else:
                    try:
                        fval = float(va_str)
                        val_num = fval
                        tender_sum_value_amount += fval
                        if fval > 0:
                            tender_value_num_categories["positive"] += 1
                        elif fval == 0:
                            tender_value_num_categories["zero"] += 1
                        else:
                            tender_value_num_categories["negative"] += 1
                    except ValueError:
                        tender_value_num_categories["non_numeric"] += 1

                tender_data_by_ocid[ocid] = {
                    "procuringEntity_id": pe_id,
                    "procuringEntity_name": pe_name,
                    "procurementMethod": pm,
                    "procurementMethodDetails": pmd,
                    "value_amount": val_num,
                    "value_currency": vc,
                    "status": status,
                    "tenderPeriod_startDate": tp_start,
                }

                # Profile fields
                for col in KEY_FIELDS_BY_TABLE["tender"]:
                    if col in row:
                        field_profilers["tender"][col].add(row[col])

    # 3. READ AWARDS
    awd_path = table_paths.get("awards")
    if awd_path and awd_path.exists():
        awd_enc = detect_encoding(awd_path)
        with awd_path.open("r", encoding=awd_enc, newline="", errors="replace") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                awards_count += 1
                ocid = row.get("ocid", "").strip()
                rel_id = row.get("release_id", "").strip()
                awd_id = row.get("id", "").strip()
                status = row.get("status", "").strip()
                dt_str = row.get("date", "").strip()
                amt_str = row.get("amount", "").strip()
                curr = row.get("currency", "").strip()
                corr_str = row.get("correctedValue_amount", "").strip()
                ent_str = row.get("enteredValue_amount", "").strip()

                awards_ocid_counts[ocid] += 1
                pair = (ocid, rel_id)
                if pair in awards_pairs:
                    awards_pairs_dups += 1
                else:
                    awards_pairs.add(pair)

                if awd_id in award_ids_by_ocid[ocid]:
                    dup_award_ids_within_proc += 1
                award_ids_by_ocid[ocid].add(awd_id)

                awards_status_counts[status] += 1
                award_currencies[curr] += 1
                award_date_strings.append(dt_str)

                amt_num: float | None = None
                if not amt_str:
                    award_amount_num_categories["empty"] += 1
                else:
                    try:
                        famt = float(amt_str)
                        amt_num = famt
                        awards_sum_amount += famt
                        if famt > 0:
                            award_amount_num_categories["positive"] += 1
                        elif famt == 0:
                            award_amount_num_categories["zero"] += 1
                        else:
                            award_amount_num_categories["negative"] += 1
                    except ValueError:
                        award_amount_num_categories["non_numeric"] += 1

                # Corrected & Entered
                corr_num: float | None = None
                if corr_str:
                    try:
                        corr_num = float(corr_str)
                        awards_sum_corrected += corr_num
                    except ValueError:
                        pass
                ent_num: float | None = None
                if ent_str:
                    try:
                        ent_num = float(ent_str)
                        awards_sum_entered += ent_num
                    except ValueError:
                        pass

                if amt_num is not None and corr_num is not None:
                    amount_vs_corrected_both_present += 1
                    if amt_num != corr_num:
                        amount_vs_corrected_diff += 1

                if amt_num is not None and ent_num is not None:
                    amount_vs_entered_both_present += 1
                    if amt_num != ent_num:
                        amount_vs_entered_diff += 1

                awards_data_by_ocid[ocid].append(
                    {
                        "id": awd_id,
                        "amount": amt_num,
                        "currency": curr,
                        "status": status,
                        "date": dt_str,
                    }
                )

                # Profile fields
                for col in KEY_FIELDS_BY_TABLE["awards"]:
                    if col in row:
                        field_profilers["awards"][col].add(row[col])

    # 4. READ CONTRACTS
    con_path = table_paths.get("contracts")
    if con_path and con_path.exists():
        con_enc = detect_encoding(con_path)
        with con_path.open("r", encoding=con_enc, newline="", errors="replace") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                contracts_count += 1
                ocid = row.get("ocid", "").strip()
                rel_id = row.get("release_id", "").strip()
                status = row.get("status", "").strip()
                ds_str = row.get("dateSigned", "").strip()
                amt_str = row.get("amount", "").strip()
                curr = row.get("currency", "").strip()

                contracts_ocid_counts[ocid] += 1
                pair = (ocid, rel_id)
                if pair in contracts_pairs:
                    contracts_pairs_dups += 1
                else:
                    contracts_pairs.add(pair)

                contracts_status_counts[status] += 1
                contracts_currencies[curr] += 1
                contracts_date_strings.append(ds_str)

                if amt_str:
                    with contextlib.suppress(ValueError):
                        contracts_sum_amount += float(amt_str)

                # Profile fields
                for col in KEY_FIELDS_BY_TABLE["contracts"]:
                    if col in row:
                        field_profilers["contracts"][col].add(row[col])

    # COMBINED PROCESS-LEVEL METRICS
    all_process_ocids = set(releases_ocid_counts.keys())
    total_processes = len(all_process_ocids)

    processes_with_both_amounts = 0
    processes_with_award_no_estimate = 0
    processes_with_estimate_no_award = 0
    processes_without_any_amount = 0

    # Multiplicity of awards per process
    award_counts_histogram: Counter[int] = Counter()
    for ocid in all_process_ocids:
        awd_list = awards_data_by_ocid.get(ocid, [])
        award_counts_histogram[len(awd_list)] += 1

        # Amounts per process:
        # Sum of awards with valid amount
        valid_awd_amts = [a["amount"] for a in awd_list if a["amount"] is not None]
        has_valid_award = len(valid_awd_amts) > 0

        t_data = tender_data_by_ocid.get(ocid)
        has_valid_estimate = t_data is not None and t_data.get("value_amount") is not None

        if has_valid_award and has_valid_estimate:
            processes_with_both_amounts += 1
        elif has_valid_award and not has_valid_estimate:
            processes_with_award_no_estimate += 1
        elif not has_valid_award and has_valid_estimate:
            processes_with_estimate_no_award += 1
        else:
            processes_without_any_amount += 1

    # CONSISTENCY: buyer_id vs procuringEntity_id
    buyer_vs_pe_exact_match = 0
    buyer_vs_pe_root_match = 0
    buyer_vs_pe_different_root = 0
    buyer_vs_pe_missing = 0

    for ocid, t_dict in tender_data_by_ocid.items():
        b_tuple = buyer_info_by_ocid.get(ocid)
        bid = b_tuple[0] if b_tuple else ""
        peid = t_dict.get("procuringEntity_id", "")
        if not bid or not peid:
            buyer_vs_pe_missing += 1
        elif bid == peid:
            buyer_vs_pe_exact_match += 1
        elif len(bid) >= 20 and len(peid) >= 20 and bid[:20] == peid[:20]:
            buyer_vs_pe_root_match += 1
        else:
            buyer_vs_pe_different_root += 1

    # AGGREGATE BY BUYER (for buyer summary CSV)
    # Map (buyer_id) -> stats
    buyer_aggregated_stats: dict[str, dict[str, Any]] = {}
    for ocid in all_process_ocids:
        b_tuple = buyer_info_by_ocid.get(ocid, ("", ""))
        bid, _ = b_tuple
        if not bid:
            bid = "EC-RUC-DESCONOCIDO"

        if bid not in buyer_aggregated_stats:
            # find most frequent name
            names_cnt = buyer_names_by_buyer_id.get(bid, Counter())
            most_freq_name = names_cnt.most_common(1)[0][0] if names_cnt else ""
            buyer_aggregated_stats[bid] = {
                "anio": year,
                "buyer_id": bid,
                "buyer_name_mas_frecuente": most_freq_name,
                "procesos": 0,
                "adjudicaciones": 0,
                "suma_adjudicado": 0.0,
                "suma_estimado": 0.0,
                "procesos_con_ambos_importes": 0,
                "procesos_sin_monto_adjudicado": 0,
            }

        stats = buyer_aggregated_stats[bid]
        stats["procesos"] += 1

        awd_list = awards_data_by_ocid.get(ocid, [])
        stats["adjudicaciones"] += len(awd_list)

        valid_awds = [a["amount"] for a in awd_list if a["amount"] is not None]
        has_awd_amount = len(valid_awds) > 0
        if has_awd_amount:
            stats["suma_adjudicado"] += sum(valid_awds)
        else:
            stats["procesos_sin_monto_adjudicado"] += 1

        t_data = tender_data_by_ocid.get(ocid)
        has_est_amount = t_data is not None and t_data.get("value_amount") is not None
        if has_est_amount:
            stats["suma_estimado"] += t_data["value_amount"]

        if has_awd_amount and has_est_amount:
            stats["procesos_con_ambos_importes"] += 1

    # Round buyer financial summaries
    for s in buyer_aggregated_stats.values():
        s["suma_adjudicado"] = round(s["suma_adjudicado"], 2)
        s["suma_estimado"] = round(s["suma_estimado"], 2)

    # Candidate date profiling
    cd_release = profile_candidate_date(release_date_strings, year)
    cd_tender = profile_candidate_date(tender_date_strings, year)
    cd_award = profile_candidate_date(award_date_strings, year)
    cd_contract = profile_candidate_date(contracts_date_strings, year)

    # Accuracy comparison (for 2025 against reference)
    accuracy_eval: dict[str, Any] = {}
    if year == 2025:
        ref_dollars = reference_awarded_2025 * 1_000_000.0
        diff_abs = abs(awards_sum_amount - ref_dollars)
        diff_rel = (awards_sum_amount - ref_dollars) / ref_dollars * 100.0
        accuracy_eval = {
            "reference_source": "Informe de Rendicion de Cuentas SERCOP 2025, p. 12 (cifra nacional provisional)",
            "reference_amount_usd": ref_dollars,
            "measured_awards_amount_usd": round(awards_sum_amount, 2),
            "difference_absolute_usd": round(diff_abs, 2),
            "difference_relative_pct": round(diff_rel, 2),
            "potential_explanatory_factors": {
                "awards_without_amount_count": award_amount_num_categories["empty"],
                "amount_vs_corrected_value_difference_count": amount_vs_corrected_diff,
                "awards_dates_outside_2025_count": cd_award["after_file_year"] + cd_award["before_2015"],
                "non_active_awards_count": sum(c for st, c in awards_status_counts.items() if st != "active"),
                "unexplained_difference_usd": round(diff_abs, 2),
            },
        }

    # Input file metadata
    inputs_meta: dict[str, Any] = {}
    for tbl_name, p in sorted(table_paths.items()):
        p_str = p.as_posix()
        if "/data/derivados/" in p_str:
            rel_path = "data/derivados/" + p_str.split("/data/derivados/", 1)[1]
        elif repo_root and p.is_relative_to(repo_root):
            rel_path = p.relative_to(repo_root).as_posix()
        else:
            rel_path = p.name

        inputs_meta[tbl_name] = {
            "relative_path": rel_path,
            "file_name": p.name,
            "size_bytes": p.stat().st_size,
            "sha256": calculate_sha256(p),
        }

    result = {
        "year": year,
        "input_files": inputs_meta,
        "control_totals": {
            "total_releases": releases_count,
            "distinct_ocids": len(releases_ocid_counts),
            "total_tender_rows": tender_count,
            "distinct_tender_ocids": len(tender_ocid_counts),
            "total_awards_rows": awards_count,
            "distinct_awards_ocids": len(awards_ocid_counts),
            "total_contracts_rows": contracts_count,
            "distinct_contracts_ocids": len(contracts_ocid_counts),
            "sum_awards_amount": round(awards_sum_amount, 2),
            "sum_tender_value_amount": round(tender_sum_value_amount, 2),
            "sum_contracts_amount": round(contracts_sum_amount, 2),
            "processes_with_both_amounts": processes_with_both_amounts,
            "pct_processes_with_both_amounts": round(processes_with_both_amounts / total_processes * 100, 2)
            if total_processes > 0
            else 0.0,
            "processes_with_award_no_estimate": processes_with_award_no_estimate,
            "pct_processes_with_award_no_estimate": round(processes_with_award_no_estimate / total_processes * 100, 2)
            if total_processes > 0
            else 0.0,
            "processes_with_estimate_no_award": processes_with_estimate_no_award,
            "pct_processes_with_estimate_no_award": round(processes_with_estimate_no_award / total_processes * 100, 2)
            if total_processes > 0
            else 0.0,
            "processes_without_any_amount": processes_without_any_amount,
            "pct_processes_without_any_amount": round(processes_without_any_amount / total_processes * 100, 2)
            if total_processes > 0
            else 0.0,
        },
        "completeness": {
            "buyer_id_missing": buyer_id_formats["empty"],
            "buyer_name_missing": releases_count - field_profilers["releases"]["buyer_name"].populated_count,
            "procurement_method_missing": tender_count - field_profilers["tender"]["procurementMethod"].populated_count,
            "procurement_method_details_missing": tender_count
            - field_profilers["tender"]["procurementMethodDetails"].populated_count,
            "tender_value_amount": {
                "empty": tender_value_num_categories["empty"],
                "zero": tender_value_num_categories["zero"],
                "positive": tender_value_num_categories["positive"],
                "negative": tender_value_num_categories["negative"],
                "non_numeric": tender_value_num_categories["non_numeric"],
                "completeness_pct_on_tender": round(
                    (field_profilers["tender"]["value_amount"].populated_count / tender_count * 100), 2
                )
                if tender_count > 0
                else 0.0,
                "completeness_pct_on_releases": round(
                    (field_profilers["tender"]["value_amount"].populated_count / releases_count * 100), 2
                )
                if releases_count > 0
                else 0.0,
            },
            "awards_amount": {
                "empty": award_amount_num_categories["empty"],
                "zero": award_amount_num_categories["zero"],
                "positive": award_amount_num_categories["positive"],
                "negative": award_amount_num_categories["negative"],
                "non_numeric": award_amount_num_categories["non_numeric"],
                "completeness_pct_on_awards": round(
                    (field_profilers["awards"]["amount"].populated_count / awards_count * 100), 2
                )
                if awards_count > 0
                else 0.0,
                "completeness_pct_on_releases": round(
                    (
                        len([o for o, a in awards_data_by_ocid.items() if any(x["amount"] is not None for x in a)])
                        / releases_count
                        * 100
                    ),
                    2,
                )
                if releases_count > 0
                else 0.0,
            },
            "corrected_value_amount": {
                "empty": awards_count - field_profilers["awards"]["correctedValue_amount"].populated_count,
                "populated": field_profilers["awards"]["correctedValue_amount"].populated_count,
            },
            "entered_value_amount": {
                "empty": awards_count - field_profilers["awards"]["enteredValue_amount"].populated_count,
                "populated": field_profilers["awards"]["enteredValue_amount"].populated_count,
            },
            "candidate_dates_coverage": {
                "release_date": {
                    "populated": cd_release["populated"],
                    "pct_on_releases": round(cd_release["populated"] / releases_count * 100, 2)
                    if releases_count > 0
                    else 0.0,
                },
                "tender_period_start_date": {
                    "populated": cd_tender["populated"],
                    "pct_on_tender": round(cd_tender["populated"] / tender_count * 100, 2) if tender_count > 0 else 0.0,
                    "pct_on_releases": round(cd_tender["populated"] / releases_count * 100, 2)
                    if releases_count > 0
                    else 0.0,
                },
                "award_date": {
                    "populated": cd_award["populated"],
                    "pct_on_awards": round(cd_award["populated"] / awards_count * 100, 2) if awards_count > 0 else 0.0,
                    "pct_on_releases": round(
                        len([o for o, a in awards_data_by_ocid.items() if any(x["date"] for x in a)])
                        / releases_count
                        * 100,
                        2,
                    )
                    if releases_count > 0
                    else 0.0,
                },
                "contract_date_signed": {
                    "populated": cd_contract["populated"],
                    "pct_on_contracts": round(cd_contract["populated"] / contracts_count * 100, 2)
                    if contracts_count > 0
                    else 0.0,
                    "pct_on_releases": round(cd_contract["populated"] / releases_count * 100, 2)
                    if releases_count > 0
                    else 0.0,
                },
            },
        },
        "validity": {
            "tender_value_amount": dict(tender_value_num_categories),
            "awards_amount": dict(award_amount_num_categories),
            "currencies": {
                "tender_value_currency": dict(tender_value_currencies),
                "awards_currency": dict(award_currencies),
                "contracts_currency": dict(contracts_currencies),
            },
            "dates": {
                "release_date": {
                    "unparseable": cd_release["unparseable"],
                    "before_2015": cd_release["before_2015"],
                    "future": cd_release["future"],
                    "after_file_year": cd_release["after_file_year"],
                },
                "tender_period_start_date": {
                    "unparseable": cd_tender["unparseable"],
                    "before_2015": cd_tender["before_2015"],
                    "future": cd_tender["future"],
                    "after_file_year": cd_tender["after_file_year"],
                },
                "award_date": {
                    "unparseable": cd_award["unparseable"],
                    "before_2015": cd_award["before_2015"],
                    "future": cd_award["future"],
                    "after_file_year": cd_award["after_file_year"],
                },
                "contract_date_signed": {
                    "unparseable": cd_contract["unparseable"],
                    "before_2015": cd_contract["before_2015"],
                    "future": cd_contract["future"],
                    "after_file_year": cd_contract["after_file_year"],
                },
            },
            "procurement_methods": {
                "distribution": dict(procurement_methods_counts),
                "unexpected_methods": {
                    k: v for k, v in procurement_methods_counts.items() if k not in EXPECTED_PROCUREMENT_METHODS
                },
            },
            "status_distributions": {
                "tender": dict(tender_status_counts),
                "awards": dict(awards_status_counts),
                "contracts": dict(contracts_status_counts),
            },
        },
        "uniqueness": {
            "releases_ocid_duplicates_within_year": sum(c - 1 for c in releases_ocid_counts.values() if c > 1),
            "releases_pairs_ocid_relid_duplicates": releases_pairs_dups,
            "tender_ocid_duplicates": sum(c - 1 for c in tender_ocid_counts.values() if c > 1),
            "tender_pairs_duplicates": tender_pairs_dups,
            "awards_pairs_duplicates": awards_pairs_dups,
            "awards_duplicate_id_within_process": dup_award_ids_within_proc,
            "contracts_pairs_duplicates": contracts_pairs_dups,
            "multiplicity_of_awards": {
                "processes_with_0_awards": award_counts_histogram[0],
                "processes_with_1_award": award_counts_histogram[1],
                "processes_with_more_than_1_award": sum(
                    cnt for n_awd, cnt in award_counts_histogram.items() if n_awd > 1
                ),
                "full_awards_per_process_histogram": dict(sorted(award_counts_histogram.items())),
            },
        },
        "consistency": {
            "buyer_id_formats": dict(buyer_id_formats),
            "buyer_names_per_buyer_id": {
                "distinct_buyer_ids": len(buyer_names_by_buyer_id),
                "buyer_ids_with_1_name": sum(1 for cnt in buyer_names_by_buyer_id.values() if len(cnt) == 1),
                "buyer_ids_with_multiple_names": sum(1 for cnt in buyer_names_by_buyer_id.values() if len(cnt) > 1),
                "max_names_for_single_buyer_id": max((len(cnt) for cnt in buyer_names_by_buyer_id.values()), default=0),
            },
            "buyer_ids_per_buyer_name": {
                "distinct_buyer_names": len(buyer_ids_by_buyer_name),
                "buyer_names_with_1_id": sum(1 for cnt in buyer_ids_by_buyer_name.values() if len(cnt) == 1),
                "buyer_names_with_multiple_ids": sum(1 for cnt in buyer_ids_by_buyer_name.values() if len(cnt) > 1),
                "max_ids_for_single_buyer_name": max((len(cnt) for cnt in buyer_ids_by_buyer_name.values()), default=0),
            },
            "buyer_id_vs_procuring_entity_id": {
                "exact_match": buyer_vs_pe_exact_match,
                "same_13digit_root_different_suffix": buyer_vs_pe_root_match,
                "different_root": buyer_vs_pe_different_root,
                "missing_either": buyer_vs_pe_missing,
            },
            "amount_vs_corrected_and_entered_value": {
                "amount_vs_corrected_both_present": amount_vs_corrected_both_present,
                "amount_vs_corrected_different": amount_vs_corrected_diff,
                "amount_vs_entered_both_present": amount_vs_entered_both_present,
                "amount_vs_entered_different": amount_vs_entered_diff,
            },
            "procurement_method_details_cardinality": {
                pm: len(details) for pm, details in sorted(procurement_details_by_method.items())
            },
        },
        "accuracy": accuracy_eval,
        "timeliness": {
            "release_date": {
                "pct_outside_file_year": cd_release["pct_after_file_year"],
                "min_date": cd_release["min_date"],
                "max_date": cd_release["max_date"],
                "monthly_distribution": cd_release["monthly_distribution"],
            },
            "tender_period_start_date": {
                "pct_outside_file_year": cd_tender["pct_after_file_year"],
                "min_date": cd_tender["min_date"],
                "max_date": cd_tender["max_date"],
                "monthly_distribution": cd_tender["monthly_distribution"],
            },
            "award_date": {
                "pct_outside_file_year": cd_award["pct_after_file_year"],
                "min_date": cd_award["min_date"],
                "max_date": cd_award["max_date"],
                "monthly_distribution": cd_award["monthly_distribution"],
            },
            "contract_date_signed": {
                "pct_outside_file_year": cd_contract["pct_after_file_year"],
                "min_date": cd_contract["min_date"],
                "max_date": cd_contract["max_date"],
                "monthly_distribution": cd_contract["monthly_distribution"],
            },
        },
        "field_profiles": {
            tbl: {col: prof.to_dict() for col, prof in prof_dict.items()} for tbl, prof_dict in field_profilers.items()
        },
        "_ocids_set": all_process_ocids,
        "_buyer_summary": buyer_aggregated_stats,
    }

    return result


def compute_cross_year_metrics(year_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute cross-year uniqueness and multi-year ocid overlaps."""
    ocid_by_year: dict[int, set[str]] = {yr["year"]: yr["_ocids_set"] for yr in year_results}
    years = sorted(ocid_by_year.keys())

    pairwise_overlaps: dict[str, int] = {}
    for i, y1 in enumerate(years):
        for y2 in years[i + 1 :]:
            shared = len(ocid_by_year[y1].intersection(ocid_by_year[y2]))
            pairwise_overlaps[f"{y1}_{y2}"] = shared

    # Global ocid counter across years
    global_ocid_counts: Counter[str] = Counter()
    for _yr, ocids in ocid_by_year.items():
        for o in ocids:
            global_ocid_counts[o] += 1

    multi_year_ocids = sum(1 for c in global_ocid_counts.values() if c > 1)
    total_distinct_global_ocids = len(global_ocid_counts)

    return {
        "total_distinct_global_ocids": total_distinct_global_ocids,
        "multi_year_ocids_count": multi_year_ocids,
        "pairwise_overlaps": pairwise_overlaps,
    }


def generate_summary_csv_rows(year_results: list[dict[str, Any]], cross_year: dict[str, Any]) -> list[dict[str, str]]:
    """Build the consolidated summary rows for perfil-calidad-sercop-resumen.csv."""
    rows: list[dict[str, str]] = []

    def add_row(dimension: str, tabla: str, campo: str, metrica: str, anio: str, valor: Any, unidad: str) -> None:
        rows.append(
            {
                "dimension": dimension,
                "tabla": tabla,
                "campo": campo,
                "metrica": metrica,
                "anio": str(anio),
                "valor": str(valor),
                "unidad": unidad,
            }
        )

    # 1. Rows per year
    for yr_res in year_results:
        yr = str(yr_res["year"])
        ct = yr_res["control_totals"]
        comp = yr_res["completeness"]
        val = yr_res["validity"]
        uniq = yr_res["uniqueness"]
        cons = yr_res["consistency"]
        time_info = yr_res["timeliness"]

        # Control
        add_row("control", "releases", "*", "filas_releases", yr, ct["total_releases"], "filas")
        add_row("control", "releases", "ocid", "procesos_distintos", yr, ct["distinct_ocids"], "procesos")
        add_row("control", "tender", "*", "filas_tender", yr, ct["total_tender_rows"], "filas")
        add_row("control", "awards", "*", "filas_awards", yr, ct["total_awards_rows"], "adjudicaciones")
        add_row("control", "contracts", "*", "filas_contracts", yr, ct["total_contracts_rows"], "contratos")
        add_row("control", "awards", "amount", "suma_monto_adjudicado", yr, f"{ct['sum_awards_amount']:.2f}", "USD")
        add_row(
            "control",
            "tender",
            "value_amount",
            "suma_valor_estimado",
            yr,
            f"{ct['sum_tender_value_amount']:.2f}",
            "USD",
        )
        add_row(
            "control",
            "Procesos_SERCOP",
            "amount_ambos",
            "procesos_con_ambos_importes",
            yr,
            ct["processes_with_both_amounts"],
            "procesos",
        )
        add_row(
            "control",
            "Procesos_SERCOP",
            "amount_ambos",
            "pct_procesos_con_ambos_importes",
            yr,
            ct["pct_processes_with_both_amounts"],
            "porcentaje",
        )
        add_row(
            "control",
            "Procesos_SERCOP",
            "amount_adjudicado_solo",
            "procesos_con_adjudicacion_sin_estimado",
            yr,
            ct["processes_with_award_no_estimate"],
            "procesos",
        )
        add_row(
            "control",
            "Procesos_SERCOP",
            "amount_estimado_solo",
            "procesos_con_estimado_sin_adjudicacion",
            yr,
            ct["processes_with_estimate_no_award"],
            "procesos",
        )
        add_row(
            "control",
            "Procesos_SERCOP",
            "amount_ninguno",
            "procesos_sin_ningun_importe",
            yr,
            ct["processes_without_any_amount"],
            "procesos",
        )

        # Completitud
        add_row("completitud", "releases", "buyer_id", "filas_vacias", yr, comp["buyer_id_missing"], "filas")
        add_row("completitud", "releases", "buyer_name", "filas_vacias", yr, comp["buyer_name_missing"], "filas")
        add_row(
            "completitud",
            "tender",
            "procurementMethod",
            "filas_vacias",
            yr,
            comp["procurement_method_missing"],
            "filas",
        )
        add_row(
            "completitud",
            "tender",
            "procurementMethodDetails",
            "filas_vacias",
            yr,
            comp["procurement_method_details_missing"],
            "filas",
        )
        add_row(
            "completitud", "tender", "value_amount", "filas_vacias", yr, comp["tender_value_amount"]["empty"], "filas"
        )
        add_row("completitud", "tender", "value_amount", "filas_cero", yr, comp["tender_value_amount"]["zero"], "filas")
        add_row(
            "completitud",
            "tender",
            "value_amount",
            "pct_completitud_sobre_tender",
            yr,
            comp["tender_value_amount"]["completeness_pct_on_tender"],
            "porcentaje",
        )
        add_row(
            "completitud",
            "tender",
            "value_amount",
            "pct_completitud_sobre_releases",
            yr,
            comp["tender_value_amount"]["completeness_pct_on_releases"],
            "porcentaje",
        )
        add_row("completitud", "awards", "amount", "filas_vacias", yr, comp["awards_amount"]["empty"], "filas")
        add_row("completitud", "awards", "amount", "filas_cero", yr, comp["awards_amount"]["zero"], "filas")
        add_row(
            "completitud",
            "awards",
            "amount",
            "pct_completitud_sobre_awards",
            yr,
            comp["awards_amount"]["completeness_pct_on_awards"],
            "porcentaje",
        )
        add_row(
            "completitud",
            "awards",
            "correctedValue_amount",
            "filas_vacias",
            yr,
            comp["corrected_value_amount"]["empty"],
            "filas",
        )
        add_row(
            "completitud",
            "awards",
            "enteredValue_amount",
            "filas_vacias",
            yr,
            comp["entered_value_amount"]["empty"],
            "filas",
        )
        add_row(
            "completitud",
            "releases",
            "date",
            "pct_completitud_sobre_releases",
            yr,
            comp["candidate_dates_coverage"]["release_date"]["pct_on_releases"],
            "porcentaje",
        )
        add_row(
            "completitud",
            "tender",
            "tenderPeriod_startDate",
            "pct_completitud_sobre_releases",
            yr,
            comp["candidate_dates_coverage"]["tender_period_start_date"]["pct_on_releases"],
            "porcentaje",
        )
        add_row(
            "completitud",
            "awards",
            "date",
            "pct_completitud_sobre_releases",
            yr,
            comp["candidate_dates_coverage"]["award_date"]["pct_on_releases"],
            "porcentaje",
        )
        add_row(
            "completitud",
            "contracts",
            "dateSigned",
            "pct_completitud_sobre_releases",
            yr,
            comp["candidate_dates_coverage"]["contract_date_signed"]["pct_on_releases"],
            "porcentaje",
        )

        # Validez
        add_row(
            "validez",
            "tender",
            "value_amount",
            "filas_monto_negativo",
            yr,
            val["tender_value_amount"].get("negative", 0),
            "filas",
        )
        add_row(
            "validez",
            "tender",
            "value_amount",
            "filas_monto_no_numerico",
            yr,
            val["tender_value_amount"].get("non_numeric", 0),
            "filas",
        )
        add_row(
            "validez", "awards", "amount", "filas_monto_negativo", yr, val["awards_amount"].get("negative", 0), "filas"
        )
        add_row(
            "validez",
            "awards",
            "amount",
            "filas_monto_no_numerico",
            yr,
            val["awards_amount"].get("non_numeric", 0),
            "filas",
        )
        non_usd_ten = sum(c for k, c in val["currencies"].get("tender_value_currency", {}).items() if k != "USD")
        non_usd_awd = sum(c for k, c in val["currencies"].get("awards_currency", {}).items() if k != "USD")
        add_row("validez", "tender", "value_currency", "moneda_no_usd", yr, non_usd_ten, "filas")
        add_row("validez", "awards", "currency", "moneda_no_usd", yr, non_usd_awd, "filas")
        add_row(
            "validez",
            "releases",
            "date",
            "fechas_no_interpretables",
            yr,
            val["dates"]["release_date"]["unparseable"],
            "filas",
        )
        add_row(
            "validez",
            "releases",
            "date",
            "fechas_anteriores_2015",
            yr,
            val["dates"]["release_date"]["before_2015"],
            "filas",
        )
        add_row(
            "validez",
            "releases",
            "date",
            "fechas_futuras_tras_corte",
            yr,
            val["dates"]["release_date"]["future"],
            "filas",
        )
        add_row(
            "validez",
            "releases",
            "date",
            "fechas_posteriores_al_archivo",
            yr,
            val["dates"]["release_date"]["after_file_year"],
            "filas",
        )
        add_row(
            "validez",
            "tender",
            "procurementMethod",
            "metodos_fuera_de_catalogo",
            yr,
            sum(val["procurement_methods"].get("unexpected_methods", {}).values()),
            "filas",
        )

        # Unicidad
        add_row(
            "unicidad",
            "releases",
            "ocid",
            "ocid_duplicados_en_anio",
            yr,
            uniq["releases_ocid_duplicates_within_year"],
            "filas",
        )
        add_row(
            "unicidad",
            "releases",
            "(ocid,id)",
            "pares_duplicados",
            yr,
            uniq["releases_pairs_ocid_relid_duplicates"],
            "filas",
        )
        add_row(
            "unicidad", "tender", "(ocid,release_id)", "pares_duplicados", yr, uniq["tender_pairs_duplicates"], "filas"
        )
        add_row(
            "unicidad",
            "awards",
            "(ocid,release_id)",
            "pares_duplicados",
            yr,
            uniq["awards_pairs_duplicates"],
            "filas",
        )
        add_row(
            "unicidad",
            "contracts",
            "(ocid,release_id)",
            "pares_duplicados",
            yr,
            uniq["contracts_pairs_duplicates"],
            "filas",
        )
        add_row(
            "unicidad",
            "awards",
            "(ocid,id)",
            "award_id_duplicado_en_proceso",
            yr,
            uniq["awards_duplicate_id_within_process"],
            "filas",
        )
        add_row(
            "unicidad",
            "Adjudicaciones_SERCOP",
            "ocid",
            "procesos_multi_adjudicacion",
            yr,
            uniq["multiplicity_of_awards"]["processes_with_more_than_1_award"],
            "procesos",
        )

        # Consistencia
        add_row(
            "consistencia",
            "releases",
            "buyer_id",
            "buyer_id_forma_simple",
            yr,
            cons["buyer_id_formats"].get("simple", 0),
            "filas",
        )
        add_row(
            "consistencia",
            "releases",
            "buyer_id",
            "buyer_id_con_sufijo",
            yr,
            cons["buyer_id_formats"].get("suffix", 0),
            "filas",
        )
        add_row(
            "consistencia",
            "releases",
            "buyer_id",
            "buyer_id_malformado",
            yr,
            cons["buyer_id_formats"].get("malformed", 0),
            "filas",
        )
        add_row(
            "consistencia",
            "releases",
            "buyer_id",
            "buyer_id_con_multiples_nombres",
            yr,
            cons["buyer_names_per_buyer_id"]["buyer_ids_with_multiple_names"],
            "entidades",
        )
        add_row(
            "consistencia",
            "releases",
            "buyer_name",
            "buyer_name_con_multiples_ids",
            yr,
            cons["buyer_ids_per_buyer_name"]["buyer_names_with_multiple_ids"],
            "nombres",
        )
        add_row(
            "consistencia",
            "tender",
            "procuringEntity_id",
            "coincidencia_exacta_con_buyer_id",
            yr,
            cons["buyer_id_vs_procuring_entity_id"]["exact_match"],
            "filas",
        )
        add_row(
            "consistencia",
            "tender",
            "procuringEntity_id",
            "coincidencia_raiz_con_buyer_id",
            yr,
            cons["buyer_id_vs_procuring_entity_id"]["same_13digit_root_different_suffix"],
            "filas",
        )
        add_row(
            "consistencia",
            "tender",
            "procuringEntity_id",
            "raiz_diferente_de_buyer_id",
            yr,
            cons["buyer_id_vs_procuring_entity_id"]["different_root"],
            "filas",
        )
        add_row(
            "consistencia",
            "awards",
            "amount_vs_corrected",
            "amount_difiere_de_corrected",
            yr,
            cons["amount_vs_corrected_and_entered_value"]["amount_vs_corrected_different"],
            "filas",
        )
        add_row(
            "consistencia",
            "awards",
            "amount_vs_entered",
            "amount_difiere_de_entered",
            yr,
            cons["amount_vs_corrected_and_entered_value"]["amount_vs_entered_different"],
            "filas",
        )

        # Exactitud (if 2025)
        if yr == "2025" and yr_res.get("accuracy"):
            acc = yr_res["accuracy"]
            add_row(
                "exactitud",
                "awards",
                "amount",
                "monto_adjudicado_referencia_oficial",
                yr,
                f"{acc['reference_amount_usd']:.2f}",
                "USD",
            )
            add_row(
                "exactitud",
                "awards",
                "amount",
                "diferencia_absoluta_vs_referencia",
                yr,
                f"{acc['difference_absolute_usd']:.2f}",
                "USD",
            )
            add_row(
                "exactitud",
                "awards",
                "amount",
                "diferencia_relativa_vs_referencia",
                yr,
                acc["difference_relative_pct"],
                "porcentaje",
            )

        # Oportunidad
        add_row(
            "oportunidad",
            "releases",
            "date",
            "pct_fecha_fuera_del_anio_archivo",
            yr,
            time_info["release_date"]["pct_outside_file_year"],
            "porcentaje",
        )
        add_row(
            "oportunidad",
            "releases",
            "date",
            "ultima_fecha_observada",
            yr,
            time_info["release_date"]["max_date"] or "",
            "fecha",
        )

    # 2. Total row (2021-2025)
    tot_releases = sum(y["control_totals"]["total_releases"] for y in year_results)
    tot_tender = sum(y["control_totals"]["total_tender_rows"] for y in year_results)
    tot_awards = sum(y["control_totals"]["total_awards_rows"] for y in year_results)
    tot_contracts = sum(y["control_totals"]["total_contracts_rows"] for y in year_results)
    tot_awd_amt = sum(y["control_totals"]["sum_awards_amount"] for y in year_results)
    tot_ten_amt = sum(y["control_totals"]["sum_tender_value_amount"] for y in year_results)
    tot_both = sum(y["control_totals"]["processes_with_both_amounts"] for y in year_results)
    tot_awd_only = sum(y["control_totals"]["processes_with_award_no_estimate"] for y in year_results)
    tot_ten_only = sum(y["control_totals"]["processes_with_estimate_no_award"] for y in year_results)
    tot_neither = sum(y["control_totals"]["processes_without_any_amount"] for y in year_results)
    tot_multi_awd = sum(
        y["uniqueness"]["multiplicity_of_awards"]["processes_with_more_than_1_award"] for y in year_results
    )

    add_row("control", "releases", "*", "filas_releases", "total", tot_releases, "filas")
    add_row(
        "control",
        "releases",
        "ocid",
        "procesos_distintos",
        "total",
        cross_year["total_distinct_global_ocids"],
        "procesos",
    )
    add_row("control", "tender", "*", "filas_tender", "total", tot_tender, "filas")
    add_row("control", "awards", "*", "filas_awards", "total", tot_awards, "adjudicaciones")
    add_row("control", "contracts", "*", "filas_contracts", "total", tot_contracts, "contratos")
    add_row("control", "awards", "amount", "suma_monto_adjudicado", "total", f"{tot_awd_amt:.2f}", "USD")
    add_row("control", "tender", "value_amount", "suma_valor_estimado", "total", f"{tot_ten_amt:.2f}", "USD")
    add_row("control", "Procesos_SERCOP", "amount_ambos", "procesos_con_ambos_importes", "total", tot_both, "procesos")
    add_row(
        "control",
        "Procesos_SERCOP",
        "amount_ambos",
        "pct_procesos_con_ambos_importes",
        "total",
        round(tot_both / tot_releases * 100, 2) if tot_releases > 0 else 0.0,
        "porcentaje",
    )
    add_row(
        "control",
        "Procesos_SERCOP",
        "amount_adjudicado_solo",
        "procesos_con_adjudicacion_sin_estimado",
        "total",
        tot_awd_only,
        "procesos",
    )
    add_row(
        "control",
        "Procesos_SERCOP",
        "amount_estimado_solo",
        "procesos_con_estimado_sin_adjudicacion",
        "total",
        tot_ten_only,
        "procesos",
    )
    add_row(
        "control", "Procesos_SERCOP", "amount_ninguno", "procesos_sin_ningun_importe", "total", tot_neither, "procesos"
    )

    # Cross-year uniqueness
    add_row(
        "unicidad",
        "releases",
        "ocid",
        "ocid_compartidos_entre_anios",
        "total",
        cross_year["multi_year_ocids_count"],
        "procesos",
    )
    add_row(
        "unicidad", "Adjudicaciones_SERCOP", "ocid", "procesos_multi_adjudicacion", "total", tot_multi_awd, "procesos"
    )
    tot_awd_pairs_dups = sum(y["uniqueness"]["awards_pairs_duplicates"] for y in year_results)
    tot_cnt_pairs_dups = sum(y["uniqueness"]["contracts_pairs_duplicates"] for y in year_results)
    add_row("unicidad", "awards", "(ocid,release_id)", "pares_duplicados", "total", tot_awd_pairs_dups, "filas")
    add_row("unicidad", "contracts", "(ocid,release_id)", "pares_duplicados", "total", tot_cnt_pairs_dups, "filas")

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--derived-dir",
        type=Path,
        default=Path("data/derivados"),
        help="Path to directory containing derived CSV folders for each year",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/h2/evidencia"),
        help="Output directory for profiling JSON and CSV outputs",
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=[2021, 2022, 2023, 2024, 2025],
        help="Years to profile (default: 2021 2022 2023 2024 2025)",
    )
    parser.add_argument(
        "--reference-awarded-2025",
        type=float,
        default=7318.7,
        help="Official published reference awarded figure in millions USD for 2025 (default: 7318.7)",
    )
    parser.add_argument(
        "--buyer-summary-csv",
        type=Path,
        default=None,
        help="Path for buyer summary CSV output (default: docs/h2/evidencia/perfil-calidad-sercop-por-comprador.csv)",
    )
    parser.add_argument(
        "--output-suffix",
        type=str,
        default="",
        help="Optional suffix for output filenames (e.g. -v2)",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    derived_dir = args.derived_dir if args.derived_dir.is_absolute() else repo_root / args.derived_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else repo_root / args.output_dir
    suffix = args.output_suffix
    buyer_summary_default_name = f"perfil-calidad-sercop-por-comprador{suffix}.csv"
    buyer_summary_path = (
        args.buyer_summary_csv if args.buyer_summary_csv is not None else output_dir / buyer_summary_default_name
    )
    if not buyer_summary_path.is_absolute():
        buyer_summary_path = repo_root / buyer_summary_path

    # Check that outputs do not overwrite existing files
    resumen_csv_path = output_dir / f"perfil-calidad-sercop-resumen{suffix}.csv"
    existing_outputs: list[Path] = []
    if resumen_csv_path.exists():
        existing_outputs.append(resumen_csv_path)
    if buyer_summary_path.exists():
        existing_outputs.append(buyer_summary_path)

    for yr in args.years:
        json_yr_path = output_dir / f"perfil-calidad-sercop-{yr}{suffix}.json"
        if json_yr_path.exists():
            existing_outputs.append(json_yr_path)

    if existing_outputs:
        print("ERROR: Refusing to overwrite existing output files:", file=sys.stderr)
        for p in existing_outputs:
            print(f"  - {p}", file=sys.stderr)
        return 1

    years_data = discover_year_data(derived_dir)
    missing_years = [y for y in args.years if y not in years_data]
    if missing_years:
        print(f"ERROR: Missing derived data folders for years: {missing_years} in {derived_dir}", file=sys.stderr)
        return 1

    script_path = Path(__file__).resolve()
    script_sha256 = compute_script_sha256(script_path)

    cmd_parts = [
        "python",
        "-I",
        f"scripts/{script_path.name}",
        "--derived-dir",
        "data/derivados",
        "--output-dir",
        "docs/h2/evidencia",
        "--years",
        *[str(y) for y in sorted(args.years)],
        "--reference-awarded-2025",
        str(args.reference_awarded_2025),
    ]
    if suffix:
        cmd_parts.extend(["--output-suffix", suffix])
    cmd_parts.extend(["--buyer-summary-csv", f"docs/h2/evidencia/{buyer_summary_path.name}"])
    exec_cmd = " ".join(cmd_parts)
    exec_time_utc = datetime.now(UTC).isoformat()

    print(f"Starting SERCOP quality profiling for years: {args.years}")
    print(f"Script SHA-256: {script_sha256}")

    year_results: list[dict[str, Any]] = []
    all_buyer_summaries: list[dict[str, Any]] = []

    for yr in sorted(args.years):
        print(f"\n--- Profiling year {yr} ---")
        tables = years_data[yr]
        res = profile_year(yr, tables, reference_awarded_2025=args.reference_awarded_2025, repo_root=repo_root)
        # Extract internal tracking before serialization
        buyer_summary_dict = res.pop("_buyer_summary", {})
        all_buyer_summaries.extend(buyer_summary_dict.values())
        year_results.append(res)
        print(f"  Releases: {res['control_totals']['total_releases']}")
        print(f"  Distinct ocids: {res['control_totals']['distinct_ocids']}")
        print(f"  Awards rows: {res['control_totals']['total_awards_rows']}")
        print(f"  Awards sum: ${res['control_totals']['sum_awards_amount']:,.2f}")
        pct_both = res["control_totals"]["pct_processes_with_both_amounts"]
        cnt_both = res["control_totals"]["processes_with_both_amounts"]
        print(f"  Processes with both amounts: {cnt_both} ({pct_both}%)")

    # Cross-year uniqueness
    cross_year = compute_cross_year_metrics(year_results)
    print("\n--- Cross-Year Metrics ---")
    print(f"Total distinct global ocids: {cross_year['total_distinct_global_ocids']}")
    print(f"Multi-year ocids: {cross_year['multi_year_ocids_count']}")
    for k, v in cross_year["pairwise_overlaps"].items():
        print(f"  Overlap {k}: {v}")

    # Build summary CSV rows
    summary_rows = generate_summary_csv_rows(year_results, cross_year)

    # Ensure output directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    buyer_summary_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean internal fields for JSON export and save annual JSONs
    for res in year_results:
        yr = res["year"]
        res.pop("_ocids_set", None)
        # Attach execution metadata
        full_json_payload = {
            "metadata": {
                "script_name": script_path.name,
                "script_sha256": script_sha256,
                "execution_command": exec_cmd,
                "executed_at_utc": exec_time_utc,
                "year": yr,
            },
            **res,
        }
        json_out = output_dir / f"perfil-calidad-sercop-{yr}{suffix}.json"
        with json_out.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(full_json_payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Saved: {json_out}")

    # Save summary CSV
    with resumen_csv_path.open("w", encoding="utf-8", newline="\n") as f:
        fieldnames = ["dimension", "tabla", "campo", "metrica", "anio", "valor", "unidad"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Saved: {resumen_csv_path} ({len(summary_rows)} rows)")

    # Save buyer summary CSV
    all_buyer_summaries.sort(key=lambda x: (x["anio"], x["buyer_id"]))
    with buyer_summary_path.open("w", encoding="utf-8", newline="\n") as f:
        fieldnames = [
            "anio",
            "buyer_id",
            "buyer_name_mas_frecuente",
            "procesos",
            "adjudicaciones",
            "suma_adjudicado",
            "suma_estimado",
            "procesos_con_ambos_importes",
            "procesos_sin_monto_adjudicado",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_buyer_summaries)
    print(f"Saved: {buyer_summary_path} ({len(all_buyer_summaries)} rows)")

    print("\nProfiling completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
