"""Complete, narrated demonstration of Worklet 1  -  one file, every feature.

Run from the project root::

    python -m worklet1.demo            # prints everything at once
    python -m worklet1.demo --pause    # waits for ENTER between sections (use this when presenting)

Each section prints WHAT is being shown, a small picture of the graph, the actual output of the
code, and WHY the answer is correct.  Sections follow the order of the design document.
"""

from __future__ import annotations

import sys
from pathlib import Path

from worklet1.algorithms import (
    BFSAlgorithm,
    BipartiteTestAlgorithm,
    ConnectedComponentsAlgorithm,
    CycleDetectionAlgorithm,
    DFSAlgorithm,
    SCCAlgorithm,
    TopologicalSortAlgorithm,
)
from worklet1.graph import (
    AdjacencyListGraph,
    AdjacencyMatrixGraph,
    EdgeAlreadyExistsError,
    EdgeNotFoundError,
    Graph,
    VertexNotFoundError,
)
from worklet1.io import EdgeListFormatError, EdgeListLoader

SAMPLES = Path(__file__).resolve().parent / "sample_graphs"
PAUSE = "--pause" in sys.argv
_section = 0


def section(title: str, why: str) -> None:
    """Start a numbered section: heading plus a one-line explanation of its purpose."""
    global _section
    _section += 1
    if PAUSE and _section > 1:
        input("\n[press ENTER for the next section] ")
    print(f"\n{'=' * 78}\n{_section}. {title}\n{'=' * 78}\n{why}\n")


def picture(text: str) -> None:
    """Print an ASCII picture of the graph being used."""
    print("\n".join("    " + line for line in text.strip("\n").splitlines()) + "\n")


def show(label: str, value: object) -> None:
    """Print one labelled result line."""
    print(f"  {label:<34} {value}")


def table_view(g: Graph) -> str:
    """Render a graph as an adjacency matrix using only the public interface."""
    vs = g.vertices
    lines = ["  (matrix view: 1 = edge)", "  " + " " * 5 + "".join(f"{v!s:>3}" for v in vs)]
    for a in vs:
        lines.append("  " + f"{a!s:>4} " + "".join(f"{int(g.has_edge(a, b)):>3}" for b in vs))
    return "\n".join(lines)


def make(cls: type, edges: list, directed: bool = False, extra: tuple = ()) -> Graph:
    """Build a small unweighted graph of the given representation."""
    g = cls(directed=directed)
    for u, v in edges:
        g.add_edge(u, v)
    for v in extra:
        g.add_vertex(v)
    return g


def count_lines(cls: type, n: int) -> int:
    """Count executed lines inside the representation module during a BFS on a path graph."""
    from worklet1.algorithms import bfs_all

    g = cls()
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    counter = [0]
    previous = sys.gettrace()

    def tracer(frame, event, arg):
        if frame.f_code.co_filename.endswith(("adj_list.py", "adj_matrix.py")):
            if event == "line":
                counter[0] += 1
            return tracer
        return None

    sys.settrace(tracer)
    try:
        bfs_all(g)
    finally:
        sys.settrace(previous)
    return counter[0]


