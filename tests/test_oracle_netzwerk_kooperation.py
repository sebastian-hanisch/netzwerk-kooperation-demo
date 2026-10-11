"""Orakel-Tests: jeder Kernbaustein gegen einen unabhängigen Rechenweg.

1. Exakte Fixierungswahrscheinlichkeit (lineares System) gegen eine Monte-Carlo-Simulation der Aktualisierungsschritte (agentenbasiert).
2. Dieselbe Wahrscheinlichkeit gegen eine Wertiteration der Markov-Kette (h ← P·h bis zur Konvergenz), also ohne Gleichungslöser.
3. Kritisches b/c gegen die geschlossene Formel (N − 2)/(N/k − 2) für Death-Birth auf regulären Graphen.
4. Die Übergangswahrscheinlichkeiten gegen eine Zählung über alle möglichen Zufallsentscheidungen (Aufzählung statt Formel).
"""

import itertools

import numpy as np
import pytest

import nwk_algorithm as A


@pytest.mark.parametrize("rule", ["DB", "IM", "BD"])
def test_exact_fixation_against_monte_carlo(rule):
    nb = A.circulant(6, 2)
    exact = A.exact_fixation(nb, 6.0, 0.1, rule)
    mc = A.single_cooperator_fixation_rate(nb, 6.0, 0.1, rule, runs=4000, seed=5)
    assert mc == pytest.approx(exact, abs=0.025)


def test_exact_fixation_against_value_iteration_of_the_chain():
    nb = A.circulant(6, 2)
    n = len(nb)
    states = 1 << n
    p = np.zeros((states, states))
    for st in range(states):
        if st in (0, states - 1):
            p[st, st] = 1.0
            continue
        s = [(st >> i) & 1 for i in range(n)]
        for t, prob in A._transitions(nb, s, st, 5.0, 0.1, "DB").items():
            p[st, t] += prob
    assert np.allclose(p.sum(axis=1), 1.0)
    h = np.zeros(states)
    h[states - 1] = 1.0
    for _ in range(20000):
        h = p @ h
    iterated = float(np.mean([h[1 << i] for i in range(n)]))
    assert iterated == pytest.approx(A.exact_fixation(nb, 5.0, 0.1, "DB"), abs=1e-9)


@pytest.mark.parametrize("n,k", [(6, 2), (8, 2)])
def test_critical_ratio_against_the_closed_formula(n, k):
    assert A.critical_ratio(A.circulant(n, k), "DB") == pytest.approx(A.critical_formula(n, k), rel=0.01)


def test_death_birth_transitions_against_enumeration_of_all_random_choices():
    """Alle Möglichkeiten (zu ersetzender Knoten, gewählter Bewerber) einzeln aufzählen und die Wahrscheinlichkeiten addieren."""
    nb = A.circulant(5, 2)
    s = [1, 0, 1, 1, 0]
    br, w = 4.0, 0.1
    st = sum(v << i for i, v in enumerate(s))
    counted: dict[int, float] = {}
    for i in range(5):
        fits = {j: A.fitness(A.payoff(nb, s, j, br), w) for j in nb[i]}
        tot = sum(fits.values())
        for j, f in fits.items():
            t = (st & ~(1 << i)) | (s[j] << i)
            counted[t] = counted.get(t, 0.0) + (1 / 5) * f / tot
    fast = A._transitions(nb, s, st, br, w, "DB")
    assert set(fast) == set(counted)
    assert all(fast[t] == pytest.approx(counted[t]) for t in counted)
    assert sum(fast.values()) == pytest.approx(1.0)


def test_all_rules_give_a_probability_distribution_from_every_mixed_state():
    nb = A.circulant(6, 4)
    for st in itertools.islice(range(1, (1 << 6) - 1), 0, None, 5):
        s = [(st >> i) & 1 for i in range(6)]
        for rule in ("DB", "IM", "BD"):
            probs = A._transitions(nb, s, st, 3.0, 0.1, rule)
            assert sum(probs.values()) == pytest.approx(1.0)
