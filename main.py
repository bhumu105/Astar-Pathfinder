import tkinter as tk
from tkinter import ttk
import heapq
import random

GRID_SIZE = 15
TILE_SIZE = 40
PADDING = 20

COLORS = {
    "bg":      "#1e1e2e",
    "panel":   "#262638",
    "empty":   "#2e2e44",
    "grid":    "#1a1a28",
    "pillar":  "#11111a",
    "start":   "#a6e3a1",
    "end":     "#f38ba8",
    "path":    "#89b4fa",
    "explored":"#3a3a55",
    "text":    "#cdd6f4",
    "muted":   "#7f849c",
    "accent":  "#cba6f7",
}

grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
tiles = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
start = None
end = None
last_path = []
paint_mode = None  # "wall" or "empty" while right-button is held


SQRT2 = 2 ** 0.5


def astar(grid, start, end, diagonal=False):
    def h(a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        if diagonal:
            # Octile distance
            return (dx + dy) + (SQRT2 - 2) * min(dx, dy)
        return dx + dy

    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    if diagonal:
        moves += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    counter = 0  # tiebreaker for stable ordering
    open_list = [(0, counter, start)]
    came_from = {}
    g_score = {start: 0}
    explored = set()

    while open_list:
        _, _, current = heapq.heappop(open_list)
        if current in explored:
            continue
        explored.add(current)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, explored

        for dx, dy in moves:
            nx, ny = current[0] + dx, current[1] + dy
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                continue
            if grid[nx][ny] == 1:
                continue
            # Block diagonal movement that cuts a corner
            if dx and dy and (grid[current[0] + dx][current[1]] == 1
                              or grid[current[0]][current[1] + dy] == 1):
                continue
            step = SQRT2 if dx and dy else 1
            tentative = g_score[current] + step
            neighbor = (nx, ny)
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                counter += 1
                heapq.heappush(open_list, (tentative + h(neighbor, end), counter, neighbor))

    return [], explored


def tile_color(x, y):
    if (x, y) == start:
        return COLORS["start"]
    if (x, y) == end:
        return COLORS["end"]
    if grid[x][y] == 1:
        return COLORS["pillar"]
    return COLORS["empty"]


def repaint_tile(x, y):
    canvas.itemconfig(tiles[x][y], fill=tile_color(x, y))


def clear_path_visual():
    global last_path
    for x, y in last_path:
        if (x, y) != start and (x, y) != end:
            repaint_tile(x, y)
    last_path = []
    # Clear any explored cells too
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) == start or (x, y) == end or grid[x][y] == 1:
                continue
            canvas.itemconfig(tiles[x][y], fill=COLORS["empty"])


def animate_path(path, idx=0):
    if idx >= len(path):
        set_status(f"Path found — length {len(path)}", COLORS["path"])
        return
    x, y = path[idx]
    if (x, y) != end:
        canvas.itemconfig(tiles[x][y], fill=COLORS["path"])
    root.after(speed_var.get(), animate_path, path, idx + 1)


def run_search():
    global last_path
    if not start or not end:
        return
    clear_path_visual()
    path, explored = astar(grid, start, end, diagonal=diagonal_var.get())
    # Briefly tint explored cells
    for x, y in explored:
        if (x, y) != start and (x, y) != end and grid[x][y] == 0:
            canvas.itemconfig(tiles[x][y], fill=COLORS["explored"])
    if not path:
        set_status("No path found", COLORS["end"])
        return
    last_path = path
    set_status("Tracing path…", COLORS["accent"])
    root.after(120, animate_path, path)


def on_left_click(event):
    global start, end
    x, y = event.x // TILE_SIZE, event.y // TILE_SIZE
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        return
    if grid[x][y] == 1:
        return

    if start is None:
        start = (x, y)
        repaint_tile(x, y)
        set_status("Pick an end tile", COLORS["end"])
    elif end is None and (x, y) != start:
        end = (x, y)
        repaint_tile(x, y)
        run_search()
    else:
        # Reset selection on subsequent clicks
        reset_selection()
        start = (x, y)
        repaint_tile(x, y)
        set_status("Pick an end tile", COLORS["end"])


