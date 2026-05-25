## Welcome to GraphLite
GraphLite is an open source Python based library that supports more interactive and higher quality graph algorithm visualization. Beyond simple visualization, GraphLite also integrates many typical graph algorithms such as BFS, DFS, Dijkstra's, Prim's A\*, Bellman-Ford, Prim's, Kruskal's, and Topologicla Sort (animated step by step).

GraphLite is built with Python and PyGame.

## Installation
```bash
pip install pygame-ce # or: pip install -r requirements.txt
python main.py # run the visualizer
```

Or install the package directly:

```bash
pip install .
graphlite # launches the window
```

Requires **Python 3.11+**.

## Controls
| Key / Action | Effect |
|---|---|
| **N** | Switch to node mode |
| **C** | Switch to edge mode |
| **T** *(edge mode)* | Toggle next edge between directed ↔ undirected |
| Click canvas *(node mode)* | Place a new node (prompted for name) |
| Drag node *(node mode)* | Reposition node |
| Click src, click dst *(edge mode)* | Draw edge (prompted for weight) |
| **Right-click** node | Delete node and its edges |
| **S** + click | Set start node |
| **E** + click | Set end node |
| **1–8** | Select algorithm |
| **Enter** | Run selected algorithm |
| **Space** | Pause / resume stepping |
| **+** / **-** | Speed up / slow down animation |
| **R** | Reset back to edit mode |
| **Q** | Quit |

## Algorithms
| # | Name | Needs start | Needs end | Graph type |
|---|---|---|---|---|
| 1 | BFS | ✓ | ✓ | Any |
| 2 | DFS | ✓ | ✓ | Any |
| 3 | Dijkstra | ✓ | ✓ | Non-negative weights |
| 4 | A\* | ✓ | ✓ | Non-negative weights |
| 5 | Bellman-Ford | ✓ | ✓ | Any (detects negative cycles) |
| 6 | Prim MST | ✓ | — | Undirected |
| 7 | Kruskal MST | — | — | Undirected |
| 8 | Topo Sort | — | — | Directed |

## Programmatic API
```python
from graph_visualization import Graph, BFS, Dijkstra, A_star, euclidean_heuristic

g = Graph(directed=False)
g.add_edge("A", "B", weight=1.0)
g.add_edge("B", "C", weight=2.5)
g.add_edge("A", "C", weight=4.0)

# plain traversal (returns parent dict)
traversal = BFS(g, "A", "C")

# dijkstra shortest path
traversal = Dijkstra(g, "A", "C")

# A* with positions
pos = {"A": (0, 0), "B": (1, 0), "C": (2, 0)}
traversal = A_star(g, "A", "C", euclidean_heuristic(pos))

# reconstruct path from traversal dict
def reconstruct(traversal, start, end):
    path, node = [], end
    while node is not None:
        path.append(node)
        node = traversal.get(node)
    return list(reversed(path))

print(reconstruct(traversal, "A", "C"))  # ['A', 'B', 'C']
```

## Mixed directed / undirected edges
```python
g = Graph(directed=False)          # undirected by default
g.add_edge("X", "Y")               # undirected
g.add_edge("Y", "Z", directed=True) # directed override
```

## Project layout
```
graphlite/
├── graph_visualization/
│   ├── __init__.py      # public API
│   ├── graph.py         # Graph data structure
│   ├── algorithms.py    # BFS, DFS, Dijkstra, A*, Bellman-Ford,
│   │                    # Prim, Kruskal, topological sort
│   ├── layouts.py       # force_directed, euclidean_heuristic
│   └── renderer.py      # pygame interactive visualizer
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License
Technically, an MIT license, but for the sake of academic progress (and more because I couldn't care less what you do with GraphLite), all code here can be generally seen as being "free-for-the-taking." So, if one truly wishes, just snatch the code that builds GraphLite, and run with it.