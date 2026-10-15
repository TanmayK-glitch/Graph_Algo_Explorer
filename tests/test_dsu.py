
"""Tests for the Disjoint Set Union implementation."""

import pytest

from src.algorithms.dsu import DisjointSetUnion


def test_initialization():
    dsu = DisjointSetUnion(5)

    assert dsu.parent == [0, 1, 2, 3, 4]
    assert dsu.rank == [0, 0, 0, 0, 0]


def test_union():
    dsu = DisjointSetUnion(5)

    assert dsu.union(0, 1) is True
    assert dsu.union(1, 2) is True
    assert dsu.connected(0, 2) is True


def test_already_connected():
    dsu = DisjointSetUnion(4)

    dsu.union(0, 1)

    assert dsu.union(0, 1) is False


def test_different_components():
    dsu = DisjointSetUnion(5)

    dsu.union(0, 1)
    dsu.union(3, 4)

    assert dsu.connected(0, 1) is True
    assert dsu.connected(0, 3) is False


def test_path_compression():
    dsu = DisjointSetUnion(4)

    dsu.parent = [0, 0, 1, 2]

    assert dsu.find(3) == 0
    assert dsu.parent[3] == 0
    assert dsu.parent[2] == 0


def test_union_by_rank():
    dsu = DisjointSetUnion(4)

    dsu.union(0, 1)
    dsu.union(2, 3)
    dsu.union(0, 2)

    assert dsu.find(0) == dsu.find(3)
    assert dsu.rank[dsu.find(0)] == 2


def test_negative_size():
    with pytest.raises(ValueError):
        DisjointSetUnion(-1)
