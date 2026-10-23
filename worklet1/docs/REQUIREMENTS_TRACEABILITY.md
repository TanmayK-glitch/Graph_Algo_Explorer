# Worklet 1 — Requirements Traceability Matrix

**Project:** COEP Mini Project 9 — Graph Algorithms Explorer, Worklet 1 (Graph Model, Traversal and Connectivity)
**Primary specification:** `Worklet1_Week3_Design_Document_last(5).docx` (dated 29 Aug 2026)
**Supporting references:** `Graph Algorithms Explorer Guidelines(2).pdf`, `Mini Project Graph Algorithms Explorer(1).pdf`
**Document status:** updated after Phase 9. Statuses in Parts A and B reflect actual results of the final run (984 tests passed; ruff and mypy clean); Parts C-G list the planned tests, all of which exist in `tests/` (see `WORKLET1_FINAL_REPORT.md`).

Section numbers (§) refer to the design document unless stated otherwise.
`D-xx` / `X-xx` entries refer to the register in `DECISIONS_PENDING.md`.

Status vocabulary (used from Phase 9): **Verified**, **Partial**, **Failed**, **Blocked**, **Unverified**, **Pending-agreement**.

---

## Part A — Functional requirements (§5.1)

| ID | Requirement (from §5.1) | Design source | Planned implementation | Phase | Verification evidence (planned) | Status |
|---|---|---|---|---|---|---|
| FR-01 | Create a graph as either an adjacency list or an adjacency matrix | §6.4, §7, Fig. 4 | `AdjacencyListGraph`, `AdjacencyMatrixGraph` behind `Graph` ABC | 2 | `test_adj_list.py`, `test_adj_matrix.py`, shared contract tests run on both classes | **Verified** - test_graph_base.py (contract x2), test_adj_list.py, test_adj_matrix.py |
| FR-02 | Directed and undirected graphs in both representations | §7.1–7.3 | `directed` flag in both classes; undirected stores both directions | 2 | Contract tests: directed A→B has `has_edge(B,A)==False`; undirected symmetry property | **Verified** - test_graph_base.py directed/undirected/symmetry tests; test_properties.py symmetry+handshake (80 cases) |
| FR-03 | Weighted edges in both representations | §7.3, §5.4 | `weighted` flag; weight stored as float; unweighted → `Edge.weight=None` | 2 | Weight 3.5 round-trips; unweighted weight is `None` in both classes; negative weights accepted (D-07, D-08) | **Verified** - test_graph_base.py weight tests incl. negative/zero; DD-11 policy |
| FR-04 | Add a vertex | §7.1, §7.2 | `add_vertex` | 2 | Contract test; isolated vertex; duplicate-vertex behaviour (D-09) | **Verified** - test_graph_base.py add_vertex/isolated/invalid ids |
| FR-05 | Remove a vertex and all incident edges | §7.1, §11 | `remove_vertex`; raises `VertexNotFoundError` if absent | 2 | Incident-edge removal in directed (in and out edges) and undirected graphs; edge-count invariant | **Verified** - test_graph_base.py remove_vertex directed/undirected/missing |
| FR-06 | Add an edge with an optional weight | §7.1, §7.2, §11 | `add_edge(u, v, weight=None)`; auto-creates missing vertices; rejects duplicates | 2 | Auto-create, duplicate rejection (`EdgeAlreadyExistsError`), self-loop, weight policy (D-07) | **Verified** - test_graph_base.py auto-create, duplicate, self-loop, atomic failure |
| FR-07 | Remove an edge | §11 | `remove_edge`; raises `EdgeNotFoundError` if absent | 2 | Undirected removal clears both directions; missing edge raises | **Verified** - test_graph_base.py remove_edge directed/undirected/missing |
| FR-08 | Query neighbours of a vertex | §7.1 contract | `neighbours(v)` → vertex IDs, insertion order, `VertexNotFoundError` if absent | 2 | Order determinism; identical result in both representations | **Verified** - test_graph_base.py neighbour order; test_properties.py equivalence |
| FR-09 | Load a graph from an edge-list file | §9.2 | `EdgeListLoader.load(filepath)` | 3 | `test_edge_list_loader.py` with fixtures in `sample_graphs/` | **Verified** - test_edge_list_loader.py (valid fixtures, both representations). Format itself is PROPOSED (X-02) |
| FR-10 | Clear error for malformed or missing file | §9.2, §11 | `FileNotFoundError`; `ValueError` with line number | 3 | One test per malformed case listed in §11 plus extra cases in D-20 | **Verified** - test_edge_list_loader.py (8 malformed fixtures with exact line numbers, empty, missing file, case, order) |
| FR-11 | BFS from a start vertex, returning visit order | §8.1 | `BFSAlgorithm` (deque, FIFO) | 4 | Order tests on both representations; BFS-level / shortest-distance property | **Verified** - test_bfs.py; test_properties.py BFS distance/parent checks vs independent reference |
| FR-12 | DFS from a start vertex, returning visit order | §8.2 | `DFSAlgorithm` (recursive, call stack) | 4 | Order tests on both representations; reachability property | **Verified** - test_dfs.py (incl. iterative variant); test_properties.py reachability |
| FR-13 | All connected components of an undirected graph | §8.3 | `ConnectedComponentsAlgorithm` | 5 | Partition property (disjoint, covering); isolated vertices; directed-input policy (D-01) | **Verified** - test_connected_components.py; test_properties.py partition oracle |
| FR-14 | All strongly connected components of a directed graph | §8.4 | `SCCAlgorithm` (Kosaraju) | 5 | Partition property; independent mutual-reachability oracle in tests; `ValueError` on undirected | **Verified** - test_scc.py; test_properties.py mutual-reachability oracle (80 cases) |
| FR-15 | Detect whether a graph contains a cycle | §8.5 | `CycleDetectionAlgorithm` (undirected parent test; directed visited + rec_stack) | 5 | Cross-edge (no cycle) vs back-edge cases; self-loops; consistency with topological sort | **Verified** - test_cycle_detection.py; test_properties.py oracles (directed closure, undirected |E|=|V|-C) |
| FR-16 | Valid topological order for a DAG; report none exists if cyclic | §8.6 | `TopologicalSortAlgorithm` (Kahn) | 6 | Ordering-validity property (every edge u→v has u before v); `success=False` on cycle; `ValueError` on undirected | **Verified** - test_topological_sort.py; test_properties.py order validity and cycle iff failure |
| FR-17 | Bipartite test with 2-colouring; reject directed graphs | §8.7 | `BipartiteTestAlgorithm` (BFS 2-colouring) | 6 | Colouring validity property; odd-cycle graphs; disconnected; `ValueError` on directed (X-05) | **Verified** - test_bipartite.py; test_properties.py brute force over all 2-colourings |
| FR-18 | `BFS(start)`/`DFS(start)` cover only start's component; `BFS_ALL`/`DFS_ALL` cover every vertex by restarting | §8.1, §8.2, §5.4 | Single-component mode and full-graph mode (shape in D-03) | 4 | Disconnected-graph tests asserting both modes | **Verified** - test_bfs.py, test_dfs.py (single vs ALL modes, disconnected). API shape is D-03 |
| FR-19 | Algorithms use only the shared Graph interface, never concrete internals | §6.2, §8 intro | Algorithms import only `Graph`, `Algorithm`, `AlgorithmResult` and exceptions | 1 (contract), 7 (check) | Automated static test scanning `algorithms/` sources for `_adj`, `_matrix`, `_index`, concrete class imports; stub-Graph test | **Verified** - test_architecture.py AST scan (7 algorithm files), stub-graph test |
| FR-20 | `AlgorithmResult` with at least algorithm name, primary output, metadata | §9.1 | `@dataclass AlgorithmResult(algorithm, primary_output, metadata, success, error_message)` | 1 | Construction/default tests; every algorithm returns it | **Verified** - test_graph_base.py defaults; every algorithm test checks the fields |

