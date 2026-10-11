# Kooperation in Netzen: warum Nachbarschaft Kooperation trägt – Streamlit-Demo

<!-- Nach dem Deploy direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-netzwerk-kooperation-demo.streamlit.app/)** -->

Elftes (optionales) Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Setzt auf [replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) auf: Dort verliert die Kooperation in der durchmischten Population. Hier spielt und lernt jeder
nur mit seinen **Nachbarn**, ohne Gedächtnis und ohne Reputation. Die Kante ist ein `fix`: derselbe Mechanismus der Auswahl, aber mit Struktur statt Durchmischung.

Vehikel: Subunternehmer, die nur mit festen Nachbarn auf einer Relation teilen (Kosten c, Nutzen b je Nachbar). Eigennutz und Nachahmung sind Modellannahmen.

## Warum dieses Problem

In einer durchmischten Population verdient der Defektierer mehr. Auf einem Gitter bilden Kooperierende Nester, in denen sie sich gegenseitig helfen. Ob das reicht, hängt davon ab,
**wie ersetzt wird**: Die Theorie von Ohtsuki et al. (2006) gibt für große reguläre Graphen und schwache Auswahl die Schwelle b/c > k (Death-Birth), b/c > k + 2 (Imitation) und nie
(Birth-Death). Die Demo misst das nach, exakt auf kleinen Ringen und in der Simulation auf einem 20×20-Gitter.

## Modell

Spenderspiel: Ein Kooperierender zahlt jedem seiner k Nachbarn den Nutzen b und trägt Kosten c = 1 je Nachbar. Fitness 1 + w · Auszahlung, nach unten bei 0 begrenzt. Drei
Ersetzungsregeln: Death-Birth, Imitation, Birth-Death. Exakter Teil: alle 2^N Zustände eines Rings mit N Spielern und k Nachbarn, die Fixierungswahrscheinlichkeit einer einzelnen
Kooperierenden als lineares Gleichungssystem, bei schwacher Auswahl w = 0,001. Räumlicher Teil: 20×20-Torus mit 4 oder 8 Nachbarn, asynchrone Aktualisierung, Start mit 50 % Kooperierenden.

## Methodik

- **Graphen:** `circulant`, `complete_graph`, `torus` (`nwk_algorithm.py`).
- **Exakt:** `exact_fixation` löst das System über alle Zustände, `critical_ratio` findet das kleinste b/c mit ρ über 1/N per Bisektion, `critical_formula` ist die geschlossene Formel (N − 2)/(N/k − 2).
- **Simulation:** `simulate` (je Generation N Ersetzungsschritte), `single_cooperator_fixation_rate` (Monte Carlo als Gegenprobe).
- **Vorgerechnete Tabelle:** `nwk_make_sweeps.py` rechnet 18 exakte Schwellen und 960 räumliche Läufe (3 Regeln × 2 Nachbarschaften × 8 b/c-Werte × 20 Zufalls-Seeds, rund 4 Minuten) nach `nwk_sweeps.json`.

## Befunde (gemessen, keine Behauptungen)

Räumlich: 20×20-Torus, w = 0,10, 60 Generationen, Start mit 50 % Kooperierenden, 20 Zufalls-Seeds je Punkt.

| Frage | Befund | Test |
|---|---|---|
| Kritisches b/c auf kleinen Ringen, Death-Birth | N = 6, k = 2: 4,003 (Formel 4,0); N = 8: 3,001 (3,0); N = 10: 2,667 (2,667); N = 10, k = 4: 16,24 (16,0). Die Schwelle sinkt mit N und liegt über k, dem Wert der großen Netze. | `test_critical_ratios_on_small_rings_match_the_formula`, `test_thresholds_shrink_with_the_ring_size` |
| Imitation und Birth-Death auf kleinen Ringen | Imitation: 13,11 bei N = 8, 8,53 bei N = 10 (k = 2); bei N = 6 nie. Birth-Death: auf keinem getesteten Ring bis b/c = 60. | `test_imitation_critical_ratios_and_cases_without_a_threshold` |
| Durchmischte Population | Die Fixierungswahrscheinlichkeit liegt bei b/c = 2, 10, 50 unter 1/N. | `test_well_mixed_population_never_favours_cooperation` |
| Death-Birth auf dem Gitter, 4 Nachbarn | Mittlerer Endanteil Kooperierender: 0 % bei b/c = 2, 11 % bei 3, 43 % bei 4 (9 von 20 Läufen mit Mehrheit), 79 % bei 5 (19 von 20), über 95 % ab 8. | `test_spatial_death_birth_on_four_neighbours` |
| Imitation, 4 Nachbarn | Erst später: 4 % bei b/c = 4, 32 % bei 6 (5 von 20 Läufen mit Mehrheit), 18 von 20 bei 8. | `test_spatial_imitation_needs_more_than_death_birth` |
| Birth-Death | In keinem der 320 Läufe (bis b/c = 12, 4 und 8 Nachbarn) bleibt ein Kooperierender übrig. | `test_spatial_birth_death_never_carries_cooperation` |
| 8 statt 4 Nachbarn | Death-Birth: 0 % bei b/c = 5 (gegen 79 % bei 4 Nachbarn), 33 % bei 8 (5 von 20), 17 von 20 bei 10, 19 von 20 bei 12. | `test_eight_neighbours_need_a_higher_benefit_than_four` |

