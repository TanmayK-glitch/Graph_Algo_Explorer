"""Dijkstra's shortest-path algorithm using a :class:`RadixHeap`.

This is a *variant* of the existing Dijkstra implementation in
``dijkstra.py``.  It works identically except for one thing: instead
of a binary min-heap (``MinHeap``), it uses a one-level Radix Heap
(``RadixHeap``).

Why a separate file?
--------------------
The original ``dijkstra.py`` is preserved unchanged.  This file adds
an alternative entrypoint ``dijkstra_radix()`` so that both can be
compared in tests and benchmarks side-by-side.

Integer-only restriction
------------------------
A Radix Heap needs to compute ``(key - d_last).bit_length()``, which
only works for Python integers.  Therefore this function rejects:

* Floating-point edge weights (e.g. 1.5, 0.1, math.pi).
* Negative edge weights.

If your graph has float weights, use the original ``dijkstra()`` instead.

Reused from dijkstra.py
-----------------------
* ``DijkstraResult`` dataclass — the return type (unchanged).
* ``reconstruct_path()`` function — path reconstruction (unchanged).

Everything else in this file is self-contained.
"""

from __future__ import annotations

import math
from collections.abc import Hashable

from src.algorithms.dijkstra import DijkstraResult, reconstruct_path  # reused as-is
from src.algorithms.radix_heap import RadixHeap

# Re-export reconstruct_path so callers of this module can import it
# from here directly without also needing to import dijkstra.py.
__all__ = ["dijkstra_radix", "reconstruct_path"]

# Type aliases (same as dijkstra.py for consistency).
Vertex = Hashable
Graph = dict[Vertex, list[tuple[Vertex, int]]]


def dijkstra_radix(graph: Graph, source: Vertex) -> DijkstraResult:
    """Compute single-source shortest paths using a one-level Radix Heap.

    The algorithm is the same as the standard Dijkstra in ``dijkstra.py``
    except that it uses a ``RadixHeap`` instead of a ``MinHeap``.

    Parameters
    ----------
    graph:
        Weighted adjacency list.  Every weight must be a non-negative
        **integer**.  Float weights are not supported.
    source:
        Starting vertex.  Must exist somewhere in the graph.

    Returns
    -------
    DijkstraResult
        A frozen dataclass containing ``distances`` and ``predecessors``
        dictionaries.  Unreachable vertices get distance ``math.inf``.

    Raises
    ------
    ValueError
        If the source vertex is not in the graph, or if any edge weight
        is negative, non-integer, or NaN.
    TypeError
        If a graph edge weight is a float (including whole-number floats
        like ``2.0``).

    Time complexity: O((V + E) log C) where C is the largest edge weight.
    This is potentially faster than O((V + E) log V) when C < V, but in
    practice the difference depends on graph density and Python overhead.
    """
    _validate_integer_graph(graph)

    # Collect every vertex that appears anywhere in the graph.
    all_vertices: set[Vertex] = set(graph.keys())
    for neighbors in graph.values():
        for neighbor, _weight in neighbors:
            all_vertices.add(neighbor)

    if source not in all_vertices:
        raise ValueError(f"Source vertex {source!r} is not present in the graph")

    # Initialise distances to infinity and predecessors to None.
    dist: dict[Vertex, float] = {v: math.inf for v in all_vertices}
    pred: dict[Vertex, Vertex | None] = {v: None for v in all_vertices}
    dist[source] = 0

    visited: set[Vertex] = set()

    # --- Key difference from dijkstra.py: use RadixHeap ---
    # RadixHeap requires non-negative integer keys.
    # We insert distance 0 for the source.
    heap = RadixHeap()
    heap.insert(0, source)

    while not heap.is_empty():
        current_dist, u = heap.extract_min()

        # Skip stale entries — same technique as dijkstra.py.
        # A stale entry is an old (larger) distance for a vertex that
        # has already been finalised.
        if u in visited:
            continue
        visited.add(u)

        # Relax all outgoing edges from u.
        for neighbor, weight in graph.get(u, []):
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                pred[neighbor] = u
                # Insert the improved distance.
                # Because Dijkstra only extracts in non-decreasing order
                # and edge weights are non-negative, new_dist >= current_dist
                # >= d_last, so the monotonicity rule is never violated.
                heap.insert(new_dist, neighbor)

    return DijkstraResult(source=source, distances=dist, predecessors=pred)


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------


def _validate_integer_graph(graph: Graph) -> None:
    """Check that the graph is well-formed and all weights are non-negative ints.

    This is stricter than the validator in dijkstra.py:
    float weights (even ``2.0``) are explicitly rejected because
    RadixHeap requires integer keys.
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

            # Reject booleans first (bool is a subclass of int in Python).
            if isinstance(weight, bool):
                raise TypeError(
                    f"Edge weight for {vertex!r} -> {_neighbor!r} must be a "
                    f"non-negative integer, got bool"
                )

            # Reject floats — they cannot be used as RadixHeap keys.
            if isinstance(weight, float):
                raise TypeError(
                    f"Edge weight for {vertex!r} -> {_neighbor!r} is a float "
                    f"({weight!r}).  dijkstra_radix() only supports integer "
                    f"weights.  Use dijkstra() for float weights."
                )

            if not isinstance(weight, int):
                raise ValueError(
                    f"Edge weight for {vertex!r} -> {_neighbor!r} must be a "
                    f"non-negative integer, got {type(weight).__name__!r}"
                )

            if isinstance(weight, float) and math.isnan(weight):  # pragma: no cover
                raise ValueError(
                    f"NaN edge weight on edge {vertex!r} -> {_neighbor!r} is not allowed"
                )

            if weight < 0:
                raise ValueError(
                    f"Negative edge weight {weight} on edge "
                    f"{vertex!r} -> {_neighbor!r} is not allowed"
                )
