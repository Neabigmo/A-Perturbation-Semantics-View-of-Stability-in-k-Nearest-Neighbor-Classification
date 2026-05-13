from pathlib import Path

from experiments.certify_minimality import build_certificate
from experiments.search_minimal_1nn import build_metadata, search_witnesses
from knn_stability.enumeration import (
    enumerate_binary_labelings,
    enumerate_connected_graphs,
)
from knn_stability.witnesses import (
    WitnessRecord,
    load_witness_search,
    save_witness_search,
)


def test_enumerate_connected_graphs_counts_small_n() -> None:
    assert len(list(enumerate_connected_graphs(1))) == 1
    assert len(list(enumerate_connected_graphs(2))) == 1
    assert len(list(enumerate_connected_graphs(3))) == 4


def test_enumerate_binary_labelings_two_items() -> None:
    assert list(enumerate_binary_labelings(2)) == [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
    ]


def test_witness_search_roundtrip(tmp_path: Path) -> None:
    witness = WitnessRecord(
        num_vertices=2,
        num_edges=1,
        adjacency_list={0: [1], 1: [0]},
        sample_order=[0, 1],
        labels=[0, 0],
        loo_max=0,
        loo_witness_index=0,
        replace_max=1,
        replace_witness_index=0,
        replace_witness_replacement_point=0,
        replace_witness_replacement_label=1,
        replace_witness_query_point=0,
        replace_witness_query_label=0,
        separation_gap=1,
    )
    output_path = tmp_path / "witnesses.json"
    metadata = {"task": "TASK-007", "num_witnesses_found": 1}

    save_witness_search(output_path, metadata, [witness])
    payload = load_witness_search(output_path)

    assert payload["metadata"] == metadata
    assert payload["witnesses"][0]["separation_gap"] == 1


def test_search_minimal_1nn_finds_two_vertex_witness() -> None:
    witnesses, stats = search_witnesses(2)
    metadata = build_metadata(2, witnesses, stats)

    assert stats["total_graphs"] == 2
    assert metadata["minimal_vertex_count"] == 2
    assert metadata["no_solution_vertex_counts"] == [1]
    assert len(witnesses) == 4
    assert all(witness.loo_max == 0 for witness in witnesses)
    assert all(witness.replace_max == 1 for witness in witnesses)


# Tests for TASK-008 tie-free witness search

from experiments.search_tie_free import (
    compute_tie_free_witness,
    has_unique_nearest,
    verify_tie_free_loo,
    verify_tie_free_replace_one,
    filter_tie_free_witnesses,
    adjacency_from_dict,
)
from knn_stability.graph_metrics import adjacency_to_graph_metric
from knn_stability.knn import LabeledSample


def test_adjacency_from_dict() -> None:
    """Test conversion of JSON adjacency list to internal format."""
    adjacency_list = {"0": [1], "1": [0]}
    adjacency = adjacency_from_dict(adjacency_list)
    assert adjacency == {0: {1}, 1: {0}}


def test_has_unique_nearest_simple() -> None:
    """Test unique nearest detection for simple case."""
    # Two vertices with edge: distance(0,1) = 1
    adj = {0: {1}, 1: {0}}
    metric = adjacency_to_graph_metric(adj)

    # Sample with order [0, 1], labels [0, 0]
    sample = LabeledSample(
        metric=metric,
        point_indices=(0, 1),
        labels=(0, 0),
    )

    # Query at point 0: nearest is point 1 (distance 1), which is unique
    assert has_unique_nearest(sample, query_point_idx=0) is True

    # Query at point 1: nearest is point 0 (distance 1), which is unique
    assert has_unique_nearest(sample, query_point_idx=1) is True


def test_has_unique_nearest_duplicate_points() -> None:
    """Test that duplicate sample occurrences are tracked separately."""
    # Two vertices with edge: distance(0,1) = 1
    adj = {0: {1}, 1: {0}}
    metric = adjacency_to_graph_metric(adj)

    # Sample with duplicate point 0, different labels: [0, 0] and [1, 0]
    sample = LabeledSample(
        metric=metric,
        point_indices=(0, 0),  # Both occurrences point to vertex 0
        labels=(0, 1),
    )

    # Query at point 1: distances to both occurrences are 1 (both from 1 to 0)
    # There are two occurrences at minimum distance, so NOT unique
    assert has_unique_nearest(sample, query_point_idx=1) is False

    # Query at point 0: both occurrences are at distance 0 (same point)
    # This is a tie for the nearest neighbor
    assert has_unique_nearest(sample, query_point_idx=0) is False


