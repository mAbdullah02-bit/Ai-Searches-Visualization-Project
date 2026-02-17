import tkinter as tk
import random
import time
from queue import Queue, PriorityQueue

# ===============================
# CONFIGURATION
# ===============================
GRID_SIZE = 10          # 10x10 grid
CELL_SIZE = 50          # Pixel size for each cell
DYNAMIC_OBSTACLE_PROB = 0.02  # Probability per step
DELAY = 0.1             # Delay for visualization

# Colors
COLOR_EMPTY = "white"
COLOR_WALL = "black"
COLOR_START = "green"
COLOR_TARGET = "red"
COLOR_FRONTIER = "yellow"
COLOR_EXPLORED = "blue"
COLOR_PATH = "orange"
COLOR_DYNAMIC = "gray"

# Movement Directions (Clockwise including diagonals)
MOVES = [
    (-1, 0),  # Up
    (0, 1),   # Right
    (1, 0),   # Down
    (1, 1),   # Bottom-Right
    (0, -1),  # Left
    (-1, -1), # Top-Left
    (-1, 1),  # Top-Right
    (1, -1),  # Bottom-Left
]

# ===============================
# NODE / GRID CLASSES
# ===============================
class Node:
    def __init__(self, row, col, parent=None):
        self.row = row
        self.col = col
        self.parent = parent

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.start = (0, 0)
        self.target = (size-1, size-1)
        self.walls = set()

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def is_empty(self, r, c):
        return (r, c) not in self.walls

    def random_dynamic_obstacle(self):
        # Randomly add a dynamic obstacle
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0 and random.random() < DYNAMIC_OBSTACLE_PROB:
                    self.walls.add((r, c))
                    return (r, c)
        return None

# ===============================
# TKINTER GUI
# ===============================
class PathfinderGUI:
    def __init__(self, master, grid: Grid):
        self.master = master
        self.grid = grid
        self.cells = [[None for _ in range(grid.size)] for _ in range(grid.size)]

        master.title("GOOD PERFORMANCE TIME APP")
        self.canvas = tk.Canvas(master, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE)
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        for r in range(self.grid.size):
            for c in range(self.grid.size):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color = COLOR_EMPTY
                if (r, c) == self.grid.start:
                    color = COLOR_START
                elif (r, c) == self.grid.target:
                    color = COLOR_TARGET
                elif (r, c) in self.grid.walls:
                    color = COLOR_WALL
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.cells[r][c] = rect

    def update_cell(self, row, col, color):
        self.canvas.itemconfig(self.cells[row][col], fill=color)
        self.master.update()
        time.sleep(DELAY)

    def draw_path(self, path):
        for r, c in path:
            if (r, c) != self.grid.start and (r, c) != self.grid.target:
                self.update_cell(r, c, COLOR_PATH)

# ===============================
# SEARCH ALGORITHMS
# ===============================
def bfs(grid: Grid, gui: PathfinderGUI):
    start = Node(*grid.start)
    target = grid.target
    queue = Queue()
    queue.put(start)
    explored = set()
    while not queue.empty():
        current = queue.get()
        r, c = current.row, current.col

        # Dynamic obstacle
        dynamic = grid.random_dynamic_obstacle()
        if dynamic:
            gui.update_cell(dynamic[0], dynamic[1], COLOR_DYNAMIC)

        if (r, c) == target:
            path = []
            while current:
                path.append((current.row, current.col))
                current = current.parent
            return path[::-1]

        if (r, c) in explored:
            continue
        explored.add((r, c))
        gui.update_cell(r, c, COLOR_EXPLORED)

        # Explore neighbors in specified order
        for dr, dc in MOVES:
            nr, nc = r+dr, c+dc
            if grid.in_bounds(nr, nc) and grid.is_empty(nr, nc) and (nr, nc) not in explored:
                queue.put(Node(nr, nc, current))
                gui.update_cell(nr, nc, COLOR_FRONTIER)

    return None

# ===============================
# MAIN EXECUTION
# ===============================
def main():
    root = tk.Tk()
    grid = Grid(GRID_SIZE)

    # Add some static walls
    for _ in range(15):
        r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        if (r, c) not in [grid.start, grid.target]:
            grid.walls.add((r, c))

    gui = PathfinderGUI(root, grid)
    root.update()

    # Run BFS
    path = bfs(grid, gui)
    if path:
        gui.draw_path(path)

    root.mainloop()

if __name__ == "__main__":
    main()

