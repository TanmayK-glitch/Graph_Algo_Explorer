from graph_integration.graph import Graph

g = Graph(directed=False)

g.add_edge("A", "B", 4)
g.add_edge("A", "C", 2)
g.add_edge("B", "C", 1)
g.add_edge("C", "D", 3)

print("Vertices:", g.vertices)
print("Number of vertices:", g.num_vertices)
print("Number of edges:", g.num_edges)
print("Density:", round(g.density, 4))

print("\nAdjacency List:")
print(g.to_adjacency_list())

print("\nAdjacency Matrix:")
vertices, matrix = g.to_adjacency_matrix()
print("Order:", vertices)
for row in matrix:
    print(row)

print("\nEdge List:")
print(g.to_edge_list())

print("\nKruskal Input:")
print(g.to_kruskal_input())
