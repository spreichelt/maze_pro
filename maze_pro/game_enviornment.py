"""Run a demo game"""

import random
import sys
import os
import time
from typing import List, Dict
import numpy
import pygame.locals
import pygame
sys.path.append('..')
import maze_pro.dfs as dfs
import maze_pro.maze
pygame.font.init()
pygame.init()
pygame.mixer.quit()

class Sprite():
    """An animated character that is displayed traversing the maze"""

    def __init__(self, img_assets: List[pygame.Surface]):

        self.img_assets = img_assets
        self.state = img_assets['up'][0]
        self.direction = 'up'
        self.ai = dfs.DFS((50, 50), (30, 1, 1))
        self.move_counter = 0
        self.pos = [self.ai.interface.player_pos.x * 16,
                    self.ai.interface.player_pos.y * 16]

    def move(self, direction: str):
        """Shift the sprite 2 pixels in the provided direction"""

        if self.move_counter == 2:
            self.move_counter = 0
        else:
            self.move_counter += 1

        self.state = self.img_assets[direction][self.move_counter]

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

    def __init__(self, maze: maze_pro.maze.Maze,
                 img_assets: List[pygame.image.load]):
        self.maze = maze
        self.mini_map = pygame.Surface((200, 200))
        self.resource = {'tiles': [], 'collected': 0, 'available': 0}
        self.images = img_assets
        self.start_time = time.time()
        self.count = 0
        self.maze_surf = self.draw_maze()
        self.mini_map.fill((0,0,0))

    def draw_maze(self):
        surf = pygame.Surface((1056, 800))
        for index, maze_tile in numpy.ndenumerate(self.maze.terrain):
            if not maze_tile:
                surf.blit(self.images['wall'], (index[0] * 16,
                                                        index[1] * 16))
            else:
                surf.blit(self.images['walkable'], (index[0] * 16,
                                                            index[1] * 16))
        self.draw_ui(surf)
        self._draw_mini_map(surf)

        return surf

    def draw(self, display_surf: pygame.display,
             visible_tiles: Dict[maze_pro.maze.Tile, int],
             pos: maze_pro.maze.Tile):
        """Iterate over the maze.terrain and load appropiate tile images"""


        # Draw maze
        self.update_mini_map(visible_tiles)
        display_surf.blit(self.maze_surf, (0, 0))
        self.update_stats(display_surf)

        # Create shaded regiong + sprites vision circle
        display_fog = self.images['fog'].copy()
        pygame.draw.circle(display_fog, (0, 0, 0, 0), (pos[0] + 8, pos[1] + 8),
                           random.randint(32, 34), 0)

        display_surf.blit(display_fog, (0, 0))

        # Illuminate found resource tiles
        for tile, tile_type in visible_tiles.items():
            if tile_type == 3 and tile not in self.resource['tiles']:
                pygame.draw.circle(self.images['fog'], (0, 0, 0, 0),
                                   (tile.x * 16 + 8, tile.y * 16 + 8),
                                   12, 0)
                self.resource['tiles'].append(tile)

        # Draw found resource tiles
        for tile in self.resource['tiles']:
            display_surf.blit(self.images['mineral'], (tile.x * 16, tile.y * 16))

    def draw_ui(self, surf: pygame.display):
        """draw the maze ui area"""

        for x in range(800, 1056, 16):
            for y in range(0, 800, 16):
                if x == 800 or y == 0 or y == 784 or x == 1040:
                    surf.blit(self.images['wall'], (x, y))
                else:
                    surf.blit(self.images['walkable'], (x, y))

        return surf

    def update_mini_map(self, visible_tiles):
        for tile, tile_type in visible_tiles.items():
            if tile_type == 2:
                self.maze_surf.blit(
                        self.images['mini_walkable'], (tile.x * 4 + 828, tile.y * 4 + 572))
            elif tile_type == 3:
                temp = pygame.Surface((4, 4))
                temp.fill((150, 255, 255))
                self.maze_surf.blit(
                        temp, (tile.x * 4 + 828, tile.y * 4 + 572))

    def _draw_mini_map(self, display_surf: pygame.display):
        """Redraw minimap"""

        for y in range(572, 772, 4):
            for x in range(828, 1028, 4):
                display_surf.fill((0, 0, 0), (x, y, 4, 4))

    def update_stats(self, display_surf: pygame.display):
        """Update the game statistics displayed on screen"""

        self.count += 1
        display_time = time.time()
        myfont = pygame.font.Font('maze_pro/fonts/breathe_fire.otf', 20)
        tiles_traversed = myfont.render(
            'Tiles Traversed: ' + str(self.count // 8), True, (0, 0, 0))
        resources_found = myfont.render(
            'Resources Found: ' + str(len(self.resource['tiles'])),
            True, (0, 0, 0))
        resources_collected = myfont.render(
            'Resources Collected: ' + str(self.resource['collected']),
            True, (0, 0, 0))
        game_clock = myfont.render(
            'Time Played: ' + str((int(display_time - self.start_time))),
            True, (0, 0, 0))

        display_surf.blit(tiles_traversed, (830, 50))
        display_surf.blit(resources_found, (830, 100))
        display_surf.blit(resources_collected, (830, 150))
        display_surf.blit(game_clock, (830, 200))


class MazeConstructor:
    """Manages the animation of maze construction"""

    def __init__(self, construction_data, img_assets, display_surf):
        self.color_map = construction_data['color_map']
        self.steps = construction_data['steps']
        self.images = img_assets
        self.animate_flags = {'draw_path': True,
                              'draw_next_clear': False,
                              'skip_animation': False}
        self.display_surf = display_surf
        self.clock = pygame.time.Clock()
        self.statistics = {'cleared_tiles' : 0, 'visited_tiles': 0}

        self.display_surf.fill((100, 100, 100, 100), (0, 0, 800, 800))
        self.restore_walls()
        self.display_controls()

    def restore_walls(self):
        """Fill in temp walk tiles as wall tiles"""

        for i in range(0, 800, 16):
            for j in range(0, 800, 16):
                if self.display_surf.get_at((i, j)) == (100, 100, 100, 255):
                    self.display_surf.blit(self.images['wall'], (i, j))
        pygame.display.flip()

    def color_tile(self, color, tile):
        """Render a tile using the provided color

        color can specify an image using a string, or an RBG value using a
        tuple i.e. (R, B, G)
        """

        if isinstance(color, str):
            self.display_surf.blit(self.images[color],
                                   (tile[0] * 16, tile[1] * 16))
        elif isinstance(color, tuple):
            pygame.draw.rect(self.display_surf,
                             color,
                             (tile[0] * 16, tile[1] * 16, 16, 16))
        else:
            raise ValueError("Unknown tile color: " + color)

    def read_keys(self, keys, color):
        if keys[pygame.K_s]:
            self.animate_flags['draw_path'] = False
        if keys[pygame.K_c]:
            if color is 'clear':
                return False
            else:
                self.animate_flags['draw_next_clear'] = True
                self.restore_walls()
                return True
        if keys[pygame.K_d]:
                self.animate_flags['draw_next_clear'] = True
                self.animate_flags['skip_animation'] = True
                self.restore_walls()
                if color is 'clear':
                    return False
                return True
        if keys[pygame.K_p]:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    break
        return False

    def animation_loop(self):
        """Drive the animation"""

        pygame.event.pump()
        pygame.display.flip()

        for step in self.steps:
            self.animate_flags['draw_path'] = True
            color, tiles = next(iter(step.items()))
            self.update_statistics(color, tiles)

            if self.animate_flags['skip_animation']:
                self.animate_flags['draw_path'] = False
                self.animate_flags['draw_next_clear'] = True

            if self.animate_flags['draw_next_clear']:
                if color is not 'clear':
                    continue
                else:
                    self.animate_flags['draw_next_clear'] = False

            self.animate_step(tiles, color)
        time.sleep(1)

    def animate_step(self, tiles, color):
        """Animate a single step"""

        for tile in tiles:
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            if self.read_keys(keys, color):
                break
            self.color_tile(self.color_map[color], tile)
            if self.animate_flags['draw_path']:
                pygame.display.flip()
        pygame.display.flip()

    def display_controls(self):

        myfont = pygame.font.Font('maze_pro/fonts/breathe_fire.otf', 20)
        skip_step = myfont.render(
                's: skip the current step', True, (0, 0, 0))
        next_clear = myfont.render(
                'c: skip until clear', True, (0, 0, 0))
        complete_animation = myfont.render(
                'd: rapid finish', True, (0, 0, 0))
        pause = myfont.render(
                'p: pause animation', True, (0, 0, 0))
        resume = myfont.render(
                'r: resume animation', True, (0, 0, 0))

        align = 50
        for control in [skip_step, next_clear, complete_animation, pause, resume]:
            self.display_surf.blit(control, (830, align))
            align = align + 50

    def update_statistics(self, color, tiles):

        if color is 'clear':
            self.statistics['cleared_tiles'] += len(tiles)
        if color is 'seek':
            self.statistics['visited_tiles'] += len(tiles)

        myfont = pygame.font.Font('maze_pro/fonts/breathe_fire.otf', 20)
        cleared = myfont.render(
                'Tiles Cleared: ' + str(self.statistics['cleared_tiles']),
                True, (0, 0, 0))
        visited = myfont.render(
                'Tiles Visited: ' + str(self.statistics['visited_tiles']),
                True, (0, 0, 0))

        for col in range(816, 1040, 16):
            for row in range(300, 380, 16):
                self.display_surf.blit(self.images['walkable'], (col, row))
        self.display_surf.blit(cleared, (830, 300))
        self.display_surf.blit(visited, (830, 350))


class App:
    """Drive the game"""

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.images = {}
        self.maze = None
        self.game_maze = None
        self.player = None
        self.clock = pygame.time.Clock()

    def on_init(self):
        """Additional initialization steps"""

        self._display_surf = pygame.display.set_mode(
            (1056, 800), pygame.HWSURFACE)

        img_directory = 'maze_pro/img_assets/sprite_sheets/link/'
        temp = load_images(img_directory)
        sprite_img_assets = {}
        for direction in ['up', 'down', 'left', 'right']:
            images = [img for key, img in temp.items() if direction in key]
            sprite_img_assets[direction] = images

        self.player = Sprite(sprite_img_assets)
        self.maze = self.player.ai.interface.get_maze()


        self._running = True

        img_directory = 'maze_pro/img_assets/enviornment/'
        self.images = load_images(img_directory)

        self.game_maze = GameMaze(self.maze.maze,
                                  self.images)

        self.game_maze.draw_ui(self._display_surf)
        pygame.display.flip()

        maze_constructor = MazeConstructor(self.maze.construction_json,
                                           self.images,
                                           self._display_surf)
        maze_constructor.animation_loop()
        del maze_constructor

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
        self.game_maze.draw(self._display_surf,
                            self.player.ai.interface.current_visible_tiles(),
                            self.player.pos)
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
            _ = pygame.key.get_pressed()

            if self.player.reached_dest():
                direct, _ = self.player.ai.step()
            self.player.move(direct)
            self.clock.tick(20)

            self.on_loop()
            self.on_render()
        self.on_cleanup()


def load_images(directory):
    """Load all .png files from the provided directory into a dictionary"""

    images = {}
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            images[filename[:-4]] = pygame.image.load(
                os.path.join(directory, filename)).convert_alpha()

    return images

if __name__ == "__main__":
    APP = App()
    APP.on_execute()
