"""Bipartite test tests (FR-17)."""

import pytest

from worklet1.algorithms import BipartiteTestAlgorithm

BT = BipartiteTestAlgorithm()


def assert_valid_colouring(g, colouring):
    assert set(colouring) == set(g.vertices)
    assert set(colouring.values()) <= {0, 1}
    for e in g.all_edges():
        assert colouring[e.src] != colouring[e.dst]


def test_triangle_not_bipartite(make_graph):
    r = BT.execute(make_graph([("A", "B"), ("B", "C"), ("A", "C")]))
    assert r.primary_output is False and r.algorithm == "BipartiteTest" and r.success


def test_even_cycle_bipartite(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])
    r = BT.execute(g)
    assert r.primary_output is True
    assert_valid_colouring(g, r.metadata["colouring"])


def test_five_cycle_not_bipartite(make_graph):
    edges = [(i, (i + 1) % 5) for i in range(5)]
    assert BT.execute(make_graph(edges)).primary_output is False


def test_disconnected_bipartite(make_graph):
    g = make_graph([("A", "B"), ("C", "D")])
    r = BT.execute(g)
    assert r.primary_output is True
    assert_valid_colouring(g, r.metadata["colouring"])


def test_disconnected_one_bad_component(make_graph):
    g = make_graph([("A", "B"), ("C", "D"), ("D", "E"), ("C", "E")])
    assert BT.execute(g).primary_output is False


def test_self_loop_not_bipartite(make_graph):
    assert BT.execute(make_graph([("A", "A")])).primary_output is False


def test_isolated_vertices_and_empty(make_graph, GraphClass):
    g = make_graph(vertices=["A", "B"])
    r = BT.execute(g)
    assert r.primary_output is True and set(r.metadata["colouring"]) == {"A", "B"}
    r = BT.execute(GraphClass())
    assert r.primary_output is True and r.metadata["colouring"] == {}


def test_tree_bipartite(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "E")])
    r = BT.execute(g)
    assert_valid_colouring(g, r.metadata["colouring"])


def test_directed_rejected(make_graph):
    with pytest.raises(ValueError):
        BT.execute(make_graph([("A", "B")], directed=True))
