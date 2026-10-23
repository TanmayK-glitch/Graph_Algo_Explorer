"""Shared fixtures: every graph test can run against both representations."""

import pytest

from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph

GRAPH_CLASSES = [AdjacencyListGraph, AdjacencyMatrixGraph]


@pytest.fixture(params=GRAPH_CLASSES, ids=lambda c: c.__name__)
def GraphClass(request):
    """Each test using this fixture runs once per representation."""
    return request.param


@pytest.fixture
def make_graph(GraphClass):
    """Factory ``make(edges, directed, weighted, vertices, first)`` building a graph of the current class."""

    def make(edges=(), directed=False, weighted=False, vertices=(), first=False):
        g = GraphClass(directed=directed, weighted=weighted)
        if first:  # extra vertices created before the edges
            for v in vertices:
                g.add_vertex(v)
        for edge in edges:
            if weighted:
                g.add_edge(*edge)
            else:
                g.add_edge(edge[0], edge[1])
        if not first:  # default: extra (isolated) vertices are created after the edges
            for v in vertices:
                g.add_vertex(v)
        return g

    return make
