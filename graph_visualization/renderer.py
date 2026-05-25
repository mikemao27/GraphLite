# GraphLite renderer — PyGame based interactive graph visualizer.

# key binds:
# edit mode: 
# - N : node sub-mode (click canvas to add, drag to move)
# - C : edge sub-mode (click source then destination)
# - T : toggle directed/undirected for the *next* edge (edge mode only)
# - Right-click : delete node under cursor
# - S + click : set start node
# - E + click : set end node
# - 1-8 : select algorithm
# - Enter : run selected algorithm

# run mode:
# - Space : pause / resume stepping
# - R : Reset back to edit mode

# always (regardless of state):
# - Q : quit
# - +  /  - : speed up / slow down step animation

from __future__ import annotations

import math
import sys

import pygame

from .graph import Graph
from .layouts import euclidean_heuristic
from .algorithms import (
    BFS_generator,
    DFS_generator,
    Dijkstra_generator,
    A_star_generator,
    Bellman_Ford_generator,
    Prim_generator,
    Kruskal_generator,
    topological_sort_generator,
)

# palette 
BACKGROUND = (18,  18,  18)
NODE_DEFAULT = (70, 130, 180)
NODE_CURRENT = (255, 200,   0)
NODE_VISITED = (50,  205,  50)
NODE_FRONTIER = (255, 140,   0)
NODE_SELECTED = (220,  80,  80)
NODE_START = (100, 220, 100)
NODE_END = (220, 100, 100)
EDGE_DEFAULT = (100, 100, 100)
EDGE_ACTIVE = (255, 255, 255)
EDGE_MST = (50,  205,  50)
EDGE_DIRECTED = (180, 100, 220) # tint for explicitly directed edges
TEXT_COLOR = (255, 255, 255)
WEIGHT_COLOR = (180, 180, 180)
PANEL_BG = (28,  28,  28)
PANEL_BORDER = (60,  60,  60)
HINT_COLOR = (140, 140, 140)
ERROR_COLOR = (220,  80,  80)
SUCCESS_COLOR = (80,  205,  80)

# constants 
NODE_RADIUS = 22
FONT_SIZE = 14
SMALL_FONT_SIZE = 12
PANEL_WIDTH = 230
FRAME_DELAY_MIN = 50 # ms (fastest)
FRAME_DELAY_MAX = 1500 # ms (slowest)
FRAME_DELAY_DEFAULT = 600


# drawing helpers 

def _dist(ax, ay, bx, by) -> float:
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

def _node_at(ipos: dict, x: int, y: int):
    for node, (nx, ny) in ipos.items():
        if _dist(x, y, nx, ny) <= NODE_RADIUS:
            return node
    return None

def _edge_endpoints(ipos: dict, u, v):
    x1, y1 = ipos[u]
    x2, y2 = ipos[v]
    dx, dy  = x2 - x1, y2 - y1
    dist    = max(math.sqrt(dx**2 + dy**2), 0.01)
    ox      = NODE_RADIUS * (dx / dist)
    oy      = NODE_RADIUS * (dy / dist)
    return (x1 + ox, y1 + oy), (x2 - ox, y2 - oy)

def _draw_arrow(surface, color, start, end, width: int = 2) -> None:
    pygame.draw.line(surface, color, start, end, width)
    dx, dy  = end[0] - start[0], end[1] - start[1]
    angle   = math.atan2(dy, dx)
    length, spread = 14, 0.4
    p1 = (end[0] - length * math.cos(angle - spread),
          end[1] - length * math.sin(angle - spread))
    p2 = (end[0] - length * math.cos(angle + spread),
          end[1] - length * math.sin(angle + spread))
    pygame.draw.polygon(surface, color, [end, p1, p2])

def _draw_text_input(surface, font, prompt, value, x, y, w, error=None) -> None:
    pygame.draw.rect(surface, PANEL_BG,     (x, y, w, 64), border_radius=6)
    pygame.draw.rect(surface, PANEL_BORDER, (x, y, w, 64), 1, border_radius=6)
    surface.blit(font.render(prompt,          True, HINT_COLOR), (x + 10, y + 8))
    surface.blit(font.render(value + "|",     True, TEXT_COLOR), (x + 10, y + 30))
    if error:
        surface.blit(font.render(error, True, ERROR_COLOR), (x + 10, y + 50))

