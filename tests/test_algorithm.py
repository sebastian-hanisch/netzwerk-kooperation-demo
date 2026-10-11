"""Einheiten des Kerns an Handbeispielen: Graphen, Auszahlung, Fitness, ein Ersetzungsschritt, exakte Fixierung, kritisches b/c."""

import pytest

import nwk_algorithm as A
import nwk_constants as C


def test_circulant_ring_neighbors_by_hand():
    assert A.circulant(6, 2)[0] == [5, 1]
    assert sorted(A.circulant(8, 4)[0]) == [1, 2, 6, 7]


def test_torus_neighborhoods_are_symmetric_and_have_the_right_size():
    for neighbors in (4, 8):
        nb = A.torus(5, neighbors)
        assert all(len(row) == neighbors and len(set(row)) == neighbors for row in nb)
        assert all(i in nb[j] for i in range(25) for j in nb[i])


def test_payoff_by_hand_on_a_ring_of_four():
    nb = A.circulant(4, 2)
    s = [1, 0, 0, 1]
    # Knoten 0: Nachbarn 3 (kooperiert) und 1 (nicht): b·1 − 1·2·1 = b − 2
    assert A.payoff(nb, s, 0, 5.0) == pytest.approx(3.0)
    # Knoten 1: Nachbarn 0 und 2: b·1 − 0 = b
    assert A.payoff(nb, s, 1, 5.0) == pytest.approx(5.0)
    # Knoten 2: Nachbarn 1 und 3: b·1
    assert A.payoff(nb, s, 2, 5.0) == pytest.approx(5.0)


def test_fitness_is_linear_and_floored_at_zero():
    assert A.fitness(2.0, 0.1) == pytest.approx(1.2)
    assert A.fitness(-20.0, 0.1) == 0.0


def test_death_birth_step_by_hand():
    nb = A.circulant(4, 2)
    s = [1, 0, 0, 0]
    # Knoten 1 stirbt, Bewerber 0 (Kooperierender, Auszahlung −2) und 2 (Auszahlung 0): Fitness 0,8 und 1,0
    assert A.update_step(nb, s, 5.0, 0.1, "DB", 1, 0.3) == (1, 1)         # 0,3·1,8 = 0,54 ≤ 0,8: Knoten 0
    assert A.update_step(nb, s, 5.0, 0.1, "DB", 1, 0.5) == (1, 0)         # 0,9 > 0,8: Knoten 2


def test_imitation_includes_the_player_itself():
    nb = A.circulant(4, 2)
    s = [1, 0, 0, 0]
    # Knoten 1 mit Bewerbern 0, 2 und sich selbst (1): Auszahlungen −2, 0, 0 + b·1 = 5 (Knoten 1 hat Nachbar 0 kooperierend)
    node, strat = A.update_step(nb, s, 5.0, 0.1, "IM", 1, 0.99)
    assert node == 1 and strat == 0


def test_birth_death_step_by_hand():
    nb = A.circulant(4, 2)
    s = [1, 0, 0, 0]
    # Auszahlungen: Knoten 0: −2, Knoten 1: 5, Knoten 2: 0, Knoten 3: 5; Fitness 0,8 / 1,5 / 1,0 / 1,5 (w = 0,1)
    node, strat = A.step_birth_death(nb, s, 5.0, 0.1, 0.05, 0.0)        # 0,05·4,8 = 0,24 ≤ 0,8: Knoten 0 reproduziert, ersetzt Nachbar 3 (Index 0 von nb[0] = [3, 1])
    assert (node, strat) == (3, 1)


def test_neutral_selection_gives_one_over_n_exactly():
    for n, k in ((4, 2), (6, 2), (6, 4)):
        assert A.exact_fixation(A.circulant(n, k), 5.0, 0.0, "DB") == pytest.approx(1 / n, abs=1e-12)


def test_two_players_under_death_birth_fixate_with_probability_one_half():
    # der sterbende Spieler hat nur einen Bewerber: Der Ausgang hängt nicht von der Fitness ab
    assert A.exact_fixation([[1], [0]], 7.0, 0.1, "DB") == pytest.approx(0.5)


def test_well_mixed_population_never_favours_cooperation():
    nb = A.complete_graph(6)
    for br in (2.0, 10.0, 50.0):
        assert A.exact_fixation(nb, br, C.WEAK_W, "DB") < 1 / 6


def test_critical_ratio_matches_the_closed_formula_on_a_ring():
    assert A.critical_ratio(A.circulant(6, 2), "DB") == pytest.approx(A.critical_formula(6, 2), rel=0.01)
    assert A.critical_formula(6, 2) == pytest.approx(4.0)
    assert A.critical_formula(8, 2) == pytest.approx(3.0)
    assert A.critical_formula(4, 4) is None


def test_birth_death_has_no_critical_ratio():
    assert A.critical_ratio(A.circulant(6, 2), "BD", hi=60.0, iterations=12) is None


def test_simulation_is_deterministic_for_a_seed_and_stops_when_absorbed():
    nb = A.torus(6, 4)
    a = A.simulate(nb, 8.0, 0.1, "DB", 3, 40)
    b = A.simulate(nb, 8.0, 0.1, "DB", 3, 40)
    assert a["trace"] == b["trace"]
    absorbed = A.simulate(nb, 8.0, 0.1, "DB", 0, 40, initial=[1] * 36)
    assert absorbed["share"] == 1.0 and len(absorbed["trace"]) == 2
