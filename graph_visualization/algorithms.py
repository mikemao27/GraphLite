from __future__ import annotations

import queue as Q
from typing import Any, Callable, Generator

from .graph import Graph

def BFS(graph: Graph, start_node: Any, end_node: Any) -> dict:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )

    q: Q.Queue = Q.Queue()
    traversal = {node: None for node in graph}
    q.put(start_node)

    while not q.empty():
        node = q.get()

        for neighbor in graph[node]:
            if traversal[neighbor] is None and neighbor != start_node:
                traversal[neighbor] = node
                q.put(neighbor)
                if neighbor == end_node:
                    return traversal
    
    return traversal

def BFS_generator(graph: Graph, start_node: Any, end_node: Any) -> Generator[dict, None, None]:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    q: Q.Queue = Q.Queue()
    traversal = {node: None for node in graph}
    visited: set = set()
    q.put(start_node)
 
    while not q.empty():
        node = q.get()
        visited.add(node)
 
        yield {
            "current": node,
            "visited": set(visited),
            "frontier": list(q.queue),
            "traversal": dict(traversal),
        }
 
        if node == end_node:
            return
 
        for neighbor in graph[node]:
            if traversal[neighbor] is None and neighbor != start_node:
                traversal[neighbor] = node
                q.put(neighbor)

def DFS(graph: Graph, start_node: Any, end_node: Any) -> dict:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    stack: list = [start_node]
    traversal = {node: None for node in graph}
 
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if traversal[neighbor] is None and neighbor != start_node:
                traversal[neighbor] = node
                stack.append(neighbor)
                if neighbor == end_node:
                    return traversal
 
    return traversal

def DFS_generator(graph: Graph, start_node: Any, end_node: Any) -> Generator[dict, None, None]:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    # use a plain list — avoids relying on LifoQueue internals for display
    stack: list = [start_node]
    traversal = {node: None for node in graph}
    visited: set = set()
 
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
 
        yield {
            "current": node,
            "visited": set(visited),
            "frontier": list(stack),
            "traversal": dict(traversal),
        }
 
        if node == end_node:
            return
 
        for neighbor in graph[node]:
            if neighbor not in visited:
                if traversal[neighbor] is None and neighbor != start_node:
                    traversal[neighbor] = node
                stack.append(neighbor)

