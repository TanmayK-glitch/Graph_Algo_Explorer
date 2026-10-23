"""NFR-12: operation-count evidence for O(V+E) list traversal and O(V^2) matrix traversal.

Counts executed lines inside the representation modules (deterministic, unlike wall-clock time)
while running a full BFS on a sparse path graph (E = V - 1).
"""

import sys

from worklet1.algorithms import bfs_all
from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph


def traced_lines(cls, n):
    g = cls()
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    count = 0
    target = ("adj_list.py", "adj_matrix.py")

    def tracer(frame, event, arg):
        nonlocal count
        if frame.f_code.co_filename.endswith(target):
            if event == "line":
                count += 1
            return tracer
        return None

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        bfs_all(g)
    finally:
        sys.settrace(previous)
    return count


def test_list_traversal_is_linear_in_v_plus_e():
    c1, c2 = traced_lines(AdjacencyListGraph, 100), traced_lines(AdjacencyListGraph, 200)
    assert 1.7 <= c2 / c1 <= 2.3, (c1, c2)


def test_matrix_traversal_is_quadratic_in_v():
    c1, c2 = traced_lines(AdjacencyMatrixGraph, 100), traced_lines(AdjacencyMatrixGraph, 200)
    assert 3.4 <= c2 / c1 <= 4.6, (c1, c2)


def test_matrix_costs_more_than_list_on_sparse_graph():
    assert traced_lines(AdjacencyMatrixGraph, 150) > 10 * traced_lines(AdjacencyListGraph, 150)
