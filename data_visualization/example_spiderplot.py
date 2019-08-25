import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

# Relationship between continuous and categorical data
rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
ROI_list = ['ROI1', 'ROI2', 'ROI3', 'ROI4', 'ROI5', 'ROI6']
tract_list = ['tract1', 'tract2']
hemi_list = ['L', 'R']

df = pd.DataFrame(columns=["subj", "ROI", "tract", "hemi", "my_value"])
print('read in data')
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for ROI in ROI_list:
        for tract in tract_list:
            for hemi in hemi_list:
                # use random value here as example
                my_val = np.random.randint(100)
                df.loc[my_row] = [sub, ROI, tract, hemi, my_val]
                my_row = my_row + 1

df.my_value = pd.to_numeric(df.my_value)

print('make plot')
n_ROIs = len(df.ROI.unique())
sections = np.linspace(0.0, 2 * np.pi, n_ROIs, endpoint=False)
width = 0.2
fig = plt.figure(figsize=(8, 3))
for he, hemi in enumerate(hemi_list):
    ax = plt.subplot(1, 2, he + 1, projection='polar')
    for tr, tract in enumerate(tract_list):
        my_means = df[(df.hemi == hemi) & (df.tract == tract)].groupby('ROI').my_value.mean().values
        my_errs = df[(df.hemi == hemi) & (df.tract == tract)].groupby('ROI').my_value.std().values / np.sqrt(len(subs))
        bars = ax.bar(sections + tr * width, my_means, width=width, bottom=0.0)
        err_bars = ax.errorbar(sections + tr * width, my_means, my_errs, fmt='.', c='black')
    ax.set_title(hemi)
    ax.set_xticks(sections)
    ax.set_xticklabels(ROI_list)

plt.show()
