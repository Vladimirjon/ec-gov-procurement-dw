"""Aggregate measurements that the H3 dimensional design relies on.

Reads the portal CSV tables (releases, tender, awards) of every ``sercop-portal-csv-AAAA-*`` folder
under the given directory and writes one JSON with counts and sums only: no record, buyer or
supplier value is written. Standard library only.

Usage:
    python -I scripts/measure_h3_design.py DERIVADOS_DIR --output docs/h3/evidencia/NAME.json
"""

import argparse
from collections import Counter
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import sys


WINDOW_FIRST_YEAR = 2021
WINDOW_LAST_YEAR = 2025
ROOT_RE = re.compile(r"^EC-RUC-(\d{13})(?:-.+)?$")
CATALOG_PREFIX = "Catálogo electrónico"
NO_DETAIL = "Sin detalle"


def read_rows(path):
    with open(path, encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def to_number(text):
    """Return the amount as float, or None when the cell is empty (an empty cell is not 0)."""
    text = text.strip()
    return float(text) if text else None


def procedure_of(detail):
    """Collapse procurementMethodDetails to a procedure name.

    The 681 catalogue details end in the framework agreement ("... en el convenio ..."), which is a
    product category and not a method: only the text before it is kept. Whitespace and line breaks
    are normalised (Q-11 of the H2 diagnosis).
    """
    text = " ".join(detail.split())
    if not text:
        return NO_DETAIL
    if text.startswith(CATALOG_PREFIX):
        return text.split(",")[0].split(" en el convenio")[0]
    return text


def load_tables(base):
    folders = sorted(base.glob("sercop-portal-csv-*"))
    processes = {}  # ocid -> (year-month as int, root or None, archive year)
    buyer_ids = set()
    tenders = {}  # ocid -> (method, detail, estimated amount or None)
    awards = {}  # ocid -> [rows, sum of amounts, rows with amount]
    counts = Counter()
    for folder in folders:
        year = int(folder.name.split("-")[3])
        for row in read_rows(folder / f"releases_{year}.csv"):
            moment = datetime.fromisoformat(row["date"])
            match = ROOT_RE.match(row["buyer_id"])
            processes[row["ocid"]] = (moment.year * 100 + moment.month, match and match.group(1), year)
            buyer_ids.add(row["buyer_id"])
        for row in read_rows(folder / f"tender_{year}.csv"):
            counts["tender_rows"] += 1
            counts["tender_repeated_ocid"] += row["ocid"] in tenders
            tenders[row["ocid"]] = (
                row["procurementMethod"],
                row["procurementMethodDetails"],
                to_number(row["value_amount"]),
            )
        for row in read_rows(folder / f"awards_{year}.csv"):
            counts["awards_rows"] += 1
            amount = to_number(row["amount"])
            entry = awards.setdefault(row["ocid"], [0, 0.0, 0])
            entry[0] += 1
            if amount is not None:
                entry[1] += amount
                entry[2] += 1
    return processes, buyer_ids, tenders, awards, counts


def measure(base):
    processes, buyer_ids, tenders, awards, counts = load_tables(Path(base))
    in_window = {o for o, p in processes.items() if WINDOW_FIRST_YEAR <= p[0] // 100 <= WINDOW_LAST_YEAR}
    has_amount = {o for o, v in awards.items() if v[2] > 0}
    multiple = {o for o, v in awards.items() if v[0] > 1}
    both = {o for o in has_amount if o in tenders and tenders[o][2] is not None}

    def awarded(ocids):
        return round(sum(awards[o][1] for o in ocids if o in awards), 2)

    out = {
        "processes": len(processes),
        "tender_rows": counts["tender_rows"],
        "tender_repeated_ocid": counts["tender_repeated_ocid"],
        "awards_rows": counts["awards_rows"],
        "awards_without_process": sum(1 for o in awards if o not in processes),
    }

    # Time window (rule: releases.date)
    by_year = Counter(p[0] // 100 for p in processes.values())
    out["processes_by_release_year"] = dict(sorted(by_year.items()))
    out["processes_in_window"] = len(in_window)
    out["processes_after_window"] = sum(v for y, v in by_year.items() if y > WINDOW_LAST_YEAR)
    out["processes_before_window"] = sum(v for y, v in by_year.items() if y < WINDOW_FIRST_YEAR)
    out["months_with_processes_in_window"] = len({processes[o][0] for o in in_window})
    out["awarded_total"] = awarded(awards)
    out["awarded_in_window"] = awarded(in_window)
    out["awarded_outside_window"] = awarded(o for o in processes if o not in in_window)
    out["processes_with_award_outside_window"] = sum(1 for o in has_amount if o not in in_window)
    out["in_window_with_other_archive_year"] = sum(1 for o in in_window if processes[o][0] // 100 != processes[o][2])

    # Method
    methods = Counter(t[0] for t in tenders.values())
    details = Counter(t[1] for t in tenders.values())
    details_normalised = Counter(" ".join(t[1].split()) for t in tenders.values())
    detail_methods = {}
    for method, detail in {(t[0], " ".join(t[1].split())) for t in tenders.values()}:
        detail_methods.setdefault(detail, set()).add(method)
    procedures = Counter((t[0], procedure_of(t[1])) for t in tenders.values())
    out["method_values"] = dict(methods.most_common())
    out["method_details_distinct"] = len(details)
    out["method_details_distinct_normalised"] = len(details_normalised)
    out["method_details_empty"] = details.get("", 0)
    out["method_details_with_several_methods"] = sum(1 for m in detail_methods.values() if len(m) > 1)
    out["catalogue_details_distinct"] = sum(1 for d in details_normalised if d.startswith(CATALOG_PREFIX))
    out["catalogue_tender_rows"] = sum(n for d, n in details_normalised.items() if d.startswith(CATALOG_PREFIX))
    out["procedures_distinct"] = len(procedures)
    awarded_by_procedure = Counter()
    for o in has_amount:
        if o in tenders:
            awarded_by_procedure[(tenders[o][0], procedure_of(tenders[o][1]))] += awards[o][1]
    out["procedures"] = [
        {"method": m, "procedure": p, "tenders": n, "awarded": round(awarded_by_procedure[(m, p)], 2)}
        for (m, p), n in sorted(procedures.items(), key=lambda kv: -kv[1])
    ]
    out["processes_without_tender_row"] = sum(1 for o in processes if o not in tenders)
    out["awarded_without_tender_row"] = awarded(o for o in processes if o not in tenders)
    awarded_by_method = Counter()
    for o in processes:
        if o in has_amount and o in tenders:
            awarded_by_method[tenders[o][0]] += awards[o][1]
    out["awarded_by_method"] = {m: round(v, 2) for m, v in awarded_by_method.most_common()}

    # Awards and amounts
    out["processes_with_award_rows"] = len(awards)
    out["processes_with_awarded_amount"] = len(has_amount)
    out["processes_with_award_rows_and_no_amount"] = len(awards) - len(has_amount)
    out["processes_with_partial_amounts"] = sum(1 for v in awards.values() if 0 < v[2] < v[0])
    out["processes_with_several_awards"] = len(multiple)
    out["extra_award_rows"] = sum(awards[o][0] - 1 for o in multiple)
    out["awarded_in_processes_with_several_awards"] = awarded(multiple)
    estimated = [t[2] for t in tenders.values() if t[2] is not None]
    out["tender_with_estimated_amount"] = len(estimated)
    out["estimated_total"] = round(sum(estimated), 2)
    out["estimated_overcount_if_award_rows_joined_1_to_n"] = round(
        sum(tenders[o][2] * (awards[o][0] - 1) for o in multiple if o in tenders and tenders[o][2] is not None), 2
    )
    out["processes_with_both_amounts"] = len(both)
    out["processes_with_both_amounts_in_window"] = len(both & in_window)
    out["processes_with_several_awards_and_both_amounts"] = len(multiple & both)
    out["awarded_in_both"] = awarded(both)
    out["estimated_in_both"] = round(sum(tenders[o][2] for o in both), 2)
    out["estimated_in_window"] = round(
        sum(tenders[o][2] for o in in_window if o in tenders and tenders[o][2] is not None), 2
    )
    out["awarded_in_both_in_window"] = awarded(both & in_window)
    out["estimated_in_both_in_window"] = round(sum(tenders[o][2] for o in both & in_window), 2)
    out["processes_with_estimated_only"] = sum(
        1 for o, t in tenders.items() if t[2] is not None and o not in has_amount
    )
    out["processes_with_awarded_only"] = len(has_amount) - len(both)

    # Buyers
    roots = Counter(p[1] for p in processes.values())
    out["buyer_ids_distinct"] = len(buyer_ids)
    out["buyer_ids_without_root_pattern"] = sum(1 for b in buyer_ids if not ROOT_RE.match(b))
    out["processes_without_root"] = roots.get(None, 0)
    out["roots_distinct"] = sum(1 for r in roots if r)
    out["roots_distinct_in_window"] = len({processes[o][1] for o in in_window if processes[o][1]})
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("derivados", help="folder that holds the sercop-portal-csv-AAAA-* folders")
    parser.add_argument("--output", required=True, help="JSON file to create (never overwritten)")
    args = parser.parse_args(argv)
    csv.field_size_limit(2**30)
    result = measure(args.derivados)
    with open(args.output, "x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    sys.stdout.write(f"{len(result)} measurements written to {args.output}\n")


if __name__ == "__main__":
    main()