def apply_paint(x, y):
    if (x, y) == start or (x, y) == end:
        return
    target = 1 if paint_mode == "wall" else 0
    if grid[x][y] != target:
        grid[x][y] = target
        repaint_tile(x, y)


def on_right_press(event):
    global paint_mode
    x, y = event.x // TILE_SIZE, event.y // TILE_SIZE
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        return
    if (x, y) == start or (x, y) == end:
        return
    paint_mode = "empty" if grid[x][y] == 1 else "wall"
    apply_paint(x, y)


def on_right_drag(event):
    if paint_mode is None:
        return
    x, y = event.x // TILE_SIZE, event.y // TILE_SIZE
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        return
    apply_paint(x, y)


def on_right_release(_event):
    global paint_mode
    paint_mode = None


def reset_selection():
    global start, end, last_path
    start = None
    end = None
    last_path = []
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            repaint_tile(x, y)
    set_status("Left-click a tile to set the start", COLORS["start"])


def reset_all():
    global grid
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    reset_selection()


def random_maze():
    global grid
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    count = (GRID_SIZE * GRID_SIZE) // 4
    placed = 0
    while placed < count:
        x, y = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)
        if grid[x][y] == 0:
            grid[x][y] = 1
            placed += 1
    reset_selection()


def set_status(text, color=None):
    status_var.set(text)
    status_label.configure(foreground=color or COLORS["text"])


root = tk.Tk()
root.title("Route Finder — A*")
root.configure(bg=COLORS["bg"])
root.resizable(False, False)

diagonal_var = tk.BooleanVar(value=False)
speed_var = tk.IntVar(value=25)  # ms per animation step


def on_diagonal_toggle():
    if start and end:
        run_search()


style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TButton",
    background=COLORS["panel"],
    foreground=COLORS["text"],
    bordercolor=COLORS["panel"],
    focusthickness=0,
    padding=(14, 8),
    font=("SF Pro Display", 11),
)
style.map(
    "TButton",
    background=[("active", COLORS["accent"]), ("pressed", COLORS["accent"])],
    foreground=[("active", COLORS["bg"]), ("pressed", COLORS["bg"])],
)

# Header
header = tk.Frame(root, bg=COLORS["bg"])
header.pack(fill="x", padx=PADDING, pady=(PADDING, 8))

title = tk.Label(
    header,
    text="Route Finder",
    bg=COLORS["bg"],
    fg=COLORS["text"],
    font=("SF Pro Display", 18, "bold"),
)
title.pack(side="left")

subtitle = tk.Label(
    header,
    text="A* pathfinding",
    bg=COLORS["bg"],
    fg=COLORS["muted"],
    font=("SF Pro Display", 11),
)
subtitle.pack(side="left", padx=(10, 0), pady=(6, 0))

# Status bar
status_var = tk.StringVar(value="Left-click a tile to set the start")
status_label = tk.Label(
    root,
    textvariable=status_var,
    bg=COLORS["bg"],
    fg=COLORS["start"],
    font=("SF Pro Display", 11),
    anchor="w",
)
status_label.pack(fill="x", padx=PADDING)

# Canvas
canvas_frame = tk.Frame(root, bg=COLORS["grid"], padx=2, pady=2)
canvas_frame.pack(padx=PADDING, pady=10)

canvas = tk.Canvas(
    canvas_frame,
    width=GRID_SIZE * TILE_SIZE,
    height=GRID_SIZE * TILE_SIZE,
    bg=COLORS["grid"],
    highlightthickness=0,
)
canvas.pack()

gap = 1
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        rect = canvas.create_rectangle(
            x * TILE_SIZE + gap,
            y * TILE_SIZE + gap,
            (x + 1) * TILE_SIZE - gap,
            (y + 1) * TILE_SIZE - gap,
            fill=COLORS["empty"],
            outline="",
        )
        tiles[x][y] = rect

