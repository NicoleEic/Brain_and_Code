import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pandas as pd
import seaborn as sns

# --------
# overhead
# --------
rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
thres_list = np.arange(0, 101)
hemi_list = ["L", "R"]

# --------
# read data into dataframe
# --------
df = pd.DataFrame(columns=["subj", "hemi", "threshold", "my_value"])
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for hemi in hemi_list:
        for thr in thres_list:
            # use random value here as example
            my_val = np.random.randint(40) + thr
            df.loc[my_row] = [sub, hemi, thr, my_val]
            my_row = my_row + 1

#  initial threshold level chosen for plotting
thres_init = 50

# initialize matplotlib figure
fig, ax = plt.subplots(figsize=(4, 4))
# adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(bottom=0.25)
# define an axes area and draw a slider in it
my_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
# generate slider with initial value
my_slider = Slider(my_slider_ax, 'threshold (%)', 0, 100, valinit=thres_init)


# define an action for when the slider's value changes
def slider_action(val):
    # the figure is updated when the slider is changed
    update_plot(np.round(val))


# link slider_action function to slider object
my_slider.on_changed(slider_action)


# define how to update the plot
def update_plot(thres):
    # clear the axis before the plot is redrawn
    ax.clear()
    sns.boxplot(x="hemi", y="my_value", data=df[df.threshold == thres], ax=ax)
    # keep the axis limits constant for better visibility of the changes
    ax.set_ylim(0, np.max(df.my_value.values))
    # update figure
    fig.canvas.draw_idle()


# draw initial plot with default threshold
update_plot(thres_init)

plt.show()
