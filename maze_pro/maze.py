"""Temp module docstring"""

import time
import random
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as pyplot
from numpy.random import random_integers as rand
import copy


@dataclass
class Tile:
    """Object representing a tile in the maze at position x,y"""
    x: int
    y: int

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

class Resources():
    """Handles placement, tracking, and mining of resources in a maze

    Members:
        stockpile (int): The total amount of resources available for placement
        __min (int): Minimum resource that can be placed in one location
        __max (int): Maximum resource that can be placed in one location

    Methods:
        place(): Place random amount of resource at provided location
        mine(): Simulate mining resource
    """

    def __init__(self, resource_allocation):
        self.stockpile = resource_allocation[0]
        self.__min = resource_allocation[1]
        self.__max = resource_allocation[2]
        self.locations = {}

    def place(self, location):
        """Given a tile, allocate random amount of resource from the stockpile

        in the range of __min to __max

        """

        amount = min(random.randint(self.__min, self.__max), self.stockpile)
        self.locations[location] = amount
        self.stockpile = self.stockpile - amount

    def mine(self, capacity, rate, source):
        """Mine resource up to max(capacity, available resource at source)

        returning after a simulated mining delay based on rate

        """

        if source not in self.locations:
            return 0

        available = self.locations[source]['amount']
        mined = min(capacity, available)
        time.sleep(capacity / rate)
        self.locations[source] = available - mined

        return mined

class PlayerInterface():
    """Interface a player can use to interact with a maze, restricts access

    to the maze to enforce vision restrictions of the maze

    Members:
        __maze: Maze class object
        player_pos: The player's current position in the maze

    Methods:
        move(): Preform a move from player_pos to a destination tile
        current_visible_tiles(): Return current visible tiles from player_pos 
        __discovered_tiles(): Return visible tiles from given tile
        __resource_data(): Return amount of resource at provided tile (or None)

    """

    def __init__(self, dimensions, resource_allocation):
        self.__maze = Maze(dimensions, resource_allocation)
        self.player_pos = self.__maze.player_start

    def move(self, dest_tile):
        """Move player from current position to dest_tile with error checking

        to ensure that an attempted move is to a tile adjacent to the players
        current position, and that the destination tile is not a wall tile

        """

        if self.__maze.is_wall(dest_tile):
            raise ValueError('Dest: ' + str(dest_tile) + ' is a wall tile')

        if dest_tile in self.__maze.adjacent_tiles(self.player_pos):
            self.player_pos = copy.copy(dest_tile)
        else:
            raise ValueError(str(self.player_pos) + ' -> ' + str(dest_tile)
                             + ' ILLEGAL MOVE')

        return self.__discovered_tiles(dest_tile)

    def current_visible_tiles(self):
        """A public facing version of __discoverd_tiles that restricts the

        the query to the players current position

        """

        return self.__discovered_tiles(self.player_pos)

    def __discovered_tiles(self, pos):
        """Returns a dictionary of tiles obersvable from the provided position

        that maps tiles to the type of tile (wall, not wall, resource)

        """

        offsets = [(x, y) for x in range(-1, 2) for y in range(-1, 2)]
        tiles = [Tile(x + pos.x, y + pos.y) for (x, y) in offsets]
        visited_tiles = {}
        for tile in tiles:
            if self.__resource_data(tile):
                visited_tiles[tile] = 3
            elif self.__maze.is_wall(tile):
                visited_tiles[tile] = 1
            else:
                visited_tiles[tile] = 2

        return visited_tiles

    def __resource_data(self, tile):
        """Returns None if the provided tile is not a resource tile, otherwise

        returns the amount of resource at the provided tile

        """

        if tile not in self.__maze.resources.locations:
            return None

        return self.__maze.resources.locations[tile]

