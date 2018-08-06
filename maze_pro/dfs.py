import random
from typing import List, Dict
import numpy as np
import maze_pro.maze as maze

class DFS():
    """A maze player that traverses the enviornment using DFS"""

    def __init__(self, dimensions, resources):
        self.interface = maze.PlayerInterface(dimensions, resources)
        self.visited = {}
        self.path = []
        self.direction = {'up': (0, -1), 'down': (0, 1), 
                          'left': (-1, 0), 'right': (1, 0)}

    def step(self):
        """Return the next tile to visit"""

        possible_tiles = self.walkable_tiles()
        direction, dest_tile = self.maze_dfs(possible_tiles)

        self.interface.move(dest_tile)
        self.visited[dest_tile] = self.visited[dest_tile] + 1
        self.path.append(dest_tile)
        return direction, dest_tile

    def maze_dfs(self, tiles: Dict[str, maze.Tile]) -> maze.Tile:
        """Select direction to travel according to DFS protocol"""

        dest = None
        direct = None
        if 'up' in tiles and tiles['up'] not in self.visited:
            dest, direct = tiles['up'], 'up'
        elif 'left' in tiles and tiles['left'] not in self.visited:
            dest, direct = tiles['left'], 'left'
        elif 'right' in tiles and tiles['right'] not in self.visited:
            dest, direct = tiles['right'], 'right'
        elif 'down' in tiles and tiles['down'] not in self.visited:
            dest, direct = tiles['down'], 'down'

        if dest:
            self.visited[dest] = 0
        else:
            direct, dest = self.backtrack()

        return direct, dest

    def backtrack(self) -> maze.Tile:
        """Retrace path back to a tile with unvisited neighbors"""

        self.path.pop()
        destination = self.path.pop()
        direction = self.get_direction(destination)

        return direction, destination

    def get_direction(self, dest_tile: maze.Tile) -> str:
        """Return the direction from the player position to the dest tile"""

        x = dest_tile.x - self.interface.player_pos.x
        y = dest_tile.y - self.interface.player_pos.y

        for direction, offsets in self.direction.items():
            if offsets == (x, y):
                return direction

        raise ValueError('Cannot move from '
                         + str(self.interface.player_pos)
                         + ' to ' + str(dest_tile))

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

        tile_value = self.interface.player_maze.terrain[tile.x][tile.y]
        if tile_value == 3:
            return True
        if tile_value == 2:
            return True
        if tile_value == 1:
            return False
        if tile_value == 0:
            raise ValueError('Tile: ' + str(tile) + ' is undiscovered')
