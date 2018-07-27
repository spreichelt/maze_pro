import maze_pro.animate_maze_player as maze_player
import maze_pro.random_mouse as random_mouse

def make_player(dimensions=(251, 251), resources=(10, 1, 1)):
    """Return a player object"""

    player = random_mouse.RobertFrostRandomMouse(dimensions, resources)

    return player

def playthrough(dimensions=(51, 51), resources=(2, 1, 1)):
    """Make a player and run its animated_find_resource() method"""

    player = make_player(dimensions, resources)
    maze_player.animated_step(player)

playthrough()
