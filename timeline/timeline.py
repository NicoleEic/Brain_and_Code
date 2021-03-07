import tkinter as tk
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


# TODO data browser
# TODO: time slider
class timeline(tk.Tk):
    def __init__(self, filename=os.path.join(os.path.dirname(sys.argv[0]), 'some_dates.csv')):
        tk.Tk.__init__(self)
        self.title("timeline")

        colors = pd.Series(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'])

        self.filename = filename
        self.df_tot = self.load_data()
        self.scale = 'year'

        # default time range for the timeline
        if self.scale == 'year':
            self.min = 1500
            self.max = 2000
            self.category_order = ["epoch", "person", "art", "event", "invention"]
        elif self.scale == 'mya':
            self.min = -4600
            self.max = 0
            self.category_order = ['supereon', 'eon', 'era', 'period', 'epoch', 'event']

        self.yearFrom = tk.StringVar()
        self.yearFrom.set(self.min)
        self.yearTo = tk.StringVar()
        self.yearTo.set(self.max)

        self.df_orig = self.prepare_df(self.df_tot)

        # create dataframe to store information about categories
        c_df = pd.DataFrame({'category': self.df_orig['category'].unique()})
        c_df['category'] = pd.Categorical(c_df['category'], self.category_order)
        c_df['color'] = colors[0:len(c_df)]
        self.c_df = c_df.sort_values('category')

        # frame configuration
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 1, weight=2)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 2, weight=1)

        fr1 = tk.Frame(self)
        fr1.grid(row=0, column=0, sticky="nsew")
        fr2 = tk.Frame(self)
        fr2.grid(row=0, column=1, sticky="nsew")
        fr3 = tk.Frame(self)
        fr3.grid(row=0, column=2, sticky="nsew")
        tk.Grid.rowconfigure(fr3, 0, weight=1)
        tk.Grid.rowconfigure(fr3, 1, weight=4)
        
        # fr1: Field and label for 'from'
        tk.Label(fr1, text="From:").pack()
        on = tk.Entry(fr1, textvariable=self.yearFrom, width=4)
        on.pack()
        on.focus_set()

        # fr1: Field and label for 'To'
        tk.Label(fr1, text="To:").pack()
        tk.Entry(fr1, textvariable=self.yearTo, width=4).pack()

        # fr1: OK button
        tk.Button(fr1, text="OK", command=self.reset).pack()
        self.bind('<Return>', self.reset)

        # fr2: toggles for categories displayed
        for i, row in self.c_df.iterrows():
            # make one toggle field for each category
            self.c_df.loc[i, 'toggle'] = tk.IntVar()
            tk.Checkbutton(fr2, fg=self.c_df.loc[i, 'color'], text=row['category'], variable=self.c_df.loc[i, 'toggle'], command=self.reset).pack()
            self.c_df.loc[i, 'toggle'].set(1)

        # fr3: label for item title
        self.label_value = tk.StringVar()
        tk.Label(fr3, textvariable=self.label_value, width=50).pack()
        self.label_value.set('Click on an event!')

        # fr3: label for image
        self.img_label = tk.Label(fr3)
        self.img_label.pack()

        # select rows from dataframe
        self.df = self.select_rows_df(self.df_orig)

        # plotting
        self.draw()

    def load_data(self):
        # TODO: add option to browse through folder
        df = pd.read_csv(self.filename)
        # replace missing yearOff by yearOn
        df['yearOff'] = np.where(np.isnan(df['yearOff']), df['yearOn'], df['yearOff'])
        df['yearOn'] = df['yearOn'].astype(pd.Int64Dtype())
        df['yearOff'] = df['yearOff'].astype(pd.Int64Dtype())
        return df

    def reset(self, *args):
        self.min = int(self.yearFrom.get())
        self.max = int(self.yearTo.get())
        self.label_value.set('Click on an event!')
        self.img_label.configure(image=[])
        self.df = self.select_rows_df(self.df_orig)
        self.draw()

    def prepare_df(self, df):
        # filter the desired time range
        df = df[df.scale == self.scale]
        if self.scale == 'mya':
            df.yearOn = -df.yearOn
            df.yearOff = -df.yearOff

        # ignore empty column
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df

    def select_rows_df(self, df):
        # pre-process the dataframe to make it suitable for display
        df = df.loc[(df['yearOn'] >= self.min) & (df['yearOff'] + 1 < self.max)]
        # determine minimal length
        min_length = np.int(np.ceil((self.max - self.min) / self.winfo_screenwidth())) * 2

        # add column for length of event
        df['length'] = df['yearOff'] - df['yearOn']
        df['length'] = np.where(df.length < min_length, min_length, df['length'])

        # show category depending on toggle setting
        for name, row in self.c_df.iterrows():
            state = row['toggle'].get()
            if state == 0:
                # exclude un-toggled categories
                df = df[df['category'] != row['category']]

        # sort and re-index cleaned df
        df['category'] = pd.Categorical(df['category'], self.category_order)
        df = df.sort_values(['category', 'yearOn'])
        df.index = pd.RangeIndex(len(df.index))
        return df

    def draw(self):
        # embed matplotlib figure in widget
        plt.close("all")
        fig = plt.figure()
        ax = plt.subplot(111)
        plt.subplots_adjust(left=0.02, bottom=0.1, right=0.98, top=1, wspace=0, hspace=0)
        plt.xlabel(self.scale)
        plt.tick_params(axis='y', which='both', left=False, labelleft=False)
        fr4 = FigureCanvasTkAgg(fig, self)
        fr4.get_tk_widget().grid(row=1, column=0, columnspan=3, sticky="nsew")
        linewidth = 1

        # initialize parameters
        my_patches = []
        ypos_group = 0
        ymax = 0

        # loop over categories
        grouped = self.df.groupby('category')
        for cat, group in grouped:
            filled = pd.DataFrame(columns=['ypos', 'on', 'off'])
            for ind, row in group.iterrows():
                # draw the event in the next free row
                ypos = ypos_group + 1

                # add subsequent pathes directly
                if cat in ['supereon', 'eon', 'era', 'period', 'epoch']:
                    while any((filled['ypos'] == ypos) & (((filled['on'] < (row['yearOn'])) & ((row['yearOn']) < filled['off'])) | ((filled['on'] < (row['yearOff'])) & ((row['yearOn'] + row['length']) < filled['off'])))):
                        ypos += 1
                    rect = patches.Rectangle((int(row['yearOn']), -(ypos + linewidth)), row['length'], linewidth * 0.9,
                                             facecolor=self.c_df[self.c_df['category'] == cat].color.unique()[0],
                                             edgecolor='black')
                # start new row for short events
                else:
                    while any((filled['ypos'] == ypos) & (((filled['on'] < (row['yearOn'] - 1)) & ((row['yearOn'] - 1) < filled['off'])) | ((filled['on'] < (row['yearOff'] - 1)) & ((row['yearOn'] + row['length'] + 1) < filled['off'])))):
                        ypos += 1
                    rect = patches.Rectangle((int(row['yearOn']), -(ypos + linewidth)), row['length'], linewidth * 0.9,
                                             facecolor=self.c_df[self.c_df['category'] == cat].color.unique()[0])

                if ypos > ymax:
                    ymax = ypos
                # draw event as rectangle
                ax.add_patch(rect)
                my_patches.append(rect)
                filled = filled.append({'ypos': ypos, 'on': row['yearOn'], 'off': row['yearOn'] + row['length']}, ignore_index=True)

            # start a new cateory in a new row
            ypos_group = ymax

        ax.set_xlim(self.min, self.max)
        ax.set_ylim(-(ypos_group + 1), 0)

        # mouse-over function to display event title
        def mouse_over(event):
            for ind, row in self.df.iterrows():
                if my_patches[ind].contains(event)[0]:
                    self.label_value.set(f'{row.title}: {row.yearOn}')

        # mouse-click function for boxes
        def mouse_click(event):
            for ind, row in self.df.iterrows():
                if my_patches[ind].contains(event)[0]:
                    img = img_google.get_tk_img(row['title'])

                    # fix width:
                    #basewidth = 300
                    # wpercent = (basewidth / float(img.size[0]))
                    # hsize = int((float(img.size[1]) * float(wpercent)))
                    # self._im = img.resize((basewidth, hsize), Image.ANTIALIAS)

                    # fix height:
                    hsize = np.int(self.winfo_screenheight() / 5)
                    wpercent = (hsize / float(img.size[1]))
                    basewidth = int((float(img.size[0]) * float(wpercent)))

                    self._im = img.resize((basewidth, hsize), Image.ANTIALIAS)
                    self._image = ImageTk.PhotoImage(self._im)
                    self.img_label.configure(image=self._image)
                    self.label_value.set(row['title'])
                    return

        fig.canvas.mpl_connect('motion_notify_event', mouse_over)
        fig.canvas.mpl_connect('button_press_event', mouse_click)


# mainloop
if __name__ == "__main__":
    root = timeline()
    root.mainloop()
