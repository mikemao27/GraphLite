# graph_visualization

# interactive graph algorithm visualizer built on pygame.

# quick start:
# - from graph_visualization import launch
# - launch() # undirected graph (default)
# - launch(directed=True) # directed graph

# or build a graph programmatically:
# - from graph_visualization import Graph
# - g = Graph()
# - g.add_edge("A", "B", weight=2.5)
# - g.add_edge("B", "C")

from .graph      import Graph
from .renderer   import launch
from .layouts    import force_directed, euclidean_heuristic
from .algorithms import (
    BFS, BFS_generator,
    DFS, DFS_generator,
    Dijkstra, Dijkstra_generator,
    A_star, A_star_generator,
    Bellman_Ford, Bellman_Ford_generator,
    Prim, Prim_generator,
    Kruskal, Kruskal_generator,
    topological_sort, topological_sort_generator,
)

__all__ = [
    "Graph",
    "launch",
    "force_directed",
    "euclidean_heuristic",
    "BFS", "BFS_generator",
    "DFS", "DFS_generator",
    "Dijkstra", "Dijkstra_generator",
    "A_star", "A_star_generator",
    "Bellman_Ford", "Bellman_Ford_generator",
    "Prim", "Prim_generator",
    "Kruskal", "Kruskal_generator",
    "topological_sort", "topological_sort_generator",
]

__version__ = "0.2.0"