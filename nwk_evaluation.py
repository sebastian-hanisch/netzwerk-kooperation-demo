"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern und die vorgerechnete Tabelle."""

import json
import os
import statistics
from dataclasses import dataclass
from functools import lru_cache

import nwk_algorithm as A
import nwk_constants as C

SWEEPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nwk_sweeps.json")


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    rule: str = C.DEFAULT_RULE
    neighbors: int = C.DEFAULT_NEIGHBORS
    br: float = C.DEFAULT_BR
    w: float = C.DEFAULT_W
    gen: int = C.DEFAULT_GEN
    seed: int = C.DEFAULT_SEED
    exact_n: int = C.DEFAULT_EXACT_N
    exact_k: int = C.DEFAULT_EXACT_K


@dataclass(frozen=True)
class Analysis:
    trace: tuple[float, ...]
    grid: tuple[tuple[int, ...], ...]
    share: float
    absorbed: bool
    start_share: float


def analyse(settings: Settings) -> Analysis:
    nb = A.torus(C.LATTICE_SIZE, settings.neighbors)
    r = A.simulate(nb, settings.br, settings.w, settings.rule, settings.seed, settings.gen)
    size = C.LATTICE_SIZE
    grid = tuple(tuple(r["final"][i * size + j] for j in range(size)) for i in range(size))
    return Analysis(tuple(r["trace"]), grid, r["share"], r["share"] in (0.0, 1.0), r["trace"][0])


def exact_curve(n: int, k: int, rule: str, w: float = C.WEAK_W) -> list[dict]:
    """Fixierungswahrscheinlichkeit einer einzelnen Kooperierenden, geteilt durch den neutralen Wert 1/n, über b/c."""
    nb = A.circulant(n, k)
    return [{"br": br, "ratio": A.exact_fixation(nb, br, w, rule) * n} for br in C.BC_GRID]


def threshold_text(rule: str, k: int) -> str:
    """Die Schwelle aus der Literatur (große reguläre Graphen, schwache Auswahl)."""
    if rule == "DB":
        return f"b/c > k = {k}"
    if rule == "IM":
        return f"b/c > k + 2 = {k + 2}"
    return "nie"


# --- Vorgerechnete Tabelle ---------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_sweeps() -> dict | None:
    try:
        with open(SWEEPS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def exact_row(n: int, k: int, rule: str) -> dict | None:
    data = load_sweeps()
    if data is None:
        return None
    for r in data["exact"]:
        if r["n"] == n and r["k"] == k and r["rule"] == rule:
            return r
    return None


def spatial_series(rule: str, neighbors: int) -> list[dict]:
    """Je b/c: mittlerer Endanteil der Kooperierenden über die Seeds, Anteil der Läufe mit Mehrheit Kooperierender und Anzahl Läufe."""
    data = load_sweeps()
    if data is None:
        return []
    rows: dict[float, list[float]] = {}
    for r in data["spatial"]:
        if r["rule"] == rule and r["neighbors"] == neighbors:
            rows.setdefault(r["br"], []).append(r["share"])
    return [{"br": br, "mean": statistics.fmean(v), "median": statistics.median(v), "majority": sum(x > 0.5 for x in v), "n": len(v), "values": v} for br, v in sorted(rows.items())]


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    label = C.RULE_LABELS[settings.rule]
    k = settings.neighbors
    thr = threshold_text(settings.rule, k)
    head = (f"{label}, {k} Nachbarn, b/c = {fmt(settings.br, 1)}: Nach {len(an.trace) - 1} Generationen sind {fmt(an.share * 100, 0)} % der Spieler Kooperierende "
            f"(Start {fmt(an.start_share * 100, 0)} %). Schwelle der Theorie für große Netze und schwache Auswahl: {thr}.")
    if an.share >= 0.5:
        return "success", head + " Die Kooperation hält sich."
    return "warning", head + " Die Defektion setzt sich durch."
