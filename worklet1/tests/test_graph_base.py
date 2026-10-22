"""Graph model tests plus the shared contract run against BOTH representations."""

import pytest

from worklet1.algorithms.base import Algorithm, AlgorithmResult
from worklet1.graph import (
    AdjacencyListGraph,
    Edge,
    EdgeAlreadyExistsError,
    EdgeNotFoundError,
    Graph,
    GraphError,
    Vertex,
    VertexNotFoundError,
)


# ----------------------------------------------------------------- model / ABC
def test_graph_is_abstract():
    with pytest.raises(TypeError):
        Graph()


def test_incomplete_subclass_cannot_be_instantiated():
    class Broken(Graph):
        pass

    with pytest.raises(TypeError):
        Broken()


def test_vertex_and_edge_models():
    assert Vertex("A").data is None
    e = Edge("A", "B")
    assert (e.src, e.dst, e.weight) == ("A", "B", None)
    assert Edge("A", "B", 2.5).weight == 2.5


def test_exception_hierarchy():
    assert issubclass(VertexNotFoundError, (GraphError, KeyError))
    assert issubclass(EdgeNotFoundError, (GraphError, KeyError))
    assert issubclass(EdgeAlreadyExistsError, (GraphError, ValueError))
    assert "'Z'" in str(VertexNotFoundError("Z"))


def test_algorithm_result_defaults():
    r = AlgorithmResult("X", [1])
    assert (r.algorithm, r.primary_output, r.metadata, r.success, r.error_message) == (
        "X", [1], {}, True, "")
    assert AlgorithmResult("X", 1).metadata is not AlgorithmResult("X", 1).metadata


def test_algorithm_is_abstract():
    with pytest.raises(TypeError):
        Algorithm()


# -------------------------------------------------------------------- contract
def test_flags(GraphClass):
    g = GraphClass(directed=True, weighted=True)
    assert g.is_directed and g.is_weighted
    d = GraphClass()
    assert not d.is_directed and not d.is_weighted


def test_add_vertex_and_isolated(make_graph):
    g = make_graph(vertices=["A", "B"])
    assert g.vertices == ["A", "B"] and g.vertex_count() == 2 and g.edge_count() == 0
    g.add_vertex("A")  # idempotent
    assert g.vertex_count() == 2
    assert g.neighbours("A") == []


def test_vertices_returns_copy(make_graph):
    g = make_graph(vertices=["A"])
    g.vertices.append("Z")
    assert g.vertices == ["A"]


@pytest.mark.parametrize("bad", [1.5, None, True, (1, 2), b"x"])
def test_invalid_vertex_ids_rejected(GraphClass, bad):
    with pytest.raises(TypeError):
        GraphClass().add_vertex(bad)


def test_int_and_str_vertices(GraphClass):
    g = GraphClass()
    g.add_edge(1, "x")
    assert g.has_edge(1, "x") and g.neighbours(1) == ["x"]


def test_directed_edge(make_graph):
    g = make_graph([("A", "B")], directed=True)
    assert g.has_edge("A", "B") and not g.has_edge("B", "A")
    assert g.neighbours("A") == ["B"] and g.neighbours("B") == []
    assert g.edge_count() == 1


def test_undirected_edge_symmetry(make_graph):
    g = make_graph([("A", "B")])
    assert g.has_edge("A", "B") and g.has_edge("B", "A")
    assert g.neighbours("A") == ["B"] and g.neighbours("B") == ["A"]
    assert g.edge_count() == 1
    assert [(e.src, e.dst) for e in g.all_edges()] == [("A", "B")]


def test_add_edge_creates_vertices(make_graph):
    g = make_graph([("A", "B")])
    assert g.vertices == ["A", "B"]


def test_weighted_edge(make_graph):
    g = make_graph([("A", "B", 3.5)], weighted=True)
    assert g.edge_weight("A", "B") == 3.5 and g.edge_weight("B", "A") == 3.5
    assert g.all_edges()[0].weight == 3.5


def test_integer_weight_stored_as_float(make_graph):
    g = make_graph([("A", "B", 2)], weighted=True)
    assert g.edge_weight("A", "B") == 2.0 and isinstance(g.edge_weight("A", "B"), float)


def test_negative_and_zero_weights_allowed(make_graph):
    g = make_graph([("A", "B", -4.0), ("B", "C", 0)], directed=True, weighted=True)
    assert g.has_edge("A", "B") and g.edge_weight("A", "B") == -4.0
    assert g.has_edge("B", "C") and g.edge_weight("B", "C") == 0.0  # zero is still an edge
    assert g.edge_count() == 2


def test_unweighted_weight_is_none(make_graph):
    g = make_graph([("A", "B")])
    assert g.edge_weight("A", "B") is None
    assert g.all_edges()[0].weight is None
    assert g.edge_weight("B", "A") is None


def test_edge_weight_absent_edge_is_none(make_graph):
    g = make_graph([("A", "B", 1)], directed=True, weighted=True, vertices=["C"])
    assert g.edge_weight("B", "A") is None and g.edge_weight("A", "C") is None
    with pytest.raises(VertexNotFoundError):
        g.edge_weight("A", "Z")


def test_weight_policy(GraphClass):
    weighted = GraphClass(weighted=True)
    with pytest.raises(ValueError):
        weighted.add_edge("A", "B")  # weight required
    unweighted = GraphClass()
    with pytest.raises(ValueError):
        unweighted.add_edge("A", "B", 3)  # weight not allowed
    for bad in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError):
            weighted.add_edge("A", "B", bad)
    for bad in ("3", True, None.__class__):
        with pytest.raises(TypeError):
            weighted.add_edge("A", "B", bad)
    with pytest.raises(ValueError):
        weighted.add_edge("A", "B", 10 ** 400)


