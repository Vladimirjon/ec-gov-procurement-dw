"""Count which fields a local SERCOP annual ZIP actually fills, without reporting records.

Companion of inspect_sercop_zip.py (same folder): it reuses that script's streaming
reader and hash helper. Only Python's standard library is required. The output has
counts and the distinct values of package-level metadata (license, publisher,
publication policy) and of the procurement method; it has no record values,
identifiers or entity names. Unlike inspect_sercop_zip.py, an `awards` or
`contracts` value that is not a list of objects is counted as an anomaly and the
run continues, so one malformed release does not hide the rest of the year.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import io
import json
import math
from pathlib import Path
import platform
import sys
import uuid
import zipfile
import zlib


def load_inspector():
    path = Path(__file__).with_name("inspect_sercop_zip.py")
    spec = importlib.util.spec_from_file_location("inspect_sercop_zip", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSPECTOR = load_inspector()


def numeric_amount(value):
    if not isinstance(value, dict):
        return False
    amount = value.get("amount")
    return (
        isinstance(amount, (int, float))
        and not isinstance(amount, bool)
        and (not isinstance(amount, float) or math.isfinite(amount))
    )


def non_empty_text(value):
    return isinstance(value, str) and bool(value.strip())


def objects_in(parent, key, anomalies):
    value = parent.get(key, [])
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    anomalies[f"{key}_not_list_of_objects"] += 1
    return [value] if isinstance(value, dict) else []


def dict_get(parent, key):
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def profile(zip_path):
    started = datetime.now(timezone.utc).isoformat()
    source_hash = INSPECTOR.sha256(zip_path)
    counts = Counter()
    anomalies = Counter()
    licenses = Counter()
    publishers = Counter()
    policies = Counter()
    methods = Counter()
    method_details = Counter()
    currencies = Counter()
    release_years = Counter()

    with zipfile.ZipFile(zip_path) as archive:
        entries = [e for e in archive.infolist() if not e.is_dir() and e.filename.lower().endswith(".json")]
        if len(entries) != 1:
            raise ValueError("Expected exactly one JSON entry in the ZIP")
        entry = entries[0]
        with archive.open(entry) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as source:
            for package in INSPECTOR.iter_packages(source):
                counts["packages"] += 1
                licenses[str(package.get("license"))] += 1
                publishers[str(dict_get(package, "publisher").get("name"))] += 1
                policies[str(package.get("publicationPolicy"))] += 1
                for release in objects_in(package, "releases", anomalies):
                    counts["releases"] += 1
                    date = release.get("date")
                    if non_empty_text(date):
                        counts["release_date"] += 1
                        release_years[date[:4]] += 1
                    buyer = dict_get(release, "buyer")
                    counts["buyer_id"] += non_empty_text(buyer.get("id"))
                    counts["buyer_name"] += non_empty_text(buyer.get("name"))
                    tender = dict_get(release, "tender")
                    counts["tender"] += bool(tender)
                    tender_amount = numeric_amount(tender.get("value"))
                    counts["tender_value_amount_numeric"] += tender_amount
                    counts["tender_start_date"] += non_empty_text(dict_get(tender, "tenderPeriod").get("startDate"))
                    method = tender.get("procurementMethod")
                    counts["tender_procurement_method"] += non_empty_text(method)
                    if non_empty_text(method):
                        methods[method] += 1
                    detail = tender.get("procurementMethodDetails")
                    counts["tender_procurement_method_details"] += non_empty_text(detail)
                    if non_empty_text(detail):
                        method_details[detail] += 1
                    awards = objects_in(release, "awards", anomalies)
                    numeric_awards = [a for a in awards if numeric_amount(a.get("value"))]
                    counts["award_objects"] += len(awards)
                    counts["award_value_amount_numeric"] += len(numeric_awards)
                    counts["award_date"] += sum(non_empty_text(a.get("date")) for a in awards)
                    for award in numeric_awards:
                        currency = dict_get(award, "value").get("currency")
                        currencies[str(currency)] += 1
                    counts["releases_with_numeric_award"] += bool(numeric_awards)
                    counts["releases_with_tender_and_award_amount"] += bool(numeric_awards) and tender_amount
                    objects_in(release, "contracts", anomalies)
                if counts["packages"] % 20000 == 0:
                    print(f"Paquetes leídos: {counts['packages']}", file=sys.stderr, flush=True)

    if INSPECTOR.sha256(zip_path) != source_hash:
        raise ValueError("The ZIP hash changed during profiling")
    return {
        "report_schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "profiler_sha256": INSPECTOR.sha256(Path(__file__)),
        "source_file": zip_path.name,
        "source_bytes": zip_path.stat().st_size,
        "source_sha256": source_hash,
        "source_hash_unchanged": True,
        "json_entry": entry.filename,
        "counts": dict(counts),
        "anomalies": dict(anomalies),
        "package_license_values": dict(licenses),
        "package_publisher_values": dict(publishers),
        "package_publication_policy_values": dict(policies),
        "procurement_method_values": dict(methods.most_common()),
        "procurement_method_details_distinct": len(method_details),
        "procurement_method_details_top10": dict(method_details.most_common(10)),
        "award_currency_values": dict(currencies),
        "release_date_year_counts": dict(sorted(release_years.items())),
        "ocds_schema_validated": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Cuenta campos de un ZIP anual local de SERCOP; no consulta la API.")
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--output", type=Path, help="Resumen JSON nuevo; no sobrescribe archivos.")
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error("El archivo de salida ya existe; elige otro nombre.")
    try:
        text = json.dumps(profile(args.zip_path), indent=2, ensure_ascii=True) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as destination:
                destination.write(text)
        print(text, end="")
    except (
        OSError, ValueError, EOFError, NotImplementedError, zipfile.BadZipFile, zlib.error, RuntimeError, RecursionError
    ) as error:
        print(f"Perfilado detenido ({type(error).__name__}); no se generó un resumen completo.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