def main() -> None:
    """Run the full demonstration."""
    print("WORKLET 1 - GRAPH MODEL, TRAVERSAL AND CONNECTIVITY  (COEP Mini Project 9)")
    print("Pure Python standard library. Two hand-built representations, seven algorithms, one loader.")

    # ------------------------------------------------------------------ 1
    section("Two representations behind ONE interface",
            "Same calls, same answers. The list stores only edges that exist (O(V+E)); the matrix\n"
            "stores a cell for every vertex pair (O(V^2)) but answers 'is there an edge?' in O(1).")
    for cls in (AdjacencyListGraph, AdjacencyMatrixGraph):
        g = cls(directed=False, weighted=True)
        g.add_edge("A", "B", 4.0)
        g.add_edge("A", "C", -2.0)  # negative weights are allowed by the graph model
        print(f"  {cls.__name__}")
        show("vertices", g.vertices)
        show("neighbours('A')", g.neighbours("A"))
        show("all_edges()", [(e.src, e.dst, e.weight) for e in g.all_edges()])
        show("edge_weight('A','C')  [proposed]", g.edge_weight("A", "C"))
        show("vertex_count / edge_count", (g.vertex_count(), g.edge_count()))
        print()
    print(table_view(g))
    print("\n  -> identical output from both classes: algorithms cannot tell them apart.")

    # ------------------------------------------------------------------ 2
    section("Editing a graph and its error handling",
            "add/remove vertices and edges. Bad requests raise clear, specific exceptions and\n"
            "leave the graph unchanged.")
    for cls in (AdjacencyListGraph, AdjacencyMatrixGraph):
        g = cls(directed=True)
        g.add_edge("A", "B")  # missing vertices are created automatically
        g.add_edge("B", "C")
        g.add_edge("C", "C")  # a self-loop is allowed
        print(f"  [{cls.__name__}]")
        show("after 3 add_edge calls", f"vertices={g.vertices} edges={g.edge_count()}")
        for label, action in (
            ("add_edge('A','B') again", lambda g=g: g.add_edge("A", "B")),
            ("remove_edge('C','A')", lambda g=g: g.remove_edge("C", "A")),
            ("neighbours('Z')", lambda g=g: g.neighbours("Z")),
            ("add_vertex(1.5)", lambda g=g: g.add_vertex(1.5)),
        ):
            try:
                action()
            except (EdgeAlreadyExistsError, EdgeNotFoundError, VertexNotFoundError, TypeError) as exc:
                show(label, f"{type(exc).__name__}: {exc}")
        g.remove_vertex("B")  # removes every edge touching B
        show("after remove_vertex('B')", f"vertices={g.vertices} edges={g.edge_count()}")
        print()

    # ------------------------------------------------------------------ 3
    section("Loading a graph from an edge-list file",
            "Format v1 (PROPOSED - pending Worklet 2/3 sign-off): two header lines, then 'u v [weight]'.")
    sample = (SAMPLES / "weighted_directed.edgelist").read_text(encoding="utf-8")
    print("    " + sample.replace("\n", "\n    ").rstrip())
    g = EdgeListLoader.load(SAMPLES / "weighted_directed.edgelist")
    print()
    show("loaded as", f"{type(g).__name__}, directed={g.is_directed}, weighted={g.is_weighted}")
    show("edges", [(e.src, e.dst, e.weight) for e in g.all_edges()])
    print("\n  Malformed files give a clear error that names the line:")
    for name in ("missing_weight", "bad_weight", "duplicate_edge", "no_header"):
        try:
            EdgeListLoader.load(SAMPLES / "malformed" / f"{name}.edgelist")
        except EdgeListFormatError as exc:
            show(f"{name}.edgelist", exc)
    try:
        EdgeListLoader.load(SAMPLES / "does_not_exist.edgelist")
    except FileNotFoundError as exc:
        show("missing file", f"FileNotFoundError: {exc.filename.split('/')[-1]}")

    # ------------------------------------------------------------------ 4
    section("BFS and DFS - visit order, one component vs the whole graph",
            "BFS uses a FIFO queue (level by level). DFS uses a stack (goes deep first).\n"
            "BFS(start)/DFS(start) cover only start's component; mode='all' restarts from every unvisited vertex.")
    picture("""
        A --- B --- D        F --- G        H
        |           |
        C ----------+
    """)
    g = make(AdjacencyListGraph, [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("F", "G")], extra=("H",))
    bfs_r = BFSAlgorithm().execute(g, start="A")
    show("BFS from A", bfs_r.primary_output)
    show("  parent map (shortest-path tree)", bfs_r.metadata["parent"])
    show("DFS from A", DFSAlgorithm().execute(g, start="A").primary_output)
    show("DFS from A (iterative variant)", DFSAlgorithm().execute(g, start="A", iterative=True).primary_output)
    show("BFS_ALL (whole graph)", BFSAlgorithm().execute(g, mode="all").primary_output)
    show("DFS_ALL (whole graph)", DFSAlgorithm().execute(g, mode="all").primary_output)
    try:
        BFSAlgorithm().execute(g, start="Z")
    except VertexNotFoundError as exc:
        show("BFS from unknown vertex 'Z'", f"VertexNotFoundError: {exc}")
    print("\n  -> BFS reaches D after B and C because both are 1 step from A (FIFO = nearest first).")

    # ------------------------------------------------------------------ 5
    section("Connected components (undirected)",
            "Repeated BFS: each BFS from an unvisited vertex finds exactly one component.\n"
            "Isolated vertices are singleton components.")
    r = ConnectedComponentsAlgorithm().execute(g)
    show("components", r.primary_output)
    show("count / component_map [proposed]", f"{r.metadata['count']} / {r.metadata['component_map']}")
    try:
        ConnectedComponentsAlgorithm().execute(make(AdjacencyListGraph, [("A", "B")], directed=True))
    except ValueError as exc:
        show("on a directed graph", f"ValueError: {exc}")

    # ------------------------------------------------------------------ 6
    section("Strongly connected components (Kosaraju)",
            "Pass 1: DFS recording finish order. Transpose the graph. Pass 2: DFS in reverse finish order;\n"
            "every tree is one SCC.")
    picture("""
        A <--> B        C ---> D
    """)
    g = make(AdjacencyMatrixGraph, [("A", "B"), ("B", "A"), ("C", "D")], directed=True)
    show("SCCs", SCCAlgorithm().execute(g).primary_output)
    picture("""
        A --> B --> C --> A      (one big cycle)      C --> D
    """)
    g = EdgeListLoader.load(SAMPLES / "directed_cycle.edgelist", graph_class=AdjacencyMatrixGraph)
    show("SCCs of directed_cycle.edgelist", SCCAlgorithm().execute(g).primary_output)

    # ------------------------------------------------------------------ 7
    section("Cycle detection - directed and undirected",
            "Undirected: reaching a visited vertex that is not my parent. Directed: reaching a vertex that is\n"
            "still on the CURRENT path (rec_stack); a plain visited set cannot tell this from a harmless cross edge.")
    picture("""
        Diamond (no cycle):  A -> B -> D          Cross edges are NOT cycles
                             A -> C -> D
    """)
    dag = EdgeListLoader.load(SAMPLES / "diamond_dag.edgelist")
    cyc = EdgeListLoader.load(SAMPLES / "directed_cycle.edgelist")
    loop = EdgeListLoader.load(SAMPLES / "self_loop.edgelist")
    tri = EdgeListLoader.load(SAMPLES / "triangle.edgelist")
    show("diamond DAG has cycle?", CycleDetectionAlgorithm().execute(dag).primary_output)
    show("A->B->C->A has cycle?", CycleDetectionAlgorithm().execute(cyc).primary_output)
    show("undirected triangle has cycle?", CycleDetectionAlgorithm().execute(tri).primary_output)
    show("undirected self-loop has cycle?", CycleDetectionAlgorithm().execute(loop).primary_output)

    # ------------------------------------------------------------------ 8
    section("Topological sort (Kahn)",
            "Repeatedly output vertices with no unfinished prerequisites. If the output is shorter than the\n"
            "graph, a cycle blocked the rest - success=False, no ordering exists.")
    r = TopologicalSortAlgorithm().execute(dag)
    show("diamond DAG order", r.primary_output)
    pos = {v: i for i, v in enumerate(r.primary_output)}
    show("every edge goes forward?", all(pos[e.src] < pos[e.dst] for e in dag.all_edges()))
    r = TopologicalSortAlgorithm().execute(cyc)
    show("cyclic graph", f"output={r.primary_output} success={r.success}")
    show("  message", r.error_message)
    try:
        TopologicalSortAlgorithm().execute(tri)
    except ValueError as exc:
        show("on an undirected graph", f"ValueError: {exc}")

    # ------------------------------------------------------------------ 9
    section("Bipartite test (BFS two-colouring)",
            "Colour a start vertex 0, its neighbours 1, theirs 0, ... A conflict means an odd cycle.")
    picture("""
        4-cycle A-B-C-D-A  -> bipartite          triangle A-B-C-A -> NOT bipartite
    """)
    ev = EdgeListLoader.load(SAMPLES / "even_cycle.edgelist")
    r = BipartiteTestAlgorithm().execute(ev)
    show("4-cycle", f"{r.primary_output}  colouring={r.metadata['colouring']}")
    show("every edge joins different colours?",
         all(r.metadata["colouring"][e.src] != r.metadata["colouring"][e.dst] for e in ev.all_edges()))
    show("triangle", BipartiteTestAlgorithm().execute(tri).primary_output)
    show("self-loop", BipartiteTestAlgorithm().execute(loop).primary_output)
    try:
        BipartiteTestAlgorithm().execute(dag)
    except ValueError as exc:
        show("on a directed graph", f"ValueError: {exc}")

    # ------------------------------------------------------------------ 10
    section("Representation independence - the same algorithm on list AND matrix",
            "Every algorithm only calls vertices / neighbours / all_edges, so the results must be identical.")
    edges = [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D"), ("E", "F")]
    cases = (
        ("BFS_ALL", BFSAlgorithm(), False),
        ("Connected components", ConnectedComponentsAlgorithm(), False),
        ("SCC", SCCAlgorithm(), True),
        ("Cycle detection", CycleDetectionAlgorithm(), True),
        ("Bipartite", BipartiteTestAlgorithm(), False),
    )
    for name, algo, directed in cases:
        kwargs = {"mode": "all"} if name == "BFS_ALL" else {}
        out = []
        for cls in (AdjacencyListGraph, AdjacencyMatrixGraph):
            out.append(algo.execute(make(cls, edges, directed=directed), **kwargs).primary_output)
        show(name, f"list == matrix? {out[0] == out[1]}   -> {out[0]}")

    # ------------------------------------------------------------------ 11
    section("Complexity evidence: O(V+E) for the list, O(V^2) for the matrix",
            "Executed-line counts inside the representation code while running BFS on a sparse path graph.")
    print(f"  {'V':>5} {'list':>10} {'matrix':>12}")
    base = None
    for n in (50, 100, 200, 400):
        a, b = count_lines(AdjacencyListGraph, n), count_lines(AdjacencyMatrixGraph, n)
        print(f"  {n:>5} {a:>10,} {b:>12,}")
        base = base or (a, b)
    print("\n  -> doubling V doubles the list's work (linear) but quadruples the matrix's (quadratic).")

    # ------------------------------------------------------------------ 12
    section("Summary and honesty note",
            "What is done, and what is not claimed.")
    print("  Implemented : FR-01..FR-20, NFR-01..NFR-08, NFR-11, NFR-12 (see docs/WORKLET1_FINAL_REPORT.md)")
    print("  Pending     : NFR-09 file format sign-off by Worklet 2/3; NFR-10 shared git repository")
    print("  Proposed    : Graph.edge_weight(), metadata['component_map']  (not yet agreed with other worklets)")
    print("  Not built   : traversal-animation step data (open question for Worklet 3)")
    print("  Limitation  : recursive DFS/SCC/cycle detection hit Python's recursion limit near 1000-deep graphs")
    print("\nDemo finished.")


if __name__ == "__main__":
    main()
