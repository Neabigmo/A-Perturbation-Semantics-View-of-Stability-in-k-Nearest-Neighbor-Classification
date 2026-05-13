"""Tests for graph shortest-path metrics."""

from __future__ import annotations

import numpy as np
import pytest

from knn_stability.graph_metrics import (
    adjacency_to_graph_metric,
    edge_list_to_adjacency,
    is_connected,
)


class TestEdgeListToAdjacency:
    """Tests for edge list to adjacency list conversion."""

    def test_empty_edges(self) -> None:
        adj = edge_list_to_adjacency([])
        assert adj == {}

    def test_single_edge(self) -> None:
        adj = edge_list_to_adjacency([(0, 1)])
        assert adj == {0: {1}, 1: {0}}

    def test_multiple_edges(self) -> None:
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 0)])
        assert 0 in adj[1] and 1 in adj[0]
        assert 1 in adj[2] and 2 in adj[1]
        assert 2 in adj[0] and 0 in adj[2]

    def test_with_explicit_vertices(self) -> None:
        adj = edge_list_to_adjacency([(0, 1)], vertices=[0, 1, 2])
        assert adj[0] == {1}
        assert adj[1] == {0}
        assert adj[2] == set()


class TestIsConnected:
    """Tests for connectivity checking."""

    def test_empty_graph(self) -> None:
        assert is_connected({})

    def test_single_vertex(self) -> None:
        assert is_connected({0: set()})

    def test_two_connected_vertices(self) -> None:
        assert is_connected({0: {1}, 1: {0}})

    def test_disconnected_vertices(self) -> None:
        assert not is_connected({0: set(), 1: set()})

    def test_path_graph_connected(self) -> None:
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 3)])
        assert is_connected(adj)

    def test_cycle_graph_connected(self) -> None:
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 0)])
        assert is_connected(adj)

    def test_two_components_disconnected(self) -> None:
        adj = edge_list_to_adjacency([(0, 1), (1, 0), (2, 3), (3, 2)])
        assert not is_connected(adj)


class TestAdjacencyToGraphMetric:
    """Tests for shortest-path metric conversion."""

    def test_empty_graph(self) -> None:
        metric = adjacency_to_graph_metric({})
        assert metric.n == 0

    def test_single_vertex(self) -> None:
        metric = adjacency_to_graph_metric({0: set()})
        assert metric.n == 1
        assert metric.d(0, 0) == 0.0

    def test_two_vertices_direct_edge(self) -> None:
        metric = adjacency_to_graph_metric({0: {1}, 1: {0}})
        assert metric.n == 2
        assert metric.d(0, 1) == 1.0
        assert metric.d(1, 0) == 1.0
        assert metric.d(0, 0) == 0.0

    def test_path_graph_shortest_paths(self) -> None:
        """Path graph: distances match path lengths."""
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 3)])
        metric = adjacency_to_graph_metric(adj)
        assert metric.d(0, 0) == 0.0
        assert metric.d(0, 1) == 1.0  # direct edge
        assert metric.d(0, 2) == 2.0  # via vertex 1
        assert metric.d(0, 3) == 3.0  # via vertices 1, 2
        assert metric.d(1, 3) == 2.0  # via vertex 2

    def test_cycle_graph_shortest_paths(self) -> None:
        """Cycle graph: triangle shows path through different routes."""
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 0)])
        metric = adjacency_to_graph_metric(adj)
        # All pairs should be distance 1 (complete cycle)
        assert metric.d(0, 1) == 1.0
        assert metric.d(1, 2) == 1.0
        assert metric.d(2, 0) == 1.0
        # No longer paths needed in triangle

    def test_cycle_graph_square(self) -> None:
        """Square cycle: corners have distance 2 via either direction."""
        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 3), (3, 0)])
        metric = adjacency_to_graph_metric(adj)
        assert metric.d(0, 1) == 1.0  # adjacent
        assert metric.d(1, 2) == 1.0  # adjacent
        assert metric.d(0, 2) == 2.0  # opposite corners
        assert metric.d(0, 3) == 1.0  # adjacent
        assert metric.d(1, 3) == 2.0  # opposite corners

    def test_complete_graph(self) -> None:
        """Complete graph: all pairs distance 1."""
        adj = edge_list_to_adjacency([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
        metric = adjacency_to_graph_metric(adj)
        for i in range(4):
            for j in range(4):
                if i == j:
                    assert metric.d(i, j) == 0.0
                else:
                    assert metric.d(i, j) == 1.0

    def test_star_graph(self) -> None:
        """Star graph: center to leaves distance 1, leaf-to-leaf distance 2."""
        adj = edge_list_to_adjacency([(0, 1), (0, 2), (0, 3), (0, 4)])
        metric = adjacency_to_graph_metric(adj)
        assert metric.d(0, 0) == 0.0
        # Center to all leaves is 1
        for i in range(1, 5):
            assert metric.d(0, i) == 1.0
        # All leaves to each other is 2 (via center)
        for i in range(1, 5):
            for j in range(i + 1, 5):
                assert metric.d(i, j) == 2.0

    def test_mixed_distances(self) -> None:
        """A more complex graph with varying path lengths."""
        adj = edge_list_to_adjacency([
            (0, 1), (1, 2), (2, 3), (2, 4), (3, 4)
        ])
        metric = adjacency_to_graph_metric(adj)
        assert metric.d(0, 1) == 1.0
        assert metric.d(1, 2) == 1.0
        assert metric.d(2, 3) == 1.0
        assert metric.d(2, 4) == 1.0
        assert metric.d(3, 4) == 1.0  # direct edge
        assert metric.d(0, 2) == 2.0  # via 1
        assert metric.d(0, 3) == 3.0  # via 1, 2
        # Path 0->4: 0->1->2->4 (3 hops) - no shorter path exists
        # since (3,4) exists but (3,2) is only via 3->2 is 1, so 0->1->2->4 = 3
        assert metric.d(0, 4) == 3.0  # via 1, 2
        assert metric.d(1, 4) == 2.0  # via 2

    def test_disconnected_graph_raises(self) -> None:
        """Disconnected graphs should raise ValueError."""
        adj = {0: {1}, 1: {0}, 2: {3}, 3: {2}}
        with pytest.raises(ValueError, match="disconnected"):
            adjacency_to_graph_metric(adj)

    def test_directed_adjacency_rejected(self) -> None:
        """Asymmetric adjacency is not accepted as an undirected graph."""
        adj = {0: {1}, 1: set()}
        with pytest.raises(ValueError, match="undirected"):
            adjacency_to_graph_metric(adj)

    def test_disconnected_single_island(self) -> None:
        """One isolated vertex raises error."""
        adj = {0: {1}, 1: {0}, 2: set()}
        with pytest.raises(ValueError, match="disconnected"):
            adjacency_to_graph_metric(adj)

    def test_hashable_vertices(self) -> None:
        """Vertices can be any hashable type."""
        adj = {"a": {"b"}, "b": {"a"}}
        metric = adjacency_to_graph_metric(adj)
        assert metric.n == 2
        # Access by index - vertex "a" is at index 0, "b" at index 1
        assert metric.d(0, 1) == 1.0
        # Verify points are stored correctly
        assert set(metric.points) == {"a", "b"}

    def test_returns_valid_metric_space(self) -> None:
        """Result should be a valid FiniteMetricSpace."""
        from knn_stability.metrics import is_valid_metric

        adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 3)])
        metric = adjacency_to_graph_metric(adj)
        assert is_valid_metric(metric.distances)
