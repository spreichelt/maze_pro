import random
from typing import List, Dict
import numpy as np
import maze_pro.maze as maze

class RobertFrostRandomMouse():
    """Handles player data and interation with maze"""

    def __init__(self, dimensions: (int, int),
                 resource_allocation: (int, int, int)):
        self.interface = maze.PlayerInterface(dimensions, resource_allocation)
        self.maze = np.zeros(dimensions, dtype=int)
        self.visited = {}
        self.path = []
        self.direction = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    def step(self):
        """Return the next tile to visit"""

        possible_tiles = self.walkable_tiles()
        never_visited = [x for x in possible_tiles if x not in self.visited]
        dest = None
        if never_visited:
            dest = random.choice(never_visited)
            self.visited[dest] = 0
        else:
            least_traveled = possible_tiles[0]
            for tile in possible_tiles:
                if self.visited[tile] < self.visited[least_traveled]:
                    least_traveled = tile
            dest = least_traveled

        observed_tiles = self.interface.move(dest)
        self.update_maze(observed_tiles)
        self.visited[dest] = self.visited[dest] + 1
        self.path.append(dest)

    def update_maze(self, observed_tiles: Dict[maze.Tile, int]):
        """Updates players view of the maze with data from last move"""

        for tile, tile_type in observed_tiles.items():
            self.maze[tile.x][tile.y] = tile_type

    def walkable_tiles(self) -> List[maze.Tile]:
        """Return set of tiles adjacent to player that can be walked on"""

        tiles = []
        pos = self.interface.player_pos
        for offset in self.direction.values():
            tile = maze.Tile(pos.x + offset[0], pos.y + offset[1])
            if self.is_walkable(tile):
                tiles.append(tile)

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

    def get_direction(self, dest_tile: maze.Tile) -> str:
        """Return the direction of a move to dest_tile from self.position"""

        x_, y_ = dest_tile.x - self.position.x, dest_tile.y - self.position.y
        for direction, offsets in self.direction.items():
            if offsets == (x_, y_):
                return direction

        raise ValueError('Not a valid move')
