"""Tests for :func:`src.algorithms.bellman_ford.bellman_ford`."""

from __future__ import annotations

import math

import pytest

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

    with pytest.raises(ValueError, match="negative-weight cycle"):
        bellman_ford(graph, "A")


def test_unreachable_negative_cycle():
    """An unreachable negative cycle must not trigger a negative cycle error."""
    graph = {
        "A": [("B", 2)],
        "B": [],
        "X": [("Y", -2)],
        "Y": [("X", -2)],
    }

    result = bellman_ford(graph, "A")
    assert result.distances["A"] == 0
    assert result.distances["B"] == 2
    assert math.isinf(result.distances["X"])
    assert math.isinf(result.distances["Y"])


def test_single_vertex():
    graph = {"A": []}
    result = bellman_ford(graph, "A")
    assert result.distances["A"] == 0.0
    assert result.predecessors["A"] is None
    assert reconstruct_path(result, "A") == ["A"]


def test_neighbor_only_vertex():
    """Target appears only in neighbor list, not as a graph dict key."""
    graph = {"A": [("B", 3)]}
    result = bellman_ford(graph, "A")
    assert result.distances["B"] == 3
    assert reconstruct_path(result, "B") == ["A", "B"]


def test_reconstruct_path_unknown_target():
    graph = {"A": []}
    result = bellman_ford(graph, "A")
    assert reconstruct_path(result, "Z") is None


def test_result_is_frozen_dataclass():
    graph = {"A": []}
    result = bellman_ford(graph, "A")
    with pytest.raises(AttributeError):
        result.source = "B"  # type: ignore[misc]


def test_validation_graph_not_dict():
    with pytest.raises(ValueError, match="Graph must be a dict"):
        bellman_ford([], "A")  # type: ignore[arg-type]


def test_validation_adjacency_not_list():
    with pytest.raises(ValueError, match="must be a list"):
        bellman_ford({"A": {("B", 1)}}, "A")  # type: ignore[dict-item]


def test_validation_edge_not_tuple():
    with pytest.raises(ValueError, match="must be a \\(neighbor, weight\\) pair"):
        bellman_ford({"A": [("B", 1, 2)]}, "A")  # type: ignore[list-item]


def test_validation_weight_not_numeric():
    with pytest.raises(ValueError, match="must be numeric"):
        bellman_ford({"A": [("B", "heavy")]}, "A")  # type: ignore[list-item]


def test_validation_weight_nan_or_inf():
    with pytest.raises(ValueError, match="must be finite"):
        bellman_ford({"A": [("B", float("nan"))]}, "A")
    with pytest.raises(ValueError, match="must be finite"):
        bellman_ford({"A": [("B", float("inf"))]}, "A")


def test_validation_missing_source():
    with pytest.raises(ValueError, match="not present in the graph"):
        bellman_ford({"A": []}, "Z")
