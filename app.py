"""Kooperation in Netzen: warum Nachbarschaft Kooperation trägt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Elftes Stück der Wiederholte-Spiele-Linie (optional): Wer nur mit Nachbarn spielt und nur von Nachbarn lernt, kann Kooperation halten, ohne Gedächtnis und ohne Reputation.
Wie viel Nutzen braucht es, und hängt das davon ab, wie ersetzt wird?

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import nwk_constants as C
import nwk_evaluation as E
from nwk_evaluation import Settings, fmt
from nwk_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from nwk_visualization import build_exact_curve, build_grid, build_threshold, build_trace

st.set_page_config(page_title="Kooperation in Netzen: warum Nachbarschaft Kooperation trägt – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _curve(n, k, rule):
    return E.exact_curve(n, k, rule)


st.title("🕸️ Kooperation in Netzen: warum Nachbarschaft Kooperation trägt")
st.markdown(
    """
In einer durchmischten Population verliert Kooperation: Wer nichts beisteuert, verdient mehr. Anders ist es, wenn jeder nur mit seinen **Nachbarn** spielt und nur von
Nachbarn lernt. Dann können Kooperierende **Nester** bilden, in denen sie sich gegenseitig helfen, und die Defektierer am Rand verdienen weniger als die Kooperierenden
im Inneren. Das braucht weder Gedächtnis noch Reputation, nur einen Ort.

Die Demo rechnet das auf zwei Wegen: **exakt** auf kleinen Ringen (alle 2^N Zustände, ein lineares Gleichungssystem) und **simuliert** auf einem 20×20-Gitter. Gefragt wird,
wie viel Nutzen im Verhältnis zu den Kosten (b/c) nötig ist, und warum das davon abhängt, **wie ersetzt wird**.

