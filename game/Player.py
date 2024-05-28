import pygame
from copy import deepcopy

class Player(pygame.sprite.Sprite):
    def __init__(self, cell_size, absolute, relative, maze, colour):
        pygame.sprite.Sprite.__init__(self)
        self.cell_size = cell_size
        self.maze = maze
        self.cooldown_time = 100  # Cooldown time in milliseconds
        self.last_move_time = 0
        self.move_in_previous_update = False

        self.image = pygame.Surface((cell_size, cell_size))
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.rect.topleft = absolute
        self.relative = relative

    def update(self, pressed_keys, current_time):
        # Check if any movement key is pressed
        move_keys_pressed = any(
            pressed_keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])

        # If any movement key is pressed and not moved in the previous update, or cooldown has elapsed, move the player
        if move_keys_pressed and (
                not self.move_in_previous_update or current_time - self.last_move_time > self.cooldown_time):
            self.move_player(pressed_keys)
        self.move_in_previous_update = move_keys_pressed

    def move_player(self, pressed_keys):
        # Calculate the new position based on pressed keys
        new_rect = self.rect.copy()
        relative = [self.relative[0], self.relative[1]]
        if pressed_keys[pygame.K_UP]:
            new_rect.move_ip(0, -self.cell_size)
            relative[0] -= 1
        elif pressed_keys[pygame.K_DOWN]:
            new_rect.move_ip(0, self.cell_size)
            relative[0] += 1
        elif pressed_keys[pygame.K_LEFT]:
            new_rect.move_ip(-self.cell_size, 0)
            relative[1] -= 1
        elif pressed_keys[pygame.K_RIGHT]:
            new_rect.move_ip(self.cell_size, 0)
            relative[1] += 1

        # Check for collisions with maze walls
        if not self.check_collision(relative):
            self.rect = new_rect
            self.relative = relative
            self.last_move_time = pygame.time.get_ticks()

    def check_collision(self, relative):
        if relative[0] < 0 or relative[1] < 0 or relative[0] >= \
                self.maze.shape[0] or relative[1] >= self.maze.shape[1] or \
                self.maze[relative[0]][
                    relative[1]] == 1:
            return True
        return False
