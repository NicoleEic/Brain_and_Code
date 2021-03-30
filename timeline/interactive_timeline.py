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
    def __init__(self):
        self.min = -3000
        self.max = 2000

        # load total data file
        #self.df = self.prep_data()
        #self.set_ypos()

        # or load
        self.df = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_prep.csv'))

        # plot
        self.do_plot()

    def get_myscale(self):
        scale_type = self.scale_type
        myscale = self.scales_info[self.scales_info.var_name == scale_type].to_dict('r')[0]
        return myscale

    def prep_data(self):
        df = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline.csv'))
        df_cat = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_types.csv'))
        # replace missing date_to by date_from
        df['date_to'] = np.where(np.isnan(df['date_to']), df['date_from'], df['date_to'])
        df['date_from'] = df['date_from'].astype(pd.Int64Dtype())
        df['date_to'] = df['date_to'].astype(pd.Int64Dtype())
        df = df.loc[(df['date_from'] >= self.min) & (df['date_to'] + 1 < self.max)]
        # add column for duration of event (min 1 year)
        df['duration'] = df['date_to'] - df['date_from']
        df['duration'] = np.where(df.duration < 1, 1, df['duration'])
        # map category
        di = df_cat.set_index('timeline_type_id')['timeline_type_name'].to_dict()
        df['timeline_type_name'] = df['timeline_type_id'].map(di)
        df = df.sort_values(['timeline_type_id', 'date_from'])
        df.index = pd.RangeIndex(len(df.index))
        return df

    def set_ypos(self):
        # initialize parameters
        ypos_arr = np.array([0])
        ypos_group = 0
        ymax = 0
        # loop over categories
        for cat in np.unique(self.df['timeline_type_id'].values):
            print(cat)
            group = self.df[self.df.timeline_type_id == cat]
            filled = pd.DataFrame(columns=['ypos', 'on', 'off'])
            # draw event as rectangle
            for ind, row in group.iterrows():
                # draw the event in the next free row
                ypos = ypos_group + 1
                while any((filled['ypos'] == ypos) & (((filled['on'] < (row['date_from'] - 1)) & ((row['date_from'] - 1) < filled['off'])) | ((filled['on'] < (row['date_to'] - 1)) & ((row['date_from'] + row['duration'] + 1) < filled['off'])))):
                    ypos += 1
                if ypos > ymax:
                    ymax = ypos
                filled = filled.append({'ypos': ypos, 'on': row['date_from'], 'off': row['date_from'] + row['duration']}, ignore_index=True)
                ypos_arr = np.append(ypos_arr, ypos)
            # start a new cateory in a new row
            ypos_group = ymax
        ypos_arr = np.delete(ypos_arr, 0)
        self.df['ypos'] = ypos_arr
        self.df.to_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_prep.csv'))

    def do_plot(self):
        fig = px.timeline(self.df, x_start="date_from", x_end="date_to", y="ypos", hover_name="text_raw", hover_data=["date_from", "date_to"], color='timeline_type_name')
        fig.layout.xaxis.type = 'linear'
        for i_d, dat in enumerate(fig.data):
            fig.data[i_d].x = self.df[self.df['timeline_type_name'] == dat.name].duration.tolist()
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))
        fig.layout.yaxis.autorange = "reversed"
        fig.layout.yaxis.visible = False
        fig.update_layout(title_text="Interactive timeline")

        fig.show()

# mainloop
if __name__ == "__main__":
    root = timeline()

