"""Strongly connected components tests (FR-14)."""

import pytest

from worklet1.algorithms import SCCAlgorithm

SCC = SCCAlgorithm()


def test_design_example(make_graph):
    g = make_graph([("A", "B"), ("B", "A"), ("C", "D")], directed=True)
    r = SCC.execute(g)
    assert r.primary_output == [["A", "B"], ["C"], ["D"]]
    assert r.algorithm == "SCC" and r.metadata["count"] == 3


def test_single_big_cycle(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A")], directed=True)
    assert SCC.execute(g).primary_output == [["A", "B", "C"]]


def test_dag_gives_all_singletons(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], directed=True)
    assert SCC.execute(g).primary_output == [["A"], ["B"], ["C"], ["D"]]


def test_classic_clrs_graph(make_graph):
    edges = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "c"), ("b", "e"), ("e", "a"), ("e", "f"),
             ("b", "f"), ("c", "g"), ("f", "g"), ("g", "f"), ("d", "h"), ("g", "h"), ("h", "h")]
    r = SCC.execute(make_graph(edges, directed=True))
    assert sorted(map(sorted, r.primary_output)) == [["a", "b", "e"], ["c", "d"], ["f", "g"], ["h"]]


def test_self_loop_is_own_component(make_graph):
    g = make_graph([("A", "A"), ("A", "B")], directed=True)
    assert SCC.execute(g).primary_output == [["A"], ["B"]]


def test_isolated_and_empty(make_graph, GraphClass):
    assert SCC.execute(make_graph(vertices=["A", "B"], directed=True)).primary_output == [["A"], ["B"]]
    assert SCC.execute(GraphClass(directed=True)).primary_output == []


def test_partition_property(make_graph):
    g = make_graph([("A", "B"), ("B", "A"), ("B", "C"), ("C", "D"), ("D", "C"), ("E", "A")],
                   directed=True)
    comps = SCC.execute(g).primary_output
    flat = [v for c in comps for v in c]
    assert sorted(flat) == sorted(g.vertices) and len(flat) == len(set(flat))


def test_component_map(make_graph):
    r = SCC.execute(make_graph([("A", "B"), ("B", "A")], directed=True, vertices=["C"]))
    assert r.metadata["component_map"] == {"A": 0, "B": 0, "C": 1}


def test_undirected_rejected(make_graph):
    with pytest.raises(ValueError):
        SCC.execute(make_graph([("A", "B")]))
