import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
import pandas as pd
import seaborn as sns

# Relationship between continuous and categorical data
rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
thres_list = np.arange(0, 101)
hemi_list = ["L", "R"]

df = pd.DataFrame(columns=["subj", "hemi", "threshold", "my_value"])
print('read in data')
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for hemi in hemi_list:
        for thr in thres_list:
            # use random value here as example
            my_val = np.random.randint(40) + thr
            df.loc[my_row] = [sub, hemi, thr, my_val]
            my_row = my_row + 1


fig = plt.figure()
ax = fig.add_subplot(111)
# Adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(bottom=0.25)

t_init = 50

# Define an axes area and draw a slider in it
my_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
my_slider = Slider(my_slider_ax, 'threshold (%)', 0, 100, valinit=t_init)


# Define an action for modifying the plot when any slider's value changes
def sliders_on_changed(val):
    update_plot(ax, np.round(val))
    fig.canvas.draw_idle()


def update_plot(ax, thres):
    ax.clear()
    sns.boxplot(x="hemi", y="my_value", data=df[df.threshold == thres], ax=ax)
    ax.set_ylim(0, np.max(df.my_value.values))


update_plot(ax, t_init)

my_slider.on_changed(sliders_on_changed)

plt.show()
