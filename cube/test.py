from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation



def main():
    i_grid = 7
    t_step = 500 # miliseconds
    n_vols = 10
    x, y, z = np.meshgrid(np.arange(i_grid), np.arange(i_grid), np.arange(i_grid))
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    data_in = np.zeros((i_grid, i_grid, i_grid, n_vols))
    data_in[::2, :, :, ::2] = 1

    def update_plot(i):
        data_vol = data_in[:, :, :, i]
        scat = ax.scatter(x.reshape(-1), y.reshape(-1), z.reshape(-1), c=data_vol.reshape(-1), cmap='binary',
                          depthshade=False, vmin=0, vmax=1, edgecolors="black")
        ax.set_xticklabels("")
        ax.set_yticklabels("")
        ax.set_zticklabels("")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_ylabel('Z')
        return scat

    ani = animation.FuncAnimation(fig, update_plot, interval=t_step, frames=n_vols)
    plt.show()



main()