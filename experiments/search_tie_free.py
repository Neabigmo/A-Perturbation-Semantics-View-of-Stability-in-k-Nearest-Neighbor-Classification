"""Tie-free witness search for LOO vs replace-one separation.

This module re-checks TASK-007 separating samples and keeps only those for
which the fixed-sample maxima can be certified by predictions with unique
nearest neighbors before and after the relevant perturbation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from knn_stability.graph_metrics import adjacency_to_graph_metric  # noqa: E402
from knn_stability.knn import LabeledSample  # noqa: E402
from knn_stability.stability import (  # noqa: E402
    delete_one_sample,
    pointwise_loo_stability,
    pointwise_replace_one_stability,
    replace_one_sample,
)
from knn_stability.witnesses import (  # noqa: E402
    WitnessRecord,
    load_witness_search,
    save_witness_search,
)


def has_unique_nearest(sample: LabeledSample, query_point_idx: int) -> bool:
    """Return whether the query has a unique nearest sample occurrence."""
    sample_distances = [
        sample.metric.distances[query_point_idx, point_idx]
        for point_idx in sample.point_indices
    ]
    min_distance = min(sample_distances)
    return bool(sum(distance == min_distance for distance in sample_distances) == 1)


def verify_tie_free_loo(
    sample: LabeledSample,
    delete_index: int,
    query_point_idx: int,
) -> bool:
    """Check the tie-free condition for one LOO prediction pair."""
    if not has_unique_nearest(sample, query_point_idx):
        return False

    sample_deleted = delete_one_sample(sample, delete_index)
    if sample_deleted.n == 0:
        return False

    return has_unique_nearest(sample_deleted, query_point_idx)


def verify_tie_free_replace_one(
    sample: LabeledSample,
    replace_index: int,
    new_point_idx: int,
    new_label: int,
    query_point_idx: int,
) -> bool:
    """Check the tie-free condition for one replace-one prediction pair."""
    if not has_unique_nearest(sample, query_point_idx):
        return False

    sample_replaced = replace_one_sample(sample, replace_index, new_point_idx, new_label)
    return has_unique_nearest(sample_replaced, query_point_idx)


def adjacency_from_dict(adjacency_list: dict[str, list[int]] | dict[int, list[int]]) -> dict[int, set[int]]:
    """Convert a JSON adjacency list into the internal adjacency representation."""
    return {int(vertex): set(neighbors) for vertex, neighbors in adjacency_list.items()}


def sample_from_witness(witness: WitnessRecord) -> LabeledSample:
    """Reconstruct a labeled sample from a witness record."""
    adjacency = adjacency_from_dict(witness.adjacency_list)
    metric = adjacency_to_graph_metric(adjacency)
    return LabeledSample(
        metric=metric,
        point_indices=tuple(witness.sample_order),
        labels=tuple(witness.labels),
    )


def find_tie_free_loo_max(sample: LabeledSample) -> tuple[int, int]:
    """Find the tie-free LOO maximum and one delete index achieving it."""
    fallback_index = 0
    for delete_index in range(sample.n):
        query_point_idx = sample.point_indices[delete_index]
        if not verify_tie_free_loo(sample, delete_index, query_point_idx):
            continue

        fallback_index = delete_index
        if pointwise_loo_stability(sample, delete_index, k=1) == 1:
            return 1, delete_index

    return 0, fallback_index


def find_tie_free_replace_max(
    sample: LabeledSample,
) -> tuple[int, int, int, int, int, int]:
    """Find the tie-free replace-one maximum and one witness achieving it."""
    fallback = (0, 0, 0, 0, 0)
    for replace_index in range(sample.n):
        for new_point_idx in range(sample.metric.n):
            for new_label in (0, 1):
                for query_point_idx in range(sample.metric.n):
                    if not verify_tie_free_replace_one(
                        sample,
                        replace_index,
                        new_point_idx,
                        new_label,
                        query_point_idx,
                    ):
                        continue

                    for query_label in (0, 1):
                        fallback = (
                            replace_index,
                            new_point_idx,
                            new_label,
                            query_point_idx,
                            query_label,
                        )
                        if (
                            pointwise_replace_one_stability(
                                sample,
                                replace_index,
                                new_point_idx,
                                new_label,
                                query_point_idx,
                                query_label,
                                k=1,
                            )
                            == 1
                        ):
                            return 1, *fallback

    return 0, *fallback


def compute_tie_free_witness(witness: WitnessRecord) -> WitnessRecord | None:
    """Recompute tie-free maxima for a TASK-007 sample.

    Returns a new witness record if tie-free separation persists, otherwise
    returns ``None``.
    """
    sample = sample_from_witness(witness)
    loo_max, loo_index = find_tie_free_loo_max(sample)
    (
        replace_max,
        replace_index,
        replacement_point,
        replacement_label,
        query_point,
        query_label,
    ) = find_tie_free_replace_max(sample)

    if loo_max == replace_max:
        return None

    return WitnessRecord(
        num_vertices=witness.num_vertices,
        num_edges=witness.num_edges,
        adjacency_list=witness.adjacency_list,
        sample_order=witness.sample_order,
        labels=witness.labels,
        loo_max=loo_max,
        loo_witness_index=loo_index,
        replace_max=replace_max,
        replace_witness_index=replace_index,
        replace_witness_replacement_point=replacement_point,
        replace_witness_replacement_label=replacement_label,
        replace_witness_query_point=query_point,
        replace_witness_query_label=query_label,
        separation_gap=abs(loo_max - replace_max),
    )


def filter_tie_free_witnesses(
    witnesses: list[WitnessRecord],
) -> tuple[list[WitnessRecord], dict[str, int]]:
    """Recompute tie-free maxima for all TASK-007 separating samples."""
    tie_free_witnesses: list[WitnessRecord] = []
    stats = {
        "total_witnesses": len(witnesses),
        "tie_free_witnesses": 0,
        "rejected_tie_witnesses": 0,
    }

    for witness in witnesses:
        tie_free_witness = compute_tie_free_witness(witness)
        if tie_free_witness is None:
            stats["rejected_tie_witnesses"] += 1
            continue

        tie_free_witnesses.append(tie_free_witness)
        stats["tie_free_witnesses"] += 1

    return tie_free_witnesses, stats


def load_task7_witnesses(input_path: Path) -> list[WitnessRecord]:
    """Load TASK-007 witness records from JSON."""
    payload = load_witness_search(input_path)
    return [WitnessRecord(**record) for record in payload["witnesses"]]


def build_metadata(
    tie_free_witnesses: list[WitnessRecord],
    stats: dict[str, int],
    original_metadata: dict[str, object],
) -> dict[str, object]:
    """Build output metadata for TASK-008."""
    max_vertices = int(str(original_metadata["search_space"]["vertex_range"]).split()[-1])
    counts_by_vertices = {
        str(vertex_count): sum(
            1 for witness in tie_free_witnesses if witness.num_vertices == vertex_count
        )
        for vertex_count in range(1, max_vertices + 1)
    }

    witness_vertices = [witness.num_vertices for witness in tie_free_witnesses]
    minimal_vertex_count = min(witness_vertices) if witness_vertices else None
    no_solution_vertex_counts = [
        vertex_count
        for vertex_count in range(1, max_vertices + 1)
        if counts_by_vertices[str(vertex_count)] == 0
    ]
    task7_minimal_vertex_count = original_metadata.get("minimal_vertex_count")

    return {
        "task": "TASK-008",
        "description": "Search for tie-free LOO vs replace-one separation witnesses",
        "source": "TASK-007 samples with recomputed tie-free maxima",
        "tie_free_definition": {
            "condition": "for every prediction used in the accepted LOO and replace-one witness records, the query has a unique nearest sample occurrence",
            "applies_to": [
                "original sample before perturbation",
                "perturbed sample after LOO deletion",
                "perturbed sample after replace-one replacement",
            ],
        },
        "search_space": original_metadata.get("search_space"),
        "separation_target": original_metadata.get("separation_target"),
        "constraints": [
            "tie-free condition is checked on the predictions that certify the accepted witness record",
            "k=1 for all computations",
            "computational witnesses are not proofs",
            "no mathematical impossibility is claimed outside the searched space",
        ],
        "filter_stats": stats,
        "counts_by_vertices": counts_by_vertices,
        "minimal_vertex_count": minimal_vertex_count,
        "no_solution_vertex_counts": no_solution_vertex_counts,
        "task7_minimal_vertex_count": task7_minimal_vertex_count,
        "task7_minimal_survived": minimal_vertex_count == task7_minimal_vertex_count,
        "num_tie_free_witnesses": len(tie_free_witnesses),
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search for tie-free 1-NN LOO vs replace-one witnesses."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_separation_witnesses.json",
        help="Input JSON path from TASK-007.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_tie_free_witnesses.json",
        help="Output JSON path for tie-free witnesses.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the TASK-008 tie-free search."""
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")

    witnesses = load_task7_witnesses(args.input)
    original_metadata = load_witness_search(args.input)["metadata"]
    tie_free_witnesses, stats = filter_tie_free_witnesses(witnesses)
    metadata = build_metadata(tie_free_witnesses, stats, original_metadata)
    save_witness_search(args.output, metadata, tie_free_witnesses)

    print(f"Wrote {len(tie_free_witnesses)} tie-free witnesses to {args.output}")
    print(f"Minimal tie-free vertex count: {metadata['minimal_vertex_count']}")
    print(f"No-solution vertex counts: {metadata['no_solution_vertex_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
