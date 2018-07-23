import random
import copy
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib import animation
import maze_pro.maze as maze

class Player():
    """Handles player data and interation with maze"""

    def __init__(self, dimensions, resource_allocation):
        self.interface = maze.PlayerInterface(dimensions, resource_allocation)
        self.maze = np.zeros(dimensions, dtype=int)
        self.animate_maze = np.zeros(dimensions, dtype=int)
        self.direction = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    def animated_find_resource(self):
        """Self explanitory"""

        self.update_maze(self.interface.current_visible_tiles())
        visited = {}
        path = [self.interface.player_pos]
        fig = pyplot.figure(figsize=(10, 10))
        pyplot.xticks([]), pyplot.yticks([])
        imgplot = pyplot.imshow(self.animate_maze, interpolation='nearest')

        def animate_step(frame):
            self.step(visited, path)
            imgplot.set_data(self.animate_maze)
            return imgplot

        anim = animation.FuncAnimation(fig, animate_step, frames=20, interval=100)
        pyplot.show()

    def find_resource(self):
        """Move until a resource is found"""
        self.update_maze(self.interface.current_visible_tiles())

        visited = {}
        path = [self.interface.player_pos]

        while self.maze[self.interface.player_pos.x][self.interface.player_pos.y] != 3:
            self.step(visited, path)

        return path, visited

    def is_junction(self, tile):
        """Return True if tile is the center of a junction"""

        neighbors = self.walkable_tiles(tile)
        if len(neighbors) > 2:
            return True
        return False

    def is_visited(self, tile, visited):
        """Return True if the tile has been visited"""

        if tile in visited:
            return True
        return False

    def backtrack(self, visited, path):
        """Return a path to nearest known junction"""

        k = len(path)
        for tile in reversed(path):
            k = k - 1
            if self.is_junction(tile):
                break
        ret_path = list(reversed(path[k:-2]))

        move_dir = random.choice(list(self.direction.keys()))
        for tile in ret_path:
            try:
                move_dir = self.move(tile, {}, [])
                break
            except ValueError:
                print("Path: " + str(path))
                print("ret_path: " + str(ret_path))
                print(str(self.position) + '->' + str(tile))
                raise ValueError('What Do?')

        return move_dir

    def step(self, visited, path):
        """Return the next tile to visit"""

        possible_tiles = self.walkable_tiles()
        never_visited = [x for x in possible_tiles if x not in visited]
        dest = None
        if never_visited:
            dest = random.choice(never_visited)
            visited[dest] = 0
        else:
            least_traveled = possible_tiles[0]
            for tile in possible_tiles:
                if visited[tile] < visited[least_traveled]:
                    least_traveled = tile
            dest = least_traveled

        observed_tiles = self.interface.move(dest)
        self.update_maze(observed_tiles)
        visited[dest] = visited[dest] + 1
        path.append(dest)

    def update_maze(self, observed_tiles):
        """Updates players view of the maze with data from last move"""

        for tile, tile_type in observed_tiles.items():
            self.maze[tile.x][tile.y] = tile_type

        self.animate_maze = np.copy(self.maze)
        self.animate_maze[self.interface.player_pos.x][self.interface.player_pos.y] = -1

    def walkable_tiles(self):
        """Return set of tiles adjacent to player that can be walked on"""

        tiles = []
        pos = self.interface.player_pos
        for offset in self.direction.values():
            tile = maze.Tile(pos.x + offset[0], pos.y + offset[1])
            if self.is_walkable(tile):
                tiles.append(tile)

        return tiles

    def is_walkable(self, tile):
        """Return True if the given tile is not a wall"""

        tile_value = self.maze[tile.x][tile.y]
        if tile_value == 3:
            return True
        if tile_value == 2:
            return True
        if tile_value == 1:
            return False
        if tile_value == 0:
            raise ValueError('Tile: ' + str(tile) + ' is undiscovered')

    def get_direction(self, dest_tile):
        """Return the direction of a move to dest_tile from self.position"""

        x_, y_ = dest_tile.x - self.position.x, dest_tile.y - self.position.y
        for direction, offsets in self.direction.items():
            if offsets == (x_, y_):
                return direction

        raise ValueError('Not a valid move')

    def print_maze(self):
        """build and display a maze"""

        pyplot.figure(figsize=(10, 10))
        pyplot.imshow(self.maze, cmap="Greys_r", interpolation='nearest')
        pyplot.xticks([]), pyplot.yticks([])
        pyplot.show()
