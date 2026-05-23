import math
import random
from graph_visualization.graph import Graph

def euclidean_heuristic(pos: dict):
    # returns a heuristic function bound to the given layout positions.
    # usage: heuristic = euclidean_heuristic(pos), A_star(graph, start, end, heuristic)

    def heuristic(node_a, node_b):
        x1, y1 = pos[node_a]
        x2, y2 = pos[node_b]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    return heuristic

def force_directed(graph: Graph, width: int, height: int, iterations: int = 500, k: float = None) -> dict:
    nodes = list(graph)
    if not nodes:
        return {}
    
    if k is None:
        k = math.sqrt((width * height) / max(len(nodes), 1))
    
    pos = {node: [random.uniform(50, width - 50), random.uniform(50, height - 50)] for node in nodes}

    for i in range(iterations):
        forces = {node: [0.0, 0.0] for node in nodes}

        for i_idx, u in enumerate(nodes):
            for v in nodes[i_idx + 1:]:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                distance = max(math.sqrt(dx ** 2 + dy ** 2), 0.01)
                repulsion = (k ** 2) / distance
                fx = repulsion * (dx / distance)
                fy = repulsion * (dy / distance)
                forces[u][0] += fx
                forces[u][1] += fy
                forces[v][0] -= fx
                forces[v][1] -= fy

        # attraction: connected nodes pull together
        for node in graph:
            for neighbor in graph[node]:
                dx = pos[node][0] - pos[neighbor][0]
                dy = pos[node][1] - pos[neighbor][1]
                distance = max(math.sqrt(dx ** 2 + dy ** 2), 0.01)
                attraction = (distance ** 2) / k
                fx = attraction * (dx / distance)
                fy = attraction * (dy / distance)
                forces[node][0] -= fx
                forces[node][1] -= fy
                forces[neighbor][0] += fx
                forces[neighbor][1] += fy
        
        # cooling: large moves early, small corrections late
        temperature = k * (1.0 - (i / iterations))

        for node in nodes:
            fx, fy = forces[node]
            magnitude = max(math.sqrt(fx ** 2 + fy ** 2), 0.01)
            scale = min(magnitude, temperature) / magnitude
            pos[node][0] += fx * scale
            pos[node][1] += fy * scale
            
            pos[node][0] = max(50, min(width - 50, pos[node][0]))
            pos[node][1] = max(50, min(height - 50, pos[node][1]))

    return {node: (pos[node][0], pos[node][1]) for node in nodes}