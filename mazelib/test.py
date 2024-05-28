from mazelib import Maze
from generate.BacktrackingGenerator import BacktrackingGenerator
from solve.ShortestPath import ShortestPath

m = Maze()
m.generator = BacktrackingGenerator(50, 50)
m.solver = ShortestPath()
m.generate_monte_carlo(100, 5, 0)
print(len(m.solutions[0]))
print(m.tostring(True, True))
m.generate_monte_carlo(100, 5, 1)
m.solutions = [m.solutions[0]]
print(len(m.solutions[0]))
print(m.tostring(True, True))
