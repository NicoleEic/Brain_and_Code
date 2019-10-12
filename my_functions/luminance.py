import numpy as np
import sys
from my import mymodule
import matplotlib.pyplot as plt
import pdb
import logging as log


luminance_factors = {'R': 0.2126, 'G': 0.7152, 'B': 0.0722}


def get_luminance(colour, luminance_factors={'R': 0.2126, 'G': 0.7152, 'B': 0.0722}):
    '''determine the perceived luminance value for a rgb colour'''
    L = luminance_factors['R'] * colour[0] + luminance_factors['G'] * colour[1] + luminance_factors['B'] * colour[2]
    return L


def rgb2yuv(colour):
    '''convert rgb colour to YUV colour space'''
    factors = np.array([[0.29900, -0.16874, 0.50000],
                        [0.58700, -0.33126, -0.41869],
                        [0.11400, 0.50000, -0.08131]])
    yuv = np.dot(colour, factors)
    return yuv


def diff_colours(c1, c2):
    '''compute the perceived distance of two colours in RGB space'''
    diff = np.sqrt(3 * (c1[0] - c2[0])**2 + 4 * (c1[1] - c2[1])**2 + 2 * (c1[2] - c2[2])**2)
    return diff


def plot_colours(colour_list):
    '''generate patches of a list of colours'''
    colour_list = [tuple(col) for col in colour_list]
    n_cols, n_rows = mymodule.get_subplots_matrix(len(colour_list))
    fig = plt.figure()
    for ind, my_colour in enumerate(colour_list):
        ax = fig.add_subplot(n_rows, n_cols, ind + 1)
        plt.plot([0, 1], c=my_colour)
        plt.text(0.5, 0.5, f'{ind}: {my_colour}')
        ax.set_facecolor(my_colour)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    plt.show()


def isoluminance_colours(L=0.5, n_colours=10, min_diff_col=0.5, verbose=1):
    '''Get a list of RGB colours that are matched in luminance.
    L: desired luminance (ranges from 0 to 1)
    n_colours: desired number of colours generated
    min_diff_col: minimal difference in RGB space across all colours
    verbose: set to 1 to print verbose messages
    '''

    # enable verboseprint function
    verboseprint = print if verbose else lambda *a, **k: None
    # mapping of index within rgb vector
    rgb_map = dict([(0, 'R'), (1, 'G'), (2, 'B')])
    # step size for initial index in staircase
    step_size = (1 / (n_colours / 3)) * 0.9
    # step size for 2nd index in staircase
    step_staircase = 0.0001
    # initialize output list
    new_colours_list = np.empty((0, 3), float)
    # initialize looping index for 1st index
    ind = 0
    running = 1
    while running:
        # exit while loop when 1st index has looped from 0 to 1
        if ind * step_size > 1:
            verboseprint('range of 1st index exceeded')
            running = 0
        else:
            # loop over R, G, B as 1st index to change
            for ind_fix in [0, 1, 2]:
                # increase 1st index by ind * step_size
                my_colour = np.array([0., 0., 0.])
                my_colour[ind_fix] = ind * step_size
                verboseprint('new colour: ', my_colour)
                # determine which two colours to update
                ind_update = np.where(np.array([0, 1, 2]) != ind_fix)[0]
                # check if a matching colour can be found with the initial value
                max_colour = np.copy(my_colour)
                max_colour[ind_update[0]] = 1
                max_colour[ind_update[1]] = 1
                min_colour = np.copy(my_colour)
                min_colour[ind_update[0]] = 0
                min_colour[ind_update[1]] = 0
                # if no matching colour can be found, continue with next while loop
                if (get_luminance(max_colour) < L) or (get_luminance(min_colour) > L):
                    verboseprint('initial values out of range')
                    ind = ind + 1
                    continue
                # loop over 2nd and 3rd index which one is set first
                for ind_pair in [[ind_update[0], ind_update[1]], [ind_update[1], ind_update[0]]]:
                    up_colour = np.copy(my_colour)
                    down_colour = np.copy(my_colour)
                    searching = 1
                    while searching:
                        # in/decrease second index
                        up_colour[ind_pair[0]] = up_colour[ind_pair[0]] + step_staircase
                        down_colour[ind_pair[0]] = down_colour[ind_pair[0]] - step_staircase
                        if up_colour[ind_pair[0]] > 1:
                            # exit while loop when 2nd index has looped from 0 to 1
                            verboseprint('2nd index out of range')
                            searching = 0
                        else:
                            for col in up_colour, down_colour:
                                # update 3rd index based on luminance value
                                col[ind_pair[1]] = (L - luminance_factors[rgb_map[ind_fix]] * col[ind_fix] - luminance_factors[rgb_map[ind_pair[0]]] * col[ind_pair[0]]) / luminance_factors[rgb_map[ind_pair[1]]]
                                # determine difference of new colour with the rest of the list
                                if len(new_colours_list) > 0:
                                    diff_C = np.apply_along_axis(diff_colours, 1, new_colours_list, col)
                                else:
                                    diff_C = 10
                                # add new colour when not too similar and within 0 1
                                if np.all(diff_C > min_diff_col) and not (np.any(col < 0) or np.any(col > 1)) and running:
                                    verboseprint(f'{my_colour}, found: {col}')
                                    verboseprint(f'difference in colour: {diff_C}')
                                    # add new colour
                                    new_colours_list = np.vstack((new_colours_list, col))
                                    # check that colour has not been added before
                                    new_colours_list = [tuple(col) for col in new_colours_list]
                                    new_colours_list = np.unique(new_colours_list, axis=0)
                                    # exit while loop for this 2nd index
                                    searching = 0
                                    # exit while loops when list is complete
                                    if len(new_colours_list) == n_colours:
                                        running = 0
        # update outer while loop index
        ind = ind + 1

    new_colours_list = np.around(new_colours_list, 2)
    print(new_colours_list)
    if len(new_colours_list) < n_colours:
        print('not enough colours generated. Decrease min_diff_col.')
    else:
        print('done!')
    return new_colours_list


if __name__ == "__main__":
    import sys
    isoluminance_colours(np.float(sys.argv[1]), np.int(sys.argv[2]))
