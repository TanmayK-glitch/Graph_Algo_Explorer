"""Adapters for converting Worklet 1 graphs to Worklet 2's graph model."""

from __future__ import annotations

from graph_integration.graph import Graph as Worklet2Graph
from worklet1.graph import Graph as Worklet1Graph


def to_worklet2_graph(graph: Worklet1Graph) -> Worklet2Graph:
    """Convert a Worklet 1 graph to Worklet 2's graph representation.

    Preserves vertex labels, weights, directedness, and isolated vertices.

    Worklet 2 does not support self-loops. Conversion raises ValueError
    rather than silently discarding them.
    """
    if not isinstance(graph, Worklet1Graph):
        raise TypeError("Expected a Worklet 1 Graph instance")

    if not graph.is_weighted:
        raise ValueError("Worklet 2 requires weighted edges")

    converted = Worklet2Graph(directed=graph.is_directed)

    for vertex in graph.vertices:
        converted.add_vertex(vertex)

    edges = graph.all_edges()

    for edge in edges:
        if edge.src == edge.dst:
            raise ValueError("Cannot convert graphs containing self-loops")

        if edge.weight is None:
            raise ValueError("Worklet 2 requires a weight for every edge")

        converted.add_edge(edge.src, edge.dst, edge.weight)

    return converted
