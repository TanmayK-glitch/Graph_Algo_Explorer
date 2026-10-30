import pytest

from visualization.execution import execute_algorithm
from visualization.input_parser import InputFormatError, parse_edge_list
from visualization.recommendation import recommend_algorithm


def test_parse_unweighted_edges_and_isolated_vertex():
    parsed = parse_edge_list("A B\nB C\nisolated", directed=False, weighted=False)

    assert parsed.graph.vertices == ["A", "B", "C", "isolated"]
    assert parsed.edge_count == 2
    assert not parsed.has_negative_weight


def test_parse_weighted_negative_edges():
    parsed = parse_edge_list("A B -2\nB C 3", directed=True, weighted=True)

    assert parsed.has_negative_weight
    assert parsed.graph.edge_weight("A", "B") == -2.0


@pytest.mark.parametrize(
    ("objective", "directed", "weighted", "text", "expected"),
    [
        ("Shortest path", False, False, "A B", "BFS"),
        ("Shortest path", True, True, "A B 2", "dijkstra"),
        ("Shortest path", True, True, "A B -2", "bellman_ford"),
        ("Minimum spanning tree", False, True, "A B 2", "kruskal"),
        ("Topological ordering", True, False, "A B", "TopologicalSort"),
        ("Check bipartite", False, False, "A B", "BipartiteTest"),
    ],
)
def test_recommendations(objective, directed, weighted, text, expected):
    parsed = parse_edge_list(text, directed=directed, weighted=weighted)

    recommendation = recommend_algorithm(
        objective,
        parsed.graph,
        has_negative_weight=parsed.has_negative_weight,
    )

    assert recommendation.algorithm == expected


def test_rejects_incompatible_recommendations():
    directed = parse_edge_list("A B 1", directed=True, weighted=True)
    negative_undirected = parse_edge_list("A B -1", directed=False, weighted=True)
    disconnected = parse_edge_list("A B 1\nC D 1", directed=False, weighted=True)

    assert (
        recommend_algorithm("Minimum spanning tree", directed.graph).algorithm is None
    )
    assert (
        recommend_algorithm(
            "Shortest path",
            negative_undirected.graph,
            has_negative_weight=True,
        ).algorithm
        is None
    )
    assert (
        recommend_algorithm("Minimum spanning tree", disconnected.graph).algorithm
        is None
    )


@pytest.mark.parametrize(
    "text",
    ["", "A", "A B", "A B nope", "A B 1 2"],
)
def test_invalid_weighted_input(text):
    if text == "A":
        parsed = parse_edge_list(text, directed=False, weighted=True)
        assert parsed.graph.vertices == ["A"]
        return
    with pytest.raises(InputFormatError):
        parse_edge_list(text, directed=False, weighted=True)


def test_execution_uses_existing_algorithms():
    parsed = parse_edge_list("A B\nA C\nB D\nC D", directed=False, weighted=False)

    result = execute_algorithm(parsed.graph, "BFS", source="A")

    assert result.primary_output == ["A", "B", "C", "D"]
