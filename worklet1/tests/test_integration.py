"""End-to-end tests: load a sample file, run algorithms, inspect results."""

from pathlib import Path

import pytest

from worklet1.algorithms import (
    BFSAlgorithm,
    BipartiteTestAlgorithm,
    ConnectedComponentsAlgorithm,
    CycleDetectionAlgorithm,
    DFSAlgorithm,
    SCCAlgorithm,
    TopologicalSortAlgorithm,
)
from worklet1.io import EdgeListLoader

SAMPLES = Path(__file__).resolve().parent.parent / "sample_graphs"


@pytest.fixture
def load(GraphClass):
    return lambda name: EdgeListLoader.load(SAMPLES / name, graph_class=GraphClass)


def test_diamond_dag_end_to_end(load):
    g = load("diamond_dag.edgelist")
    assert BFSAlgorithm().execute(g, start="A").primary_output == ["A", "B", "C", "D"]
    assert DFSAlgorithm().execute(g, start="A").primary_output == ["A", "B", "D", "C"]
    topo = TopologicalSortAlgorithm().execute(g)
    assert topo.primary_output[0] == "A" and topo.primary_output[-1] == "D"
    assert CycleDetectionAlgorithm().execute(g).primary_output is False


def test_undirected_components_end_to_end(load):
    g = load("undirected_components.edgelist")
    assert ConnectedComponentsAlgorithm().execute(g).primary_output == [["A", "B"], ["C", "D"], ["E"]]
    assert BipartiteTestAlgorithm().execute(g).primary_output is True
    assert BFSAlgorithm().execute(g, mode="all").primary_output == ["A", "B", "C", "D", "E"]


def test_triangle_and_even_cycle(load):
    assert BipartiteTestAlgorithm().execute(load("triangle.edgelist")).primary_output is False
    assert BipartiteTestAlgorithm().execute(load("even_cycle.edgelist")).primary_output is True
    assert CycleDetectionAlgorithm().execute(load("triangle.edgelist")).primary_output is True


def test_scc_and_directed_cycle_files(load):
    assert SCCAlgorithm().execute(load("scc_example.edgelist")).primary_output == [["A", "B"], ["C"], ["D"]]
    g = load("directed_cycle.edgelist")
    assert CycleDetectionAlgorithm().execute(g).primary_output is True
    assert TopologicalSortAlgorithm().execute(g).success is False
    assert SCCAlgorithm().execute(g).primary_output == [["A", "B", "C"], ["D"]]


def test_self_loop_file(load):
    g = load("self_loop.edgelist")
    assert CycleDetectionAlgorithm().execute(g).primary_output is True
    assert BipartiteTestAlgorithm().execute(g).primary_output is False


def test_negative_weights_do_not_affect_structure_algorithms(load):
    g = load("negative_weights.edgelist")
    assert g.edge_weight("A", "B") == -2.5
    assert TopologicalSortAlgorithm().execute(g).primary_output == ["A", "B", "C"]


def test_edit_then_analyse(make_graph):
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A")], directed=True)
    assert TopologicalSortAlgorithm().execute(g).success is False
    g.remove_edge("C", "A")
    assert TopologicalSortAlgorithm().execute(g).primary_output == ["A", "B", "C"]
    g.remove_vertex("B")
    assert SCCAlgorithm().execute(g).primary_output == [["A"], ["C"]]
