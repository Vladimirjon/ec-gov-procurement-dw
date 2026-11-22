"""Build the entity classification seed for DimEntidad (Hito 3, issue #68).

Crosswalk rule (ADR 0001, decisions 6 and 7), never by buyer name:
1. exact: the full ``buyer_id`` equals ``EC-RUC-{13 digits}`` of a catalog RUC;
2. root: ``buyer_id`` carries a unit suffix and its ``EC-RUC-{13}`` root is a catalog RUC;
3. otherwise the buyer is ``sin_clasificar`` (no catalog match or malformed id).

Classification comes from the MDEP catalog only (sector, UDAF group and the group's
head name); it is a team criterion, not a course rule. Every catalog group that does
not fit Presidencia, ministerio or instituto is ``dudosa`` and stays out of the
indicators until the leader approves it, through ``--overrides``. Standard library
only; outputs are never overwritten.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET
import zipfile


NS = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BUYER_REGEX = re.compile(r"^EC-RUC-(\d{13})(?:-(.+))?$")
SNAPSHOT = "catalogo_mdep_20260831"
SEED_COLUMNS = [
    "buyer_id",
    "ruc_root",
    "match_type",
    "catalog_udaf",
    "catalog_eod",
    "entity_name",
    "name_source",
    "entity_type",
    "proposed_type",
    "parent_entity",
    "source",
    "valid_from",
    "valid_to",
    "status",
    "note",
]
IN_SCOPE = ("presidencia", "ministerio", "instituto")
OVERRIDE_COLUMNS = {"scope", "key", "entity_type", "decided_on", "decision_note"}

# Catalog sector (code) -> (status, source). All of them are fuera_de_alcance.
SECTOR_OUT = {
    "112": ("propuesta", "criterio del equipo: educacion superior no es Presidencia, ministerio ni instituto"),
    "113": ("propuesta", "Hito 1: exclusion provisional de la seguridad social (ADR 0001, regla 6)"),
    "121": ("aprobada", "ADR 0001 decision 2: GAD fuera de alcance"),
    "122": ("aprobada", "ADR 0001 decision 2: GAD fuera de alcance"),
    "123": ("aprobada", "ADR 0001 decision 2: GAD fuera de alcance"),
    "211": ("aprobada", "ADR 0001 decision 2: empresas publicas fuera de alcance"),
    "212": ("aprobada", "ADR 0001 decision 2: empresas publicas y de los GAD fuera de alcance"),
    "221": ("propuesta", "criterio del equipo: entidad financiera publica no es Presidencia, ministerio ni instituto"),
    "311": ("propuesta", "criterio del equipo: sociedad anonima con participacion publica, no es del gobierno central"),
}
# Sector 111 heads that belong to other State functions (ADR 0001 decision 2), approved.
OTHER_FUNCTION_APPROVED = (
    "ASAMBLEA NACIONAL",
    "CONSEJO DE LA JUDICATURA",
    "CORTE CONSTITUCIONAL",
    "CONSEJO NACIONAL ELECTORAL",
    "TRIBUNAL CONTENCIOSO ELECTORAL",
    "FISCALIA GENERAL",
    "DEFENSORIA PUBLICA",
    "DEFENSORIA DEL PUEBLO",
    "CONTRALORIA GENERAL",
    "CONSEJO DE PARTICIPACION CIUDADANA",
)
# Other autonomous bodies outside the three categories: proposed out, not approved.
OTHER_FUNCTION_PROPOSED = (
    "SUPERINTENDENCIA",
    "PROCURADURIA GENERAL",
    "PARLAMENTO ANDINO",
    "SECRETARIA TECNICA DEL COMITE DE COORDINACION DE LA FUNCION DE TRANSPARENCIA",
)


@dataclass(frozen=True)
class CatalogRow:
    sector: str
    udaf: str
    eod: str
    name: str
    ruc: str


@dataclass
class Classification:
    entity_type: str
    status: str
    source: str
    proposed_type: str = ""
    note: str = ""


@dataclass
class SeedRow:
    buyer_id: str
    ruc_root: str
    match_type: str
    catalog_udaf: str = ""
    catalog_eod: str = ""
    entity_name: str = ""
    name_source: str = ""
    entity_type: str = "sin_clasificar"
    proposed_type: str = ""
    parent_entity: str = ""
    source: str = ""
    valid_from: str = ""
    valid_to: str = ""
    status: str = "dudosa"
    note: str = ""


CatalogEntry = tuple[Classification, str, str, str, str]


def norm(text: str) -> str:
    """Upper-case and collapse whitespace; used on catalog names only, never to join."""
    return " ".join(text.upper().split())


def parse_buyer_id(buyer_id: str) -> tuple[str, str] | None:
    """Return (ruc_root, suffix) when ``buyer_id`` is ``EC-RUC-{13}`` plus an optional suffix."""
    m = BUYER_REGEX.match(buyer_id.strip())
    if not m:
        return None
    return m.group(1), m.group(2) or ""


def normalize_ruc(raw: str) -> str | None:
    """Left-pad a catalog RUC to 13 digits (finding Q-E01); None if it is not numeric."""
    value = raw.strip()
    if not value.isdigit() or len(value) > 13:
        return None
    return value.zfill(13)


# --------------------------------------------------------------------------- catalog
def read_catalog(xlsx_path: Path) -> tuple[list[CatalogRow], dict[str, int]]:
    """Read the MDEP catalog (an .xlsx is a ZIP of XML) and drop title and footer rows (Q-E03)."""
    with zipfile.ZipFile(xlsx_path) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            tree = ET.fromstring(z.read("xl/sharedStrings.xml"))  # noqa: S314
            strings = ["".join(t.text or "" for t in si.findall(".//ns:t", NS)) for si in tree.findall(".//ns:si", NS)]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))  # noqa: S314
    parsed: list[dict[str, str]] = []
    for row in sheet.findall(".//ns:row", NS):
        cols: dict[str, str] = {}
        for c in row.findall("ns:c", NS):
            m = re.match(r"[A-Z]+", c.attrib.get("r", ""))
            if not m:
                continue
            v = c.find("ns:v", NS)
            kind = c.attrib.get("t")
            if kind == "inlineStr":
                cols[m.group(0)] = "".join(c.itertext())
            elif v is None or v.text is None:
                cols[m.group(0)] = ""
            elif kind == "s":
                cols[m.group(0)] = strings[int(v.text)]
            else:
                cols[m.group(0)] = v.text
        parsed.append(cols)
    header = next(
        (
            i
            for i, cols in enumerate(parsed)
            if cols.get("F", "").strip().upper() == "RUC" and "SECTOR" in norm(cols.get("A", ""))
        ),
        None,
    )
    if header is None:
        raise ValueError("catalog header row (SECTOR ... RUC) not found")
    rows: list[CatalogRow] = []
    stats = {"rows_loaded": 0, "rows_skipped": 0, "rows_padded_ruc": 0}
    for cols in parsed[header + 1 :]:
        ruc_raw = cols.get("F", "").strip()
        ruc = normalize_ruc(ruc_raw) if ruc_raw else None
        if ruc is None:
            stats["rows_skipped"] += 1  # title, footnote or non-numeric RUC rows
            continue
        if len(ruc_raw) < 13:
            stats["rows_padded_ruc"] += 1
        rows.append(
            CatalogRow(
                sector=cols.get("A", "").strip(),
                udaf=cols.get("C", "").strip(),
                eod=cols.get("D", "").strip(),
                name=" ".join(cols.get("E", "").split()),
                ruc=ruc,
            )
        )
        stats["rows_loaded"] += 1
    return rows, stats


def group_heads(rows: list[CatalogRow]) -> dict[tuple[str, str], CatalogRow]:
    """Head of each (sector, UDAF) group: the row with EOD 0 or 9999 (planta central)."""
    heads: dict[tuple[str, str], CatalogRow] = {}
    for row in rows:
        if row.eod in ("0", "9999"):
            heads.setdefault((row.sector, row.udaf), row)
    return heads


def classify_group(sector: str, head_name: str) -> Classification:
    """Classify a catalog group from its sector and head name (catalog text, never buyer.name)."""
    if sector in SECTOR_OUT:
        status, source = SECTOR_OUT[sector]
        return Classification("fuera_de_alcance", status, source)
    if sector != "111":
        return Classification(
            "sin_clasificar", "dudosa", "catalogo MDEP: sector sin regla", note=f"sector {sector} sin regla"
        )
    name = norm(head_name)
    if name.startswith(OTHER_FUNCTION_APPROVED):
        return Classification(
            "fuera_de_alcance", "aprobada", "ADR 0001 decision 2: otras funciones del Estado (nombre en catalogo)"
        )
    if name.startswith(OTHER_FUNCTION_PROPOSED):
        return Classification(
            "fuera_de_alcance",
            "propuesta",
            "criterio del equipo: organismo autonomo o internacional, no es Presidencia, ministerio ni instituto",
        )
    if name.startswith("PRESIDENCIA DE LA REPUBLICA"):
        return Classification("presidencia", "propuesta", "catalogo MDEP sector 111 + ADR 0001 decision 1")
    if name.startswith("MINISTERIO"):
        return Classification("ministerio", "propuesta", "catalogo MDEP sector 111 + ADR 0001 decision 1")
    if name.startswith("INSTITUTO"):
        return Classification(
            "instituto",
            "propuesta",
            "criterio del equipo: denominacion Instituto en el catalogo; dependencia ministerial no verificada",
        )
    return Classification(
        "sin_clasificar",
        "dudosa",
        "criterio del equipo: no es Presidencia, ministerio ni instituto por denominacion",
        proposed_type=recommend_doubtful(name),
        note="grupo del sector 111 fuera de las tres categorias",
    )


def recommend_doubtful(head_name: str) -> str:
    """Firm recommendation for a doubtful sector-111 group.

    Literal reading of ADR 0001 decision 1: only Presidencia, ministerios and the
    institutos that depend on them are in scope. Agencies, services, secretariats,
    councils, ports and similar bodies are none of the three, so the default is out.
    The Vicepresidencia and the Casa Militar Presidencial belong to the Presidency's
    own structure (Hito 1, executive function), so they are recommended in.
    """
    if head_name.startswith(("VICEPRESIDENCIA", "CASA MILITAR PRESIDENCIAL")):
        return "presidencia"
    return "fuera_de_alcance"


# --------------------------------------------------------------------------- crosswalk
def classify_catalog_root(rows: list[CatalogRow], heads: dict[tuple[str, str], CatalogRow]) -> CatalogEntry:
    """Classify one catalog RUC that may appear in several (UDAF, EOD) rows.

    Returns (classification, entity_name, parent_entity, udaf, eod). When the rows
    disagree on the outcome the root is ambiguous: sin_clasificar, dudosa. When they
    agree but sit under different parents, the parent is left empty. UDAF and EOD are
    kept only when the RUC belongs to a single group.
    """
    results = []
    for row in sorted(rows, key=lambda r: (r.sector, int(r.udaf) if r.udaf.isdigit() else 0, r.eod)):
        head = heads.get((row.sector, row.udaf))
        cls = classify_group(row.sector, head.name if head else row.name)
        parent = head.name if head is not None and head is not row else ""
        results.append((row, cls, parent))
    first_row, first_cls, first_parent = results[0]
    outcomes = {(cls.entity_type, cls.proposed_type, cls.status) for _, cls, _ in results}
    if len(outcomes) > 1:
        where = "; ".join(f"{r.sector}/{r.udaf}/{r.eod}" for r, _, _ in results)
        return (
            Classification(
                "sin_clasificar",
                "dudosa",
                "criterio del equipo: el RUC consta en varias filas del catalogo con clasificaciones distintas",
                note=f"RUC repetido con tipos distintos ({where})",
            ),
            first_row.name,
            "",
            "",
            "",
        )
    note = first_cls.note
    parent = first_parent
    if len({p for _, _, p in results}) > 1:
        parent = ""
        note = (note + "; " if note else "") + "RUC repetido en varios grupos del catalogo: padre no unico"
    cls = Classification(first_cls.entity_type, first_cls.status, first_cls.source, first_cls.proposed_type, note)
    # A RUC in several groups has no single UDAF: a group-level decision must not reach it.
    one_group = len({(r.sector, r.udaf) for r, _, _ in results}) == 1
    return cls, first_row.name, parent, first_row.udaf if one_group else "", first_row.eod if one_group else ""


def build_catalog_index(rows: list[CatalogRow]) -> dict[str, CatalogEntry]:
    heads = group_heads(rows)
    by_ruc: dict[str, list[CatalogRow]] = defaultdict(list)
    for row in rows:
        by_ruc[row.ruc].append(row)
    return {ruc: classify_catalog_root(group, heads) for ruc, group in by_ruc.items()}


def match_buyer(buyer_id: str, index: dict[str, CatalogEntry], fallback_names: dict[str, str]) -> SeedRow:
    """Apply the ADR 0001 crosswalk to one buyer_id. ``fallback_names`` maps root -> SERCOP name."""
    parsed = parse_buyer_id(buyer_id)
    if parsed is None:
        return SeedRow(
            buyer_id=buyer_id,
            ruc_root="",
            match_type="malformado",
            source="sin cruce: buyer_id sin la forma EC-RUC-{13}",
            note="buyer_id malformado (Q-E08)",
        )
    root, suffix = parsed
    entry = index.get(root)
    if entry is None:
        return SeedRow(
            buyer_id=buyer_id,
            ruc_root=root,
            match_type="sin_cruce",
            entity_name=fallback_names.get(root, ""),
            name_source="sercop_nombre_mas_frecuente",
            source="sin cruce: la raiz no consta en el catalogo MDEP",
            note="RUC fuera del catalogo (Q-E05)",
        )
    cls, name, parent, udaf, eod = entry
    return SeedRow(
        buyer_id=buyer_id,
        ruc_root=root,
        match_type="raiz" if suffix else "exacta",
        catalog_udaf=udaf,
        catalog_eod=eod,
        entity_name=name,
        name_source="catalogo",
        entity_type=cls.entity_type,
        proposed_type=cls.proposed_type,
        parent_entity=parent,
        source=f"{cls.source}; {SNAPSHOT}",
        status=cls.status,
        note=cls.note,
    )


def read_overrides(path: Path) -> list[dict[str, str]]:
    """Leader decisions: scope is ``ruc_root`` or ``udaf``; key is the root or the UDAF code."""
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = OVERRIDE_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"overrides file lacks columns: {sorted(missing)}")
        rows = list(reader)
    valid = {*IN_SCOPE, "fuera_de_alcance", "sin_clasificar"}
    for r in rows:
        if r["scope"] not in ("ruc_root", "udaf") or r["entity_type"] not in valid:
            raise ValueError(f"invalid override: {r}")
    return rows


def apply_overrides(seed: list[SeedRow], overrides: list[dict[str, str]]) -> int:
    """Apply leader decisions to matched rows (never to malformed ids); returns rows changed."""
    applied = 0
    for ov in overrides:
        for row in seed:
            if row.match_type == "malformado":
                continue
            hit = row.ruc_root == ov["key"] if ov["scope"] == "ruc_root" else row.catalog_udaf == ov["key"]
            if not hit:
                continue
            row.entity_type = ov["entity_type"]
            row.status = "aprobada"
            row.source = f"decision del lider {ov['decided_on']}"
            row.note = ov["decision_note"]
            applied += 1
    return applied


# --------------------------------------------------------------------------- SERCOP
def discover_years(derived_dir: Path) -> dict[int, tuple[Path, Path]]:
    found: dict[int, tuple[Path, Path]] = {}
    for sub in sorted(derived_dir.iterdir()):
        m = re.search(r"(20\d\d)", sub.name)
        if not sub.is_dir() or not m:
            continue
        year = int(m.group(1))
        rel, awd = sub / f"releases_{year}.csv", sub / f"awards_{year}.csv"
        if rel.exists() and awd.exists():
            found[year] = (rel, awd)
    return found


def read_awards(path: Path) -> dict[str, float]:
    """Sum of award amounts per ocid; ocids without a numeric amount are absent (empty is not zero)."""
    totals: dict[str, float] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            raw = r.get("amount", "").strip()
            if not raw:
                continue
            try:
                totals[r["ocid"]] = totals.get(r["ocid"], 0.0) + float(raw)
            except ValueError:
                continue
    return totals


def aggregate_sercop(
    years: dict[int, tuple[Path, Path]],
) -> tuple[dict[tuple[int, str], list[float]], dict[str, Counter]]:
    """Aggregate by (year of releases.date, buyer_id): processes, with award amount, amount.

    Also returns name counts per buyer_id, used only as a display fallback (Q-13).
    """
    agg: dict[tuple[int, str], list[float]] = defaultdict(lambda: [0, 0, 0.0])
    names: dict[str, Counter] = defaultdict(Counter)
    for _file_year, (rel, awd) in sorted(years.items()):
        amounts = read_awards(awd)
        with rel.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                date = r.get("date", "").strip()
                year = int(date[:4]) if date[:4].isdigit() else 0
                buyer = r["buyer_id"].strip()
                cell = agg[(year, buyer)]
                cell[0] += 1
                amount = amounts.get(r["ocid"])
                if amount is not None:
                    cell[1] += 1
                    cell[2] += amount
                name = " ".join(r.get("buyer_name", "").split())
                if name:
                    names[buyer][name] += 1
    return agg, names


def fallback_names_by_root(names: dict[str, Counter]) -> dict[str, str]:
    """One display name per RUC root: the most frequent SERCOP spelling (ties: alphabetical)."""
    per_root: dict[str, Counter] = defaultdict(Counter)
    for buyer, counter in names.items():
        parsed = parse_buyer_id(buyer)
        if parsed:
            per_root[parsed[0]].update(counter)
    return {root: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for root, c in per_root.items()}


# --------------------------------------------------------------------------- coverage
def segment(row: SeedRow) -> str:
    """Bucket used in the coverage tables."""
    if row.entity_type != "sin_clasificar":
        return row.entity_type
    if row.match_type == "malformado":
        return "sin_clasificar:malformado"
    if row.match_type == "sin_cruce":
        return "sin_clasificar:sin_cruce"
    return "sin_clasificar:dudosa"


def coverage(seed: list[SeedRow], agg: dict[tuple[int, str], list[float]]) -> dict[str, Any]:
    by_buyer = {row.buyer_id: row for row in seed}
    table: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0]))
    for (year, buyer), (procs, with_amount, amount) in agg.items():
        cell = table[year][segment(by_buyer[buyer])]
        cell[0] += procs
        cell[1] += with_amount
        cell[2] += amount
    grand: dict[str, list[float]] = defaultdict(lambda: [0, 0, 0.0])
    years: dict[str, Any] = {}
    for year in sorted(table):
        years[str(year)] = {
            seg: {"processes": int(v[0]), "processes_with_amount": int(v[1]), "awarded_amount": round(v[2], 2)}
            for seg, v in sorted(table[year].items())
        }
        if 2021 <= year <= 2025:
            for seg, v in table[year].items():
                for i in range(3):
                    grand[seg][i] += v[i]
    total = {
        seg: {"processes": int(v[0]), "processes_with_amount": int(v[1]), "awarded_amount": round(v[2], 2)}
        for seg, v in sorted(grand.items())
    }
    return {"years": years, "total_2021_2025": total}


def doubtful_cases(seed: list[SeedRow], agg: dict[tuple[int, str], list[float]]) -> list[dict[str, Any]]:
    """Ranked cases kept out of the indicators (business years 2021-2025), grouped per case.

    A case is a catalog UDAF group, an uncrossed RUC root or a malformed buyer_id.
    Weight is the sum of the case's share of processes and of awarded amount.
    """
    by_buyer = {row.buyer_id: row for row in seed}
    total_procs = sum(v[0] for (y, _), v in agg.items() if 2021 <= y <= 2025)
    total_amount = sum(v[2] for (y, _), v in agg.items() if 2021 <= y <= 2025)
    cases: dict[tuple[str, str], dict[str, Any]] = {}
    for (year, buyer), (procs, _with_amount, amount) in agg.items():
        row = by_buyer[buyer]
        if not 2021 <= year <= 2025 or row.entity_type != "sin_clasificar":
            continue
        if row.match_type == "malformado":
            key = ("malformado", row.buyer_id)
        elif row.match_type == "sin_cruce":
            key = ("sin_cruce", row.ruc_root)
        elif "RUC repetido con tipos distintos" in row.note:
            key = ("ruc_ambiguo", row.ruc_root)
        else:
            key = ("grupo_catalogo", row.catalog_udaf)
        case = cases.setdefault(
            key,
            {
                "kind": key[0],
                "key": key[1],
                "entity_name": row.parent_entity or row.entity_name,
                "name_source": row.name_source,
                "buyer_ids": set(),
                "processes": 0,
                "awarded_amount": 0.0,
                "proposed_type": row.proposed_type,
                "source": row.source,
                "note": row.note,
            },
        )
        case["buyer_ids"].add(buyer)
        case["processes"] += procs
        case["awarded_amount"] += amount
    ranked = []
    for case in cases.values():
        share = case["processes"] / total_procs + case["awarded_amount"] / total_amount
        case["weight_pct"] = round(100 * share, 4)
        case["buyer_ids"] = len(case["buyer_ids"])
        case["awarded_amount"] = round(case["awarded_amount"], 2)
        ranked.append(case)
    return sorted(ranked, key=lambda c: (-c["weight_pct"], c["key"]))


# --------------------------------------------------------------------------- main
def write_new(path: Path, writer) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        writer(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-xlsx", type=Path, required=True)
    parser.add_argument("--derived-dir", type=Path, required=True)
    parser.add_argument("--output-seed", type=Path, required=True)
    parser.add_argument("--output-coverage", type=Path, required=True)
    parser.add_argument("--output-cases", type=Path, required=True)
    parser.add_argument("--overrides", type=Path, default=None, help="leader decisions (second pass)")
    args = parser.parse_args(argv)

    for out in (args.output_seed, args.output_coverage, args.output_cases):
        if out.exists():
            print(f"ERROR: {out} already exists; refusing to overwrite", file=sys.stderr)
            return 1
    catalog_rows, catalog_stats = read_catalog(args.catalog_xlsx)
    index = build_catalog_index(catalog_rows)
    years = discover_years(args.derived_dir)
    if not years:
        print(f"ERROR: no year folders under {args.derived_dir}", file=sys.stderr)
        return 1
    agg, names = aggregate_sercop(years)
    fallback = fallback_names_by_root(names)
    seed = [match_buyer(b, index, fallback) for b in sorted({buyer for _, buyer in agg})]
    applied = apply_overrides(seed, read_overrides(args.overrides)) if args.overrides else 0
    cov = coverage(seed, agg)
    cases = doubtful_cases(seed, agg)

    def write_seed(f) -> None:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SEED_COLUMNS)
        for row in seed:
            w.writerow([getattr(row, c) for c in SEED_COLUMNS])

    def write_cov(f) -> None:
        json.dump(
            {
                "rule": "ADR 0001 decisions 6 and 7: exact buyer_id, then EC-RUC-{13} root, never buyer name",
                "business_date": "releases.date",
                "catalog": {"snapshot": SNAPSHOT, **catalog_stats, "distinct_rucs": len(index)},
                "seed_rows": len(seed),
                "overrides_applied_rows": applied,
                "status_counts": dict(Counter(r.status for r in seed)),
                "entity_type_counts": dict(Counter(r.entity_type for r in seed)),
                "match_type_counts": dict(Counter(r.match_type for r in seed)),
                "coverage": cov,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    columns = [
        "kind",
        "key",
        "entity_name",
        "name_source",
        "buyer_ids",
        "processes",
        "awarded_amount",
        "weight_pct",
        "proposed_type",
        "source",
        "note",
    ]

    def write_cases(f) -> None:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["rank", *columns])
        for i, case in enumerate(cases, 1):
            w.writerow([i, *[case[c] for c in columns]])

    write_new(args.output_seed, write_seed)
    write_new(args.output_coverage, write_cov)
    write_new(args.output_cases, write_cases)
    print(f"seed rows: {len(seed)}; doubtful cases: {len(cases)}; overrides applied: {applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
