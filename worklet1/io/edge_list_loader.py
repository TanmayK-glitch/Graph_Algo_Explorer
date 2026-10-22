"""Edge-list file loader (format v1, PROPOSED - pending Worklet 2/3 sign-off, X-02).

Format::

    # comment (whole line or trailing after whitespace)
    DIRECTED | UNDIRECTED        <- first non-comment line
    WEIGHTED | UNWEIGHTED        <- second non-comment line
    u v [weight]                 <- one edge per line (weight required iff WEIGHTED)
    v                            <- an isolated vertex

Vertex identifiers are whitespace-free strings.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from ..graph.adj_list import AdjacencyListGraph
from ..graph.base import Graph
from ..graph.exceptions import EdgeAlreadyExistsError


class EdgeListFormatError(ValueError):
    """A malformed edge-list file; the message names the offending line number."""

    def __init__(self, line_number: int, message: str) -> None:
        """Store *line_number* (1-based) and prefix the message with it."""
        self.line_number = line_number
        super().__init__(f"line {line_number}: {message}")


def _tokens(line: str) -> list[str]:
    """Split a line into tokens, dropping everything from the first ``#`` token on."""
    out: list[str] = []
    for tok in line.split():
        if tok.startswith("#"):  # a "#" token starts a comment: ignore the rest of the line
            break
        out.append(tok)
    return out


class EdgeListLoader:
    """Builds a :class:`Graph` from an edge-list text file."""

    @staticmethod
    def load(filepath: str | os.PathLike[str],
             graph_class: Callable[..., Graph] = AdjacencyListGraph) -> Graph:
        """Load *filepath* and return a graph (adjacency list unless *graph_class* is given).

        Raises:
            FileNotFoundError: the file does not exist.
            EdgeListFormatError: (a ``ValueError``) the content is malformed.
        """
        with open(filepath, encoding="utf-8-sig") as handle:
            lines = handle.read().splitlines()

        # Small state machine: header 1 (direction) -> header 2 (weighting) -> edge records.
        # `directed`/`weighted` stay None until their header line has been read.
        directed: Any = None
        weighted: Any = None
        graph: Graph | None = None
        last_line = 0
        for number, raw in enumerate(lines, start=1):
            last_line = number
            toks = _tokens(raw)
            if not toks:
                continue  # blank line or comment-only line
            if directed is None:
                if toks not in (["DIRECTED"], ["UNDIRECTED"]):
                    raise EdgeListFormatError(
                        number, "expected header 'DIRECTED' or 'UNDIRECTED', got " + repr(raw.strip()))
                directed = toks[0] == "DIRECTED"
                continue  # header consumed; next non-blank line must be the weighting header
            if weighted is None:
                if toks not in (["WEIGHTED"], ["UNWEIGHTED"]):
                    raise EdgeListFormatError(
                        number, "expected header 'WEIGHTED' or 'UNWEIGHTED', got " + repr(raw.strip()))
                weighted = toks[0] == "WEIGHTED"
                # Both headers known => the empty graph can be created (list or matrix).
                graph = graph_class(directed=directed, weighted=weighted)
                continue
            assert graph is not None
            EdgeListLoader._apply(graph, toks, number, weighted)

        if graph is None:
            raise EdgeListFormatError(
                max(last_line, 1), "missing DIRECTED/UNDIRECTED and WEIGHTED/UNWEIGHTED header lines")
        return graph

    @staticmethod
    def _apply(graph: Graph, toks: list[str], number: int, weighted: bool) -> None:
        """Apply one edge / isolated-vertex record to *graph*."""
        if len(toks) == 1:  # single token => an isolated vertex declaration
            graph.add_vertex(toks[0])
            return
        expected = 3 if weighted else 2
        if len(toks) < expected:
            raise EdgeListFormatError(number, "weight missing for edge in a WEIGHTED file")
        if len(toks) > expected:
            raise EdgeListFormatError(
                number, f"too many fields ({len(toks)}) for a "
                f"{'WEIGHTED' if weighted else 'UNWEIGHTED'} edge line")
        weight = None
        if weighted:
            try:
                weight = float(toks[2])
            except ValueError:
                raise EdgeListFormatError(number, f"invalid weight {toks[2]!r}") from None
        try:
            graph.add_edge(toks[0], toks[1], weight)
        except EdgeAlreadyExistsError:  # translate graph errors into file errors WITH a line number
            raise EdgeListFormatError(number, f"duplicate edge {toks[0]} {toks[1]}") from None
        except ValueError as exc:  # NaN / infinite weight
            raise EdgeListFormatError(number, str(exc)) from None
