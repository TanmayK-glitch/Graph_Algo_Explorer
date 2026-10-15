"""Adapters connecting the shared Graph class with the team's algorithms.

Run examples from repository root:
    from graph_integration.integration import run_dijkstra, run_bellman_ford, run_kruskal

The original algorithm files remain unchanged. All result edges use the graph's
original vertex labels, including when Kruskal requires integer indices.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from graph_integration.graph import Edge, Graph, Vertex, Weight
from src.algorithms.bellman_ford import bellman_ford
from src.algorithms.dijkstra import dijkstra
from src.algorithms.kruskal import kruskal_mst


@dataclass(frozen=True)
class ShortestPathResult:
    """Standardized Dijkstra / Bellman-Ford result.

    ``distances[v] == math.inf`` signifies an unreachable vertex.
    """

    algorithm: str
    source: Vertex
    distances: dict[Vertex, float]
    predecessors: dict[Vertex, Vertex | None]

    def path_to(self, target: Vertex) -> list[Vertex] | None:
        """Return a path from the source to target, or None if unreachable."""
        if target not in self.distances or math.isinf(self.distances[target]):
            return None

        path: list[Vertex] = []
        cursor: Vertex | None = target
        while cursor is not None:
            path.append(cursor)
            cursor = self.predecessors[cursor]
        return list(reversed(path))


@dataclass(frozen=True)
class MSTResult:
    """Standardized Kruskal result using original vertex labels."""

    algorithm: str
    edges: list[Edge]
    total_weight: Weight


def _require_graph(graph: Graph) -> None:
    if not isinstance(graph, Graph):
        raise TypeError("Expected a graph_integration.graph.Graph instance")


def run_dijkstra(graph: Graph, source: Vertex) -> ShortestPathResult:
    """Compute shortest paths. Negative weights are rejected by Dijkstra."""
    _require_graph(graph)
    result = dijkstra(graph.to_adjacency_list(), source)
    return ShortestPathResult(
        algorithm="dijkstra",
        source=result.source,
        distances=result.distances,
        predecessors=result.predecessors,
    )


def run_bellman_ford(graph: Graph, source: Vertex) -> ShortestPathResult:
    """Compute shortest paths, including negative edges unless a reachable
    negative-weight cycle exists (in which case Bellman-Ford raises ValueError).
    """
    _require_graph(graph)
    result = bellman_ford(graph.to_adjacency_list(), source)
    return ShortestPathResult(
        algorithm="bellman_ford",
        source=result.source,
        distances=result.distances,
        predecessors=result.predecessors,
    )


def run_kruskal(graph: Graph) -> MSTResult:
    """Find the MST of a connected, undirected graph.

    Internally maps arbitrary vertex labels to 0..n-1 as required by the
    existing Kruskal implementation, and maps the result back to labels.
    """
    _require_graph(graph)
    count, indexed_edges, labels = graph.to_kruskal_input()
    selected, total_weight = kruskal_mst(count, indexed_edges)
    labeled_edges: list[Edge] = [
        (labels[u], labels[v], weight) for u, v, weight in selected
    ]
    return MSTResult(
        algorithm="kruskal",
        edges=labeled_edges,
        total_weight=total_weight,
    )
