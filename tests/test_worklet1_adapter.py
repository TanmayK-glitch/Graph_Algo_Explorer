"""Tests for converting Worklet 1 graphs to Worklet 2."""

import pytest

from graph_integration.integration import (
    run_bellman_ford,
    run_dijkstra,
    run_kruskal,
)
from graph_integration.worklet1_adapter import to_worklet2_graph
from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph


@pytest.mark.parametrize(
    "graph_type",
    [AdjacencyListGraph, AdjacencyMatrixGraph],
)
def test_conversion_preserves_vertices_edges_and_weights(graph_type):
    graph = graph_type(directed=False, weighted=True)
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "C", 1)
    graph.add_vertex("isolated")

    converted = to_worklet2_graph(graph)

    assert converted.vertices == ["A", "B", "C", "isolated"]
    assert converted.to_edge_list() == [
        ("A", "B", 4.0),
        ("A", "C", 2.0),
        ("B", "C", 1.0),
    ]


def test_dijkstra_works_with_converted_graph():
    graph = AdjacencyListGraph(directed=True, weighted=True)
    graph.add_edge("start", "middle", 2)
    graph.add_edge("middle", "end", 3)

    converted = to_worklet2_graph(graph)
    result = run_dijkstra(converted, "start")

    assert result.distances["end"] == 5
    assert result.path_to("end") == ["start", "middle", "end"]


def test_bellman_ford_supports_negative_edges():
    graph = AdjacencyListGraph(directed=True, weighted=True)
    graph.add_edge("A", "B", -2)
    graph.add_edge("B", "C", 3)

    result = run_bellman_ford(to_worklet2_graph(graph), "A")

    assert result.distances["C"] == 1


def test_kruskal_preserves_original_labels():
    graph = AdjacencyListGraph(directed=False, weighted=True)
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "C", 1)

    result = run_kruskal(to_worklet2_graph(graph))

    assert result.total_weight == 3
    assert len(result.edges) == 2


def test_unweighted_graph_is_rejected():
    graph = AdjacencyListGraph(directed=False, weighted=False)
    graph.add_edge("A", "B")

    with pytest.raises(ValueError, match="weighted"):
        to_worklet2_graph(graph)


def test_self_loop_is_rejected():
    graph = AdjacencyListGraph(directed=False, weighted=True)
    graph.add_edge("A", "A", 1)

    with pytest.raises(ValueError, match="self-loops"):
        to_worklet2_graph(graph)
