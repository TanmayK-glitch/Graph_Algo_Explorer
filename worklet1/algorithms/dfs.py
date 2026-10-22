"""Depth-first search (recursive; the call stack is the LIFO stack).

Known limitation (design section 14 / D-12): the default recursive version raises
``RecursionError`` on graphs about 1000 vertices deep.  The opt-in ``iterative=True``
variant uses an explicit stack of neighbour iterators, has no depth limit and visits
vertices in exactly the same order.
"""

from __future__ import annotations

from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult, require_vertex


def dfs_component(graph: Graph, start: Any, visited: set, order: list, iterative: bool = False) -> None:
    """Pre-order DFS from *start*; extends *visited* and *order* in place.

    Recursive by default (call stack as the LIFO stack); ``iterative=True`` uses an explicit stack.
    """
    if iterative:
        # Explicit stack. Each stack entry is an ITERATOR over one vertex's neighbours, so we
        # can pause that vertex, go deeper, and later resume where we left off. This produces
        # exactly the same order as the recursive version but has no depth limit.
        visited.add(start)
        order.append(start)
        stack = [iter(graph.neighbours(start))]
        while stack:
            for nbr in stack[-1]:  # continues from where this vertex's iterator stopped
                if nbr not in visited:
                    visited.add(nbr)
                    order.append(nbr)
                    stack.append(iter(graph.neighbours(nbr)))
                    break  # go deeper first (depth-first)
            else:
                stack.pop()  # all neighbours used up => backtrack
        return

    def _visit(v: Any) -> None:
        visited.add(v)
        order.append(v)  # pre-order: record the vertex BEFORE exploring its neighbours
        for nbr in graph.neighbours(v):
            if nbr not in visited:
                _visit(nbr)  # the Python call stack is the LIFO stack of the DFS

    _visit(start)


def dfs(graph: Graph, start: Any, iterative: bool = False) -> AlgorithmResult:
    """DFS over the component containing *start* (FR-12, FR-18)."""
    require_vertex(graph, start)
    visited: set = set()
    order: list = []
    dfs_component(graph, start, visited, order, iterative)
    return AlgorithmResult("DFS", order, {"start": start})


def dfs_all(graph: Graph, iterative: bool = False) -> AlgorithmResult:
    """DFS restarted from every unvisited vertex, covering the whole graph (FR-18)."""
    visited: set = set()  # shared across restarts so every vertex is visited exactly once
    order: list = []
    for v in graph.vertices:
        if v not in visited:  # new component found => restart DFS here
            dfs_component(graph, v, visited, order, iterative)
    return AlgorithmResult("DFS_ALL", order, {})


class DFSAlgorithm(Algorithm):
    """Strategy wrapper: ``execute(graph, start=..., mode='single'|'all')`` (decision D-03)."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "DFS"

    def execute(self, graph: Graph, start: Any | None = None, mode: str = "single",
                iterative: bool = False, **kwargs: Any) -> AlgorithmResult:
        """Run DFS; see :meth:`BFSAlgorithm.execute` for *start*/*mode*.

        ``iterative=True`` selects the explicit-stack variant (no recursion limit, same order).
        """
        if mode == "all":
            return dfs_all(graph, iterative)
        if mode != "single":
            raise ValueError(f"mode must be 'single' or 'all', got {mode!r}")
        if start is None:
            raise ValueError("DFS in 'single' mode requires a start vertex")
        return dfs(graph, start, iterative)
