"""Minimal 1-NN witness search for LOO vs replace-one separation.

This module enumerates small graph metric examples and produces witness JSON
for 1-NN separation candidates, as specified in TASK-007.

Search space for --max_vertices M:
- all connected simple undirected labeled graphs on vertex sets {0, ..., v-1}
  for each 1 <= v <= M
- all binary labelings of the ordered sample
- all orderings of the vertex set as the sample order

Separation target:
- fixed-sample brute-force LOO maximum versus
- fixed-sample brute-force replace-one maximum,
both at k=1, using the accepted semantics from stability.py.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Iterator

import networkx as nx

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knn_stability.graph_metrics import adjacency_to_graph_metric
from knn_stability.knn import LabeledSample
from knn_stability.stability import (
    uniform_loo_stability,
    uniform_replace_one_stability,
)


@dataclass
class WitnessRecord:
    """Record for a potential LOO vs replace-one separation witness."""
    num_vertices: int
    num_edges: int
    adjacency_list: dict[int, list[int]]
    sample_order: list[int]  # vertex order in sample
    labels: list[int]  # label for each vertex in sample order
    loo_max: int  # max over delete indices
    loo_witness_index: int  # delete_index achieving loo_max
    replace_max: int  # max over all replace indices
    replace_witness_index: int  # replace_index achieving replace_max
    replace_witness_replacement_point: int
    replace_witness_replacement_label: int
    replace_witness_query_point: int
    replace_witness_query_label: int
    separation_gap: int  # abs(loo_max - replace_max)


def enumerate_connected_graphs(num_vertices: int) -> Iterator[dict[int, set[int]]]:
    """Generate all connected simple undirected graphs on vertices 0..n-1.

    Parameters
    ----------
    num_vertices : int
        Number of vertices.

    Yields
    ------
    dict[int, set[int]]
        Adjacency list representation of each connected graph.
    """
    vertices = list(range(num_vertices))
    edges = list(itertools.combinations(vertices, 2))

    # Generate all possible edge subsets
    for edge_mask in range(1 << len(edges)):
        adjacency: dict[int, set[int]] = {v: set() for v in vertices}

        for i, (u, v) in enumerate(edges):
            if edge_mask & (1 << i):
                adjacency[u].add(v)
                adjacency[v].add(u)

        # Check connectivity using NetworkX
        G = nx.Graph()
        G.add_nodes_from(vertices)
        for u, v in edges:
            if u in adjacency[v]:  # edge exists
                G.add_edge(u, v)

        if nx.is_connected(G):
            yield adjacency


def compute_stability_metrics(
    metric,  # FiniteMetricSpace
    sample_order: tuple[int, ...],
    labels: tuple[int, ...],
    k: int = 1,
) -> tuple[int, int, int, int, int, int]:
    """Compute LOO and replace-one stability maxima for a sample.

    Returns
    -------
    tuple[int, int, int, int, int, int]
        (loo_max, loo_witness_index,
         replace_max, replace_witness_index,
         replace_replacement_point, replace_replacement_label,
         replace_query_point, replace_query_label)
    """
    sample = LabeledSample(
        metric=metric,
        point_indices=sample_order,
        labels=labels,
    )

    # LOO stability: max over delete indices
    loo_max, loo_witness = uniform_loo_stability(sample, k)

    # Replace-one stability: max over replace indices
    replace_max = 0
    best_replace = (0, 0, 0, (0, 0))  # (point, label, index, query)
    for replace_idx in range(sample.n):
        rep_max, rep_point, rep_label, rep_query = uniform_replace_one_stability(
            sample, replace_idx, k
        )
        if rep_max > replace_max:
            replace_max = rep_max
            best_replace = (rep_point, rep_label, replace_idx, rep_query)

    rep_point, rep_label, replace_witness, (rep_query_point, rep_query_label) = best_replace

    return (
        loo_max, loo_witness,
        replace_max, replace_witness,
        rep_point, rep_label, rep_query_point, rep_query_label
    )


def search_witnesses(max_vertices: int, output_dir: str) -> list[WitnessRecord]:
    """Search for LOO vs replace-one separation witnesses.

    Parameters
    ----------
    max_vertices : int
        Maximum number of vertices to search (inclusive).
    output_dir : str
        Directory to save witness JSON files.

    Returns
    -------
    list[WitnessRecord]
        List of witness records where LOO max != replace-one max.
    """
    witnesses: list[WitnessRecord] = []
    search_stats = {
        "total_graphs": 0,
        "total_samples_per_graph": 0,
        "graphs_with_separation": 0,
    }

    for num_vertices in range(1, max_vertices + 1):
        print(f"Searching graphs with {num_vertices} vertices...", file=sys.stderr)

        # Generate all connected graphs
        for adjacency in enumerate_connected_graphs(num_vertices):
            search_stats["total_graphs"] += 1

            try:
                metric = adjacency_to_graph_metric(adjacency)
            except ValueError:
                # Skip disconnected or invalid graphs
                continue

            # Convert adjacency to list format for JSON
            adj_list = {k: sorted(list(v)) for k, v in adjacency.items()}

            vertices = list(range(num_vertices))

            # All orderings of vertices as sample
            for sample_order in itertools.permutations(vertices):
                # All binary labelings
                for label_mask in range(1 << num_vertices):
                    labels = tuple((label_mask >> i) & 1 for i in range(num_vertices))

                    search_stats["total_samples_per_graph"] += 1

                    # Compute stability metrics
                    try:
                        (
                            loo_max, loo_witness,
                            rep_max, rep_witness,
                            rep_point, rep_label, rep_query_point, rep_query_label
                        ) = compute_stability_metrics(
                            metric,
                            sample_order,
                            labels,
                            k=1,
                        )
                    except (ValueError, IndexError):
                        # Skip invalid configurations
                        continue

                    # Check for separation
                    if loo_max != rep_max:
                        search_stats["graphs_with_separation"] += 1

                        record = WitnessRecord(
                            num_vertices=num_vertices,
                            num_edges=sum(len(v) for v in adjacency.values()) // 2,
                            adjacency_list=adj_list,
                            sample_order=list(sample_order),
                            labels=list(labels),
                            loo_max=loo_max,
                            loo_witness_index=loo_witness,
                            replace_max=rep_max,
                            replace_witness_index=rep_witness,
                            replace_witness_replacement_point=rep_point,
                            replace_witness_replacement_label=rep_label,
                            replace_witness_query_point=rep_query_point,
                            replace_witness_query_label=rep_query_label,
                            separation_gap=abs(loo_max - rep_max),
                        )
                        witnesses.append(record)

    # Print search statistics
    print(
        f"\nSearch Statistics:\n"
        f"  Total graphs searched: {search_stats['total_graphs']}\n"
        f"  Total samples evaluated: {search_stats['total_samples_per_graph']}\n"
        f"  Graphs with separation found: {search_stats['graphs_with_separation']}\n",
        file=sys.stderr
    )

    return witnesses


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search for minimal 1-NN LOO vs replace-one separation witnesses."
    )
    parser.add_argument(
        "--max_vertices",
        type=int,
        required=True,
        help="Maximum number of vertices to search (inclusive)."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs/witnesses",
        help="Directory to save witness JSON files."
    )
    parser.add_argument(
        "--min_gap",
        type=int,
        default=1,
        help="Minimum separation gap to report."
    )
    args = parser.parse_args()

    if args.max_vertices < 1:
        parser.error("--max_vertices must be at least 1")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print(
        f"Searching for LOO vs replace-one separation witnesses...\n"
        f"Max vertices: {args.max_vertices}\n"
        f"Output directory: {args.output_dir}\n",
        file=sys.stderr
    )

    # Run search
    witnesses = search_witnesses(args.max_vertices, args.output_dir)

    # Filter by minimum gap
    witnesses = [w for w in witnesses if w.separation_gap >= args.min_gap]

    # Save all witnesses to single JSON
    output_file = os.path.join(args.output_dir, "1nn_separation_witnesses.json")

    # Convert dataclass instances to dicts for JSON serialization
    witness_data = [asdict(w) for w in witnesses]

    metadata = {
        "task": "TASK-007",
        "description": "Search for minimal 1-NN LOO vs replace-one separation witnesses",
        "search_space": {
            "graph_type": "connected simple undirected labeled graphs",
            "vertex_range": f"1 to {args.max_vertices}",
            "sample_constraint": "each graph vertex appears exactly once (no duplicates)",
            "labelings": "all binary labelings",
            "orderings": "all permutations of vertex set",
        },
        "separation_target": {
            "fixed_sample_loo_max": "max over delete indices of |loss_original - loss_deleted|",
            "fixed_sample_replace_one_max": "max over replace indices of |loss_original - loss_replaced|",
            "k": 1,
        },
        "min_gap_filter": args.min_gap,
        "num_witnesses_found": len(witnesses),
        "constraints": [
            "sample is ordered tuple with each vertex exactly once",
            "no duplicate sample occurrences in search",
            "k=1 for all computations",
            "computational witnesses are not proofs",
            "tie-breaking: distance then index, label ties favor 0",
        ],
    }

    output_data = {
        "metadata": metadata,
        "witnesses": witness_data,
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"Witnesses found: {len(witnesses)}")

    if witnesses:
        print("\nFirst witness (sorted by vertices, edges, order):")
        print(json.dumps(output_data["witnesses"][0], indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())

