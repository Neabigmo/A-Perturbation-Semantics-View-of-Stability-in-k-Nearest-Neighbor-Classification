"""Post-process tabular benchmark: print summary for updating paper text."""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "outputs/experiments/tabular_benchmark.json"
d = json.load(open(path, "r"))

agg = d["aggregates"]
print(f"=== Tabular Benchmark: {len(agg)} aggregate groups ===\n")

datasets = sorted(set(a["dataset"] for a in agg))
k_values = sorted(set(a["k"] for a in agg))

name_map = {
    "iris": "Iris",
    "wine": "Wine",
    "breast_cancer": "Breast Cancer",
    "digits": "Digits",
}

for ds in datasets:
    print(f"\n--- {name_map.get(ds, ds)} ---")
    for k in k_values:
        match = [a for a in agg if a["dataset"] == ds and a["k"] == k]
        if match:
            e = match[0]
            print(f"  k={k}: sep={e['separation_frequency']:.3f} +/- {e['separation_ci']:.3f}, "
                  f"vuln={e['mean_vulnerable_query_rate']:.3f}, "
                  f"prec={e['mean_diagnostic_precision']:.2f}, "
                  f"rec={e['mean_diagnostic_recall']:.2f}, "
                  f"n={e['n_replicates']}")

# Find Digits max separation for paper text
print("\n\n=== Key Numbers for Paper ===")
for ds in datasets:
    for k in k_values:
        match = [a for a in agg if a["dataset"] == ds and a["k"] == k]
        if match:
            e = match[0]
            if e['separation_frequency'] > 0.8:
                print(f"{name_map.get(ds, ds)} k={k}: sep={e['separation_frequency']:.2f}")
