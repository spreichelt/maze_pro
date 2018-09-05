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
import dfs as dfs
import maze
pygame.font.init()
pygame.init()
pygame.mixer.quit()

class Sprite():
    """An animated character that is displayed traversing the maze

    Members:
        img_assets: a dictionary mapping image labels to pygame.Surfaces
        state: The current image used to render sprite
        direction: The direction the spite is traveling to reach destination
        ai: A class implementing a step() function that returns next destination
        move_counter: Used to cycle images in animation
        pos: The sprites position (in pixels) as a maze.Tile object
        dest: The destination returned by ai.step()
        graph_surf: Surface displaying sprites movement by coloring a graph
        last_drawn: Used to differentiate where the sprite is v. where it has been

    Methods:
        move(): Animates movement of sprite, and drawing of graph according to 
            ai.step() instructions
        update_graph(): Determines whether to draw a node or edge and calls the
            appropriate function
        update_node(): Colors the node at the sprite position
        update_edge(): Colors the edge at the sprite position
        is_node(): used to determine is the sprite is on a node or an edge
        color_trail(): Restores the sprites previous position to a different color,
            differentiating where the sprite is v. where it has been
        reached_dest(): Determine if the sprites animation sequence has brought it
            to the destination tile
        win_animation(): Preform an animation sequence when the sprite has reached
            the maze exit

 
    """

    def __init__(self, img_assets: List[pygame.Surface], resources):

        self.img_assets = img_assets
        self.state = img_assets['up'][0]
        self.direction = 'up'
        self.ai = dfs.DFS((50, 50), resources)
        self.move_counter = 0
        self.pos = Tile(self.ai.interface.player_pos.x * 16,
                        self.ai.interface.player_pos.y * 16)
        self.dest = self.ai.interface.player_pos
        self.graph_surf = pygame.Surface((800, 800), pygame.SRCALPHA)
        self.graph_surf.fill((0, 0, 0, 0))
        self.last_drawn = self.pos.x + 8, self.pos.y + 8

    def move(self, display_surf: pygame.display):
        """Shift the sprite 2 pixels in the provided direction

        Return False if the current position is not a winning tile,
        True if the current position is a winning tile. When the player
        is on a winning tile, run an alternate animation

        """

        # If current position is a maze exit
        self.update_graph()
        if self.ai.interface.tile_type(self.ai.interface.player_pos) == 3:
            if(self.reached_dest()):
                self.win_animation(display_surf)
                return True

        if self.reached_dest():
            self.direction, self.dest = self.ai.step()

        if self.move_counter == 2:
            self.move_counter = 0
        else:
            self.move_counter += 1

        self.state = self.img_assets[self.direction][self.move_counter]

        if self.direction == 'up':
            self.pos.y = self.pos.y - 2
        elif self.direction == 'down':
            self.pos.y = self.pos.y + 2
        elif self.direction == 'left':
            self.pos.x = self.pos.x - 2
        elif self.direction == 'right':
            self.pos.x = self.pos.x + 2
        else:
            raise ValueError("Invalid direction " + self.direction)

        return False

    def update_graph(self):
        """Update graph surface overlay"""
        if self.reached_dest() and self.is_node(self.ai.interface.player_pos):
            self.update_node()
        else:
            self.update_edge()

    def update_node(self):
        x_pos = self.pos.x + 8
        y_pos = self.pos.y + 8
        pygame.draw.circle(self.graph_surf, (100, 150, 200), (x_pos, y_pos), 6)
        self.color_trail()
        self.last_drawn = x_pos, y_pos

    def update_edge(self):
        start = [a + 8 for a in self.pos]
        if self.direction is 'left':
            end = [start[0] - 2, start[1]]
        elif self.direction is 'right':
            end = [start[0] + 2, start[1]]
        elif self.direction is 'down':
            end = [start[0], start[1] + 2]
        elif self.direction is 'up':
            end = [start[0], start[1] - 2]

        pygame.draw.line(self.graph_surf, (100, 150, 200), start, end, 1)

    def is_node(self, pos):

        def is_walkable(position):
            if self.ai.interface.player_maze.terrain[position] != 1:
                return True
            else:
                return False

        tiles = {'up':(pos.x, pos.y - 1),
                          'down':(pos.x, pos.y + 1),
                          'left':(pos.x - 1, pos.y),
                          'right':(pos.x + 1, pos.y)}

        walkable = {direct : is_walkable(tiles[direct]) for direct in tiles.keys()}
        num_true = sum(1 for condition in walkable.values() if condition)

        if num_true is 1:
            return True
        elif (walkable['up'] or walkable['down']) and (walkable['left'] or walkable['right']):
            return True

        return False

    def color_trail(self):
        if self.last_drawn is None:
            pass

        pygame.draw.circle(self.graph_surf, (100, 200, 150), self.last_drawn, 6)
        pygame.draw.line(self.graph_surf,
                         (100, 200, 150),
                         (self.last_drawn[0], self.last_drawn[1]),
                         (self.pos.x + 8, self.pos.y + 8),
                         1)

    def reached_dest(self) -> bool:
        """Determine if the sprite has shifted completely to the destination"""

        if self.pos.x != self.ai.interface.player_pos.x * 16:
            return False
        if self.pos.y != self.ai.interface.player_pos.y * 16:
            return False
        return True

    def win_animation(self, display_surf):
        """Preform a _victory dance_ style win animation"""

        direct = ['down', 'right', 'up', 'left', 'down']
        self.move_counter = 0
        for direction in direct:
            pygame.event.pump()
            for i in range(3):
                self.state = self.img_assets[direction][i]
                display_surf.blit(self.state, (self.pos.x, self.pos.y))
                pygame.display.flip()


