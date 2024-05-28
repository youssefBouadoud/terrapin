import math

import pygame
from button import Button
import random
from skimage import color
from datetime import datetime

from Player import Player
from mazelib.mazelib import Maze
import mazelib.generate.BacktrackingGenerator
import mazelib.solve.ShortestPath
import mazelib.solve.BacktrackingSolver

PADDING = 50
SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640
MAZE_WIDTH = random.randrange(7, 49, 2)
MAZE_HEIGHT = random.randrange(7, 49, 2)

CELL_SIZE = min(((SCREEN_WIDTH - (2 * PADDING)) // MAZE_WIDTH), ((SCREEN_HEIGHT - (2 * PADDING)) // MAZE_HEIGHT))
print(
    f"maze size: {CELL_SIZE * MAZE_HEIGHT}x{CELL_SIZE * MAZE_WIDTH}, maze size: {MAZE_HEIGHT}x{MAZE_WIDTH}, cell size: {CELL_SIZE}")


def generate_maze(h, w):
    m = Maze()
    h = int((h - 1.0) // 2)
    w = int((w - 1.0) // 2)
    m.generator = mazelib.generate.BacktrackingGenerator.BacktrackingGenerator(h, w)
    m.solver = mazelib.solve.ShortestPath.ShortestPath()
    m.generate_monte_carlo(100, difficulty=random.random())
    m.grid[m.start[0]][m.start[1]] = 0
    m.grid[m.end[0]][m.end[1]] = 0
    return m


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


def draw_maze(surface, m, cell_size):
    maze_map = m.tostring(True, False, nl=False)
    chars = set(maze_map)
    palette = generate_palette(len(chars))
    color_map = dict(zip(chars, palette))
    print(color_map)

    for y in range(m.grid.shape[0]):
        for x in range(m.grid.shape[1]):
            pygame.draw.rect(surface, color_map[maze_map[m.grid.shape[1] * y + x]],
                             pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))


def play(screen):
    screen.fill((0,0,0))
    now = datetime.now()
    maze = generate_maze(MAZE_HEIGHT, MAZE_WIDTH)
    print(maze.grid)
    print(f"it took {(datetime.now() - now).total_seconds()}s to generate maze")
    clock = pygame.time.Clock()
    fps = 60

    maze_surface = pygame.Surface((CELL_SIZE * maze.grid.shape[1], CELL_SIZE * maze.grid.shape[0]))

    draw_maze(maze_surface, maze, CELL_SIZE)

    cx, cy = screen.get_rect().center
    maze_x = maze_surface.get_rect(center=(cx, cy)).x
    maze_y = maze_surface.get_rect(center=(cx, cy)).y

    player = Player(cell_size=CELL_SIZE,
                    absolute=(maze.start[1] * CELL_SIZE + maze_x, maze.start[0] * CELL_SIZE + maze_y),
                    relative=maze.start,
                    maze=maze.grid)
    screen.blit(maze_surface, maze_surface.get_rect(center=(cx, cy)))

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()

        screen.blit(maze_surface, maze_surface.get_rect(center=(cx, cy)))

        current_time = pygame.time.get_ticks()
        all_sprites.update(pressed_keys, current_time)

        all_sprites.draw(screen)

        pygame.display.flip()

        clock.tick(fps)


def main_menu(screen, bg):
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        connect_btn = Button(pygame.Surface(size=(300, 110), masks=(69, 137, 239)), pos=(300, 200), text_input="connect",
                             font=pygame.font.Font("./assets/SF-Pro.ttf", size=75),
                             base_color=(255, 255, 255), hovering_color=(255, 0, 0))

        connect_btn.changeColor(mouse_pos)
        connect_btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if connect_btn.checkForInput(mouse_pos):
                    screen.fill((0, 0, 0))
                    play(screen)

            pygame.display.update()


def main():
    pygame.init()
    icon = pygame.image.load("assets/icon.ico")
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Terrapin")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    main_menu(screen, None)
    pygame.quit()


if __name__ == "__main__":
    main()
