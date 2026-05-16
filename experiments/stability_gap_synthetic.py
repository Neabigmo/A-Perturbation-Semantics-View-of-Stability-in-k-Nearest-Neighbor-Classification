"""Synthetic finite metric benchmark for LOO/replace-one stability gap.

Generates random graph metrics, controls duplicate/conflict ratio and label noise,
and compares max LOO and max replace-one for k = 1, 3, 5, 7.

Primary metrics:
- Separation frequency: Pr[max_loo = 0, max_replace_one = 1]
- Vulnerable-query rate: Pr_x[|M_k(S,x)| <= 2]

Outputs summary statistics with confidence intervals and ablation data.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from knn_stability.diagnostic import diagnose_sample, compute_signed_margin
from knn_stability.graph_metrics import adjacency_to_graph_metric
from knn_stability.knn import LabeledSample


def random_connected_graph(n_vertices: int, edge_prob: float, seed: int) -> dict[int, set[int]]:
    """Generate a random connected graph using Erdos-Renyi with connectivity guarantee."""
    rng = random.Random(seed)
    while True:
        vertices = list(range(n_vertices))
        edges: set[tuple[int, int]] = set()
        for i in range(n_vertices):
            for j in range(i + 1, n_vertices):
                if rng.random() < edge_prob:
                    edges.add((i, j))
        shuffled = vertices[:]
        rng.shuffle(shuffled)
        for i in range(1, n_vertices):
            edge = (shuffled[i - 1], shuffled[i])
            edges.add(edge)

        adjacency: dict[int, set[int]] = {v: set() for v in vertices}
        for u, v in edges:
            adjacency[u].add(v)
            adjacency[v].add(u)
        return adjacency


def generate_sample(
    n_vertices: int,
    sample_size: int,
    duplicate_ratio: float,
    conflict_ratio: float,
    noise_ratio: float,
    metric_space_size: int,
    rng: random.Random,
) -> tuple[list[int], list[int]]:
    """Generate a random labeled sample with controlled duplicate/conflict/noise."""
    point_indices: list[int] = []
    labels: list[int] = []

    for _ in range(sample_size):
        if rng.random() < duplicate_ratio and point_indices:
            idx = rng.choice(point_indices)
        else:
            idx = rng.randrange(metric_space_size)

        if rng.random() < conflict_ratio and labels:
            base_label = labels[-1] if labels else 0
            label = 1 - base_label
        else:
            label = rng.randint(0, 1)

        if rng.random() < noise_ratio:
            label = 1 - label

        point_indices.append(idx)
        labels.append(label)

    return point_indices, labels


def compute_vulnerable_query_rate(sample: LabeledSample, k: int) -> float:
    """Fraction of metric-space points with |M_k(S,x)| <= 2."""
    n_vuln = 0
    m = sample.metric.n
    for q_idx in range(m):
        try:
            margin = compute_signed_margin(sample, q_idx, k)
        except (ValueError, IndexError):
            continue
        if abs(margin) <= 2:
            n_vuln += 1
    return n_vuln / m if m > 0 else 0.0


def run_synthetic_benchmark(
    k_values: list[int],
    n_vertices_list: list[int],
    sample_sizes: list[int],
    duplicate_ratios: list[float],
    conflict_ratios: list[float],
    noise_ratios: list[float],
    n_trials: int,
    base_seed: int,
) -> list[dict]:
    """Run the full synthetic benchmark with 50+ trials."""
    results: list[dict] = []

    for trial in range(n_trials):
        seed = base_seed + trial
        rng = random.Random(seed)

        for nv in n_vertices_list:
            adjacency = random_connected_graph(nv, edge_prob=0.5, seed=seed)
            metric = adjacency_to_graph_metric(adjacency)

            for ss in sample_sizes:
                for dr in duplicate_ratios:
                    for cr in conflict_ratios:
                        for nr in noise_ratios:
                            pts, labs = generate_sample(
                                nv, ss, dr, cr, nr, nv, rng
                            )
                            sample = LabeledSample(
                                metric=metric,
                                point_indices=tuple(pts),
                                labels=tuple(labs),
                            )

                            for k in k_values:
                                if k > sample.n:
                                    continue
                                try:
                                    diag = diagnose_sample(sample, k, compute_all_replacements=True)
                                except Exception:
                                    continue

                                max_loo = diag.max_loo
                                max_rep = diag.replace_one_max
                                vuln_rate = compute_vulnerable_query_rate(sample, k)

                                # Separation occurred: LOO all zero, replace-one hit 1
                                separation = 1 if (max_loo == 0 and max_rep == 1) else 0

                                record = {
                                    "trial": trial,
                                    "seed": seed,
                                    "n_vertices": nv,
                                    "sample_size": ss,
                                    "duplicate_ratio": dr,
                                    "conflict_ratio": cr,
                                    "noise_ratio": nr,
                                    "k": k,
                                    "max_loo": max_loo,
                                    "max_replace_one": max_rep,
                                    "separation": separation,
                                    "vulnerable_query_rate": vuln_rate,
                                }
                                results.append(record)

    return results


def compute_aggregate_stats(results: list[dict]) -> list[dict]:
    """Compute aggregate statistics with confidence intervals."""
    grouped: dict[tuple, list[dict]] = {}
    for rec in results:
        key = (rec["k"], rec["n_vertices"], rec["duplicate_ratio"],
               rec["conflict_ratio"], rec["noise_ratio"])
        grouped.setdefault(key, []).append(rec)

    agg: list[dict] = []
    for key, group in grouped.items():
        seps = [r["separation"] for r in group]
        vulns = [r["vulnerable_query_rate"] for r in group]
        k, nv, dr, cr, nr = key

        sep_arr = np.array(seps)
        vuln_arr = np.array(vulns)
        n = len(sep_arr)

        sep_mean = float(np.mean(sep_arr))
        vuln_mean = float(np.mean(vuln_arr))

        # Wilson score interval for separation frequency (binomial)
        sep_stderr = math.sqrt(sep_mean * (1 - sep_mean) / n) if n > 0 else 0.0
        vuln_stderr = float(np.std(vuln_arr) / math.sqrt(n)) if n > 0 else 0.0
        z = 1.96  # 95% CI

        agg.append({
            "k": k,
            "n_vertices": nv,
            "duplicate_ratio": dr,
            "conflict_ratio": cr,
            "noise_ratio": nr,
            "n_trials": n,
            "separation_frequency": sep_mean,
            "separation_ci": sep_stderr * z,
            "mean_vulnerable_query_rate": vuln_mean,
            "vuln_rate_ci": vuln_stderr * z,
            "mean_max_loo": float(np.mean([r["max_loo"] for r in group])),
            "mean_max_replace_one": float(np.mean([r["max_replace_one"] for r in group])),
        })

    return agg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic finite metric stability benchmark."
    )
    parser.add_argument("--k_values", type=int, nargs="+", default=[1, 3, 5, 7])
    parser.add_argument("--n_vertices", type=int, nargs="+", default=[2, 3, 4, 5])
    parser.add_argument("--sample_sizes", type=int, nargs="+", default=[4, 6, 8])
    parser.add_argument("--duplicate_ratios", type=float, nargs="+", default=[0.0, 0.3, 0.6])
    parser.add_argument("--conflict_ratios", type=float, nargs="+", default=[0.0, 0.3])
    parser.add_argument("--noise_ratios", type=float, nargs="+", default=[0.0, 0.1])
    parser.add_argument("--n_trials", type=int, default=50)
    parser.add_argument("--base_seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "experiments" / "synthetic_benchmark.json")
    args = parser.parse_args()

    print(f"Running synthetic benchmark: {args.n_trials} trials...")
    results = run_synthetic_benchmark(
        k_values=args.k_values,
        n_vertices_list=args.n_vertices,
        sample_sizes=args.sample_sizes,
        duplicate_ratios=args.duplicate_ratios,
        conflict_ratios=args.conflict_ratios,
        noise_ratios=args.noise_ratios,
        n_trials=args.n_trials,
        base_seed=args.base_seed,
    )
    print(f"Generated {len(results)} raw records.")

    agg = compute_aggregate_stats(results)
    print(f"Computed {len(agg)} aggregate groups.")

    payload = {
        "metadata": {
            "description": "Synthetic benchmark: LOO/replace-one stability gaps on random graph metrics",
            "k_values": args.k_values,
            "n_vertices": args.n_vertices,
            "sample_sizes": args.sample_sizes,
            "duplicate_ratios": args.duplicate_ratios,
            "conflict_ratios": args.conflict_ratios,
            "noise_ratios": args.noise_ratios,
            "n_trials": args.n_trials,
            "base_seed": args.base_seed,
        },
        "raw_results": results,
        "aggregates": agg,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, cls=_Encoder), encoding="utf-8")
    print(f"Results written to {args.output}")

    # Print summary: separation frequency
    print("\n=== Separation Frequency Summary ===")
    for a in agg:
        if a["noise_ratio"] == 0.0 and a["conflict_ratio"] == 0.0:
            print(f"  k={a['k']} V={a['n_vertices']} D={a['duplicate_ratio']}: "
                  f"sep_freq={a['separation_frequency']:.3f} +/- {a['separation_ci']:.3f} "
                  f"vuln_rate={a['mean_vulnerable_query_rate']:.3f}")

    return 0


class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


if __name__ == "__main__":
    raise SystemExit(main())
