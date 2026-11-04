"""Tests for scripts/inspect_sercop_zip.py with synthetic ZIP files built in tmp_path."""

import json
import sys

import inspect_sercop_zip as inspector
import pytest


def inspect(path, expected=None):
    return inspector.inspect_zip(path, expected)


def run_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["inspect_sercop_zip.py", *map(str, args)])
    return inspector.main()


def test_counts_match_hand_computed_values(sample_zip):
    report = inspect(sample_zip)

    assert report["packages"] == 2
    assert report["releases"] == 3
    assert report["distinct_ocids"] == 2
    assert report["releases_without_nonempty_ocid"] == 1
    assert report["distinct_ocid_release_id_pairs"] == 2
    assert report["award_objects"] == 3
    assert report["contract_objects"] == 3
    # Only 90 counts: "90" is a string and 1e999 decodes to an infinite float.
    assert report["awards_with_numeric_amount"] == 1
    # 80 and 5 count; the third contract has no value.
    assert report["contracts_with_numeric_amount"] == 2
    assert report["releases_with_multiple_awards"] == 1
    assert report["releases_with_multiple_contracts"] == 1
    assert report["award_count_distribution"] == {0: 1, 1: 1, 2: 1}
    assert report["contract_count_distribution"] == {0: 1, 1: 1, 2: 1}
    assert report["package_field_presence"] == {
        "license": 2,
        "publicationPolicy": 2,
        "publishedDate": 2,
        "publisher": 2,
        "releases": 2,
        "uri": 2,
    }
    assert report["release_field_presence"] == {
        "awards": 2,
        "buyer": 2,
        "contracts": 3,
        "date": 2,
        "id": 3,
        "ocid": 2,
        "tender": 2,
    }
    assert report["json_entry"] == "releases.json"
    assert report["expected_processes"] is None
    assert report["distinct_ocids_match_expected"] is None
    assert report["ocds_schema_validated"] is False


@pytest.mark.parametrize(("expected", "matches"), [(2, True), (3, False), (0, False)])
def test_compares_distinct_ocids_with_expected_count(sample_zip, expected, matches):
    assert inspect(sample_zip, expected)["distinct_ocids_match_expected"] is matches


def test_report_records_hashes_and_sizes(sample_zip, file_sha256, scripts_dir):
    before = file_sha256(sample_zip)

    report = inspect(sample_zip)

    assert file_sha256(sample_zip) == before
    assert report["source_sha256"] == before
    assert report["source_hash_unchanged"] is True
    assert report["source_bytes"] == sample_zip.stat().st_size
    assert report["inspector_sha256"] == file_sha256(scripts_dir / "inspect_sercop_zip.py")


def test_stops_when_zip_hash_changes_during_inspection(sample_zip, monkeypatch):
    hashes = iter(["A" * 64, "B" * 64])
    monkeypatch.setattr(inspector, "sha256", lambda _path: next(hashes))

    with pytest.raises(ValueError, match="hash changed"):
        inspect(sample_zip)


def test_report_contains_no_record_values(sample_zip, sentinel):
    text = json.dumps(inspect(sample_zip), ensure_ascii=True)

    assert sentinel not in text


def test_empty_award_list_and_award_without_amount(make_zip):
    releases = [
        {"ocid": "ocds-a", "id": "1", "awards": [], "contracts": []},
        {"ocid": "ocds-b", "id": "2", "awards": [{"id": "x"}, {"id": "y", "value": {"currency": "USD"}}]},
    ]
    report = inspect(make_zip({"r.json": [{"releases": releases}]}))

    assert report["award_objects"] == 2
    assert report["awards_with_numeric_amount"] == 0
    assert report["award_count_distribution"] == {0: 1, 2: 1}
    assert report["contract_count_distribution"] == {0: 2}


@pytest.mark.parametrize(
    "amount_json",
    ['"100"', "true", "false", "null", "[1]", '{"amount": 1}', "1e999", "-1e999"],
    ids=["string", "true", "false", "null", "list", "object", "overflow", "negative-overflow"],
)
def test_non_numeric_amounts_are_not_counted(make_zip, amount_json):
    text = '[{"releases": [{"ocid": "o", "id": "1", "awards": [{"value": {"amount": ' + amount_json + "}}]}]}]"
    report = inspect(make_zip({"r.json": text}))

    assert report["award_objects"] == 1
    assert report["awards_with_numeric_amount"] == 0


