"""Dijkstra's shortest-path algorithm using a custom :class:`MinHeap`.

This module provides :func:`dijkstra` which computes single-source
shortest paths on a weighted graph represented as an adjacency list,
and :func:`reconstruct_path` which rebuilds the shortest path from
source to a given target.

Graph representation
--------------------
A graph is a ``dict`` mapping each vertex (any *hashable* label) to a
list of ``(neighbor, weight)`` pairs::

    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 2), ("D", 5)],
        "D": [],
    }

Vertices that appear *only* as neighbors (and have no key in the dict)
are treated as having **no outgoing edges**.

Complexity
----------
Using an adjacency-list representation and a binary min-heap the
algorithm runs in **O((V + E) log V)** time, where *V* is the number
of vertices and *E* is the number of edges.

* Each vertex is inserted into (and extracted from) the heap at most
  once per relaxation, giving up to *O(E)* heap insertions.
* Each heap operation costs *O(log V)* in the worst case (the heap
  never exceeds *O(E)* entries, but *log E ∈ O(log V)* for simple
  graphs).

Space complexity is **O(V + E)** for the distance / predecessor maps
plus the heap.

Negative-weight edges are **not supported**; a ``ValueError`` is
raised if any are encountered.
"""

from __future__ import annotations

import math
from collections.abc import Hashable
from dataclasses import dataclass, field

from src.algorithms.min_heap import MinHeap

# Type aliases for readability.
Vertex = Hashable
Graph = dict[Vertex, list[tuple[Vertex, float | int]]]


@dataclass(frozen=True)
class DijkstraResult:
    """Immutable result of :func:`dijkstra`.

    Attributes
    ----------
    source:
        The source vertex used for the computation.
    distances:
        Mapping from each reachable (or known) vertex to its shortest
        distance from *source*.  Unreachable vertices have distance
        ``math.inf``.
    predecessors:
        Mapping from each vertex to its predecessor on the shortest
        path from *source*.  The source itself maps to ``None``, and
        unreachable vertices also map to ``None``.
    """

    source: Vertex
    distances: dict[Vertex, float] = field(repr=False)
    predecessors: dict[Vertex, Vertex | None] = field(repr=False)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def dijkstra(graph: Graph, source: Vertex) -> DijkstraResult:
    """Compute single-source shortest paths using Dijkstra's algorithm.

    Parameters
    ----------
    graph:
        Weighted adjacency list.  Every weight must be non-negative.
    source:
        Starting vertex.  Must be present as a key in *graph* or
        appear as a neighbor of another vertex.

    Returns
    -------
    DijkstraResult
        A frozen dataclass containing ``distances`` and
        ``predecessors`` dictionaries.

    Raises
    ------
    ValueError
        If *source* is not in the graph, if any edge weight is
        negative, or if any edge entry is malformed.

    Time complexity: O((V + E) log V).
    """
    _validate_graph(graph)

    # Collect every vertex mentioned anywhere (keys + neighbors).
    all_vertices: set[Vertex] = set(graph.keys())
    for neighbors in graph.values():
        for neighbor, _weight in neighbors:
            all_vertices.add(neighbor)

    if source not in all_vertices:
        raise ValueError(f"Source vertex {source!r} is not present in the graph")

    # Initialise distances and predecessors.
    dist: dict[Vertex, float] = {v: math.inf for v in all_vertices}
    pred: dict[Vertex, Vertex | None] = {v: None for v in all_vertices}
    dist[source] = 0.0

    visited: set[Vertex] = set()
    heap = MinHeap()
    heap.insert(0.0, source)

    while not heap.is_empty():
        current_dist, u = heap.extract_min()

        # Skip stale entries — the vertex was already finalised with a
        # shorter distance.
        if u in visited:
            continue
        visited.add(u)

        # Relax outgoing edges.  Vertices with no adjacency-list key
        # are treated as having no outgoing edges.
        for neighbor, weight in graph.get(u, []):
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                pred[neighbor] = u
                heap.insert(new_dist, neighbor)

    return DijkstraResult(source=source, distances=dist, predecessors=pred)


def reconstruct_path(result: DijkstraResult, target: Vertex) -> list[Vertex] | None:
    """Rebuild the shortest path from *result.source* to *target*.

    Parameters
    ----------
    result:
        The :class:`DijkstraResult` returned by :func:`dijkstra`.
    target:
        The destination vertex.

    Returns
    -------
    list[Vertex] | None
        An ordered list of vertices from source to *target*
        (inclusive), or ``None`` if *target* is unreachable.

    A source-to-source query returns ``[source]``.
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


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------


def _validate_graph(graph: Graph) -> None:
    """Check that *graph* is well-formed.

    Raises ``ValueError`` on the first problem detected.
    """
    if not isinstance(graph, dict):
        raise ValueError("Graph must be a dict")

    for vertex, neighbors in graph.items():
        if not isinstance(neighbors, list):
            raise ValueError(
                f"Adjacency list for vertex {vertex!r} must be a list, "
                f"got {type(neighbors).__name__}"
            )
        for i, entry in enumerate(neighbors):
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise ValueError(
                    f"Edge entry {i} for vertex {vertex!r} must be a "
                    f"(neighbor, weight) pair, got {entry!r}"
                )
            _neighbor, weight = entry
            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Edge weight for {vertex!r} -> {_neighbor!r} must be "
                    f"numeric, got {type(weight).__name__}"
                )
            if isinstance(weight, float) and math.isnan(weight):
                raise ValueError(
                    f"NaN edge weight on edge "
                    f"{vertex!r} -> {_neighbor!r} is not allowed"
                )
            if weight < 0:
                raise ValueError(
                    f"Negative edge weight {weight} on edge "
                    f"{vertex!r} -> {_neighbor!r} is not allowed"
                )