Weiter unten: **❓ Kernfrage**, drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Vorgänger in der Linie sind
[replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) (durchmischte Population, dort verliert die Kooperation) und
[indirekte-reziprozitaet-demo](https://sebastianhanisch-indirekte-reziprozitaet-demo.streamlit.app/) (Reputation statt Ort).
"""
)

with st.expander("So funktioniert das Spiel", expanded=True):
    st.markdown(
        """
1. **Spenderspiel:** Jeder Spieler hat k Nachbarn. Ein Kooperierender zahlt jedem Nachbarn einen Nutzen b und trägt dafür Kosten c = 1 je Nachbar; ein Defektierer zahlt nichts.
2. **Auszahlung** eines Spielers: b · (Zahl kooperierender Nachbarn) − c · k, wenn er selbst kooperiert, sonst nur der erste Teil. **Fitness** = 1 + w · Auszahlung (nach unten bei 0 begrenzt).
3. **Ersetzen:** Nach einer festen Regel wird ein Spieler durch die Strategie eines Nachbarn ersetzt, mit Wahrscheinlichkeit ∝ Fitness (siehe nächste Tabelle).
4. **Frage:** Ab welchem b/c nimmt die Zahl der Kooperierenden zu, statt zu schrumpfen?
        """
    )

with st.expander("Die drei Ersetzungsregeln: wer macht was?", expanded=True):
    rows = ["| Regel | Ablauf | Schwelle der Theorie (große Netze, schwache Auswahl) |", "|---|---|---|"]
    for key in C.RULE_KEYS:
        rows.append(f"| **{C.RULE_LABELS[key]}** | {C.RULE_TEXT[key]} | {'b/c > k' if key == 'DB' else ('b/c > k + 2' if key == 'IM' else 'nie')} |")
    st.markdown("\n".join(rows))
    st.caption("k ist die Zahl der Nachbarn. Die Schwellen stammen aus der Theorie; die Demo misst sie nach, auf kleinen Ringen exakt und auf dem Gitter in der Simulation.")

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Ersetzung**")
    rule = st.selectbox("Ersetzungsregel", C.RULE_KEYS, key="rule_select", format_func=lambda k: C.RULE_LABELS[k], help="Wie ein Spieler durch die Strategie eines Nachbarn ersetzt wird.")
    st.caption(C.RULE_TEXT[rule])
    st.markdown("**Spiel auf dem Gitter**")
    neighbors = st.selectbox("Nachbarschaft", C.NEIGHBOR_KEYS, key="neighbors_select", format_func=lambda k: C.NEIGHBOR_LABELS[k])
    br = st.slider("Nutzen im Verhältnis zu den Kosten b/c", *bounds("br_slider"), step=C.BR_STEP, key="br_slider", help="Was ein Nachbar von einem Kooperierenden bekommt, je Einheit Kosten.")
    w = st.slider("Auswahlstärke w", *bounds("w_slider"), step=C.W_STEP, key="w_slider", help="Wie stark die Fitness vom Gewinn abhängt. Klein = schwache Auswahl.")
    gen = st.slider("Generationen", *bounds("gen_slider"), step=C.GEN_STEP, key="gen_slider", help="Eine Generation sind so viele Ersetzungen, wie es Spieler gibt.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), step=1, key="seed_input")
    st.button("🎲 Anderen Zufalls-Seed würfeln", on_click=randomize_seed, key="seed_button")
    st.markdown("**Kleiner Ring (exakt)**")
    exact_n = st.selectbox("Zahl der Spieler N", C.EXACT_N_OPTIONS, key="exact_n_select")
    exact_k = st.selectbox("Zahl der Nachbarn k", C.EXACT_K_OPTIONS, key="exact_k_select", help="Auf einem Ring mit 6 Spielern gibt es bei k = 4 fast jeden als Nachbarn.")

settings = Settings(rule, int(neighbors), round(float(br), 2), round(float(w), 2), int(gen), int(seed), int(exact_n), int(exact_k))
sync_query_params({"rule_select": settings.rule, "neighbors_select": settings.neighbors, "br_slider": settings.br, "w_slider": settings.w, "gen_slider": settings.gen,
                   "seed_input": settings.seed, "exact_n_select": settings.exact_n, "exact_k_select": settings.exact_k})

t0 = time.time()
with st.spinner("Das Gitter entwickelt sich ..."):
    an = _analysis(settings)
elapsed = time.time() - t0

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown(f"## 🎬 {C.RULE_LABELS[rule]} auf dem 20×20-Gitter mit {settings.neighbors} Nachbarn")
m1, m2, m3 = st.columns(3)
m1.metric("Kooperierende am Ende", f"{fmt(an.share * 100, 0)} %", delta=f"Start {fmt(an.start_share * 100, 0)} %", delta_color="off")
m2.metric("Generationen gerechnet", f"{len(an.trace) - 1}", delta="beendet, wenn eine Strategie die ganze Population hat" if an.absorbed else "volle Länge", delta_color="off")
m3.metric("Schwelle der Theorie", E.threshold_text(rule, settings.neighbors), delta=f"b/c = {fmt(settings.br, 1)}", delta_color="off")
c_left, c_right = st.columns(2)
with c_left:
    st.plotly_chart(build_grid(an.grid), width="stretch", key="grid_chart")
with c_right:
    st.plotly_chart(build_trace(an.trace), width="stretch", key="trace_chart")
st.caption(f"Rechenzeit {fmt(elapsed, 1)} s. Ein Lauf ist ein einzelner Zufallsablauf; die Aussagen über die Schwelle stehen unten, über je 20 Läufe.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Trägt Nachbarschaft die Kooperation, und wovon hängt es ab?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info}[level](sentence)
st.markdown("---")

sweeps = E.load_sweeps()
if sweeps is None:
    st.warning("Die vorgerechnete Tabelle `nwk_sweeps.json` fehlt. Erzeugen mit `python nwk_make_sweeps.py`.")
else:
    # --- Experiment 1 ----------------------------------------------------------------------------------------------------------------------
    st.subheader("🔬 Experiment: Ab welchem Nutzen trägt es?")
    st.caption(f"Mittlerer Endanteil Kooperierender auf dem 20×20-Gitter mit {settings.neighbors} Nachbarn, {sweeps['meta']['generations']} Generationen, w = {fmt(sweeps['meta']['w'])}, "
               f"Start 50 %, je Punkt {len(sweeps['meta']['seeds'])} Zufalls-Seeds. Vorgerechnet.")
    series = {r: E.spatial_series(r, settings.neighbors) for r in C.RULE_KEYS}
    st.plotly_chart(build_threshold(series, settings.neighbors), width="stretch", key="threshold_chart")
    rows = ["| b/c | " + " | ".join(C.RULE_LABELS[r] for r in C.RULE_KEYS) + " |", "|---|---|---|---|"]
    for i, point in enumerate(series["DB"]):
        rows.append(f"| {fmt(point['br'], 0)} | " + " | ".join(f"{fmt(series[r][i]['mean'] * 100, 0)} %" for r in C.RULE_KEYS) + " |")
    st.markdown("\n".join(rows))
    st.info("Die Regel entscheidet: Bei Death-Birth steigt der Anteil schon bei b/c um k, bei Imitation erst später, und bei Birth-Death trägt auch ein b/c von 12 die "
            "Kooperation nicht. Wer zuerst stirbt und von Nachbarn ersetzt wird, hat die Konkurrenz um den Platz vor der eigenen Tür; wer andere ersetzt, nicht.")
    st.markdown("---")

    # --- Experiment 2 ----------------------------------------------------------------------------------------------------------------------
    st.subheader("🔬 Experiment: Exakt auf einem kleinen Ring")
    st.caption(f"Ring mit N = {settings.exact_n} Spielern und k = {settings.exact_k} Nachbarn, Regel {C.RULE_LABELS[rule]}, schwache Auswahl (w = {C.WEAK_W:g}): Wahrscheinlichkeit, dass "
               "eine einzelne Kooperierende die ganze Population ersetzt, geteilt durch den neutralen Wert 1/N. Über 1 heißt: Die Kooperation setzt sich eher durch als der Zufall.")
    if settings.exact_k >= settings.exact_n:
        st.info("Mit k ≥ N gibt es keinen Ring mehr.")
    else:
        with st.spinner("Löse das Gleichungssystem über alle Zustände ..."):
            curve = _curve(settings.exact_n, settings.exact_k, rule)
        row = E.exact_row(settings.exact_n, settings.exact_k, rule)
        critical = row["critical"] if row else None
        formula = row.get("formula") if row else None
        st.plotly_chart(build_exact_curve(curve, critical, formula), width="stretch", key="exact_chart")
        if critical is None:
            st.info("Auf diesem Ring liegt die Fixierungswahrscheinlichkeit bei keinem getesteten b/c (bis 60) über dem neutralen Wert: Kooperation setzt sich nie eher durch als der Zufall.")
        else:
            extra = f" Die geschlossene Formel (N − 2)/(N/k − 2) für Death-Birth gibt {fmt(formula, 2)}." if formula is not None else ""
            st.info(f"Kritisches b/c auf diesem Ring: {fmt(critical, 2)}.{extra}")
    st.markdown("---")

    # --- Experiment 3 ----------------------------------------------------------------------------------------------------------------------
    st.subheader("🔬 Experiment: Die kritische Schwelle auf kleinen Ringen, alle Regeln")
    rows = ["| N | k | Death-Birth (gemessen) | Death-Birth (Formel) | Imitation | Birth-Death |", "|---|---|---|---|---|---|"]
    for n in (6, 8, 10):
        for k in C.EXACT_K_OPTIONS:
            if k >= n:
                continue
            db, im, bd = (E.exact_row(n, k, r) for r in ("DB", "IM", "BD"))
            cell = lambda r: "nie (bis 60)" if r is None or r["critical"] is None else fmt(r["critical"], 2)
            f = db.get("formula") if db else None
            rows.append(f"| {n} | {k} | {cell(db)} | {fmt(f, 2) if f is not None else 'nicht definiert'} | {cell(im)} | {cell(bd)} |")
    st.markdown("\n".join(rows))
    st.info("Auf kleinen Ringen ist die Schwelle höher als der Wert der großen Netze (k beziehungsweise k + 2) und wird mit wachsendem N kleiner. Für Death-Birth stimmt die gemessene "
            "Schwelle mit der geschlossenen Formel überein.")
st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Reguläres Netz: alle haben gleich viele Nachbarn, Randanschluss** | Bei ungleichen Graden (Sterne, Netzwerke mit Nabenknoten) ändert sich die Schwelle; sie hängt dann an der Struktur. | – |
| **Feste Strategien: kooperieren oder defektieren, ohne Gedächtnis** | Strategien mit Gedächtnis (Tit-for-Tat) bilden auf dem Gitter andere Muster. | `tit-for-tat-demo` |
| **Schwache Auswahl (exakter Teil)** | Bei starker Auswahl und kleinem Netz weichen die Schwellen ab; die Simulation läuft mit w = 0,10. | – |
| **Kleine Ringe (N ≤ 10) und ein einzelnes Gitter (20×20)** | Die Theorie gilt für große Netze; hier sind die Zahlen für endliche N gemessen. | – |
| **Kein Mutations- und kein Rauscheintrag** | Mit Mutation kann sich ein Zustand wieder auflösen. | `replikator-demo` |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Auszahlung.** Spieler $i$ mit Nachbarn $N(i)$, Strategien $s_j \in \{0, 1\}$ (1 = kooperiert):
$$\pi_i = b \sum_{j \in N(i)} s_j \;-\; c\,k\,s_i.$$

**Fitness.** $f_i = \max\{0,\; 1 + w\,\pi_i\}$.

**Death-Birth.** Spieler $i$ wird zufällig gewählt und durch einen Nachbarn $j$ ersetzt, mit Wahrscheinlichkeit $f_j / \sum_{l \in N(i)} f_l$.
**Imitation:** wie Death-Birth, aber $i$ selbst bewirbt sich mit. **Birth-Death:** $j$ wird mit $f_j / \sum_l f_l$ gewählt und ersetzt einen zufälligen Nachbarn.

**Fixierungswahrscheinlichkeit.** Für jeden Zustand $x \in \{0,1\}^N$ gilt $h(x) = \sum_{x'} P(x, x')\,h(x')$ mit $h(0) = 0$, $h(1) = 1$; die Demo löst dieses lineare System exakt und
mittelt $h$ über die $N$ möglichen Startplätze einer einzelnen Kooperierenden. Die Kooperation wird begünstigt, wenn $\rho > 1/N$.

**Schwellen.** Große reguläre Graphen, schwache Auswahl (Ohtsuki et al. 2006): Death-Birth $b/c > k$, Imitation $b/c > k + 2$, Birth-Death nie. Für endliches $N$ und Death-Birth:
$$\left(\frac{b}{c}\right)^* = \frac{N - 2}{N/k - 2}.$$

**Literatur.** Nowak und May (1992), *Evolutionary games and spatial chaos*, Nature 359, 826–829 (räumliche Spiele auf dem Gitter); Ohtsuki, Hauert, Lieberman und Nowak (2006),
*A simple rule for the evolution of cooperation on graphs and social networks*, Nature 441, 502–505 (die Schwelle b/c > k); Allen, Lippner, Chen, Fotouhi, Momeni, Yau und Nowak (2017),
*Evolutionary dynamics on any population structure*, Nature 544, 227–230 (beliebige Strukturen, endliche Populationen). Nur Zusammenfassungen gelesen. Die Zahlen hier sind gerechnet
und gegen unabhängige Wege geprüft.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
