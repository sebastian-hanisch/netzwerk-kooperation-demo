"""Plotly-Abbildungen: Gitter, Verlauf, Schwellen über b/c. Alle Achsen gesperrt (Touch-Scrollen)."""

import plotly.graph_objects as go

import nwk_constants as C

_LAYOUT = dict(margin=dict(l=10, r=10, t=40, b=10), height=400, legend=dict(orientation="h", y=-0.2))


def _lock(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_grid(grid) -> go.Figure:
    """Endzustand auf dem Torus: Kooperierende dunkelgrün, Defektierer orange."""
    fig = go.Figure(go.Heatmap(z=[list(r) for r in grid], colorscale=[[0.0, C.COLOR_DEFECT], [1.0, C.COLOR_COOP]], showscale=False, xgap=1, ygap=1,
                               hovertemplate="Zeile %{y}, Spalte %{x}<br>%{z:.0f} (1 = kooperiert)<extra></extra>"))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=440, title="Endzustand auf dem Gitter (grün: kooperiert, orange: defektiert)")
    fig.update_yaxes(autorange="reversed", scaleanchor="x", showticklabels=False)
    fig.update_xaxes(showticklabels=False)
    return _lock(fig)


def build_trace(trace) -> go.Figure:
    fig = go.Figure(go.Scatter(x=list(range(len(trace))), y=trace, mode="lines", line=dict(color=C.COLOR_COOP, width=3), name="Anteil Kooperierender",
                               hovertemplate="Generation %{x}<br>Anteil %{y:.3f}<extra></extra>"))
    fig.add_hline(y=0.5, line_dash="dot", line_color=C.COLOR_NEUTRAL)
    fig.update_layout(**_LAYOUT, title="Anteil der Kooperierenden je Generation", xaxis_title="Generation", yaxis_title="Anteil", yaxis=dict(range=[0, 1]))
    return _lock(fig)


def build_threshold(series_by_rule: dict[str, list[dict]], k: int) -> go.Figure:
    """Mittlerer Endanteil der Kooperierenden über b/c, je Regel eine Linie, die Punkte sind die einzelnen Läufe."""
    colors = {"DB": C.COLOR_COOP, "IM": C.COLOR_LINE, "BD": C.COLOR_DEFECT}
    names = C.RULE_LABELS
    fig = go.Figure()
    for rule, series in series_by_rule.items():
        fig.add_trace(go.Scatter(x=[s["br"] for s in series], y=[s["mean"] for s in series], mode="lines+markers", name=names[rule], line=dict(color=colors[rule], width=3)))
    fig.add_vline(x=k, line_dash="dash", line_color=C.COLOR_NEUTRAL, annotation_text=f"b/c = k = {k}", annotation_position="top")
    fig.update_layout(**_LAYOUT, title="Mittlerer Endanteil Kooperierender über b/c (20 Seeds je Punkt)", xaxis_title="b/c", yaxis_title="Anteil Kooperierender", yaxis=dict(range=[0, 1.02]))
    return _lock(fig)


def build_exact_curve(curve: list[dict], critical: float | None, formula: float | None) -> go.Figure:
    fig = go.Figure(go.Scatter(x=[c["br"] for c in curve], y=[c["ratio"] for c in curve], mode="lines+markers", line=dict(color=C.COLOR_COOP, width=3), name="N·ρ"))
    fig.add_hline(y=1.0, line_dash="dot", line_color=C.COLOR_NEUTRAL, annotation_text="neutral (ρ = 1/N)", annotation_position="bottom right")
    if critical is not None:
        fig.add_vline(x=critical, line_dash="dash", line_color=C.COLOR_LINE, annotation_text=f"kritisch {critical:.2f}".replace(".", ","), annotation_position="top")
    fig.update_layout(**_LAYOUT, title="Fixierungswahrscheinlichkeit einer einzelnen Kooperierenden, geteilt durch den neutralen Wert 1/N", xaxis_title="b/c", yaxis_title="N·ρ")
    return _lock(fig)
