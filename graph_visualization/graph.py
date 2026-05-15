from typing import Any

class Graph:
    def __init__(self, graph: dict[Any, dict[Any, float]] | None = None, directed: bool = False):
        self._graph = {k: dict(v) for k, v in graph.items()} if graph is not None else {}
        self._is_directed = directed

    def add_node(self, node):
        if node not in self._graph:
            self._graph[node] = {}

    def add_edge(self, in_node, out_node, weight: float = 1.0):
        if out_node not in self._graph[in_node]:
            self._graph[in_node][out_node] = weight
        if not self._is_directed and in_node not in self._graph[out_node]:
            self._graph[out_node][in_node] = weight

    def __contains__(self, node):
        return node in self._graph
    
    def __getitem__(self, node):
        return self._graph[node]
    
    def __iter__(self):
        return iter(self._graph)