def Dijkstra(graph: Graph, start_node: Any, end_node: Any) -> dict:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
    assert all(
        w >= 0 for n in graph for w in graph[n].values()
    ), "Dijkstra requires non-negative edge weights; use Bellman-Ford instead."
 
    traversal = {start_node: None}
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    closed_set: set = set()
    open_set.put((0, start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in closed_set:
            continue
        closed_set.add(node)
        if node == end_node:
            return traversal
        for neighbor, weight in graph[node].items():
            if neighbor not in closed_set:
                new_cost = g_cost[node] + weight
                if new_cost < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = new_cost
                    traversal[neighbor] = node
                    open_set.put((new_cost, neighbor))
 
    return traversal
 
def Dijkstra_generator(graph: Graph, start_node: Any, end_node: Any) -> Generator[dict, None, None]:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
    assert all(
        w >= 0 for n in graph for w in graph[n].values()
    ), "Dijkstra requires non-negative edge weights; use Bellman-Ford instead."
 
    traversal = {start_node: None}
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    closed_set: set = set()
    open_set.put((0, start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in closed_set:
            continue
        closed_set.add(node)
 
        yield {
            "current": node,
            "visited": set(closed_set),
            "g_cost": dict(g_cost),
            "traversal": dict(traversal),
        }
 
        if node == end_node:
            return
 
        for neighbor, weight in graph[node].items():
            if neighbor not in closed_set:
                new_cost = g_cost[node] + weight
                if new_cost < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = new_cost
                    traversal[neighbor] = node
                    open_set.put((new_cost, neighbor))

def A_star(graph: Graph, start_node: Any, end_node: Any, heuristic: Callable[[Any, Any], float]) -> dict:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    traversal = {start_node: None}
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    closed_set: set = set()
    open_set.put((heuristic(start_node, end_node), start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in closed_set:
            continue
        closed_set.add(node)
        if node == end_node:
            return traversal
        for neighbor, weight in graph[node].items():
            if neighbor not in closed_set:
                new_g = g_cost[node] + weight
                if new_g < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = new_g
                    traversal[neighbor] = node
                    open_set.put((new_g + heuristic(neighbor, end_node), neighbor))
 
    return traversal

def A_star_generator(graph: Graph, start_node: Any, end_node: Any, heuristic: Callable[[Any, Any], float]) -> Generator[dict, None, None]:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    traversal = {start_node: None}
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    closed_set: set = set()
    open_set.put((heuristic(start_node, end_node), start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in closed_set:
            continue
        closed_set.add(node)
 
        yield {
            "current": node,
            "visited": set(closed_set),
            "g_cost": dict(g_cost),
            "traversal": dict(traversal),
        }
 
        if node == end_node:
            return
 
        for neighbor, weight in graph[node].items():
            if neighbor not in closed_set:
                new_g = g_cost[node] + weight
                if new_g < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = new_g
                    traversal[neighbor] = node
                    open_set.put((new_g + heuristic(neighbor, end_node), neighbor))

def Bellman_Ford(graph: Graph, start_node: Any, end_node: Any) -> dict:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    dist = {node: float("inf") for node in graph}
    dist[start_node] = 0
    traversal = {start_node: None}
 
    for _ in range(len(graph) - 1):
        for node in graph:
            for neighbor, weight in graph[node].items():
                if dist[node] + weight < dist[neighbor]:
                    dist[neighbor] = dist[node] + weight
                    traversal[neighbor] = node
 
    for node in graph:
        for neighbor, weight in graph[node].items():
            if dist[node] + weight < dist[neighbor]:
                raise ValueError("graph contains a negative-weight cycle.")
 
    return traversal

def Bellman_Ford_generator(graph: Graph, start_node: Any, end_node: Any) -> Generator[dict, None, None]:
    assert start_node in graph and end_node in graph, (
        f"start_node {start_node!r} and end_node {end_node!r} "
        f"must both be nodes in the graph."
    )
 
    dist = {node: float("inf") for node in graph}
    dist[start_node] = 0
    traversal = {start_node: None}
    relaxed: set = set() # nodes that have been successfully relaxed at least once

    for _ in range(len(graph) - 1):
        for node in graph:
            for neighbor, weight in graph[node].items():
                if dist[node] + weight < dist.get(neighbor, float("inf")):
                    dist[neighbor] = dist[node] + weight
                    traversal[neighbor] = node
                    relaxed.add(neighbor)
                    yield {
                        "current": node,
                        "visited": set(relaxed), # reuse visited colour for relaxed nodes
                        "relaxed": neighbor,
                        "current_edge": (node, neighbor),
                        "dist": dict(dist),
                        "traversal": dict(traversal),
                    }
 
    for node in graph:
        for neighbor, weight in graph[node].items():
            if dist[node] + weight < dist[neighbor]:
                raise ValueError("graph contains a negative-weight cycle.")
            
def Prim(graph: Graph, start_node: Any) -> dict:
    assert start_node in graph, (
        f"start_node {start_node!r} must be a node in the graph."
    )
 
    traversal = {start_node: None}
    visited: set = set()
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    open_set.put((0, start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                if weight < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = weight
                    traversal[neighbor] = node
                    open_set.put((weight, neighbor))
 
    return traversal

def Prim_generator(graph: Graph, start_node: Any) -> Generator[dict, None, None]:
    assert start_node in graph, (
        f"start_node {start_node!r} must be a node in the graph."
    )
 
    traversal = {start_node: None}
    visited: set = set()
    g_cost = {start_node: 0}
    open_set: Q.PriorityQueue = Q.PriorityQueue()
    open_set.put((0, start_node))
 
    while not open_set.empty():
        _, node = open_set.get()
        if node in visited:
            continue
        visited.add(node)
 
        yield {
            "current": node,
            "visited": set(visited),
            "mst_edges": {k: v for k, v in traversal.items() if v is not None},
            "traversal": dict(traversal),
        }
 
        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                if weight < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = weight
                    traversal[neighbor] = node
                    open_set.put((weight, neighbor))

def Kruskal(graph: Graph) -> dict:
    assert not graph._is_directed, "Kruskal requires an undirected graph."
 
    parent = {node: node for node in graph}
    rank = {node: 0 for node in graph}
 
    def find(n):
        if parent[n] != n:
            parent[n] = find(parent[n])
        return parent[n]
 
    def union(a, b) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True
 
    edges = []
    seen: set[frozenset] = set()
    for node in graph:
        for neighbor, weight in graph[node].items():
            key = frozenset([node, neighbor])
            if key not in seen:
                seen.add(key)
                edges.append((weight, node, neighbor))
    edges.sort()
 
    mst = {node: None for node in graph}
    for weight, u, v in edges:
        if union(u, v):
            mst[v] = u
 
    return mst

def Kruskal_generator(graph: Graph) -> Generator[dict, None, None]:
    assert not graph._is_directed, "Kruskal requires an undirected graph."
 
    parent = {node: node for node in graph}
    rank = {node: 0 for node in graph}
 
    def find(n):
        if parent[n] != n:
            parent[n] = find(parent[n])
        return parent[n]
 
    def union(a, b) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True
 
    edges = []
    seen: set[frozenset] = set()
    for node in graph:
        for neighbor, weight in graph[node].items():
            key = frozenset([node, neighbor])
            if key not in seen:
                seen.add(key)
                edges.append((weight, node, neighbor))
    edges.sort()
 
    mst = {node: None for node in graph}
    for weight, u, v in edges:
        if union(u, v):
            mst[v] = u
            yield {
                "current_edge": (u, v),
                "mst_edges": {k: val for k, val in mst.items() if val is not None},
                "weight": weight,
            }

def topological_sort(graph: Graph) -> list:
    assert graph._is_directed, "topological sort requires a directed graph."

    visited: set = set()
    order: list = []
 
    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        order.append(node)
 
    for node in graph:
        if node not in visited:
            dfs(node)
 
    return list(reversed(order))

def topological_sort_generator(graph: Graph) -> Generator[dict, None, None]:
    assert graph._is_directed, "topological sort requires a directed graph."
 
    visited: set = set()
    order: list = []
 
    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        order.append(node)
 
    for node in graph:
        if node not in visited:
            dfs(node)

    # replay the final sorted order one node at a time so the renderer can highlight each node in topological sequence.
    result: list = list(reversed(order))
    for i, node in enumerate(result):
        yield {
            "current": node,
            "visited": set(result[: i + 1]),
            "order_so_far": result[: i + 1],
        }