## Part B — Non-functional requirements (§5.2)

| ID | Requirement | Planned implementation | Phase | Verification evidence (planned) | Status |
|---|---|---|---|---|---|
| NFR-01 | Python 3.10+, no prohibited libraries | Stdlib only for the library; `pytest` as test tool; `python_requires>=3.10` | 1 | Import scan test for third-party/graph-library imports; run on Python 3.10 | **Verified** - test_architecture.py stdlib-only import scan; clean-room run on Python 3.10.12 |
| NFR-02 | Representation separated from algorithm logic | Same as FR-19 plus parameterised tests over both classes | 7 | Same-result-on-both-representations tests; randomised cross-representation comparison | **Verified** - test_properties.py list-vs-matrix equivalence (40x2) and algorithm equality; stub graph |
| NFR-03 | Each algorithm is a self-contained, replaceable module (strategy pattern) | One `Algorithm` subclass per module with `execute(graph, **kwargs)` | 1, 4–6 | Test that all algorithms are interchangeable through the `Algorithm` interface | **Verified** - test_architecture.py strategy-interchangeability test |
| NFR-04 | Modules named `graph/`, `algorithms/`, `io/` | Layout from §6.3 | 1 | Directory/import check | **Verified** - test_architecture.py layout test |
| NFR-05 | Docstrings on all public functions and classes | Written with each module | 1–8 | Automated docstring-presence test over public API (`inspect`/`ast`) | **Verified** - test_architecture.py AST docstring check over all public modules/classes/functions |
| NFR-06 | At least one unit test per algorithm and graph operation | Test file per module (§6.3, §12) | 1–7 | Operation-to-test coverage table (Phase 7) plus coverage run if `pytest-cov` is available | **Verified** - every operation and algorithm has dedicated tests (984 total) |
| NFR-07 | BFS uses a queue, not a stack or recursion | `collections.deque`, `popleft` | 4 | Code review; FIFO-order test; no recursion in `bfs.py` | **Verified** - test_architecture.py (deque/popleft, no recursion in bfs.py), FIFO order tests |
| NFR-08 | DFS uses a stack, explicit or via recursion | Recursive (call stack) per §8.2 | 4 | Code review; deep-graph behaviour documented (D-12) | **Verified** - test_architecture.py (recursive _visit), test_dfs.py |
| NFR-09 | Edge-list format identical across all three worklets | Format v1 implemented as proposed; **cannot be confirmed by Worklet 1 alone** | 3, 8 | Format spec doc and fixtures supplied to W2/W3 — approval requires evidence from them (X-02) | **Pending-agreement** - implemented as proposed; no sign-off from W2/W3 (X-02). W1 cannot verify it alone |
| NFR-10 | Small meaningful commits in one shared team repository | Commit discipline only if the user supplies/initialises a repo | — | The project folder currently has **no git repository** (observed Phase 0). Cannot be verified without one (D-18) | **Blocked** - folder is not a git repository; nothing committed |
| NFR-11 | Design decisions and trade-offs in a decision log | `design/design_decisions.md` (DD-01…DD-07 from §10, plus additions) | 8 | Log exists and every DD maps to code or doc | **Verified** - design/design_decisions.md (DD-01..DD-17) |
| NFR-12 | O(V+E) list traversal, O(V²) matrix traversal | Natural cost of `neighbours()` in each representation | 7 | Operation-count instrumentation across growing graphs (not wall-clock timing) | **Verified** - test_complexity.py operation counts: list ratio ~2.0, matrix ratio ~4.0 per doubling of V (docs/COMPLEXITY.md) |

