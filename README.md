# Graph Algorithms Explorer

A modular, tested Python implementation of fundamental graph algorithms,
starting with **Dijkstra's shortest-path algorithm** backed by a
custom **Min Heap**.

> **Status:** Standalone module — designed for easy integration into a
> larger graph-algorithm project.

---

## Implemented Algorithms

| Algorithm | Module | Complexity |
|-----------|--------|------------|
| **Min Heap** (binary) | `src/algorithms/min_heap.py` | insert O(log n), extract O(log n), peek O(1) |
| **Dijkstra's Algorithm** | `src/algorithms/dijkstra.py` | O((V + E) log V) |

---

## Project Structure

```
Graph_Algo_Explorer/
├── src/
│   ├── __init__.py
│   └── algorithms/
│       ├── __init__.py
│       ├── min_heap.py        # Reusable MinHeap class
│       └── dijkstra.py        # Dijkstra + path reconstruction
├── tests/
│   ├── test_min_heap.py       # MinHeap unit tests
│   └── test_dijkstra.py       # Dijkstra unit tests
├── examples/
│   ├── __init__.py
│   └── example_dijkstra.py    # Runnable demo
├── pyproject.toml             # Project metadata & Ruff config
├── .gitignore
└── README.md
```

---

## Requirements

- **Python 3.10+**
- No external runtime dependencies.
- [Ruff](https://docs.astral.sh/ruff/) (optional) for formatting and
  linting.

---

## Quick Start

### MinHeap Usage

```python
from src.algorithms.min_heap import MinHeap

heap = MinHeap()
heap.insert(5, "task-low")
heap.insert(1, "task-high")
heap.insert(3, "task-mid")

print(heap.peek_min())  # (1, 'task-high')
print(heap.extract_min())  # (1, 'task-high')
print(len(heap))  # 2
```

**Key properties:**

- Stores `(priority, item)` pairs; lower priority = extracted first.
- Supports negative and duplicate priorities.
- Uses an insertion counter as a tie-breaker so **items are never
  compared** — any hashable or unhashable object is safe.
- Raises `IndexError` on peek/extract from an empty heap.

### Dijkstra Usage

#### Graph Input Format

A graph is a `dict` mapping each vertex to a list of
`(neighbor, weight)` tuples:

```python
graph = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": [],
}
```

Vertices that appear only as neighbors (no key in the dict) are
treated as having no outgoing edges.

#### Computing Shortest Paths

```python
from src.algorithms.dijkstra import dijkstra, reconstruct_path

result = dijkstra(graph, "A")

# Distances from source
print(result.distances)
# {'A': 0, 'B': 3, 'C': 1, 'D': 4}

# Shortest path from A to D
path = reconstruct_path(result, "D")
print(path)  # ['A', 'C', 'B', 'D']
```

#### Return Values

`dijkstra()` returns a **`DijkstraResult`** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `source` | `Hashable` | The source vertex |
| `distances` | `dict[Vertex, float]` | Shortest distance from source (`math.inf` if unreachable) |
| `predecessors` | `dict[Vertex, Vertex \| None]` | Predecessor on the shortest path (`None` for source and unreachable vertices) |

#### Path Reconstruction

```python
path = reconstruct_path(result, target)
```

- Returns a `list` of vertices from source to target (inclusive).
- Returns `None` if the target is unreachable.
- A source-to-source query returns `[source]`.

---

## Running the Example

```bash
python -m examples.example_dijkstra
```

Expected output:

```
Shortest distances from 'A':
  A: 0.0
  B: 3.0
  C: 1.0
  D: 4.0

Shortest path from 'A' to 'D':
  A -> C -> B -> D
  Total distance: 4.0
```

---

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

---

## Ruff Formatting & Linting

```bash
# Format
ruff format .

# Check formatting (CI-friendly)
ruff format --check .

# Lint
ruff check .

# Lint and auto-fix
ruff check --fix .
```

Ruff is configured in `pyproject.toml`.

---

## Algorithm Details

### Min Heap

A standard binary min-heap stored in a flat list. Each entry is a
`(priority, counter, item)` triple internally; the counter provides
FIFO ordering for equal priorities without comparing items.

| Operation | Time |
|-----------|------|
| `insert` | O(log n) |
| `extract_min` | O(log n) |
| `peek_min` | O(1) |
| `is_empty` | O(1) |
| `size` / `len` | O(1) |

### Dijkstra's Algorithm

Single-source shortest paths using a binary min-heap as the priority
queue. The algorithm:

1. Initialises the source distance to 0 and all others to ∞.
2. Pushes the source onto the heap.
3. Extracts the minimum-distance vertex and relaxes its outgoing edges.
4. Records predecessors whenever a shorter path is found.
5. Skips stale heap entries (vertices already finalised).

**Complexity:** O((V + E) log V) with an adjacency list and binary
heap. Each edge relaxation may insert a new heap entry; the heap never
exceeds O(E) entries, and since log E ∈ O(log V) for simple graphs,
each operation costs O(log V).

**Non-negative weights required.** The algorithm raises `ValueError`
if any edge weight is negative.

---

## Future Integration

The public API (`dijkstra`, `reconstruct_path`, `MinHeap`) is
deliberately simple and accepts plain Python dicts and lists. When
integrating into a larger project (e.g., with a shared `Graph` class),
a thin adapter can translate between representations without changing
the core algorithm.
