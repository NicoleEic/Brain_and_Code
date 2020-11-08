from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import matplotlib.animation
import pandas as pd

def main():
    n_points = 5
    a = np.arange(n_points)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    color_vec = ['r', 'r', 'r', 'r', 'b']

    scat = ax.scatter(a, a, a, c=color_vec)

    ani = matplotlib.animation.FuncAnimation(fig, update_graph, frames=10, fargs=(['b', 'b', 'b', 'b', 'b'], scat))

    plt.show()


def update_graph(i, color_vec, scat):
    print(i)
    scat.set_color(color_vec)
    return scat

main()