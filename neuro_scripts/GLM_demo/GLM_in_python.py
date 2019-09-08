import os
import random
import numpy as np
import pandas as pd
import patsy
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.anova import AnovaRM
from scipy import stats
import seaborn as sns
# --------
# 1-way ANOVA in Python (between-subject factor)
# --------
# information on experimental design
group_list = ['control','patient1','patient2']
subs_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
# read data into dataframe
df_1way = pd.DataFrame(columns=["group", "my_value"])
my_row = 0
for ind_g, group in enumerate(group_list):
    for sub in subs_list:
        # generate random value here as example
        my_val = np.random.normal(ind_g, 1, 1)[0]
        df_1way.loc[my_row] = [group, my_val]
        my_row = my_row + 1

# inspect data
sns.catplot(x="group", y="my_value", data=df_1way, dodge=True, kind='violin', aspect=3)
plt.show()

# generate model for linear regression
my_model = smf.ols(formula='my_value ~ group', data=df_1way)
# fit model to data to obtain parameter estimates
my_model_fit = my_model.fit()
# print summary of linear regression
print(my_model_fit.summary())
# show anova table
anova_table = sm.stats.anova_lm(my_model_fit, typ=2)
print(anova_table)

# compare p-value to:scipy for 1-way (one factorial) analysis
F, p = stats.f_oneway(df_1way[df_1way['group'] == 'control'].my_value, df_1way[df_1way['group'] == 'patient1'].my_value, df_1way[df_1way['group'] == 'patient2'].my_value)
print(p)

# --------
# 2-way ANOVA in Python (between-subject factors)
# --------
# information on experimental design
group_list = ['control','patient1','patient2']
language_list = ['English', 'German', 'French']
subs_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
# read data into dataframe
df_2way = pd.DataFrame(columns=["group", "language", "my_value"])
my_row = 0
for ind_g, group in enumerate(group_list):
    for ind_l, lan in enumerate(language_list):
        for sub in subs_list:
                # generate random value here as example
                my_val = np.random.normal(ind_g + ind_l, 1, 1)[0]
                df_2way.loc[my_row] = [group, lan, my_val]
                my_row = my_row + 1

# plot data
sns.catplot(x="language", y="my_value", data=df_2way, dodge=True, hue='group', kind='violin', aspect=3)
plt.show()

# fit model to data to obtain parameter estimates
my_model_fit = smf.ols(formula='my_value ~ group * language', data=df_2way).fit()
# print summary of linear regression
print(my_model_fit.summary())
# show anova table
print(sm.stats.anova_lm(my_model_fit, typ=2))


# use Patsy to construct the model above
model_matrix = patsy.dmatrix("group * language", df_2way)
# visualize model
plt.show(plt.imshow(model_matrix, aspect='auto'))
# use sum coding scheme for factors
plt.show(plt.imshow(patsy.dmatrix("C(group, Sum) * C(language, Sum)", df_2way), aspect='auto'))

# --------
# 2-way Repeated measures ANOVA in Python (within-subject factors)
# --------
# information on experimental design
subs_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
task_list = ['task1', 'task2', 'task3']
condition_list = ['pre', 'post']

# read data into dataframe
df_2way_rm = pd.DataFrame(columns=["sub_id", "task", "condition", "my_value"])
my_row = 0
# unique subject-ID as additional factor
sub_id = 0
for sub in subs_list:
    sub_id = sub_id + 1
    for ind_t, task in enumerate(task_list):
        for ind_c, con in enumerate(condition_list):
            # generate random value here as example
            my_val = np.random.normal(ind_t + ind_c, 1, 1)[0]
            df_2way_rm.loc[my_row] = [sub_id, task, con, my_val]
            my_row = my_row + 1

# conduct ANOVA using mixedlm
my_model_fit = smf.mixedlm("my_value ~ task * condition", df_2way_rm, groups=df_2way_rm["sub_id"]).fit()
# get fixed effects
my_model_fit.summary()
# get random effects
my_model_fit.random_effects

# conduct ANOVA using AnovaRM
my_model_fit = AnovaRM(df_2way_rm, 'my_value', 'sub_id', within=['task', 'condition']).fit()
print(my_model_fit.anova_table)


# --------
# 4-way ANOVA with between-group and within-group factors (repeated measures)
# --------
# information on experimental design
group_list = ['control','patient1','patient2']
language_list = ['English', 'German', 'French']
subs_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
task_list = ['task1', 'task2', 'task3']
condition_list = ['pre', 'post']

# read data into dataframe
df_full = pd.DataFrame(columns=["group", "language", "sub_id", "task", "condition", "my_value"])
my_row = 0
# unique subject-ID
sub_id = 0
for ind_g, group in enumerate(group_list):
    for ind_l, lan in enumerate(language_list):
        for sub in subs_list:
            sub_id = sub_id + 1
            for ind_t, task in enumerate(task_list):
                for ind_c, con in enumerate(condition_list):
                    # generate random value here as example
                    my_val = np.random.normal(ind_c + ind_t, 1, 1)[0]
                    df_full.loc[my_row] = [group, lan, sub_id, task, con, my_val]
                    my_row = my_row + 1

# conduct ANOVA using mixedlm
my_model_fit = smf.mixedlm("my_value ~ group * language * task * condition", df_full, groups=df_full["sub_id"]).fit()
# get fixed effects
my_model_fit.summary()
# get random effects
my_model_fit.random_effects

# 4-way analysis possible in ols, but random effects not accounted for!
my_model_fit = smf.ols(formula='my_value ~ group * language * task * condition', data=df_full).fit()
sm.stats.anova_lm(my_model_fit, typ=2)
my_model_fit.summary()

# --------
# Save dataframes as csv
# --------
df_2way.to_csv('df_2way.csv', index=False)
df_full.to_csv('df_full.csv', index=False)
