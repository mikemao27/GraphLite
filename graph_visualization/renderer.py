import pygame
import sys
import math
from graph_visualization.graph import Graph
from graph_visualization.layouts import force_directed, euclidean_heuristic
from graph_visualization.algorithms import (
    BFS_generator, DFS_generator, Dijkstra_generator,
    A_star_generator, Bellman_Ford_generator,
    Prim_generator, Kruskal_generator, topological_sort_generator
)

# colors
BACKGROUND = (18,  18,  18)
NODE_DEFAULT = (70,  130, 180)
NODE_CURRENT = (255, 200,   0)
NODE_VISITED = (50,  205,  50)
NODE_FRONTIER = (255, 140,   0)
NODE_SELECTED = (220,  80,  80)
NODE_START = (100, 220, 100)
NODE_END = (220, 100, 100)
EDGE_DEFAULT = (100, 100, 100)
EDGE_ACTIVE = (255, 255, 255)
EDGE_MST = (50,  205,  50)
TEXT_COLOR = (255, 255, 255)
WEIGHT_COLOR = (180, 180, 180)
PANEL_BG = (28,  28,  28)
PANEL_BORDER = (60,  60,  60)
HINT_COLOR = (140, 140, 140)
ERROR_COLOR = (220,  80,  80)
SUCCESS_COLOR = (80,  205,  80)

NODE_RADIUS = 22
FONT_SIZE = 14
SMALL_FONT_SIZE = 12
PANEL_WIDTH = 220
FRAME_DELAY_MS = 600


# helpers
def _dist(ax, ay, bx, by):
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

def _node_at(pos, ipos, x, y):
    for node, (nx, ny) in ipos.items():
        if _dist(x, y, nx, ny) <= NODE_RADIUS:
            return node
    return None

def _edge_endpoints(ipos, u, v):
    x1, y1 = ipos[u]
    x2, y2 = ipos[v]
    dx, dy = x2 - x1, y2 - y1
    dist = max(math.sqrt(dx**2 + dy**2), 0.01)
    ox = NODE_RADIUS * (dx / dist)
    oy = NODE_RADIUS * (dy / dist)
    return (x1 + ox, y1 + oy), (x2 - ox, y2 - oy)

def _draw_arrow(surface, color, start, end, width=2):
    pygame.draw.line(surface, color, start, end, width)
    dx, dy = end[0] - start[0], end[1] - start[1]
    angle = math.atan2(dy, dx)
    length, spread = 14, 0.4
    p1 = (end[0] - length * math.cos(angle - spread),
          end[1] - length * math.sin(angle - spread))
    p2 = (end[0] - length * math.cos(angle + spread),
          end[1] - length * math.sin(angle + spread))
    pygame.draw.polygon(surface, color, [end, p1, p2])

def _draw_text_input(surface, font, prompt, value, x, y, w, error=None):
    pygame.draw.rect(surface, PANEL_BG,    (x, y, w, 64), border_radius=6)
    pygame.draw.rect(surface, PANEL_BORDER,(x, y, w, 64), 1, border_radius=6)
    surface.blit(font.render(prompt, True, HINT_COLOR),  (x + 10, y + 8))
    surface.blit(font.render(value + "|", True, TEXT_COLOR), (x + 10, y + 30))
    if error:
        surface.blit(font.render(error, True, ERROR_COLOR), (x + 10, y + 50))