class Maze():
    """Random construction of a data structure representing a maze

    Members:
        dim: Dimensions of a maze (x, y)
        maze_terrain: A bool numpy array the encodes a maze using False for
                      wall tiles and True for walkable tiles
        resource_allocation: Data used to construct a Resource class to manage
                             available resources in maze

        player_start: The starting location for players traversing the maze
        resources: A Resource class object

    Methods:
        __build_maze(): Drives the random processes that constuct a maze
        random_walk(): Preform a random walk from provided tile until a tile
                       that is not a wall is discovered
        __clear_zone(): Clear tiles in a 3x3 square centered around the
                        provided tile
        __clear_tiles(): Flip all tiles to True in the provided list of tiles
        random_wall_tile(): Return a randomly selected wall tile
        random_direction(): Return a randomly selected wall tile adjacent to
                            the paramater tile
        adjacent_tiles(): Return a list of valid adjacent tiles that are in
                          walkable directions (North/South/East/West)
        valid_tiles(): Return True if tile is within the boundry of the maze
        print_maze_terrain(): Display maze such that wall tiles are black and
                              walkable tiles are white
        is_wall(): Return True if the provided tile is a wall tile

    """


    def __init__(self, dimensions, resource_allocation):

        self.dim = dimensions
        self.maze_terrain = np.zeros(dimensions, dtype=bool) # False == Wall
        self.resource_allocation = resource_allocation
        self.player_start = None
        self.resources = Resources(resource_allocation)

        self.__build_maze()

    def __build_maze(self):
        """Starting point for building data structures required for maze

        Alters the maze_terrain member using a version of Wilson's maze
        creation algorithm. Random tiles are assigned to resources until
        the stockpile is exhausted, then the remainder of the maze is
        randomly build until no more tiles can be randomly selected.

        """

        self.player_start = self.random_wall_tile(self.maze_terrain)
        self.__clear_zone(self.player_start)
        valid_tiles = np.copy(self.maze_terrain)
        valid_tiles[0, :] = valid_tiles[-1, :] = True
        valid_tiles[:, 0] = valid_tiles[:, -1] = True

        # Place resource and connect to maze through a random walk
        while self.resources.stockpile > 0:
            tile = self.random_wall_tile(valid_tiles)
            self.resources.place(tile)

            walk = self.random_walk(tile)
            self.__clear_tiles(walk)
            walk = [self.adjacent_tiles(x) for x in walk]
            walk = [x for sublist in walk for x in sublist]
            valid_tiles = self.__clear_tiles(walk, valid_tiles)

        while not np.all(valid_tiles):
            walk = self.random_walk(self.random_wall_tile(valid_tiles))
            self.__clear_tiles(walk)
            walk = [self.adjacent_tiles(x) for x in walk]
            walk = [x for sublist in walk for x in sublist]
            valid_tiles = self.__clear_tiles(walk, valid_tiles)

        self.print_maze_terrain()

    def random_walk(self, start_tile):
        """Preform a random walk along valid wall tiles return a path"""

        path = [start_tile]
        curr_tile = start_tile

        while not self.maze_terrain[curr_tile.x][curr_tile.y]:
            next_tile = self.random_direction(curr_tile)
            for tile in self.adjacent_tiles(curr_tile):
                if self.maze_terrain[tile.x][tile.y]:
                    next_tile = tile

            if next_tile in path:
                path = path[:path.index(next_tile) + 1]
            else:
                path.append(next_tile)
            curr_tile = next_tile

        return path

    def __clear_zone(self, center):
        """Clear the 3x3 zone around center tile"""

        clear_zone = []
        for i in range(-3, 3):
            for j in range(-3, 3):
                tile = Tile(i + center.x, j + center.y)
                if self.valid_tile(tile):
                    clear_zone.append(tile)

        self.__clear_tiles(clear_zone)

    def __clear_tiles(self, tiles, maze=None):
        """Clear each tile in tiles, concurrency safe over the set of tiles"""

        if maze is None:
            maze = self.maze_terrain

        for tile in tiles:
            if self.valid_tile(tile):
                maze[tile.x][tile.y] = True

        return maze

    def random_wall_tile(self, maze):
        """Return a random wall tile"""

        available_tiles = np.column_stack((np.where(
            maze == False)))
        tile_pos = random.choice(available_tiles)
        rand_tile = Tile(tile_pos[0], tile_pos[1])

        return rand_tile

    def random_direction(self, start_tile):
        """Choose a random adjacent tile that is currently a wall"""

        possible_tiles = self.adjacent_tiles(start_tile)
        for tile in possible_tiles:
            if not self.valid_tile(tile):
                possible_tiles.remove(tile)

        if not possible_tiles:
            raise ValueError('No valid moves')
        else:
            return random.choice(possible_tiles)

    def adjacent_tiles(self, start_tile):
        """Returns a list of valid adjacent tiles"""

        adjacent_tiles = []
        if start_tile.y != self.dim[1] - 1:
            adjacent_tiles.append(Tile(start_tile.x, start_tile.y + 1))
        if start_tile.y != 0:
            adjacent_tiles.append(Tile(start_tile.x, start_tile.y - 1))
        if start_tile.x != self.dim[0] - 1:
            adjacent_tiles.append(Tile(start_tile.x + 1, start_tile.y))
        if start_tile.x != 0:
            adjacent_tiles.append(Tile(start_tile.x - 1, start_tile.y))

        return adjacent_tiles

    def valid_tile(self, tile):
        """Check for tile actually in maze"""

        if tile.x < 1 or tile.x >= self.dim[0] - 1:
            return False
        if tile.y < 1 or tile.y >= self.dim[1] - 1:
            return False
        return True

    def print_maze_terrain(self):
        """build and display a maze"""

        pyplot.figure(figsize=(10, 10))
        pyplot.imshow(self.maze_terrain, cmap="Greys_r", interpolation='nearest')
        pyplot.xticks([]), pyplot.yticks([])
        pyplot.show()

    def is_wall(self, tile):
        """Return True if the provided tile is a wall tile"""

        return not self.maze_terrain[tile.x][tile.y]
