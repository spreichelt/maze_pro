import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib import animation

def animated_step(player):
    """Self explanitory"""

    def animated_maze():
        pos = player.interface.player_pos
        animate_maze = np.copy(player.maze)
        animate_maze[pos.x][pos.y] = -1

        return animate_maze

    def animate_step(frame):
        player.step()
        imgplot.set_data(animated_maze())
        return imgplot

    player.update_maze(player.interface.current_visible_tiles())
    fig = pyplot.figure(figsize=(10, 10))
    pyplot.xticks([]), pyplot.yticks([])
    imgplot = pyplot.imshow(animated_maze(), interpolation='nearest')


    anim = animation.FuncAnimation(fig, animate_step, frames=20, interval=100)
    pyplot.show()
