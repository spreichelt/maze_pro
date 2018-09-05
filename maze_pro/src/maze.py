"""Temp module docstring"""

import time
import random
from typing import List, Dict
import copy
import codecs, json
from tqdm import tqdm
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as pyplot

@dataclass
class Maze:
    """Object representing a maze"""
    terrain: np.array
    dim: (int, int)

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
    """Preform placement, tracking, and mining of resources in a maze

    Attributes:
        stockpile: The total amount of resources available for placement.
        __min: Minimum resource that can be placed in one location.
        __max: Maximum resource that can be placed in one location.
        locations: Dictionary of the form Tile:Int where tile is a maze location
            and Int is the amount of resource at that location.

    Methods:
        place: Place random amount of resource at provided location
        mine: Simulate mining resource
    """

    def __init__(self, resource_allocation: (int, int, int)):
        self.stockpile = resource_allocation[0]
        self.__min = resource_allocation[1]
        self.__max = resource_allocation[2]
        self.locations = {}

    def place(self, location: Tile):
        """Given a tile, allocate random amount of resource from the stockpile

        in the range of __min to __max

        """

        amount = min(random.randint(self.__min, self.__max), self.stockpile)
        self.locations[location] = amount
        self.stockpile = self.stockpile - amount

    def mine(self, capacity: int, rate: float, source: Tile) -> int:
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

    def __init__(self, dimensions: Tile, resource_allocation: (int, int, int)):
        self.__maze = MazeBuilder(dimensions, resource_allocation)
        self.player_maze = Maze(np.zeros(dimensions, dtype=int), dimensions)
        self.dimensions = dimensions
        self.player_pos = self.__maze.player_start
        self.update_player_maze(self.current_visible_tiles())

    def get_maze(self):
        return self.__maze

    def move(self, dest_tile: Tile) -> Dict[Tile, int]:
        """Move player from current position to dest_tile with error checking

        to ensure that an attempted move is to a tile adjacent to the players
        current position, and that the destination tile is not a wall tile

        """

        if self.__maze.is_wall(dest_tile):
            raise ValueError('Dest: ' + str(dest_tile) + ' is a wall tile')

        if dest_tile in adjacent_tiles(self.player_pos, self.__maze.maze):
            self.player_pos = copy.copy(dest_tile)
        else:
            if dest_tile != self.player_pos:
                raise ValueError(str(self.player_pos) + ' -> ' + str(dest_tile)
                                 + ' ILLEGAL MOVE')

        disc_tiles = self.__discovered_tiles(dest_tile)
        self.update_player_maze(disc_tiles)
        return disc_tiles

    def update_player_maze(self, tiles: Dict[Tile, int]):
        """Updates the players view of the maze with discovered tiles"""

        for tile, tile_type in tiles.items():
            self.player_maze.terrain[tile.x][tile.y] = tile_type

    def current_visible_tiles(self):
        """A public facing version of __discoverd_tiles that restricts the

        the query to the players current position

        """

        return self.__discovered_tiles(self.player_pos)

    def tile_type(self, tile):

        if self.__resource_data(tile):
            return 3
        elif self.__maze.is_wall(tile):
            return 1
        else:
            return 2

    def __discovered_tiles(self, pos):
        """Returns a dictionary of tiles obersvable from the provided position

        that maps tiles to the type of tile (wall, not wall, resource)

        """

        offsets = [(x, y) for x in range(-1, 2) for y in range(-1, 2)]
        tiles = [Tile(x + pos.x, y + pos.y) for (x, y) in offsets]
        visited_tiles = {tile : self.tile_type(tile) for tile in tiles}

        return visited_tiles

    def __resource_data(self, tile: Tile) -> int:
        """Returns None if the provided tile is not a resource tile, otherwise

        returns the amount of resource at the provided tile

        """

        if tile not in self.__maze.resources.locations:
            return None

        return self.__maze.resources.locations[tile]

