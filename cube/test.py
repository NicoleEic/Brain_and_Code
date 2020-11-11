from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation

i_grid = 7
x, y, z = np.meshgrid(np.arange(i_grid), np.arange(i_grid), np.arange(i_grid))
fig = plt.figure()
ax = p3.Axes3D(fig)


def main():
    ani = animation.FuncAnimation(fig, update_plot, frames=range(len(x)))
    plt.show()


def update_plot(i):
    data = np.zeros((len(x.reshape(-1)), 3))
    data[i, :] = [1, 0, 1]
    scat = ax.scatter(x.reshape(-1), y.reshape(-1), z.reshape(-1), c=data)
    return scat


main()