### Befunde gegenüber dem Plan

Der Plan nannte das Stück ohne eigene Hypothese. Zwei Ergebnisse gehen über die Literaturregel hinaus: (1) Die exakten Schwellen kleiner Ringe stimmen mit der geschlossenen Formel für
endliches N überein und liegen weit über dem Wert großer Netze (bei N = 6 genau 4 statt 2), der Wert k gilt also nur für große Netze. (2) Imitation hat auf kleinen Ringen bei N = 6 keine
Schwelle, auf dem Gitter dagegen ab etwa b/c = 6 bis 8; der Zusatz „k + 2“ ist also kein fester Zuschlag, sondern eine Schwelle für große Netze.

## Ehrliche Grenzen

- **Reguläre Graphen mit Randanschluss:** bei ungleichen Graden ändern sich die Schwellen.
- **Feste Strategien ohne Gedächtnis:** mit Gedächtnis (Tit-for-Tat) bilden sich andere Muster.
- **Exakter Teil bei schwacher Auswahl und N ≤ 10:** die Theorie gilt für große Netze; hier sind die endlichen Werte gemessen.
- **Ein Gitter, ein Start (50 %):** andere Anfangsanteile verschieben die Anteile am Ende.
- **Kein Rauschen und keine Mutation:** ein absorbierter Zustand bleibt es.
- **Literatur nur über Zusammenfassungen gelesen.**

## Verifikation

- **Kern:** je Einheit eine Handrechnung (Nachbarlisten, Auszahlung auf einem Ring mit vier Knoten, Fitness, ein Death-Birth-, Imitations- und Birth-Death-Schritt mit festem Zufall,
  neutrale Auswahl gleich 1/N, zwei Spieler, vollständiger Graph).
- **Orakel** (`tests/test_oracle_netzwerk_kooperation.py`): (1) exakte Fixierung gegen eine Monte-Carlo-Simulation der Aktualisierungsschritte (alle drei Regeln); (2) dieselbe Zahl gegen
  eine Wertiteration der Markov-Kette ohne Gleichungslöser; (3) kritisches b/c gegen die geschlossene Formel; (4) die Übergangswahrscheinlichkeiten gegen eine Aufzählung aller Zufallsentscheidungen.
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py`, gelesen aus `nwk_sweeps.json`; dazu eine Stichprobe, die vier Läufe neu rechnet.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, jede Regel mit jeder Ringgröße, Permalink begrenzt und rastet ein, Erklärungen) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `nwk_algorithm.py` | Kern: Graphen, Auszahlung, exakte Fixierung, Simulation |
| `nwk_constants.py` | Spielparameter, Reglergrenzen, Regeln, Presets |
| `nwk_evaluation.py` | Analyse, Kurven, Zugriff auf die vorgerechnete Tabelle, Verdikt |
| `nwk_make_sweeps.py` | rechnet `nwk_sweeps.json` vor |
| `nwk_presets.py` | Permalink (Begrenzen und Einrasten), Presets |
| `nwk_sweeps.json` | vorgerechnete Schwellen und Läufe |
| `nwk_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest (Orakel nutzen nur numpy) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest, Footer |

## Bewusst nicht umgesetzt

- **Beliebige Netzwerke (Skalenfreie, Kleine Welt):** eigene Modelle, die Schwellen hängen an der Struktur.
- **Synchrone Aktualisierung und Strategien mit Gedächtnis:** gibt andere Muster (Nowak und May 1992).
- **Größere exakte Ringe:** 2^N Zustände wachsen schnell; N = 10 steht nur in der Tabelle.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
