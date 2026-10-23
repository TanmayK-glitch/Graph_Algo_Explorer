# Worklet 1 — Unresolved Decisions Register

Phase 0 status. Nothing here has been approved by anyone yet.

Two kinds of entry:

* **X-xx — Cross-worklet agreements.** The design document itself marks these as proposed or pending. Worklet 1 may implement its own proposal, but it will be labelled **PROPOSED** in code, README and interface docs. No document will claim that Worklet 2, Worklet 3 or the faculty approved it unless evidence is provided.
* **D-xx — Gaps, ambiguities and inconsistencies inside the design document, plus project-setup choices.** Each has a **Default** that Phase 1 onward will use if you do not object. Defaults are chosen to follow the design document literally wherever it is explicit, and to be the smallest change otherwise. Any default can be reversed in the phase where it is first used.

"Needed by" is the earliest phase that is affected.

---

## X — Cross-worklet agreements (proposed, not approved)

| ID | Item | Source | Current status | Worklet 1 plan | Needed by |
|---|---|---|---|---|---|
| X-01 | `Graph.edge_weight(u, v) -> float \| None` (O(1) lookup for Dijkstra). Returns `None` if the edge is absent or the graph is unweighted | §7 Fig. 4, §9.3 | Proposed by W1; awaiting W2 confirmation | Implement in both representations and the ABC, marked PROPOSED. It is additive, so removal later does not break `all_edges()`/`neighbours()`. Open question: if the edge is absent, `None` and "unweighted" are indistinguishable by design; callers must use `has_edge` | Phase 1 |
| X-02 | Edge-list file format v1 (header lines, `u v [weight]`, single-token isolated vertex, `#` comments) | §9.2, NFR-09 | "Team decision proposed by W1, pending sign-off from W2 and W3" | Implement exactly as proposed; format spec in `sample_graphs/` README and `design/interfaces.md` marked PROPOSED. NFR-09 cannot be marked verified by W1 | Phase 3 |
| X-03 | `metadata['component_map']` (vertex → component index) on connected-component and SCC results | §9.4 | Pending | Proposal only. Cheap to add (one dict); I would add it as an optional, clearly labelled extension. Not claimed as agreed | Phase 5 |
| X-04 | Step-by-step traversal data for animation (W1 stores a step list vs W3 re-runs with hooks) | §9.4 | Pending, no preference stated | **Not implemented.** Out of W1 scope (animation is W3). Documented as an open interface question. Optional later: a `record_steps` kwarg, only if W3 asks | Phase 8 |
| X-05 | Whether the bipartite test may run on a directed graph by ignoring edge direction | §8.7 ("unless the integrated project explicitly defines…") | Not defined | Follow FR-17 and §11: `ValueError` on directed graphs | Phase 6 |

---

## D — Gaps, ambiguities and inconsistencies in the specification

### Behaviour that affects the public interface

