"""Connected components tests (FR-13)."""

import pytest

from worklet1.algorithms import ConnectedComponentsAlgorithm

CC = ConnectedComponentsAlgorithm()


def test_two_components(make_graph):
    r = CC.execute(make_graph([("A", "B"), ("C", "D")]))
    assert r.primary_output == [["A", "B"], ["C", "D"]]
    assert r.metadata["count"] == 2 and r.algorithm == "ConnectedComponents"


def test_isolated_vertices_are_singletons(make_graph):
    r = CC.execute(make_graph(vertices=["A", "B", "C"]))
    assert r.primary_output == [["A"], ["B"], ["C"]] and r.metadata["count"] == 3


def test_empty_graph(GraphClass):
    r = CC.execute(GraphClass())
    assert r.primary_output == [] and r.metadata["count"] == 0


def test_single_component(make_graph):
    r = CC.execute(make_graph([("A", "B"), ("B", "C"), ("C", "A")]))
    assert r.primary_output == [["A", "B", "C"]]


def test_partition_property(make_graph):
    g = make_graph([("A", "B"), ("C", "D"), ("D", "E")], vertices=["F"])
    comps = CC.execute(g).primary_output
    flat = [v for c in comps for v in c]
    assert sorted(flat) == sorted(g.vertices) and len(flat) == len(set(flat))


def test_canonical_order_independent_of_edge_order(make_graph):
    g = make_graph([("D", "C"), ("B", "A")], vertices=["A", "B", "C", "D"], first=True)
    assert CC.execute(g).primary_output == [["A", "B"], ["C", "D"]]


def test_component_map(make_graph):
    r = CC.execute(make_graph([("A", "B")], vertices=["C"]))
    assert r.metadata["component_map"] == {"A": 0, "B": 0, "C": 1}


def test_self_loop_does_not_merge_components(make_graph):
    r = CC.execute(make_graph([("A", "A")], vertices=["B"]))
    assert r.primary_output == [["A"], ["B"]]


def test_directed_graph_rejected(make_graph):
    with pytest.raises(ValueError):
        CC.execute(make_graph([("A", "B")], directed=True))
