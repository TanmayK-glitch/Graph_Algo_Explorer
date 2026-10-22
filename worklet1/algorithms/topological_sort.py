"""Topological sort using Kahn's algorithm."""

from __future__ import annotations

from collections import deque
from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult


class TopologicalSortAlgorithm(Algorithm):
    """Kahn's algorithm (FR-16): repeatedly remove vertices of in-degree zero."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "TopologicalSort"

    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Return a topological order, or ``success=False`` if the graph has a cycle.

        Raises ``ValueError`` for an undirected graph.
        """
        if not graph.is_directed:
            raise ValueError("topological order is only defined for directed graphs")
        in_degree = dict.fromkeys(graph.vertices, 0)
        for e in graph.all_edges():
            in_degree[e.dst] += 1
        queue = deque(v for v in graph.vertices if in_degree[v] == 0)
        order: list = []
        while queue:
            v = queue.popleft()
            order.append(v)
            for nbr in graph.neighbours(v):
                in_degree[nbr] -= 1
                if in_degree[nbr] == 0:
                    queue.append(nbr)
        if len(order) != graph.vertex_count():
            return AlgorithmResult(
                "TopologicalSort", None, {"has_cycle": True}, success=False,
                error_message="Graph has a cycle; no ordering exists.",
            )
        return AlgorithmResult("TopologicalSort", order, {"has_cycle": False})
