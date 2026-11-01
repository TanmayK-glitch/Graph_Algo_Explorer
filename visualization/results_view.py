"""Human-readable presentation and metrics for algorithm execution results."""

from __future__ import annotations

from typing import Any

import streamlit as st


def _format_weight(val: float | int | None) -> str:
    """Format weight cleanly without trailing zeros for integers."""
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        v = float(val)
        return str(int(v)) if v.is_integer() else f"{v:g}"
    return str(val)


def _safe_metric_row(metrics: list[tuple[str, Any]]) -> None:
    """Render a row of metrics using st.columns or fallback."""
    if not metrics:
        return
    cols = st.columns(len(metrics))
    for col, (label, val) in zip(cols, metrics, strict=True):
        col.metric(label=label, value=str(val))


def render_human_results(
    algorithm: str,
    result: Any,
    graph: Any,
    *,
    source: Any | None = None,
    target: Any | None = None,
    objective: str | None = None,
) -> None:
    """Render a clear, human-readable summary of algorithm execution results."""

    # 1. Shortest Path (Dijkstra / Bellman-Ford)
    if hasattr(result, "path_to") and target is not None:
        path = result.path_to(target)
        if path is not None:
            dist = result.distances[target]
            st.markdown("### Shortest Route Found")
            if algorithm == "dijkstra":
                st.write(
                    f"Dijkstra's algorithm identified the optimal minimum-cost path from "
                    f"source **{source}** to destination **{target}** with non-negative edge weights."
                )
            elif algorithm == "bellman_ford":
                st.write(
                    f"Bellman-Ford algorithm identified the optimal minimum-cost path from "
                    f"source **{source}** to destination **{target}**, confirming no negative-weight cycles affect this route."
                )
            else:
                st.write(
                    f"Found the optimal path from source **{source}** to destination **{target}**."
                )

            metrics: list[tuple[str, Any]] = [
                ("Source", source),
                ("Destination", target),
                ("Total Cost", _format_weight(dist)),
                ("Hops (Edges)", len(path) - 1),
            ]
            if algorithm == "bellman_ford":
                metrics.append(("Negative Cycle", "None on route"))
            _safe_metric_row(metrics)

            st.markdown(f"**Optimal Route:** `{' ➔ '.join(str(p) for p in path)}`")

            # Edge-by-edge breakdown table
            if len(path) > 1:
                st.markdown("**Edge-by-Edge Route Breakdown:**")
                breakdown_rows = []
                cum_cost = 0.0
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    try:
                        w = graph.edge_weight(u, v)
                    except Exception:
                        w = result.distances[v] - result.distances[u]
                    step_cost = float(w) if w is not None else 0.0
                    cum_cost += step_cost
                    breakdown_rows.append(
                        f"| Step {i + 1} | `{u}` ➔ `{v}` | `{_format_weight(step_cost)}` | `{_format_weight(cum_cost)}` |"
                    )

                table_md = (
                    "| Step | Segment | Segment Cost | Cumulative Cost |\n"
                    "| :--- | :--- | :--- | :--- |\n" + "\n".join(breakdown_rows)
                )
                st.markdown(table_md)
        else:
            st.markdown("### No Route Available")
            st.warning(
                f"Destination vertex **{target}** cannot be reached from source **{source}**."
            )
            _safe_metric_row(
                [
                    ("Source", source),
                    ("Destination", target),
                    ("Route Status", "Unreachable"),
                ]
            )

    # 2. Minimum Spanning Tree (Kruskal)
    elif hasattr(result, "edges"):
        st.markdown("### Minimum Spanning Tree Computed")
        st.write(
            "Kruskal's algorithm connected all vertices with the minimum possible total weight without forming any cycles."
        )

        mst_vertices = {u for u, v, _ in result.edges} | {v for u, v, _ in result.edges}
        total_graph_vertices = len(graph.vertices)
        is_fully_connected = len(mst_vertices) == total_graph_vertices

        metrics = [
            ("Total Weight", _format_weight(result.total_weight)),
            ("Tree Edges", len(result.edges)),
            (
                "Connected Vertices",
                f"{len(mst_vertices)} of {total_graph_vertices}",
            ),
            (
                "Status",
                "Fully connected" if is_fully_connected else "Partial component",
            ),
        ]
        _safe_metric_row(metrics)

        st.markdown("**Selected Minimum Spanning Tree Edges:**")
        edge_rows = [
            f"| {i + 1} | `{u}` -- `{v}` | `{_format_weight(w)}` |"
            for i, (u, v, w) in enumerate(result.edges)
        ]
        table_md = (
            "| # | Edge Connection | Weight |\n"
            "| :--- | :--- | :--- |\n" + "\n".join(edge_rows)
        )
        st.markdown(table_md)

    # 3. BFS Shortest Path (Unweighted Graph)
    elif algorithm == "BFS" and objective == "Shortest path" and target is not None:
        parent_map = (
            result.metadata.get("parent", {}) if hasattr(result, "metadata") else {}
        )
        if target in parent_map:
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = parent_map.get(curr)
            path.reverse()

            st.markdown("### Shortest Route Found (Fewest Hops)")
            st.write(
                f"Breadth-First Search found the path with the fewest connections (edge hops) "
                f"from source **{source}** to destination **{target}**."
            )
            metrics = [
                ("Source", source),
                ("Destination", target),
                ("Total Hops", len(path) - 1),
                ("Visited Vertices", len(result.primary_output)),
            ]
            _safe_metric_row(metrics)
            st.markdown(f"**Optimal Route:** `{' ➔ '.join(str(p) for p in path)}`")
        else:
            st.markdown("### No Route Available")
            st.warning(
                f"Destination vertex **{target}** cannot be reached from source **{source}**."
            )
            _safe_metric_row(
                [
                    ("Source", source),
                    ("Destination", target),
                    ("Route Status", "Unreachable"),
                ]
            )

    # 4. BFS Traversal
    elif algorithm == "BFS":
        st.markdown("### Breadth-First Traversal Completed")
        st.write(
            f"BFS explored all reachable vertices level-by-level, visiting all immediate neighbors "
            f"before advancing deeper, starting from vertex **{source}**."
        )
        total_v = len(graph.vertices)
        visited_v = len(result.primary_output)
        metrics = [
            ("Start Vertex", source),
            ("Vertices Visited", visited_v),
            ("Total Vertices", total_v),
            ("Coverage", f"{(visited_v / total_v * 100):.0f}%"),
        ]
        _safe_metric_row(metrics)
        st.markdown(
            f"**Traversal Order:** `{' ➔ '.join(str(v) for v in result.primary_output)}`"
        )

    # 5. DFS Traversal
    elif algorithm == "DFS":
        st.markdown("### Depth-First Traversal Completed")
        st.write(
            f"DFS explored deeply along each branch to the furthest reachable vertex before backtracking, "
            f"starting from vertex **{source}**."
        )
        total_v = len(graph.vertices)
        visited_v = len(result.primary_output)
        metrics = [
            ("Start Vertex", source),
            ("Vertices Visited", visited_v),
            ("Total Vertices", total_v),
            ("Coverage", f"{(visited_v / total_v * 100):.0f}%"),
        ]
        _safe_metric_row(metrics)
        st.markdown(
            f"**Traversal Order:** `{' ➔ '.join(str(v) for v in result.primary_output)}`"
        )

    # 6. Connected Components
    elif algorithm == "ConnectedComponents":
        st.markdown("### Connected Components Identified")
        st.write(
            "Identified all isolated subgraphs where any two vertices within the same component are connected by a path."
        )
        num_components = len(result.primary_output)
        total_v = len(graph.vertices)
        metrics = [
            ("Component Count", num_components),
            ("Total Vertices", total_v),
            (
                "Connectivity",
                "Fully connected"
                if num_components == 1
                else f"{num_components} separate groups",
            ),
        ]
        _safe_metric_row(metrics)

        st.markdown("**Component Breakdown:**")
        for i, comp in enumerate(result.primary_output, 1):
            st.markdown(
                f"- **Component {i}** ({len(comp)} vertices): `{'`, `'.join(str(v) for v in comp)}`"
            )

    # 7. Strongly Connected Components (SCC)
    elif algorithm == "SCC":
        st.markdown("### Strongly Connected Components Identified")
        st.write(
            "Partitioned the directed graph into maximal subgraphs where every vertex in a group can reach every other vertex in that group."
        )
        num_scc = len(result.primary_output)
        total_v = len(graph.vertices)
        metrics = [
            ("SCC Count", num_scc),
            ("Total Vertices", total_v),
        ]
        _safe_metric_row(metrics)

        st.markdown("**Strongly Connected Component Groups:**")
        for i, comp in enumerate(result.primary_output, 1):
            st.markdown(
                f"- **Group {i}** ({len(comp)} vertices): `{'`, `'.join(str(v) for v in comp)}`"
            )

    # 8. Cycle Detection
    elif algorithm == "CycleDetection":
        has_cycle = bool(result.primary_output)
        if has_cycle:
            st.markdown("### Cycle Detected")
            st.warning("The graph contains at least one cycle (closed loop).")
            st.write(
                "Following edge directions leads back to an already visited vertex, forming a circular path."
            )
            _safe_metric_row([("Has Cycle", "Yes"), ("Graph Type", "Cyclic")])
        else:
            st.markdown("### No Cycles Detected (Acyclic)")
            st.success("The graph contains no cycles or closed loops.")
            st.write(
                "Traversing edges in the graph will never loop back to an ancestor vertex."
            )
            _safe_metric_row([("Has Cycle", "No"), ("Graph Type", "Acyclic")])

    # 9. Topological Sort
    elif algorithm == "TopologicalSort":
        if getattr(result, "success", True) and result.primary_output is not None:
            st.markdown("### Topological Ordering Found")
            st.write(
                "Found a valid linear sequence where every prerequisite vertex appears before its dependents (valid scheduling order)."
            )
            metrics = [
                ("Ordered Vertices", len(result.primary_output)),
                ("Graph Structure", "Directed Acyclic Graph (DAG)"),
            ]
            _safe_metric_row(metrics)
            st.markdown(
                f"**Valid Execution Sequence:** `{' ➔ '.join(str(v) for v in result.primary_output)}`"
            )
        else:
            st.markdown("### Topological Sort Impossible")
            st.error(
                result.error_message
                or "The graph contains a directed cycle; no linear ordering can satisfy all edge dependencies."
            )
            _safe_metric_row(
                [("Ordering Status", "Failed"), ("Reason", "Cycle Detected")]
            )

    # 10. Bipartite Test
    elif algorithm == "BipartiteTest":
        is_bipartite = bool(result.primary_output)
        if is_bipartite:
            st.markdown("### Graph Is Bipartite (2-Colorable)")
            st.success(
                "The graph can be partitioned into two independent sets such that no two adjacent vertices belong to the same set."
            )
            colouring = (
                result.metadata.get("colouring", {})
                if hasattr(result, "metadata")
                else {}
            )
            set_0 = [v for v, c in colouring.items() if c == 0]
            set_1 = [v for v, c in colouring.items() if c == 1]
            metrics = [
                ("Is Bipartite", "Yes"),
                ("Set A Vertices", len(set_0)),
                ("Set B Vertices", len(set_1)),
            ]
            _safe_metric_row(metrics)
            st.markdown(
                f"- **Set A:** `{'`, `'.join(str(v) for v in set_0)}`\n"
                f"- **Set B:** `{'`, `'.join(str(v) for v in set_1)}`"
            )
        else:
            st.markdown("### Graph Is Not Bipartite")
            st.warning(
                "The graph cannot be partitioned into two independent sets because it contains an odd-length cycle."
            )
            _safe_metric_row(
                [
                    ("Is Bipartite", "No"),
                    ("Reason", "Contains odd-length cycle"),
                ]
            )

    # Default fallback for any other algorithm result
    else:
        st.markdown(f"### Algorithm Results: {algorithm}")
        st.write(result.primary_output)