def _draw_panel(surface, font, small_font, graph, mode, start_node, end_node,
                selected_algo, status_msg, width, height):
    px = width - PANEL_WIDTH
    pygame.draw.rect(surface, PANEL_BG,    (px, 0, PANEL_WIDTH, height))
    pygame.draw.rect(surface, PANEL_BORDER,(px, 0, PANEL_WIDTH, height), 1)

    y = 12
    def line(text, color=TEXT_COLOR, f=None):
        nonlocal y
        (f or font).render(text, True, color)
        surface.blit((f or font).render(text, True, color), (px + 10, y))
        y += 20

    line("── GraphLite ──", HINT_COLOR)
    y += 4

    line(f"Mode: {'EDIT' if mode == 'edit' else 'RUN'}", NODE_CURRENT)
    y += 4

    line("── Graph ──", HINT_COLOR)
    line(f"Nodes : {len(list(graph))}")
    line(f"Edges : {sum(len(graph[n]) for n in graph)}")
    line(f"Directed: {'yes' if graph._is_directed else 'no'}")
    y += 4

    line("── Algorithm ──", HINT_COLOR)
    algos = ["BFS", "DFS", "Dijkstra", "A*",
             "Bellman-Ford", "Prim", "Kruskal", "Topo Sort"]
    for i, name in enumerate(algos):
        color = NODE_CURRENT if name == selected_algo else TEXT_COLOR
        line(f"  {'>' if name == selected_algo else ' '} {i+1}. {name}", color, small_font)
    y += 4

    line("── Selection ──", HINT_COLOR)
    line(f"Start : {start_node or '—'}", NODE_START)
    line(f"End   : {end_node   or '—'}", NODE_END)
    y += 4

    line("── Controls ──", HINT_COLOR)
    controls = [
        "Click space : add node",
        "Drag nodes : move",
        "Drag n→n : add edge",
        "Right-click : delete",
        "S + click : set start",
        "E + click : set end",
        "1–8 : pick algo",
        "Enter : run algo",
        "Space : pause/resume",
        "R : reset view",
        "Q : quit",
    ]
    for c in controls:
        line(c, HINT_COLOR, small_font)

    if status_msg:
        y += 4
        color = ERROR_COLOR if status_msg.startswith("!") else SUCCESS_COLOR
        # word-wrap crudely at 26 chars
        words = status_msg
        line(words[:28], color, small_font)
        if len(words) > 28:
            line(words[28:], color, small_font)


