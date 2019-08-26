import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --------
# overhead
# --------
rootdir = 'my/path/somewhere/'
subs = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
ROI_list = ['ROI1', 'ROI2', 'ROI3', 'ROI4']
condition_list = ['pre', 'post']
hemi_list = ["L", "R"]

# --------
# read data into dataframe
# --------
df = pd.DataFrame(columns=["subj", "ROI", "hemi", "condition", "my_value"])
my_row = 0
for sub in subs:
    OD = os.path.join('rootdir', 'derivatives', 'sub-' + sub)
    for ind_r, ROI in enumerate(ROI_list):
        for hemi in hemi_list:
            for ind_c, cond in enumerate(condition_list):
                # generate random value here as example
                my_val = np.random.randint(10) + ind_r + ind_c
                df.loc[my_row] = [sub, ROI, hemi, cond, my_val]
                my_row = my_row + 1

# --------
# plotting
# --------
# boxes show quartiles
# whiskers show rest of distribution (here within 2 SD)
sns.catplot(x="ROI", y="my_value", data=df, dodge=True, hue='condition', col='hemi', kind='box', whis=[5, 95], aspect=3)
plt.show()
