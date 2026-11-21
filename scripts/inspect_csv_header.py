"""Inspect CSV header and structure without reporting record values or cell contents.

Only Python's standard library is required. Describes encoding, delimiter,
columns, and row count. Never outputs cell values or data records.
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


CHUNK_SIZE = 1024 * 1024


def calculate_sha256(path: Path) -> str:
    """Calculate the SHA-256 digest of a file in streaming chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def detect_encoding(path: Path) -> str:
    """Detect file encoding using standard library heuristics.

    Checks for UTF-8-SIG (BOM), validates UTF-8 streams, and falls back to
    Latin-1 / Windows-1252 if UTF-8 decoding fails.
    """
    with path.open("rb") as stream:
        leading_bytes = stream.read(4)
        if leading_bytes.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        stream.seek(0)
        try:
            for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                chunk.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            return "windows-1252"


def detect_dialect_and_columns(path: Path, encoding: str) -> tuple[str, str, list[str]]:
    """Determine delimiter, quotechar, and column names without reading data rows."""
    with path.open("r", encoding=encoding, newline="", errors="replace") as stream:
        sample = stream.read(65536)
        if not sample:
            return ",", '"', []

        delimiter = ","
        quotechar = '"'
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample, delimiters=[",", ";", "\t", "|"])
            delimiter = dialect.delimiter
            quotechar = dialect.quotechar or '"'
        except csv.Error:
            first_line = sample.splitlines()[0] if sample.splitlines() else ""
            for cand in [",", ";", "\t", "|"]:
                if cand in first_line:
                    delimiter = cand
                    break

        stream.seek(0)
        reader = csv.reader(stream, delimiter=delimiter, quotechar=quotechar)
        try:
            header_row = next(reader)
        except StopIteration:
            header_row = []

    columns = [col.strip() for col in header_row]
    return delimiter, quotechar, columns


def count_data_rows(path: Path, encoding: str, delimiter: str, quotechar: str) -> int:
    """Count total data rows (excluding header) using csv.reader to handle multiline quotes."""
    with path.open("r", encoding=encoding, newline="", errors="replace") as stream:
        reader = csv.reader(stream, delimiter=delimiter, quotechar=quotechar)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def inspect_csv_file(path: Path) -> dict[str, Any]:
    """Inspect a single CSV file, returning metadata and structure without cell data."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    file_size = path.stat().st_size
    file_sha256 = calculate_sha256(path)
    encoding = detect_encoding(path)
    delimiter, quotechar, columns = detect_dialect_and_columns(path, encoding)
    row_count = count_data_rows(path, encoding, delimiter, quotechar)

    header_bytes = ",".join(columns).encode("utf-8")
    header_sha256 = hashlib.sha256(header_bytes).hexdigest().upper()

    return {
        "file_name": path.name,
        "file_size_bytes": file_size,
        "sha256": file_sha256,
        "encoding": encoding,
        "delimiter": delimiter,
        "quotechar": quotechar,
        "column_count": len(columns),
        "columns": columns,
        "row_count": row_count,
        "header_sha256": header_sha256,
    }


def inspect_csv_path(path: Path) -> dict[str, Any]:
    """Inspect a single CSV file or all CSV files in a directory."""
    script_path = Path(__file__).resolve()
    script_sha256 = calculate_sha256(script_path)
    now_utc = datetime.now(UTC).isoformat()

    base_report: dict[str, Any] = {
        "inspected_at_utc": now_utc,
        "script_sha256": script_sha256,
        "python_version": sys.version.split()[0],
    }

    if path.is_file():
        file_report = inspect_csv_file(path)
        base_report.update(file_report)
        return base_report

    if path.is_dir():
        csv_files = sorted(path.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in directory: {path}")
        inspected_files = [inspect_csv_file(f) for f in csv_files]
        base_report.update(
            {
                "directory_name": path.name,
                "total_csv_files": len(inspected_files),
                "files": inspected_files,
            }
        )
        return base_report

    raise FileNotFoundError(f"Path not found: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect CSV structure, encoding, and header without reading cell values."
    )
    parser.add_argument("csv_path", type=Path, help="Path to a CSV file or directory of CSV files.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Path to new output JSON summary (fails if file already exists).",
    )
    args = parser.parse_args()

    if args.output is not None and args.output.exists():
        parser.error(f"Output file already exists: {args.output}")

    try:
        report = inspect_csv_path(args.csv_path)
        text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as out_file:
                out_file.write(text)
        print(text, end="")
    except (OSError, ValueError, csv.Error) as err:
        print(f"Inspection error ({type(err).__name__}): inspection aborted.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