| ID | Issue | Evidence in the design | Options | Default (recommended) | Needed by |
|---|---|---|---|---|---|
| D-01 | **Connected components on a directed graph.** §8.3 says "defined only for undirected graphs" and FR-13 says "undirected graph", but §9.1 says "BFS, DFS, and connected components accept any graph". The two statements conflict. | §8.3, §9.1, FR-13 | (a) `ValueError` on directed graphs. (b) Accept directed graphs and compute weakly connected components (needs reverse edges built inside the algorithm). (c) Accept and run BFS on out-neighbours (wrong: result depends on vertex order) | **(a)** `ValueError`. It matches FR-13/§8.3 and the pattern used for SCC/bipartite, and avoids silently returning a mathematically wrong partition. **Please confirm**, because §9.1 literally says otherwise. | Phase 5 |
| D-02 | **What `all_edges()` and `edge_count()` return for undirected graphs.** The adjacency-list sample stores two `Edge` objects per undirected edge. The design never says whether `all_edges()` lists each undirected edge once or twice, nor how `edge_count()` counts. W2 (Kruskal/Prim) and W3 (rendering) both consume `all_edges()`. | §7.1 sample, §9.3, §9.4 | (a) Each undirected edge once, `edge_count()` = number of logical edges. (b) Both directions listed, `edge_count()` = 2×edges | **(a)**, with a deterministic orientation (the direction in which the edge was first added). Kahn's sort uses `all_edges()` only for directed graphs, so it is unaffected. Must be told to W2/W3 as part of the interface doc. | Phase 1 |
| D-03 | **How `BFS_ALL`/`DFS_ALL` are exposed.** §8.1/§8.2 show module functions `bfs_all(graph)`/`dfs_all(graph)`; §6.4 and §9.1 say every algorithm is an `Algorithm` with `execute(graph, **kwargs)`. The master prompt allows "the specified modes or their agreed equivalents". | §8.1, §8.2, §9.1 | (a) `execute(graph, start=…)` is single mode; `execute(graph)` with no start is ALL mode (implicit). (b) Explicit `mode="single"\|"all"` kwarg; `start` required for single. (c) Separate classes | **(b)** plus the module-level functions `bfs`, `bfs_all`, `dfs`, `dfs_all` exactly as in the design. Explicit mode avoids silently traversing the whole graph when `start` is forgotten. Result `algorithm` field: `'BFS'`, `'BFS_ALL'`, `'DFS'`, `'DFS_ALL'`. | Phase 4 |
| D-04 | **BFS metadata.** §8.1 code returns `{'start': start}`; the §9.1 table lists `{'start': 'A', 'parent': {...}}`. | §8.1 vs §9.1 | Include or omit `parent` | **Include `parent`** (vertex → predecessor, start → `None`). It follows the interface table, costs nothing, and directly supports the shortest-path viva question. `*_ALL` metadata stays `{}` as in the design. | Phase 4 |
| D-05 | **Exception classes.** Names `VertexNotFoundError`, `EdgeNotFoundError`, `EdgeAlreadyExistsError` appear, but base class, module and relation to `KeyError`/`ValueError` are not given ("raises KeyError *or* a custom…"). | §7.1, §11 | Various | `GraphError(Exception)` base; `VertexNotFoundError(GraphError, KeyError)`; `EdgeNotFoundError(GraphError, KeyError)`; `EdgeAlreadyExistsError(GraphError, ValueError)`. Inheriting the builtins satisfies both readings of §11. Put them in a small `graph/exceptions.py` re-exported from `graph/__init__.py` (a one-file addition to the §6.3 layout, see D-16). | Phase 1 |
| D-06 | **Vertex identifier rules.** "Integers or strings; no complex objects". Python quirks: `True == 1`, `1 == 1.0` with equal hashes, so `add_vertex(True)` and `add_vertex(1)` would collide. Mixed int/str IDs are also not mutually orderable. | §5.4 | Accept anything hashable vs validate | Accept `int` (not `bool`) and `str`; anything else raises `TypeError`. Mixed int/str is allowed (insertion order is used everywhere, never sorting). Loader produces `str` IDs only (§9.2). | Phase 1 |
| D-07 | **Weight policy on `add_edge`.** FR-06 says "optional weight". Unspecified: weighted graph with weight omitted; unweighted graph with a weight supplied. The matrix sample (`w = weight if self._weighted else 1`) would store `None` for an omitted weight on a weighted graph, which the matrix treats as "no edge", silently losing the edge. | §7.2 sample, §7.3, FR-06 | (a) Weighted graph requires a weight (`ValueError`); unweighted rejects a weight (`ValueError`). (b) Weighted default 1.0; unweighted ignores weight | **(a).** Consistent with the loader rule "weight missing in a WEIGHTED file → ValueError" and avoids silent data loss. Validation happens before any mutation. | Phase 2 |
| D-08 | **Weight type and range.** "Floats, may be negative; no restriction on sign." Not stated: ints, `bool`, NaN, infinity. | §5.4 | | Accept `int`/`float` (not `bool`), stored as `float`; reject NaN and ±inf with `ValueError`; **negative and zero weights accepted** with no restriction (Worklet 2 enforces its own). | Phase 2 |
| D-09 | **`add_vertex` on an existing vertex.** Not specified. | FR-04 | Idempotent no-op vs error | **Idempotent no-op** (the design itself calls `add_vertex` from `add_edge` for endpoints that may already exist). | Phase 2 |
| D-10 | **Invalid vertex arguments.** `has_edge(u, v)` with an unknown vertex: the samples raise a bare `KeyError`; nothing in §11. Algorithms with an unknown start vertex: §9.1 says "raise an error" without a type. Missing `start` kwarg: unspecified. | §7.1, §9.1, §11 | | `has_edge`, `edge_weight`, `remove_edge` with unknown vertex → `VertexNotFoundError` (consistent with `neighbours`). Algorithm with unknown `start` → `VertexNotFoundError`. Missing `start` in single mode → `ValueError`. | Phase 2 / 4 |
| D-11 | **Output ordering for components.** §12.2 expects SCC `[[A,B],[C],[D]]` for A→B→A, C→D. A literal Kosaraju run yields `[[C],[D],[A,B]]` (reverse finish order), so the example is not reproducible without a canonical ordering. | §12.2 T-11, §8.4 | | Canonical ordering for both CC and SCC: members of each component in `graph.vertices` order; components ordered by their earliest member's position in `graph.vertices`. This reproduces the §12.2 examples exactly and makes results deterministic and representation-independent. Tests also check partitions as sets. | Phase 5 |
| D-12 | **Recursion limit.** DFS, cycle detection and Kosaraju are recursive per §8.2/§8.5; Python's default limit (about 1000) is hit by a path graph of roughly 1000 vertices. §14 lists this as a known limitation; the design says the iterative fallback is documented, "not built by default". Target size is "a few hundred vertices". | §8.2, §11, §14 | (a) Recursive only, document limit. (b) Also provide an opt-in iterative DFS | **(a)** follow the design; document the limit and the exact failing size observed in a test. Offer (b) as a later optional extension if you want it; it would not change defaults. | Phase 4 |
| D-13 | **Algorithm names.** Result `algorithm` strings given: `BFS`, `DFS`, `BFS_ALL`, `DFS_ALL`, `ConnectedComponents`, `TopologicalSort`, `BipartiteTest`. Not given for SCC and cycle detection. | §8, §9.1 | | `SCC` and `CycleDetection`. `Algorithm.name` on `BFSAlgorithm` is `'BFS'`; ALL mode reports `'BFS_ALL'` in the result. | Phase 1 |
| D-14 | **Empty-graph results.** §11: "all algorithms return an empty result; no exception". Needs concrete values for Boolean outputs. | §11 | | BFS_ALL/DFS_ALL `[]`; components `[]` with `count 0`; cycle `False`; topological sort `[]` with `success=True`; bipartite `True` with empty `colouring`. Single-mode BFS/DFS on an empty graph has no valid start, so it raises `VertexNotFoundError`. | Phase 4 |
| D-15 | **Self-loop semantics across modules.** Stated: accepted; counted as a cycle. Implied but unstated: stored once in neighbours (the §7.1 sample would append it twice for undirected graphs); undirected `edge_count` counts it once; bipartite test returns `False` (odd cycle of length 1); directed topological sort reports a cycle; SCC treats the vertex as its own component. | §7.1, §11 | | Implement the implied behaviour above and cover each with a test. | Phase 2 / 5 / 6 |

