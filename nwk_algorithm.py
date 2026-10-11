"""Kern: Spenderspiel auf regulären Graphen, exakte Fixierungswahrscheinlichkeit einer einzelnen Kooperierenden und räumliche Simulation.

Fitness eines Spielers: 1 + w·π, nach unten bei 0 begrenzt (π = Summe über die Nachbarn: erhaltener Nutzen b je kooperierendem Nachbarn minus
Kosten c je Nachbar, wenn der Spieler selbst kooperiert).
"""

import random

import numpy as np

import nwk_constants as C


# --- Graphen ------------------------------------------------------------------------------------------------------------------------------------

def circulant(n: int, k: int) -> list[list[int]]:
    """Ring mit k Nachbarn je Knoten (k/2 auf jeder Seite)."""
    return [[(i + d) % n for d in range(-(k // 2), k // 2 + 1) if d != 0] for i in range(n)]


def complete_graph(n: int) -> list[list[int]]:
    return [[j for j in range(n) if j != i] for i in range(n)]


def torus(size: int, neighbors: int = 4) -> list[list[int]]:
    """Quadratisches Gitter mit Randanschluss; 4 Nachbarn (Von Neumann) oder 8 (Moore)."""
    nb = []
    for i in range(size):
        for j in range(size):
            cells = [((i + 1) % size, j), ((i - 1) % size, j), (i, (j + 1) % size), (i, (j - 1) % size)]
            if neighbors == 8:
                cells += [((i + 1) % size, (j + 1) % size), ((i - 1) % size, (j - 1) % size), ((i + 1) % size, (j - 1) % size), ((i - 1) % size, (j + 1) % size)]
            nb.append([a * size + b for a, b in cells])
    return nb


# --- Spiel ---------------------------------------------------------------------------------------------------------------------------------------

def payoff(nb: list[list[int]], s, j: int, br: float) -> float:
    """Auszahlung von Knoten j bei Nutzen b = br (Kosten c = 1): b je kooperierendem Nachbarn minus c je Nachbar, wenn j selbst kooperiert."""
    return br * sum(s[l] for l in nb[j]) - C.COST * len(nb[j]) * s[j]


def fitness(pay: float, w: float) -> float:
    return max(0.0, 1.0 + w * pay)


def update_step(nb, s, br: float, w: float, rule: str, i: int, r: float) -> tuple[int, int]:
    """Death-Birth oder Imitation mit vorgegebenem Zufall: Knoten i wird neu besetzt, r in [0,1) wählt unter den Bewerbern im Verhältnis zur Fitness.
    Gibt (Zielknoten, übernommene Strategie) zurück.
    """
    if rule == "BD":
        raise ValueError("Birth-Death braucht step_birth_death")
    cand = nb[i] if rule == "DB" else nb[i] + [i]
    fs = [fitness(payoff(nb, s, j, br), w) for j in cand]
    tot = sum(fs)
    if tot <= 0.0:
        return i, s[cand[min(int(r * len(cand)), len(cand) - 1)]]
    acc, x = 0.0, r * tot
    for c, f in zip(cand, fs):
        acc += f
        if x <= acc:
            return i, s[c]
    return i, s[cand[-1]]


def step_birth_death(nb, s, br: float, w: float, r: float, pick: float) -> tuple[int, int]:
    """Birth-Death: Spieler j wird mit Wahrscheinlichkeit ∝ Fitness gewählt (r), ersetzt den Nachbarn mit Index int(pick·k)."""
    n = len(nb)
    fs = [fitness(payoff(nb, s, j, br), w) for j in range(n)]
    tot = sum(fs)
    x, acc, j = r * tot, 0.0, n - 1
    for c, f in enumerate(fs):
        acc += f
        if x <= acc:
            j = c
            break
    target = nb[j][min(int(pick * len(nb[j])), len(nb[j]) - 1)]
    return target, s[j]


# --- Exakte Fixierungswahrscheinlichkeit -------------------------------------------------------------------------------------------------------

def _transitions(nb, s, st: int, br: float, w: float, rule: str) -> dict[int, float]:
    n = len(nb)
    fit = [fitness(payoff(nb, s, j, br), w) for j in range(n)]
    probs: dict[int, float] = {}

    def add(node, strategy, p):
        t = (st & ~(1 << node)) | (strategy << node)
        probs[t] = probs.get(t, 0.0) + p

    if rule in ("DB", "IM"):
        for i in range(n):
            cand = nb[i] if rule == "DB" else nb[i] + [i]
            tot = sum(fit[j] for j in cand)
            for j in cand:
                add(i, s[j], (1.0 / n) * fit[j] / tot)
    else:
        tot = sum(fit)
        for j in range(n):
            for i in nb[j]:
                add(i, s[j], (fit[j] / tot) / len(nb[j]))
    return probs


def exact_fixation(nb, br: float, w: float, rule: str = "DB") -> float:
    """Wahrscheinlichkeit, dass eine einzelne Kooperierende (gleichverteilt unter den Knoten) die ganze Population ersetzt.
    Löst das lineare Gleichungssystem über alle 2^n Zustände (nur für kleine n)."""
    n = len(nb)
    states = 1 << n
    a = np.zeros((states, states))
    rhs = np.zeros(states)
    for st in range(states):
        a[st, st] = 1.0
        if st == 0:
            continue
        if st == states - 1:
            rhs[st] = 1.0
            continue
        s = [(st >> i) & 1 for i in range(n)]
        for t, p in _transitions(nb, s, st, br, w, rule).items():
            a[st, t] -= p
    h = np.linalg.solve(a, rhs)
    return float(np.mean([h[1 << i] for i in range(n)]))


def critical_ratio(nb, rule: str = "DB", w: float = C.WEAK_W, lo: float = 0.5, hi: float = 60.0, iterations: int = 30) -> float | None:
    """Kleinstes b/c, ab dem die Fixierungswahrscheinlichkeit über 1/n liegt (Bisektion). None, wenn sie bis `hi` nie darüber liegt."""
    n = len(nb)

    def excess(r):
        return exact_fixation(nb, r, w, rule) - 1.0 / n

    if excess(lo) > 0:
        return lo
    if excess(hi) < 0:
        return None
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if excess(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def critical_formula(n: int, k: int) -> float | None:
    """Geschlossene Formel für Death-Birth auf regulären Graphen bei schwacher Auswahl: (N − 2) / (N/k − 2); nur für N/k > 2 sinnvoll."""
    if n / k <= 2:
        return None
    return (n - 2) / (n / k - 2)


# --- Räumliche Simulation -----------------------------------------------------------------------------------------------------------------------

def simulate(nb, br: float, w: float, rule: str, seed: int, generations: int = C.DEFAULT_GEN, start_share: float = C.START_SHARE,
             initial: list[int] | None = None) -> dict:
    """Asynchrone Aktualisierung: je Generation n Schritte. Gibt den Verlauf des Kooperationsanteils je Generation und den Endzustand zurück."""
    rng = random.Random(seed)
    n = len(nb)
    s = list(initial) if initial is not None else [1 if rng.random() < start_share else 0 for _ in range(n)]
    trace = [sum(s) / n]
    for _ in range(generations):
        for _ in range(n):
            if rule == "BD":
                node, strat = step_birth_death(nb, s, br, w, rng.random(), rng.random())
            else:
                node, strat = update_step(nb, s, br, w, rule, rng.randrange(n), rng.random())
            s[node] = strat
            if sum(s) in (0, n):
                break
        trace.append(sum(s) / n)
        if trace[-1] in (0.0, 1.0):
            break
    return {"trace": trace, "final": s, "share": trace[-1]}


def single_cooperator_fixation_rate(nb, br: float, w: float, rule: str, runs: int, seed: int = 0, max_steps: int = 20000) -> float:
    """Monte-Carlo-Schätzung der Fixierungswahrscheinlichkeit einer einzelnen, zufällig platzierten Kooperierenden (unabhängig vom linearen System)."""
    rng = random.Random(seed)
    n = len(nb)
    wins = 0
    for _ in range(runs):
        s = [0] * n
        s[rng.randrange(n)] = 1
        for _ in range(max_steps):
            if rule == "BD":
                node, strat = step_birth_death(nb, s, br, w, rng.random(), rng.random())
            else:
                node, strat = update_step(nb, s, br, w, rule, rng.randrange(n), rng.random())
            s[node] = strat
            total = sum(s)
            if total == 0:
                break
            if total == n:
                wins += 1
                break
    return wins / runs
