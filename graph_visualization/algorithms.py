from .graph import Graph
import queue as Q
from typing import Any, Callable

def BFS(graph: Graph, start_node, end_node):
    assert start_node in graph and end_node in graph, \
        f"the start_node {start_node} and end_node {end_node} should both be nodes in {graph}"
    
    # create a standard queue for BFS
    queue = Q.Queue()
    traversal = {node: None for node in graph}
    
    # push the starting node into the queue
    queue.put(start_node)

    # while the queue is not empty
    while not queue.empty():
        node = queue.get()
        for neighbor in graph[node]:
            if traversal[neighbor] is None and neighbor != start_node:
                traversal[neighbor] = node
                queue.put(neighbor)
                if neighbor == end_node:
                    return traversal
    
    return traversal

def DFS(graph: Graph, start_node, end_node):
    assert start_node in graph and end_node in graph, \
        f"the start_node {start_node} and end_node {end_node} should both be nodes in {graph}"
    
    # create a standard stack for BFS
    stack = Q.LifoQueue()
    traversal = {node: None for node in graph}
    
    # push the starting node into the stack
    stack.put(start_node)

    # while the stack is not empty
    while not stack.empty():
        node = stack.get()
        for neighbor in graph[node]:
            if traversal[neighbor] is None and neighbor != start_node:
                traversal[neighbor] = node
                stack.put(neighbor)
                if neighbor == end_node:
                    return traversal
    
    return traversal

# note that the heuristic estimator needs to be implemented and is currently not available
def A_star(graph: Graph, start_node, end_node, heuristic: Callable[[Any, Any], float]):
    assert start_node in graph and end_node in graph, \
        f"the start node {start_node} and end_node {end_node} should both be nodes in {graph}"
    
    traversal = {start_node: None}
    g_cost = {start_node: 0}
    f_cost = {start_node: 0 + heuristic(start_node, end_node)}

    open_set = Q.PriorityQueue() # feels easier than heapq
    closed_set = set()

    open_set.put((f_cost[start_node], start_node))

    while not open_set.empty():
        _, node = open_set.get()

        if node in closed_set:
            continue
        closed_set.add(node)
        
        if node == end_node:
            return traversal
        
        for neighbor in graph[node]:
            if neighbor not in closed_set:
                neighbor_g_cost = graph[node][neighbor] + g_cost[node]

                if neighbor_g_cost < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = neighbor_g_cost
                    f_cost[neighbor] = neighbor_g_cost + heuristic(neighbor, end_node)
                    traversal[neighbor] = node
                    open_set.put((f_cost[neighbor], neighbor))
    
    return traversal

def Dijkstra(graph: Graph, start_node, end_node):
    assert start_node in graph and end_node in graph, \
        f"the start node {start_node} and end_node {end_node} should both be nodes in {graph}"
    
    assert all(weight >= 0 for node in graph for weight in graph[node].values()), \
        f"Dijkstra's requires non-negative edge weights. Use Bellman-Ford for negative edge weights."
    
    traversal = {start_node: None}
    g_cost = {start_node: 0}

    open_set = Q.PriorityQueue()
    closed_set = set()

    open_set.put((g_cost[start_node], start_node))

    while not open_set.empty():
        _, node = open_set.get()

        if node in closed_set:
            continue
        closed_set.add(node)

        if node == end_node:
            return traversal
        
        for neighbor in graph[node]:
            if neighbor not in closed_set:
                neighbor_g_cost = graph[node][neighbor] + g_cost[node]

                if neighbor_g_cost < g_cost.get(neighbor, float("inf")):
                    g_cost[neighbor] = neighbor_g_cost
                    traversal[neighbor] = node
                    open_set.put((g_cost[neighbor], neighbor))

    return traversal

def Prim(graph: Graph, start_node):
    assert start_node in graph, \
        f"the start node {start_node} must be a node in {graph}"
    
    traversal = {start_node: None}
    visited = set()

    open_set = Q.PriorityQueue()
    open_set.put((0, start_node))
    g_cost = {start_node: 0}

    while not open_set.empty():
        _, node = open_set.get()

        if node in visited:
            continue
        visited.add(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                edge_weight = graph[node][neighbor]
                open_set.put((edge_weight, neighbor))
                if neighbor not in traversal or edge_weight < g_cost.get(neighbor, float("inf")):
                    traversal[neighbor] = node
                    g_cost[neighbor] = edge_weight
    
    return traversal

