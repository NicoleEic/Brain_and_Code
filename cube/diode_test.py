from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation

'''src: https://stackoverflow.com/questions/51632254/animated-3d-python-plot-with-several-moving-points'''

fig = plt.figure()
ax = p3.Axes3D(fig)

q = [[-4.32, -2.17, -2.25, 4.72, 2.97, 1.74],
     [2.45, 9.73,  7.45, 4.01, 3.42,  1.80],
     [-1.40, -1.76, -3.08, -9.94, -3.13, -1.13]]

fx = np.array(q[0])
fy = np.array(q[1])
fz = np.array(q[2])

fpoints, = ax.plot(fx, fy, fz, '*')
txt = fig.suptitle('')


def update_points(num, x, y, z, points):
    # update title
    txt.set_text('num={:d}'.format(num))
    # calculate the new sets of coordinates here. The resulting arrays should have the same shape
    # as the original x,y,z
    new_x = x + np.random.normal(1, 0.1, size=(len(x),))
    new_y = y + np.random.normal(1, 0.1, size=(len(y),))
    new_z = z + np.random.normal(1, 0.1, size=(len(z),))

    # update properties
    points.set_data(new_x, new_y)
    points.set_3d_properties(new_z, 'z')

    # return modified artists
    return points, txt


ani = animation.FuncAnimation(fig, update_points, frames=30, fargs=(fx, fy, fz, fpoints))
plt.show()