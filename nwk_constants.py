"""Konstanten: Spielparameter, Regler-Grenzen, Aktualisierungsregeln, vorgerechnete Tabelle, Farben und Presets."""

COST = 1.0                                   # Kosten c je Nachbar (der Nutzen b ist der Regler b/c)
WEAK_W = 1e-3                                # schwache Auswahl für den exakten Teil (Fixierungswahrscheinlichkeit, kritisches b/c)

# --- Aktualisierungsregeln ----------------------------------------------------------------------------------------------------------------------
RULE_KEYS = ("DB", "IM", "BD")
RULE_LABELS = {"DB": "Death-Birth", "IM": "Imitation", "BD": "Birth-Death"}
RULE_TEXT = {
    "DB": "Ein zufälliger Spieler scheidet aus; seine Nachbarn bewerben sich um den Platz, im Verhältnis zu ihrer Fitness.",
    "IM": "Ein zufälliger Spieler überlegt, die Strategie zu wechseln, und vergleicht sich mit seinen Nachbarn und sich selbst, im Verhältnis zur Fitness.",
    "BD": "Ein Spieler wird im Verhältnis zur Fitness ausgewählt und ersetzt einen zufälligen Nachbarn.",
}
DEFAULT_RULE = "DB"

# --- exakter Teil (kleine Ringe, alle 2^N Zustände) -----------------------------------------------------------------------------------------------
EXACT_N_OPTIONS = (6, 8)                       # live exakt lösbar; N = 10 steht nur in der vorgerechneten Tabelle (1024 Zustände)
EXACT_K_OPTIONS = (2, 4)
DEFAULT_EXACT_N, DEFAULT_EXACT_K = 8, 2
BC_GRID = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0)

# --- räumlicher Teil (Torus) --------------------------------------------------------------------------------------------------------------------
LATTICE_SIZE = 20
NEIGHBOR_KEYS = (4, 8)
NEIGHBOR_LABELS = {4: "4 Nachbarn (Von Neumann)", 8: "8 Nachbarn (Moore)"}
DEFAULT_NEIGHBORS = 4
BR_MIN, BR_MAX, BR_STEP, DEFAULT_BR = 1.5, 12.0, 0.5, 5.0
W_MIN, W_MAX, W_STEP, DEFAULT_W = 0.01, 0.20, 0.01, 0.10     # w ≤ 1/k hält 1 + w·π für k ≤ 8 nahe der Null; negative Fitness wird auf 0 gesetzt
GEN_MIN, GEN_MAX, GEN_STEP, DEFAULT_GEN = 10, 150, 10, 60
SEED_MIN, SEED_MAX, DEFAULT_SEED = 0, 9999, 0
START_SHARE = 0.5                            # Anfangsanteil der Kooperierenden

# --- vorgerechnete Tabelle (nwk_sweeps.json) ------------------------------------------------------------------------------------------------------
SWEEP_SEEDS = tuple(range(2000, 2020))
SWEEP_BRS = (2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0)
SWEEP_W = 0.10
SWEEP_GEN = 60

COLOR_COOP = "#2F6B65"
COLOR_DEFECT = "#C0662B"
COLOR_LINE = "#4c78a8"
COLOR_NEUTRAL = "rgba(150,150,150,0.8)"

PRESETS = {
    "Death-Birth, 4 Nachbarn, b/c = 5": {"rule": "DB", "neighbors": 4, "br": 5.0, "w": 0.10, "gen": 60, "seed": 0},
    "Death-Birth, 4 Nachbarn, b/c = 3": {"rule": "DB", "neighbors": 4, "br": 3.0, "w": 0.10, "gen": 60, "seed": 0},
    "Imitation, 4 Nachbarn, b/c = 5": {"rule": "IM", "neighbors": 4, "br": 5.0, "w": 0.10, "gen": 60, "seed": 0},
    "Birth-Death, 4 Nachbarn, b/c = 10": {"rule": "BD", "neighbors": 4, "br": 10.0, "w": 0.10, "gen": 60, "seed": 0},
    "Death-Birth, 8 Nachbarn, b/c = 5": {"rule": "DB", "neighbors": 8, "br": 5.0, "w": 0.10, "gen": 60, "seed": 0},
}
PRESET_HELP = {
    "Death-Birth, 4 Nachbarn, b/c = 5": "Über der Schwelle b/c = k = 4: Kooperierende bilden Nester und halten sich.",
    "Death-Birth, 4 Nachbarn, b/c = 3": "Unter der Schwelle: Die Defektierer verdrängen die Kooperierenden.",
    "Imitation, 4 Nachbarn, b/c = 5": "Die Schwelle liegt bei Imitation höher (k + 2): Bei b/c = 5 trägt es nicht.",
    "Birth-Death, 4 Nachbarn, b/c = 10": "Bei Birth-Death hilft die Nachbarschaft nichts: Kooperation verliert bei jedem b/c.",
    "Death-Birth, 8 Nachbarn, b/c = 5": "Mit 8 statt 4 Nachbarn liegt die Schwelle der Theorie bei k = 8: Bei b/c = 5 reicht der Nutzen nicht.",
}
