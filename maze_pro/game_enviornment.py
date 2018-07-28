"""Run a demo game"""

import sys
sys.path.append('..')
import maze_pro.random_mouse as random_mouse
import maze_pro.maze as maze_pro
import numpy as np
import time
from typing import List, Dict
from pygame.locals import *
import pygame

class Sprite():
    """An animated character that is displayed traversing the maze"""

    def __init__(self, img_assets: List[pygame.image.load],
                 interface: maze_pro.PlayerInterface):

        self.img_assets = img_assets
        self.state = img_assets['up'][0]
        self.move_counter = 0
        self.pos = [interface.player_pos.x * 16, interface.player_pos.y * 16]
        self.direction = 'up'
        self.ai = random_mouse.RobertFrostRandomMouse(interface)

    def move(self, direction: str):
        """Shift the sprite 2 pixels in the provided direction"""

        if direction == 'N':
            direction = 'up'
        if direction == 'S':
            direction = 'down'
        if direction == 'W':
            direction = 'left'
        if direction == 'E':
            direction = 'right'

        self.state = self.img_assets[direction][self.move_counter]

        if self.move_counter == 2:
            self.move_counter = 0
        else:
            self.move_counter += 1

        if direction == 'up':
            self.pos[1] = self.pos[1] - 2
        elif direction == 'down':
            self.pos[1] = self.pos[1] + 2
        elif direction == 'left':
            self.pos[0] = self.pos[0] - 2
        elif direction == 'right':
            self.pos[0] = self.pos[0] + 2
        else:
            raise ValueError("Invalid direction " + direction)

    def reached_dest(self) -> bool:
        """Determine if the sprite has shifted completely to the destination"""

        if self.pos[0] != self.ai.interface.player_pos.x * 16:
            return False
        if self.pos[1] != self.ai.interface.player_pos.y * 16:
            return False
        return True

class GameMaze:
    """Manage drawing of maze on screen"""

    def __init__(self, maze: np.array, img_assets: List[pygame.image.load]):
        self.col = maze.dim[0]
        self.row = maze.dim[1]
        self.maze = maze
        self.wall_img = img_assets['wall']
        self.walkable_img = img_assets['walkable']

    def draw(self, display_surf: pygame.display):
        """Iterate over the maze.terrain and load appropiate tile images"""

        for index, tile in np.ndenumerate(self.maze.terrain):
            if tile:
                display_surf.blit(self.walkable_img, (index[0] * 16, index[1] * 16))
            else:
                display_surf.blit(self.wall_img, (index[0] * 16, index[1] * 16))

class App:
    """Drive the game"""

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._wall_img = None
        self._walkable_img = None
        self.maze = None
        self.game_maze = None
        self.interface = maze_pro.PlayerInterface((50, 50), (3, 1, 1))
        self.player = None
        self.clock = pygame.time.Clock()

    def on_init(self):
        """Additional initialization steps"""

        self.maze = self.interface.get_maze()
        self._display_surf = pygame.display.set_mode(
            (800, 800), pygame.HWSURFACE)

        self._running = True
        self._wall_img = pygame.image.load(
            'maze_pro/img_assets/enviornment/shrub.png').convert()
        self._walkable_img = pygame.image.load(
            'maze_pro/img_assets/enviornment/grass.png').convert()

        maze_img_assets = {'wall': self._wall_img,
                           'walkable': self._walkable_img}
        self.game_maze = GameMaze(self.maze, maze_img_assets)

        sprite_img_assets = {}
        for direction in ['up', 'down', 'left', 'right']:
            sprite_img_assets[direction] = []
            for i in range(1, 4):
                img = pygame.image.load('maze_pro/img_assets/sprite_sheets/link/'
                                        + direction
                                        + '_'
                                        + str(i)
                                        + '.png')

                sprite_img_assets[direction].append(img)
        self.player = Sprite(sprite_img_assets, self.interface)
        self.player.ai.interface = self.interface

    def on_event(self, event):
        """Handle event triggers occuring in on_execute"""

        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        """Additional actions to preform every loop"""

        pass

    def on_render(self):
        """Actions to preform along with rendering the maze"""

        self._display_surf.fill((0, 0, 255))
        self.game_maze.draw(self._display_surf)
        self._display_surf.blit(self.player.state,
                                (self.player.pos[0], self.player.pos[1]))
        pygame.display.flip()

    def on_cleanup(self):
        """Preform a graceful exit from the game"""

        pygame.quit()

    def on_execute(self):
        """Process input, and handle event calls"""

        if self.on_init() == False:
            self._running = False

        while self._running:
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if self.player.reached_dest():
                direct, next_tile = self.player.ai.step()
            self.player.move(direct)
            self.clock.tick(60)

            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    APP = App()
    APP.on_execute()
