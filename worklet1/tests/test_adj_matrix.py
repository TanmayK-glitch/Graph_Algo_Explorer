"""Representation-specific tests for AdjacencyMatrixGraph."""

from worklet1.graph import AdjacencyMatrixGraph


def test_matrix_shape_grows_and_shrinks():
    g = AdjacencyMatrixGraph()
    for v in "ABC":
        g.add_vertex(v)
    assert len(g._matrix) == 3 and all(len(r) == 3 for r in g._matrix)
    g.remove_vertex("B")
    assert len(g._matrix) == 2 and all(len(r) == 2 for r in g._matrix)
    assert g._index == {"A": 0, "C": 1}


def test_unweighted_cell_marker_is_one_but_weight_is_none():
    g = AdjacencyMatrixGraph()
    g.add_edge("A", "B")
    assert g._matrix[0][1] == 1 and g._matrix[1][0] == 1
    assert g.edge_weight("A", "B") is None and g.all_edges()[0].weight is None


def test_zero_weight_cell_is_an_edge_not_absence():
    g = AdjacencyMatrixGraph(weighted=True)
    g.add_edge("A", "B", 0)
    assert g._matrix[0][1] == 0.0 and g.has_edge("A", "B")


def test_directed_sets_single_cell():
    g = AdjacencyMatrixGraph(directed=True)
    g.add_edge("A", "B")
    assert g._matrix[0][1] == 1 and g._matrix[1][0] is None


def test_reindex_after_middle_removal_keeps_edges():
    g = AdjacencyMatrixGraph(directed=True)
    g.add_edge("A", "C")
    g.add_edge("C", "D")
    g.add_edge("B", "D")
    g.remove_vertex("B")
    assert g.has_edge("A", "C") and g.has_edge("C", "D")
    assert g.vertices == ["A", "C", "D"] and g.edge_count() == 2
