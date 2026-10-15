"""Bellman-Ford shortest-path algorithm for weighted graphs.

This module provides bellman_ford(), which computes single-source
shortest paths on a weighted graph represented as an adjacency list,
and reconstruct_path(), which rebuilds a shortest path.

Unlike Dijkstra's algorithm, Bellman-Ford supports negative edge
weights and detects reachable negative-weight cycles.

Time complexity: O(V * E)
Space complexity: O(V + E)
"""

from __future__ import annotations

import math
from collections.abc import Hashable
from dataclasses import dataclass, field

# Type aliases consistent with dijkstra.py.
Vertex = Hashable
Graph = dict[Vertex, list[tuple[Vertex, float | int]]]


@dataclass(frozen=True)
class BellmanFordResult:
    """Immutable result of bellman_ford().

    Attributes
    ----------
    source:
        Source vertex used for the computation.
    distances:
        Shortest distances from source. Unreachable vertices have
        distance math.inf.
    predecessors:
        Predecessor of each vertex on its shortest path.
        The source and unreachable vertices map to None.
    """

    source: Vertex
    distances: dict[Vertex, float] = field(repr=False)
    predecessors: dict[Vertex, Vertex | None] = field(repr=False)


def bellman_ford(graph: Graph, source: Vertex) -> BellmanFordResult:
    """Compute shortest paths using the Bellman-Ford algorithm.

    Parameters
    ----------
    graph:
        Weighted adjacency list. Negative edge weights are supported.
    source:
        Starting vertex. Must exist as a key or neighbor in graph.

    Returns
    -------
    BellmanFordResult
        Distances and predecessors for every vertex.

    Raises
    ------
    ValueError
        If the graph is malformed, the source is absent, or a
        reachable negative-weight cycle exists.
    """

    _validate_graph(graph)

    # Collect all vertices, including vertices appearing only
    # as neighbors.
    all_vertices: set[Vertex] = set(graph.keys())

    for neighbors in graph.values():
        for neighbor, _weight in neighbors:
            all_vertices.add(neighbor)

    if source not in all_vertices:
        raise ValueError(f"Source vertex {source!r} is not present in the graph")

    # Initialize distances and predecessors.
    dist: dict[Vertex, float] = {vertex: math.inf for vertex in all_vertices}

    pred: dict[Vertex, Vertex | None] = {vertex: None for vertex in all_vertices}

    dist[source] = 0.0

    # Relax every edge at most V - 1 times.
    for _ in range(len(all_vertices) - 1):
        updated = False

        for u, neighbors in graph.items():
            if math.isinf(dist[u]):
                continue

            for v, weight in neighbors:
                new_dist = dist[u] + weight

                if new_dist < dist[v]:
                    dist[v] = new_dist
                    pred[v] = u
                    updated = True

        # If no distance changes, further iterations are unnecessary.
        if not updated:
            break

    # Check for a reachable negative-weight cycle.
    for u, neighbors in graph.items():
        if math.isinf(dist[u]):
            continue

        for v, weight in neighbors:
            if dist[u] + weight < dist[v]:
                raise ValueError("Reachable negative-weight cycle detected")

    return BellmanFordResult(
        source=source,
        distances=dist,
        predecessors=pred,
    )


def reconstruct_path(
    result: BellmanFordResult,
    target: Vertex,
) -> list[Vertex] | None:
    """Reconstruct the shortest path from source to target.

    Returns a list of vertices, or None if the target is unreachable
    or is not present in the result.
    """

    if target not in result.distances:
        return None

    if math.isinf(result.distances[target]):
        return None

    path: list[Vertex] = []
    current: Vertex | None = target

    while current is not None:
        path.append(current)
        current = result.predecessors[current]

    path.reverse()
    return path


def _validate_graph(graph: Graph) -> None:
    """Validate graph structure and edge weights."""

    if not isinstance(graph, dict):
        raise ValueError("Graph must be a dict")

    for vertex, neighbors in graph.items():
        if not isinstance(neighbors, list):
            raise ValueError(f"Adjacency list for vertex {vertex!r} must be a list")

        for i, entry in enumerate(neighbors):
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise ValueError(
                    f"Edge entry {i} for vertex {vertex!r} must be "
                    "a (neighbor, weight) pair"
                )

            neighbor, weight = entry

            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Edge weight for {vertex!r} -> {neighbor!r} must be numeric"
                )

            if isinstance(weight, float) and (math.isnan(weight) or math.isinf(weight)):
                raise ValueError(
                    f"Edge weight for {vertex!r} -> {neighbor!r} must be finite"
                )
