"""Parse the edge-list text entered in the visualization UI."""

from __future__ import annotations

from dataclasses import dataclass

from worklet1.graph import AdjacencyListGraph


class InputFormatError(ValueError):
    """Raised when an entered edge list cannot be converted into a graph."""


@dataclass(frozen=True)
class ParsedGraph:
    """A validated graph and the properties needed by recommendation rules."""

    graph: AdjacencyListGraph
    has_negative_weight: bool
    edge_count: int


def _parse_weight(token: str, line_number: int) -> float:
    try:
        weight = float(token)
    except ValueError:
        raise InputFormatError(
            f"Line {line_number}: invalid weight {token!r}."
        ) from None
    if not weight == weight or weight in (float("inf"), float("-inf")):
        raise InputFormatError(f"Line {line_number}: weight must be finite.")
    return weight


def parse_edge_list(
    text: str,
    *,
    directed: bool,
    weighted: bool,
) -> ParsedGraph:
    """Parse ``source target [weight]`` records into a Worklet 1 graph.

    A single token declares an isolated vertex. Blank lines and lines beginning
    with ``#`` are ignored. Unweighted edges use the graph API's implicit
    unweighted representation rather than assigning a synthetic weight.
    """
    graph = AdjacencyListGraph(directed=directed, weighted=weighted)
    negative = False
    parsed_edges = 0

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        tokens = line.split()
        if len(tokens) == 1:
            try:
                graph.add_vertex(tokens[0])
            except (TypeError, ValueError) as exc:
                raise InputFormatError(
                    f"Line {line_number}: invalid vertex: {exc}"
                ) from exc
            continue

        expected = 3 if weighted else 2
        if len(tokens) != expected:
            mode = (
                "three fields (source target weight)"
                if weighted
                else "two fields (source target)"
            )
            raise InputFormatError(
                f"Line {line_number}: expected {mode}, got {len(tokens)} fields."
            )

        weight = _parse_weight(tokens[2], line_number) if weighted else None
        try:
            graph.add_edge(tokens[0], tokens[1], weight)
        except (TypeError, ValueError) as exc:
            raise InputFormatError(f"Line {line_number}: {exc}") from exc
        parsed_edges += 1
        negative = negative or (weight is not None and weight < 0)

    if not graph.vertices:
        raise InputFormatError(
            "Graph input is empty; enter at least one vertex or edge."
        )

    return ParsedGraph(graph, negative, parsed_edges)
