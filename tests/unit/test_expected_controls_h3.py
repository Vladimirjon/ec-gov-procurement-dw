import csv
from decimal import Decimal
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "expected_controls_h3", Path(__file__).resolve().parents[2] / "scripts" / "expected_controls_h3.py"
)
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sources(base, years=(2021,)):
    for year in years:
        folder = base / f"sercop-portal-csv-{year}-20990101-000000"
        folder.mkdir()
        write_csv(
            folder / f"releases_{year}.csv",
            ["ocid", "buyer_id", "buyer_name", "date"],
            [
                {
                    "ocid": f"{year}-{i}",
                    "buyer_id": buyer,
                    "buyer_name": "Entidad sintética",
                    "date": "2022-01-31T23:30:00-05:00",
                }
                for i, buyer in enumerate(("EC-RUC-0100000000001-x", "MALFORMADO", "EC-RUC-0100000000001"))
            ],
        )
        write_csv(
            folder / f"tender_{year}.csv",
            ["ocid", "value_amount", "value_currency", "procurementMethodDetails"],
            [
                {
                    "ocid": f"{year}-{i}",
                    "value_amount": amount,
                    "value_currency": currency,
                    "procurementMethodDetails": "Subasta\n  Inversa\u00a0Electrónica",
                }
                for i, (amount, currency) in enumerate((("100.10", "USD"), ("", ""), ("0", "USD")))
            ],
        )
        write_csv(
            folder / f"awards_{year}.csv",
            ["ocid", "id", "amount", "currency", "correctedValue_amount", "enteredValue_amount"],
            [
                {
                    "ocid": f"{year}-{i}",
                    "id": str(j),
                    "amount": amount,
                    "currency": currency,
                    "correctedValue_amount": "",
                    "enteredValue_amount": "",
                }
                for i, j, amount, currency in (
                    (0, 0, "0.10", "USD"),
                    (0, 1, "0.20", "USD"),
                    (1, 0, "", ""),
                    (1, 1, "", ""),
                    (2, 0, "0", "USD"),
                )
            ],
        )


def step(rows, table, name, year="TOTAL"):
    return next(r for r in rows if r["tabla"] == table and r["anio_archivo"] == year and r["paso"] == name)


def metric(rows, table, name, year="TOTAL"):
    return next(r["valor"] for r in rows if r["tabla"] == table and r["anio_archivo"] == year and r["metrica"] == name)


def check_grouping_null_zero_exact_sum_and_quoted_newline(tmp_path):
    sources(tmp_path)
    rows = controls.measure(tmp_path, (2021,))
    grouped = step(rows, "awards", controls.STEPS["awards"][-1])
    assert (grouped["filas_antes"], grouped["filas_despues"]) == (5, 3)
    assert Decimal(grouped["suma_antes_usd"]) == Decimal("0.30")
    assert grouped["suma_antes_usd"] == grouped["suma_despues_usd"]
    assert metric(rows, "awards", "procesos_varias_adjudicaciones") == 2
    assert metric(rows, "awards", "filas_adicionales") == 2
    assert metric(rows, "awards", "grupos_todos_null") == 1
    assert metric(rows, "awards", "procesos_ambos_importes") == 2  # zero is present
    assert metric(rows, "tender", "importes_vacios") == 1
    assert metric(rows, "tender", "importes_cero") == 1
    assert step(rows, "tender", controls.STEPS["tender"][-1])["filas_despues"] == 3
    assert metric(rows, "tender", "detalle_normalizado") == 3
    assert controls.normalise("Subasta\n  Inversa\u00a0Electrónica") == "Subasta Inversa Electrónica"
    assert metric(rows, "releases", "buyer_id_malformado") == 1
    assert metric(rows, "releases", "fecha_otro_anio") == 3
    for field in ("ocid", "buyer_id", "buyer_name", "date"):
        assert metric(rows, "releases", f"vacios_{field}") == 0