# main entry point
def launch(width: int = 1100, height: int = 720, directed: bool = False):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("GraphLite")
    font = pygame.font.SysFont("monospace", FONT_SIZE,       bold=True)
    small_font = pygame.font.SysFont("monospace", SMALL_FONT_SIZE, bold=False)
    clock = pygame.time.Clock()

    canvas_w = width - PANEL_WIDTH

    graph = Graph(directed=directed)
    ipos = {} # {node: (int x, int y)}

    # interaction state
    mode = "edit" # "edit" | "run"
    dragging_node = None # node being dragged
    drag_offset = (0, 0)
    edge_source = None # node where edge drag started
    mouse_pos = (0, 0)

    # text input overlay
    input_active = False
    input_value = ""
    input_prompt = ""
    input_callback = None # called with final string when Enter pressed
    input_error = ""

    # algorithm state
    selected_algo = "BFS"
    start_node = None
    end_node = None
    step_iter = None
    algo_state = {}
    algo_done = False
    last_step_time = 0
    paused = False
    status_msg = ""

    algo_names = ["BFS", "DFS", "Dijkstra", "A*",
                  "Bellman-Ford", "Prim", "Kruskal", "Topo Sort"]

    def set_status(msg):
        nonlocal status_msg
        status_msg = msg

    def start_input(prompt, callback):
        nonlocal input_active, input_value, input_prompt, input_callback, input_error
        input_active = True
        input_value = ""
        input_prompt = prompt
        input_callback = callback
        input_error = ""

    def finish_input():
        nonlocal input_active, input_error
        val = input_value.strip()
        if not val:
            input_error = "Name can't be empty"
            return
        input_active = False
        input_callback(val)

    def add_node_at(name, x, y):
        if name in ipos:
            set_status(f"! Node '{name}' already exists")
            return
        graph.add_node(name)
        ipos[name] = (x, y)
        set_status(f"Added node '{name}'")

    def add_edge_between(u, v, weight_str):
        nonlocal input_active
        try:
            w = float(weight_str) if weight_str.strip() else 1.0
        except ValueError:
            set_status("! Invalid weight — using 1.0")
            w = 1.0
        graph.add_edge(u, v, w)
        set_status(f"Added edge {u} → {v}  (w={w})")

    def run_algorithm():
        nonlocal step_iter, algo_state, algo_done, mode, paused, last_step_time
        algo_state = {}
        algo_done = False
        paused = False
        mode = "run"
        last_step_time = pygame.time.get_ticks()

        try:
            if selected_algo == "BFS":
                step_iter = BFS_generator(graph, start_node, end_node)
            elif selected_algo == "DFS":
                step_iter = DFS_generator(graph, start_node, end_node)
            elif selected_algo == "Dijkstra":
                step_iter = Dijkstra_generator(graph, start_node, end_node)
            elif selected_algo == "A*":
                pos_float = {n: (float(x), float(y)) for n, (x, y) in ipos.items()}
                h = euclidean_heuristic(pos_float)
                step_iter = A_star_generator(graph, start_node, end_node, h)
            elif selected_algo == "Bellman-Ford":
                step_iter = Bellman_Ford_generator(graph, start_node, end_node)
            elif selected_algo == "Prim":
                step_iter = Prim_generator(graph, start_node)
            elif selected_algo == "Kruskal":
                step_iter = Kruskal_generator(graph)
            elif selected_algo == "Topo Sort":
                step_iter = topological_sort_generator(graph)
            set_status(f"Running {selected_algo}…")
        except AssertionError as e:
            set_status(f"! {e}")
            mode = "edit"

    def reset_run():
        nonlocal mode, step_iter, algo_state, algo_done, paused
        mode       = "edit"
        step_iter  = None
        algo_state = {}
        algo_done  = False
        paused     = False
        set_status("Reset to edit mode")

    # main loop
    while True:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # keyboard
            if event.type == pygame.KEYDOWN:

                if input_active:
                    if event.key == pygame.K_RETURN:
                        finish_input()
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_value = input_value[:-1]
                    else:
                        if event.unicode.isprintable():
                            input_value += event.unicode
                    continue  # swallow all keys while input is open

                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

                if event.key == pygame.K_r:
                    reset_run()

                if event.key == pygame.K_SPACE and mode == "run":
                    paused = not paused

                if event.key == pygame.K_RETURN and mode == "edit":
                    if start_node is None:
                        set_status("! Set a start node first (S + click)")
                    elif selected_algo not in ("Prim", "Kruskal", "Topo Sort") and end_node is None:
                        set_status("! Set an end node first (E + click)")
                    else:
                        run_algorithm()

                # algorithm selection 1–8
                algo_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]
                for i, k in enumerate(algo_keys):
                    if event.key == k:
                        selected_algo = algo_names[i]
                        set_status(f"Selected {selected_algo}")

            # mouse down
            if event.type == pygame.MOUSEBUTTONDOWN and not input_active:
                mx, my = event.pos
                if mx >= canvas_w:  # clicked panel — ignore
                    continue

                hit = _node_at(ipos, ipos, mx, my)

                if event.button == 1:  # left click
                    if keys[pygame.K_s] and hit:
                        start_node = hit
                        set_status(f"Start set to '{hit}'")

                    elif keys[pygame.K_e] and hit:
                        end_node = hit
                        set_status(f"End set to '{hit}'")

                    elif hit and mode == "edit":
                        # could be drag-move or edge-draw start — decide on mouse up
                        dragging_node = hit
                        drag_offset   = (mx - ipos[hit][0], my - ipos[hit][1])
                        edge_source   = hit

                    elif not hit and mode == "edit":
                        # click on empty space — add node
                        cx, cy = mx, my
                        start_input("Node name:", lambda name, x=cx, y=cy: add_node_at(name, x, y))

                if event.button == 3:  # right click — delete
                    if hit and mode == "edit":
                        del ipos[hit]
                        # rebuild graph without this node
                        new_graph = Graph(directed=graph._is_directed)
                        for n in ipos:
                            new_graph.add_node(n)
                        for n in ipos:
                            for nb, w in graph[n].items():
                                if nb in ipos:
                                    new_graph.add_edge(n, nb, w)
                        graph._graph = new_graph._graph
                        if start_node == hit: start_node = None
                        if end_node   == hit: end_node   = None
                        set_status(f"Deleted node '{hit}'")

            # mouse motion
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                mx, my = mouse_pos
                if dragging_node and mode == "edit":
                    nx = max(NODE_RADIUS, min(canvas_w - NODE_RADIUS, mx - drag_offset[0]))
                    ny = max(NODE_RADIUS, min(height   - NODE_RADIUS, my - drag_offset[1]))
                    ipos[dragging_node] = (nx, ny)
                    edge_source = None  # moved — not an edge drag

            # mouse up
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mx, my = event.pos
                if edge_source is not None and mode == "edit":
                    target = _node_at(ipos, ipos, mx, my)
                    if target and target != edge_source:
                        src = edge_source
                        start_input(
                            f"Weight {src}→{target} (enter=1):",
                            lambda w, u=src, v=target: add_edge_between(u, v, w)
                        )
                dragging_node = None
                edge_source   = None

        # algorithm step advance
        if step_iter and not algo_done and not paused:
            if now - last_step_time >= FRAME_DELAY_MS:
                try:
                    snapshot = next(step_iter)
                    algo_state.update(snapshot)
                    last_step_time = now
                except StopIteration:
                    algo_done = True
                    set_status(f"{selected_algo} complete — R to reset")
                except ValueError as e:
                    algo_done = True
                    set_status(f"! {e}")

        # draw 
        screen.fill(BACKGROUND)

        # clip drawing to canvas area
        canvas_rect = pygame.Rect(0, 0, canvas_w, height)
        screen.set_clip(canvas_rect)

        # draw edges
        drawn = set()
        for node in graph:
            if node not in ipos:
                continue
            for neighbor, weight in graph[node].items():
                if neighbor not in ipos:
                    continue
                key = frozenset([node, neighbor])
                if key in drawn and not graph._is_directed:
                    continue
                drawn.add(key)

                mst = algo_state.get("mst_edges", {})
                cur_edge = algo_state.get("current_edge")
                if mst.get(neighbor) == node or mst.get(node) == neighbor:
                    color = EDGE_MST
                elif cur_edge in [(node, neighbor), (neighbor, node)]:
                    color = EDGE_ACTIVE
                else:
                    color = EDGE_DEFAULT

                s, e = _edge_endpoints(ipos, node, neighbor)
                if graph._is_directed:
                    _draw_arrow(screen, color, s, e)
                else:
                    pygame.draw.line(screen, color, s, e, 2)

                if weight != 1.0:
                    mx2 = int((ipos[node][0] + ipos[neighbor][0]) / 2)
                    my2 = int((ipos[node][1] + ipos[neighbor][1]) / 2)
                    wlabel = small_font.render(f"{weight:.1f}", True, WEIGHT_COLOR)
                    screen.blit(wlabel, (mx2 + 4, my2 + 4))

        # draw in-progress edge drag
        if edge_source and mouse_pos:
            sx, sy = ipos[edge_source]
            pygame.draw.line(screen, EDGE_ACTIVE, (sx, sy), mouse_pos, 1)

        # draw nodes
        for node, (nx, ny) in ipos.items():
            cur     = algo_state.get("current")
            visited = algo_state.get("visited", set())
            frontier= algo_state.get("frontier", [])

            if node == start_node:
                color = NODE_START
            elif node == end_node:
                color = NODE_END
            elif node == cur:
                color = NODE_CURRENT
            elif node in visited:
                color = NODE_VISITED
            elif node in frontier:
                color = NODE_FRONTIER
            else:
                color = NODE_DEFAULT

            pygame.draw.circle(screen, color,      (nx, ny), NODE_RADIUS)
            pygame.draw.circle(screen, TEXT_COLOR, (nx, ny), NODE_RADIUS, 2)
            lbl = font.render(str(node), True, TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(center=(nx, ny)))

        screen.set_clip(None)

        # draw panel
        _draw_panel(screen, font, small_font, graph, mode, start_node, end_node,
                    selected_algo, status_msg, width, height)

        # draw text input overlay
        if input_active:
            _draw_text_input(screen, font, input_prompt, input_value,
                             canvas_w // 2 - 150, height // 2 - 32, 300, input_error)

        pygame.display.flip()
        clock.tick(60)