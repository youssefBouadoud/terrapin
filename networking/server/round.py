import math
import random

import numpy as np
from skimage import color

from mazelib.generate import BacktrackingGenerator
from mazelib.mazelib import Maze
from mazelib.solve import ShortestPath


def generate_palette(num_colors):
    start_hue = random.random()  # Random starting hue
    colors = []

    for i in range(num_colors):
        hue = (start_hue + i / num_colors) % 1.0  # Distribute hues evenly

        # Convert hue to radians
        hue_rad = hue * 2 * math.pi

        C = 70

        # Oklab parameters
        L = 70  # Lightness
        a = C * math.cos(hue_rad)
        b = C * math.sin(hue_rad)

        rgb_color = color.lab2rgb((L, a, b))
        colors.append(tuple(int(c * 255) for c in rgb_color))
    return colors


def generate_map() -> np.matrix:
    maze = Maze()

    height = random.randrange(30, 60, 2)
    width = random.randrange(25, 40, 2)

    height /= 2
    width /= 2

    h = max(height, 7) if height % 2 == 0 else height
    w = max(width, 7) if width % 2 == 0 else width

    h = int((h - 1.0) // 2)
    w = int((w - 1.0) // 2)

    maze.generator = BacktrackingGenerator.BacktrackingGenerator(max(h, 3), max(w, 3))
    maze.solver = ShortestPath.ShortestPath()
    maze.generate_monte_carlo(100, difficulty=random.random())

    maze.grid = np.delete(maze.grid, (0), axis=0)
    maze.grid = np.delete(maze.grid, (np.shape(maze.grid)[1]-1), axis=1)

    mirrored_maze_h = np.flip(maze.grid, 0)
    mirrored_maze_v = np.flip(maze.grid, 1)
    mirrored_maze_hv = np.flip(mirrored_maze_h, 1)

    bigger_maze = np.bmat([[mirrored_maze_h, mirrored_maze_hv], [maze.grid, mirrored_maze_v]])
    bigger_maze = np.delete(bigger_maze, (np.shape(bigger_maze)[0]//2), axis=0)
    bigger_maze = np.delete(bigger_maze, (np.shape(bigger_maze)[1]//2), axis=1)

    bigger_maze = mark_central_goal(bigger_maze)
    return bigger_maze

def mark_central_goal(maze):
    height, width = np.shape(maze)

    if width % 2 == 1 and height % 2 == 1:
        c_x, c_y = height // 2, width // 2
        maze[c_x, c_y] = 2
    else:
        x1, x2 = (height - 1) // 2, height // 2
        y1, y2 = (width - 1) // 2, width // 2
        maze[x2, y1] = 2
        maze[x1, y1] = 2
        maze[x1, y2] = 2
        maze[x2, y2] = 2

    return maze


def generate_map_and_colours():
    m = generate_map()
    return m, generate_palette(len(set(m)) + 4)
