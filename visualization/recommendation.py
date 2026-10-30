"""Deterministic algorithm recommendations for the visualization UI."""

from __future__ import annotations

from dataclasses import dataclass

from worklet1.graph import Graph

OBJECTIVES = (
    "Shortest path",
    "Explore or traverse",
    "Minimum spanning tree",
    "Check connectivity",
    "Detect cycles",
    "Topological ordering",
    "Check bipartite",
)


@dataclass(frozen=True)
class Recommendation:
    """The selected algorithm and the reason it is applicable or unsupported."""

    objective: str
    algorithm: str | None
    explanation: str
    properties: tuple[str, ...]
    limitations: tuple[str, ...] = ()

    @property
    def supported(self) -> bool:
        return self.algorithm is not None


def _is_connected(graph: Graph) -> bool:
    if not graph.vertices:
        return False
    visited = {graph.vertices[0]}
    pending = [graph.vertices[0]]
    while pending:
        vertex = pending.pop()
        for neighbour in graph.neighbours(vertex):
            if neighbour not in visited:
                visited.add(neighbour)
                pending.append(neighbour)
    return len(visited) == graph.vertex_count()


def _has_self_loop(graph: Graph) -> bool:
    return any(edge.src == edge.dst for edge in graph.all_edges())


def recommend_algorithm(
    objective: str,
    graph: Graph,
    *,
    has_negative_weight: bool = False,
) -> Recommendation:
    """Choose a supported algorithm using graph direction and weight rules."""
    if objective not in OBJECTIVES:
        raise ValueError(f"Unknown objective: {objective!r}")

    properties = (
        f"{'directed' if graph.is_directed else 'undirected'}",
        f"{'weighted' if graph.is_weighted else 'unweighted'}",
        f"{graph.vertex_count()} vertices",
        f"{graph.edge_count()} edges",
    )
    if graph.is_weighted:
        properties += (
            "contains negative weights"
            if has_negative_weight
            else "all weights nonnegative",
        )

    if objective == "Shortest path":
        if not graph.is_weighted:
            return Recommendation(
                objective,
                "BFS",
                "BFS finds shortest paths by number of edges in an unweighted graph.",
                properties,
            )
        if _has_self_loop(graph):
            return Recommendation(
                objective,
                None,
                "The weighted integration layer does not support self-loops.",
                properties,
                ("Remove self-loops to run a weighted shortest-path algorithm.",),
            )
        if has_negative_weight and not graph.is_directed:
            return Recommendation(
                objective,
                None,
                "No shortest-path wrapper is applicable: a negative undirected edge creates a negative two-way cycle.",
                properties,
                ("Use a directed graph for Bellman-Ford, or remove negative weights.",),
            )
        if has_negative_weight:
            return Recommendation(
                objective,
                "bellman_ford",
                "Bellman-Ford supports negative edges and reports reachable negative cycles.",
                properties,
                (
                    "The result is unavailable if a reachable negative-weight cycle exists.",
                ),
            )
        return Recommendation(
            objective,
            "dijkstra",
            "Dijkstra is appropriate because every edge weight is nonnegative.",
            properties,
        )

    if objective == "Explore or traverse":
        return Recommendation(
            objective,
            "BFS",
            "BFS provides a deterministic breadth-first traversal from the chosen source.",
            properties,
        )
    if objective == "Minimum spanning tree":
        if graph.is_directed:
            return Recommendation(
                objective, None, "Kruskal requires an undirected graph.", properties
            )
        if not graph.is_weighted:
            return Recommendation(
                objective, None, "Kruskal requires weighted edges.", properties
            )
        if _has_self_loop(graph):
            return Recommendation(
                objective,
                None,
                "The weighted integration layer does not support self-loops.",
                properties,
            )
        if not _is_connected(graph):
            return Recommendation(
                objective,
                None,
                "The existing Kruskal wrapper requires a connected graph.",
                properties,
                (
                    "Add edges connecting every component, or choose a traversal objective.",
                ),
            )
        return Recommendation(
            objective,
            "kruskal",
            "Kruskal computes a minimum spanning tree for a connected undirected weighted graph.",
            properties,
        )
    if objective == "Check connectivity":
        algorithm = "SCC" if graph.is_directed else "ConnectedComponents"
        explanation = (
            "Strongly connected components are the directed connectivity result."
            if graph.is_directed
            else "Connected components partition an undirected graph."
        )
        return Recommendation(objective, algorithm, explanation, properties)
    if objective == "Detect cycles":
        return Recommendation(
            objective,
            "CycleDetection",
            "Cycle detection selects directed or undirected logic from the graph flag.",
            properties,
        )
    if objective == "Topological ordering":
        if not graph.is_directed:
            return Recommendation(
                objective,
                None,
                "Topological ordering is defined only for directed graphs.",
                properties,
            )
        return Recommendation(
            objective,
            "TopologicalSort",
            "Kahn's topological sort is implemented for directed graphs.",
            properties,
        )
    if not graph.is_directed:
        return Recommendation(
            objective,
            "BipartiteTest",
            "The existing bipartite test supports undirected graphs.",
            properties,
        )
    return Recommendation(
        objective,
        None,
        "The existing bipartite implementation requires an undirected graph.",
        properties,
    )
