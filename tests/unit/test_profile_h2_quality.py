"""Unit tests for scripts/profile_h2_quality.py using synthetic CSV data."""

from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import sys

import profile_h2_quality
from profile_h2_quality import (
    compute_cross_year_metrics,
    detect_encoding,
    generate_summary_csv_rows,
    parse_iso_datetime,
    profile_candidate_date,
    profile_year,
)


def create_synthetic_year_csvs(
    folder: Path,
    year: int,
    releases_rows: list[dict[str, str]],
    tender_rows: list[dict[str, str]],
    awards_rows: list[dict[str, str]],
    contracts_rows: list[dict[str, str]],
) -> dict[str, Path]:
    """Helper to generate synthetic CSV tables for a specific year in tmp_path."""
    folder.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    # Releases
    rel_path = folder / f"releases_{year}.csv"
    with rel_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["ocid", "id", "initiationType", "buyer_id", "buyer_name", "language", "date", "tag"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(releases_rows)
    paths["releases"] = rel_path

    # Tender
    ten_path = folder / f"tender_{year}.csv"
    with ten_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "ocid",
            "release_id",
            "id",
            "title",
            "description",
            "status",
            "procuringEntity_id",
            "procuringEntity_name",
            "value_amount",
            "value_currency",
            "procurementMethod",
            "procurementMethodDetails",
            "mainProcurementCategory",
            "awardCriteria",
            "tenderPeriod_startDate",
            "tenderPeriod_endDate",
            "tenderPeriod_maxExtentDate",
            "tenderPeriod_durationInDays",
            "enquiryPeriod_startDate",
            "enquiryPeriod_endDate",
            "enquiryPeriod_maxExtentDate",
            "enquiryPeriod_durationInDays",
            "hasEnquiries",
            "eligibilityCriteria",
            "awardPeriod_startDate",
            "awardPeriod_endDate",
            "awardPeriod_maxExtentDate",
            "awardPeriod_durationInDays",
            "numberOfTenderers",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(tender_rows)
    paths["tender"] = ten_path

    # Awards
    awd_path = folder / f"awards_{year}.csv"
    with awd_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "ocid",
            "release_id",
            "id",
            "title",
            "description",
            "status",
            "date",
            "amount",
            "currency",
            "correctedValue_amount",
            "correctedValue_currency",
            "enteredValue_amount",
            "enteredValue_currency",
            "contractPeriod_startDate",
            "contractPeriod_endDate",
            "contractPeriod_maxExtentDate",
            "contractPeriod_durationInDays",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(awards_rows)
    paths["awards"] = awd_path

    # Contracts
    con_path = folder / f"contracts_{year}.csv"
    with con_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "ocid",
            "release_id",
            "id",
            "awardID",
            "title",
            "description",
            "status",
            "contractPeriod_startDate",
            "contractPeriod_endDate",
            "contractPeriod_maxExtentDate",
            "contractPeriod_durationInDays",
            "amount",
            "currency",
            "dateSigned",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(contracts_rows)
    paths["contracts"] = con_path

    return paths


def test_detect_encoding_multibyte_split_across_chunks(tmp_path: Path, monkeypatch):
    """A UTF-8 character straddling a chunk boundary is still UTF-8."""
    monkeypatch.setattr(profile_h2_quality, "CHUNK_SIZE", 5)
    text = "a,b\n\u00f3\u00f3\u00f3\u00f3,\u00f1\n"
    utf8_file = tmp_path / "utf8.csv"
    utf8_file.write_bytes(text.encode("utf-8"))
    assert detect_encoding(utf8_file) == "utf-8"

    cp1252_file = tmp_path / "cp1252.csv"
    cp1252_file.write_bytes(text.encode("cp1252"))
    assert detect_encoding(cp1252_file) == "windows-1252"


def test_parse_iso_datetime():
    dt, status = parse_iso_datetime("2021-05-10T14:30:00-05:00")
    assert status == "valid"
    assert dt is not None
    assert dt.year == 2021

    dt_empty, status_empty = parse_iso_datetime("   ")
    assert status_empty == "empty"
    assert dt_empty is None

    dt_bad, status_bad = parse_iso_datetime("fecha_invalida")
    assert status_bad == "unparseable"
    assert dt_bad is None


def test_profile_candidate_date():
    dates = [
        "2021-05-10T10:00:00Z",  # valid, same year
        "2022-01-15T10:00:00Z",  # after file year 2021
        "2014-12-31T23:59:59Z",  # before 2015
        "2027-01-01T00:00:00Z",  # future
        "",  # empty
        "invalida",  # unparseable
    ]
    res = profile_candidate_date(dates, file_year=2021)
    assert res["total_evaluated"] == 6
    assert res["populated"] == 5
    assert res["empty"] == 1
    assert res["unparseable"] == 1
    assert res["before_2015"] == 1
    assert res["future"] == 1
    assert res["after_file_year"] == 2  # 2022 and 2027
    assert res["valid_range"] == 2  # 2021 and 2022


def test_profile_synthetic_dataset(tmp_path: Path):
    """Test full year profiling with known synthetic anomalies and edge cases."""
    yr = 2021
    sub = tmp_path / f"sercop-portal-csv-{yr}-synthetic"

    # Known properties:
    # 5 releases:
    # - ocid_1: standard process, simple buyer_id, valid amounts
    # - ocid_2: duplicate ocid in releases (appears twice!), suffix buyer_id
    # - ocid_3: malformed buyer_id, empty tender amount, negative award amount
    # - ocid_4: future date, non-USD currency, tender with multiline description
    # - ocid_5: award amount != correctedValue_amount, 2 awards (multi-award)
    releases = [
        {
            "ocid": "ocid_1",
            "id": "rel_1",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000010001",
            "buyer_name": "MINISTERIO TEST A",
            "language": "es",
            "date": "2021-06-01T10:00:00Z",
            "tag": "compiled",
        },
        {
            "ocid": "ocid_2",
            "id": "rel_2a",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000020001-100",
            "buyer_name": "MINISTERIO TEST B",
            "language": "es",
            "date": "2021-07-01T10:00:00Z",
            "tag": "compiled",
        },
        {
            "ocid": "ocid_2",  # DUPLICATE OCID
            "id": "rel_2b",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000020001-100",
            "buyer_name": "MINISTERIO TEST B",
            "language": "es",
            "date": "2021-07-01T10:00:00Z",
            "tag": "compiled",
        },
        {
            "ocid": "ocid_3",
            "id": "rel_3",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-MALFORMADO-XYZ",  # MALFORMED BUYER_ID
            "buyer_name": "INSTITUTO TEST C",
            "language": "es",
            "date": "2021-08-01T10:00:00Z",
            "tag": "compiled",
        },
        {
            "ocid": "ocid_4",
            "id": "rel_4",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000040001",
            "buyer_name": "MINISTERIO TEST D",
            "language": "es",
            "date": "2027-02-01T10:00:00Z",  # FUTURE DATE
            "tag": "compiled",
        },
        {
            "ocid": "ocid_5",
            "id": "rel_5",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000050001",
            "buyer_name": "MINISTERIO TEST E",
            "language": "es",
            "date": "2022-03-01T10:00:00Z",  # OUT OF FILE YEAR (2022 in 2021)
            "tag": "compiled",
        },
    ]

    tender = [
        {
            "ocid": "ocid_1",
            "release_id": "rel_1",
            "id": "ten_1",
            "title": "Tender 1",
            "description": "Desc 1",
            "status": "complete",
            "procuringEntity_id": "EC-RUC-1768000010001",  # EXACT MATCH
            "procuringEntity_name": "MINISTERIO TEST A",
            "value_amount": "1000.00",
            "value_currency": "USD",
            "procurementMethod": "open",
            "procurementMethodDetails": "Subasta Inversa",
            "tenderPeriod_startDate": "2021-05-01T10:00:00Z",
        },
        {
            "ocid": "ocid_2",
            "release_id": "rel_2a",
            "id": "ten_2",
            "title": "Tender 2",
            "description": "Desc 2",
            "status": "complete",
            "procuringEntity_id": "EC-RUC-1768000020001-200",  # SAME ROOT DIFFERENT SUFFIX
            "procuringEntity_name": "MINISTERIO TEST B",
            "value_amount": "0.00",  # ZERO ESTIMATE
            "value_currency": "USD",
            "procurementMethod": "selective",
            "procurementMethodDetails": "Cotizacion",
            "tenderPeriod_startDate": "",
        },
        {
            "ocid": "ocid_3",
            "release_id": "rel_3",
            "id": "ten_3",
            "title": "Tender 3",
            "description": "Desc 3",
            "status": "active",
            "procuringEntity_id": "EC-RUC-9999999999999",  # DIFFERENT ROOT
            "procuringEntity_name": "INSTITUTO TEST C",
            "value_amount": "",  # EMPTY ESTIMATE
            "value_currency": "USD",
            "procurementMethod": "direct",
            "procurementMethodDetails": "Menor Cuantia",
            "tenderPeriod_startDate": "2021-07-15T10:00:00Z",
        },
        {
            "ocid": "ocid_4",
            "release_id": "rel_4",
            "id": "ten_4",
            "title": "Tender 4",
            "description": "Linea 1\nLinea 2 con salto de linea entre comillas",  # MULTILINE
            "status": "active",
            "procuringEntity_id": "EC-RUC-1768000040001",
            "procuringEntity_name": "MINISTERIO TEST D",
            "value_amount": "-50.00",  # NEGATIVE ESTIMATE
            "value_currency": "EUR",  # NON-USD CURRENCY
            "procurementMethod": "limited",
            "procurementMethodDetails": "Licitacion",
            "tenderPeriod_startDate": "2027-01-10T10:00:00Z",
        },
        {
            "ocid": "ocid_5",
            "release_id": "rel_5",
            "id": "ten_5",
            "title": "Tender 5",
            "description": "Desc 5",
            "status": "complete",
            "procuringEntity_id": "EC-RUC-1768000050001",
            "procuringEntity_name": "MINISTERIO TEST E",
            "value_amount": "5000.00",
            "value_currency": "USD",
            "procurementMethod": "open",
            "procurementMethodDetails": "Subasta Inversa",
            "tenderPeriod_startDate": "2021-12-01T10:00:00Z",
        },
    ]

    awards = [
        {
            "ocid": "ocid_1",
            "release_id": "rel_1",
            "id": "awd_1",
            "status": "active",
            "date": "2021-05-20T10:00:00Z",
            "amount": "950.00",
            "currency": "USD",
            "correctedValue_amount": "",
            "enteredValue_amount": "",
        },
        {
            "ocid": "ocid_3",
            "release_id": "rel_3",
            "id": "awd_3",
            "status": "active",
            "date": "2021-07-25T10:00:00Z",
            "amount": "-100.00",  # NEGATIVE AMOUNT
            "currency": "USD",
            "correctedValue_amount": "",
            "enteredValue_amount": "",
        },
        {
            "ocid": "ocid_4",
            "release_id": "rel_4",
            "id": "awd_4",
            "status": "cancelled",
            "date": "2027-01-20T10:00:00Z",  # FUTURE
            "amount": "0.00",  # ZERO AMOUNT
            "currency": "EUR",  # NON-USD
            "correctedValue_amount": "",
            "enteredValue_amount": "",
        },
        {
            "ocid": "ocid_5",
            "release_id": "rel_5",
            "id": "awd_5a",
            "status": "active",
            "date": "2021-12-10T10:00:00Z",
            "amount": "2000.00",
            "currency": "USD",
            "correctedValue_amount": "2500.00",  # AMOUNT != CORRECTEDVALUE
            "enteredValue_amount": "2000.00",
        },
        {
            "ocid": "ocid_5",  # MULTI-AWARD
            "release_id": "rel_5",
            "id": "awd_5b",
            "status": "active",
            "date": "2021-12-15T10:00:00Z",
            "amount": "2500.00",
            "currency": "USD",
            "correctedValue_amount": "2500.00",
            "enteredValue_amount": "2500.00",
        },
    ]

    contracts = [
        {
            "ocid": "ocid_1",
            "release_id": "rel_1",
            "id": "con_1",
            "awardID": "awd_1",
            "status": "active",
            "amount": "950.00",
            "currency": "USD",
            "dateSigned": "2021-05-30T10:00:00Z",
        },
        {
            "ocid": "ocid_5",
            "release_id": "rel_5",
            "id": "con_5",
            "awardID": "awd_5a",
            "status": "active",
            "amount": "4500.00",
            "currency": "USD",
            "dateSigned": "2022-01-10T10:00:00Z",  # OUT OF FILE YEAR
        },
    ]

    table_paths = create_synthetic_year_csvs(sub, yr, releases, tender, awards, contracts)

    res = profile_year(yr, table_paths)

    # 1. Control Totals:
    ct = res["control_totals"]
    assert ct["total_releases"] == 6
    assert ct["distinct_ocids"] == 5  # ocid_1, ocid_2, ocid_3, ocid_4, ocid_5
    assert ct["total_tender_rows"] == 5
    assert ct["total_awards_rows"] == 5
    assert ct["total_contracts_rows"] == 2
    # Awards sum: 950 - 100 + 0 + 2000 + 2500 = 5350.00
    assert ct["sum_awards_amount"] == 5350.00
    # Tender sum: 1000 + 0 - 50 + 5000 = 5950.00
    assert ct["sum_tender_value_amount"] == 5950.00

    # 2. Uniqueness:
    uniq = res["uniqueness"]
    assert uniq["releases_ocid_duplicates_within_year"] == 1  # ocid_2 appears twice
    assert uniq["multiplicity_of_awards"]["processes_with_more_than_1_award"] == 1  # ocid_5 has 2 awards
    assert uniq["multiplicity_of_awards"]["processes_with_1_award"] == 3  # ocid_1, ocid_3, ocid_4
    assert uniq["multiplicity_of_awards"]["processes_with_0_awards"] == 1  # ocid_2

    # 3. Completeness:
    comp = res["completeness"]
    assert comp["buyer_id_missing"] == 0
    assert comp["tender_value_amount"]["empty"] == 1  # ocid_3
    assert comp["tender_value_amount"]["zero"] == 1  # ocid_2
    assert comp["tender_value_amount"]["positive"] == 2
    assert comp["tender_value_amount"]["negative"] == 1
    assert comp["awards_amount"]["zero"] == 1
    assert comp["awards_amount"]["negative"] == 1
    assert comp["corrected_value_amount"]["populated"] == 2  # in ocid_5 awards

    # 4. Validity:
    val = res["validity"]
    assert val["currencies"]["tender_value_currency"]["EUR"] == 1
    assert val["currencies"]["awards_currency"]["EUR"] == 1
    assert val["dates"]["release_date"]["future"] == 1  # ocid_4 2027
    assert val["dates"]["release_date"]["after_file_year"] == 2  # 2027 and 2022

    # 5. Consistency:
    cons = res["consistency"]
    assert cons["buyer_id_formats"]["simple"] == 3
    assert cons["buyer_id_formats"]["suffix"] == 2  # ocid_2 (2 releases)
    assert cons["buyer_id_formats"]["malformed"] == 1  # ocid_3
    assert cons["amount_vs_corrected_and_entered_value"]["amount_vs_corrected_different"] == 1  # awd_5a (2000 != 2500)
    assert cons["buyer_id_vs_procuring_entity_id"]["exact_match"] == 3  # ocid_1, ocid_4, ocid_5
    assert cons["buyer_id_vs_procuring_entity_id"]["same_13digit_root_different_suffix"] == 1  # ocid_2
    assert cons["buyer_id_vs_procuring_entity_id"]["different_root"] == 1  # ocid_3


def test_cross_year_and_summary_csv(tmp_path: Path):
    """Test multi-year overlap and consolidated summary CSV generation."""
    # Create two years with 1 shared ocid
    y1_rel = [
        {
            "ocid": "shared_ocid",
            "id": "r1",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000010001",
            "buyer_name": "MIN A",
            "language": "es",
            "date": "2021-01-01T00:00:00Z",
            "tag": "t",
        },
        {
            "ocid": "only_y1",
            "id": "r2",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000010001",
            "buyer_name": "MIN A",
            "language": "es",
            "date": "2021-01-01T00:00:00Z",
            "tag": "t",
        },
    ]
    y2_rel = [
        {
            "ocid": "shared_ocid",
            "id": "r3",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000010001",
            "buyer_name": "MIN A",
            "language": "es",
            "date": "2022-01-01T00:00:00Z",
            "tag": "t",
        },
        {
            "ocid": "only_y2",
            "id": "r4",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000020001",
            "buyer_name": "MIN B",
            "language": "es",
            "date": "2022-01-01T00:00:00Z",
            "tag": "t",
        },
    ]

    p1 = create_synthetic_year_csvs(tmp_path / "sercop-portal-csv-2021-s1", 2021, y1_rel, [], [], [])
    p2 = create_synthetic_year_csvs(tmp_path / "sercop-portal-csv-2022-s2", 2022, y2_rel, [], [], [])

    res1 = profile_year(2021, p1)
    res2 = profile_year(2022, p2)

    cross = compute_cross_year_metrics([res1, res2])
    assert cross["total_distinct_global_ocids"] == 3  # shared_ocid, only_y1, only_y2
    assert cross["multi_year_ocids_count"] == 1  # shared_ocid
    assert cross["pairwise_overlaps"]["2021_2022"] == 1

    rows = generate_summary_csv_rows([res1, res2], cross)
    assert len(rows) > 0
    # Check that dimension, tabla, campo, metrica, anio, valor, unidad exist
    assert "dimension" in rows[0]
    assert "valor" in rows[0]
    assert any(r["anio"] == "total" for r in rows)


def test_cli_execution_and_no_overwrite(tmp_path: Path):
    """Test script execution via CLI, ensuring output contains no ocid and refuses overwrite."""
    derived_dir = tmp_path / "derived"
    output_dir = tmp_path / "output"

    y1_rel = [
        {
            "ocid": "secret_ocid_999",
            "id": "r1",
            "initiationType": "tender",
            "buyer_id": "EC-RUC-1768000010001",
            "buyer_name": "MINISTERIO PUBLICO",
            "language": "es",
            "date": "2021-01-01T00:00:00Z",
            "tag": "t",
        },
    ]
    create_synthetic_year_csvs(derived_dir / "sercop-portal-csv-2021-test", 2021, y1_rel, [], [], [])

    script_path = Path(__file__).resolve().parents[2] / "scripts" / "profile_h2_quality.py"

    cmd = [
        sys.executable,
        "-I",
        str(script_path),
        "--derived-dir",
        str(derived_dir),
        "--output-dir",
        str(output_dir),
        "--years",
        "2021",
    ]

    # First run: should succeed
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

    # Verify JSON output exists
    json_path = output_dir / "perfil-calidad-sercop-2021.json"
    assert json_path.exists()
    json_text = json_path.read_text(encoding="utf-8")
    assert "secret_ocid_999" not in json_text  # NO OCID in output!

    # Verify CSV outputs exist and have no ocid
    resumen_csv = output_dir / "perfil-calidad-sercop-resumen.csv"
    assert resumen_csv.exists()
    assert "secret_ocid_999" not in resumen_csv.read_text(encoding="utf-8")

    buyer_csv = output_dir / "perfil-calidad-sercop-por-comprador.csv"
    assert buyer_csv.exists()
    assert "secret_ocid_999" not in buyer_csv.read_text(encoding="utf-8")

    # Second run: should FAIL because outputs already exist (refusing overwrite)
    proc2 = subprocess.run(cmd, capture_output=True, text=True)
    assert proc2.returncode == 1
    assert "Refusing to overwrite existing output files" in proc2.stderr

    # Third run with new suffix: should SUCCEED
    cmd_v2 = [*cmd, "--output-suffix=-v2"]
    proc3 = subprocess.run(cmd_v2, capture_output=True, text=True)
    assert proc3.returncode == 0, f"STDOUT: {proc3.stdout}\nSTDERR: {proc3.stderr}"
    assert (output_dir / "perfil-calidad-sercop-2021-v2.json").exists()
    assert (output_dir / "perfil-calidad-sercop-resumen-v2.csv").exists()
    assert (output_dir / "perfil-calidad-sercop-por-comprador-v2.csv").exists()
