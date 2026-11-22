"""Validate H3 log coverage and before/after controls using standard-library CSV."""

import argparse
import csv
from pathlib import Path
import re
import sys


COLUMNS = (
    "id",
    "tabla",
    "problema_h2",
    "transformacion",
    "paso_power_query",
    "control_antes",
    "control_despues",
    "nota",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(quality: list[dict[str, str]], log: list[dict[str, str]]) -> list[str]:
    required = {
        row["id"] for row in quality if re.fullmatch(r"Q-(?:E)?\d+", row["id"]) and (row.get("accion_h3") or "").strip()
    }
    errors = [f"Missing action: {key}" for key in sorted(required - {row.get("id") for row in log})]
    seen = set()
    for index, row in enumerate(log, 2):
        label = f"Row {index} ({row.get('id', '')})"
        if any(column not in row for column in COLUMNS):
            errors.append(f"{label}: missing column")
        if not (row.get("id") or "").strip() or row.get("id") in seen:
            errors.append(f"{label}: missing or duplicate id")
        seen.add(row.get("id"))
        for column in ("tabla", "problema_h2", "transformacion", "control_antes", "control_despues"):
            if not (row.get(column) or "").strip():
                errors.append(f"{label}: missing {column}")
        if not (row.get("paso_power_query") or "").strip() and not (row.get("nota") or "").strip():
            errors.append(f"{label}: neither step nor explanation")
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quality", type=Path)
    parser.add_argument("log", type=Path)
    args = parser.parse_args(argv)
    try:
        errors = validate(read_csv(args.quality), read_csv(args.log))
    except (OSError, UnicodeError, csv.Error, KeyError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Bitacora: coverage, steps/explanations and before/after controls OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