## Part C — Edge cases and error conventions (§11)

| ID | Situation (§11) | Expected behaviour | Phase | Planned test |
|---|---|---|---|---|
| E-01 | Empty graph | All algorithms return an empty result, no exception (interpretation in D-14) | 4–6 | Each algorithm on empty graph, both representations |
| E-02 | Single vertex, no edges | BFS/DFS `[v]`; components `[[v]]`; no cycle | 4–5 | Per-algorithm tests |
| E-03 | Isolated vertices | Singleton components; included in full-graph traversal | 4–5 | Isolated-only graph |
| E-04 | `add_edge` with unknown vertex | Vertex auto-created | 2 | Contract test |
| E-05 | `remove_vertex` on missing vertex | `VertexNotFoundError` | 2 | Contract test |
| E-06 | `remove_edge` on missing edge | `EdgeNotFoundError` | 2 | Contract test |
| E-07 | BFS/DFS on disconnected graph | Single mode = start's component; ALL mode = every component | 4 | Disconnected-graph tests |
| E-08 | Topological sort with a cycle | `success=False`, `primary_output=None`, error message | 6 | A→B→A, self-loop, longer cycles |
| E-09 | Topological sort on undirected graph | `ValueError` | 6 | Test |
| E-10 | Bipartite test on directed graph | `ValueError` | 6 | Test |
| E-11 | Bipartite on disconnected graph | Every component tested; any failure ⇒ non-bipartite | 6 | Mixed bipartite/non-bipartite components |
| E-12 | Malformed edge-list file | `ValueError` naming the line number | 3 | Parameterised malformed fixtures |
| E-13 | Missing edge-list file | `FileNotFoundError` | 3 | Test |
| E-14 | Missing weight in a WEIGHTED file | `ValueError` | 3 | Test |
| E-15 | Self-loop | Accepted; counted as a cycle in both directed and undirected detection | 2, 5 | Graph + cycle tests; bipartite consequence in D-15 |
| E-16 | Duplicate edge | `EdgeAlreadyExistsError` via `has_edge` check | 2 | Directed, undirected, reversed-pair undirected |

