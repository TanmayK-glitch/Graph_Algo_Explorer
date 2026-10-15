"""Reproducible Worklet 2 benchmarks for algorithms and graph representations.

Run from repository root:
    python -m graph_integration.benchmark --sizes 10 50 100 --densities 0.1 0.5 --repeats 3

Outputs two CSV summaries in benchmark_results/:
* algorithms.csv: timed integration wrappers (including input adaptation).
* representations.csv: graph -> adjacency list/matrix/edge-list conversion cost.

Important: The current Dijkstra and Bellman-Ford implementations both run on
adjacency lists. Matrix timings measure representation conversion, NOT a native
matrix-based shortest-path implementation.
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from graph_integration.graph import Graph
from graph_integration.integration import (
    run_bellman_ford,
    run_dijkstra,
    run_kruskal,
)


ALGORITHM_COLUMNS = [
    "algorithm", "vertices", "edges", "density", "requested_density",
    "graph_representation", "repetitions", "execution_time_ms",
    "min_time_ms", "max_time_ms", "execution_status", "error",
]
REPRESENTATION_COLUMNS = [
    "operation", "graph_representation", "vertices", "edges", "density",
    "requested_density", "repetitions", "execution_time_ms", "min_time_ms",
    "max_time_ms", "execution_status", "error",
]


def generate_graph(vertices: int, density: float, seed: int = 42) -> Graph:
    """Create a deterministic connected, undirected graph with positive weights.

    A spanning tree guarantees connectivity. If the requested edge density is
    below the minimum possible for connectivity, actual density is higher.
    """
    if isinstance(vertices, bool) or not isinstance(vertices, int) or vertices < 2:
        raise ValueError("vertices must be an integer >= 2")
    if isinstance(density, bool) or not isinstance(density, (int, float)) or not 0 <= density <= 1:
        raise ValueError("density must be between 0 and 1")

    rng = random.Random(seed)
    graph = Graph(directed=False)
    for vertex in range(vertices):
        graph.add_vertex(vertex)

    selected: set[tuple[int, int]] = set()
    for v in range(1, vertices):
        u = rng.randrange(v)
        graph.add_edge(u, v, rng.randint(1, 20))
        selected.add((u, v))

    maximum_edges = vertices * (vertices - 1) // 2
    target = max(vertices - 1, round(density * maximum_edges))
    while len(selected) < target:
        u = rng.randrange(vertices)
        v = rng.randrange(vertices - 1)
        if v >= u:
            v += 1
        key = (min(u, v), max(u, v))
        if key in selected:
            continue
        selected.add(key)
        graph.add_edge(u, v, rng.randint(1, 20))
    return graph


def _measure(action: Callable[[], Any], repetitions: int) -> dict[str, Any]:
    """Measure runs; errors are explicitly recorded instead of invented times."""
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("repetitions must be >= 1")

    timings: list[float] = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        try:
            action()
        except Exception as exc:
            return {
                "repetitions": len(timings),
                "execution_time_ms": "",
                "min_time_ms": "",
                "max_time_ms": "",
                "execution_status": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            }
        timings.append((time.perf_counter_ns() - start) / 1_000_000)
    return {
        "repetitions": repetitions,
        "execution_time_ms": round(statistics.mean(timings), 6),
        "min_time_ms": round(min(timings), 6),
        "max_time_ms": round(max(timings), 6),
        "execution_status": "OK",
        "error": "",
    }


def benchmark_algorithms(graph: Graph, requested_density: float, repetitions: int) -> list[dict[str, Any]]:
    """Time algorithm + graph input adaptation, not graph generation."""
    source = graph.vertices[0]
    actions = (
        ("dijkstra", "adjacency_list", lambda: run_dijkstra(graph, source)),
        ("bellman_ford", "adjacency_list", lambda: run_bellman_ford(graph, source)),
        ("kruskal", "edge_list", lambda: run_kruskal(graph)),
    )
    rows = []
    for name, representation, action in actions:
        rows.append({
            "algorithm": name,
            "vertices": graph.num_vertices,
            "edges": graph.num_edges,
            "density": round(graph.density, 6),
            "requested_density": requested_density,
            "graph_representation": representation,
            **_measure(action, repetitions),
        })
    return rows


def benchmark_representations(graph: Graph, requested_density: float, repetitions: int) -> list[dict[str, Any]]:
    """Time conversion from shared Graph to each representation only."""
    conversions = (
        ("adjacency_list", graph.to_adjacency_list),
        ("adjacency_matrix", graph.to_adjacency_matrix),
        ("edge_list", graph.to_edge_list),
    )
    rows = []
    for name, operation in conversions:
        rows.append({
            "operation": "graph_to_representation",
            "graph_representation": name,
            "vertices": graph.num_vertices,
            "edges": graph.num_edges,
            "density": round(graph.density, 6),
            "requested_density": requested_density,
            **_measure(operation, repetitions),
        })
    return rows


def run_benchmarks(
    sizes: Iterable[int] = (10, 50, 100, 500, 1000),
    densities: Iterable[float] = (0.05, 0.2),
    repetitions: int = 3,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return actual timing results for each (size, density) configuration."""
    if repetitions < 1:
        raise ValueError("repetitions must be >= 1")
    algorithm_rows: list[dict[str, Any]] = []
    representation_rows: list[dict[str, Any]] = []

    for size in sizes:
        for density in densities:
            graph = generate_graph(size, density, seed=seed + size * 1009 + round(density * 10000))
            algorithm_rows.extend(benchmark_algorithms(graph, density, repetitions))
            representation_rows.extend(benchmark_representations(graph, density, repetitions))
            print(
                f"Completed: vertices={size}, edges={graph.num_edges}, "
                f"density={graph.density:.4f} (requested={density})",
                flush=True,
            )
    return algorithm_rows, representation_rows


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Worklet 2 graph benchmarks")
    parser.add_argument("--sizes", nargs="+", type=int, default=[10, 50, 100, 500, 1000])
    parser.add_argument("--densities", nargs="+", type=float, default=[0.05, 0.2])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("benchmark_results"))
    args = parser.parse_args()

    algorithm_rows, representation_rows = run_benchmarks(
        args.sizes, args.densities, args.repeats, args.seed
    )
    _write_csv(args.output / "algorithms.csv", ALGORITHM_COLUMNS, algorithm_rows)
    _write_csv(args.output / "representations.csv", REPRESENTATION_COLUMNS, representation_rows)
    print(f"Wrote {len(algorithm_rows)} algorithm rows and "
          f"{len(representation_rows)} representation rows to {args.output.resolve()}")


if __name__ == "__main__":
    main()
