"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen aus der vorgerechneten Tabelle nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import nwk_algorithm as A
import nwk_constants as C
import nwk_evaluation as E


def series(rule, k):
    return {round(s["br"]): s for s in E.spatial_series(rule, k)}


def test_table_has_every_exact_row_and_twenty_seeds_per_spatial_point():
    data = E.load_sweeps()
    assert len(data["exact"]) == 18
    assert len(data["spatial"]) == 3 * 2 * len(C.SWEEP_BRS) * 20
    assert all(s["n"] == 20 for rule in C.RULE_KEYS for k in C.NEIGHBOR_KEYS for s in E.spatial_series(rule, k))


def test_critical_ratios_on_small_rings_match_the_formula():
    for n, k, crit, formula in ((6, 2, 4.003, 4.0), (8, 2, 3.001, 3.0), (10, 2, 2.667, 2.667), (10, 4, 16.24, 16.0)):
        row = E.exact_row(n, k, "DB")
        assert row["critical"] == pytest.approx(crit, abs=0.005)
        assert row["formula"] == pytest.approx(formula, abs=0.005)
        assert row["critical"] == pytest.approx(row["formula"], rel=0.02)


def test_imitation_critical_ratios_and_cases_without_a_threshold():
    assert E.exact_row(8, 2, "IM")["critical"] == pytest.approx(13.11, abs=0.01)
    assert E.exact_row(10, 2, "IM")["critical"] == pytest.approx(8.53, abs=0.01)
    assert E.exact_row(6, 2, "IM")["critical"] is None
    for n, k in ((6, 2), (8, 2), (10, 2), (10, 4)):
        assert E.exact_row(n, k, "BD")["critical"] is None


def test_thresholds_shrink_with_the_ring_size():
    values = [E.exact_row(n, 2, "DB")["critical"] for n in (6, 8, 10)]
    assert values == sorted(values, reverse=True) and values[-1] > 2.0
    im = [E.exact_row(n, 2, "IM")["critical"] for n in (8, 10)]
    assert im[0] > im[1] > 4.0


def test_spatial_death_birth_on_four_neighbours():
    s = series("DB", 4)
    assert s[2]["mean"] == pytest.approx(0.0, abs=0.005) and s[2]["majority"] == 0
    assert s[3]["mean"] == pytest.approx(0.11, abs=0.01)
    assert s[4]["mean"] == pytest.approx(0.43, abs=0.01) and s[4]["majority"] == 9
    assert s[5]["mean"] == pytest.approx(0.79, abs=0.01) and s[5]["majority"] == 19
    assert s[8]["mean"] > 0.95 and s[12]["majority"] == 20


def test_spatial_imitation_needs_more_than_death_birth():
    db, im = series("DB", 4), series("IM", 4)
    assert im[4]["mean"] == pytest.approx(0.04, abs=0.01) and im[5]["majority"] == 0
    assert im[6]["mean"] == pytest.approx(0.32, abs=0.01) and im[6]["majority"] == 5
    assert im[8]["majority"] == 18
    assert all(db[b]["mean"] > im[b]["mean"] for b in (4, 5, 6, 8))


def test_spatial_birth_death_never_carries_cooperation():
    for k in C.NEIGHBOR_KEYS:
        assert all(s["mean"] == 0.0 and s["majority"] == 0 for s in E.spatial_series("BD", k))


def test_eight_neighbours_need_a_higher_benefit_than_four():
    four, eight = series("DB", 4), series("DB", 8)
    assert eight[5]["mean"] == pytest.approx(0.0, abs=0.005) and four[5]["majority"] == 19
    assert eight[8]["mean"] == pytest.approx(0.33, abs=0.01) and eight[8]["majority"] == 5
    assert eight[10]["majority"] == 17 and eight[12]["majority"] == 19


def test_preset_stories_hold_for_the_default_seed():
    def share(name):
        p = C.PRESETS[name]
        return E.analyse(E.Settings(p["rule"], p["neighbors"], p["br"], p["w"], p["gen"], p["seed"])).share

    assert share("Death-Birth, 4 Nachbarn, b/c = 5") > 0.5
    assert share("Death-Birth, 4 Nachbarn, b/c = 3") < 0.5
    assert share("Imitation, 4 Nachbarn, b/c = 5") < 0.5
    assert share("Birth-Death, 4 Nachbarn, b/c = 10") < 0.5
    assert share("Death-Birth, 8 Nachbarn, b/c = 5") < 0.5


def test_a_live_rerun_of_one_point_matches_the_table():
    """Stichprobe: Death-Birth, 4 Nachbarn, b/c = 5, vier Seeds neu gerechnet; Band, weil Plattform-Ulps einen Lauf kippen könnten."""
    nb = A.torus(C.LATTICE_SIZE, 4)
    live = [A.simulate(nb, 5.0, C.SWEEP_W, "DB", seed, C.SWEEP_GEN)["share"] for seed in C.SWEEP_SEEDS[:4]]
    table = [r["share"] for r in E.load_sweeps()["spatial"] if r["rule"] == "DB" and r["neighbors"] == 4 and r["br"] == 5.0 and r["seed"] in C.SWEEP_SEEDS[:4]]
    assert sum(live) / 4 == pytest.approx(sum(table) / 4, abs=0.15)
