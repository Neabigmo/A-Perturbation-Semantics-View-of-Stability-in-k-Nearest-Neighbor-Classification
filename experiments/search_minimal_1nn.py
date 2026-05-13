"""Minimal 1-NN witness search for LOO vs replace-one separation.

This module enumerates small graph metric examples and produces witness JSON
for 1-NN separation candidates, as specified in TASK-007.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from knn_stability.enumeration import (  # noqa: E402
    enumerate_binary_labelings,
    enumerate_connected_graphs,
    enumerate_vertex_orders,
)
from knn_stability.graph_metrics import adjacency_to_graph_metric  # noqa: E402
from knn_stability.knn import LabeledSample  # noqa: E402
from knn_stability.stability import (  # noqa: E402
    uniform_loo_stability,
    uniform_replace_one_stability,
)
from knn_stability.witnesses import (  # noqa: E402
    WitnessRecord,
    save_witness_search,
)


def compute_stability_metrics(
    sample: LabeledSample,
    k: int = 1,
) -> tuple[int, int, int, int, int, int, int, int]:
    """Compute fixed-sample LOO and replace-one maxima for one sample."""
    loo_max, loo_witness_index = uniform_loo_stability(sample, k)

    replace_max = 0
    replace_witness_index = 0
    replace_witness_point = 0
    replace_witness_label = 0
    replace_query_point = 0
    replace_query_label = 0

    for replace_index in range(sample.n):
        (
            candidate_max,
            candidate_point,
            candidate_label,
            candidate_query,
        ) = uniform_replace_one_stability(sample, replace_index, k)
        if candidate_max > replace_max:
            replace_max = candidate_max
            replace_witness_index = replace_index
            replace_witness_point = candidate_point
            replace_witness_label = candidate_label
            replace_query_point, replace_query_label = candidate_query

    return (
        loo_max,
        loo_witness_index,
        replace_max,
        replace_witness_index,
        replace_witness_point,
        replace_witness_label,
        replace_query_point,
        replace_query_label,
    )


def search_witnesses(max_vertices: int) -> tuple[list[WitnessRecord], dict[str, int]]:
    """Search the TASK-007 graph space for separation candidates."""
    witnesses: list[WitnessRecord] = []
    stats = {
        "total_graphs": 0,
        "total_samples_evaluated": 0,
        "skipped_undefined_samples": 0,
    }

    for num_vertices in range(1, max_vertices + 1):
        for adjacency in enumerate_connected_graphs(num_vertices):
            stats["total_graphs"] += 1
            metric = adjacency_to_graph_metric(adjacency)
            adjacency_list = {
                vertex: sorted(neighbors) for vertex, neighbors in adjacency.items()
            }

            for sample_order in enumerate_vertex_orders(num_vertices):
                for labels in enumerate_binary_labelings(num_vertices):
                    stats["total_samples_evaluated"] += 1
                    sample = LabeledSample(
                        metric=metric,
                        point_indices=sample_order,
                        labels=labels,
                    )
                    try:
                        (
                            loo_max,
                            loo_witness_index,
                            replace_max,
                            replace_witness_index,
                            replace_witness_point,
                            replace_witness_label,
                            replace_query_point,
                            replace_query_label,
                        ) = compute_stability_metrics(sample, k=1)
                    except ValueError:
                        stats["skipped_undefined_samples"] += 1
                        continue

                    if loo_max == replace_max:
                        continue

                    witnesses.append(
                        WitnessRecord(
                            num_vertices=num_vertices,
                            num_edges=sum(len(neighbors) for neighbors in adjacency.values())
                            // 2,
                            adjacency_list=adjacency_list,
                            sample_order=list(sample_order),
                            labels=list(labels),
                            loo_max=loo_max,
                            loo_witness_index=loo_witness_index,
                            replace_max=replace_max,
                            replace_witness_index=replace_witness_index,
                            replace_witness_replacement_point=replace_witness_point,
                            replace_witness_replacement_label=replace_witness_label,
                            replace_witness_query_point=replace_query_point,
                            replace_witness_query_label=replace_query_label,
                            separation_gap=abs(loo_max - replace_max),
                        )
                    )

    return witnesses, stats


def build_metadata(
    max_vertices: int,
    witnesses: list[WitnessRecord],
    stats: dict[str, int],
) -> dict[str, object]:
    """Build JSON metadata for the TASK-007 search output."""
    counts_by_vertices: dict[str, int] = {}
    for vertex_count in range(1, max_vertices + 1):
        counts_by_vertices[str(vertex_count)] = sum(
            1 for witness in witnesses if witness.num_vertices == vertex_count
        )

    witness_vertices = [witness.num_vertices for witness in witnesses]
    minimal_vertex_count = min(witness_vertices) if witness_vertices else None
    no_solution_vertex_counts = [
        vertex_count
        for vertex_count in range(1, max_vertices + 1)
        if counts_by_vertices[str(vertex_count)] == 0
    ]

    return {
        "task": "TASK-007",
        "description": "Search for minimal 1-NN LOO vs replace-one separation witnesses",
        "search_space": {
            "graph_type": "connected simple undirected labeled graphs",
            "vertex_range": f"1 to {max_vertices}",
            "sample_constraint": "each graph vertex appears exactly once (no duplicates)",
            "labelings": "all binary labelings",
            "orderings": "all permutations of vertex set",
        },
        "separation_target": {
            "fixed_sample_loo_max": "max over delete indices of |loss_original - loss_deleted|",
            "fixed_sample_replace_one_max": "max over replace indices of |loss_original - loss_replaced|",
            "k": 1,
        },
        "constraints": [
            "sample is an ordered tuple with each graph vertex exactly once",
            "no duplicate sample occurrences in this TASK-007 search",
            "k=1 for all computations",
            "computational witnesses are not proofs",
            "tie-breaking: distance then sample index, label ties favor 0",
        ],
        "search_stats": stats,
        "counts_by_vertices": counts_by_vertices,
        "minimal_vertex_count": minimal_vertex_count,
        "no_solution_vertex_counts": no_solution_vertex_counts,
        "num_witnesses_found": len(witnesses),
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search for minimal 1-NN LOO vs replace-one separation witnesses."
    )
    parser.add_argument(
        "--max_vertices",
        type=int,
        required=True,
        help="Maximum number of vertices to search (inclusive).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_separation_witnesses.json",
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the TASK-007 witness search."""
    args = parse_args()
    if args.max_vertices < 1:
        raise SystemExit("--max_vertices must be at least 1.")

    witnesses, stats = search_witnesses(args.max_vertices)
    metadata = build_metadata(args.max_vertices, witnesses, stats)
    save_witness_search(args.output, metadata, witnesses)

    print(f"Wrote {len(witnesses)} witnesses to {args.output}")
    if metadata["minimal_vertex_count"] is not None:
        print(f"Minimal witness vertex count: {metadata['minimal_vertex_count']}")
    print(f"No-solution vertex counts: {metadata['no_solution_vertex_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
