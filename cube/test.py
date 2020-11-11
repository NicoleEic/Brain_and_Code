from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation

numpoints = 10
x = np.arange(numpoints)

fig = plt.figure()
ax = p3.Axes3D(fig)


def main():

    rgb_color_data = np.zeros((numpoints, 3))
    scat = ax.scatter(x, x, x, c=rgb_color_data)
    ani = animation.FuncAnimation(fig, update_plot, frames=range(numpoints))
    plt.show()


def update_plot(i):
    data = np.zeros((numpoints, 3))
    data[i, :] = [1, 1, 1]
    print(data)
    scat = ax.scatter(x, x, x, c=data)
    return scat


main()