### Project and setup choices

| ID | Issue | Default | Needed by |
|---|---|---|---|
| D-16 | **Layout adaptations.** (1) The §6.3 tree has no package marker for `worklet1/` itself. (2) The `io/` package name shadows the stdlib `io` module if `worklet1/` itself is ever put on `sys.path` (for example by running scripts from inside it). (3) Config files are not shown. (4) `graph/exceptions.py` is an addition (D-05). | Project root = your folder `D:\Mini Project Worklet 1 Graph Algorithm Explorer`. Python package = `worklet1/` with `__init__.py` (imports are `worklet1.graph`, `worklet1.io`). `pyproject.toml` and `pytest.ini` at the project root, so `worklet1/` itself never lands on `sys.path`. `tests/` stays inside `worklet1/` as in the design. The `io/` name is kept (NFR-04 requires it) with a README warning plus a test asserting `import io` still resolves to the stdlib. | Phase 1 |
| D-17 | **Documentation inconsistencies in the design document** (no code impact, to be recorded, not silently fixed): the table of contents lists Kosaraju as "Decision 3" but the body's Decision 3 is Kahn's and no Kosaraju decision exists; the DD table has DD-01…DD-07 but Appendix A expects DD-01…DD-08; §13 gives Pranav and Vedant the same MIS number 612415026 (the cover page gives Vedant 612415060); the §8.4 step list is numbered 7–10 instead of 1–4. | The decision log keeps DD-01…DD-07 as written and adds **DD-08 Kosaraju for SCC**, labelled as added by this implementation. Other items listed in the log as "noted, not changed". | Phase 8 |
| D-18 | **NFR-10 (small commits, one shared team repo).** The project folder is not a git repository and no repo URL was supplied. | I will not run `git init`, commit or push without your permission. NFR-10 is reported **Blocked** in the final audit unless you give me a repo to commit to. | Phase 9 |
| D-19 | **Matrix internals vs interface.** The matrix stores `1` as a presence marker in unweighted graphs, but the interface says unweighted `Edge.weight` is `None`. | The matrix converts: `all_edges()` and `edge_weight()` return `None` for unweighted graphs in both classes. Contract tests assert identical edge-weight semantics across the two representations. All mutations validate first, then change state, so a failed `add_edge` leaves the graph unchanged. | Phase 2 |
| D-20 | **Edge-list loader details not in §9.2.** Keyword case; trailing `# …` comments (the §9.2 example itself shows `DIRECTED # or UNDIRECTED`); what counts as a header; duplicate edges in a file; extra tokens; unparsable weights; empty file; BOM; which class to build. | Keywords upper-case only, exactly as shown (strictest form, safest for NFR-09). A `#` token begins a comment, whole-line or trailing. First two non-blank, non-comment lines must be the two headers, in that order. Single-token line = isolated vertex. Duplicate edge, wrong token count for the mode, non-numeric/NaN/inf weight, missing/invalid header, empty file → `ValueError` carrying the line number (through a `ValueError` subclass named `EdgeListFormatError`). Missing file → `FileNotFoundError`. UTF-8 with BOM tolerated. Default graph class `AdjacencyListGraph` (DD-02) with an optional keyword to choose the matrix; the required signature `EdgeListLoader.load(filepath)` still works. | Phase 3 |
| D-21 | **Tooling.** Design says pytest. Linter, type checker, coverage are optional. | `pytest` required; `ruff`, `mypy`, `pytest-cov` used only if they install cleanly; each is reported as run or not run. No other dependencies. | Phase 1 |
| D-22 | **Role of `Vertex`.** §6.4 requires `Vertex` ("an identifier and optional data") but the whole API (`vertices`, `neighbours`, algorithm loops) exchanges raw IDs. | `Vertex` is a small frozen dataclass provided for the model layer and documentation but **not** used in the Graph API; the API continues to exchange raw IDs exactly as the design's code shows. Flagged so it is not mistaken for an omission. | Phase 1 |

