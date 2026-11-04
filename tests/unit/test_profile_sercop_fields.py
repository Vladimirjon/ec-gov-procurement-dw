"""Tests for scripts/profile_sercop_fields.py with synthetic ZIP files built in tmp_path."""

import json
import sys
import zlib

import profile_sercop_fields as profiler
import pytest


def run_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["profile_sercop_fields.py", *map(str, args)])
    return profiler.main()


def single_release_zip(make_zip, release):
    return make_zip({"r.json": [{"releases": [release]}]})


def test_counts_match_hand_computed_values(sample_zip):
    report = profiler.profile(sample_zip)

    assert report["counts"] == {
        "packages": 2,
        "releases": 3,
        "release_date": 2,
        "buyer_id": 2,
        "buyer_name": 2,
        "tender": 2,
        # 100.5 counts; `true` is a boolean, not an amount.
        "tender_value_amount_numeric": 1,
        "tender_start_date": 1,
        "tender_procurement_method": 2,
        "tender_procurement_method_details": 2,
        "award_objects": 3,
        # Only 90 counts: "90" is a string and 1e999 decodes to an infinite float.
        "award_value_amount_numeric": 1,
        "award_date": 1,
        "releases_with_numeric_award": 1,
        "releases_with_tender_and_award_amount": 1,
    }
    assert report["anomalies"] == {}
    assert report["package_license_values"] == {"https://example.invalid/license": 2}
    assert report["package_publisher_values"] == {"Synthetic publisher": 2}
    assert report["package_publication_policy_values"] == {"https://example.invalid/policy": 2}
    assert report["procurement_method_values"] == {"open": 1, "direct": 1}
    assert report["procurement_method_details_distinct"] == 2
    assert report["procurement_method_details_top10"] == {"Synthetic method A": 1, "Synthetic method B": 1}
    assert report["award_currency_values"] == {"USD": 1}
    assert report["release_date_year_counts"] == {"2024": 1, "2025": 1}
    assert report["json_entry"] == "releases.json"
    assert report["ocds_schema_validated"] is False


def test_report_records_hashes_and_sizes(sample_zip, file_sha256, scripts_dir):
    before = file_sha256(sample_zip)

    report = profiler.profile(sample_zip)

    assert file_sha256(sample_zip) == before
    assert report["source_sha256"] == before
    assert report["source_hash_unchanged"] is True
    assert report["source_bytes"] == sample_zip.stat().st_size
    assert report["profiler_sha256"] == file_sha256(scripts_dir / "profile_sercop_fields.py")


def test_stops_when_zip_hash_changes_during_profiling(sample_zip, monkeypatch):
    hashes = iter(["A" * 64, "B" * 64])
    monkeypatch.setattr(profiler.INSPECTOR, "sha256", lambda _path: next(hashes))

    with pytest.raises(ValueError, match="hash changed"):
        profiler.profile(sample_zip)


def test_report_contains_no_record_values(sample_zip, sentinel):
    text = json.dumps(profiler.profile(sample_zip), ensure_ascii=True)

    assert sentinel not in text


def test_empty_award_list_and_award_without_amount(make_zip):
    releases = [
        {"ocid": "a", "awards": []},
        {"ocid": "b", "awards": [{"id": "x"}, {"id": "y", "value": {"currency": "USD"}}]},
    ]
    report = profiler.profile(make_zip({"r.json": [{"releases": releases}]}))

    assert report["counts"]["award_objects"] == 2
    assert report["counts"]["award_value_amount_numeric"] == 0
    assert report["counts"]["releases_with_numeric_award"] == 0
    assert report["award_currency_values"] == {}
    assert report["anomalies"] == {}


@pytest.mark.parametrize(
    "amount_json",
    ['"100"', "true", "false", "null", "[1]", '{"amount": 1}', "1e999", "-1e999"],
    ids=["string", "true", "false", "null", "list", "object", "overflow", "negative-overflow"],
)
def test_non_numeric_amounts_are_not_counted(make_zip, amount_json):
    value = '{"amount": ' + amount_json + "}"
    text = '[{"releases": [{"tender": {"value": ' + value + '}, "awards": [{"value": ' + value + "}]}]}]"
    counts = profiler.profile(make_zip({"r.json": text}))["counts"]

    assert counts["tender_value_amount_numeric"] == 0
    assert counts["award_value_amount_numeric"] == 0
    assert counts["releases_with_tender_and_award_amount"] == 0


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_json_numeric_constants_are_rejected(make_zip, constant):
    text = '[{"releases": [{"awards": [{"value": {"amount": ' + constant + "}}]}]}]"

    with pytest.raises(ValueError, match="Non-JSON numeric constant"):
        profiler.profile(make_zip({"r.json": text}))


def test_contracts_object_is_an_anomaly_and_the_run_continues(make_zip):
    packages = [
        {"releases": [{"ocid": "a", "contracts": {"id": "single"}}]},
        {"releases": [{"ocid": "b", "contracts": []}]},
    ]
    report = profiler.profile(make_zip({"r.json": packages}))

    assert report["anomalies"] == {"contracts_not_list_of_objects": 1}
    assert report["counts"]["packages"] == 2
    assert report["counts"]["releases"] == 2


def test_awards_object_is_an_anomaly_counted_as_one_award(make_zip):
    release = {"awards": {"value": {"amount": 7, "currency": "USD"}}}
    report = profiler.profile(single_release_zip(make_zip, release))

    assert report["anomalies"] == {"awards_not_list_of_objects": 1}
    assert report["counts"]["award_objects"] == 1
    assert report["counts"]["award_value_amount_numeric"] == 1


