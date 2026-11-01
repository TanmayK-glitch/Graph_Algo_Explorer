"""Streamlit entry point for Graph Algorithms Explorer."""

from __future__ import annotations

import math
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from visualization.execution import execute_algorithm
from visualization.input_parser import InputFormatError, parse_edge_list
from visualization.recommendation import OBJECTIVES, recommend_algorithm
from visualization.renderer import render_graph
from visualization.results_view import render_human_results

# ---------------------------------------------------------------------------
# Centralized display-name mapping
# ---------------------------------------------------------------------------
# Internal algorithm identifiers (used by recommendation.py and execution.py)
# are mapped to human-readable labels for every user-facing surface.

DISPLAY_NAMES: dict[str, str] = {
    "BFS": "BFS",
    "DFS": "DFS",
    "dijkstra": "Dijkstra",
    "bellman_ford": "Bellman-Ford",
    "kruskal": "Kruskal",
    "ConnectedComponents": "Connected Components",
    "SCC": "Strongly Connected Components",
    "CycleDetection": "Cycle Detection",
    "TopologicalSort": "Topological Sort",
    "BipartiteTest": "Bipartite Test",
}


def _display_name(algo: str | None) -> str:
    """Return a user-facing display name for an internal algorithm identifier."""
    if algo is None:
        return "Unsupported"
    return DISPLAY_NAMES.get(algo, algo)


# ---------------------------------------------------------------------------
# Example presets
# ---------------------------------------------------------------------------

EXAMPLES: dict[str, dict[str, Any]] = {
    "Weighted shortest path": {
        "directed": True,
        "weighted": True,
        "objective": "Shortest path",
        "edge_text": "A B 4\nA C 2\nB C 1\nC D 3",
    },
    "Directed DAG": {
        "directed": True,
        "weighted": False,
        "objective": "Topological ordering",
        "edge_text": "A B\nA C\nB D\nC D",
    },
    "Undirected traversal": {
        "directed": False,
        "weighted": False,
        "objective": "Explore or traverse",
        "edge_text": "A B\nA C\nB D\nC D\nE",
    },
}


def _apply_example(example: str) -> None:
    if example in EXAMPLES:
        preset = EXAMPLES[example]
        st.session_state["directed"] = preset["directed"]
        st.session_state["weighted"] = preset["weighted"]
        st.session_state["objective"] = preset["objective"]
        st.session_state["edge_text"] = preset["edge_text"]


def _on_example_change() -> None:
    _apply_example(st.session_state.example_selector)


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Graph Algorithms Explorer", layout="wide")
st.title("Graph Algorithms Explorer")
st.caption(
    "Enter a graph, receive a rule-based recommendation, and inspect the algorithm result."
)

# ---------------------------------------------------------------------------
# Sidebar - graph input
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Graph Input")
    example_name = st.selectbox(
        "Load an example",
        ["Custom", *EXAMPLES],
        key="example_selector",
        on_change=_on_example_change,
    )
    if st.session_state.get("_last_example") != example_name:
        if example_name in EXAMPLES:
            _apply_example(example_name)
        st.session_state["_last_example"] = example_name

    directed = st.checkbox("Directed graph", key="directed")
    weighted = st.checkbox("Weighted graph", key="weighted")
    objective = st.selectbox("Objective", OBJECTIVES, key="objective")
    edge_text = st.text_area(
        "Edges (source target [weight], one per line)",
        height=180,
        key="edge_text",
        help="Use two fields for unweighted edges or three fields for weighted edges. "
        "Lines with one token add isolated vertices. # starts a comment.",
    )

# ---------------------------------------------------------------------------
# Parse input
# ---------------------------------------------------------------------------

try:
    parsed = parse_edge_list(edge_text, directed=directed, weighted=weighted)
except InputFormatError as exc:
    st.error(str(exc))
    st.stop()
    parsed = None

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