class MazeBuilder():
    """Random construction of a data structure representing a maze

    Attributes:
        dim: Dimensions of the maze (x, y).
        terrain: A Maze dataclass object.
        resource_allocation: Data used to construct a Resource class to manage
            available resources in maze.
        player_start: The starting location for players traversing the maze.
        resources: A Resource class object.

    Methods:
        __build_maze: Drive the random processes that construct a maze.
        random_walk: Preform a random walk from provided tile until a tile
            that is not a wall is discovered.
        __clear_zone: Clear tiles in a 3x3 square centered around the
            provided tile.
        __clear_tiles: Set all provided tiles to True (walkable) in the terrain.
        random_wall_tile: Return a randomly selected wall tile.
        random_direction: Return a randomly selected wall tile adjacent to
            the paramater tile.
        adjacent_tiles: Return a list of valid adjacent tiles that are in
            walkable directions (up/down/left/right).
        valid_tiles: Return True if tile is within the boundary of the maze.
        print_maze_terrain: Display maze using matplotlib such that wall tiles 
            are black and walkable tiles are white.
        is_wall: Return True if the provided tile is a wall tile.
    """

    def __init__(self, dimensions: (int, int),
                 resource_allocation: (int, int, int)):

        self.dim = dimensions
        self.maze = Maze(np.zeros(dimensions, dtype=bool), dimensions)
        self.resource_allocation = resource_allocation
        self.player_start = None
        self.resources = Resources(resource_allocation)
        self.construction_json = {}

        self.__build_maze()

    def __build_maze(self):
        """Starting point for building data structures required for maze

        Alters the maze.terrain member using a version of Wilson's maze
        creation algorithm. Random tiles are assigned to resources until
        the stockpile is exhausted, then the remainder of the maze is
        randomly build until no more tiles can be randomly selected.

        """
        self.construction_json = {'color_map': {'seek': (100, 100, 100),
                                                'reset': 'wall',
                                                'clear': 'walkable'},
                                 'speed': 1,
                                 'steps': []}

        self.player_start = random_wall_tile(self.maze)
        clear_zone(self.player_start, self.maze, self.construction_json)
        available_tiles = Maze(np.copy(self.maze.terrain), self.dim)
        available_tiles.terrain[0, :] = available_tiles.terrain[-1, :] = True
        available_tiles.terrain[:, 0] = available_tiles.terrain[:, -1] = True

        total_available_tiles = (np.size(available_tiles.terrain)
                                 - np.count_nonzero(available_tiles.terrain))

        with tqdm(total=total_available_tiles) as pbar:
            # Place resource and connect to maze through a random walk
            while self.resources.stockpile > 0:
                tile = random_wall_tile(available_tiles)
                self.resources.place(tile)

                walk = self.random_walk(tile)
                clear_tiles(walk, self.maze, self.construction_json)
                walk = [adjacent_tiles(x, self.maze) for x in walk]
                walk = [x for sublist in walk for x in sublist]
                available_tiles = clear_tiles(walk, available_tiles)

                pbar.update(len(walk))

            while not np.all(available_tiles.terrain):
                walk = self.random_walk(random_wall_tile(available_tiles))
                clear_tiles(walk, self.maze, self.construction_json)
                walk = [adjacent_tiles(x, self.maze) for x in walk]
                walk = [x for sublist in walk for x in sublist]
                available_tiles = clear_tiles(walk, available_tiles)

                pbar.update(len(walk))

    def random_walk(self, start_tile: Tile) -> List[Tile]:
        """Preform a random walk along valid wall tiles return a path"""

        def construct(construction, path, color):
            construction['steps'].append({color: []})
            for tile in path:
                construction['steps'][-1][color].append((tile.x, tile.y))


        path = [start_tile]
        curr_tile = start_tile

        while not self.maze.terrain[curr_tile.x][curr_tile.y]:
            next_tile = random_direction(curr_tile, self.maze)
            for tile in adjacent_tiles(curr_tile, self.maze):
                if self.maze.terrain[tile.x][tile.y]:
                    next_tile = tile

            if next_tile in path:
                construct(self.construction_json, path, 'seek')
                construct(self.construction_json,
                        list(reversed(path[path.index(next_tile):])), 'reset')
                path = path[:path.index(next_tile) + 1]
            else:
                path.append(next_tile)
            curr_tile = next_tile

        construct(self.construction_json, path, 'seek')
        return path

    def is_wall(self, tile: Tile) -> bool:
        """Return True if the provided tile is a wall in the provided maze"""

        return not self.maze.terrain[tile.x][tile.y]


def valid_tile(tile, maze: Maze) -> bool:
    """Check for tile actually in maze"""

    if tile.x < 1 or tile.x >= maze.dim[0] - 1:
        return False
    if tile.y < 1 or tile.y >= maze.dim[1] - 1:
        return False
    return True

def clear_tiles(tiles, maze: Maze, construction = None) -> Maze:
    """Clear each tile in tiles, concurrency safe over the set of tiles"""

    for tile in tiles:
        if valid_tile(tile, maze):
            maze.terrain[tile.x][tile.y] = True


    if construction:
        construction['steps'].append({'clear': []})
        for tile in tiles:
            construction['steps'][-1]['clear'].append((tile.x,
                                                            tile.y))
    return maze

def clear_zone(center: Tile, maze: Maze, construction,  size: (int, int)=(3, 3)):
    """Clear the 3x3 zone around center tile"""

    x, y = size
    zone = []
    for i in range(-x, x):
        for j in range(-y, y):
            tile = Tile(i + center.x, j + center.y)
            if valid_tile(tile, maze):
                zone.append(tile)

    clear_tiles(zone, maze, construction)
    return zone

def print_maze_terrain(maze: Maze):
    """build and display a maze"""

    pyplot.figure(figsize=(10, 10))
    pyplot.imshow(maze.terrain, cmap="Greys_r", interpolation='nearest')
    pyplot.xticks([]), pyplot.yticks([])
    pyplot.show()

def random_wall_tile(maze: Maze) -> Tile:
    """Return a random wall tile"""

    available_tiles = np.column_stack((np.where(maze.terrain == False)))
    tile_pos = random.choice(available_tiles)
    rand_tile = Tile(tile_pos[0], tile_pos[1])

    return rand_tile

def adjacent_tiles(start_tile: Tile, maze: Maze) -> List[Tile]:
    """Returns a list of valid adjacent tiles"""

    tiles = []
    if start_tile.y != maze.dim[1] - 1:
        tiles.append(Tile(start_tile.x, start_tile.y + 1))
    if start_tile.y != 0:
        tiles.append(Tile(start_tile.x, start_tile.y - 1))
    if start_tile.x != maze.dim[0] - 1:
        tiles.append(Tile(start_tile.x + 1, start_tile.y))
    if start_tile.x != 0:
        tiles.append(Tile(start_tile.x - 1, start_tile.y))

    return tiles

def random_direction(start_tile: Tile, maze: Maze) -> Tile:
    """Choose a random adjacent tile that is currently a wall"""

    possible_tiles = adjacent_tiles(start_tile, maze)
    for tile in possible_tiles:
        if not valid_tile(tile, maze):
            possible_tiles.remove(tile)

    if not possible_tiles:
        raise ValueError('No valid moves')
    else:
        return random.choice(possible_tiles)

def serialize_maze_json(maze: Maze, file_path: str):
    """Store maze as json file"""

    formatted_array = maze.terrain.tolist()
    json.dump(formatted_array, codecs.open(
        file_path, 'w', encoding='utf-8'), separators=(',', ':'),
              sort_keys=True, indent=4)
