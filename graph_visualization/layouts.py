import math

def euclidean_heuristic(pos: dict):
    # returns a heuristic function bound to the given layout positions.
    # usage: heuristic = euclidean_heuristic(pos), A_star(graph, start, end, heuristic)

    def heuristic(node_a, node_b):
        x1, y1 = pos[node_a]
        x2, y2 = pos[node_b]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    return heuristic