"""Calculate independent H3 model aggregates from portal CSV and the approved seed.

Usage: python -I scripts/expected_model_h3.py DERIVADOS SEED --output NEW.csv
Inputs are read only; output is exclusively created. Monetary blanks remain blank.
"""

import argparse
from collections import defaultdict
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
import re


YEARS = tuple(range(2021, 2026))
ROOT = re.compile(r"EC-RUC-([0-9]{13})(?:-[\s\S]+)?")
SECTOR = {"presidencia", "ministerio", "instituto"}
FIELDS = ("grupo", "etapa", "tipo_entidad", "anio", "filas", "suma_adjudicado_usd", "suma_estimado_usd")


def root_of(value):
    match = ROOT.fullmatch(value)
    return match[1] if match else ""


def amount_of(value):
    amount = Decimal(value.strip()) if value.strip() else None
    if amount is not None and not amount.is_finite():
        raise ValueError("non-finite amount")
    return amount


def procedure_of(value):
    value = " ".join(part for part in re.split(r"[ \t\r\n\u00a0]", value) if part)
    if value.startswith("Catálogo electrónico"):
        value = value.split(" en el convenio", 1)[0]
    return value or "Sin detalle"


def load_seed(path):
    exact, roots = {}, defaultdict(list)
    with Path(path).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            buyer = row["buyer_id"]
            if buyer in exact:
                raise ValueError("duplicate seed buyer_id")
            if root_of(buyer) != row["ruc_root"]:
                raise ValueError("seed root differs from validated buyer_id")
            exact[buyer] = row
            if row["ruc_root"]:
                roots[row["ruc_root"]].append(row)
    return exact, roots


def classification(buyer, exact, roots):
    root = root_of(buyer)
    candidates = roots.get(root, [])
    if not root or not candidates:
        return "Dudoso o sin clasificar", ""
    if len({row["entity_type"] for row in candidates}) != 1 or any(row["status"] != "aprobada" for row in candidates):
        return "Dudoso o sin clasificar", ""
    row = exact.get(buyer, candidates[0])
    kind = row["entity_type"]
    if kind in SECTOR and row["status"] == "aprobada":
        return "En el hecho", kind
    if kind == "fuera_de_alcance" and row["status"] == "aprobada":
        return "Fuera del gobierno central", ""
    return "Dudoso o sin clasificar", ""


def empty_stats():
    return [0, Decimal(0), Decimal(0), 0, 0]


def add(stats, awarded, estimated):
    stats[0] += 1
    for index, value in ((1, awarded), (2, estimated)):
        if value is not None:
            stats[index] += value
            stats[index + 2] += 1


def measure(base, seed, years=YEARS):
    """Return only aggregates; duplicate source keys stop the chain without deletion."""
    exact, roots = load_seed(seed)
    processes, tenders, awards = {}, {}, {}
    award_keys, tender_keys = set(), set()
    methods = {("Sin licitación", "Sin licitación")}
    for year in years:
        folders = sorted(Path(base).glob(f"sercop-portal-csv-{year}-*"))
        if len(folders) != 1:
            raise ValueError(f"expected exactly one source folder for {year}, found {len(folders)}")
        for table in ("releases", "tender", "awards"):
            with (folders[0] / f"{table}_{year}.csv").open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    ocid = row["ocid"]
                    if not ocid.strip():
                        raise ValueError("empty ocid")
                    if table == "releases":
                        if ocid in processes:
                            raise ValueError("duplicate release ocid across or within files; no rows removed")
                        if any(not row[field].strip() for field in ("buyer_id", "buyer_name", "date")):
                            raise ValueError("S-05: missing release key")
                        processes[ocid] = (row["buyer_id"], date.fromisoformat(row["date"][:10]))
                        continue
                    if table == "tender":
                        if ocid in tender_keys:
                            raise ValueError("duplicate tender ocid")
                        tender_keys.add(ocid)
                        amount, currency = amount_of(row["value_amount"]), row["value_currency"]
                    else:
                        key = (ocid, row["id"])
                        if key in award_keys:
                            raise ValueError("duplicate award key")
                        award_keys.add(key)
                        amount, currency = amount_of(row["amount"]), row["currency"]
                    if not (currency == "USD" or (amount is None and currency == "")):
                        continue
                    if amount is not None and amount < 0:
                        continue
                    if table == "tender":
                        method = row["procurementMethod"]
                        if method not in {"open", "selective", "direct", "limited"}:
                            raise ValueError("unexpected procurement method")
                        methods.add((method, procedure_of(row["procurementMethodDetails"])))
                        tenders[ocid] = amount
                    else:
                        count, total = awards.get(ocid, (0, None))
                        if amount is not None:
                            total = amount if total is None else total + amount
                        awards[ocid] = (count + 1, total)
    if (set(tenders) | set(awards)) - processes.keys():
        raise ValueError("tender or award without release")
    stats = defaultdict(empty_stats)
    entity_roots = set()
    for ocid, (buyer, moment) in processes.items():
        awarded = awards.get(ocid, (0, None))[1]
        estimated = tenders.get(ocid)
        for stage in ("Nacional descargado", "Sin ocid duplicados"):
            add(stats["cadena", stage, "", ""], awarded, estimated)
        if not 2021 <= moment.year <= 2025:
            reason = "Fuera de la ventana 2021-2025"
            add(stats["control_alcance", reason, "", moment.year], awarded, estimated)
            add(stats["exclusion", "Fuera de la ventana 2021-2025", "", ""], awarded, estimated)
            continue
        add(stats["cadena", "Ventana 2021-2025", "", ""], awarded, estimated)
        reason, kind = classification(buyer, exact, roots)
        add(stats["control_alcance", reason, "", moment.year], awarded, estimated)
        add(stats["alcance", reason, "", ""], awarded, estimated)
        if reason != "En el hecho":
            continue
        entity_roots.add(root_of(buyer))
        for stage in ("Sector clasificado", "FactContratacion"):
            add(stats["cadena", stage, "", ""], awarded, estimated)
        add(stats["tipo_anio", "FactContratacion", kind, moment.year], awarded, estimated)
    for stage in (
        "Nacional descargado",
        "Sin ocid duplicados",
        "Ventana 2021-2025",
        "Sector clasificado",
        "FactContratacion",
    ):
        stats.setdefault(("cadena", stage, "", ""), empty_stats())
    for reason in ("En el hecho", "Fuera del gobierno central", "Dudoso o sin clasificar"):
        stats.setdefault(("alcance", reason, "", ""), empty_stats())
    stats.setdefault(("exclusion", "Fuera de la ventana 2021-2025", "", ""), empty_stats())
    for kind in sorted(SECTOR):
        for year in YEARS:
            stats.setdefault(("tipo_anio", "FactContratacion", kind, year), empty_stats())
    for name, count in (("DimTiempo", 60), ("DimEntidad", len(entity_roots) + 1), ("DimMetodo", len(methods))):
        stats["dimension", name, "", ""][0] = count
    output = []
    for (group, stage, kind, year), values in stats.items():
        output.append(
            dict(
                zip(
                    FIELDS,
                    (
                        group,
                        stage,
                        kind,
                        year,
                        values[0],
                        str(values[1]) if values[3] else "",
                        str(values[2]) if values[4] else "",
                    ),
                    strict=True,
                )
            )
        )
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("derivados", type=Path)
    parser.add_argument("semilla", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; choose a new evidence filename")
    csv.field_size_limit(2**30)
    controls = measure(args.derivados, args.semilla)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(controls)
    print(f"{len(controls)} aggregate controls written")


if __name__ == "__main__":
    main()
