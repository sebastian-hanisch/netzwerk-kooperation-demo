"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzen und Einrasten."""

import nwk_constants as C
import nwk_evaluation as ev
import nwk_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["rule"] in C.RULE_KEYS and p["neighbors"] in C.NEIGHBOR_KEYS, name
        assert C.BR_MIN <= p["br"] <= C.BR_MAX and C.W_MIN <= p["w"] <= C.W_MAX and C.GEN_MIN <= p["gen"] <= C.GEN_MAX, name
        assert C.SEED_MIN <= p["seed"] <= C.SEED_MAX, name


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) <= set(P.SETTING_SPECS)


def test_default_settings_equal_the_first_preset_where_they_overlap():
    first = next(iter(C.PRESETS.values()))
    d = ev.Settings()
    assert (d.rule, d.neighbors, d.br, d.w, d.gen, d.seed) == (first["rule"], first["neighbors"], first["br"], first["w"], first["gen"], first["seed"])


def test_clamp_limits_and_snaps():
    spec = P.SETTING_SPECS
    assert P.clamp(spec["br_slider"], 99.0) == C.BR_MAX and P.clamp(spec["br_slider"], 0.0) == C.BR_MIN
    assert P.clamp(spec["br_slider"], 5.2) == 5.0
    assert P.clamp(spec["gen_slider"], 63) == 60
    assert P.clamp(spec["rule_select"], "XX") == C.DEFAULT_RULE and P.clamp(spec["neighbors_select"], 5) == C.DEFAULT_NEIGHBORS
