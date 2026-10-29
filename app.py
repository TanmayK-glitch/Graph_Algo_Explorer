
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from worklet1.graph import AdjacencyListGraph
from worklet1.algorithms import (
    BFSAlgorithm,
    DFSAlgorithm,
    CycleDetectionAlgorithm,
)
from src.algorithms import dijkstra, bellman_ford, reconstruct_path
from src.algorithms.kruskal import kruskal_mst

st.set_page_config(
    page_title="Graph Algorithm Explorer",
    page_icon="🕸️",
    layout="wide",
)

st.title("Graph Algorithm Explorer")
st.caption("Create a graph. Run an algorithm. Explore the result.")

DEFAULT_VERTICES = ["A", "B", "C", "D", "E"]
DEFAULT_EDGES = [
    ("A", "B", 4),
    ("A", "C", 2),
    ("B", "C", 1),
    ("B", "D", 5),
    ("C", "D", 8),
    ("C", "E", 10),
    ("D", "E", 2),
]

if "vertices" not in st.session_state:
    st.session_state.vertices = DEFAULT_VERTICES.copy()

if "edges" not in st.session_state:
    st.session_state.edges = DEFAULT_EDGES.copy()

if "result" not in st.session_state:
    st.session_state.result = None

with st.sidebar:
    st.header("Graph Settings")
    directed = st.toggle("Directed graph", value=False, key="directed")
    weighted = st.toggle("Weighted edges", value=True, key="weighted")

    st.divider()
    st.subheader("Add vertex")
    new_vertex = st.text_input("Vertex name", max_chars=12)

    if st.button("Add vertex", use_container_width=True):
        name = new_vertex.strip()
        if not name:
            st.warning("Enter a vertex name.")
        elif name in st.session_state.vertices:
            st.warning("Vertex already exists.")
        else:
            st.session_state.vertices.append(name)
            st.session_state.result = None
            st.rerun()

    st.divider()
    st.subheader("Add edge")

    vertices = st.session_state.vertices
    if len(vertices) >= 2:
        source_edge = st.selectbox("From", vertices, key="edge_source")
        targets = [v for v in vertices if v != source_edge]
        destination_edge = st.selectbox("To", targets, key="edge_destination")
        edge_weight = st.number_input("Weight", value=1, step=1)

        if st.button("Add edge", use_container_width=True):
            duplicate = any(
                (u == source_edge and v == destination_edge)
                or (
                    not directed
                    and u == destination_edge
                    and v == source_edge
                )
                for u, v, _ in st.session_state.edges
            )
            if duplicate:
                st.warning("That edge already exists.")
            else:
                st.session_state.edges.append(
                    (source_edge, destination_edge, edge_weight)
                )
                st.session_state.result = None
                st.rerun()

    st.divider()
    st.subheader("Remove edge")

    if st.session_state.edges:
        edge_options = [
            f"{u} → {v} (weight {w})"
            for u, v, w in st.session_state.edges
        ]
        selected_edge = st.selectbox(
            "Select edge", range(len(edge_options)),
            format_func=lambda i: edge_options[i],
        )
        if st.button("Remove selected edge", use_container_width=True):
            st.session_state.edges.pop(selected_edge)
            st.session_state.result = None
            st.rerun()

    st.divider()
    if st.button("Reset graph", use_container_width=True):
        st.session_state.vertices = DEFAULT_VERTICES.copy()
        st.session_state.edges = DEFAULT_EDGES.copy()
        st.session_state.result = None
        st.rerun()


# Build the graph for drawing and algorithm execution.
graph = nx.DiGraph() if directed else nx.Graph()
graph.add_nodes_from(st.session_state.vertices)

for u, v, w in st.session_state.edges:
    graph.add_edge(u, v, weight=w if weighted else 1)

st.subheader("Run an Algorithm")

algorithm = st.selectbox(
    "Choose algorithm",
    [
        "Dijkstra",
        "Bellman-Ford",
        "BFS",
        "DFS",
        "Kruskal (Minimum Spanning Tree)",
        "Cycle Detection",
    ],
)

needs_source = algorithm in ("Dijkstra", "Bellman-Ford", "BFS", "DFS")
if needs_source:
    start = st.selectbox("Starting vertex", st.session_state.vertices)
else:
    start = None

if algorithm in ("BFS", "DFS"):
    traversal_mode = st.radio(
        "Traversal scope",
        ["Reachable component", "All vertices"],
        horizontal=True,
    )
else:
    traversal_mode = "Reachable component"

