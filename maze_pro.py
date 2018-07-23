import maze_pro.maze_player as maze_player

def make_player(dimensions=(251, 251), resources=(10, 1, 1)):
    """Return a player object"""

    player = maze_player.Player(dimensions, resources)

    return player

def playthrough(dimensions=(51, 51), resources=(2, 1, 1)):
    """Make a player and run its animated_find_resource() method"""

    player = make_player(dimensions, resources)
    player.animated_find_resource()

playthrough()