@pytest.mark.parametrize("amount_json", ["0", "-5", "1.25", "12345678901234567890"])
def test_numeric_amounts_are_counted(make_zip, amount_json):
    text = '[{"releases": [{"ocid": "o", "id": "1", "awards": [{"value": {"amount": ' + amount_json + "}}]}]}]"

    assert inspect(make_zip({"r.json": text}))["awards_with_numeric_amount"] == 1


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_json_numeric_constants_are_rejected(make_zip, constant):
    text = '[{"releases": [{"ocid": "o", "id": "1", "awards": [{"value": {"amount": ' + constant + "}}]}]}]"

    with pytest.raises(ValueError, match="Non-JSON numeric constant"):
        inspect(make_zip({"r.json": text}))


@pytest.mark.parametrize("key", ["awards", "contracts", "releases"])
def test_object_instead_of_list_stops_inspection(make_zip, key):
    release = {"ocid": "o", "id": "1"}
    package = {"releases": [release]}
    if key == "releases":
        package["releases"] = release
    else:
        release[key] = {"id": "single", "value": {"amount": 1}}

    with pytest.raises(ValueError, match=f"Expected an array of objects in {key}"):
        inspect(make_zip({"r.json": [package]}))


def test_package_with_empty_releases(make_zip):
    report = inspect(make_zip({"r.json": [{"releases": []}, {"releases": [{"ocid": "o", "id": "1"}]}]}))

    assert report["packages"] == 2
    assert report["releases"] == 1


def test_empty_root_array(make_zip):
    report = inspect(make_zip({"r.json": " [ ] \n"}))

    assert report["packages"] == 0
    assert report["releases"] == 0


@pytest.mark.parametrize(
    "entries",
    [{}, {"notes.txt": "x"}, {"a.json": [], "b.JSON": []}, {"a.json": [], "folder/b.json": []}],
    ids=["empty-zip", "no-json", "two-json", "json-in-subfolder"],
)
def test_requires_exactly_one_json_entry(make_zip, entries):
    with pytest.raises(ValueError, match="exactly one JSON entry"):
        inspect(make_zip(entries))


def test_ignores_non_json_entries(make_zip):
    report = inspect(make_zip({"readme.txt": "not json", "data.json": [{"releases": []}]}))

    assert report["json_entry"] == "data.json"
    assert report["packages"] == 1


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "top-level JSON array"),
        ('{"releases": []}', "top-level JSON array"),
        ("[1]", "package object at index 0"),
        ('[{"releases": []}, 2]', "package object at index 1"),
        ('[{"releases": []} {"releases": []}]', "Missing separator after package index 0"),
        ('[{"releases": []}] []', "Unexpected content after the JSON array"),
        ('[{"releases": [', "Invalid or truncated JSON at package index 0"),
        ('[{"releases": []},', "package object at index 1"),
        ('[{"releases": []}', "Missing separator after package index 0"),
    ],
    ids=[
        "empty-file",
        "root-object",
        "number-item",
        "number-second-item",
        "missing-comma",
        "trailing-content",
        "truncated-object",
        "truncated-after-comma",
        "missing-closing-bracket",
    ],
)
def test_rejects_malformed_or_truncated_json(make_zip, text, message):
    with pytest.raises(ValueError, match=message):
        inspect(make_zip({"r.json": text}))


def test_accepts_utf8_bom(make_zip, packages):
    plain = inspect(make_zip({"r.json": packages}, name="plain.zip"))
    with_bom = inspect(make_zip({"r.json": packages}, name="bom.zip", encoding="utf-8-sig"))

    for key in ("packages", "releases", "distinct_ocids", "award_objects", "awards_with_numeric_amount"):
        assert with_bom[key] == plain[key]


def test_accepts_whitespace_between_tokens(make_zip):
    text = '\r\n[\n\t{"releases": [{"ocid": "a", "id": "1"}]} ,\r\n {"releases": []}\n]\n\n'
    report = inspect(make_zip({"r.json": text}))

    assert report["packages"] == 2
    assert report["releases"] == 1


def test_rejects_invalid_utf8(make_zip):
    with pytest.raises(UnicodeDecodeError):
        inspect(make_zip({"r.json": b'[{"releases": [{"ocid": "\xff"}]}]'}))


def test_small_chunks_give_the_same_counts(sample_zip, monkeypatch):
    expected = inspect(sample_zip)
    # A 7-character chunk splits keys, strings and numbers across reads.
    monkeypatch.setattr(inspector, "CHUNK_CHARS", 7)

    report = inspect(sample_zip)

    for key in ("packages", "releases", "distinct_ocids", "award_objects", "contracts_with_numeric_amount"):
        assert report[key] == expected[key]


def test_package_larger_than_buffer_limit_stops(make_zip, monkeypatch):
    # The real limit is 64 Mi characters; shrinking it avoids building a huge file.
    monkeypatch.setattr(inspector, "CHUNK_CHARS", 16)
    monkeypatch.setattr(inspector, "MAX_BUFFER_CHARS", 64)
    path = make_zip({"r.json": [{"releases": [{"ocid": "o" * 200, "id": "1"}]}]})

    with pytest.raises(ValueError, match="exceeds the 64 Mi-character buffer limit"):
        inspect(path)