---

## What I need from you

You do not need to answer all of these. If you type `CONTINUE`, every **Default** above is adopted. The ones I'd most like you to look at, because they change behaviour that other teams or your viva might notice:

1. **D-01** — connected components on a directed graph: `ValueError` (default) or accept?
2. **D-02** — undirected `all_edges()` lists each edge once (default) or twice?
3. **D-03** — explicit `mode` argument (default) or implicit "no start means whole graph"?
4. **D-12** — recursion only (default), or also an opt-in iterative DFS?
5. **D-16** — OK to make `worklet1/` a package inside your project folder, with config files at the folder root?

---

## Implementation outcome (added after the full build)

You asked for the complete Worklet 1 in one request, so **every default above was adopted** (none was explicitly confirmed by you or anyone else). Status of each:

| ID | Outcome |
|---|---|
| D-01 | Adopted: `ConnectedComponentsAlgorithm` raises `ValueError` on directed graphs. Still contradicts the literal wording of §9.1; **please confirm**. |
| D-02 | Adopted, orientation refined: an undirected edge is listed once with the endpoint created first as `src` (not "first-added direction"). Must be confirmed with W2/W3. |
| D-03 | Adopted: `mode="single"\|"all"` plus `bfs`, `bfs_all`, `dfs`, `dfs_all`. |
| D-04 | Adopted: `parent` included for BFS. |
| D-05, D-06, D-07, D-08, D-09, D-10, D-13, D-14, D-15, D-19, D-20, D-22 | Adopted as written and covered by tests. |
| D-11 | Adopted; reproduces the §12.2 SCC example exactly. |
| D-12 | Adopted with the optional extension: recursive by default (path of 990 vertices works, 1000 raises `RecursionError`), plus opt-in `iterative=True` for DFS only (5000-deep path works; order equals the recursive version on 240 random graphs). Cycle detection and SCC remain recursive. |
| D-16 | Adopted: `worklet1/` is a package in your project folder; `pyproject.toml` at the folder root. |
| D-17 | Adopted: recorded in `design/design_decisions.md`; DD-08 added for Kosaraju. |
| D-18 | **Blocked**: no git repository; no git commands were run. |
| D-21 | `pytest 9.1.1`, `pytest-cov 7.1.0`, `ruff 0.17.0`, `mypy 2.4.0` installed and run (results in the final report). |
| **D-23 (new)** | **Neighbour order.** The design says "insertion order". A matrix has no edge-insertion order, so both representations use **vertex-creation order** for `neighbours()` and `all_edges()`. This makes list and matrix results identical (NFR-02). Consequence: when a vertex is created before an edge to it is added, its position follows vertex creation, not the order of `add_edge` calls. Documented as DD-09. |
| X-01 | Implemented, labelled PROPOSED. **Not agreed.** |
| X-02 | Implemented as proposed. **Not agreed.** |
| X-03 | `component_map` added to CC and SCC results, labelled PROPOSED. **Not agreed.** |
| X-04 | Not implemented. |
| X-05 | `ValueError` on directed graphs. |
