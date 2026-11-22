import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("measure_h3_design", ROOT / "scripts" / "measure_h3_design.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CATALOG = "Catálogo electrónico - Mejor oferta en el convenio X-001, PRODUCTO, DETALLE"


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def build_year(base, year, releases, tenders, awards):
    folder = base / f"sercop-portal-csv-{year}-20990101-000000"
    folder.mkdir()
    write(folder / f"releases_{year}.csv", ["ocid", "buyer_id", "date"], releases)
    write(
        folder / f"tender_{year}.csv",
        ["ocid", "value_amount", "procurementMethod", "procurementMethodDetails"],
        tenders,
    )
    write(folder / f"awards_{year}.csv", ["ocid", "amount"], awards)


def test_procedure_of_collapses_catalogue_and_normalises_whitespace():
    assert module.procedure_of(CATALOG) == "Catálogo electrónico - Mejor oferta"
    assert module.procedure_of("Subasta  Inversa\nElectrónica") == "Subasta Inversa Electrónica"
    assert module.procedure_of("  ") == module.NO_DETAIL


def test_measure_counts_windows_amounts_and_multiple_awards(tmp_path):
    build_year(
        tmp_path,
        2090,
        [
            ["o1", "EC-RUC-1000000000001-5", "2021-01-31T23:30:00-05:00"],
            ["o2", "EC-RUC-1000000000001", "2025-12-15T10:00:00-05:00"],
            ["o3", "EC-RUC-2000000000001", "2026-01-02T10:00:00-05:00"],
            ["o4", "MALFORMED", "2022-06-01T10:00:00-05:00"],
            ["o5", "EC-RUC-3000000000001", "2023-03-01T10:00:00-05:00"],
        ],
        [
            ["o1", "100.00", "open", "Licitación"],
            ["o2", "", "selective", CATALOG],
            ["o3", "50.00", "direct", ""],
            ["o4", "10.00", "open", "Licitación"],
        ],
        [
            ["o1", "60.00"],
            ["o1", "50.00"],
            ["o2", "30.00"],
            ["o3", "40.00"],
            ["o4", ""],
        ],
    )
    result = module.measure(tmp_path)
    assert result["processes"] == 5
    assert result["processes_in_window"] == 4
    assert result["processes_after_window"] == 1
    assert result["months_with_processes_in_window"] == 4
    assert result["processes_without_tender_row"] == 1
    assert result["awarded_total"] == 180.0
    assert result["awarded_outside_window"] == 40.0
    assert result["processes_with_several_awards"] == 1
    assert result["extra_award_rows"] == 1
    assert result["extra_award_rows_in_window"] == 1
    assert result["award_rows_in_window"] == 4
    assert result["tender_rows_in_window"] == 3
    assert result["estimated_overcount_if_award_rows_joined_1_to_n"] == 100.0
    assert result["processes_with_awarded_amount"] == 3
    assert result["processes_with_award_rows_and_no_amount"] == 1
    assert result["processes_with_both_amounts"] == 2
    assert result["processes_with_estimated_only"] == 1
    assert result["processes_with_awarded_only"] == 1
    assert result["procedures_distinct"] == 3
    assert result["catalogue_details_distinct"] == 1
    assert result["roots_distinct"] == 3
    assert result["processes_without_root"] == 1
    assert result["buyer_ids_without_root_pattern"] == 1


def test_main_writes_json_and_never_overwrites(tmp_path):
    build_year(
        tmp_path,
        2090,
        [["o1", "EC-RUC-1000000000001", "2021-02-01T10:00:00-05:00"]],
        [["o1", "", "open", "Licitación"]],
        [["o1", "5.00"]],
    )
    output = tmp_path / "out.json"
    module.main([str(tmp_path), "--output", str(output)])
    assert json.loads(output.read_text(encoding="utf-8"))["processes"] == 1
    try:
        module.main([str(tmp_path), "--output", str(output)])
    except FileExistsError:
        return
    raise AssertionError("the output file was overwritten")


def test_measure_rejects_two_downloads_of_the_same_year(tmp_path):
    for sello in ("20990101-000000", "20990102-000000"):
        folder = tmp_path / f"sercop-portal-csv-2090-{sello}"
        folder.mkdir()
    try:
        module.measure(tmp_path)
    except ValueError as error:
        assert "2090" in str(error)
        return
    raise AssertionError("two folders for one year were accepted")


def test_measure_rejects_a_repeated_ocid(tmp_path):
    row = ["o1", "EC-RUC-1000000000001", "2021-02-01T10:00:00-05:00"]
    build_year(tmp_path, 2090, [row, row], [["o1", "", "open", "Licitación"]], [["o1", "5.00"]])
    try:
        module.measure(tmp_path)
    except ValueError as error:
        assert "ocid" in str(error)
        return
    raise AssertionError("a repeated ocid was accepted")
