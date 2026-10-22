# Worklet 1 — Implementation Plan

Phase 0 deliverable. Describes the architecture, file-by-file contents, test strategy and the exact work per phase. Nothing here is implemented yet. Decision IDs (`D-xx`, `X-xx`) refer to `DECISIONS_PENDING.md`; requirement IDs refer to `REQUIREMENTS_TRACEABILITY.md`.

## 1. Starting point (observed)

* Project folder: `D:\Mini Project Worklet 1 Graph Algorithm Explorer`
* It contains only the three reference documents. No code, tests, configuration or README exist, and it is not a git repository.
* Toolchain available in the session shell: Python 3.10.12 (meets the 3.10 minimum). `pytest` is **not installed** in the session shell (checked at the end of Phase 0); Phase 1 will install it with pip and report the result. `ruff`, `mypy`, `pytest-cov` have not been checked yet (D-21).
* Timeline context from the Guidelines: worklet reviews on 3 Oct and **17 Oct**, integration review 24 Oct. The phase sequence is deliberately small-step so each phase leaves a working, tested state.

## 2. Architecture

Four layers, as in §6.2 of the design. Each layer calls only the one below through its public interface.

```
Application / I-O      EdgeListLoader, demo entry point
Algorithm              BFS, DFS, ConnectedComponents, SCC, CycleDetection,
                       TopologicalSort, BipartiteTest  -> AlgorithmResult
Representation         AdjacencyListGraph, AdjacencyMatrixGraph
Graph model            Vertex, Edge, Graph (ABC), exceptions
```

Rules that hold in every phase:

1. Algorithms import only `Graph`, the exceptions, `Algorithm` and `AlgorithmResult`. They never import `adj_list`/`adj_matrix` and never touch `_adj`, `_matrix`, `_index`, `_vertices` (FR-19). An automated test enforces this.
2. Both representations satisfy one behavioural contract. A single contract test module is parameterised over both classes (`GraphClass` fixture).
3. Algorithms that need extra structure (for example Kosaraju's transpose, Kahn's in-degree) build it locally from `vertices`, `neighbours()` and, where the design says so, `all_edges()`.
4. Validation happens before mutation; a failed operation leaves the graph unchanged (D-19).
5. Iteration order is always insertion order; nothing sorts vertex IDs (D-06).
6. Nothing outside Worklet 1 scope is built (no Dijkstra, Bellman–Ford, MST, metrics, colouring, drawing, animation, mazes, benchmarks).

## 3. Target file layout

Inside the project folder (adapted from §6.3, adaptations justified in D-16):

```
<project root>/
  pyproject.toml          # python>=3.10, pytest config, optional dev tools
  pytest.ini              # (or pytest config inside pyproject)
  requirements-dev.txt    # pytest (+ optional ruff, mypy, pytest-cov)
  worklet1/
    __init__.py
    graph/        __init__.py  base.py  exceptions.py  adj_list.py  adj_matrix.py
    algorithms/   __init__.py  base.py  bfs.py  dfs.py  connected_components.py
                  scc.py  cycle_detection.py  topological_sort.py  bipartite.py
    io/           __init__.py  edge_list_loader.py
    tests/        conftest.py + test_graph_base.py test_adj_list.py test_adj_matrix.py
                  test_edge_list_loader.py test_bfs.py test_dfs.py
                  test_connected_components.py test_scc.py test_cycle_detection.py
                  test_topological_sort.py test_bipartite.py
                  + test_architecture.py (import/internals/docstring checks)
                  + test_integration.py, test_properties.py (Phases 2 and 7)
    sample_graphs/ *.edgelist  (+ README describing the format)
    design/       design_decisions.md  interfaces.md
    docs/         REQUIREMENTS_TRACEABILITY.md  IMPLEMENTATION_PLAN.md  DECISIONS_PENDING.md
                  COMPLEXITY.md  DEMO.md  VIVA_PREP.md  WORKLET1_FINAL_REPORT.md
    demo.py       # small runnable demonstration (Phase 8)
    README.md
```

The extra test files (`test_architecture.py`, `test_integration.py`, `test_properties.py`) are additions to the required list; they exist to verify FR-19, NFR-02, NFR-05 and the mathematical properties required by master prompt §9.

## 4. Component specifications