def test_failed_add_edge_leaves_graph_unchanged(GraphClass):
    g = GraphClass(weighted=True)
    with pytest.raises(ValueError):
        g.add_edge("A", "B", float("nan"))
    assert g.vertices == [] and g.edge_count() == 0
    with pytest.raises(TypeError):
        g.add_edge("A", 1.5, 1.0)
    assert g.vertices == []


@pytest.mark.parametrize("directed", [True, False])
def test_duplicate_edge_rejected(make_graph, directed):
    g = make_graph([("A", "B")], directed=directed)
    with pytest.raises(EdgeAlreadyExistsError):
        g.add_edge("A", "B")
    assert g.edge_count() == 1


def test_duplicate_reversed_edge_undirected_rejected(make_graph):
    g = make_graph([("A", "B")])
    with pytest.raises(EdgeAlreadyExistsError):
        g.add_edge("B", "A")


def test_reverse_edge_allowed_in_directed(make_graph):
    g = make_graph([("A", "B"), ("B", "A")], directed=True)
    assert g.edge_count() == 2


@pytest.mark.parametrize("directed", [True, False])
def test_self_loop(make_graph, directed):
    g = make_graph([("A", "A"), ("A", "B")], directed=directed)
    assert g.has_edge("A", "A")
    assert g.neighbours("A").count("A") == 1
    assert g.edge_count() == 2
    assert len(g.all_edges()) == 2
    with pytest.raises(EdgeAlreadyExistsError):
        g.add_edge("A", "A")


def test_remove_edge_directed(make_graph):
    g = make_graph([("A", "B"), ("B", "A")], directed=True)
    g.remove_edge("A", "B")
    assert not g.has_edge("A", "B") and g.has_edge("B", "A") and g.edge_count() == 1


def test_remove_edge_undirected_removes_both(make_graph):
    g = make_graph([("A", "B")])
    g.remove_edge("B", "A")
    assert not g.has_edge("A", "B") and not g.has_edge("B", "A")
    assert g.edge_count() == 0 and g.vertex_count() == 2


def test_remove_self_loop(make_graph):
    g = make_graph([("A", "A")])
    g.remove_edge("A", "A")
    assert g.edge_count() == 0


def test_remove_missing_edge(make_graph):
    g = make_graph([("A", "B")], directed=True, vertices=["C"])
    with pytest.raises(EdgeNotFoundError):
        g.remove_edge("B", "A")
    with pytest.raises(EdgeNotFoundError):
        g.remove_edge("A", "C")
    with pytest.raises(VertexNotFoundError):
        g.remove_edge("A", "Z")
    with pytest.raises(KeyError):  # design allows KeyError or the custom error
        g.remove_edge("A", "C")


def test_remove_vertex_directed_removes_in_and_out_edges(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A"), ("C", "C")], directed=True)
    g.remove_vertex("C")
    assert g.vertices == ["A", "B"]
    assert g.edge_count() == 1 and g.has_edge("A", "B")
    assert g.neighbours("B") == []


def test_remove_vertex_undirected(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("A", "C")])
    g.remove_vertex("B")
    assert g.vertices == ["A", "C"] and g.edge_count() == 1
    assert g.neighbours("A") == ["C"] and g.neighbours("C") == ["A"]


def test_remove_vertex_then_readd(make_graph):
    g = make_graph([("A", "B"), ("B", "C")])
    g.remove_vertex("A")
    g.add_vertex("A")
    assert g.vertices == ["B", "C", "A"]
    assert g.neighbours("A") == []
    g.add_edge("A", "B")
    assert g.has_edge("B", "A")


def test_remove_missing_vertex(make_graph):
    g = make_graph([("A", "B")])
    with pytest.raises(VertexNotFoundError):
        g.remove_vertex("Z")
    with pytest.raises(KeyError):
        g.remove_vertex("Z")


def test_unknown_vertex_queries(make_graph):
    g = make_graph([("A", "B")])
    for call in (lambda: g.neighbours("Z"), lambda: g.has_edge("A", "Z"),
                 lambda: g.has_edge("Z", "A")):
        with pytest.raises(VertexNotFoundError):
            call()


def test_neighbour_order_is_vertex_creation_order(make_graph):
    g = make_graph([("A", "C"), ("A", "B")], vertices=["B"], first=True)  # B created before A and C
    assert g.vertices == ["B", "A", "C"]
    assert g.neighbours("A") == ["B", "C"]


def test_all_edges_returns_copies(make_graph):
    g = make_graph([("A", "B", 1.0)], weighted=True)
    g.all_edges()[0].weight = 99
    assert g.edge_weight("A", "B") == 1.0


def test_empty_graph(GraphClass):
    g = GraphClass()
    assert g.vertices == [] and g.vertex_count() == 0 and g.edge_count() == 0
    assert g.all_edges() == []


def test_handshake(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "D"), ("A", "D"), ("A", "C")])
    assert sum(len(g.neighbours(v)) for v in g.vertices) == 2 * g.edge_count()
    assert g.edge_count() == len(g.all_edges())


def test_list_and_matrix_agree_on_weights_and_edges():
    from worklet1.graph import AdjacencyMatrixGraph

    ops = [("A", "B", 2.0), ("B", "C", -1.0), ("C", "A", 0.0)]
    graphs = []
    for cls in (AdjacencyListGraph, AdjacencyMatrixGraph):
        g = cls(directed=True, weighted=True)
        for op in ops:
            g.add_edge(*op)
        graphs.append(g)
    a, b = graphs
    assert a.all_edges() == b.all_edges()
    assert a.vertices == b.vertices
