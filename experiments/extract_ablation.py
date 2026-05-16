"""Extract ablation table data from synthetic benchmark results."""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "outputs/experiments/synthetic_benchmark.json"
d = json.load(open(path, "r"))

aggs = d["aggregates"]

# Baseline: all ratios = 0
baseline_1 = [a for a in aggs if a["k"]==1 and a["duplicate_ratio"]==0 and a["conflict_ratio"]==0 and a["noise_ratio"]==0]
baseline_3 = [a for a in aggs if a["k"]==3 and a["duplicate_ratio"]==0 and a["conflict_ratio"]==0 and a["noise_ratio"]==0]
baseline_5 = [a for a in aggs if a["k"]==5 and a["duplicate_ratio"]==0 and a["conflict_ratio"]==0 and a["noise_ratio"]==0]

print("=== BASELINE (V=2, no dup, no conf, no noise) ===")
for e in baseline_1:
    if e["n_vertices"] == 2:
        print(f"k={e['k']}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, vuln_rate={e['mean_vulnerable_query_rate']:.3f}, n={e['n_trials']}")
for e in baseline_3:
    if e["n_vertices"] == 2:
        print(f"k={e['k']}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, vuln_rate={e['mean_vulnerable_query_rate']:.3f}, n={e['n_trials']}")
for e in baseline_5:
    if e["n_vertices"] == 2:
        print(f"k={e['k']}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, vuln_rate={e['mean_vulnerable_query_rate']:.3f}, n={e['n_trials']}")

# Ablation conditions
ablations = [
    ("Noise only", {"duplicate_ratio": 0, "conflict_ratio": 0, "noise_ratio": 0.1}),
    ("Conflict only", {"duplicate_ratio": 0, "conflict_ratio": 0.3, "noise_ratio": 0}),
    ("Duplicate only", {"duplicate_ratio": 0.3, "conflict_ratio": 0, "noise_ratio": 0}),
    ("Dup+Conf", {"duplicate_ratio": 0.3, "conflict_ratio": 0.3, "noise_ratio": 0}),
    ("Dup(0.6)", {"duplicate_ratio": 0.6, "conflict_ratio": 0, "noise_ratio": 0}),
]

for name, params in ablations:
    print(f"\n=== {name} (V=2) ===")
    for k in [1, 3, 5]:
        entries = [a for a in aggs if a["k"]==k and a["n_vertices"]==2
                   and a["duplicate_ratio"]==params["duplicate_ratio"]
                   and a["conflict_ratio"]==params["conflict_ratio"]
                   and a["noise_ratio"]==params["noise_ratio"]]
        if entries:
            e = entries[0]
            print(f"k={k}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, "
                  f"vuln_rate={e['mean_vulnerable_query_rate']:.3f}, n={e['n_trials']}")

# Effect of vertices
print("\n=== VERTEX COUNT (V=3, no dup, no conf, no noise) ===")
for k in [1, 3, 5]:
    entries = [a for a in aggs if a["k"]==k and a["n_vertices"]==3
               and a["duplicate_ratio"]==0 and a["conflict_ratio"]==0 and a["noise_ratio"]==0]
    if entries:
        e = entries[0]
        print(f"k={k}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, "
              f"vuln_rate={e['mean_vulnerable_query_rate']:.3f}, n={e['n_trials']}")

# Precision/recall info
print("\n=== PRECISION / RECALL (not available in synthetic) ===")
print("Tabular benchmark has diagnostic precision/recall - available after that run completes.")
