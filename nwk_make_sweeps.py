"""Rechnet die Tabelle `nwk_sweeps.json` vor (einmalig, einige Minuten): kritische b/c-Werte kleiner Ringe (exakt) und räumliche Läufe auf dem Torus.

    python nwk_make_sweeps.py           # schreibt nwk_sweeps.json neben dieses Skript
    python nwk_make_sweeps.py --check   # nur die Aufgabenliste zeigen
"""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import nwk_algorithm as A  # noqa: E402
import nwk_constants as C  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nwk_sweeps.json")
EXACT_NS = (6, 8, 10)


def exact_tasks():
    return [("exact", n, k, rule) for n in EXACT_NS for k in C.EXACT_K_OPTIONS for rule in C.RULE_KEYS if n / k > 1]


def spatial_tasks():
    return [("spatial", rule, nbs, br, seed) for rule in C.RULE_KEYS for nbs in C.NEIGHBOR_KEYS for br in C.SWEEP_BRS for seed in C.SWEEP_SEEDS]


def work(task):
    if task[0] == "exact":
        _, n, k, rule = task
        if k >= n:
            return {"kind": "exact", "n": n, "k": k, "rule": rule, "critical": None, "skipped": True}
        return {"kind": "exact", "n": n, "k": k, "rule": rule, "critical": A.critical_ratio(A.circulant(n, k), rule), "formula": A.critical_formula(n, k) if rule == "DB" else None}
    _, rule, nbs, br, seed = task
    nb = A.torus(C.LATTICE_SIZE, nbs)
    r = A.simulate(nb, br, C.SWEEP_W, rule, seed, C.SWEEP_GEN)
    return {"kind": "spatial", "rule": rule, "neighbors": nbs, "br": br, "seed": seed, "share": r["share"], "absorbed": r["share"] in (0.0, 1.0)}


def main():
    tasks = exact_tasks() + spatial_tasks()
    if "--check" in sys.argv:
        print(len(exact_tasks()), "exakte Aufgaben,", len(spatial_tasks()), "räumliche Läufe")
        return
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max(1, min(6, (os.cpu_count() or 2) - 1))) as pool:
        results = list(pool.map(work, tasks, chunksize=4))
    exact = [r for r in results if r["kind"] == "exact"]
    spatial = [r for r in results if r["kind"] == "spatial"]
    data = {"meta": {"seeds": list(C.SWEEP_SEEDS), "w": C.SWEEP_W, "generations": C.SWEEP_GEN, "lattice": C.LATTICE_SIZE, "weak_w": C.WEAK_W,
                     "start_share": C.START_SHARE, "seconds": round(time.time() - t0)}, "exact": exact, "spatial": spatial}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("geschrieben:", OUT, f"({len(tasks)} Aufgaben, {round(time.time() - t0)} s)")


if __name__ == "__main__":
    main()
