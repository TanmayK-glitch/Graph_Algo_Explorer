"""Representation-specific tests for AdjacencyListGraph."""

from worklet1.graph import AdjacencyListGraph


def test_internal_storage_undirected_both_directions():
    g = AdjacencyListGraph()
    g.add_edge("A", "B")
    assert [e.dst for e in g._adj["A"]] == ["B"] and [e.dst for e in g._adj["B"]] == ["A"]


def test_internal_storage_directed_one_direction():
    g = AdjacencyListGraph(directed=True)
    g.add_edge("A", "B")
    assert g._adj["B"] == []


def test_self_loop_stored_once():
    g = AdjacencyListGraph()
    g.add_edge("A", "A")
    assert len(g._adj["A"]) == 1


def test_no_adjacency_entries_left_after_remove_vertex():
    g = AdjacencyListGraph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("B", "A")
    g.remove_vertex("B")
    assert g._adj == {"A": []} and "B" not in g._rank


def test_sparse_graph_uses_no_quadratic_storage():
    g = AdjacencyListGraph()
    for i in range(200):
        g.add_vertex(i)
    assert sum(len(v) for v in g._adj.values()) == 0
