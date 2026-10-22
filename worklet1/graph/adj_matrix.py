"""Adjacency-matrix representation: a 2-D list indexed by vertex position."""

from __future__ import annotations

from typing import Any

from .base import Edge, Graph
from .exceptions import EdgeAlreadyExistsError, EdgeNotFoundError, VertexNotFoundError


class AdjacencyMatrixGraph(Graph):
    """2-D list graph.  O(V^2) space, O(1) edge lookup, O(V) neighbour scan.

    A cell holds ``None`` for "no edge".  Weighted graphs store the float weight
    (zero and negative weights are real edges because the test is ``is not None``);
    unweighted graphs store ``1`` as a presence marker, which is translated back to
    ``Edge.weight = None`` at the interface (decision D-19).
    """

    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        """Create an empty graph (see :class:`Graph`)."""
        super().__init__(directed, weighted)
        self._vertices: list[Any] = []  # row/column number -> vertex (creation order)
        self._index: dict[Any, int] = {}  # vertex -> row/column number
        self._matrix: list[list[Any]] = []  # _matrix[i][j] is the edge i -> j, or None

    def _idx(self, v: Any) -> int:
        if v not in self._index:
            raise VertexNotFoundError(v)
        return self._index[v]

    @property
    def vertices(self) -> list:
        """All vertices in creation order."""
        return list(self._vertices)

    def add_vertex(self, v: Any) -> None:
        """Add vertex *v* (no-op if present).  O(V) for matrix expansion."""
        self.validate_vertex_id(v)
        if v in self._index:
            return
        self._index[v] = len(self._vertices)
        self._vertices.append(v)
        for row in self._matrix:
            row.append(None)  # new column in every existing row
        # new row: no edges yet. Growing both dimensions is why add_vertex is O(V).
        self._matrix.append([None] * len(self._vertices))

    def remove_vertex(self, v: Any) -> None:
        """Remove *v*: delete its row and column and re-index the rest.  O(V^2)."""
        i = self._idx(v)
        del self._matrix[i]  # remove v's row ...
        for row in self._matrix:
            del row[i]  # ... and v's column
        # Everything after position i shifts left by one, so the vertex->index map is rebuilt below.
        del self._vertices[i]
        del self._index[v]
        for pos in range(i, len(self._vertices)):
            self._index[self._vertices[pos]] = pos

    def add_edge(self, u: Any, v: Any, weight: float | None = None) -> None:
        """Add edge ``u -> v``.  O(1) once both vertices exist."""
        self.validate_vertex_id(u)
        self.validate_vertex_id(v)
        value = self._normalise_weight(weight)
        if u in self._index and v in self._index and self.has_edge(u, v):
            raise EdgeAlreadyExistsError(u, v)
        self.add_vertex(u)
        self.add_vertex(v)
        # Cell content: the weight (weighted) or 1 as a "present" marker (unweighted).
        # None is reserved for "no edge", so a weight of 0.0 is still a real edge.
        cell = value if self._weighted else 1
        i, j = self._index[u], self._index[v]
        self._matrix[i][j] = cell
        if not self._directed:
            self._matrix[j][i] = cell  # undirected => matrix is symmetric

    def remove_edge(self, u: Any, v: Any) -> None:
        """Remove edge ``u -> v`` (both cells if undirected)."""
        i, j = self._idx(u), self._idx(v)
        if self._matrix[i][j] is None:
            raise EdgeNotFoundError(u, v)
        self._matrix[i][j] = None
        if not self._directed:
            self._matrix[j][i] = None

    def has_edge(self, u: Any, v: Any) -> bool:
        """Whether ``u -> v`` exists.  O(1)."""
        return self._matrix[self._idx(u)][self._idx(v)] is not None

    def neighbours(self, v: Any) -> list:
        """Adjacent vertex identifiers by scanning one row.  O(V)."""
        row = self._matrix[self._idx(v)]  # scanning a whole row is why this is O(V), not O(degree)
        out = []
        for j in range(len(row)):
            if row[j] is not None:
                out.append(self._vertices[j])
        return out

    def all_edges(self) -> list:
        """Edge copies; each undirected edge once (upper triangle incl. diagonal)."""
        out: list[Edge] = []
        n = len(self._vertices)
        for i in range(n):
            # Undirected: the matrix is symmetric, so read only the upper triangle (j >= i)
            # to report each edge once (diagonal = self-loops).
            start = 0 if self._directed else i
            for j in range(start, n):
                cell = self._matrix[i][j]
                if cell is not None:
                    out.append(
                        Edge(self._vertices[i], self._vertices[j], cell if self._weighted else None)
                    )
        return out

    def vertex_count(self) -> int:
        """Number of vertices."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Number of edges (undirected edge and self-loop each count once)."""
        n = len(self._vertices)
        count = 0
        for i in range(n):
            start = 0 if self._directed else i
            for j in range(start, n):
                if self._matrix[i][j] is not None:
                    count += 1
        return count

    def edge_weight(self, u: Any, v: Any) -> float | None:
        """PROPOSED: weight of ``u -> v`` or ``None``.  O(1)."""
        cell = self._matrix[self._idx(u)][self._idx(v)]
        if cell is None or not self._weighted:
            return None  # no edge, or an unweighted graph (cell holds the marker 1, not a weight)
        return cell
