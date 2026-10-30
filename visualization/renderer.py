"""PyVis rendering for graph inputs and algorithm results."""

from __future__ import annotations

import json
from itertools import pairwise
from typing import Any


def render_graph(
    graph: Any, result: Any = None, *, source: Any = None, target: Any = None
) -> str:
    """Return standalone interactive HTML generated from the current graph."""
    try:
        from pyvis.network import Network
    except ImportError as exc:
        raise RuntimeError(
            "PyVis is required for graph rendering. Install dependencies from requirements.txt."
        ) from exc

    highlighted_nodes = {value for value in (source, target) if value is not None}
    highlighted_edges: set[tuple[Any, Any]] = set()
    visited_nodes: set[Any] = set()

    if result is not None:
        if hasattr(result, "path_to") and target is not None:
            path = result.path_to(target) or []
            highlighted_nodes.update(path)
            highlighted_edges.update(pairwise(path))
        if hasattr(result, "edges"):
            highlighted_edges.update((u, v) for u, v, _ in result.edges)
        primary = getattr(result, "primary_output", None)
        if isinstance(primary, list) and all(
            not isinstance(item, (list, tuple, set, dict)) for item in primary
        ):
            visited_nodes.update(primary)

    network = Network(height="650px", width="100%", directed=graph.is_directed)
    network.set_options(
        json.dumps(
            {
                "interaction": {"hover": True, "navigationButtons": True},
                "physics": {"stabilization": True},
            }
        )
    )

    for vertex in graph.vertices:
        color = (
            "#ffb703"
            if vertex in highlighted_nodes
            else ("#8ecae6" if vertex in visited_nodes else "#219ebc")
        )
        network.add_node(
            vertex, label=str(vertex), title=f"Vertex: {vertex}", color=color
        )

    for edge in graph.all_edges():
        key = (edge.src, edge.dst)
        reverse_key = (edge.dst, edge.src)
        is_highlighted = key in highlighted_edges or reverse_key in highlighted_edges
        label = "" if edge.weight is None else str(edge.weight)
        network.add_edge(
            edge.src,
            edge.dst,
            label=label,
            title=f"{edge.src} -> {edge.dst}"
            + (f" (weight {edge.weight})" if label else ""),
            color="#d62828" if is_highlighted else "#6c757d",
            width=4 if is_highlighted else 1,
            arrows="to" if graph.is_directed else "",
        )
    return network.generate_html()
