import math

from src.algorithms.bellman_ford import (
    bellman_ford,
    reconstruct_path,
)


def test_negative_edge():
    graph = {
        "A": [("B", 4), ("C", 5)],
        "B": [("C", -2), ("D", 4)],
        "C": [("D", 3)],
        "D": [],
    }

    result = bellman_ford(graph, "A")

    assert result.distances["A"] == 0
    assert result.distances["B"] == 4
    assert result.distances["C"] == 2
    assert result.distances["D"] == 5

    assert reconstruct_path(result, "D") == ["A", "B", "C", "D"]


def test_unreachable_vertex():
    graph = {
        "A": [("B", 2)],
        "B": [],
        "C": [],
    }

    result = bellman_ford(graph, "A")

    assert result.distances["B"] == 2
    assert math.isinf(result.distances["C"])
    assert reconstruct_path(result, "C") is None


def test_negative_cycle():
    graph = {
        "A": [("B", 1)],
        "B": [("C", -2)],
        "C": [("B", -2)],
    }

    try:
        bellman_ford(graph, "A")
        raise AssertionError("Expected a negative-cycle error")
    except ValueError as error:
        assert "negative-weight cycle" in str(error)


if __name__ == "__main__":
    test_negative_edge()
    test_unreachable_vertex()
    test_negative_cycle()

    print("All Bellman-Ford tests passed!")
