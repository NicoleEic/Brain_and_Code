from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation


def main():
    numframes = 100
    numpoints = 10

    rgb_color_data = np.random.random((numpoints, 3))
    x, y = np.random.random((2, numpoints))

    fig = plt.figure()
    scat = plt.scatter(x, y, c=rgb_color_data, s=100) #this work well at this level

    ani = animation.FuncAnimation(fig, update_plot2, frames=range(numframes),
                                  fargs=(rgb_color_data, scat))

    plt.show()


def update_plot2(i,data,scat):
    data[ i%10 ] = np.random.random((3))
    scat.set_color(data)
    return scat,


main()