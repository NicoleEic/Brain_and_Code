import tkinter as tk
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# --------
# overhead
# --------
rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
ROI_list = ['ROI1', 'ROI2', 'ROI3', 'ROI4']
hemi_list = ["L", "R"]

# --------
# read data into dataframe
# --------
df = pd.DataFrame(columns=["subj", "ROI", "hemi", "my_value"])
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for ind_r, ROI in enumerate(ROI_list):
        for hemi in hemi_list:
            # generate random value here as example
            my_val = np.random.randint(10) + ind_r
            df.loc[my_row] = [sub, ROI, hemi, my_val]
            my_row = my_row + 1

# --------
# Set up TK-widget
# --------
root = tk.Tk()
root.wm_title("Matplotlib embedded in Tkinter")

# --------
# plotting
# --------
# initialize matplotlib figure
fig, ax = plt.subplots(figsize=(4, 4))
# generate mutliple patches from data
my_patches = []
for ind_r, ROI in enumerate(ROI_list):
    # get a rectangle reaching from lowest to highest value for each ROI
    rect = patches.Rectangle((np.min(df[(df.hemi == "L") & (df.ROI == ROI)].my_value.values) + 1, ind_r + 1), np.max(df[(df.hemi == "L") & (df.ROI == ROI)].my_value.values), 0.5)
    ax.add_patch(rect)
    my_patches.append(rect)

# hard-code axis limits for better visibility
ax.set_xlim(0, 15)
ax.set_ylim(0.5, len(ROI_list) + 1)

# link figure to tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# define settings for text lable below figure
output_val = tk.StringVar()
output_lbl = tk.Label(textvariable=output_val).pack()
output_val.set("")


# define what happens when the figure is clicked
def mouse_click(event):
    # find the ROI associated with the selected patch
    for ROI, patch in zip(ROI_list, my_patches):
        if patch.contains(event)[0]:
            # update the text in the label
            output_val.set(ROI)
            return


# define function when window is closed so that no error is thrown
def _quit():
    root.quit()

# link mouse_click function to figure
canvas.mpl_connect('button_press_event', mouse_click)

# execute widget
tk.mainloop()
