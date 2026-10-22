"""Cycle detection tests (FR-15)."""


from worklet1.algorithms import CycleDetectionAlgorithm

CD = CycleDetectionAlgorithm()


def has_cycle(g):
    r = CD.execute(g)
    assert r.algorithm == "CycleDetection" and r.success
    return r.primary_output


def test_directed_cross_edges_not_a_cycle(make_graph):
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], directed=True)
    assert has_cycle(g) is False


def test_directed_back_edge(make_graph):
    assert has_cycle(make_graph([("A", "B"), ("B", "C"), ("C", "A")], directed=True)) is True


def test_directed_two_cycle(make_graph):
    assert has_cycle(make_graph([("A", "B"), ("B", "A")], directed=True)) is True


def test_directed_cycle_in_later_component(make_graph):
    g = make_graph([("A", "B"), ("C", "D"), ("D", "C")], directed=True)
    assert has_cycle(g) is True


def test_directed_self_loop(make_graph):
    assert has_cycle(make_graph([("A", "A")], directed=True)) is True


def test_directed_dag_forward_edge(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("A", "C")], directed=True)
    assert has_cycle(g) is False


def test_undirected_tree_no_cycle(make_graph):
    assert has_cycle(make_graph([("A", "B"), ("B", "C"), ("B", "D")])) is False


def test_undirected_single_edge_not_a_cycle(make_graph):
    assert has_cycle(make_graph([("A", "B")])) is False


def test_undirected_triangle(make_graph):
    assert has_cycle(make_graph([("A", "B"), ("B", "C"), ("A", "C")])) is True


def test_undirected_cycle_in_second_component(make_graph):
    g = make_graph([("A", "B"), ("C", "D"), ("D", "E"), ("E", "C")])
    assert has_cycle(g) is True


def test_undirected_self_loop(make_graph):
    assert has_cycle(make_graph([("A", "A")])) is True


def test_empty_and_isolated(make_graph, GraphClass):
    assert has_cycle(GraphClass()) is False
    assert has_cycle(GraphClass(directed=True)) is False
    assert has_cycle(make_graph(vertices=["A", "B"])) is False


def test_weighted_negative_edges_irrelevant(make_graph):
    g = make_graph([("A", "B", -1.0), ("B", "A", -1.0)], directed=True, weighted=True)
    assert has_cycle(g) is True