canvas.bind("<Button-1>", on_left_click)
canvas.bind("<Button-2>", on_right_press)
canvas.bind("<Button-3>", on_right_press)
canvas.bind("<B2-Motion>", on_right_drag)
canvas.bind("<B3-Motion>", on_right_drag)
canvas.bind("<ButtonRelease-2>", on_right_release)
canvas.bind("<ButtonRelease-3>", on_right_release)

# Controls
controls = tk.Frame(root, bg=COLORS["bg"])
controls.pack(fill="x", padx=PADDING, pady=(4, 16))

ttk.Button(controls, text="Clear Path", command=clear_path_visual).pack(side="left")
ttk.Button(controls, text="Reset Selection", command=reset_selection).pack(side="left", padx=8)
ttk.Button(controls, text="Random Maze", command=random_maze).pack(side="left")
ttk.Button(controls, text="Reset All", command=reset_all).pack(side="right")

style.configure(
    "TCheckbutton",
    background=COLORS["bg"],
    foreground=COLORS["text"],
    focuscolor=COLORS["bg"],
    font=("SF Pro Display", 11),
)
style.map(
    "TCheckbutton",
    background=[("active", COLORS["bg"])],
    foreground=[("active", COLORS["accent"])],
)
ttk.Checkbutton(
    controls,
    text="Diagonal moves",
    variable=diagonal_var,
    command=on_diagonal_toggle,
).pack(side="right", padx=12)

# Speed slider row
speed_row = tk.Frame(root, bg=COLORS["bg"])
speed_row.pack(fill="x", padx=PADDING, pady=(0, 8))

tk.Label(
    speed_row,
    text="Animation speed",
    bg=COLORS["bg"],
    fg=COLORS["muted"],
    font=("SF Pro Display", 10),
).pack(side="left")

tk.Label(speed_row, text="slow", bg=COLORS["bg"], fg=COLORS["muted"],
         font=("SF Pro Display", 9)).pack(side="left", padx=(10, 4))

style.configure(
    "Speed.Horizontal.TScale",
    background=COLORS["bg"],
    troughcolor=COLORS["panel"],
)
# Inverted: left = slow (high ms delay), right = fast (low ms delay)
ttk.Scale(
    speed_row,
    from_=120,
    to=1,
    orient="horizontal",
    variable=speed_var,
    style="Speed.Horizontal.TScale",
    length=200,
).pack(side="left")

tk.Label(speed_row, text="fast", bg=COLORS["bg"], fg=COLORS["muted"],
         font=("SF Pro Display", 9)).pack(side="left", padx=(4, 0))

# Legend
legend = tk.Frame(root, bg=COLORS["bg"])
legend.pack(fill="x", padx=PADDING, pady=(0, PADDING))


def add_legend(parent, color, label):
    item = tk.Frame(parent, bg=COLORS["bg"])
    item.pack(side="left", padx=(0, 16))
    swatch = tk.Frame(item, bg=color, width=12, height=12)
    swatch.pack(side="left", padx=(0, 6), pady=2)
    swatch.pack_propagate(False)
    tk.Label(item, text=label, bg=COLORS["bg"], fg=COLORS["muted"],
             font=("SF Pro Display", 10)).pack(side="left")


add_legend(legend, COLORS["start"], "Start")
add_legend(legend, COLORS["end"], "End")
add_legend(legend, COLORS["path"], "Path")
add_legend(legend, COLORS["pillar"], "Wall")

tk.Label(
    legend,
    text="Left-click: place • Right-click + drag: paint walls",
    bg=COLORS["bg"],
    fg=COLORS["muted"],
    font=("SF Pro Display", 10),
).pack(side="right")

# Initial pillars for visual interest
for x, y in [(3, 4), (4, 4), (5, 4), (6, 4), (10, 9), (10, 10), (10, 11), (2, 10), (3, 10)]:
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        grid[x][y] = 1
        repaint_tile(x, y)

root.mainloop()
