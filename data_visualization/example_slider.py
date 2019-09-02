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
intensity_list = np.arange(0, 101)
hemi_list = ["L", "R"]

# --------
# read data into dataframe
# --------
df = pd.DataFrame(columns=["subj", "hemi", "intensity", "my_value"])
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for hemi in hemi_list:
        for intensity in intensity_list:
            # use random value here as example
            my_val = np.random.randint(40) + intensity
            df.loc[my_row] = [sub, hemi, intensity, my_val]
            my_row = my_row + 1

# initialize matplotlib figure
fig, ax = plt.subplots(figsize=(4, 4))
# adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(bottom=0.25)
# define an axes area and draw a slider in it
my_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
#  initial intensity level chosen for plotting
intensity_init = 50
# generate slider with initial value
my_slider = Slider(my_slider_ax, 'intensity (%)', 0, 100, valinit=intensity_init)


# define an action for when the slider's value changes
def slider_action(val):
    # the figure is updated when the slider is changed
    update_plot(np.round(val))


# link slider_action function to slider object
my_slider.on_changed(slider_action)


# define how to update the plot
def update_plot(intensity):
    # clear the axis before the plot is redrawn
    ax.clear()
    sns.boxplot(x="hemi", y="my_value", data=df[df.intensity == intensity], ax=ax)
    # keep the axis limits constant for better visibility of the changes
    ax.set_ylim(0, np.max(df.my_value.values))
    # update figure
    fig.canvas.draw_idle()


# draw initial plot with default intensity
update_plot(intensity_init)
# display figure
plt.show()
