"""Independently calculate aggregate controls for the H3 intermediate Power Query steps.

Usage: python -I scripts/expected_controls_h3.py DERIVADOS --output NEW.csv
Only the standard library is used. Inputs are never modified and output is created exclusively.
Years refer to the source file, not the business date. Empty monetary totals remain empty.
"""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
import re


YEARS = tuple(range(2021, 2026))
ROOT_PATTERN = re.compile(r"EC-RUC-([0-9]{13})(?:-[^\r\n]+)?")
COMMON = ("Cinco años anexados",)
STEPS = {
    "releases": (
        *COMMON,
        "Campos para comprobar claves",
        "Claves completas verificadas",
        "Unicidad de proceso verificada",
        "Fecha de negocio desde releases.date",
        "Año y mes desde la fecha de negocio",
        "Raíz de RUC desde buyer_id",
        "Columnas finales de procesos",
    ),
    "tender": (
        *COMMON,
        "Campos para limpiar licitaciones",
        "Método sin espacios repetidos ni saltos de línea",
        "Importe estimado decimal anulable",
        "Unicidad de licitación verificada",
        "Moneda solo USD verificada",
        "Importes negativos excluidos",
        "Indicador de importe estimado",
        "Columnas finales de licitaciones",
    ),
    "awards": (
        *COMMON,
        "Campos de adjudicación sin importes vacíos de oferta",
        "Importe adjudicado decimal anulable",
        "Unicidad de adjudicación verificada",
        "Moneda solo USD verificada",
        "Importes negativos excluidos",
        "Adjudicaciones agrupadas por ocid (suma, conteo)",
    ),
}
FIELDS = (
    "tabla",
    "anio_archivo",
    "paso",
    "filas_antes",
    "filas_despues",
    "suma_antes_usd",
    "suma_despues_usd",
    "filas_excluidas",
    "metrica",
    "valor",
)


def amount_of(value):
    """Parse the portal's en-US decimal, preserving blank versus numeric zero."""
    value = value.strip()
    amount = Decimal(value) if value else None
    if amount is not None and not amount.is_finite():
        raise ValueError("non-finite amount")
    return amount


def root_of(value):
    match = ROOT_PATTERN.fullmatch(value)
    return match[1] if match else "NO_IDENTIFICADO"


def normalise(value):
    # Exactly the separator set of NormalizarTexto in the M draft.
    return " ".join(part for part in re.split(r"[ \t\r\n\u00a0]", value) if part)


def add(stats, amount):
    stats[0] += 1
    if amount is not None:
        stats[1] += amount
        stats[2] += 1


def empty_stats():
    return [0, Decimal(0), 0]


def monetary(stats):
    return str(stats[1]) if stats[2] else ""