if st.button("▶ Run Algorithm", type="primary"):
    st.session_state.result = None

    try:
        if algorithm in ("Dijkstra", "Bellman-Ford"):
            # Worklet 2 shortest-path functions expect an adjacency mapping.
            adjacency = {v: {} for v in st.session_state.vertices}
            for u, v, w in st.session_state.edges:
                adjacency[u][v] = w if weighted else 1
                if not directed:
                    adjacency[v][u] = w if weighted else 1

            if algorithm == "Dijkstra":
                if any(w < 0 for _, _, w in st.session_state.edges):
                    raise ValueError(
                        "Dijkstra requires non-negative edge weights."
                    )
                output = dijkstra(adjacency, start)
            else:
                output = bellman_ford(adjacency, start)

            st.session_state.result = {
                "algorithm": algorithm,
                "kind": "shortest_path",
                "distances": output.distances,
                "predecessors": output.predecessors,
                "source": start,
            }

        elif algorithm in ("BFS", "DFS"):
            algo_graph = AdjacencyListGraph(
                directed=directed, weighted=weighted
            )
            for v in st.session_state.vertices:
                algo_graph.add_vertex(v)
            for u, v, w in st.session_state.edges:
                algo_graph.add_edge(u, v, w if weighted else None)

            runner = BFSAlgorithm() if algorithm == "BFS" else DFSAlgorithm()
            output = runner.execute(
                algo_graph,
                start=start,
                mode="all" if traversal_mode == "All vertices" else "single",
            )

            if not output.success:
                raise ValueError(output.error_message)

            st.session_state.result = {
                "algorithm": algorithm,
                "kind": "traversal",
                "order": output.primary_output,
            }

        elif algorithm == "Cycle Detection":
            algo_graph = AdjacencyListGraph(
                directed=directed, weighted=weighted
            )
            for v in st.session_state.vertices:
                algo_graph.add_vertex(v)
            for u, v, w in st.session_state.edges:
                algo_graph.add_edge(u, v, w if weighted else None)

            output = CycleDetectionAlgorithm().execute(algo_graph)
            if not output.success:
                raise ValueError(output.error_message)

            st.session_state.result = {
                "algorithm": algorithm,
                "kind": "cycle",
                "found": bool(output.primary_output),
            }

        elif algorithm == "Kruskal (Minimum Spanning Tree)":
            if directed:
                raise ValueError("Kruskal requires an undirected graph.")

            adjacency = {v: {} for v in st.session_state.vertices}
            for u, v, w in st.session_state.edges:
                adjacency[u][v] = w if weighted else 1
                adjacency[v][u] = w if weighted else 1

            output = kruskal_mst(adjacency)
            st.session_state.result = {
                "algorithm": algorithm,
                "kind": "mst",
                "output": output,
            }

    except Exception as exc:
        st.session_state.result = {
            "algorithm": algorithm,
            "kind": "error",
            "message": str(exc),
        }


result = st.session_state.result
highlight_nodes = []
highlight_edges = []

if result:
    st.divider()
    st.subheader("Algorithm Results")

    if result["kind"] == "error":
        st.error(result["message"])

    elif result["kind"] == "shortest_path":
        st.write(f"**Source:** {result['source']}")
        rows = []
        for vertex in st.session_state.vertices:
            distance = result["distances"].get(vertex, float("inf"))
            rows.append({
                "Vertex": vertex,
                "Distance": distance if distance != float("inf") else "∞",
                "Previous vertex": result["predecessors"].get(vertex) or "—",
            })
        st.dataframe(rows, hide_index=True, use_container_width=True)

        destinations = [
            v for v in st.session_state.vertices if v != result["source"]
        ]
        if destinations:
            target = st.selectbox("Show path to", destinations)
            try:
                path = reconstruct_path(
                    result["predecessors"], result["source"], target
                )
                if path:
                    highlight_nodes = path
                    highlight_edges = list(zip(path, path[1:]))
                    st.success(" → ".join(map(str, path)))
                else:
                    st.info(f"No path found from {result['source']} to {target}.")
            except (KeyError, ValueError, TypeError):
                st.info(f"No path found from {result['source']} to {target}.")

    elif result["kind"] == "traversal":
        order = result["order"]
        if isinstance(order, (list, tuple)):
            highlight_nodes = list(order)
            highlight_edges = list(zip(order, order[1:]))
            st.success(" → ".join(map(str, order)))
        else:
            st.write(order)

    elif result["kind"] == "cycle":
        if result["found"]:
            st.warning("A cycle was detected in this graph.")
        else:
            st.success("No cycle was detected.")

    elif result["kind"] == "mst":
        st.write("Kruskal output:")
        st.write(result["output"])


st.divider()
left, right = st.columns([1.7, 1])

with left:
    st.subheader("Graph Canvas")

    positions = nx.spring_layout(graph, seed=42)
    fig, ax = plt.subplots(figsize=(9, 6))

    node_colors = [
        "orange" if node in highlight_nodes else "skyblue"
        for node in graph.nodes
    ]
    nx.draw_networkx_nodes(
        graph, positions, ax=ax, node_size=1400, node_color=node_colors
    )
    nx.draw_networkx_labels(graph, positions, ax=ax, font_size=12)

    edge_colors = []
    for u, v in graph.edges:
        highlighted = (u, v) in highlight_edges or (
            not directed and (v, u) in highlight_edges
        )
        edge_colors.append("orange" if highlighted else "gray")

    nx.draw_networkx_edges(
        graph, positions, ax=ax, arrows=directed, arrowsize=18,
        width=2.5, edge_color=edge_colors
    )

    edge_labels = {
        (u, v): str(data["weight"])
        for u, v, data in graph.edges(data=True)
    } if weighted else {}

    nx.draw_networkx_edge_labels(
        graph, positions, edge_labels=edge_labels, ax=ax
    )
    ax.set_axis_off()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Graph Overview")
    st.metric("Vertices", graph.number_of_nodes())
    st.metric("Edges", graph.number_of_edges())
    st.write("**Type:**", "Directed" if directed else "Undirected")
    st.write("**Weights:**", "Enabled" if weighted else "Disabled")

    st.subheader("Current Edges")
    edge_rows = [
        {"From": u, "To": v, "Weight": w}
        for u, v, w in st.session_state.edges
    ]
    if edge_rows:
        st.dataframe(edge_rows, hide_index=True, use_container_width=True)
    else:
        st.info("No edges yet.")
