"""Generate experiment figures for the paper.

Produces figures with consistent metrics:
- Fig A (synthetic): separation frequency heatmap + vulnerable-query rate
- Fig B (tabular): grouped bar plot, all 4 datasets, all k=1,3,5,7
- Fig C (diagnostic): precision/recall summary
- Fig D (margin): vulnerable-query rate diagnostic illustration

All figures use the same two metrics throughout:
1. Separation frequency: Pr[max_loo = 0, max_replace_one = 1]
2. Vulnerable-query rate: Pr_x[|M_k(S,x)| <= 2]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 12,
        "figure.titlesize": 13,
        "axes.labelsize": 10,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
    })
    return plt


def load_data(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return None


def generate_separation_heatmap(output_dir: Path):
    """Heatmap of separation frequency by k and duplicate ratio.

    This is the replacement for the old 'mean LOO/Replace gap' heatmap.
    Now shows separation frequency (matching Table 4).
    """
    data = load_data(ROOT / "outputs" / "experiments" / "synthetic_benchmark.json")

    plt = setup_matplotlib()

    if data is None or not data.get("aggregates"):
        print("WARNING: No synthetic data. Generating placeholder.")
        _placeholder_sep_heatmap(output_dir, plt)
        return

    agg = data["aggregates"]

    # Filter to no-noise, no-conflict baseline
    filtered = [a for a in agg
                if a.get("noise_ratio", 0) == 0.0
                and a.get("conflict_ratio", 0) == 0.0
                and a.get("n_vertices", 2) == 2]

    if not filtered:
        filtered = agg[:10]

    k_values = sorted(set(a["k"] for a in filtered))
    d_values = sorted(set(a["duplicate_ratio"] for a in filtered))

    sep_matrix = np.full((len(k_values), len(d_values)), np.nan)
    vuln_matrix = np.full((len(k_values), len(d_values)), np.nan)

    for a in filtered:
        i = k_values.index(a["k"])
        j = d_values.index(a["duplicate_ratio"])
        sep_matrix[i, j] = a["separation_frequency"]
        vuln_matrix[i, j] = a.get("mean_vulnerable_query_rate", 0)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Panel A: separation frequency
    ax = axes[0]
    im = ax.imshow(sep_matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(d_values)))
    ax.set_xticklabels([f"{d:.1f}" for d in d_values])
    ax.set_yticks(range(len(k_values)))
    ax.set_yticklabels([str(k) for k in k_values])
    ax.set_xlabel("Duplicate ratio")
    ax.set_ylabel("k")
    ax.set_title("Separation frequency")

    for i in range(len(k_values)):
        for j in range(len(d_values)):
            val = sep_matrix[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="white" if val > 0.5 else "black", fontsize=9)

    plt.colorbar(im, ax=ax, fraction=0.046)

    # Panel B: vulnerable-query rate
    ax = axes[1]
    im = ax.imshow(vuln_matrix, cmap="Blues", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(d_values)))
    ax.set_xticklabels([f"{d:.1f}" for d in d_values])
    ax.set_yticks(range(len(k_values)))
    ax.set_yticklabels([str(k) for k in k_values])
    ax.set_xlabel("Duplicate ratio")
    ax.set_ylabel("k")
    ax.set_title("Vulnerable-query rate")

    for i in range(len(k_values)):
        for j in range(len(d_values)):
            val = vuln_matrix[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="white" if val > 0.35 else "black", fontsize=9)

    plt.colorbar(im, ax=ax, fraction=0.046)

    fig.suptitle("Synthetic Graph-Metric Benchmark (no noise, no conflict)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_dir / "synthetic_gap_heatmap.png", dpi=200)
    fig.savefig(output_dir / "synthetic_gap_heatmap.pdf")
    plt.close(fig)
    print("Generated synthetic_gap_heatmap (separation frequency + vulnerable-query rate)")


def _placeholder_sep_heatmap(output_dir: Path, plt):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    k_vals = [1, 3, 5, 7]
    d_vals = [0.0, 0.3, 0.6]

    sep_data = np.array([
        [0.27, 0.42, 0.60],
        [0.18, 0.30, 0.50],
        [0.10, 0.22, 0.40],
        [0.05, 0.15, 0.30],
    ])
    vuln_data = np.array([
        [0.35, 0.50, 0.70],
        [0.25, 0.38, 0.58],
        [0.18, 0.28, 0.48],
        [0.12, 0.20, 0.38],
    ])

    for ax, data, title, cmap in [
        (axes[0], sep_data, "Separation frequency (placeholder)", "YlOrRd"),
        (axes[1], vuln_data, "Vulnerable-query rate (placeholder)", "Blues"),
    ]:
        im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=1)
        ax.set_xticks(range(len(d_vals)))
        ax.set_xticklabels([f"{d:.1f}" for d in d_vals])
        ax.set_yticks(range(len(k_vals)))
        ax.set_yticklabels([str(k) for k in k_vals])
        ax.set_xlabel("Duplicate ratio")
        ax.set_ylabel("k")
        ax.set_title(title)
        for i in range(len(k_vals)):
            for j in range(len(d_vals)):
                ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center",
                        color="white" if data[i, j] > 0.5 else "black", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.046)

    fig.tight_layout()
    fig.savefig(output_dir / "synthetic_gap_heatmap.png", dpi=200)
    fig.savefig(output_dir / "synthetic_gap_heatmap.pdf")
    plt.close(fig)
    print("Generated placeholder synthetic_gap_heatmap")


def generate_tabular_gap_plot(output_dir: Path):
    """Grouped bar plot: separation frequency for all 4 datasets, all k=1,3,5,7 with CI."""
    data = load_data(ROOT / "outputs" / "experiments" / "tabular_benchmark.json")

    plt = setup_matplotlib()

    if data is None or not data.get("aggregates"):
        print("WARNING: No tabular data. Generating placeholder.")
        _placeholder_tabular_plot(output_dir, plt)
        return

    agg = data["aggregates"]
    if not agg:
        _placeholder_tabular_plot(output_dir, plt)
        return

    datasets = sorted(set(a["dataset"] for a in agg))
    k_values = sorted(set(a["k"] for a in agg))

    # Human-readable names
    name_map = {
        "iris": "Iris",
        "wine": "Wine",
        "breast_cancer": "Breast Cancer",
        "digits": "Digits",
    }
    ds_labels = [name_map.get(d, d) for d in datasets]

    colors = ["#3182ce", "#63a3d6", "#9bc3e8", "#c9dff5"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panel A: Separation frequency with CIs
    ax = axes[0]
    width = 0.2
    x = np.arange(len(datasets))

    for idx, k in enumerate(k_values):
        means = []
        cis = []
        for ds in datasets:
            match = [a for a in agg if a["dataset"] == ds and a["k"] == k]
            means.append(match[0]["separation_frequency"] if match else 0)
            cis.append(match[0].get("separation_ci", 0) if match else 0)
        ax.bar(x + idx * width, means, width, yerr=cis,
               label=f"k={k}", capsize=3, color=colors[idx % len(colors)],
               error_kw={"linewidth": 1.5})

    ax.set_xticks(x + width * (len(k_values) - 1) / 2)
    ax.set_xticklabels(ds_labels, rotation=15, ha="right")
    ax.set_ylabel("Separation frequency")
    ax.set_xlabel("Dataset")
    ax.legend(title="k", fontsize=9)
    ax.set_title("LOO/Replace-one separation frequency")
    ax.set_ylim(0, 1.1)

    # Panel B: Vulnerable-query rate with CIs
    ax = axes[1]
    for idx, k in enumerate(k_values):
        means = []
        cis = []
        for ds in datasets:
            match = [a for a in agg if a["dataset"] == ds and a["k"] == k]
            means.append(match[0].get("mean_vulnerable_query_rate", 0) if match else 0)
            cis.append(match[0].get("vuln_rate_ci", 0) if match else 0)
        ax.bar(x + idx * width, means, width, yerr=cis,
               label=f"k={k}", capsize=3, color=colors[idx % len(colors)],
               error_kw={"linewidth": 1.5})

    ax.set_xticks(x + width * (len(k_values) - 1) / 2)
    ax.set_xticklabels(ds_labels, rotation=15, ha="right")
    ax.set_ylabel("Vulnerable-query rate")
    ax.set_xlabel("Dataset")
    ax.legend(title="k", fontsize=9)
    ax.set_title("Vulnerable-query rate $|M_k(S,x)| \\leq 2$")
    ax.set_ylim(0, 1.1)

    fig.suptitle("Tabular Benchmark: LOO/Replace-one Stability Gap (50 replicates, 95% CI)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_dir / "tabular_gap_by_dataset.png", dpi=200)
    fig.savefig(output_dir / "tabular_gap_by_dataset.pdf")
    plt.close(fig)
    print("Generated tabular_gap_by_dataset (4 datasets, all k)")


def _placeholder_tabular_plot(output_dir: Path, plt):
    datasets = ["Iris", "Wine", "Breast Cancer", "Digits"]
    k_values = [1, 3, 5, 7]
    colors = ["#3182ce", "#63a3d6", "#9bc3e8", "#c9dff5"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    width = 0.2
    x = np.arange(len(datasets))

    placeholder_sep = {
        1: [0.33, 0.67, 0.33, 1.00],
        3: [0.00, 0.33, 0.00, 1.00],
        5: [0.00, 0.00, 0.00, 0.67],
        7: [0.00, 0.00, 0.00, 0.33],
    }
    placeholder_vuln = {
        1: [0.40, 0.70, 0.35, 0.95],
        3: [0.05, 0.35, 0.05, 0.85],
        5: [0.00, 0.15, 0.00, 0.70],
        7: [0.00, 0.05, 0.00, 0.40],
    }

    for ax, data, title in [
        (axes[0], placeholder_sep, "Separation frequency (placeholder)"),
        (axes[1], placeholder_vuln, "Vulnerable-query rate (placeholder)"),
    ]:
        for idx, k in enumerate(k_values):
            ax.bar(x + idx * width, data[k], width,
                   label=f"k={k}", color=colors[idx])
        ax.set_xticks(x + width * (len(k_values) - 1) / 2)
        ax.set_xticklabels(datasets, rotation=15, ha="right")
        ax.set_ylabel("Rate")
        ax.set_xlabel("Dataset")
        ax.legend(title="k", fontsize=9)
        ax.set_title(title)
        ax.set_ylim(0, 1.1)

    fig.suptitle("Tabular Benchmark (placeholder)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_dir / "tabular_gap_by_dataset.png", dpi=200)
    fig.savefig(output_dir / "tabular_gap_by_dataset.pdf")
    plt.close(fig)
    print("Generated placeholder tabular_gap_by_dataset")


def generate_diagnostic_summary(output_dir: Path):  # pragma: no cover — exact by theorem for odd k
    """Diagnostic precision/recall summary figure."""
    data = load_data(ROOT / "outputs" / "experiments" / "tabular_benchmark.json")
    plt = setup_matplotlib()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    if data and data.get("aggregates"):
        agg = data["aggregates"]
        datasets = sorted(set(a["dataset"] for a in agg))
        k_values = sorted(set(a["k"] for a in agg))
        name_map = {
            "iris": "Iris", "wine": "Wine",
            "breast_cancer": "Breast Cancer", "digits": "Digits",
        }
        ds_labels = [name_map.get(d, d) for d in datasets]
        colors = ["#3182ce", "#63a3d6", "#9bc3e8", "#c9dff5"]

        for ax, metric, title in [
            (axes[0], "mean_diagnostic_precision", "Precision"),
            (axes[1], "mean_diagnostic_recall", "Recall"),
        ]:
            width = 0.2
            x = np.arange(len(datasets))
            for idx, k in enumerate(k_values):
                vals = []
                for ds in datasets:
                    match = [a for a in agg if a["dataset"] == ds and a["k"] == k]
                    vals.append(match[0].get(metric, 0) if match else 0)
                ax.bar(x + idx * width, vals, width,
                       label=f"k={k}", color=colors[idx])

            ax.set_xticks(x + width * (len(k_values) - 1) / 2)
            ax.set_xticklabels(ds_labels, rotation=15, ha="right")
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.set_xlabel("Dataset")
            ax.legend(title="k", fontsize=9)
            ax.set_title(f"Diagnostic {title}")
            ax.set_ylim(0, 1.1)

        fig.suptitle("Diagnostic Performance: $|M| \\leq 2$ as Predictor of Replace-One Flip",
                     fontsize=12)
    else:
        for ax in axes:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                    transform=ax.transAxes, fontsize=12)
        fig.suptitle("Diagnostic Summary (no data)", fontsize=12)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_dir / "diagnostic_example.png", dpi=200)
    fig.savefig(output_dir / "diagnostic_example.pdf")
    plt.close(fig)
    print("Generated diagnostic_example (precision/recall)")


def generate_margin_distribution(output_dir: Path):
    """Margin distribution figure showing vulnerability boundary."""
    plt = setup_matplotlib()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    k_values = [1, 3, 5]
    rng = np.random.RandomState(42)

    for idx, k in enumerate(k_values):
        ax = axes[idx]
        if k == 1:
            margins = rng.choice([-1, 1], size=200, p=[0.4, 0.6])
        elif k == 3:
            margins = rng.choice([-3, -1, 1, 3], size=200, p=[0.1, 0.3, 0.4, 0.2])
        else:
            margins = rng.choice([-5, -3, -1, 1, 3, 5], size=200,
                                  p=[0.05, 0.10, 0.20, 0.35, 0.20, 0.10])

        ax.hist(margins, bins=k + 2, color="#3182ce", edgecolor="#1f2937", alpha=0.8)
        ax.axvline(-2, color="#e53e3e", linestyle="--", linewidth=1.5)
        ax.axvline(2, color="#e53e3e", linestyle="--", linewidth=1.5)
        ax.axvspan(-2, 2, alpha=0.1, color="#e53e3e", label="Vulnerable")
        n_vuln = int(np.sum(np.abs(margins) <= 2))
        ax.set_title(f"k={k}: {n_vuln}/{len(margins)} vulnerable "
                     f"({100*n_vuln/len(margins):.0f}%)")
        ax.set_xlabel("Margin $M_k(S,x)$")
        ax.set_ylabel("Count")
        if idx == 2:
            ax.legend(fontsize=8)

    fig.suptitle("Margin Distribution — Queries with $|M| \\leq 2$ are Potentially Vulnerable",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_dir / "margin_distribution.png", dpi=200)
    fig.savefig(output_dir / "margin_distribution.pdf")
    plt.close(fig)
    print("Generated margin_distribution")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate experiment figures.")
    parser.add_argument("--output_dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    generate_separation_heatmap(args.output_dir)
    generate_tabular_gap_plot(args.output_dir)
    # generate_diagnostic_summary disabled: for odd k the |M| <= 2 condition
    # is exact by theorem, so precision = recall = 1.0 identically
    # generate_diagnostic_summary(args.output_dir)
    generate_margin_distribution(args.output_dir)

    print(f"All experiment figures generated in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
