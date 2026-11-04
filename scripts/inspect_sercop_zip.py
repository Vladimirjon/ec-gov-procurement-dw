"""Inspect a local SERCOP ZIP without extracting it or reporting record values.

Only Python's standard library is required. The JSON root must be an array of
release packages, as observed in the January 2025 download. This is a source
inspection helper, not an OCDS schema validator or a warehouse extractor.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys
import time
import uuid
import zipfile
import zlib


CHUNK_CHARS = 1024 * 1024
MAX_BUFFER_CHARS = 64 * CHUNK_CHARS


def sha256(path):
    with path.open("rb") as source:
        digest = hashlib.sha256()
        for chunk in iter(lambda: source.read(CHUNK_CHARS), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def reject_non_json_number(_value):
    raise ValueError("Non-JSON numeric constant encountered")


def iter_packages(source):
    """Decode one array element at a time, retaining only a chunk and one item.

    raw_decode returns both a decoded value and the next character position:
    https://docs.python.org/3.13/library/json.html#json.JSONDecoder.raw_decode
    Identifier sets held by the caller grow with the number of processes.
    """
    decoder = json.JSONDecoder(parse_constant=reject_non_json_number)
    buffer = ""
    position = 0
    item_number = 0

    def refill():
        nonlocal buffer, position
        chunk = source.read(CHUNK_CHARS)
        buffer = buffer[position:] + chunk
        position = 0
        if len(buffer) > MAX_BUFFER_CHARS:
            raise ValueError("A package exceeds the 64 Mi-character buffer limit")
        return bool(chunk)

    def next_character():
        nonlocal position
        while True:
            while position < len(buffer) and buffer[position] in " \t\r\n":
                position += 1
            if position < len(buffer):
                return buffer[position]
            if not refill():
                return ""

    if next_character() != "[":
        raise ValueError("Expected a top-level JSON array")
    position += 1
    if next_character() == "]":
        position += 1
    else:
        while True:
            if next_character() != "{":
                raise ValueError(f"Expected package object at index {item_number}")
            while True:
                try:
                    package, end = decoder.raw_decode(buffer, position)
                    break
                except json.JSONDecodeError:
                    if not refill():
                        raise ValueError(
                            f"Invalid or truncated JSON at package index {item_number}"
                        ) from None
            position = end
            yield package
            item_number += 1
            delimiter = next_character()
            if delimiter == "]":
                position += 1
                break
            if delimiter != ",":
                raise ValueError(f"Missing separator after package index {item_number - 1}")
            position += 1
    if next_character():
        raise ValueError("Unexpected content after the JSON array")


def child_array(parent, key):
    value = parent.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Expected an array of objects in {key}")
    return value


def has_numeric_amount(value):
    if not isinstance(value, dict):
        return False
    amount = value.get("amount")
    return (
        isinstance(amount, (int, float))
        and not isinstance(amount, bool)
        and (not isinstance(amount, float) or math.isfinite(amount))
    )


def inspect_zip(zip_path, expected_processes):
    started = datetime.now(timezone.utc).isoformat()
    timer = time.perf_counter()
    source_hash = sha256(zip_path)
    counts = Counter()
    package_fields = Counter()
    release_fields = Counter()
    award_distribution = Counter()
    contract_distribution = Counter()
    ocids = set()
    release_keys = set()

    # ZipFile.open reads an entry without writing extracted files:
    # https://docs.python.org/3.13/library/zipfile.html#zipfile.ZipFile.open
    with zipfile.ZipFile(zip_path) as archive:
        json_entries = [
            entry for entry in archive.infolist()
            if not entry.is_dir() and entry.filename.lower().endswith(".json")
        ]
        if len(json_entries) != 1:
            raise ValueError("Expected exactly one JSON entry in the ZIP")
        entry = json_entries[0]
        with archive.open(entry) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as source:
            for package in iter_packages(source):
                counts["packages"] += 1
                package_fields.update(package.keys())
                for release in child_array(package, "releases"):
                    counts["releases"] += 1
                    release_fields.update(release.keys())
                    ocid = release.get("ocid")
                    if isinstance(ocid, str) and ocid.strip():
                        ocids.add(ocid)
                    else:
                        counts["releases_without_nonempty_ocid"] += 1
                    release_id = release.get("id")
                    if isinstance(ocid, str) and ocid.strip() and isinstance(release_id, str) and release_id.strip():
                        release_keys.add((ocid, release_id))
                    awards = child_array(release, "awards")
                    contracts = child_array(release, "contracts")
                    award_distribution[len(awards)] += 1
                    contract_distribution[len(contracts)] += 1
                    counts["award_objects"] += len(awards)
                    counts["contract_objects"] += len(contracts)
                    counts["awards_with_numeric_amount"] += sum(
                        has_numeric_amount(award.get("value")) for award in awards
                    )
                    counts["contracts_with_numeric_amount"] += sum(
                        has_numeric_amount(contract.get("value")) for contract in contracts
                    )
                if counts["packages"] % 10000 == 0:
                    print(f"Paquetes leídos: {counts['packages']}", file=sys.stderr, flush=True)

    if sha256(zip_path) != source_hash:
        raise ValueError("The ZIP hash changed during inspection")
    return {
        "report_schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.perf_counter() - timer, 3),
        "python_version": platform.python_version(),
        "inspector_sha256": sha256(Path(__file__)),
        "source_file": zip_path.name,
        "source_bytes": zip_path.stat().st_size,
        "source_sha256": source_hash,
        "source_hash_unchanged": True,
        "json_entry": entry.filename,
        "json_uncompressed_bytes": entry.file_size,
        "packages": counts["packages"],
        "releases": counts["releases"],
        "distinct_ocids": len(ocids),
        "releases_without_nonempty_ocid": counts["releases_without_nonempty_ocid"],
        "distinct_ocid_release_id_pairs": len(release_keys),
        "award_objects": counts["award_objects"],
        "contract_objects": counts["contract_objects"],
        "awards_with_numeric_amount": counts["awards_with_numeric_amount"],
        "contracts_with_numeric_amount": counts["contracts_with_numeric_amount"],
        "releases_with_multiple_awards": sum(n for size, n in award_distribution.items() if size > 1),
        "releases_with_multiple_contracts": sum(n for size, n in contract_distribution.items() if size > 1),
        "award_count_distribution": dict(sorted(award_distribution.items())),
        "contract_count_distribution": dict(sorted(contract_distribution.items())),
        "package_field_presence": dict(sorted(package_fields.items())),
        "release_field_presence": dict(sorted(release_fields.items())),
        "expected_processes": expected_processes,
        "distinct_ocids_match_expected": (
            len(ocids) == expected_processes if expected_processes is not None else None
        ),
        "ocds_schema_validated": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspecciona un ZIP local; no consulta la API.")
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--expected-processes", type=int)
    parser.add_argument("--output", type=Path, help="Resumen JSON nuevo; no sobrescribe archivos.")
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error("El archivo de salida ya existe; elige otro nombre.")
    if args.expected_processes is not None and args.expected_processes < 0:
        parser.error("El conteo esperado no puede ser negativo.")
    try:
        report = inspect_zip(args.zip_path, args.expected_processes)
        text = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as destination:
                destination.write(text)
        print(text, end="")
    except (
        OSError, ValueError, EOFError, NotImplementedError, zipfile.BadZipFile, zlib.error, RuntimeError, RecursionError
    ) as error:
        # Do not print exception messages that might contain source record values.
        print(f"Inspección detenida ({type(error).__name__}); no se generó un resumen completo.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
