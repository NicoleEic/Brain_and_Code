# -*- coding: utf-8 -*-
import tkinter as tk
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pdb

rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
ROI_list = ['ROI1', 'ROI2', 'ROI3', 'ROI4']
hemi_list = ["L", "R"]

df = pd.DataFrame(columns=["subj", "ROI", "hemi", "my_value"])
print('read in data')
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for ind_r, ROI in enumerate(ROI_list):
        for hemi in hemi_list:
            # use random value here as example
            my_val = np.random.randint(10) + ind_r
            df.loc[my_row] = [sub, ROI, hemi, my_val]
            my_row = my_row + 1


root = tk.Tk()
root.wm_title("Matplotlib embedded in Tkinter")


def _quit():
    root.quit()

fig = plt.figure(figsize=(4, 4))
ax = fig.add_subplot(111)
my_patches = []
for ind_r, ROI in enumerate(ROI_list):
    rect = patches.Rectangle((np.min(df[(df.hemi == "L") & (df.ROI == ROI)].my_value.values) + 1, ind_r + 1), np.max(df[(df.hemi == "L") & (df.ROI == ROI)].my_value.values), 0.5)
    ax.add_patch(rect)
    my_patches.append(rect)

ax.set_xlim(0, 15)
ax.set_ylim(0, len(ROI_list) + 2)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()
output_val = tk.StringVar()
output_lbl = tk.Label(textvariable=output_val).pack()
output_val.set("")


def mouse_click(event):
    for ROI, patch in zip(ROI_list, my_patches):
        if patch.contains(event)[0]:
            output_val.set(ROI)
            return


canvas.mpl_connect('button_press_event', mouse_click)

tk.mainloop()
