import csv
import importlib.util
import io
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "measure_tender_accuracy", ROOT / "scripts" / "measure_tender_accuracy.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def package(releases):
    return json.dumps({"uri": "x", "releases": releases}, ensure_ascii=False)


def test_iter_releases_streams_several_packages_with_small_chunks(monkeypatch):
    data = "[" + package([{"id": "a", "ocid": "o1"}, {"id": "ñ]é", "ocid": "o2"}])
    data += "," + package([]) + "," + package([{"id": "c", "ocid": "o3"}]) + "]"
    monkeypatch.setattr(module, "CHUNK", 5)
    found = list(module.iter_releases(io.BytesIO(data.encode("utf-8"))))
    assert [r["ocid"] for r in found] == ["o1", "o2", "o3"]
    assert found[1]["id"] == "ñ]é"


def test_measure_year_counts_differences(tmp_path):
    releases = [
        {
            "id": "r1",
            "ocid": "o1",
            "tender": {"value": {"amount": 10.005}, "procurementMethod": "open", "procurementMethodDetails": "A\nB"},
        },
        {"id": "r2", "ocid": "o2", "tender": {"value": {"amount": 0}, "procurementMethod": "direct"}},
        {"id": "r3", "ocid": "o3", "tender": {"value": {"amount": 5}, "procurementMethod": "open"}},
        {"id": "r4", "ocid": "o4"},
    ]
    zip_path = tmp_path / "releases_2099.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("releases_2099.json", "[" + package(releases) + "]")
    csv_path = tmp_path / "tender_2099.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ocid", "release_id", "value_amount", "procurementMethod", "procurementMethodDetails"])
        writer.writerow(["o1", "r1", "10.01", "open", "A B"])
        writer.writerow(["o2", "r2", "", "direct", ""])
        writer.writerow(["o3", "r3", "7.00", "limited", ""])
        writer.writerow(["o9", "r9", "1.00", "open", ""])
    year, stats = module.measure_year(("2099", str(zip_path), str(csv_path)))
    assert year == "2099"
    assert stats["json_releases"] == 4
    assert stats["json_tender_rows"] == 3
    assert stats["tender_rows_only_in_csv"] == 1
    assert stats["tender_rows_only_in_json"] == 0
    assert stats["amount_present_in_both"] == 2
    assert stats["amount_differs_up_to_0_01"] == 1
    assert stats["amount_differs_more_than_0_01"] == 1
    assert stats["json_amount_zero_csv_empty"] == 1
    assert stats["procurement_method_differs"] == 1
    assert stats["method_details_differs"] == 1
    assert stats["method_details_differs_only_in_whitespace"] == 1
