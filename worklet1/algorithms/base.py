"""Shared algorithm contract: ``Algorithm`` (strategy interface) and ``AlgorithmResult``."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..graph.base import Graph
from ..graph.exceptions import VertexNotFoundError


@dataclass
class AlgorithmResult:
    """Structured output of every algorithm.

    Attributes:
        algorithm: documented algorithm name, e.g. ``'BFS'``.
        primary_output: the main answer (visit order, components, bool, ...).
        metadata: extra information (start vertex, counts, colouring, ...).
        success: ``False`` only when the algorithm ran but no answer exists
            (topological sort of a cyclic graph).
        error_message: explanation when ``success`` is ``False``.
    """

    algorithm: str
    primary_output: Any
    metadata: dict = field(default_factory=dict)
    success: bool = True
    error_message: str = ""


class Algorithm(ABC):
    """Strategy interface: every algorithm is a replaceable object with ``execute``."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Documented algorithm name."""

    @abstractmethod
    def execute(self, graph: Graph, **kwargs: Any) -> AlgorithmResult:
        """Run the algorithm on *graph* using only the public ``Graph`` interface."""


def require_vertex(graph: Graph, v: Any) -> None:
    """Raise ``VertexNotFoundError`` unless *v* is a vertex of *graph*."""
    if v not in graph.vertices:  # uses the public `vertices` list only
        raise VertexNotFoundError(v)


def canonical_components(graph: Graph, components: list) -> list:
    """Order components canonically (decision D-11).

    Members follow ``graph.vertices`` order; components are ordered by the position
    of their earliest member.  This makes results independent of traversal details.
    """
    rank = {v: i for i, v in enumerate(graph.vertices)}  # vertex -> creation position
    ordered = [sorted(c, key=rank.__getitem__) for c in components]  # members in vertex order
    ordered.sort(key=lambda c: rank[c[0]])  # components by their earliest member
    return ordered
