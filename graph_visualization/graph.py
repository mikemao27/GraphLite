from typing import Any

class Graph:
    def __init__(self, graph: dict[Any, dict[Any, float]] | None = None, directed: bool = False):
        self._graph: dict[Any, dict[Any, float]] = {}
        self._is_directed = directed

        self._directed_edges: set[tuple] = set()

        if graph is not None:
            for node, neighbors in graph.items():
                self.add_node(node)
                for neighbor, weight in neighbors.items():
                    self.add_node(neighbor)
                    self.add_edge(node, neighbor, weight)
    
    def add_node(self, node: Any) -> None:
        if node not in self._graph:
            self._graph[node] = {}

    def remove_node(self, node: Any) -> None:
        # removes a node and all edges touching it.
        if node not in self._graph:
            return
        del self._graph[node]

        for neighbor in self._graph:
            self._graph[neighbor].pop(node, None)
        
        self._directed_edges = {
            (u, v) for (u, v) in self._drected_edges if u != node and v != node
        }
    
    def add_edge(self, in_node: Any, out_node: Any, weight: float = 1.0, directed: bool | None = None) -> None:
        # adds an edge. 
        # directed overrides the graph-level default for this specific edge, allowing mixed graphs.
        self.add_node(in_node)
        self.add_node(out_node)

        edge_directed = self._is_directed if directed is None else directed

        if out_node not in self._graph[in_node]:
            self._graph[in_node][out_node] = weight
        if not edge_directed and in_node not in self._graph[out_node]:
            self._graph[out_node][in_node]= weight
        
        if edge_directed:
            self._directed_edges.add((in_node, out_node))
    
    def remove_edge(self, in_node: Any, out_node: Any) -> None:
        self._graph[in_node].pop(out_node, None)
        self._graph[out_node].pop(in_node, None)
        self._directed_edges.discard((in_node, out_node))
        self._directed_edges.discard((out_node, in_node))

    def is_edge_directed(self, u: Any, v: Any) -> bool:
        return (u, v) in self._directed_edges
    
    def __contains__(self, node: Any) -> bool:
        return node in self._graph
    
    def __getitem__(self, node: Any) -> dict[Any, float]:
        return self._graph[node]
    
    def __iter__(self):
        return iter(self._graph)
    
    def __len__(self) -> int:
        return len(self._graph)
    
    def __repr__(self) -> str:
        kind = "Directed" if self._is_directed else "Undirected"
        return f"{kind} Graph(nodes = {len(self)}, edges = {self.edge_count()})"
    
    def edge_count(self) -> int:
        # returns the number of logical edges (undirected pairs count once).
        if self._is_directed:
            return sum(len(self._graph[node]) for node in self._graph)
        
        directed_count = len(self._directed_edges)
        undirected_stored = (
            sum(len(self._graph[node]) for node in self._graph) - directed_count
        )

        return directed_count + undirected_stored // 2
    
    def node(self) -> list[Any]:
        return list(self._graph)
    
    def edges(self) -> list[tuple[Any, Any, float]]:
        # returns a list of (u, v, weight) tuples; undirected edges appear once.
        seen: set[frozenset] = set()
        result = []
        
        for u in self._graph:
            for v, w in self._graph[u].items():
                key = frozenset([u, v])
                if self._is_directed or self.is_edge_directed(u, v):
                    result.append((u, v, w))
                elif key not in seen:
                    seen.add(key)
                    result.append((u, v, w))

        return result