def measure(base, years=YEARS):
    """Return counts and exact sums only; never return source records or identifiers.

    Duplicate keys fail closed just like the M guards. No arbitrary duplicate is retained.
    Currency and negative exclusions are sequential, so their counts do not overlap.
    """
    base = Path(base)
    snapshots = defaultdict(empty_stats)
    metrics = defaultdict(Counter)
    processes = {}
    tenders = {}
    awards = {}
    award_keys = set()
    for year in years:
        folders = sorted(base.glob(f"sercop-portal-csv-{year}-*"))
        if len(folders) != 1:
            raise ValueError(f"expected exactly one source folder for {year}, found {len(folders)}")
        for table, steps in STEPS.items():
            key = (table, year)
            counts = metrics[key]
            with (folders[0] / f"{table}_{year}.csv").open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    ocid = row["ocid"]
                    amount = (
                        None
                        if table == "releases"
                        else amount_of(row["value_amount" if table == "tender" else "amount"])
                    )
                    if table == "releases":
                        for field in ("ocid", "buyer_id", "buyer_name", "date"):
                            counts[f"vacios_{field}"] += not row[field].strip()
                        if any(not row[field].strip() for field in ("ocid", "buyer_id", "buyer_name", "date")):
                            raise ValueError("S-05: missing release key")
                        if ocid in processes:
                            raise ValueError("Q-06: duplicate release ocid; no rows removed")
                        moment = date.fromisoformat(row["date"][:10])
                        processes[ocid] = year
                        counts["buyer_id_malformado"] += root_of(row["buyer_id"]) == "NO_IDENTIFICADO"
                        counts["fecha_otro_anio"] += moment.year != year
                        counts["fecha_fuera_2021_2025"] += not 2021 <= moment.year <= 2025
                        for step in steps:
                            add(snapshots[table, year, step], amount)
                        continue
                    if table == "tender":
                        if ocid in tenders:
                            raise ValueError("Q-06/S-04: duplicate tender ocid; no rows removed")
                        tenders[ocid] = None
                        counts["detalle_normalizado"] += (
                            normalise(row["procurementMethodDetails"]) != row["procurementMethodDetails"]
                        )
                    else:
                        award_key = (ocid, row["id"])
                        if award_key in award_keys:
                            raise ValueError("Q-06: duplicate award key; no rows removed")
                        award_keys.add(award_key)
                        for field in ("correctedValue_amount", "enteredValue_amount"):
                            counts[f"poblados_{field}"] += bool(row[field].strip())
                    counts["importes_vacios"] += amount is None
                    counts["importes_cero"] += amount == 0
                    currency = row["value_currency" if table == "tender" else "currency"]
                    usd = currency == "USD" or (amount is None and currency == "")
                    nonnegative = amount is None or amount >= 0
                    counts["moneda_excluidas"] += not usd
                    counts["negativos_excluidos"] += usd and not nonnegative
                    for step in steps:
                        if step == "Adjudicaciones agrupadas por ocid (suma, conteo)":
                            break
                        if step == "Moneda solo USD verificada" and not usd:
                            break
                        if step == "Importes negativos excluidos" and not nonnegative:
                            break
                        add(snapshots[table, year, step], amount)
                    if usd and nonnegative:
                        if table == "tender":
                            tenders[ocid] = amount
                        else:
                            entry = awards.setdefault(ocid, [year, empty_stats()])
                            if entry[0] != year:
                                raise ValueError("award ocid shared between source years")
                            add(entry[1], amount)
    for ocid, (year, stats) in awards.items():
        add(snapshots["awards", year, STEPS["awards"][-1]], stats[1] if stats[2] else None)
        counts = metrics["awards", year]
        counts["procesos_varias_adjudicaciones"] += stats[0] > 1
        counts["filas_adicionales"] += stats[0] - 1
        counts["grupos_todos_null"] += not stats[2]
        counts["ocid_sin_proceso"] += ocid not in processes
        counts["procesos_ambos_importes"] += stats[2] > 0 and tenders.get(ocid) is not None
    output = []
    for table, steps in STEPS.items():
        for year in (*years, "TOTAL"):
            selected = years if year == "TOTAL" else (year,)
            previous = None
            for step in steps:
                current = [
                    sum((snapshots[table, y, step][i] for y in selected), Decimal(0) if i == 1 else 0) for i in range(3)
                ]
                before = previous if previous is not None else current
                # Group collapse is not an exclusion: every input award is counted in NumAdjudicaciones.
                excluded = (
                    before[0] - current[0]
                    if step in ("Moneda solo USD verificada", "Importes negativos excluidos")
                    else 0
                )
                output.append(
                    dict(
                        zip(
                            FIELDS,
                            (
                                table,
                                year,
                                step,
                                before[0],
                                current[0],
                                monetary(before),
                                monetary(current),
                                excluded,
                                "",
                                "",
                            ),
                            strict=True,
                        )
                    )
                )
                previous = current
            names = set().union(*(metrics[table, y] for y in selected))
            names.add("duplicados_excluidos")
            for name in sorted(names):
                output.append(
                    dict(
                        zip(
                            FIELDS,
                            (
                                table,
                                year,
                                "Diagnóstico",
                                "",
                                "",
                                "",
                                "",
                                "",
                                name,
                                sum(metrics[table, y][name] for y in selected),
                            ),
                            strict=True,
                        )
                    )
                )
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("derivados", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; choose a new evidence filename")
    csv.field_size_limit(2**30)
    controls = measure(args.derivados)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(controls)
    print(f"{len(controls)} aggregate controls written")


if __name__ == "__main__":
    main()
