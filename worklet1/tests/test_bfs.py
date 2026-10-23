"""BFS tests (FR-11, FR-18, NFR-07)."""

import pytest

from worklet1.algorithms import BFSAlgorithm, bfs, bfs_all
from worklet1.graph import VertexNotFoundError


def test_bfs_simple(make_graph):
    g = make_graph([("A", "B"), ("B", "C")])
    assert BFSAlgorithm().execute(g, start="A").primary_output == ["A", "B", "C"]


def test_bfs_levels_order(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")])
    r = bfs(g, "A")
    assert r.primary_output == ["A", "B", "C", "D", "E"]
    assert r.algorithm == "BFS" and r.success and r.metadata["start"] == "A"


def test_bfs_parent_map_gives_shortest_paths(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("A", "D"), ("D", "C"), ("C", "E")])
    parent = bfs(g, "A").metadata["parent"]
    assert parent["A"] is None and parent["C"] in ("B", "D") and parent["E"] == "C"


def test_bfs_covers_only_start_component(make_graph):
    g = make_graph([("A", "B"), ("C", "D")], vertices=["E"])
    assert bfs(g, "A").primary_output == ["A", "B"]
    assert bfs(g, "E").primary_output == ["E"]


def test_bfs_all_restarts(make_graph):
    g = make_graph([("A", "B")], vertices=["C"])
    r = bfs_all(g)
    assert r.primary_output == ["A", "B", "C"] and r.algorithm == "BFS_ALL" and r.metadata == {}


def test_execute_all_mode(make_graph):
    g = make_graph([("A", "B"), ("C", "D")])
    r = BFSAlgorithm().execute(g, mode="all")
    assert r.algorithm == "BFS_ALL" and r.primary_output == ["A", "B", "C", "D"]


def test_directed_bfs_follows_edge_direction(make_graph):
    g = make_graph([("A", "B"), ("C", "A")], directed=True)
    assert bfs(g, "A").primary_output == ["A", "B"]


def test_cycle_does_not_loop_forever(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A")], directed=True)
    assert bfs(g, "A").primary_output == ["A", "B", "C"]


def test_self_loop_ok(make_graph):
    g = make_graph([("A", "A"), ("A", "B")])
    assert bfs(g, "A").primary_output == ["A", "B"]


def test_single_vertex(make_graph):
    assert bfs(make_graph(vertices=["A"]), "A").primary_output == ["A"]


def test_invalid_start_vertex(make_graph):
    g = make_graph([("A", "B")])
    with pytest.raises(VertexNotFoundError):
        bfs(g, "Z")
    with pytest.raises(VertexNotFoundError):
        BFSAlgorithm().execute(g, start="Z")


def test_missing_start_and_bad_mode(make_graph):
    g = make_graph([("A", "B")])
    with pytest.raises(ValueError):
        BFSAlgorithm().execute(g)
    with pytest.raises(ValueError):
        BFSAlgorithm().execute(g, start="A", mode="everything")


def test_empty_graph(GraphClass):
    g = GraphClass()
    assert bfs_all(g).primary_output == []
    with pytest.raises(VertexNotFoundError):
        bfs(g, "A")


def test_weighted_graph_ignores_weights(make_graph):
    g = make_graph([("A", "B", 10.0), ("A", "C", -3.0)], weighted=True)
    assert bfs(g, "A").primary_output == ["A", "B", "C"]


def test_name_property():
    assert BFSAlgorithm().name == "BFS"