class GameMaze:
    """Manage drawing of maze on screen"""

    def __init__(self, maze: maze.Maze,
                 img_assets: List[pygame.image.load], mode):
        self.maze = maze
        self.mini_map = pygame.Surface((200, 200))
        self.resource = {'tiles': [], 'collected': 0, 'available': 0}
        self.images = img_assets
        self.start_time = time.time()
        self.count = 0
        self.maze_surf = self.draw_maze()
        self.graph_surf = self.draw_graph()
        self.mini_map.fill((0,0,0))
        self.mode = mode

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

    def draw_graph(self):

        surf = pygame.Surface((1056, 800))
        surf.fill((0, 0, 0))
        for index, maze_tile in numpy.ndenumerate(self.maze.terrain):
            if maze_tile:
                x_pos = index[0] * 16 + 8
                y_pos = index[1] * 16 + 8
                surf, need_node = self.draw_graph_edges(surf, index)
                if need_node:
                    pygame.draw.circle(
                            surf, (255, 255, 255), (x_pos, y_pos), 6)

        self.draw_ui(surf)
        self._draw_mini_map(surf)

        return surf

    def draw_graph_edges(self, surf, node):

        x_pos = node[0] * 16 + 8
        y_pos = node[1] * 16 + 8
        edges = {direct : False for direct in ['up', 'down', 'left', 'right']}
        if self.maze.terrain[node[0] + 1][node[1]]:
            edges['down'] = True
            pygame.draw.line(
                surf, (255, 255, 255), (x_pos, y_pos), (x_pos + 8, y_pos), 1)
        if self.maze.terrain[node[0] - 1][node[1]]:
            edges['up'] = True
            pygame.draw.line(
                surf, (255, 255, 255), (x_pos, y_pos), (x_pos - 8, y_pos), 1)
        if self.maze.terrain[node[0]][node[1] + 1]:
            edges['left'] = True
            pygame.draw.line(
                surf, (255, 255, 255), (x_pos, y_pos), (x_pos, y_pos + 8), 1)
        if self.maze.terrain[node[0]][node[1] - 1]:
            edges['right'] = True
            pygame.draw.line(
                surf, (255, 255, 255), (x_pos, y_pos), (x_pos, y_pos - 8), 1)

        num_true = sum(1 for condition in edges.values() if condition)
        need_node = False
        if num_true is 1:
            need_node = True
        elif (edges['up'] or edges['down']) and (edges['left'] or edges['right']):
            need_node = True

        return surf, need_node

    def draw(self, display_surf: pygame.display,
             visible_tiles: Dict[maze.Tile, int],
             pos: maze.Tile,
             mode: str):
        """Iterate over the maze.terrain and load appropiate tile images"""


        # Draw maze
        self.update_mini_map(visible_tiles)
        if mode is "maze":
            display_surf.blit(self.maze_surf, (0, 0))
        elif mode is "graph":
            display_surf.blit(self.graph_surf, (0, 0))
        else:
            raise ValueError("Invalid game mode: " + mode)

        self.update_stats(display_surf)

        # Create shaded region + sprites vision circle
        display_fog = self.images['fog'].copy()
        pygame.draw.circle(display_fog, (0, 0, 0, 0), (pos.x + 8, pos.y + 8),
                           random.randint(32, 34), 0)
        
        if mode is "maze":
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
            if self.mode is "find_exit":
                display_surf.blit(self.images['door'], (tile.x * 16, tile.y * 16))
            else:
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
        myfont = pygame.font.Font('maze_pro/assets/fonts/breathe_fire.otf', 20)
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

    def win_animation(self, display_surf: pygame.display, player: Sprite):
        """Win animation sequence"""

        pygame.event.pump()
        display_surf.blit(self.images['door'], (player.pos.x,
                                                player.pos.y))


        myfont = pygame.font.Font('maze_pro/assets/fonts/breathe_fire.otf', 50)

        congrats = myfont.render("Congratulations!", True, (0, 0, 0))
        display_surf.fill((100, 255, 50), (200, 380, 400, 80))
        display_surf.blit(congrats, (250, 400))
        pygame.display.flip()

        tick = time.time()
        while True:
            pygame.event.wait()
            if time.time() - tick > 5.0:
                break


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

        myfont = pygame.font.Font('maze_pro/assets/fonts/breathe_fire.otf', 20)
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

        myfont = pygame.font.Font('maze_pro/assets/fonts/breathe_fire.otf', 20)
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

    def __init__(self, mode, resources):
        self.mode = mode
        self.resources = resources
        self._running = True
        self._display_surf = None
        self.images = {}
        self.maze = None
        self.game_maze = None
        self.player = None
        self.clock = pygame.time.Clock()
        self.display_mode = "maze"

    def on_init(self):
        """Additional initialization steps"""

        self._display_surf = pygame.display.set_mode(
            (1056, 800), pygame.HWSURFACE)

        img_directory = 'maze_pro/assets/img/sprite_sheets/link/'
        temp = load_images(img_directory)
        sprite_img_assets = {}
        for direction in ['up', 'down', 'left', 'right']:
            images = [img for key, img in temp.items() if direction in key]
            sprite_img_assets[direction] = images

        self.player = Sprite(sprite_img_assets, self.resources)
        self.maze = self.player.ai.interface.get_maze()


        self._running = True

        img_directory = 'maze_pro/assets/img/enviornment/'
        self.images = load_images(img_directory)

        self.game_maze = GameMaze(self.maze.maze,
                                  self.images,
                                  self.mode)

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
                            self.player.pos,
                            self.display_mode)
        if self.display_mode is 'maze':
            self._display_surf.blit(self.player.state,
                                    (self.player.pos.x, self.player.pos.y))
        elif self.display_mode is 'graph':
            self._display_surf.blit(self.player.graph_surf, (0, 0))

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
            if keys[pygame.K_g]:
                self.display_mode = "graph"
            elif keys[pygame.K_m]:
                self.display_mode = "maze"

            if self.player.move(self._display_surf):
                self.game_maze.win_animation(self._display_surf, self.player)
                self.on_cleanup()
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
    APP = App("find_exit")
    APP.on_execute()

