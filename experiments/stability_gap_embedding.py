"""Embedding-space stability experiments on Digits dataset.

Tests whether dimensionality reduction (PCA, autoencoder) affects the
LOO/replace-one stability gap.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from knn_stability.knn import LabeledSample
from knn_stability.metrics import FiniteMetricSpace
from knn_stability.stability import (
    pointwise_loo_stability,
    pointwise_replace_one_stability,
)


def load_digits():
    """Load sklearn digits dataset."""
    from sklearn.datasets import load_digits
    data = load_digits()
    X = data.data.astype(np.float64)
    y = data.target.astype(np.int64)
    # Binary: digit 0 vs rest
    y_bin = np.where(y == 0, 0, 1).astype(np.int64)
    return X, y_bin


def pca_reduce(X: np.ndarray, n_components: int, seed: int = 42) -> np.ndarray:
    """Reduce dimensionality with PCA."""
    from sklearn.decomposition import PCA
    pca = PCA(n_components=n_components, random_state=seed)
    return pca.fit_transform(X)


def autoencoder_reduce(X: np.ndarray, n_components: int, seed: int = 42) -> np.ndarray:
    """Reduce dimensionality with a simple autoencoder (sklearn MLP)."""
    from sklearn.neural_network import MLPRegressor
    rng = np.random.RandomState(seed)
    # Simple 3-layer autoencoder
    hidden = max(n_components * 2, 16)
    ae = MLPRegressor(
        hidden_layer_sizes=(hidden, n_components, hidden),
        activation="relu",
        max_iter=500,
        random_state=seed,
        early_stopping=True,
    )
    # Train: input = output
    ae.fit(X, X)
    # Extract encoder output
    # We use the activations: pass through first hidden layer, then bottleneck
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Manual forward pass for the bottleneck layer
    W0 = ae.coefs_[0]
    b0 = ae.intercepts_[0]
    h0 = np.maximum(0, X_scaled @ W0 + b0)

    W1 = ae.coefs_[1]
    b1 = ae.intercepts_[1]
    bottleneck = h0 @ W1 + b1
    return bottleneck


def compute_embedding_gap(
    X: np.ndarray,
    y: np.ndarray,
    k: int,
    seed: int = 42,
    max_points: int = 100,
) -> dict:
    """Compute LOO/replace-one gap on embedded data."""
    n = min(X.shape[0], max_points)
    rng = np.random.RandomState(seed)
    idx = rng.choice(X.shape[0], n, replace=False)
    X_sub = X[idx]
    y_sub = y[idx]

    # Compute Euclidean distance matrix
    dist = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.sqrt(np.sum((X_sub[i] - X_sub[j]) ** 2))
            dist[i, j] = d
            dist[j, i] = d

    metric = FiniteMetricSpace(points=list(range(n)), distances=dist)
    sample = LabeledSample(
        metric=metric,
        point_indices=tuple(range(n)),
        labels=tuple(int(l) for l in y_sub),
    )

    # LOO profile
    loo_vals = []
    for i in range(n):
        try:
            val = pointwise_loo_stability(sample, i, k)
        except (ValueError, IndexError):
            val = 0
        loo_vals.append(val)

    max_loo = max(loo_vals)

    # Replace-one: same-point label flips
    rep_vals = []
    for i in range(n):
        orig_point = sample.point_indices[i]
        flipped_label = 1 - sample.labels[i]
        for q_idx in range(n):
            for q_label in (0, 1):
                try:
                    val = pointwise_replace_one_stability(
                        sample, i, orig_point, flipped_label, q_idx, q_label, k
                    )
                except (ValueError, IndexError):
                    val = 0
                rep_vals.append(val)

    max_rep = max(rep_vals) if rep_vals else 0

    return {
        "n": n,
        "k": k,
        "max_loo": int(max_loo),
        "max_replace_one": int(max_rep),
        "loo_rep_gap": int(max_rep - max_loo),
        "separation_found": int(max_loo == 0 and max_rep == 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Embedding-space stability experiments."
    )
    parser.add_argument("--k_values", type=int, nargs="+", default=[1, 3, 5])
    parser.add_argument("--n_components_list", type=int, nargs="+", default=[5, 10, 20])
    parser.add_argument("--n_replicates", type=int, default=3)
    parser.add_argument("--base_seed", type=int, default=42)
    parser.add_argument("--max_points", type=int, default=100)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "outputs" / "experiments" / "embedding_benchmark.json")
    args = parser.parse_args()

    print("Loading Digits dataset...")
    X, y = load_digits()
    print(f"  Shape: {X.shape}")

    results = []

    # Original representation
    print("Testing original (64d) representation...")
    for k in args.k_values:
        for rep in range(args.n_replicates):
            seed = args.base_seed + rep
            profile = compute_embedding_gap(X, y, k, seed=seed, max_points=args.max_points)
            results.append({
                "representation": "original_64d",
                "n_components": 64,
                "replicate": rep,
                **profile,
            })

    # PCA representations
    for n_comp in args.n_components_list:
        print(f"Testing PCA ({n_comp}d) representation...")
        X_pca = pca_reduce(X, n_comp)
        for k in args.k_values:
            for rep in range(args.n_replicates):
                seed = args.base_seed + rep
                profile = compute_embedding_gap(X_pca, y, k, seed=seed, max_points=args.max_points)
                results.append({
                    "representation": f"pca_{n_comp}d",
                    "n_components": n_comp,
                    "replicate": rep,
                    **profile,
                })

    # Autoencoder representation (only for small n_comp to keep runtime manageable)
    for n_comp in args.n_components_list[:2]:  # Only 5 and 10
        print(f"Testing AE ({n_comp}d) representation...")
        X_ae = autoencoder_reduce(X, n_comp)
        for k in args.k_values:
            for rep in range(args.n_replicates):
                seed = args.base_seed + rep
                profile = compute_embedding_gap(X_ae, y, k, seed=seed, max_points=args.max_points)
                results.append({
                    "representation": f"ae_{n_comp}d",
                    "n_components": n_comp,
                    "replicate": rep,
                    **profile,
                })

    payload = {
        "metadata": {
            "description": "Embedding stability benchmark on Digits dataset",
            "k_values": args.k_values,
            "n_components_list": args.n_components_list,
            "n_replicates": args.n_replicates,
            "max_points": args.max_points,
        },
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, cls=_Encoder), encoding="utf-8")
    print(f"Results written to {args.output}")

    # Summary
    print("\n=== Summary ===")
    from collections import defaultdict
    by_rep = defaultdict(list)
    for r in results:
        key = (r["representation"], r["k"])
        by_rep[key].append(r)

    for key, group in sorted(by_rep.items()):
        rep_name, k = key
        gaps = [r["loo_rep_gap"] for r in group]
        sep_count = sum(1 for r in group if r["separation_found"])
        print(f"  {rep_name} k={k}: mean_gap={np.mean(gaps):.3f} "
              f"sep_freq={sep_count/len(group):.3f}")

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
