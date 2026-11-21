"""Unit tests for scripts/inspect_csv_header.py using synthetic CSV files."""

import json
from pathlib import Path
import subprocess
import sys

from inspect_csv_header import (
    calculate_sha256,
    detect_encoding,
    inspect_csv_file,
    inspect_csv_path,
)
import pytest


@pytest.fixture
def synthetic_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "sample.csv"
    content = (
        "ocid,buyer_id,buyer_name,amount,notes\n"
        'ocds-k50b04-1,EC-RUC-01,Ministerio de Salud,150.50,"Simple note"\n'
        'ocds-k50b04-2,EC-RUC-02,Ministerio de Educacion,200.00,"Multiline\n'
        'note with comma, and quotes"\n'
        'ocds-k50b04-3,EC-RUC-03,Presidencia,350.00,"Third note"\n'
    )
    csv_file.write_text(content, encoding="utf-8", newline="")
    return csv_file


@pytest.fixture
def synthetic_bom_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "sample_bom.csv"
    content = "col1,col2\nval1,val2\n"
    csv_file.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
    return csv_file


@pytest.fixture
def synthetic_single_column_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "single_col.csv"
    content = "extension\next1\next2\next3\n"
    csv_file.write_text(content, encoding="utf-8", newline="")
    return csv_file


def test_inspect_csv_file_basic(synthetic_csv: Path):
    report = inspect_csv_file(synthetic_csv)
    assert report["file_name"] == "sample.csv"
    assert report["encoding"] == "utf-8"
    assert report["delimiter"] == ","
    assert report["quotechar"] == '"'
    assert report["column_count"] == 5
    assert report["columns"] == ["ocid", "buyer_id", "buyer_name", "amount", "notes"]
    # 3 data rows even though one row has a newline inside quotes
    assert report["row_count"] == 3
    # exactly one field holds a line break; physical lines (5) exceed records (3 + header)
    assert report["fields_with_line_break"] == 1
    assert report["file_size_bytes"] == synthetic_csv.stat().st_size
    assert report["sha256"] == calculate_sha256(synthetic_csv)


def test_no_cell_values_in_report(synthetic_csv: Path):
    report = inspect_csv_file(synthetic_csv)
    report_json = json.dumps(report)
    # Check that actual row values are never emitted
    assert "ocds-k50b04-1" not in report_json
    assert "Ministerio de Salud" not in report_json
    assert "150.50" not in report_json
    assert "Multiline" not in report_json


def test_detect_encoding_utf8_sig(synthetic_bom_csv: Path):
    assert detect_encoding(synthetic_bom_csv) == "utf-8-sig"


def test_single_column_csv(synthetic_single_column_csv: Path):
    report = inspect_csv_file(synthetic_single_column_csv)
    assert report["column_count"] == 1
    assert report["columns"] == ["extension"]
    assert report["row_count"] == 3
    assert report["fields_with_line_break"] == 0


def test_inspect_directory(tmp_path: Path, synthetic_csv: Path, synthetic_single_column_csv: Path):
    dir_report = inspect_csv_path(tmp_path)
    assert dir_report["total_csv_files"] == 2
    assert len(dir_report["files"]) == 2
    names = [f["file_name"] for f in dir_report["files"]]
    assert "sample.csv" in names
    assert "single_col.csv" in names


def test_cli_execution_with_output(synthetic_csv: Path, tmp_path: Path):
    output_path = tmp_path / "output_summary.json"
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "inspect_csv_header.py"

    cmd = [sys.executable, "-I", str(script_path), str(synthetic_csv), "--output", str(output_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert result.returncode == 0
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["file_name"] == "sample.csv"
    assert data["row_count"] == 3

    # Running again with the same output path must fail because output files must not be overwritten
    rerun = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert rerun.returncode != 0
    assert "Output file already exists" in rerun.stderr