## Part D — Representative test cases already in the design (§12.2)

| ID | Case | Expected | Phase |
|---|---|---|---|
| T-01 | Directed edge A→B | `has_edge(A,B)` True, `has_edge(B,A)` False | 2 |
| T-02 | Weighted edge A–B, weight 3.5 | Stored weight 3.5 | 2 |
| T-03 | Disconnected graph, `bfs_all` | A and B first, then C via restart | 4 |
| T-04 | Back edge A–B–C–A under DFS | All vertices visited; DFS does not report a cycle | 4 |
| T-05 | A–B, C–D connected components | `[[A,B],[C,D]]` | 5 |
| T-06 | Directed cross edges A→B, A→C, B→D, C→D | No cycle | 5 |
| T-07 | Diamond DAG | A first, D last | 6 |
| T-08 | A→B→A topological sort | `success=False` | 6 |
| T-09 | Triangle bipartite test | False | 6 |
| T-10 | Disconnected A–B, C–D bipartite | True | 6 |
| T-11 | SCC of A→B→A, C→D | `[[A,B],[C],[D]]` (ordering rule in D-11) | 5 |

## Part E — Interface and contract statements (§7, §9)

| ID | Statement | Source | Phase | Notes |
|---|---|---|---|---|
| I-01 | `Graph` exposes `is_directed`, `is_weighted`, `vertices`, `add_vertex`, `remove_vertex`, `add_edge`, `remove_edge`, `has_edge`, `neighbours`, `all_edges`, `vertex_count`, `edge_count` | §7 Fig. 4 | 1 | Agreed in §9.3/§9.4 |
| I-02 | `edge_weight(u, v) -> float | None` | §7 Fig. 4, §9.3 | 1–2 | **Proposed, not agreed** (X-01). Label as proposed everywhere |
| I-03 | `neighbours(v)` returns vertex IDs in insertion order; raises `VertexNotFoundError` | §7.1 | 2 | |
| I-04 | `Algorithm.execute(graph, **kwargs) -> AlgorithmResult`; `name` property | §9.1 | 1 | |
| I-05 | Result shapes per algorithm (BFS/DFS list; components list of lists plus `count`; cycle bool; topo list or None plus `has_cycle`; bipartite bool plus `colouring`) | §9.1 table | 4–6 | BFS `parent` key discrepancy in D-04 |
| I-06 | SCC and topological sort need directed; bipartite needs undirected; all raise `ValueError` otherwise | §9.1 | 5–6 | |
| I-07 | W3 metadata: `colouring` map | §9.4 | 6 | Agreed |
| I-08 | W3 metadata: `component_map` for component/SCC results | §9.4 | 5 | **Pending** (X-03) |
| I-09 | W3 animation step data | §9.4 | — | **Pending** (X-04); not implemented unless agreed |
| I-10 | Edge-list format v1 | §9.2 | 3 | **Proposed**, pending W2/W3 sign-off (X-02) |

