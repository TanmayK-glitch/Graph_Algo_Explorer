"""Topological sort tests (FR-16)."""

import pytest

from worklet1.algorithms import TopologicalSortAlgorithm

TS = TopologicalSortAlgorithm()


def assert_valid_order(g, order):
    pos = {v: i for i, v in enumerate(order)}
    assert sorted(order, key=str) == sorted(g.vertices, key=str)
    for e in g.all_edges():
        assert pos[e.src] < pos[e.dst]


def test_diamond(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], directed=True)
    r = TS.execute(g)
    assert r.success and r.primary_output[0] == "A" and r.primary_output[-1] == "D"
    assert r.metadata == {"has_cycle": False} and r.algorithm == "TopologicalSort"
    assert_valid_order(g, r.primary_output)


def test_deterministic_order(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], directed=True)
    assert TS.execute(g).primary_output == ["A", "B", "C", "D"]


def test_cycle_reports_failure(make_graph):
    r = TS.execute(make_graph([("A", "B"), ("B", "A")], directed=True))
    assert r.success is False and r.primary_output is None
    assert r.metadata == {"has_cycle": True} and "cycle" in r.error_message.lower()


def test_longer_cycle_with_tail(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "B"), ("C", "D")], directed=True)
    assert TS.execute(g).success is False


def test_self_loop_is_cycle(make_graph):
    assert TS.execute(make_graph([("A", "A")], directed=True)).success is False


def test_disconnected_dag(make_graph):
    g = make_graph([("A", "B"), ("C", "D")], directed=True, vertices=["E"])
    r = TS.execute(g)
    assert r.success
    assert_valid_order(g, r.primary_output)


def test_empty_graph(GraphClass):
    r = TS.execute(GraphClass(directed=True))
    assert r.success and r.primary_output == []


def test_undirected_rejected(make_graph):
    with pytest.raises(ValueError):
        TS.execute(make_graph([("A", "B")]))


def test_weighted_dag(make_graph):
    g = make_graph([("A", "B", -5.0), ("B", "C", 2.0)], directed=True, weighted=True)
    assert TS.execute(g).primary_output == ["A", "B", "C"]
