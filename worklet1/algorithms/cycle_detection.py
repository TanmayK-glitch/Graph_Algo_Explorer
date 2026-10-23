"""Cycle detection for directed and undirected graphs."""

from __future__ import annotations

from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult


def has_cycle_undirected(graph: Graph) -> bool:
    """DFS; a visited non-parent neighbour (or a self-loop) is a back edge."""
    visited: set = set()

    def _dfs(v: Any, parent: Any) -> bool:
        visited.add(v)
        for nbr in graph.neighbours(v):
            if nbr not in visited:
                if _dfs(nbr, v):  # pass v down so the child can ignore the edge back to v
                    return True
            elif nbr != parent:
                # Already visited and NOT the vertex we just came from => a different path
                # leads back here => cycle. A self-loop (nbr == v) also lands here.
                return True
        return False

    return any(_dfs(v, None) for v in graph.vertices if v not in visited)


def has_cycle_directed(graph: Graph) -> bool:
    """DFS with a recursion-stack set: an edge into the current path is a back edge."""
    # visited   = vertices fully or partly explored (never explore twice)
    # rec_stack = vertices on the CURRENT DFS path.
    # One set is not enough: an edge to an already-finished vertex (cross/forward edge) is
    # harmless, but an edge to a vertex still on the current path (back edge) is a cycle.
    visited: set = set()
    rec_stack: set = set()

    def _dfs(v: Any) -> bool:
        visited.add(v)
        rec_stack.add(v)
        for nbr in graph.neighbours(v):
            if nbr not in visited:
                if _dfs(nbr):
                    return True
            elif nbr in rec_stack:
                return True  # back edge: points to an ancestor on the current path
        rec_stack.remove(v)  # leaving v: it is no longer on the current path
        return False

    return any(_dfs(v) for v in graph.vertices if v not in visited)


class CycleDetectionAlgorithm(Algorithm):
    """Detect whether a graph contains a cycle (FR-15).  A self-loop counts as a cycle."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "CycleDetection"

    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Return ``True``/``False`` as ``primary_output``; picks the algorithm by direction."""
        # The two kinds of graph need different logic, chosen by the graph's own flag.
        found = has_cycle_directed(graph) if graph.is_directed else has_cycle_undirected(graph)
        return AlgorithmResult("CycleDetection", found, {})
