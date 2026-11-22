import csv
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "expected_model_h3.py"
spec = importlib.util.spec_from_file_location("expected_model_h3", SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fixture(base):
    folder = base / "sercop-portal-csv-2021-synthetic"
    folder.mkdir()
    buyers = [
        "EC-RUC-0100000000001-new",
        "EC-RUC-0200000000001",
        "EC-RUC-0100000000001",
        "EC-RUC-0100000000001",
        "EC-RUC-0300000000001",
    ]
    releases = [
        dict(
            ocid=str(i),
            buyer_id=buyer,
            buyer_name="Entidad sintética",
            date="2026-01-01" if i == 2 else "2021-01-31T23:30:00-05:00",
        )
        for i, buyer in enumerate(buyers)
    ]
    write_csv(folder / "releases_2021.csv", ("ocid", "buyer_id", "buyer_name", "date"), releases)
    write_csv(
        folder / "tender_2021.csv",
        ("ocid", "value_amount", "value_currency", "procurementMethod", "procurementMethodDetails"),
        [
            dict(
                ocid=str(i),
                value_amount="100.12345" if i == 0 else "",
                value_currency="USD",
                procurementMethod="selective",
                procurementMethodDetails="Catálogo electrónico Mejor oferta en el convenio X",
            )
            for i in range(5)
        ],
    )
    write_csv(
        folder / "awards_2021.csv",
        ("ocid", "id", "amount", "currency"),
        [
            dict(ocid=ocid, id=str(i), amount=amount, currency="USD")
            for i, (ocid, amount) in enumerate(
                (("0", "0.10"), ("0", "0.20"), ("1", "5"), ("2", "7"), ("3", ""), ("4", "9"))
            )
        ],
    )
    seed = base / "seed.csv"
    fields = ("buyer_id", "ruc_root", "entity_type", "status")
    rows = [
        dict(buyer_id=f"EC-RUC-{root}", ruc_root=root, entity_type=kind, status=status)
        for root, kind, status in (
            ("0100000000001", "ministerio", "aprobada"),
            ("0200000000001", "instituto", "dudosa"),
            ("0300000000001", "fuera_de_alcance", "aprobada"),
        )
    ]
    write_csv(seed, fields, rows)
    return folder, seed, releases, rows


def control(rows, group, stage):
    return next(row for row in rows if row["grupo"] == group and row["etapa"] == stage)


class ExpectedModelTests(unittest.TestCase):
    def test_multiple_awards_window_doubt_root_and_blanks(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, seed, _, _ = fixture(base)
            rows = model.measure(base, seed, years=(2021,))
            fact = control(rows, "cadena", "FactContratacion")
            self.assertEqual(
                (fact["filas"], fact["suma_adjudicado_usd"], fact["suma_estimado_usd"]), (2, "0.30", "100.12345")
            )
            self.assertEqual(control(rows, "dimension", "DimEntidad")["filas"], 2)
            self.assertEqual(control(rows, "dimension", "DimMetodo")["filas"], 2)
            self.assertEqual(control(rows, "dimension", "DimTiempo")["filas"], 60)
            self.assertEqual(control(rows, "exclusion", "Fuera de la ventana 2021-2025")["filas"], 1)
            self.assertEqual(control(rows, "alcance", "Dudoso o sin clasificar")["filas"], 1)
            self.assertEqual(control(rows, "alcance", "Fuera del gobierno central")["filas"], 1)
            self.assertEqual(control(rows, "cadena", "Nacional descargado")["suma_adjudicado_usd"], "21.30")

    def test_conflicting_root_overrides_exact_match(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, seed, _, seed_rows = fixture(base)
            seed_rows.append(
                dict(
                    buyer_id="EC-RUC-0100000000001-conflict",
                    ruc_root="0100000000001",
                    entity_type="ministerio",
                    status="dudosa",
                )
            )
            write_csv(seed, seed_rows[0].keys(), seed_rows)
            exact, roots = model.load_seed(seed)
            self.assertEqual(model.classification("EC-RUC-0100000000001", exact, roots)[0], "Dudoso o sin clasificar")

    def test_duplicate_source_stops_without_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            folder, seed, releases, _ = fixture(base)
            write_csv(folder / "releases_2021.csv", releases[0].keys(), [*releases, releases[0]])
            with self.assertRaisesRegex(ValueError, "duplicate release"):
                model.measure(base, seed, years=(2021,))

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.csv"
            output.write_text("preserved\n", encoding="utf-8", newline="\n")
            result = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), directory, "missing.csv", "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserved\n")

    def test_no_awarded_amount_remains_blank(self):
        stats = model.empty_stats()
        model.add(stats, None, None)
        self.assertEqual(stats, [1, 0, 0, 0, 0])
        self.assertIsNone(model.amount_of(" "))
        self.assertEqual(
            model.procedure_of("Catálogo\nelectrónico Mejor oferta en el convenio Y"),
            "Catálogo electrónico Mejor oferta",
        )

    def test_all_empty_imports_produce_empty_totals_not_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            folder, seed, releases, _ = fixture(base)
            write_csv(folder / "releases_2021.csv", releases[0].keys(), [releases[3]])
            write_csv(
                folder / "tender_2021.csv",
                ("ocid", "value_amount", "value_currency", "procurementMethod", "procurementMethodDetails"),
                [],
            )
            write_csv(
                folder / "awards_2021.csv",
                ("ocid", "id", "amount", "currency"),
                [dict(ocid="3", id="blank", amount="", currency="")],
            )
            fact = control(model.measure(base, seed, years=(2021,)), "cadena", "FactContratacion")
            self.assertEqual(fact["filas"], 1)
            self.assertEqual(fact["suma_adjudicado_usd"], "")
            self.assertEqual(fact["suma_estimado_usd"], "")

    def test_no_approved_sector_still_reports_zero_fact_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, seed, _, seed_rows = fixture(base)
            for row in seed_rows:
                row["status"] = "dudosa"
            write_csv(seed, seed_rows[0].keys(), seed_rows)
            rows = model.measure(base, seed, years=(2021,))
            fact = control(rows, "cadena", "FactContratacion")
            self.assertEqual(fact["filas"], 0)
            self.assertEqual(fact["suma_adjudicado_usd"], "")
            self.assertEqual(control(rows, "dimension", "DimEntidad")["filas"], 1)


if __name__ == "__main__":
    unittest.main()
