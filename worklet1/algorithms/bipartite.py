"""Bipartite test by BFS two-colouring."""

from __future__ import annotations

from collections import deque
from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult


class BipartiteTestAlgorithm(Algorithm):
    """BFS 2-colouring of every component (FR-17)."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "BipartiteTest"

    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Return ``True`` with ``metadata['colouring']`` (vertex -> 0/1), else ``False``.

        Raises ``ValueError`` for a directed graph.  A self-loop makes the graph
        non-bipartite (odd cycle of length one).
        """
        if graph.is_directed:
            raise ValueError("bipartite test is defined for undirected graphs only")
        colour: dict = {}  # vertex -> 0 or 1; doubles as the "visited" set
        for start in graph.vertices:  # loop so every component (and isolated vertex) is tested
            if start in colour:
                continue
            colour[start] = 0
            queue = deque([start])
            while queue:
                v = queue.popleft()
                for nbr in graph.neighbours(v):
                    if nbr not in colour:
                        colour[nbr] = 1 - colour[v]  # neighbours get the opposite colour
                        queue.append(nbr)
                    elif colour[nbr] == colour[v]:
                        # Two adjacent vertices forced to the same colour => an odd cycle
                        # exists (a self-loop is the shortest one) => not bipartite.
                        return AlgorithmResult("BipartiteTest", False, {})
        return AlgorithmResult("BipartiteTest", True, {"colouring": colour})