## Part F — Constraints from the supporting documents

| ID | Constraint | Source | Handling |
|---|---|---|---|
| C-01 | No NetworkX, igraph, graph DBs, web frameworks, cloud services, or ML/AI libraries | Guidelines §3; Overview PDF; master prompt §3 | Stdlib only; automated import scan (NFR-01) |
| C-02 | Hand-built representations and algorithms | Same | No third-party graph code |
| C-03 | Queues for BFS, stacks for DFS, hash maps for visited | Guidelines §3 | NFR-07/08 |
| C-04 | Strategy pattern; representation separated from traversal; pluggable representations | Guidelines §3 | NFR-02/03 |
| C-05 | Worklet 2 (Dijkstra, Bellman–Ford, MST) and Worklet 3 (metrics, colouring, visualisation, animation, mazes, benchmarks) are **out of scope** | §4.2; Guidelines §4 | Not implemented; interfaces prepared only |
| C-06 | Individual viva readiness: every design decision explainable | Guidelines §1, §9 | `docs/VIVA_PREP.md` in Phase 8 |
| C-07 | Test edge cases early: disconnected graph, negative weight, graph with a cycle | Guidelines §9 | Included in test plan (negative weights accepted by the model, D-08) |
| C-08 | Pitfall: cycle detection with a single visited set | Guidelines §10 | Directed detection uses visited + rec_stack (DD-06) |
| C-09 | Pitfall: matrix used on sparse graphs | Guidelines §10 | List is the default representation (DD-02) |
| C-10 | Pitfall: reporting BFS as shortest path on weighted graphs | Guidelines §10 | Documentation states BFS minimises edge count only |
| C-11 | Shared repo with small frequent commits; a build that runs for all members; tiny end-to-end test | Guidelines §5 | NFR-10 blocked pending repo; end-to-end test in Phase 1 |
| C-12 | Python 3.10 or later; reproducible setup and execution | Master prompt §3 | `pyproject.toml`/`requirements-dev.txt`, README steps tested in Phase 8 |
| C-13 | Evaluation dates in the Guidelines: worklet reviews 19 Sep, **3 Oct, 17 Oct**; integration 24 Oct; final viva 4–6 Nov | Guidelines §6 | Schedule pressure noted in the implementation plan |

## Part G — Deliverables checklist (Appendix A of the design, plus master prompt §4G)

| ID | Deliverable | Phase |
|---|---|---|
| DL-01 | Requirements note FR-01…FR-20, NFR-01…NFR-12 | 0 (this file) |
| DL-02 | Module decomposition and architecture | 0, 1 |
| DL-03 | Interface definitions: Graph ABC, Algorithm ABC, AlgorithmResult, EdgeListLoader | 1, 8 (`design/interfaces.md`) |
| DL-04 | Edge-list format specification (pending agreement) | 3, 8 |
| DL-05 | Design decision log (design says DD-01…DD-08; the design body defines DD-01…DD-07 — D-17) | 8 |
| DL-06 | W1–W2 and W1–W3 interface agreements, documented | 8 — documented as **pending** unless evidence is provided |
| DL-07 | Test suite | 1–7 |
| DL-08 | README with build instructions | 8 |
| DL-09 | Sample graph fixtures | 3 |
| DL-10 | Complexity analysis | 8 |
| DL-11 | Demonstration procedure | 8 |
| DL-12 | Viva preparation material | 8 |
| DL-13 | `WORKLET1_FINAL_REPORT.md` | 9 |
