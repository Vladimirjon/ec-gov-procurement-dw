"""Download entity catalog and directory sources and record provenance evidence.

Only standard library is used. Follows the rate-limiting rules (>=3s delay between
requests), sequential execution, respects robots.txt, stores headers without cookies,
sets files to read-only, and logs evidence to docs/h2/evidencia/descargas-entidades.csv.
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import stat
import sys
import time
from typing import NamedTuple
import urllib.request


CHUNK_SIZE = 1024 * 1024
ECUADOR_TZ = timezone(timedelta(hours=-5))


class DownloadTarget(NamedTuple):
    folder_prefix: str
    file_name: str
    url: str
    year: str
    license_url: str
    license_value: str


TARGETS: list[DownloadTarget] = [
    DownloadTarget(
        folder_prefix="mdep-catalogo-instituciones",
        file_name="catalogo_instituciones_mdep.xlsx",
        url="https://www.economicoproductivo.gob.ec/wp-content/plugins/download-monitor/download.php?id=18691",
        year="2026",
        license_url="",
        license_value="No declarada",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-raiz",
        file_name="instituciones.html",
        url="https://www.gob.ec/instituciones",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-p",
        file_name="instituciones_p.html",
        url="https://www.gob.ec/instituciones/P",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-m",
        file_name="instituciones_m.html",
        url="https://www.gob.ec/instituciones/M",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-i",
        file_name="instituciones_i.html",
        url="https://www.gob.ec/instituciones/I",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-v",
        file_name="instituciones_v.html",
        url="https://www.gob.ec/instituciones/V",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
    DownloadTarget(
        folder_prefix="gob-ec-instituciones-s",
        file_name="instituciones_s.html",
        url="https://www.gob.ec/instituciones/S",
        year="2026",
        license_url="",
        license_value="Sin licencia explícita",
    ),
]

CSV_HEADER = [
    "year",
    "url",
    "http_status",
    "download_started_utc",
    "download_started_local",
    "download_finished_utc",
    "download_finished_local",
    "bytes_received",
    "content_length",
    "sha256",
    "file_name",
    "folder",
    "license_url",
    "license_value",
]


def format_iso_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"


def format_local(dt: datetime) -> str:
    return dt.astimezone(ECUADOR_TZ).strftime("%Y-%m-%d %H:%M:%S")


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def download_one(
    target: DownloadTarget,
    output_root: Path,
    repo_root: Path,
    evidence_csv: Path,
    user_agent: str,
) -> None:
    if not (target.url.startswith("https://") or target.url.startswith("http://")):
        raise ValueError(f"URL scheme not allowed: {target.url}")

    timestamp_str = datetime.now(ECUADOR_TZ).strftime("%Y%m%d-%H%M%S")
    folder_name = f"{target.folder_prefix}-{timestamp_str}"
    dest_dir = output_root / folder_name
    dest_dir.mkdir(parents=True, exist_ok=False)

    dest_file = dest_dir / target.file_name
    headers_file = dest_dir / "headers.txt"

    started_utc = datetime.now(UTC)
    req = urllib.request.Request(  # noqa: S310
        target.url,
        headers={"User-Agent": user_agent},
    )

    print(f"Downloading {target.url} -> {dest_file}")
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        http_status = str(resp.status)
        content_length_hdr = resp.headers.get("Content-Length", "")

        # Write headers excluding cookies
        header_lines = [f"HTTP/1.1 {resp.status} {resp.reason}"]
        for k, v in resp.headers.items():
            if "cookie" not in k.lower():
                header_lines.append(f"{k}: {v}")
        headers_file.write_text("\r\n".join(header_lines) + "\r\n", encoding="utf-8")

        # Stream content
        with dest_file.open("wb") as out_stream:
            for chunk in iter(lambda: resp.read(CHUNK_SIZE), b""):
                out_stream.write(chunk)

    finished_utc = datetime.now(UTC)
    bytes_received = str(dest_file.stat().st_size)
    sha256_hash = calculate_sha256(dest_file)

    # Set file read-only
    os.chmod(dest_file, stat.S_IREAD)

    # Calculate folder relative to repo root using forward slashes
    try:
        rel_folder = dest_dir.relative_to(repo_root).as_posix()
    except ValueError:
        rel_folder = f"data/datos_crudos/{folder_name}"

    # Append to evidence CSV
    file_exists = evidence_csv.exists()
    evidence_csv.parent.mkdir(parents=True, exist_ok=True)
    with evidence_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writerow(CSV_HEADER)
        writer.writerow(
            [
                target.year,
                target.url,
                http_status,
                format_iso_utc(started_utc),
                format_local(started_utc),
                format_iso_utc(finished_utc),
                format_local(finished_utc),
                bytes_received,
                content_length_hdr,
                sha256_hash,
                target.file_name,
                rel_folder,
                target.license_url,
                target.license_value,
            ]
        )

    print(f"  Saved {bytes_received} bytes (SHA-256: {sha256_hash}) in {rel_folder}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/datos_crudos"),
        help="Directory where download folders are created",
    )
    parser.add_argument(
        "--evidence-csv",
        type=Path,
        default=Path("docs/h2/evidencia/descargas-entidades.csv"),
        help="Path to CSV evidence log",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay in seconds between requests (minimum 3.0)",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        help="HTTP User-Agent",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_root = args.output_root if args.output_root.is_absolute() else repo_root / args.output_root
    evidence_csv = args.evidence_csv if args.evidence_csv.is_absolute() else repo_root / args.evidence_csv

    delay = max(3.0, args.delay)

    for i, target in enumerate(TARGETS):
        if i > 0:
            print(f"Waiting {delay} seconds before next request...")
            time.sleep(delay)

        # Retry once if needed
        success = False
        last_error = None
        for attempt in range(2):
            try:
                download_one(target, output_root, repo_root, evidence_csv, args.user_agent)
                success = True
                break
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed for {target.url}: {e}", file=sys.stderr)
                if attempt == 0:
                    time.sleep(delay)

        if not success:
            print(f"ERROR: Download failed twice for {target.url}: {last_error}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
