from pathlib import Path

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
