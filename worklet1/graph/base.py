"""Graph model layer: ``Vertex``, ``Edge`` and the ``Graph`` abstract base class.

The ``Graph`` ABC is the only thing the algorithm layer is allowed to know about.
It holds no algorithm logic.  Weight / vertex-id validation lives here so that
both representations behave identically (design decisions D-06, D-07, D-08).

Contract summary (shared by every representation)
-------------------------------------------------
* Vertex identifiers are ``int`` (not ``bool``) or ``str``.
* ``vertices`` and ``neighbours`` use *vertex creation order* (D-23), so results
  are identical for every representation.
* An undirected edge is reported **once** by ``all_edges()`` and counted once by
  ``edge_count()`` (lower-creation-order endpoint first).  A self-loop is stored
  and counted once.
* Unweighted graphs always report ``Edge.weight is None``.
* Parallel edges are rejected; self-loops are allowed; negative weights are allowed.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Vertex:
    """Data holder for a vertex: an identifier and optional payload.

    The Graph API exchanges raw identifiers; this class exists for the model
    layer and documentation (decision D-22).
    """

    id: Any
    data: Any = None


@dataclass
class Edge:
    """A directed edge ``src -> dst`` with an optional weight (``None`` if unweighted)."""

    src: Any
    dst: Any
    weight: float | None = None


class Graph(ABC):
    """Abstract interface that every graph representation must implement."""

    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        """Create an empty graph.

        Args:
            directed: ``True`` for a directed graph.
            weighted: ``True`` if every edge carries a numeric weight.
        """
        # Stored privately; the public read-only properties below expose them.
        self._directed = bool(directed)
        self._weighted = bool(weighted)

    # ------------------------------------------------------------------ flags
    @property
    def is_directed(self) -> bool:
        """``True`` if edges have a direction."""
        return self._directed

    @property
    def is_weighted(self) -> bool:
        """``True`` if edges carry weights."""
        return self._weighted

    # ------------------------------------------------------- shared validation
    @staticmethod
    def validate_vertex_id(vertex: Any) -> None:
        """Raise ``TypeError`` unless *vertex* is an ``int`` (not ``bool``) or ``str``."""
        # bool is a subclass of int in Python (True == 1), so it must be excluded explicitly,
        # otherwise add_vertex(True) and add_vertex(1) would silently be the same vertex.
        if isinstance(vertex, bool) or not isinstance(vertex, (int, str)):
            raise TypeError(
                f"vertex identifiers must be int or str, got {type(vertex).__name__}: {vertex!r}"
            )

    def _normalise_weight(self, weight: Any) -> float | None:
        """Validate *weight* against the graph type and return the value to store.

        Weighted graphs require a finite number (negative and zero allowed) and
        store it as ``float``; unweighted graphs reject any weight and store ``None``.
        """
        # Rules: weighted graph => a finite number is REQUIRED; unweighted graph => NO weight.
        # Strictness prevents silent data loss (e.g. a missing weight turning into "no edge").
        if not self._weighted:
            if weight is not None:
                raise ValueError("cannot assign a weight to an edge of an unweighted graph")
            return None
        if weight is None:
            raise ValueError("a weighted graph requires a weight for every edge")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise TypeError(f"edge weight must be int or float, got {type(weight).__name__}")
        try:
            value = float(weight)
        except OverflowError:
            raise ValueError("edge weight is too large to represent as a float") from None
        if not math.isfinite(value):  # NaN / infinity would break comparisons in later algorithms
            raise ValueError("edge weight must be finite (not NaN or infinity)")
        return value

    # --------------------------------------------------------------- interface
    @property
    @abstractmethod
    def vertices(self) -> list:
        """A new list of all vertex identifiers in creation order."""

    @abstractmethod
    def add_vertex(self, v: Any) -> None:
        """Add vertex *v*; adding an existing vertex is a no-op."""

    @abstractmethod
    def remove_vertex(self, v: Any) -> None:
        """Remove *v* and every incident edge; ``VertexNotFoundError`` if absent."""

    @abstractmethod
    def add_edge(self, u: Any, v: Any, weight: float | None = None) -> None:
        """Add edge ``u -> v`` (both directions if undirected), creating missing vertices.

        Raises ``EdgeAlreadyExistsError`` for a duplicate; the graph is unchanged on any error.
        """

    @abstractmethod
    def remove_edge(self, u: Any, v: Any) -> None:
        """Remove edge ``u -> v``; ``VertexNotFoundError`` / ``EdgeNotFoundError`` if absent."""

    @abstractmethod
    def has_edge(self, u: Any, v: Any) -> bool:
        """Whether edge ``u -> v`` exists; ``VertexNotFoundError`` for unknown vertices."""

    @abstractmethod
    def neighbours(self, v: Any) -> list:
        """Identifiers of the vertices reachable from *v* by one edge, in creation order."""

    @abstractmethod
    def all_edges(self) -> list:
        """List of ``Edge`` copies; each undirected edge appears once."""

    @abstractmethod
    def vertex_count(self) -> int:
        """Number of vertices."""

    @abstractmethod
    def edge_count(self) -> int:
        """Number of edges (an undirected edge counts once)."""

    @abstractmethod
    def edge_weight(self, u: Any, v: Any) -> float | None:
        """PROPOSED (pending Worklet 2 agreement): weight of ``u -> v``.

        Returns ``None`` if the edge does not exist or the graph is unweighted.
        """
