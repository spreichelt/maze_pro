import random
from typing import List, Dict
import numpy as np
import maze_pro.maze as maze

class DFS():
    """A maze player that traverses the enviornment using DFS"""

    def __init__(self, dimensions: (int, int),
                 resource_allocation: (int, int, int)):
        self.interface = maze.PlayerInterface(dimensions, resource_allocation)
        self.maze = np.zeros(dimensions, dtype=int)
        self.visited = {}
        self.path = []
        self.direction = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}

    def step(self):
        """Return the next tile to visit"""

        possible_tiles = self.walkable_tiles()
        dest = self.maze_dfs(possible_tiles)

        observed_tiles = self.interface.move(dest)
        self.update_maze(observed_tiles)
        self.visited[dest] = self.visited[dest] + 1
        self.path.append(dest)

    def maze_dfs(self, tiles: Dict[str, maze.Tile]) -> maze.Tile:
        """Select direction to travel according to DFS protocol"""

        dest = None
        if 'N' in tiles and tiles['N'] not in self.visited:
            dest = tiles['N']
        elif 'E' in tiles and tiles['E'] not in self.visited:
            dest = tiles['E']
        elif 'W' in tiles and tiles['W'] not in self.visited:
            dest = tiles['W']
        elif 'S' in tiles and tiles['S'] not in self.visited:
            dest = tiles['S']

        if dest:
            self.visited[dest] = 0
        else:
            dest = self.backtrack()

        return dest

    def backtrack(self) -> maze.Tile:
        """Retrace path back to a tile with unvisited neighbors"""

        self.path.pop()

        return self.path.pop()

    def update_maze(self, observed_tiles: Dict[maze.Tile, int]) -> maze.Tile:
        """Updates players view of the maze with data from last move"""

        for tile, tile_type in observed_tiles.items():
            self.maze[tile.x][tile.y] = tile_type

    def walkable_tiles(self) -> Dict[str, maze.Tile]:
        """Return set of tiles adjacent to player that can be walked on"""

        tiles = {}
        pos = self.interface.player_pos
        for direction, offset in self.direction.items():
            tile = maze.Tile(pos.x + offset[0], pos.y + offset[1])
            if self.is_walkable(tile):
                tiles[direction] = tile

        return tiles

    def is_walkable(self, tile: maze.Tile) -> bool:
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
