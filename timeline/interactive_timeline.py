import os
import sys
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from my_functions import img_google
import plotly.express as px

pd.set_option('mode.chained_assignment', None)

class timeline():
    def __init__(self, filename=os.path.join(os.path.dirname(sys.argv[0]), 'some_dates.csv')):
        # define scale values
        self.scales_info = pd.DataFrame(columns=['var_name', 'xlabel', 'title', 'default_min', 'default_max', 'tot_min', 'tot_max', 'cat_order'])
        self.scales_info.loc[len(self.scales_info)] = ['mya', 'million years ago', 'History of Life', -4600, 0, -4600, 0, ['supereon', 'eon', 'era', 'period', 'epoch', 'event']]
        self.scales_info.loc[len(self.scales_info)] = ['year', 'year', 'Modern History', 1500, 2000, -3500, 2019, ['epoch', 'person', 'art', 'event', 'invention']]
        self.scales_info.loc[len(self.scales_info)] = ['pre', 'kilo years ago', 'Prehistoric Time', -1000, 0, -3600, 0, ['epoch', 'event', 'invention', 'art', 'person']]
        
        # selected scale
        self.scale_type = 'year'
        self.myscale = self.get_myscale()

        # load total data file
        self.filename = filename
        self.df_orig = self.load_data()
        self.dict_cat = self.get_dict_cat()

        # initialize selection 
        self.df_myscale = self.get_df_myscale()

        # plot
        self.do_plot()

    def get_myscale(self):
        scale_type = self.scale_type
        myscale = self.scales_info[self.scales_info.var_name == scale_type].to_dict('r')[0]
        return myscale

    def get_dict_cat(self):
        # create dataframe to store information about categories
        df_cat = pd.DataFrame({'category': self.df_orig['category'].unique()})
        df_cat['category'] = pd.Categorical(df_cat['category'], self.myscale['cat_order'])
        #df_cat['color'] = self.colors[0:len(df_cat)]
        df_cat['color'] = np.arange(len(df_cat))
        df_cat.sort_values('category', inplace=True, ignore_index=True)
        dict_cat = df_cat.set_index('category')['color'].to_dict()
        return dict_cat

    def load_data(self):
        df = pd.read_csv(self.filename)
        # replace missing yearOff by yearOn
        df['yearOff'] = np.where(np.isnan(df['yearOff']), df['yearOn'], df['yearOff'])
        df['yearOn'] = df['yearOn'].astype(pd.Int64Dtype())
        df['yearOff'] = df['yearOff'].astype(pd.Int64Dtype())
        # ignore empty column
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df

    def get_df_myscale(self):
        # filter the desired scale
        df = self.df_orig[self.df_orig.scale == self.scale_type]
        if self.scale_type == 'mya':
            df.yearOn = -df.yearOn
            df.yearOff = -df.yearOff
        elif self.scale_type == 'pre':
            df.yearOn = np.round(df.yearOn / 1000)
            df.yearOff = np.round(df.yearOff / 1000)
            df['yearOn'] = df['yearOn'].astype(pd.Int64Dtype())
            df['yearOff'] = df['yearOff'].astype(pd.Int64Dtype())

        df = df.loc[(df['yearOn'] >= self.myscale['tot_min']) & (df['yearOff'] + 1 < self.myscale['tot_max'])]

        # add column for duration of event (min 1 year)
        df['duration'] = df['yearOff'] - df['yearOn']
        df['duration'] = np.where(df.duration < 1, 1, df['duration'])
        # add task-column
        df['ypos'] = self.get_ypos(df)
        # sort and re-index cleaned df
        df['category'] = pd.Categorical(df['category'], self.myscale['cat_order'])
        # column for color value
        df['color'] = df['category']
        df.replace({"color": self.dict_cat}, inplace=True)
        # sort
        df = df.sort_values(['category', 'yearOn'])
        df.index = pd.RangeIndex(len(df.index))
        return df

    def new_scale(self):
        self.myscale = self.get_myscale()
        self.df_myscale = self.get_df_myscale()

    def get_ypos(self, df):
        # initialize parameters
        ypos_arr = np.array([0])
        ypos_group = 0
        ymax = 0
        # loop over categories
        for cat in self.dict_cat.keys():
            group = df[df.category == cat]
            filled = pd.DataFrame(columns=['ypos', 'on', 'off'])
            # draw event as rectangle
            for ind, row in group.iterrows():
                # draw the event in the next free row
                ypos = ypos_group + 1
                # add subsequent pathes directly
                if cat in ['supereon', 'eon', 'era', 'period', 'epoch']:
                    while any((filled['ypos'] == ypos) & (((filled['on'] < (row['yearOn'])) & ((row['yearOn']) < filled['off'])) | ((filled['on'] < (row['yearOff'])) & ((row['yearOn'] + row['duration']) < filled['off'])))):
                        ypos += 1
                # start new row for short events
                else:
                    while any((filled['ypos'] == ypos) & (((filled['on'] < (row['yearOn'] - 1)) & ((row['yearOn'] - 1) < filled['off'])) | ((filled['on'] < (row['yearOff'] - 1)) & ((row['yearOn'] + row['duration'] + 1) < filled['off'])))):
                        ypos += 1
                if ypos > ymax:
                    ymax = ypos
                filled = filled.append({'ypos': ypos, 'on': row['yearOn'], 'off': row['yearOn'] + row['duration']}, ignore_index=True)
                ypos_arr = np.append(ypos_arr, ypos)
            # start a new cateory in a new row
            ypos_group = ymax
        ypos_arr = np.delete(ypos_arr, 0)
        return ypos_arr

    def do_plot(self):
        fig = px.timeline(self.df_myscale, x_start="yearOn", x_end="yearOff", y="ypos", hover_name="title", hover_data=["yearOn", "yearOff"], color='color', color_continuous_scale='Viridis')
        fig.layout.xaxis.type = 'linear'
        fig.data[0].x = self.df_myscale.duration.tolist()
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))
        fig.update_layout(hovermode="x")
        fig['layout']['yaxis']['autorange'] = "reversed"
        fig.show()

# mainloop
if __name__ == "__main__":
    root = timeline()

