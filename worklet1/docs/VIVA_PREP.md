# Viva preparation - Worklet 1

Each answer is short on purpose; know where the code is.

**1. When is an adjacency matrix better than a list?** Dense graphs or many O(1) edge lookups (Floyd-Warshall, triangles).
Sparse graphs and traversal: list, O(V+E) space and work. Measured: `docs/COMPLEXITY.md` (matrix did ~100x the work at V=400).

**2. Why does BFS give shortest paths in an unweighted graph?** FIFO dequeues vertices in non-decreasing distance; the first
time a vertex is discovered is via the fewest edges. The `parent` map is the shortest-path tree
(`test_properties.py` checks the hop counts against an independent BFS). It fails once edges have different weights.

**3. Why can't one visited set detect directed cycles?** It cannot separate a back edge (neighbour still on the current path:
`rec_stack`) from a cross/forward edge to a finished vertex. `cycle_detection.py::has_cycle_directed`; test: A->B, A->C, B->D, C->D has no cycle.

**4. Why does Kosaraju transpose the graph?** Finish order of pass 1 puts a source SCC last; in the transpose, edges between SCCs
point the other way, so DFS from the highest finish time cannot leave its own SCC. Why not Tarjan: one pass and faster, but harder to explain; our choice DD-08.

**5. Prove: bipartite iff no odd cycle.** Bipartite => every edge crosses the parts => cycles alternate => even length.
No odd cycle => BFS levels: an edge inside one level would close an odd cycle with the two tree paths to the common ancestor, so
2-colouring by level parity never conflicts. Our test detects it: `test_bipartite_matches_brute_force` compares against all 2^n colourings;
a self-loop is an odd cycle of length 1.

**6. Why separate representation from algorithms?** Algorithms call `vertices`, `neighbours`, `all_edges` only; swapping
representations changes nothing (`test_algorithms_identical_on_both_representations`, `test_every_algorithm_runs_on_a_stub_graph`,
AST scan in `test_architecture.py`).

**7. Why Kahn over DFS post-order for topological sort?** A cycle shows up as fewer outputs than vertices - no extra bookkeeping.
Topological order of a cycle contradicts itself (A before B before C before A).

**8. Why does `neighbours` use vertex-creation order?** A matrix cannot remember edge insertion order; one shared rule makes both
representations return identical results (DD-09).

**9. Why can the graph hold negative weights?** The model is sign-agnostic; Dijkstra (Worklet 2) must reject them itself
(Dijkstra's greedy settling is wrong with negative edges; Bellman-Ford relaxes V-1 times and detects negative cycles).

**10. Known weaknesses (say them first):** recursion limit at ~1000 deep (DFS has an opt-in iterative mode; cycle detection and SCC do not); list `edge_weight` is O(degree); cross-worklet items
(`edge_weight`, file format, `component_map`, animation data) are proposals, not agreements; no git history in this folder.

**Where things are:** `graph/base.py` (contract), `adj_list.py`, `adj_matrix.py`, `algorithms/*.py`, `io/edge_list_loader.py`, decisions in `design/design_decisions.md`.