def _draw_panel(
    surface, font, small_font,
    graph, mode, edit_submode, next_edge_directed,
    start_node, end_node, selected_algo,
    status_msg, frame_delay_ms,
    width, height,
) -> None:
    px = width - PANEL_WIDTH
    pygame.draw.rect(surface, PANEL_BG,     (px, 0, PANEL_WIDTH, height))
    pygame.draw.rect(surface, PANEL_BORDER, (px, 0, PANEL_WIDTH, height), 1)

    y = 12

    def line(text, color=TEXT_COLOR, f=None):
        nonlocal y
        surface.blit((f or font).render(text, True, color), (px + 10, y))
        y += 20

    line("GraphLite", HINT_COLOR)
    y += 4

    if mode == "edit":
        submode_label = "NODE" if edit_submode == "node" else "EDGE"
        line(f"Mode: EDIT ({submode_label})", NODE_CURRENT)
    else:
        line("Mode: RUN", NODE_CURRENT)
    y += 4

    line("Graph", HINT_COLOR)
    line(f"Nodes : {len(graph)}")
    line(f"Edges : {graph.edge_count()}")
    line(f"Directed: {'yes' if graph._is_directed else 'no'}")
    y += 4

    if mode == "edit" and edit_submode == "edge":
        dir_label = "DIRECTED"   if next_edge_directed else "UNDIRECTED"
        dir_color = EDGE_DIRECTED if next_edge_directed else HINT_COLOR
        line(f"Next Edge: {dir_label}", dir_color)
        line("(T to toggle)", HINT_COLOR, small_font)
        y += 4

    line("Algorithm", HINT_COLOR)
    algos = ["BFS", "DFS", "Dijkstra", "A*",
             "Bellman-Ford", "Prim", "Kruskal", "Topo Sort"]
    for i, name in enumerate(algos):
        color = NODE_CURRENT if name == selected_algo else TEXT_COLOR
        line(f"  {'>' if name == selected_algo else ' '} {i+1}. {name}",
             color, small_font)
    y += 4

    line("Selection", HINT_COLOR)
    line(f"Start : {start_node or '-'}", NODE_START)
    line(f"End   : {end_node   or '-'}", NODE_END)
    y += 4

    speed_pct = int(100 * (FRAME_DELAY_MAX - frame_delay_ms) /
                    (FRAME_DELAY_MAX - FRAME_DELAY_MIN))
    line(f"Speed : {speed_pct}%  (+/-)", HINT_COLOR, small_font)
    y += 4

    line("Controls", HINT_COLOR)
    controls = [
        "N : node mode",
        "C : edge mode",
        "  node: click to place",
        "  node: drag to move",
        "  edge: click src -> dst",
        "  T : toggle edge dir",
        "Right-click : delete",
        "S + click : set start",
        "E + click : set end",
        "1-8 : pick algorithm",
        "Enter : run algorithm",
        "Space : pause/resume",
        "+/- : speed of animation",
        "R : reset run",
        "Q : quit",
    ]
    for c in controls:
        line(c, HINT_COLOR, small_font)

    if status_msg:
        y += 4
        color = ERROR_COLOR if status_msg.startswith("!") else SUCCESS_COLOR
        for chunk in [status_msg[i:i+28] for i in range(0, len(status_msg), 28)]:
            line(chunk, color, small_font)


# terminal output

def _reconstruct_path(traversal: dict, start, end) -> list:
    # walk the parent-pointer dict back from end to start.
    path, node = [], end
    while node is not None:
        path.append(node)
        node = traversal.get(node)
    path.reverse()
    # if start isn't in the path the end node was unreachable
    return path if path and path[0] == start else []


