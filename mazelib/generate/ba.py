from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
from mazelib.mazelib import Maze

a = Maze()
a.generator = BacktrackingGenerator(10, 10)
a.generate()
print(a.grid)