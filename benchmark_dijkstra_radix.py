import random
import statistics
import time

from src.algorithms.dijkstra import dijkstra
from src.algorithms.dijkstra_radix import dijkstra_radix


def generate_graph(vertices, density, seed=42):
    """Generate a connected undirected graph with positive integer weights."""
    rng = random.Random(seed)
    graph = {v: [] for v in range(vertices)}
    edges = set()

    # Ensure the graph is connected.
    for v in range(1, vertices):
        u = rng.randrange(v)
        weight = rng.randint(1, 20)
        graph[u].append((v, weight))
        graph[v].append((u, weight))
        edges.add((min(u, v), max(u, v)))

    max_edges = vertices * (vertices - 1) // 2
    target_edges = max(vertices - 1, round(density * max_edges))

    while len(edges) < target_edges:
        u = rng.randrange(vertices)
        v = rng.randrange(vertices)

        if u == v:
            continue

        edge = (min(u, v), max(u, v))
        if edge in edges:
            continue

        edges.add(edge)
        weight = rng.randint(1, 20)
        graph[u].append((v, weight))
        graph[v].append((u, weight))

    return graph, len(edges)


def measure(function, graph, source, repetitions=9):
    """Warm up, then return repeated execution times in milliseconds."""
    function(graph, source)

    timings = []

    for _ in range(repetitions):
        start = time.perf_counter_ns()
        function(graph, source)
        elapsed = time.perf_counter_ns() - start
        timings.append(elapsed / 1_000_000)

    return statistics.median(timings)


def main():
    print("\nDijkstra vs Radix-Heap Dijkstra")
    print("=" * 88)
    print(
        f"{'Vertices':>8} {'Edges':>8} "
        f"{'MinHeap ms':>12} {'Radix ms':>12} "
        f"{'Speedup':>10} {'Correct?':>10}"
    )
    print("-" * 88)

    for vertices in (100, 500, 1000, 2000):
        for density in (0.01, 0.05):
            graph, edge_count = generate_graph(
                vertices,
                density,
                seed=42 + vertices + int(density * 1000),
            )
            source = 0

            # Check correctness outside the timed measurements.
            standard_result = dijkstra(graph, source)
            radix_result = dijkstra_radix(graph, source)

            correct = (
                standard_result.distances == radix_result.distances
            )

            if not correct:
                print(
                    f"CORRECTNESS FAILURE: vertices={vertices}, "
                    f"density={density}"
                )
                print("Standard:", standard_result.distances)
                print("Radix:", radix_result.distances)
                raise SystemExit(1)

            # Alternate execution order to reduce order-related bias.
            standard_times = []
            radix_times = []

            dijkstra(graph, source)
            dijkstra_radix(graph, source)

            for iteration in range(9):
                if iteration % 2 == 0:
                    start = time.perf_counter_ns()
                    dijkstra(graph, source)
                    standard_times.append(
                        (time.perf_counter_ns() - start) / 1_000_000
                    )

                    start = time.perf_counter_ns()
                    dijkstra_radix(graph, source)
                    radix_times.append(
                        (time.perf_counter_ns() - start) / 1_000_000
                    )
                else:
                    start = time.perf_counter_ns()
                    dijkstra_radix(graph, source)
                    radix_times.append(
                        (time.perf_counter_ns() - start) / 1_000_000
                    )

                    start = time.perf_counter_ns()
                    dijkstra(graph, source)
                    standard_times.append(
                        (time.perf_counter_ns() - start) / 1_000_000
                    )

            standard_ms = statistics.median(standard_times)
            radix_ms = statistics.median(radix_times)
            speedup = standard_ms / radix_ms if radix_ms else float("inf")

            print(
                f"{vertices:8d} {edge_count:8d} "
                f"{standard_ms:12.4f} {radix_ms:12.4f} "
                f"{speedup:9.2f}x {str(correct):>10}"
            )

    print("\nSpeedup > 1.00x means Radix Dijkstra was faster.")
    print("Speedup < 1.00x means standard Dijkstra was faster.")
    print("Times are medians of nine measurements per algorithm.")


if __name__ == "__main__":
    main()