def test_awards_list_with_non_objects_is_an_anomaly_and_ignored(make_zip):
    release = {"awards": [{"value": {"amount": 7}}, "not an object"]}
    report = profiler.profile(single_release_zip(make_zip, release))

    assert report["anomalies"] == {"awards_not_list_of_objects": 1}
    assert report["counts"]["award_objects"] == 0


def test_releases_object_is_an_anomaly_counted_as_one_release(make_zip):
    report = profiler.profile(make_zip({"r.json": [{"releases": {"ocid": "a"}}]}))

    assert report["anomalies"] == {"releases_not_list_of_objects": 1}
    assert report["counts"]["releases"] == 1


def test_package_with_empty_releases(make_zip):
    report = profiler.profile(make_zip({"r.json": [{"releases": []}, {"releases": [{"ocid": "a"}]}]}))

    assert report["counts"]["packages"] == 2
    assert report["counts"]["releases"] == 1
    assert report["anomalies"] == {}


def test_missing_package_metadata_is_reported_as_none(make_zip):
    report = profiler.profile(make_zip({"r.json": [{"releases": []}]}))

    assert report["package_license_values"] == {"None": 1}
    assert report["package_publisher_values"] == {"None": 1}


@pytest.mark.parametrize(
    "entries",
    [{}, {"notes.txt": "x"}, {"a.json": [], "b.JSON": []}],
    ids=["empty-zip", "no-json", "two-json"],
)
def test_requires_exactly_one_json_entry(make_zip, entries):
    with pytest.raises(ValueError, match="exactly one JSON entry"):
        profiler.profile(make_zip(entries))


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('{"releases": []}', "top-level JSON array"),
        ("[1]", "package object at index 0"),
        ('[{"releases": [', "Invalid or truncated JSON at package index 0"),
        ('[{"releases": []}] []', "Unexpected content after the JSON array"),
    ],
    ids=["root-object", "number-item", "truncated-object", "trailing-content"],
)
def test_rejects_malformed_or_truncated_json(make_zip, text, message):
    with pytest.raises(ValueError, match=message):
        profiler.profile(make_zip({"r.json": text}))


def test_accepts_utf8_bom(make_zip, packages):
    plain = profiler.profile(make_zip({"r.json": packages}, name="plain.zip"))
    with_bom = profiler.profile(make_zip({"r.json": packages}, name="bom.zip", encoding="utf-8-sig"))

    assert with_bom["counts"] == plain["counts"]


def test_package_larger_than_buffer_limit_stops(make_zip, monkeypatch):
    # The profiler reuses the inspector's reader, loaded as its own module object.
    monkeypatch.setattr(profiler.INSPECTOR, "CHUNK_CHARS", 16)
    monkeypatch.setattr(profiler.INSPECTOR, "MAX_BUFFER_CHARS", 64)
    path = make_zip({"r.json": [{"releases": [{"ocid": "o" * 200}]}]})

    with pytest.raises(ValueError, match="exceeds the 64 Mi-character buffer limit"):
        profiler.profile(path)


# --- main() in process -------------------------------------------------------


def test_main_prints_report_and_writes_new_output(sample_zip, tmp_path, monkeypatch, capsys):
    output = tmp_path / "profile.json"

    assert run_main(monkeypatch, sample_zip, "--output", output) == 0

    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(capsys.readouterr().out)


def test_main_does_not_overwrite_existing_output(sample_zip, tmp_path, monkeypatch, capsys):
    output = tmp_path / "profile.json"
    output.write_text("previous evidence", encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        run_main(monkeypatch, sample_zip, "--output", output)

    assert exit_info.value.code == 2
    assert output.read_text(encoding="utf-8") == "previous evidence"
    assert "ya existe" in capsys.readouterr().err


def test_main_failure_hides_record_values(make_zip, tmp_path, monkeypatch, capsys, sentinel):
    text = '[{"releases": [{"ocid": "' + sentinel + '", "awards": [{"value": {"amount": NaN}}]}]}]'
    output = tmp_path / "profile.json"

    assert run_main(monkeypatch, make_zip({"r.json": text}), "--output", output) == 1

    captured = capsys.readouterr()
    assert "Perfilado detenido (ValueError)" in captured.err
    assert sentinel not in captured.out + captured.err
    assert not output.exists()


@pytest.mark.xfail(
    raises=zlib.error,
    strict=True,
    reason="Known defect: main() does not catch zlib.error, so a corrupt deflate stream ends with a "
    "traceback instead of the controlled message. The script is frozen evidence; see issue #43.",
)
def test_main_reports_corrupt_compressed_data(sample_zip, corrupt_deflate, monkeypatch):
    assert run_main(monkeypatch, corrupt_deflate(sample_zip)) == 1


# --- command line ------------------------------------------------------------


def test_command_line_success(run_script, sample_zip, tmp_path):
    output = tmp_path / "cli-profile.json"

    result = run_script("profile_sercop_fields.py", sample_zip, "--output", output)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads(output.read_text(encoding="utf-8"))


def test_command_line_failure_exit_code(run_script, make_zip):
    result = run_script("profile_sercop_fields.py", make_zip({"a.json": [], "b.json": []}))

    assert result.returncode == 1
    assert result.stdout == ""
    assert "Perfilado detenido (ValueError)" in result.stderr


def test_command_line_existing_output_exit_code(run_script, sample_zip, tmp_path):
    output = tmp_path / "taken.json"
    output.write_text("{}", encoding="utf-8")

    result = run_script("profile_sercop_fields.py", sample_zip, "--output", output)

    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "{}"