def check_all_null_sum_stays_empty(tmp_path):
    sources(tmp_path)
    path = next(tmp_path.glob("*/awards_2021.csv"))
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    for row in rows:
        row["amount"] = row["currency"] = ""
    write_csv(path, fields, rows)
    grouped = step(controls.measure(tmp_path, (2021,)), "awards", controls.STEPS["awards"][-1])
    assert grouped["suma_antes_usd"] == grouped["suma_despues_usd"] == ""


def check_currency_and_negative_exclusions_are_disjoint(tmp_path):
    sources(tmp_path)
    path = next(tmp_path.glob("*/tender_2021.csv"))
    write_csv(
        path,
        ["ocid", "value_amount", "value_currency", "procurementMethodDetails"],
        [
            {"ocid": "2021-0", "value_amount": "-2", "value_currency": "EUR", "procurementMethodDetails": ""},
            {"ocid": "2021-1", "value_amount": "-3", "value_currency": "USD", "procurementMethodDetails": ""},
            {"ocid": "2021-2", "value_amount": "", "value_currency": "", "procurementMethodDetails": ""},
        ],
    )
    rows = controls.measure(tmp_path, (2021,))
    assert metric(rows, "tender", "moneda_excluidas") == 1
    assert metric(rows, "tender", "negativos_excluidos") == 1
    assert step(rows, "tender", "Moneda solo USD verificada")["filas_despues"] == 2
    assert step(rows, "tender", "Importes negativos excluidos")["filas_despues"] == 1


def check_duplicate_keys_fail_without_silent_deletion(tmp_path, table):
    sources(tmp_path)
    path = next(tmp_path.glob(f"*/{table}_2021.csv"))
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    write_csv(path, fields, [*rows, rows[0]])
    with unittest.TestCase().assertRaisesRegex(ValueError, "duplicate"):
        controls.measure(tmp_path, (2021,))


def check_cli_five_years_refuses_overwrite(tmp_path):
    sources(tmp_path, controls.YEARS)
    output = tmp_path / "controls.csv"
    command = [sys.executable, "-I", str(controls.__file__), str(tmp_path), "--output", str(output)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    first = output.read_bytes()
    assert b"\r\n" not in first
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert (
        next(
            r
            for r in rows
            if r["tabla"] == "releases" and r["anio_archivo"] == "TOTAL" and r["paso"] == "Cinco años anexados"
        )["filas_despues"]
        == "15"
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert output.read_bytes() == first


def check_ambiguous_download_and_bad_root_are_rejected(tmp_path):
    sources(tmp_path)
    (tmp_path / "sercop-portal-csv-2021-another").mkdir()
    with unittest.TestCase().assertRaisesRegex(ValueError, "exactly one"):
        controls.measure(tmp_path, (2021,))
    assert controls.root_of("EC-RUC-0100000000001-5") == "0100000000001"
    for value in ("EC-RUC-123", "EC-RUC-0100000000001-", "EC-RUC-\uff10100000000001"):
        assert controls.root_of(value) == "NO_IDENTIFICADO"


class ExpectedControlsTests(unittest.TestCase):
    """Also runnable with python -I when the development environment cannot be installed."""

    def run_check(self, check, *args):
        with tempfile.TemporaryDirectory() as folder:
            check(Path(folder), *args)

    def test_grouping_null_zero_and_newline(self):
        self.run_check(check_grouping_null_zero_exact_sum_and_quoted_newline)

    def test_all_null(self):
        self.run_check(check_all_null_sum_stays_empty)

    def test_exclusions(self):
        self.run_check(check_currency_and_negative_exclusions_are_disjoint)

    def test_duplicate_releases(self):
        self.run_check(check_duplicate_keys_fail_without_silent_deletion, "releases")

    def test_duplicate_tender(self):
        self.run_check(check_duplicate_keys_fail_without_silent_deletion, "tender")

    def test_duplicate_awards(self):
        self.run_check(check_duplicate_keys_fail_without_silent_deletion, "awards")

    def test_cli(self):
        self.run_check(check_cli_five_years_refuses_overwrite)

    def test_folder_and_root(self):
        self.run_check(check_ambiguous_download_and_bad_root_are_rejected)


if __name__ == "__main__":
    unittest.main()