def _print_result(algo: str, state: dict, start, end) -> None:
    # print a compact traversal/result summary to the terminal.
    sep = "─" * 48

    if algo in ("BFS", "DFS", "Dijkstra", "A*", "Bellman-Ford"):
        traversal = state.get("traversal", {})
        path = _reconstruct_path(traversal, start, end)
        visited_order = list(state.get("visited", set()))

        print(sep)
        print(f" {algo} | Start Node: {start} → End Node: {end}")
        if path:
            print(f" Path : {' → '.join(str(n) for n in path)}")
        else:
            print(f" Path : (unreachable)")
        print(f" Visited : {visited_order}")
        print(sep)

    elif algo in ("Prim", "Kruskal"):
        mst = state.get("mst_edges", {})
        edges = [(v, u) for v, u in mst.items()]  # (child, parent)
        print(sep)
        print(f" {algo} MST")
        print(f" Edges : {[(str(u), str(v)) for u, v in edges]}")
        print(sep)

    elif algo == "Topo Sort":
        order = state.get("order_so_far", [])
        print(sep)
        print(f" Topological Sort")
        print(f" Order : {' → '.join(str(n) for n in order)}")
        print(sep)


# main entry point 

def launch(width: int = 1100, height: int = 720, directed: bool = False) -> None:
    # open the GraphLite window.

    # parameters:
    # - width, height: Window dimensions in pixels.

    # directed:
    # - default edge direction for the graph.
    # - Can be overridden per-edge in the UI by pressing **T** before completing an edge in edge mode.

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("GraphLite")
    font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)
    small_font = pygame.font.SysFont("monospace", SMALL_FONT_SIZE, bold=False)
    clock = pygame.time.Clock()

    canvas_w = width - PANEL_WIDTH

    graph = Graph(directed=directed)
    ipos: dict = {} # node → (x, y)  pixel positions

    # interaction state
    mode         = "edit"
    edit_submode = "node" # "node" | "edge"
    dragging_node = None
    drag_offset = (0, 0)
    edge_source = None # first click in edge mode
    mouse_pos = (0, 0)

    # per-edge directed toggle — starts at the graph default
    next_edge_directed: bool = directed

    # text input overlay
    input_active   = False
    input_value    = ""
    input_prompt   = ""
    input_callback = None
    input_error    = ""

    # algorithm state
    algo_names = ["BFS", "DFS", "Dijkstra", "A*", 
                  "Bellman-Ford", "Prim", "Kruskal", "Topo Sort"]
    selected_algo = "BFS"
    start_node = None
    end_node = None
    step_iter = None
    algo_state: dict = {}
    algo_done = False
    last_step_time = 0
    paused = False
    status_msg = ""
    frame_delay_ms = FRAME_DELAY_DEFAULT

    # local helpers 
    def set_status(msg: str) -> None:
        nonlocal status_msg
        status_msg = msg

    def start_input(prompt: str, callback) -> None:
        nonlocal input_active, input_value, input_prompt, input_callback, input_error
        input_active = True
        input_value = ""
        input_prompt = prompt
        input_callback = callback
        input_error = ""

    def finish_input() -> None:
        nonlocal input_active, input_error
        val = input_value.strip()
        if not val:
            input_error = "Name can't be empty"
            return
        input_active = False
        input_callback(val)

    def add_node_at(name: str, x: int, y: int) -> None:
        if name in ipos:
            set_status(f"! Node '{name}' exists already")
            return
        graph.add_node(name)
        ipos[name] = (x, y)
        set_status(f"Added node '{name}'")

    def add_edge_between(u, v, weight_str: str, edge_directed: bool) -> None:
        try:
            w = float(weight_str) if weight_str.strip() else 1.0
        except ValueError:
            set_status("! Invalid weight — using 1.0")
            w = 1.0
        graph.add_edge(u, v, w, directed=edge_directed)
        arrow = "→" if edge_directed else "—"
        set_status(f"Edge {u} {arrow} {v}  (w={w})")

    def run_algorithm() -> None:
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
                pos_f = {n: (float(x), float(y)) for n, (x, y) in ipos.items()}
                step_iter = A_star_generator(
                    graph, start_node, end_node, euclidean_heuristic(pos_f)
                )
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

    def reset_run() -> None:
        nonlocal mode, step_iter, algo_state, algo_done, paused
        mode = "edit"
        step_iter = None
        algo_state = {}
        algo_done = False
        paused = False
        set_status("Reset to Edit Mode")

    # main loop 
    while True:
        now  = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keyboard 
            if event.type == pygame.KEYDOWN:

                if input_active:
                    if   event.key == pygame.K_RETURN:    finish_input()
                    elif event.key == pygame.K_ESCAPE:    input_active = False
                    elif event.key == pygame.K_BACKSPACE: input_value = input_value[:-1]
                    elif event.unicode.isprintable():     input_value += event.unicode
                    continue

                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

                if event.key == pygame.K_r:
                    reset_run()

                if event.key == pygame.K_n and mode == "edit":
                    edit_submode = "node"
                    edge_source  = None
                    set_status("Node mode")

                if event.key == pygame.K_c and mode == "edit":
                    edit_submode = "edge"
                    edge_source  = None
                    set_status("Edge mode — click source node")

                # T toggles direction for the next edge
                if event.key == pygame.K_t and mode == "edit" and edit_submode == "edge":
                    next_edge_directed = not next_edge_directed
                    label = "DIRECTED" if next_edge_directed else "UNDIRECTED"
                    set_status(f"Next edge: {label}")

                if event.key == pygame.K_SPACE and mode == "run":
                    paused = not paused

                if event.key == pygame.K_RETURN and mode == "edit":
                    if start_node is None:
                        set_status("! Set a start node first (S + click)")
                    elif selected_algo not in ("Prim", "Kruskal", "Topo Sort") \
                            and end_node is None:
                        set_status("! Set an end node (E + click)")
                    else:
                        run_algorithm()

                # speed control
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    frame_delay_ms = max(FRAME_DELAY_MIN,
                                         frame_delay_ms - 100)
                    set_status(f"Step Delay: {frame_delay_ms} ms")
                if event.key == pygame.K_MINUS:
                    frame_delay_ms = min(FRAME_DELAY_MAX,
                                         frame_delay_ms + 100)
                    set_status(f"Step Delay: {frame_delay_ms} ms")

                # algorithm selector 1-8
                algo_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]
                for i, k in enumerate(algo_keys):
                    if event.key == k:
                        selected_algo = algo_names[i]
                        set_status(f"Selected {selected_algo}")

            # mouse down
            if event.type == pygame.MOUSEBUTTONDOWN and not input_active:
                mx, my = event.pos
                if mx >= canvas_w:
                    continue

                hit = _node_at(ipos, mx, my)

                if event.button == 1:
                    if keys[pygame.K_s] and hit:
                        start_node = hit
                        set_status(f"Start → '{hit}'")

                    elif keys[pygame.K_e] and hit:
                        end_node = hit
                        set_status(f"End → '{hit}'")

                    elif mode == "edit" and edit_submode == "node":
                        if hit:
                            dragging_node = hit
                            drag_offset   = (mx - ipos[hit][0], my - ipos[hit][1])
                        else:
                            cx, cy = mx, my
                            start_input(
                                "Node Name:",
                                lambda name, x=cx, y=cy: add_node_at(name, x, y),
                            )

                    elif mode == "edit" and edit_submode == "edge":
                        if hit:
                            if edge_source is None:
                                edge_source = hit
                                set_status(f"Source: '{hit}' — click destination")
                            else:
                                if hit != edge_source:
                                    src = edge_source
                                    captured_directed = next_edge_directed
                                    edge_source = None
                                    start_input(
                                        f"Weight {src}→{hit} (Enter = 1):",
                                        lambda w, u=src, v=hit,
                                        d=captured_directed: add_edge_between(u, v, w, d),
                                    )
                                else:
                                    edge_source = None
                                    set_status("Edge Mode — click source node")

                if event.button == 3:
                    if hit and mode == "edit":
                        graph.remove_node(hit)
                        del ipos[hit]
                        if start_node == hit: start_node = None
                        if end_node == hit: end_node = None
                        if edge_source == hit: edge_source = None
                        set_status(f"Deleted '{hit}'")

            # mouse motion 
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                mx, my    = mouse_pos
                if dragging_node and mode == "edit" and edit_submode == "node":
                    nx = max(NODE_RADIUS, min(canvas_w - NODE_RADIUS,
                                              mx - drag_offset[0]))
                    ny = max(NODE_RADIUS, min(height  - NODE_RADIUS,
                                              my - drag_offset[1]))
                    ipos[dragging_node] = (nx, ny)

            # mouse up 
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_node = None

        # algorithm step advance 
        if step_iter and not algo_done and not paused:
            if now - last_step_time >= frame_delay_ms:
                try:
                    snapshot = next(step_iter)
                    algo_state.update(snapshot)
                    last_step_time = now
                except StopIteration:
                    algo_done = True
                    set_status(f"{selected_algo} done — R to reset")
                    _print_result(selected_algo, algo_state, start_node, end_node)
                except ValueError as e:
                    algo_done = True
                    set_status(f"! {e}")

        # draw 
        screen.fill(BACKGROUND)
        screen.set_clip(pygame.Rect(0, 0, canvas_w, height))

        # edges
        drawn: set = set()
        for node in graph:
            if node not in ipos:
                continue
            for neighbor, weight in graph[node].items():
                if neighbor not in ipos:
                    continue
                key = frozenset([node, neighbor])
                is_directed_edge = graph.is_edge_directed(node, neighbor)

                # for undirected edges skip the reverse duplicate
                if not is_directed_edge and key in drawn:
                    continue
                drawn.add(key)

                mst = algo_state.get("mst_edges", {})
                cur_edge = algo_state.get("current_edge")

                if mst.get(neighbor) == node or mst.get(node) == neighbor:
                    color = EDGE_MST
                elif cur_edge in [(node, neighbor), (neighbor, node)]:
                    color = EDGE_ACTIVE
                elif is_directed_edge and not graph._is_directed:
                    color = EDGE_DIRECTED # mixed-mode: highlight directed edges
                else:
                    color = EDGE_DEFAULT

                s, e = _edge_endpoints(ipos, node, neighbor)

                if graph._is_directed or is_directed_edge:
                    _draw_arrow(screen, color, s, e)
                else:
                    pygame.draw.line(screen, color, s, e, 2)

                if weight != 1.0:
                    mx2 = int((ipos[node][0] + ipos[neighbor][0]) / 2)
                    my2 = int((ipos[node][1] + ipos[neighbor][1]) / 2)
                    screen.blit(
                        small_font.render(f"{weight:.1f}", True, WEIGHT_COLOR),
                        (mx2 + 4, my2 + 4),
                    )

        # in-progress edge line
        if edit_submode == "edge" and edge_source and edge_source in ipos:
            sx, sy = ipos[edge_source]
            pygame.draw.line(screen, EDGE_ACTIVE, (sx, sy), mouse_pos, 1)

        # nodes
        for node, (nx, ny) in ipos.items():
            cur      = algo_state.get("current")
            visited  = algo_state.get("visited", set())
            frontier = algo_state.get("frontier", [])

            if node == edge_source: color = NODE_SELECTED
            elif node == start_node: color = NODE_START
            elif node == end_node: color = NODE_END
            elif node == cur: color = NODE_CURRENT
            elif node in visited: color = NODE_VISITED
            elif node in frontier: color = NODE_FRONTIER
            else: color = NODE_DEFAULT

            pygame.draw.circle(screen, color, (nx, ny), NODE_RADIUS)
            pygame.draw.circle(screen, TEXT_COLOR, (nx, ny), NODE_RADIUS, 2)
            lbl = font.render(str(node), True, TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(center=(nx, ny)))

        screen.set_clip(None)

        # panel
        _draw_panel(
            screen, font, small_font,
            graph, mode, edit_submode, next_edge_directed,
            start_node, end_node, selected_algo,
            status_msg, frame_delay_ms,
            width, height,
        )

        # text input overlay
        if input_active:
            _draw_text_input(
                screen, font, input_prompt, input_value,
                canvas_w // 2 - 150, height // 2 - 32, 300,
                input_error,
            )

        pygame.display.flip()
        clock.tick(60)