"""DFS tests (FR-12, FR-18, NFR-08)."""

import pytest

from worklet1.algorithms import DFSAlgorithm, dfs, dfs_all
from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph, VertexNotFoundError


def test_dfs_preorder(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D")])
    assert DFSAlgorithm().execute(g, start="A").primary_output == ["A", "B", "D", "C"]


def test_dfs_back_edge_visits_all_without_reporting_cycle(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A")])
    r = dfs(g, "A")
    assert sorted(r.primary_output) == ["A", "B", "C"] and r.metadata == {"start": "A"}


def test_dfs_covers_only_start_component(make_graph):
    g = make_graph([("A", "B"), ("C", "D")])
    assert dfs(g, "C").primary_output == ["C", "D"]


def test_dfs_all(make_graph):
    g = make_graph([("A", "B"), ("C", "D")], vertices=["E"])
    r = dfs_all(g)
    assert r.primary_output == ["A", "B", "C", "D", "E"] and r.algorithm == "DFS_ALL"


def test_execute_all_mode(make_graph):
    g = make_graph([("A", "B")], vertices=["C"])
    assert DFSAlgorithm().execute(g, mode="all").primary_output == ["A", "B", "C"]


def test_directed_dfs(make_graph):
    g = make_graph([("A", "B"), ("C", "A")], directed=True)
    assert dfs(g, "A").primary_output == ["A", "B"]


def test_visits_each_vertex_once(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("D", "A")])
    order = dfs(g, "A").primary_output
    assert len(order) == len(set(order)) == 4


def test_invalid_start(make_graph):
    with pytest.raises(VertexNotFoundError):
        dfs(make_graph([("A", "B")]), "Z")
    with pytest.raises(ValueError):
        DFSAlgorithm().execute(make_graph([("A", "B")]))
    with pytest.raises(ValueError):
        DFSAlgorithm().execute(make_graph([("A", "B")]), start="A", mode="x")


def test_empty_and_single(GraphClass):
    g = GraphClass()
    assert dfs_all(g).primary_output == []
    g.add_vertex("A")
    assert dfs(g, "A").primary_output == ["A"]


def test_recursion_limit_is_a_documented_limitation():
    """Design section 14 / D-12: very deep graphs hit Python's recursion limit."""
    g = AdjacencyListGraph(directed=True)
    for i in range(5000):
        g.add_edge(i, i + 1)
    with pytest.raises(RecursionError):
        dfs(g, 0)


def test_moderately_deep_graph_ok():
    g = AdjacencyListGraph(directed=True)
    for i in range(300):  # "a few hundred vertices" target size
        g.add_edge(i, i + 1)
    assert len(dfs(g, 0).primary_output) == 301


# ------------------------------------------------ opt-in iterative variant (D-12)
def test_iterative_has_no_recursion_limit():
    g = AdjacencyListGraph(directed=True)
    for i in range(5000):
        g.add_edge(i, i + 1)
    assert len(dfs(g, 0, iterative=True).primary_output) == 5001
    assert len(dfs_all(g, iterative=True).primary_output) == 5001


def test_iterative_order_equals_recursive_on_random_graphs():
    import random

    for seed in range(60):
        rng = random.Random(seed)
        n = rng.randint(1, 12)
        for directed in (False, True):
            for cls in (AdjacencyListGraph, AdjacencyMatrixGraph):
                g = cls(directed=directed)
                for v in range(n):
                    g.add_vertex(v)
                for u in range(n):
                    for v in range(n):
                        if (directed or u <= v) and rng.random() < 0.25:
                            g.add_edge(u, v)
                assert dfs_all(g).primary_output == dfs_all(g, iterative=True).primary_output
                assert dfs(g, 0).primary_output == dfs(g, 0, iterative=True).primary_output


def test_execute_iterative_flag(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D")])
    a = DFSAlgorithm().execute(g, start="A")
    b = DFSAlgorithm().execute(g, start="A", iterative=True)
    assert a.primary_output == b.primary_output == ["A", "B", "D", "C"]
    assert b.algorithm == "DFS" and b.metadata == {"start": "A"}
    assert DFSAlgorithm().execute(g, mode="all", iterative=True).algorithm == "DFS_ALL"
