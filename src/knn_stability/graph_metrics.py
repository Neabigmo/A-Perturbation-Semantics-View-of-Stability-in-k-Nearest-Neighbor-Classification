"""Graph shortest-path metric helpers.

For a finite, simple, connected, unweighted, undirected graph G = (V, E),
the graph metric is d_G(u, v) = length of a shortest path from u to v.

Disconnected graphs are rejected in code paths that require a metric.
"""

from __future__ import annotations

from collections import deque
from typing import Hashable

import numpy as np

from knn_stability.metrics import FiniteMetricSpace


def adjacency_to_graph_metric(
    adjacency: dict[Hashable, set[Hashable]],
) -> FiniteMetricSpace:
    """Convert an undirected unweighted connected graph to a shortest-path metric.

    Parameters
    ----------
    adjacency : dict[Hashable, set[Hashable]]
        Adjacency list representation of an undirected graph.
        Keys are vertices, values are sets of neighboring vertices.
        Self-loops are ignored.

    Returns
    -------
    FiniteMetricSpace
        A metric space where points are the graph vertices and
        distances are shortest-path distances.

    Raises
    ------
    ValueError
        If the graph is disconnected or not undirected.

    Examples
    --------
    >>> adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}  # triangle
    >>> metric = adjacency_to_graph_metric(adj)
    >>> metric.d(0, 1)  # direct edge
    1.0
    >>> metric.d(0, 2)  # direct edge
    1.0
    >>> metric.d(1, 2)  # direct edge
    1.0
    """
    if not adjacency:
        return FiniteMetricSpace(points=[], distances=np.array([]))

    _validate_undirected_adjacency(adjacency)

    vertices = list(adjacency.keys())
    n = len(vertices)
    vertex_to_idx = {v: i for i, v in enumerate(vertices)}

    # Initialize distance matrix with infinity (no path)
    INF = float("inf")
    dist = np.full((n, n), INF, dtype=np.float64)

    # Self-distance is zero
    for i in range(n):
        dist[i, i] = 0.0

    # Set edge weights to 1 for adjacency
    for v, neighbors in adjacency.items():
        i = vertex_to_idx[v]
        for neighbor in neighbors:
            if neighbor == v:
                continue  # skip self-loops
            if neighbor not in vertex_to_idx:
                raise ValueError(
                    f"Vertex {neighbor} appears in adjacency of {v} but is not a key"
                )
            j = vertex_to_idx[neighbor]
            dist[i, j] = 1.0
            dist[j, i] = 1.0

    # Floyd-Warshall algorithm to compute shortest paths
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]

    # Check for disconnected graph (any INF remaining off diagonal)
    if not np.isfinite(dist).all():
        disconnected = []
        for i in range(n):
            for j in range(i + 1, n):
                if not np.isfinite(dist[i, j]) or dist[i, j] == INF:
                    disconnected.append((vertices[i], vertices[j]))
        if disconnected:
            raise ValueError(
                f"Graph is disconnected. No path exists between: {disconnected[:5]}"
                + (" ..." if len(disconnected) > 5 else "")
            )

    return FiniteMetricSpace(points=vertices, distances=dist)


def _validate_undirected_adjacency(adjacency: dict[Hashable, set[Hashable]]) -> None:
    """Check that every listed edge appears in both adjacency directions."""
    for vertex, neighbors in adjacency.items():
        for neighbor in neighbors:
            if neighbor not in adjacency:
                raise ValueError(
                    f"Vertex {neighbor} appears in adjacency of {vertex} but is not a key"
                )
            if vertex == neighbor:
                continue
            if vertex not in adjacency[neighbor]:
                raise ValueError("Adjacency list must represent an undirected graph")


def edge_list_to_adjacency(
    edges: list[tuple[Hashable, Hashable]],
    vertices: list[Hashable] | None = None,
) -> dict[Hashable, set[Hashable]]:
    """Convert an edge list to an adjacency list representation.

    Parameters
    ----------
    edges : list[tuple[Hashable, Hashable]]
        List of edges as (u, v) tuples representing undirected edges.
    vertices : list[Hashable] | None
        Optional list of all vertices. If None, vertices are inferred from edges.

    Returns
    -------
    dict[Hashable, set[Hashable]]
        Adjacency list representation.

    Examples
    --------
    >>> adj = edge_list_to_adjacency([(0, 1), (1, 2), (2, 0)])
    >>> adj[0]
    {1, 2}
    """
    if vertices is None:
        vertices_set: set[Hashable] = set()
        for u, v in edges:
            vertices_set.add(u)
            vertices_set.add(v)
        vertices = list(vertices_set)

    adjacency: dict[Hashable, set[Hashable]] = {v: set() for v in vertices}

    for u, v in edges:
        if u not in adjacency:
            adjacency[u] = set()
        if v not in adjacency:
            adjacency[v] = set()
        adjacency[u].add(v)
        adjacency[v].add(u)

    return adjacency


def is_connected(adjacency: dict[Hashable, set[Hashable]]) -> bool:
    """Check if an undirected graph is connected.

    Uses BFS to determine connectivity.

    Parameters
    ----------
    adjacency : dict[Hashable, set[Hashable]]
        Adjacency list representation of an undirected graph.

    Returns
    -------
    bool
        True if the graph is connected, False otherwise.
    """
    if not adjacency:
        return True

    vertices = list(adjacency.keys())
    if not vertices:
        return True

    visited: set[Hashable] = set()
    queue = deque([vertices[0]])
    visited.add(vertices[0])

    while queue:
        v = queue.popleft()
        for neighbor in adjacency.get(v, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return len(visited) == len(vertices)