**`graph/base.py`** — `Vertex` (frozen dataclass: `id`, optional `data`; not used in the API, D-22). `Edge` (dataclass: `src`, `dst`, `weight`). `Graph(ABC)` with constructor `(directed=False, weighted=False)`, properties `is_directed`, `is_weighted`, `vertices`, and abstract methods from Fig. 4: `add_vertex`, `remove_vertex`, `add_edge(u, v, weight=None)`, `remove_edge`, `has_edge`, `neighbours`, `all_edges`, `vertex_count`, `edge_count`, plus PROPOSED `edge_weight` (X-01). No algorithm logic. Common validation helpers (vertex ID type, weight policy) live here so both representations behave identically.

**`graph/exceptions.py`** — hierarchy from D-05.

**`graph/adj_list.py`** — `dict[vertex, list[Edge]]`; undirected edges stored in both lists (self-loop once); duplicate check by `has_edge`; `remove_vertex` removes incident edges in both directions, O(V+E).

**`graph/adj_matrix.py`** — `_vertices` list, `_index` dict, `_matrix` list of lists with `None` = no edge; `1` as the unweighted presence marker, translated to `None` at the interface (D-19); `remove_vertex` deletes row and column and re-indexes.

**`algorithms/base.py`** — `Algorithm(ABC)` with `name` property and `execute(graph, **kwargs)`; `AlgorithmResult` dataclass with `algorithm`, `primary_output`, `metadata`, `success`, `error_message`.

**Algorithms** — each as in §8 and §9.1, with the choices recorded in D-01, D-03, D-04, D-11, D-13, D-14, D-15:

| Module | Class | Key points |
|---|---|---|
| `bfs.py` | `BFSAlgorithm`; functions `bfs`, `bfs_all` | `deque`, FIFO; start validation; `parent` metadata; `BFS_ALL` restarts in `graph.vertices` order |
| `dfs.py` | `DFSAlgorithm`; functions `dfs`, `dfs_all` | Recursive pre-order; recursion limit documented |
| `connected_components.py` | `ConnectedComponentsAlgorithm` | Repeated BFS using shared helper (the design's `bfs_from` is undefined there; implemented privately in `bfs.py`) |
| `scc.py` | `SCCAlgorithm` | Kosaraju; transpose built locally as a reverse-adjacency dict; canonical ordering |
| `cycle_detection.py` | `CycleDetectionAlgorithm` | Undirected parent rule; directed visited + rec_stack; self-loop = cycle |
| `topological_sort.py` | `TopologicalSortAlgorithm` | Kahn; `success=False` with message on cycle; `ValueError` if undirected |
| `bipartite.py` | `BipartiteTestAlgorithm` | BFS 2-colouring over all components; `ValueError` if directed |

**`io/edge_list_loader.py`** — `EdgeListLoader.load(filepath)` (static method) per §9.2 and D-20; `EdgeListFormatError(ValueError)` includes line number.

## 5. Test strategy

* pytest, one test file per module (§12), plus the three extra files listed above.
* **Parameterisation:** every graph and algorithm test runs against both `AdjacencyListGraph` and `AdjacencyMatrixGraph`.
* **Contract tests:** shared behaviour of the two representations is defined once and run twice.
* **Mathematical properties** (master prompt §9), checked on hand-built and seeded random graphs (stdlib `random` with fixed seeds; no extra libraries):
  * undirected adjacency symmetry; `edge_count == len(all_edges())`; handshake property (sum of degrees = 2E for loop-free undirected graphs);
  * list and matrix representations return identical `vertices`, `neighbours`, `all_edges`, `edge_count` after the same sequence of operations;
  * BFS distances equal an independently computed reference; DFS visits exactly the vertices reachable from start;
  * connected components and SCCs form a partition (disjoint, covering); SCC checked against an independent mutual-reachability oracle written in the test;
  * topological order valid for every edge; a graph has a cycle iff its topological sort fails (directed);
  * bipartite colouring valid for every edge when `True`; for small graphs `True` iff a brute-force search finds no odd cycle.
* **Negative tests:** every `ValueError`, `TypeError`, `VertexNotFoundError`, `EdgeNotFoundError`, `EdgeAlreadyExistsError`, `FileNotFoundError` path in §11 and D-xx.
* **Architecture tests:** algorithms contain no reference to representation internals or concrete graph classes; a minimal stub `Graph` subclass runs every algorithm; third-party-import scan; docstring presence on public API; `import io` still resolves to the stdlib.
* **Complexity check (NFR-12):** count operations (neighbour-list entries scanned / matrix cells scanned) for growing graphs and assert linear-in-(V+E) for the list and quadratic-in-V for the matrix. Wall-clock timing is not used as evidence because it is noisy.
* **Honest reporting:** the number of tests, pass/fail counts and any skipped checks are reported exactly as printed by the runner.

## 6. Phase plan

Each phase ends by running the full test suite and stopping for `CONTINUE`.

| Phase | Builds | Tests added | Exit criteria |
|---|---|---|---|
| 1 | Folder scaffold, package markers, config, `Vertex`, `Edge`, exceptions, `Graph` ABC (incl. PROPOSED `edge_weight`), `Algorithm`, `AlgorithmResult`; test infrastructure (`conftest.py`, `GraphClass` fixture); one tiny end-to-end test using a minimal stub graph | `test_graph_base.py` (ABC cannot be instantiated, model classes, exceptions), result/interface tests, architecture import checks | `python -c "import worklet1…"` works; suite green; stub `Graph` instantiable only when complete |
| 2 | `AdjacencyListGraph`, `AdjacencyMatrixGraph`, all editing/query operations | Shared contract tests run on both; per-class tests; seeded random cross-representation equivalence | FR-01…FR-08 evidence; E-04…E-06, E-15, E-16 |
| 3 | `EdgeListLoader`, `EdgeListFormatError`, `sample_graphs/*.edgelist` (valid and malformed), format description | `test_edge_list_loader.py` | FR-09, FR-10; E-12…E-14; loader works into both representations |
| 4 | `bfs.py`, `dfs.py` with single and all modes | `test_bfs.py`, `test_dfs.py` | FR-11, FR-12, FR-18; NFR-07, NFR-08; T-03, T-04 |
| 5 | `connected_components.py`, `scc.py`, `cycle_detection.py` | Three test files plus partition and oracle property tests | FR-13…FR-15; T-05, T-06, T-11 |
| 6 | `topological_sort.py`, `bipartite.py` | Two test files plus validity properties | FR-16, FR-17; T-07…T-10; E-08…E-11 |
| 7 | Integration: end-to-end load → run → inspect; architecture checks complete; docstring check; complexity instrumentation; fix any defects found; run every available quality tool | `test_integration.py`, `test_properties.py`, `test_architecture.py` completion | Full suite green; requirements matrix statuses updated from real results; defect list reported |
| 8 | README, `design/design_decisions.md` (DD-01…DD-08 + additions), `design/interfaces.md` (with PROPOSED/PENDING labels), `docs/COMPLEXITY.md`, `docs/DEMO.md`, `docs/VIVA_PREP.md`, `demo.py` | Doc-vs-code consistency checks (documented public names exist; README commands actually run) | Every documented feature exists or is labelled proposed/pending; README setup steps executed from a clean virtualenv |
| 9 | Per-requirement audit against evidence; `docs/WORKLET1_FINAL_REPORT.md` with categories Verified / Partial / Failed / Blocked / Unverified / Pending-agreement; known limitations | Final full run | No compliance claim without evidence; NFR-09, NFR-10 and cross-worklet items reported as pending/blocked unless you supply evidence |

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Spec contradictions (D-01, D-02, D-03) lead to a design that another team does not expect | Defaults are literal-spec-first; all are in the register; interface doc will list them for W2/W3 |
| `io` package name shadows stdlib | D-16: package-qualified imports, config at project root, guard test |
| Recursion limit on deep graphs | D-12: documented, tested at a known size, no silent crash claims |
| Undirected `all_edges()` semantics differ from what W2/W3 assume | D-02 stated explicitly in the interface doc as an item for them to confirm |
| NFR-09/NFR-10 and cross-worklet items cannot be proven from inside Worklet 1 | Reported as pending/blocked rather than verified |
| Tool availability (pytest, linters) in the session shell | Checked at Phase 1; absent tools are reported as "not run" |
| Evaluation date 17 Oct is close | Phases are independent and each leaves a runnable, tested state, so work can stop after any phase and still be demonstrable |

## 8. What happens next

Nothing is implemented. On `CONTINUE`, Phase 1 will be executed alone (scaffold and abstractions), tested, and reported, and then I will stop again.
