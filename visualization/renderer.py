"""PyVis rendering for graph inputs and algorithm results."""

from __future__ import annotations

import json
from itertools import pairwise
from typing import Any


def _get_layout_config(num_vertices: int) -> dict[str, Any]:
    """Return layout and physics options adapted to the graph vertex count."""
    if num_vertices <= 10:
        return {
            "gravitationalConstant": -6000,
            "centralGravity": 0.08,
            "springLength": 260,
            "springConstant": 0.04,
            "damping": 0.09,
            "avoidOverlap": 1.0,
            "node_size_base": 26,
            "font_size": 15,
        }
    if num_vertices <= 35:
        return {
            "gravitationalConstant": -3800,
            "centralGravity": 0.15,
            "springLength": 190,
            "springConstant": 0.04,
            "damping": 0.09,
            "avoidOverlap": 0.8,
            "node_size_base": 22,
            "font_size": 14,
        }
    if num_vertices <= 70:
        return {
            "gravitationalConstant": -2200,
            "centralGravity": 0.2,
            "springLength": 140,
            "springConstant": 0.05,
            "damping": 0.09,
            "avoidOverlap": 0.5,
            "node_size_base": 18,
            "font_size": 12,
        }
    return {
        "gravitationalConstant": -1200,
        "centralGravity": 0.25,
        "springLength": 95,
        "springConstant": 0.05,
        "damping": 0.1,
        "avoidOverlap": 0.3,
        "node_size_base": 14,
        "font_size": 11,
    }


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

    highlighted_edges: set[tuple[Any, Any]] = set()
    path_nodes: set[Any] = set()
    path_intermediate: set[Any] = set()
    mst_nodes: set[Any] = set()
    visited_nodes: set[Any] = set()

    if result is not None:
        if hasattr(result, "path_to") and target is not None:
            path = result.path_to(target) or []
            if path:
                path_nodes.update(path)
                if len(path) > 2:
                    path_intermediate.update(path[1:-1])
                highlighted_edges.update(pairwise(path))
        if hasattr(result, "edges"):
            for u, v, _ in result.edges:
                highlighted_edges.add((u, v))
                mst_nodes.add(u)
                mst_nodes.add(v)
        primary = getattr(result, "primary_output", None)
        if isinstance(primary, list) and all(
            not isinstance(item, (list, tuple, set, dict)) for item in primary
        ):
            visited_nodes.update(primary)

    num_vertices = len(graph.vertices)
    layout = _get_layout_config(num_vertices)
    base_node_size = layout["node_size_base"]
    font_size = layout["font_size"]

    network = Network(height="720px", width="100%", directed=graph.is_directed)
    options = {
        "interaction": {
            "hover": True,
            "hoverConnectedEdges": True,
            "selectConnectedEdges": True,
            "navigationButtons": True,
            "zoomView": True,
            "dragNodes": True,
            "dragView": True,
            "multiselect": False,
            "tooltipDelay": 150,
        },
        "physics": {
            "enabled": True,
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": layout["gravitationalConstant"],
                "centralGravity": layout["centralGravity"],
                "springLength": layout["springLength"],
                "springConstant": layout["springConstant"],
                "damping": layout["damping"],
                "avoidOverlap": layout["avoidOverlap"],
            },
            "stabilization": {
                "enabled": True,
                "iterations": 250,
                "updateInterval": 25,
                "fit": True,
            },
        },
        "edges": {
            "font": {
                "size": max(11, font_size - 1),
                "color": "#1f2937",
                "strokeWidth": 3,
                "strokeColor": "#ffffff",
                "align": "horizontal",
            },
            "arrows": {
                "to": {
                    "enabled": bool(graph.is_directed),
                    "scaleFactor": 1.2,
                }
            },
            "smooth": False,
        },
        "nodes": {
            "shape": "dot",
            "font": {
                "size": font_size,
                "color": "#1f2937",
                "strokeWidth": 2,
                "strokeColor": "#ffffff",
                "face": "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            },
            "borderWidth": 2,
            "borderWidthSelected": 3,
        },
    }
    network.set_options(json.dumps(options))

    # Pre-compute directed edge set to identify bidirectional pairs
    directed_pairs = {(edge.src, edge.dst) for edge in graph.all_edges()}

    for vertex in graph.vertices:
        is_src = source is not None and vertex == source
        is_tgt = target is not None and vertex == target
        is_path = vertex in path_intermediate
        is_mst = vertex in mst_nodes
        is_visited = vertex in visited_nodes

        if is_src:
            color = {
                "background": "#2ec4b6",
                "border": "#0f7173",
                "highlight": {"background": "#38b000", "border": "#004b23"},
                "hover": {"background": "#52b788", "border": "#1b4332"},
            }
            node_size = base_node_size + 4
            border_width = 3
            title = f"Source Vertex: {vertex}"
        elif is_tgt:
            color = {
                "background": "#e71d36",
                "border": "#9b111e",
                "highlight": {"background": "#ff4d6d", "border": "#590d22"},
                "hover": {"background": "#ff758f", "border": "#800f2f"},
            }
            node_size = base_node_size + 4
            border_width = 3
            title = f"Destination Vertex: {vertex}"
        elif is_path or is_mst:
            color = {
                "background": "#ff9f1c",
                "border": "#d47a00",
                "highlight": {"background": "#ffb703", "border": "#bc6c25"},
                "hover": {"background": "#ffd166", "border": "#dda15e"},
            }
            node_size = base_node_size + 2
            border_width = 2.5
            title = f"Path Vertex: {vertex}" if is_path else f"MST Vertex: {vertex}"
        elif is_visited:
            color = {
                "background": "#90e0ef",
                "border": "#0077b6",
                "highlight": {"background": "#00b4d8", "border": "#03045e"},
                "hover": {"background": "#ade8f4", "border": "#023e8a"},
            }
            node_size = base_node_size
            border_width = 2
            title = f"Visited Vertex: {vertex}"
        else:
            color = {
                "background": "#457b9d",
                "border": "#1d3557",
                "highlight": {"background": "#1d3557", "border": "#0d1b2a"},
                "hover": {"background": "#a8dadc", "border": "#1d3557"},
            }
            node_size = base_node_size
            border_width = 1.5
            title = f"Vertex: {vertex}"

        network.add_node(
            vertex,
            label=str(vertex),
            title=title,
            color=color,
            size=node_size,
            borderWidth=border_width,
            shape="dot",
        )

    for edge in graph.all_edges():
        key = (edge.src, edge.dst)
        reverse_key = (edge.dst, edge.src)

        if graph.is_directed:
            is_highlighted = key in highlighted_edges
        else:
            is_highlighted = (
                key in highlighted_edges or reverse_key in highlighted_edges
            )

        if edge.weight is None:
            label = ""
        elif isinstance(edge.weight, (int, float)):
            w = float(edge.weight)
            label = str(int(w)) if w.is_integer() else f"{w:g}"
        else:
            label = str(edge.weight)

        op = "->" if graph.is_directed else "--"
        edge_title = (
            f"{edge.src} {op} {edge.dst} (weight: {label})"
            if label
            else f"{edge.src} {op} {edge.dst}"
        )

        is_bidirectional = graph.is_directed and (edge.dst, edge.src) in directed_pairs
        smooth = (
            {"enabled": True, "type": "curvedCW", "roundness": 0.22}
            if is_bidirectional
            else False
        )

        if is_highlighted:
            edge_color = {
                "color": "#e71d36",
                "highlight": "#d90429",
                "hover": "#ff4d6d",
            }
            width = 4.5
            font_cfg = {
                "size": max(12, font_size),
                "color": "#d90429",
                "strokeWidth": 3,
                "strokeColor": "#ffffff",
                "bold": True,
                "align": "horizontal",
            }
            arrows_cfg = (
                {"to": {"enabled": True, "scaleFactor": 1.35}}
                if graph.is_directed
                else ""
            )
        else:
            edge_color = {
                "color": "#adb5bd",
                "highlight": "#6c757d",
                "hover": "#495057",
            }
            width = 1.5
            font_cfg = {
                "size": max(11, font_size - 1),
                "color": "#495057",
                "strokeWidth": 3,
                "strokeColor": "#ffffff",
                "align": "horizontal",
            }
            arrows_cfg = (
                {"to": {"enabled": True, "scaleFactor": 1.0}}
                if graph.is_directed
                else ""
            )

        network.add_edge(
            edge.src,
            edge.dst,
            label=label,
            title=edge_title,
            color=edge_color,
            width=width,
            arrows=arrows_cfg,
            smooth=smooth,
            font=font_cfg,
        )

    return network.generate_html()
