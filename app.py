"""Streamlit entry point for Graph Algorithms Explorer."""

from __future__ import annotations

import math

import streamlit as st
import streamlit.components.v1 as components

from visualization.execution import execute_algorithm
from visualization.input_parser import InputFormatError, parse_edge_list
from visualization.recommendation import OBJECTIVES, recommend_algorithm
from visualization.renderer import render_graph

EXAMPLES = {
    "Weighted shortest path": "A B 4\nA C 2\nB C 1\nC D 3",
    "Directed DAG": "A B 1\nA C 1\nB D 1\nC D 1",
    "Undirected traversal": "A B\nA C\nB D\nC D\nE",
}

st.set_page_config(page_title="Graph Algorithms Explorer", layout="wide")
st.title("Graph Algorithms Explorer")
st.caption(
    "Enter a graph, receive a rule-based recommendation, and inspect the actual algorithm result."
)

with st.sidebar:
    st.header("Graph input")
    example_name = st.selectbox("Load an example", ["Custom", *EXAMPLES])
    directed = st.checkbox("Directed graph")
    weighted = st.checkbox("Weighted graph")
    objective = st.selectbox("Objective", OBJECTIVES)
    edge_text = st.text_area(
        "Edges (source target [weight], one per line)",
        value=EXAMPLES.get(example_name, ""),
        height=180,
        help="Use two fields for unweighted edges or three fields for weighted edges. Lines with one token add isolated vertices. # starts a comment.",
    )

try:
    parsed = parse_edge_list(edge_text, directed=directed, weighted=weighted)
except InputFormatError as exc:
    st.error(str(exc))
    st.stop()

recommendation = recommend_algorithm(
    objective,
    parsed.graph,
    has_negative_weight=parsed.has_negative_weight,
)

st.subheader("Recommendation")
st.write(f"**Algorithm:** {recommendation.algorithm or 'Unsupported'}")
st.write(recommendation.explanation)
st.write("**Properties considered:** " + ", ".join(recommendation.properties))
for limitation in recommendation.limitations:
    st.info(limitation)

needs_source = recommendation.algorithm in {"BFS", "DFS", "dijkstra", "bellman_ford"}
source = None
target = None
if needs_source:
    source = st.selectbox("Source vertex", parsed.graph.vertices)
if objective == "Shortest path" and recommendation.supported:
    target = st.selectbox("Destination vertex", parsed.graph.vertices)

input_key = (directed, weighted, objective, edge_text, source, target)
if "run_token" not in st.session_state:
    st.session_state.run_token = None
run_clicked = st.button(
    "Run Algorithm", type="primary", disabled=not recommendation.supported
)
if run_clicked:
    try:
        result = execute_algorithm(
            parsed.graph, recommendation.algorithm, source=source
        )
    except (ValueError, RuntimeError, KeyError) as exc:
        st.error(f"Algorithm could not be executed: {exc}")
    else:
        st.session_state.run_token = (
            input_key,
            parsed.graph,
            recommendation.algorithm,
            result,
            target,
        )

if (
    st.session_state.run_token is not None
    and st.session_state.run_token[0] == input_key
):
    _, _, algorithm, result, result_target = st.session_state.run_token
    st.subheader("Visualization")
    try:
        components.html(
            render_graph(parsed.graph, result, source=source, target=result_target),
            height=680,
            scrolling=False,
        )
    except RuntimeError as exc:
        st.error(str(exc))

    st.subheader("Results")
    st.write(f"**Algorithm:** {algorithm}")
    if hasattr(result, "path_to") and result_target is not None:
        path = result.path_to(result_target)
        st.write({"source": source, "destination": result_target, "path": path})
        if path is not None:
            st.write({"distance": result.distances[result_target]})
        st.write(
            {
                "distances": {
                    vertex: distance
                    for vertex, distance in result.distances.items()
                    if not math.isinf(distance)
                }
            }
        )
    elif hasattr(result, "edges"):
        st.write({"selected_edges": result.edges, "total_weight": result.total_weight})
    else:
        st.write(result.primary_output)
        if result.metadata:
            st.write(result.metadata)
        if not result.success:
            st.warning(result.error_message)
