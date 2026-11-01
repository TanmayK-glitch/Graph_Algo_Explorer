import pytest

from visualization.execution import execute_algorithm
from visualization.input_parser import InputFormatError, parse_edge_list
from visualization.recommendation import recommend_algorithm
from visualization.renderer import _get_layout_config, render_graph


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


def test_example_presets():
    from app import EXAMPLES

    assert set(EXAMPLES.keys()) == {
        "Weighted shortest path",
        "Directed DAG",
        "Undirected traversal",
    }

    # 1. Weighted shortest path preset
    sp = EXAMPLES["Weighted shortest path"]
    assert sp["directed"] is True
    assert sp["weighted"] is True
    assert sp["objective"] == "Shortest path"
    parsed_sp = parse_edge_list(
        sp["edge_text"], directed=sp["directed"], weighted=sp["weighted"]
    )
    rec_sp = recommend_algorithm(
        sp["objective"],
        parsed_sp.graph,
        has_negative_weight=parsed_sp.has_negative_weight,
    )
    assert rec_sp.algorithm == "dijkstra"
    assert rec_sp.supported is True

    # 2. Directed DAG preset (unweighted)
    dag = EXAMPLES["Directed DAG"]
    assert dag["directed"] is True
    assert dag["weighted"] is False
    assert dag["objective"] == "Topological ordering"
    parsed_dag = parse_edge_list(
        dag["edge_text"], directed=dag["directed"], weighted=dag["weighted"]
    )
    rec_dag = recommend_algorithm(
        dag["objective"],
        parsed_dag.graph,
        has_negative_weight=parsed_dag.has_negative_weight,
    )
    assert rec_dag.algorithm == "TopologicalSort"
    assert rec_dag.supported is True
    topo_res = execute_algorithm(parsed_dag.graph, "TopologicalSort")
    assert topo_res.primary_output == ["A", "B", "C", "D"]

    # 3. Undirected traversal preset
    trav = EXAMPLES["Undirected traversal"]
    assert trav["directed"] is False
    assert trav["weighted"] is False
    assert trav["objective"] == "Explore or traverse"
    parsed_trav = parse_edge_list(
        trav["edge_text"], directed=trav["directed"], weighted=trav["weighted"]
    )
    rec_trav = recommend_algorithm(
        trav["objective"],
        parsed_trav.graph,
        has_negative_weight=parsed_trav.has_negative_weight,
    )
    assert rec_trav.algorithm == "BFS"
    assert rec_trav.supported is True
    bfs_res = execute_algorithm(parsed_trav.graph, "BFS", source="A")
    assert bfs_res.primary_output == ["A", "B", "C", "D"]


def test_render_graph_dijkstra_textbook():
    textbook_edges = """s t 10
s y 5
t x 1
t y 2
y t 3
y x 9
y z 2
z s 7
z x 6
x z 4"""
    parsed = parse_edge_list(textbook_edges, directed=True, weighted=True)
    result = execute_algorithm(parsed.graph, "dijkstra", source="s")
    html = render_graph(parsed.graph, result, source="s", target="x")

    assert "Source Vertex: s" in html
    assert "Destination Vertex: x" in html
    assert "Path Vertex: t" in html
    assert "Path Vertex: y" in html
    assert "curvedCW" in html  # bidirectional pairs curved
    assert "#2ec4b6" in html  # source color
    assert "#e71d36" in html  # destination / path edge color
    assert "#ff9f1c" in html  # path intermediate color


def test_render_graph_kruskal_mst():
    mst_edges = """A B 4
A H 8
B C 8
B H 11"""
    parsed = parse_edge_list(mst_edges, directed=False, weighted=True)
    result = execute_algorithm(parsed.graph, "kruskal")
    html = render_graph(parsed.graph, result)

    assert "MST Vertex:" in html
    assert "#ff9f1c" in html
    assert "#e71d36" in html


def test_layout_config_adaptive():
    small = _get_layout_config(5)
    med = _get_layout_config(20)
    large = _get_layout_config(50)
    xlarge = _get_layout_config(100)

    assert (
        small["springLength"]
        > med["springLength"]
        > large["springLength"]
        > xlarge["springLength"]
    )
    assert (
        small["gravitationalConstant"]
        < med["gravitationalConstant"]
        < large["gravitationalConstant"]
        < xlarge["gravitationalConstant"]
    )
    assert small["avoidOverlap"] >= med["avoidOverlap"] >= large["avoidOverlap"]


# ---------------------------------------------------------------------------
# Display-name mapping tests
# ---------------------------------------------------------------------------


def test_display_names_cover_all_recommendation_identifiers():
    """Every internal algorithm identifier used by the recommendation engine
    must have a corresponding entry in the centralized DISPLAY_NAMES mapping."""
    from app import DISPLAY_NAMES

    # Collect every algorithm identifier the recommendation engine can return.
    objectives_and_graphs = [
        ("Shortest path", False, False, "A B"),
        ("Shortest path", True, True, "A B 2"),
        ("Shortest path", True, True, "A B -2"),
        ("Explore or traverse", False, False, "A B"),
        ("Minimum spanning tree", False, True, "A B 2"),
        ("Check connectivity", True, False, "A B"),
        ("Check connectivity", False, False, "A B"),
        ("Detect cycles", False, False, "A B"),
        ("Topological ordering", True, False, "A B"),
        ("Check bipartite", False, False, "A B"),
    ]
    returned_identifiers = set()
    for objective, directed, weighted, text in objectives_and_graphs:
        parsed = parse_edge_list(text, directed=directed, weighted=weighted)
        rec = recommend_algorithm(
            objective,
            parsed.graph,
            has_negative_weight=parsed.has_negative_weight,
        )
        if rec.algorithm is not None:
            returned_identifiers.add(rec.algorithm)

    assert returned_identifiers, "Expected at least one algorithm identifier"
    for identifier in returned_identifiers:
        assert identifier in DISPLAY_NAMES, (
            f"Algorithm identifier {identifier!r} is missing from DISPLAY_NAMES"
        )


@pytest.mark.parametrize(
    ("internal_id", "expected_display"),
    [
        ("dijkstra", "Dijkstra"),
        ("bellman_ford", "Bellman-Ford"),
        ("kruskal", "Kruskal"),
        ("BFS", "BFS"),
        ("DFS", "DFS"),
        ("ConnectedComponents", "Connected Components"),
        ("SCC", "Strongly Connected Components"),
        ("CycleDetection", "Cycle Detection"),
        ("TopologicalSort", "Topological Sort"),
        ("BipartiteTest", "Bipartite Test"),
    ],
)
def test_display_name_formatting(internal_id, expected_display):
    from app import _display_name

    assert _display_name(internal_id) == expected_display


def test_display_name_returns_unsupported_for_none():
    from app import _display_name

    assert _display_name(None) == "Unsupported"


def test_display_name_passes_through_unknown():
    from app import _display_name

    assert _display_name("some_future_algo") == "some_future_algo"
