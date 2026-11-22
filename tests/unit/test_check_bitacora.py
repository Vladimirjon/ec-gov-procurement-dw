import csv

import check_bitacora as module


def sample():
    quality = [
        {"id": "Q-01", "accion_h3": "Keep nulls"},
        {"id": "Q-E01", "accion_h3": "Pad"},
        {"id": "S-01", "accion_h3": "Keep"},
        {"id": "Q-99", "accion_h3": ""},
    ]
    log = [{column: "value" for column in module.COLUMNS} for _ in range(2)]
    for row, key in zip(log, ("Q-01", "Q-E01"), strict=True):
        row.update(id=key, control_antes="10", control_despues="10")
    return quality, log


def test_complete_log_and_explained_nonapplication():
    quality, log = sample()
    log[1]["paso_power_query"] = ""
    assert module.validate(quality, log) == []


def test_removing_one_action_fails_including_entity_actions():
    quality, log = sample()
    for index in range(2):
        errors = module.validate(quality, log[:index] + log[index + 1 :])
        assert f"Missing action: {log[index]['id']}" in errors


def test_missing_control_or_step_and_note_fails():
    quality, log = sample()
    for field in ("control_antes", "control_despues"):
        changed = [dict(row) for row in log]
        changed[0][field] = ""
        assert module.validate(quality, changed)
    log[0].update(paso_power_query="", nota="")
    assert module.validate(quality, log)


def test_cli_reads_utf8_csv_and_returns_failure(tmp_path):
    quality, log = sample()
    paths = [tmp_path / "quality.csv", tmp_path / "log.csv"]
    for path, rows in zip(paths, (quality, log), strict=True):
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    assert module.main([str(p) for p in paths]) == 0
    paths[1].write_text("id\nQ-01\n", encoding="utf-8", newline="\n")
    assert module.main([str(p) for p in paths]) == 1
