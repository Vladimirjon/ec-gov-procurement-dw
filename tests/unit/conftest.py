"""Shared synthetic fixtures for the tests of the SERCOP reconnaissance scripts.

Every ZIP is built in tmp_path from invented values; nothing here comes from a
real download. Field names follow those observed in docs/sources/, values do not.
"""

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import zipfile

import pytest


# Tests write only inside tmp_path: do not leave bytecode caches beside the scripts.
sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Invented marker placed in record values (identifiers and names). A summary that
# contains it would be leaking record values.
SENTINEL = "SENTINEL-ZX81-NOT-A-REAL-VALUE"


def sample_packages():
    """Two release packages with three releases, built so counts are easy to check by hand.

    Release 1: two awards (one numeric amount, one string), one contract with an amount.
    Release 2: one award whose amount is not finite (1e999) and no contracts.
    Release 3: no ocid, no buyer, no tender, no awards key, two contracts (one with amount).
    """
    publisher = {"name": "Synthetic publisher"}
    common = {
        "uri": "https://example.invalid/package",
        "publishedDate": "2025-02-01T00:00:00Z",
        "license": "https://example.invalid/license",
        "publisher": publisher,
        "publicationPolicy": "https://example.invalid/policy",
    }
    release_1 = {
        "ocid": f"ocds-test-1-{SENTINEL}",
        "id": f"release-1-{SENTINEL}",
        "date": "2025-01-10T10:00:00Z",
        "buyer": {"id": f"buyer-{SENTINEL}", "name": f"Buyer {SENTINEL}"},
        "tender": {
            "value": {"amount": 100.5, "currency": "USD"},
            "tenderPeriod": {"startDate": "2025-01-05T00:00:00Z"},
            "procurementMethod": "open",
            "procurementMethodDetails": "Synthetic method A",
        },
        "awards": [
            {"id": f"award-1-{SENTINEL}", "date": "2025-01-20T00:00:00Z", "value": {"amount": 90, "currency": "USD"}},
            {"id": f"award-2-{SENTINEL}", "value": {"amount": "90", "currency": "USD"}},
        ],
        "contracts": [{"id": f"contract-1-{SENTINEL}", "value": {"amount": 80, "currency": "USD"}}],
    }
    release_2 = {
        "ocid": "ocds-test-2",
        "id": "release-2",
        "date": "2024-12-31T23:00:00Z",
        "buyer": {"id": "buyer-2", "name": "Buyer two"},
        "tender": {
            "value": {"amount": True, "currency": "USD"},
            "procurementMethod": "direct",
            "procurementMethodDetails": "Synthetic method B",
        },
        # Replaced by a bare 1e999 literal in the JSON text (see packages_text).
        "awards": [{"id": "award-3", "value": {"amount": "__HUGE__", "currency": "USD"}}],
        "contracts": [],
    }
    release_3 = {
        "id": "release-3",
        "contracts": [{"id": "contract-2", "value": {"amount": 5, "currency": "USD"}}, {"id": "contract-3"}],
    }
    return [
        {**common, "releases": [release_1, release_2]},
        {**common, "releases": [release_3]},
    ]


def packages_text(packages):
    """Serialize packages as the source would, turning the "__HUGE__" marker into 1e999."""
    return json.dumps(packages).replace('"__HUGE__"', "1e999")


@pytest.fixture
def sentinel():
    return SENTINEL


@pytest.fixture
def scripts_dir():
    return SCRIPTS_DIR


@pytest.fixture
def packages():
    return sample_packages()


@pytest.fixture
def make_zip(tmp_path):
    """Build a ZIP in tmp_path.

    `entries` maps entry names to raw bytes, to text (encoded with `encoding`) or to a
    list of packages (serialized as JSON).
    """

    def build(entries, name="sample.zip", encoding="utf-8"):
        path = tmp_path / name
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for entry_name, content in entries.items():
                if isinstance(content, bytes):
                    data = content
                else:
                    text = content if isinstance(content, str) else packages_text(content)
                    data = text.encode(encoding)
                archive.writestr(entry_name, data)
        return path

    return build


@pytest.fixture
def sample_zip(make_zip, packages):
    return make_zip({"releases.json": packages})


@pytest.fixture
def corrupt_deflate():
    """Overwrite the compressed bytes of the first ZIP entry with an invalid deflate stream.

    0xFF starts a final block of reserved type 3, which every zlib build rejects. The
    central directory stays intact, so the ZIP still opens and fails only when read.
    """

    def corrupt(path):
        with zipfile.ZipFile(path) as archive:
            info = archive.infolist()[0]
        data = bytearray(path.read_bytes())
        name_length, extra_length = struct.unpack("<HH", data[info.header_offset + 26 : info.header_offset + 30])
        start = info.header_offset + 30 + name_length + extra_length
        data[start : start + info.compress_size] = b"\xff" * info.compress_size
        path.write_bytes(bytes(data))
        return path

    return corrupt


@pytest.fixture
def run_script(tmp_path):
    """Run a script as a separate process, the way the team runs it, from tmp_path.

    -I isolates the child from user site-packages and PYTHON* variables, -B keeps it
    from writing bytecode beside the scripts and -X utf8 makes its Spanish messages
    decode the same way on Windows and Linux.
    """

    def run(script_name, *args):
        command = [sys.executable, "-I", "-B", "-X", "utf8", str(SCRIPTS_DIR / script_name), *map(str, args)]
        return subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", cwd=tmp_path, timeout=60, check=False
        )

    return run


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


@pytest.fixture
def file_sha256():
    return sha256_of
