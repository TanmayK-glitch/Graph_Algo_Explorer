"""Exceptions raised by the graph model (design decision D-05)."""

from __future__ import annotations

from typing import Any


class GraphError(Exception):
    """Base class of all graph-model errors."""


class VertexNotFoundError(GraphError, KeyError):
    """Raised when an operation names a vertex that is not in the graph."""

    def __init__(self, vertex: Any) -> None:
        """Remember the missing *vertex*."""
        self.vertex = vertex
        super().__init__(f"vertex {vertex!r} not found in graph")

    def __str__(self) -> str:  # KeyError would otherwise show repr() of the message
        return f"vertex {self.vertex!r} not found in graph"


class EdgeNotFoundError(GraphError, KeyError):
    """Raised when removing or querying an edge that does not exist."""

    def __init__(self, src: Any, dst: Any) -> None:
        """Remember the edge endpoints."""
        self.src = src
        self.dst = dst
        super().__init__(f"edge {src!r} -> {dst!r} not found in graph")

    def __str__(self) -> str:
        return f"edge {self.src!r} -> {self.dst!r} not found in graph"


class EdgeAlreadyExistsError(GraphError, ValueError):
    """Raised when adding an edge that already exists (parallel edges are rejected)."""

    def __init__(self, src: Any, dst: Any) -> None:
        """Remember the edge endpoints."""
        self.src = src
        self.dst = dst
        super().__init__(f"edge {src!r} -> {dst!r} already exists")
