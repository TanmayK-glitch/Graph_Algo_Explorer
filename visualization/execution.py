"""Execute recommended algorithms through the existing public APIs."""

from __future__ import annotations

from typing import Any

from graph_integration.integration import run_bellman_ford, run_dijkstra, run_kruskal
from graph_integration.worklet1_adapter import to_worklet2_graph
from worklet1.algorithms import (
    BFSAlgorithm,
    BipartiteTestAlgorithm,
    ConnectedComponentsAlgorithm,
    CycleDetectionAlgorithm,
    DFSAlgorithm,
    SCCAlgorithm,
    TopologicalSortAlgorithm,
)
from worklet1.graph import Graph


def execute_algorithm(
    graph: Graph,
    algorithm: str,
    *,
    source: Any | None = None,
) -> Any:
    """Run one supported algorithm, adapting to Worklet 2 where required."""
    if algorithm == "BFS":
        return BFSAlgorithm().execute(graph, start=source)
    if algorithm == "DFS":
        return DFSAlgorithm().execute(graph, start=source)
    if algorithm == "ConnectedComponents":
        return ConnectedComponentsAlgorithm().execute(graph)
    if algorithm == "SCC":
        return SCCAlgorithm().execute(graph)
    if algorithm == "CycleDetection":
        return CycleDetectionAlgorithm().execute(graph)
    if algorithm == "TopologicalSort":
        return TopologicalSortAlgorithm().execute(graph)
    if algorithm == "BipartiteTest":
        return BipartiteTestAlgorithm().execute(graph)
    if algorithm in {"dijkstra", "bellman_ford", "kruskal"}:
        converted = to_worklet2_graph(graph)
        if algorithm == "dijkstra":
            if source is None:
                raise ValueError("A source vertex is required for Dijkstra.")
            return run_dijkstra(converted, source)
        if algorithm == "bellman_ford":
            if source is None:
                raise ValueError("A source vertex is required for Bellman-Ford.")
            return run_bellman_ford(converted, source)
        return run_kruskal(converted)
    raise ValueError(f"Unsupported algorithm: {algorithm!r}")
