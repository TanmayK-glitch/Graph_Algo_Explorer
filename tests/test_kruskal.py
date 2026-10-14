
"""Tests for Kruskal's Minimum Spanning Tree algorithm."""

import pytest

from src.algorithms.kruskal import kruskal_mst


def test_basic_mst():
    edges = [
        (0, 1, 1),
        (0, 2, 4),
        (1, 3, 3),
        (2, 3, 2),
        (0, 3, 5)
    ]

    mst, total = kruskal_mst(4, edges)

    assert total == 6
    assert len(mst) == 3
    assert set(mst) == {
        (0, 1, 1),
        (2, 3, 2),
        (1, 3, 3)
    }


def test_cycle_prevention():
    edges = [
        (0, 1, 1),
        (1, 2, 2),
        (0, 2, 3)
    ]

    mst, total = kruskal_mst(3, edges)

    assert total == 3
    assert len(mst) == 2
    assert (0, 2, 3) not in mst


def test_negative_weights():
    edges = [
        (0, 1, -5),
        (1, 2, 2),
        (0, 2, 4)
    ]

    mst, total = kruskal_mst(3, edges)

    assert total == -3
    assert len(mst) == 2


def test_disconnected_graph():
    edges = [
        (0, 1, 2),
        (2, 3, 4)
    ]

    with pytest.raises(ValueError):
        kruskal_mst(4, edges)


def test_single_vertex():
    mst, total = kruskal_mst(1, [])

    assert mst == []
    assert total == 0


def test_empty_graph():
    mst, total = kruskal_mst(0, [])

    assert mst == []
    assert total == 0


def test_invalid_vertex():
    edges = [(0, 5, 10)]

    with pytest.raises(ValueError):
        kruskal_mst(3, edges)


def test_negative_vertex_count():
    with pytest.raises(ValueError):
        kruskal_mst(-1, [])
