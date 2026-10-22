# Worklet 1 - Final Acceptance Report

Date: 14 Oct 2026. Environment: Linux, Python 3.10.12, pytest 9.1.1, pytest-cov 7.1.0, ruff 0.17.0, mypy 2.4.0.
All numbers below were produced by actually running the commands; nothing is estimated.

## 1. Commands run and results

| Command | Result |
|---|---|
| `python -m pytest` (project root) | **984 passed**, 0 failed, 0 skipped |
| Fresh virtualenv built from `requirements-dev.txt` on a copy of the project (run before the iterative-DFS addition) | 980 passed; demo ran; ruff and mypy clean. Not re-run in a fresh venv after the addition |
| `COVERAGE_FILE=/tmp/w1cov python -m pytest --cov=worklet1` | Source coverage: every module 100% except `graph/exceptions.py` (95%, line 34) and `io/edge_list_loader.py` (99%, line 76) - total for library modules about 99% |
| `python -m ruff check worklet1` (rules E,F,W,I,UP,C4,B; line length 120) | All checks passed |
| `python -m mypy worklet1/graph worklet1/algorithms worklet1/io` | Success: no issues found in 16 source files (tests are not type-checked) |
| `python -m worklet1.demo` | Ran to completion; output matches expectations |

Test counts per file: test_graph_base 83, test_adj_list 5, test_adj_matrix 5, test_edge_list_loader 25, test_bfs 29, test_dfs 24,
test_connected_components 18, test_scc 18, test_cycle_detection 26, test_topological_sort 18, test_bipartite 18,
test_architecture 18, test_complexity 3, test_integration 14, test_properties 680 (seeded random graphs; includes parameterised cases).

Defects found and fixed during the build (all in my own work): four public `__init__` methods lacked docstrings (caught by the NFR-05 test);
my complexity test disabled coverage tracing (fixed to restore the previous tracer); several test fixtures assumed the wrong vertex order.
No algorithm defect was found by the oracle tests.

## 2. Requirement status

Detailed rows with evidence: `REQUIREMENTS_TRACEABILITY.md`.

| Category | Requirements |
|---|---|
| **Verified complete** | FR-01 ... FR-20 (all 20); NFR-01 ... NFR-08; NFR-11; NFR-12 |
| **Partially satisfied** | none |
| **Failed** | none |
| **Blocked** | NFR-10 (small commits in one shared repository): the project folder is not a git repository and no git commands were run |
| **Unverified** | none |
| **Pending cross-worklet agreement** | NFR-09 (identical edge-list format in all three worklets): implemented as proposed, no sign-off from Worklet 2 or 3 |

"Verified" means a test or an automated check in `tests/` demonstrates it, as listed per row. FR-09, FR-18 and a few other items are verified against the
design as written *plus the defaults chosen in `DECISIONS_PENDING.md`* where the design was silent or contradictory.

## 3. Pending agreements (not claimed as approved)

* X-01 `edge_weight(u, v)` - implemented, PROPOSED to Worklet 2.
* X-02 edge-list format v1 - implemented, PROPOSED to Worklet 2 and 3.
* X-03 `metadata["component_map"]` - implemented on CC and SCC, PROPOSED to Worklet 3.
* X-04 traversal-animation step data - **not implemented**; open question.
* Choices other teams may notice: undirected `all_edges()` lists each edge once (D-02); neighbour order is vertex-creation order (D-23).

## 4. Choices that depart from or resolve the design text

* D-01: connected components reject directed graphs (design sections 8.3 and 9.1 disagree).
* D-23: vertex-creation order instead of edge-insertion order.
* D-03: `BFS_ALL`/`DFS_ALL` are exposed through `mode="all"` (plus the module functions the design shows).
* D-17: inconsistencies inside the design document are recorded, not silently corrected.

## 5. Limitations

* DFS, SCC and cycle detection are recursive by default; a directed path of 1000 vertices raises `RecursionError` (990 works). Plain DFS has an opt-in `iterative=True` (tested to 5000 vertices); SCC and cycle detection have no iterative variant.
* `AdjacencyListGraph.edge_weight` is O(degree), not O(1).
* Vertex ids must be `int` or `str`; the loader produces only `str` ids.
* Complexity evidence (NFR-12) is operation counting on a sparse path graph, not a benchmark across graph families.
* Tests were run on Linux/Python 3.10.12. The Windows commands in the README were not executed on Windows.
* `mypy` was run on the library only. Cache folders (`.mypy_cache`, `.pytest_cache`, `.ruff_cache`) exist in the project folder; they are listed in `.gitignore`.
* Two stray coverage files created by an early failed coverage run were moved to `_to_delete/` (deletion is not permitted in the folder); you can delete that folder.

## 6. Deliverables checklist

Code (`graph/`, `algorithms/`, `io/`), tests, `sample_graphs/`, README, `design/design_decisions.md`, `design/interfaces.md`,
`docs/COMPLEXITY.md`, `docs/DEMO.md`, `docs/VIVA_PREP.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/IMPLEMENTATION_PLAN.md`,
`docs/DECISIONS_PENDING.md`, `demo.py`, this report. The W1-W2 and W1-W3 interface agreements are documented **as pending**, not as agreed.