def test_packages_below_buffer_limit_pass(make_zip, monkeypatch):
    monkeypatch.setattr(inspector, "CHUNK_CHARS", 16)
    monkeypatch.setattr(inspector, "MAX_BUFFER_CHARS", 64)
    # Each package is small; the buffer drops consumed text, so many of them fit.
    path = make_zip({"r.json": [{"releases": []}] * 50})

    assert inspect(path)["packages"] == 50


# --- main() in process -------------------------------------------------------


def test_main_prints_report_and_writes_new_output(sample_zip, tmp_path, monkeypatch, capsys):
    output = tmp_path / "summary.json"

    assert run_main(monkeypatch, sample_zip, "--expected-processes", "2", "--output", output) == 0

    printed = capsys.readouterr().out
    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(printed)
    assert json.loads(printed)["distinct_ocids_match_expected"] is True


def test_main_does_not_overwrite_existing_output(sample_zip, tmp_path, monkeypatch, capsys):
    output = tmp_path / "summary.json"
    output.write_text("previous evidence", encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        run_main(monkeypatch, sample_zip, "--output", output)

    assert exit_info.value.code == 2
    assert output.read_text(encoding="utf-8") == "previous evidence"
    assert "ya existe" in capsys.readouterr().err


def test_main_rejects_negative_expected_count(sample_zip, monkeypatch):
    with pytest.raises(SystemExit) as exit_info:
        run_main(monkeypatch, sample_zip, "--expected-processes", "-1")

    assert exit_info.value.code == 2


def test_main_failure_hides_record_values(make_zip, tmp_path, monkeypatch, capsys, sentinel):
    path = make_zip({"r.json": [{"releases": [{"ocid": sentinel, "id": "1", "contracts": {"id": sentinel}}]}]})
    output = tmp_path / "summary.json"

    assert run_main(monkeypatch, path, "--output", output) == 1

    captured = capsys.readouterr()
    assert "Inspección detenida (ValueError)" in captured.err
    assert sentinel not in captured.out + captured.err
    assert not output.exists()


def test_main_reports_missing_zip(tmp_path, monkeypatch, capsys):
    assert run_main(monkeypatch, tmp_path / "missing.zip") == 1
    assert "FileNotFoundError" in capsys.readouterr().err


def test_main_reports_file_that_is_not_a_zip(tmp_path, monkeypatch, capsys):
    path = tmp_path / "fake.zip"
    path.write_bytes(b"not a zip archive")

    assert run_main(monkeypatch, path) == 1
    assert "BadZipFile" in capsys.readouterr().err


def test_main_reports_corrupt_compressed_data(sample_zip, corrupt_deflate, monkeypatch, capsys):
    assert run_main(monkeypatch, corrupt_deflate(sample_zip)) == 1
    assert "Inspección detenida (error)" in capsys.readouterr().err


@pytest.mark.parametrize("error", [EOFError("truncated"), NotImplementedError("compression")])
def test_main_reports_unreadable_entries(sample_zip, monkeypatch, capsys, error):
    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(inspector, "inspect_zip", fail)

    assert run_main(monkeypatch, sample_zip) == 1
    assert f"Inspección detenida ({type(error).__name__})" in capsys.readouterr().err


@pytest.mark.parametrize("ocid", ["", "   "])
def test_release_with_blank_ocid_is_not_counted_as_a_pair(make_zip, ocid):
    release = {"ocid": ocid, "id": "r1"}
    report = inspect(make_zip({"r.json": [{"releases": [release]}]}))

    assert report["releases_without_nonempty_ocid"] == 1
    assert report["distinct_ocids"] == 0
    assert report["distinct_ocid_release_id_pairs"] == 0


# --- command line ------------------------------------------------------------


def test_command_line_success(run_script, sample_zip, tmp_path):
    output = tmp_path / "cli-summary.json"

    result = run_script("inspect_sercop_zip.py", sample_zip, "--output", output)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads(output.read_text(encoding="utf-8"))


def test_command_line_failure_exit_code(run_script, make_zip, sentinel):
    path = make_zip({"r.json": [{"releases": {"ocid": sentinel}}]})

    result = run_script("inspect_sercop_zip.py", path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "Inspección detenida (ValueError)" in result.stderr
    assert sentinel not in result.stderr


def test_command_line_existing_output_exit_code(run_script, sample_zip, tmp_path):
    output = tmp_path / "taken.json"
    output.write_text("{}", encoding="utf-8")

    result = run_script("inspect_sercop_zip.py", sample_zip, "--output", output)

    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "{}"
