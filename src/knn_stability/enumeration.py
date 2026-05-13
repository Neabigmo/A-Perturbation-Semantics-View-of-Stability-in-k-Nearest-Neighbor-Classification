"""Deterministic finite enumeration utilities for witness search."""

from __future__ import annotations

import itertools
from collections import deque
from typing import Iterator


def is_connected_graph(adjacency: dict[int, set[int]]) -> bool:
    """Return whether an undirected graph is connected."""
    if not adjacency:
        return False

    start = next(iter(adjacency))
    seen = {start}
    queue: deque[int] = deque([start])

    while queue:
        vertex = queue.popleft()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return len(seen) == len(adjacency)


def enumerate_connected_graphs(num_vertices: int) -> Iterator[dict[int, set[int]]]:
    """Enumerate connected simple undirected labeled graphs on ``0..n-1``."""
    if num_vertices < 1:
        raise ValueError(f"num_vertices must be at least 1, got {num_vertices}")

    vertices = list(range(num_vertices))
    edges = list(itertools.combinations(vertices, 2))

    for edge_mask in range(1 << len(edges)):
        adjacency: dict[int, set[int]] = {vertex: set() for vertex in vertices}
        for edge_idx, (u, v) in enumerate(edges):
            if edge_mask & (1 << edge_idx):
                adjacency[u].add(v)
                adjacency[v].add(u)

        if is_connected_graph(adjacency):
            yield adjacency


def enumerate_binary_labelings(num_items: int) -> Iterator[tuple[int, ...]]:
    """Enumerate all binary labelings of length ``num_items``."""
    if num_items < 0:
        raise ValueError(f"num_items must be non-negative, got {num_items}")

    for label_mask in range(1 << num_items):
        yield tuple((label_mask >> idx) & 1 for idx in range(num_items))


def enumerate_vertex_orders(num_vertices: int) -> Iterator[tuple[int, ...]]:
    """Enumerate all orderings of ``0..num_vertices-1``."""
    if num_vertices < 0:
        raise ValueError(f"num_vertices must be non-negative, got {num_vertices}")

    return itertools.permutations(range(num_vertices))
