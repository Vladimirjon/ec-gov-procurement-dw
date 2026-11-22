"""Compare the tender table of the SERCOP CSV download against the JSON download.

Accuracy check for H2 (issue #64, Licitaciones_SERCOP x Exactitud): for each
year, the portal CSV (`tender_AAAA.csv`) and the OCDS JSON (`releases_AAAA.zip`)
are two representations of the same data, so the rows of `tender`, the estimated
amount and the procurement method must agree. The script streams both files and
writes only aggregates (counts, sums, a checksum): no records.

Usage (paths are arguments; the downloads are untrusted data, run with -I):
    python -I scripts/measure_tender_accuracy.py --output OUT.json \
        2021=JSON_ZIP,CSV 2022=JSON_ZIP,CSV ...

The output is never overwritten.
"""

from __future__ import annotations

import argparse
import codecs
from concurrent.futures import ProcessPoolExecutor
import csv
from decimal import Decimal
import io
import json
from pathlib import Path
import sys
import zipfile


CHUNK = 1 << 20
MARKER = '"releases": ['


def iter_releases(stream: io.BufferedIOBase):
    """Yield every release of every package of a JSON file, without loading it."""
    decoder = json.JSONDecoder(parse_float=Decimal)
    text_decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    pos = 0
    in_array = False
    eof = False
    while True:
        if in_array:
            while pos < len(buffer) and buffer[pos] in " \r\n\t,":
                pos += 1
            if pos < len(buffer) and buffer[pos] == "]":
                pos += 1
                in_array = False
                continue
            if pos < len(buffer):
                try:
                    obj, end = decoder.raw_decode(buffer, pos)
                except json.JSONDecodeError:
                    if eof:
                        raise
                else:
                    pos = end
                    yield obj
                    continue
        else:
            found = buffer.find(MARKER, pos)
            if found >= 0:
                pos = found + len(MARKER)
                in_array = True
                continue
            if eof:
                return
            pos = max(pos, len(buffer) - len(MARKER))
        if eof:
            return
        data = stream.read(CHUNK)
        if not data:
            eof = True
            buffer = buffer[pos:] + text_decoder.decode(b"", final=True)
            pos = 0
            continue
        buffer = buffer[pos:] + text_decoder.decode(data)
        pos = 0


def normalize_text(value: str | None) -> str:
    """Collapse any whitespace run (including line breaks) to one space."""
    return " ".join((value or "").split())


def load_csv(csv_path: str) -> dict[tuple[str, str], tuple[str, str, str]]:
    records: dict[tuple[str, str], tuple[str, str, str]] = {}
    csv.field_size_limit(1 << 27)
    with open(csv_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            records[(row["ocid"], row["release_id"])] = (
                row["value_amount"].strip(),
                row["procurementMethod"],
                row["procurementMethodDetails"],
            )
    return records


def measure_year(job: tuple[str, str, str]) -> tuple[str, dict]:
    year, zip_path, csv_path = job
    csv_records = load_csv(csv_path)
    stats = {
        "csv_tender_rows": len(csv_records),
        "json_releases": 0,
        "json_tender_rows": 0,
        "tender_rows_only_in_json": 0,
        "tender_rows_only_in_csv": 0,
        "amount_present_in_both": 0,
        "amount_identical": 0,
        "amount_differs_up_to_0_01": 0,
        "amount_differs_more_than_0_01": 0,
        "amount_only_in_json": 0,
        "amount_only_in_csv": 0,
        "json_amount_zero_csv_empty": 0,
        "procurement_method_differs": 0,
        "method_details_differs": 0,
        "method_details_differs_only_in_whitespace": 0,
    }
    sum_json = Decimal("0")
    sum_csv = Decimal("0")
    seen: set[tuple[str, str]] = set()
    with zipfile.ZipFile(zip_path) as archive:
        for name in (n for n in archive.namelist() if n.endswith(".json")):
            with archive.open(name) as stream:
                for release in iter_releases(stream):
                    stats["json_releases"] += 1
                    tender = release.get("tender")
                    if not isinstance(tender, dict):
                        continue
                    stats["json_tender_rows"] += 1
                    key = (release.get("ocid") or "", release.get("id") or "")
                    seen.add(key)
                    row = csv_records.get(key)
                    if row is None:
                        stats["tender_rows_only_in_json"] += 1
                        continue
                    csv_amount, csv_method, csv_details = row
                    value = tender.get("value")
                    raw = value.get("amount") if isinstance(value, dict) else None
                    json_amount = None if raw is None else Decimal(raw)
                    if json_amount is not None:
                        sum_json += json_amount
                    if csv_amount:
                        sum_csv += Decimal(csv_amount)
                    if json_amount is not None and csv_amount:
                        stats["amount_present_in_both"] += 1
                        gap = abs(json_amount - Decimal(csv_amount))
                        if gap == 0:
                            stats["amount_identical"] += 1
                        elif gap <= Decimal("0.01"):
                            stats["amount_differs_up_to_0_01"] += 1
                        else:
                            stats["amount_differs_more_than_0_01"] += 1
                    elif json_amount is not None:
                        stats["amount_only_in_json"] += 1
                        if json_amount == 0:
                            stats["json_amount_zero_csv_empty"] += 1
                    elif csv_amount:
                        stats["amount_only_in_csv"] += 1
                    if (tender.get("procurementMethod") or "") != csv_method:
                        stats["procurement_method_differs"] += 1
                    json_details = tender.get("procurementMethodDetails") or ""
                    if json_details != csv_details:
                        stats["method_details_differs"] += 1
                        if normalize_text(json_details) == normalize_text(csv_details):
                            stats["method_details_differs_only_in_whitespace"] += 1
    stats["tender_rows_only_in_csv"] = len(csv_records.keys() - seen)
    stats["sum_value_amount_json"] = str(sum_json)
    stats["sum_value_amount_csv"] = str(sum_csv)
    stats["sum_difference_json_minus_csv"] = str(sum_json - sum_csv)
    return year, stats


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("jobs", nargs="+", help="AAAA=ZIP_JSON,CSV_TENDER")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error(f"{args.output} already exists; use a new name")
    jobs = []
    for item in args.jobs:
        year, _, paths = item.partition("=")
        zip_path, _, csv_path = paths.partition(",")
        if not (year and zip_path and csv_path):
            parser.error(f"invalid job: {item}")
        jobs.append((year, zip_path, csv_path))
    with ProcessPoolExecutor(max_workers=min(len(jobs), 5)) as pool:
        results = dict(pool.map(measure_year, jobs))
    document = {
        "description": "tender table: SERCOP portal CSV versus OCDS JSON, aggregates only",
        "years": dict(sorted(results.items())),
    }
    with open(args.output, "x", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(document["years"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
