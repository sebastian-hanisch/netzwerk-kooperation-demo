"""Permalink (Begrenzen und Einrasten), Presets und Zufalls-Seed-Button."""

import random
from dataclasses import dataclass

import streamlit as st

import nwk_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    step: float | None = None
    choices: tuple | None = None


SETTING_SPECS = {
    "rule_select": SettingSpec("rule", str, C.DEFAULT_RULE, choices=C.RULE_KEYS),
    "neighbors_select": SettingSpec("k", int, C.DEFAULT_NEIGHBORS, choices=C.NEIGHBOR_KEYS),
    "br_slider": SettingSpec("br", float, C.DEFAULT_BR, C.BR_MIN, C.BR_MAX, C.BR_STEP),
    "w_slider": SettingSpec("w", float, C.DEFAULT_W, C.W_MIN, C.W_MAX, C.W_STEP),
    "gen_slider": SettingSpec("gen", int, C.DEFAULT_GEN, C.GEN_MIN, C.GEN_MAX, C.GEN_STEP),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, C.SEED_MIN, C.SEED_MAX),
    "exact_n_select": SettingSpec("n", int, C.DEFAULT_EXACT_N, choices=C.EXACT_N_OPTIONS),
    "exact_k_select": SettingSpec("ek", int, C.DEFAULT_EXACT_K, choices=C.EXACT_K_OPTIONS),
}
PRESET_KEYS = {"rule": "rule_select", "neighbors": "neighbors_select", "br": "br_slider", "w": "w_slider", "gen": "gen_slider", "seed": "seed_input"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp(spec: SettingSpec, value):
    """Begrenzt auf die Reglergrenzen und rastet auf den Reglerschritt ein; unbekannte Auswahlwerte werden zur Voreinstellung."""
    if spec.choices is not None:
        return value if value in spec.choices else spec.default
    value = min(spec.hi, max(spec.lo, value))
    if spec.step:
        value = spec.lo + round((value - spec.lo) / spec.step) * spec.step
        value = min(spec.hi, max(spec.lo, value))
    return round(value, 2) if spec.caster is float else int(round(value))


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param not in qp:
            continue
        raw = qp[spec.url_param]
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        try:
            value = spec.caster(raw)
        except (ValueError, TypeError):
            continue
        st.session_state[state_key] = clamp(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]


def randomize_seed():
    st.session_state["seed_input"] = random.randint(C.SEED_MIN, C.SEED_MAX)
