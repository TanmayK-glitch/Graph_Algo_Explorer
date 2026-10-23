"""Strongly connected components of a directed graph (Kosaraju's two-pass algorithm)."""

from __future__ import annotations

from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult, canonical_components


class SCCAlgorithm(Algorithm):
    """Kosaraju's algorithm (FR-14)."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "SCC"

    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Return strongly connected components in canonical order.

        1. DFS on the graph recording finish order.
        2. Transpose (reverse every edge; built locally from ``neighbours``).
        3. DFS on the transpose in decreasing finish order; each tree is one SCC.

        Raises ``ValueError`` for an undirected graph.  Metadata: ``count`` and
        ``component_map`` (PROPOSED, X-03).
        """
        if not graph.is_directed:
            raise ValueError("strongly connected components require a directed graph")
        vertices = graph.vertices

        # ---- Pass 1: DFS on the original graph, recording FINISH order. ----
        # A vertex finishes after everything reachable from it has finished, so the
        # last vertex to finish lies in a "source" SCC of the condensed graph.
        visited: set = set()
        finish: list = []

        def _first(v: Any) -> None:
            visited.add(v)
            for nbr in graph.neighbours(v):
                if nbr not in visited:
                    _first(nbr)
            finish.append(v)  # appended AFTER the recursive calls => post-order

        for v in vertices:
            if v not in visited:
                _first(v)

        # ---- Transpose: reverse every edge. Built locally from neighbours() only. ----
        # In the reversed graph, edges BETWEEN different SCCs point the other way, so a DFS
        # started in the last-finished SCC cannot escape into another SCC.
        transpose: dict = {v: [] for v in vertices}
        for u in vertices:
            for w in graph.neighbours(u):
                transpose[w].append(u)

        # ---- Pass 2: DFS on the transpose in DECREASING finish order. ----
        # Every DFS tree grown here is exactly one strongly connected component.
        seen: set = set()
        found: list = []

        def _second(v: Any, comp: list) -> None:
            seen.add(v)
            comp.append(v)
            for nbr in transpose[v]:
                if nbr not in seen:
                    _second(nbr, comp)

        for v in reversed(finish):
            if v not in seen:
                comp: list = []
                _second(v, comp)
                found.append(comp)

        components = canonical_components(graph, found)
        component_map = {v: i for i, comp in enumerate(components) for v in comp}
        return AlgorithmResult(
            "SCC", components, {"count": len(components), "component_map": component_map}
        )
