"""End-to-end Smoke-Test via Streamlits AppTest: lädt app.py mit den Standardeinstellungen, klickt jeden Preset-Button, fährt jeden Regler an Minimum und Maximum
und prüft, dass kein Python-Fehler auftritt."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = 240
AUTOPLAY_MARKER = "▶"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


def test_every_rule_and_ring_size_renders_without_exception():
    for rule in ("DB", "IM", "BD"):
        for n, k in ((6, 2), (6, 4), (8, 2), (8, 4)):
            at = AppTest.from_file(APP_PATH)
            at.query_params["rule"] = rule
            at.query_params["n"] = str(n)
            at.query_params["ek"] = str(k)
            at.run(timeout=TIMEOUT)
            assert not at.exception, (rule, n, k, [str(e) for e in at.exception])


def test_permalink_is_clamped_and_snapped():
    at = AppTest.from_file(APP_PATH)
    at.query_params["br"] = "99"
    at.query_params["w"] = "-1"
    at.query_params["gen"] = "63"
    at.query_params["rule"] = "XX"
    at.query_params["k"] = "5"
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["br_slider"] == 12.0
    assert at.session_state["w_slider"] == 0.01
    assert at.session_state["gen_slider"] == 60
    assert at.session_state["rule_select"] == "DB"
    assert at.session_state["neighbors_select"] == 4


def test_the_page_explains_the_rules_and_the_game():
    text = " ".join(m.value for m in _fresh_app().markdown)
    for word in ("Spenderspiel", "Death-Birth", "Imitation", "Birth-Death", "Fitness", "Nachbarn"):
        assert word in text, word
