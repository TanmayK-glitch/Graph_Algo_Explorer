"""Connected components of an undirected graph (repeated BFS)."""

from __future__ import annotations

from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult, canonical_components
from .bfs import bfs_component


class ConnectedComponentsAlgorithm(Algorithm):
    """Partition an undirected graph into connected components (FR-13)."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "ConnectedComponents"

    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Return components as ``[[...], ...]`` in canonical order.

        Raises ``ValueError`` for a directed graph (decision D-01).  Metadata:
        ``count`` and ``component_map`` (vertex -> component index; PROPOSED, X-03).
        """
        if graph.is_directed:
            raise ValueError("connected components are defined for undirected graphs only")
        visited: set = set()
        found: list = []
        for v in graph.vertices:
            if v not in visited:
                # One BFS from an unvisited vertex reaches exactly its component.
                # Isolated vertices naturally become singleton components.
                comp, _ = bfs_component(graph, v, visited)
                found.append(comp)
        # Sort members/components into a fixed order so the output never depends on traversal details.
        components = canonical_components(graph, found)
        # component_map: vertex -> index of its component (PROPOSED for Worklet 3 colouring).
        component_map = {v: i for i, comp in enumerate(components) for v in comp}
        return AlgorithmResult(
            "ConnectedComponents", components,
            {"count": len(components), "component_map": component_map},
        )
