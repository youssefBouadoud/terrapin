import sys
import random

seed = random.randint(0, 0xFFFF_FFFF)
height = 80
width = height

hex_seed = hex(seed)[2:].upper()
random.seed(hex_seed)

grid = [[0] * width for _ in range(height)]

# Constants for directions
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}


# Recursive backtracking algorithm
def carve_passages_from(cx, cy, grid):
    directions = [N, S, E, W]
    random.shuffle(directions)

    for direction in directions:
        nx, ny = cx + DX[direction], cy + DY[direction]

        if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]) and grid[ny][nx] == 0:
            grid[cy][cx] |= direction
            grid[ny][nx] |= OPPOSITE[direction]
            carve_passages_from(nx, ny, grid)


sys.setrecursionlimit(8000)
carve_passages_from(0, 0, grid)

# Printing the maze as ASCII
print(" " + "_" * (width * 2 - 1))
for y in range(height):
    row = "|"
    for x in range(width):
        row += " " if grid[y][x] & S != 0 else "_"
        if grid[y][x] & E != 0:
            row += " " if (grid[y][x] | grid[y][x + 1]) & S != 0 else "_"
        else:
            row += "|"
    print(row)

# Showing the parameters used to build this maze
print(f"{width} {height} {hex_seed}")
