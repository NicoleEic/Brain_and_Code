import numpy as np
import sys
from my import mymodule
import matplotlib.pyplot as plt
import pdb

luminance_factors = {'R': 0.2126, 'G': 0.7152, 'B': 0.0722}


def get_luminance(colour, luminance_factors={'R': 0.2126, 'G': 0.7152, 'B': 0.0722}):
    L = luminance_factors['R'] * colour[0] + luminance_factors['G'] * colour[1] + luminance_factors['B'] * colour[2]
    return L


def plot_colours(colour_list):
    colour_list = [tuple(col) for col in colour_list]
    n_cols, n_rows = mymodule.get_subplots_matrix(len(colour_list))
    fig = plt.figure()
    for ind, my_colour in enumerate(colour_list):
        ax = fig.add_subplot(n_rows, n_cols, ind + 1)
        plt.plot([1, 1], c=my_colour)
        ax.set_facecolor(my_colour)
    plt.show()


def isoluminance_colours(L=0.5, n_colours=10, step_size=0.2):
    rgb_map = dict([(0, 'R'), (1, 'G'), (2, 'B')])
    step_staircase = 0.001
    new_colours_list = np.empty((0, 3), float)
    ind = 0
    while len(new_colours_list) < n_colours:
        for ind_fix in [0, 1, 2]:
            if ind * step_size == 1:
                print('exceeded range, change step size')
                return new_colours_list

            my_colour = np.array([0., 0., 0.])
            my_colour[ind_fix] = ind * step_size
            ind_update = np.where(np.array([0, 1, 2]) != ind_fix)[0]
            max_colour = np.copy(my_colour)
            max_colour[ind_update[0]] = 1
            max_colour[ind_update[1]] = 1
            min_colour = np.copy(my_colour)
            min_colour[ind_update[0]] = 0
            min_colour[ind_update[1]] = 0
            if (get_luminance(max_colour) < L) or (get_luminance(min_colour) > L):
                #print('doesnt work')
                ind = ind + 1
                continue
            for ind_pair in [[ind_update[0], ind_update[1]], [ind_update[1], ind_update[0]]]:
                up_colour = np.copy(my_colour)
                down_colour = np.copy(my_colour)
                searching = 1
                while searching and len(new_colours_list) < n_colours:
                    # in/decrease first index
                    up_colour[ind_pair[0]] = up_colour[ind_pair[0]] + step_staircase
                    down_colour[ind_pair[0]] = down_colour[ind_pair[0]] - step_staircase
                    for col in up_colour, down_colour:
                        # update second colour
                        col[ind_pair[1]] = (L - luminance_factors[rgb_map[ind_fix]] * col[ind_fix] - luminance_factors[rgb_map[ind_pair[0]]] * col[ind_pair[0]]) / luminance_factors[rgb_map[ind_pair[1]]]
                        if get_luminance(col) == L and not (np.any(col < 0) or np.any(col > 1)):
                            #print(f'{my_colour}, found: {col}')
                            new_colours_list = np.vstack((new_colours_list, col))
                            searching = 0
        new_colours_list = [tuple(col) for col in new_colours_list]
        new_colours_list = np.unique(new_colours_list, axis=0)
        ind = ind + 1

    print(new_colours_list)
    plot_colours(new_colours_list)
    return new_colours_list


if __name__ == "__main__":
    import sys
    isoluminance_colours(np.float(sys.argv[1]), np.int(sys.argv[2]))