if parsed is not None:
    recommendation = recommend_algorithm(
        objective,
        parsed.graph,
        has_negative_weight=parsed.has_negative_weight,
    )

    # --- Recommendation section -------------------------------------------
    st.subheader("Recommendation")
    st.write(f"**Algorithm:** {_display_name(recommendation.algorithm)}")
    st.write(recommendation.explanation)
    st.write("**Properties considered:** " + ", ".join(recommendation.properties))
    for limitation in recommendation.limitations:
        st.info(limitation)

    # --- Build eligible algorithm list ------------------------------------
    if objective == "Explore or traverse":
        algorithm_options = ["BFS", "DFS"]
    elif objective == "Shortest path":
        if not parsed.graph.is_weighted:
            algorithm_options = ["BFS"]
        elif recommendation.supported and not parsed.has_negative_weight:
            algorithm_options = ["dijkstra", "bellman_ford"]
        elif recommendation.supported and parsed.has_negative_weight:
            algorithm_options = ["bellman_ford"]
        else:
            algorithm_options = []
    elif objective == "Minimum spanning tree":
        algorithm_options = ["kruskal"] if recommendation.supported else []
    elif objective == "Check connectivity":
        algorithm_options = (
            ["SCC"] if parsed.graph.is_directed else ["ConnectedComponents"]
        )
    elif objective == "Detect cycles":
        algorithm_options = ["CycleDetection"]
    elif objective == "Topological ordering":
        algorithm_options = ["TopologicalSort"] if recommendation.supported else []
    elif objective == "Check bipartite":
        algorithm_options = ["BipartiteTest"] if recommendation.supported else []
    else:
        algorithm_options = []

    if not algorithm_options:
        algorithm_options = ["Unsupported"]
        _dropdown_disabled = True
    else:
        _dropdown_disabled = False

    default_index = (
        algorithm_options.index(recommendation.algorithm)
        if recommendation.algorithm in algorithm_options
        else 0
    )

    def _label(algo: str) -> str:
        """Format algorithm option with display name and recommended tag."""
        name = _display_name(algo)
        if algo == recommendation.algorithm and len(algorithm_options) > 1:
            return f"{name} (Recommended)"
        return name

    selected_algorithm = st.selectbox(
        "Select Algorithm",
        algorithm_options,
        index=default_index,
        format_func=_label,
        disabled=_dropdown_disabled,
    )

    # --- Source / destination selection ------------------------------------
    needs_source = selected_algorithm in {"BFS", "DFS", "dijkstra", "bellman_ford"}
    source = None
    target = None
    if needs_source:
        source = st.selectbox("Source vertex", parsed.graph.vertices)
    if objective == "Shortest path" and not _dropdown_disabled:
        target = st.selectbox("Destination vertex", parsed.graph.vertices)

    # --- Run button -------------------------------------------------------
    input_key = (
        directed,
        weighted,
        objective,
        edge_text,
        selected_algorithm,
        source,
        target,
    )
    if "run_token" not in st.session_state:
        st.session_state.run_token = None
    run_clicked = st.button(
        "Run Algorithm", type="primary", disabled=_dropdown_disabled
    )
    if run_clicked:
        try:
            result = execute_algorithm(parsed.graph, selected_algorithm, source=source)
        except (ValueError, RuntimeError, KeyError) as exc:
            st.error(f"Algorithm could not be executed: {exc}")
        else:
            st.session_state.run_token = (
                input_key,
                parsed.graph,
                selected_algorithm,
                result,
                target,
            )

    # --- Results & Visualization ------------------------------------------
    if (
        st.session_state.run_token is not None
        and st.session_state.run_token[0] == input_key
    ):
        _, _, algorithm, result, result_target = st.session_state.run_token
        st.subheader("Results")
        render_human_results(
            algorithm,
            result,
            parsed.graph,
            source=source,
            target=result_target,
            objective=objective,
        )

        st.subheader("Visualization")
        try:
            components.html(
                render_graph(parsed.graph, result, source=source, target=result_target),
                height=750,
                scrolling=False,
            )
        except RuntimeError as exc:
            st.error(str(exc))

        with st.expander("Advanced Details (Technical Output)", expanded=False):
            st.write(f"**Algorithm:** {_display_name(algorithm)}")
            if hasattr(result, "path_to") and result_target is not None:
                path = result.path_to(result_target)
                st.json({"source": source, "destination": result_target, "path": path})
                if path is not None:
                    st.json({"distance": result.distances[result_target]})
                st.json(
                    {
                        "distances": {
                            vertex: distance
                            for vertex, distance in result.distances.items()
                            if not math.isinf(distance)
                        }
                    }
                )
            elif hasattr(result, "edges"):
                st.json(
                    {
                        "selected_edges": result.edges,
                        "total_weight": result.total_weight,
                    }
                )
            else:
                st.write(result.primary_output)
                if result.metadata:
                    st.json(result.metadata)
                if not result.success:
                    st.warning(result.error_message)