def test_verify_tie_free_loo() -> None:
    """Test LOO tie-free verification."""
    adj = {0: {1}, 1: {0}}
    metric = adjacency_to_graph_metric(adj)

    sample = LabeledSample(
        metric=metric,
        point_indices=(0, 1),
        labels=(0, 0),
    )

    # Delete index 0 (point 0) and query at point 0
    # Original: nearest is point 1 (distance 1), unique -> True
    # After deletion: sample only has point 1, query at 0: nearest is point 1 (distance 1), unique -> True
    assert verify_tie_free_loo(sample, delete_index=0, query_point_idx=0) is True


def test_verify_tie_free_loo_false_on_original() -> None:
    """Test that LOO verification fails when original sample has a tie."""
    adj = {0: {1}, 1: {0}}
    metric = adjacency_to_graph_metric(adj)

    # Sample with duplicate points at same location
    sample = LabeledSample(
        metric=metric,
        point_indices=(0, 0),  # Both at point 0
        labels=(0, 1),
    )

    # Query at point 1: both occurrences are at distance 1, not unique
    assert verify_tie_free_loo(sample, delete_index=0, query_point_idx=1) is False


def test_verify_tie_free_replace_one() -> None:
    """Test replace-one tie-free verification."""
    adj = {0: {1}, 1: {0}}
    metric = adjacency_to_graph_metric(adj)

    sample = LabeledSample(
        metric=metric,
        point_indices=(0, 1),
        labels=(0, 0),
    )

    # Replace index 0 with point 0, label 1; query at point 0
    # Original: nearest is point 1 (distance 1), unique -> True
    # After replacement: same as original (replacing with same point)
    # nearest is point 1 (distance 1), unique -> True
    assert verify_tie_free_replace_one(
        sample, replace_index=0, new_point_idx=0, new_label=1, query_point_idx=0
    ) is True


def test_compute_tie_free_witness_accepts_minimal() -> None:
    """Test that minimal 2-vertex witnesses survive tie-free recomputation."""
    # Create a witness record for the minimal case
    witness = WitnessRecord(
        num_vertices=2,
        num_edges=1,
        adjacency_list={0: [1], 1: [0]},
        sample_order=[0, 1],
        labels=[0, 0],
        loo_max=0,
        loo_witness_index=0,
        replace_max=1,
        replace_witness_index=0,
        replace_witness_replacement_point=0,
        replace_witness_replacement_label=1,
        replace_witness_query_point=0,
        replace_witness_query_label=0,
        separation_gap=1,
    )

    tie_free = compute_tie_free_witness(witness)
    assert tie_free is not None
    assert tie_free.loo_max == 0
    assert tie_free.replace_max == 1


def test_filter_tie_free_witnesses() -> None:
    """Test filtering of tie-free witnesses."""
    # Create witnesses: one tie-free, one with ties
    tie_free = WitnessRecord(
        num_vertices=2,
        num_edges=1,
        adjacency_list={0: [1], 1: [0]},
        sample_order=[0, 1],
        labels=[0, 0],
        loo_max=0,
        loo_witness_index=0,
        replace_max=1,
        replace_witness_index=0,
        replace_witness_replacement_point=0,
        replace_witness_replacement_label=1,
        replace_witness_query_point=0,
        replace_witness_query_label=0,
        separation_gap=1,
    )

    with_ties = WitnessRecord(
        num_vertices=2,
        num_edges=1,
        adjacency_list={0: [1], 1: [0]},
        sample_order=[0, 0],  # Duplicate points - causes ties
        labels=[0, 1],
        loo_max=0,
        loo_witness_index=0,
        replace_max=1,
        replace_witness_index=0,
        replace_witness_replacement_point=0,
        replace_witness_replacement_label=1,
        replace_witness_query_point=1,
        replace_witness_query_label=0,
        separation_gap=1,
    )

    tie_free_witnesses, stats = filter_tie_free_witnesses([tie_free, with_ties])

    assert stats["total_witnesses"] == 2
    assert stats["tie_free_witnesses"] == 1
    assert stats["rejected_tie_witnesses"] == 1
    assert len(tie_free_witnesses) == 1


def test_build_minimality_certificate() -> None:
    certificate = build_certificate(
        Path("outputs/witnesses/1nn_separation_witnesses.json"),
        Path("outputs/witnesses/1nn_tie_free_witnesses.json"),
    )

    assert certificate["status"] == "computational_evidence_only"
    assert certificate["not_a_proof"] is True
    assert certificate["observed_minimal_vertex_counts"]["task_007"] == 2
    assert certificate["observed_minimal_vertex_counts"]["task_008"] == 2
