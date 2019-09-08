import os
import sys
import pandas as pd
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import pdb
import requests
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from my_functions import img_google


# TODO data browser
# TODO: why is one category overwritten?
class timeline(tk.Tk):
    def __init__(self, filename=os.path.join(os.path.dirname(sys.argv[0]), 'some_dates.csv')):
        tk.Tk.__init__(self)
        self.title("timeline")

        colors = pd.Series(['b', 'g', 'r', 'c', 'm', 'y', 'k'])

        # default time range for the timeline
        self.min = 1500
        self.max = 2000
        self.filename = filename
        self.loadData()
        self.yearFrom = tk.StringVar()
        self.yearFrom.set(self.min)
        self.yearTo = tk.StringVar()
        self.yearTo.set(self.max)

        # create dataframe to store information about categories
        c_df = pd.DataFrame({'types': self.df_orig['type'].unique()})
        c_df['colors'] = colors[0:len(c_df)]
        self.c_df = c_df.sort_values('types')

        fr1 = tk.Frame(self)
        fr1.grid(row=0, column=0, sticky=tk.W)

        #pdb.set_trace()

        # Field and label for 'from'
        tk.Label(fr1, text="From:").pack()
        on = tk.Entry(fr1, textvariable=self.yearFrom, width=4)
        on.pack()
        on.focus_set()

        # Field and label for 'To'
        tk.Label(fr1, text="To:").pack()
        tk.Entry(fr1, textvariable=self.yearTo, width=4).pack()

        # OK button
        tk.Button(fr1, text="OK", command=self.reset).pack()
        self.bind('<Return>', self.reset)

        # toggles for categories displayed
        fr2 = tk.Frame(self)
        fr2.grid(row=0, column=1, sticky=tk.W)

        # make one toggle field for each category
        for i, row in self.c_df.iterrows():
            self.c_df.loc[i, 'toggle'] = tk.IntVar()
            tk.Checkbutton(fr2, text=row['types'], variable=self.c_df.loc[i, 'toggle'], command=self.reset).pack()
            self.c_df.loc[i, 'toggle'].set(1)

        # label for item title
        fr5 = tk.Frame(self)
        fr5.grid(row=0, column=2)
        self.label_value = tk.StringVar()
        tk.Label(fr5, textvariable=self.label_value, width=50).pack()

        # image
        fr4 = tk.Frame(self)
        fr4.grid(row=1, column=2)
        self.img_label = tk.Label(fr4)
        self.img_label.pack()

        self.prepare_df()

        self.draw()

    def loadData(self):
        # TODO: add option to browse through folder
        self.df_orig = pd.read_csv(self.filename)

    def reset(self, *args):
        self.min = int(self.yearFrom.get())
        self.max = int(self.yearTo.get())
        self.label_value.set("")
        self.img_label.configure(image=[])
        self.prepare_df()
        self.draw()

    def prepare_df(self):
        # pre-process the original dataframe to make it suitable for display

        # filter the desired time range
        self.df = self.df_orig.loc[(self.df_orig['yearOn'] > self.min) & (self.df_orig['yearOff'] + 1 < self.max)]

        # ignore empty column
        self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
        # add column for length of event
        self.df['length'] = self.df['yearOff'].get_values() - self.df['yearOn'].get_values()

        # show category depending on toggle setting
        for name, row in self.c_df.iterrows():
            state = row['toggle'].get()
            if state == 0:
                self.df = self.df[self.df['type'] != row['types']]

        # sort and reindex cleaned df
        self.df = self.df.sort_values(['type', 'yearOn'])
        self.df.index = pd.RangeIndex(len(self.df.index))

    def draw(self):
        # embed matplotlib figure in widget
        plt.close("all")
        fig = plt.figure(figsize=(8, 8), dpi=80)
        ax = plt.subplot(111)
        fr3 = FigureCanvasTkAgg(fig, self)
        fr3.get_tk_widget().grid(row=1, column=0, columnspan=2)
        linewidth = 1

        # initialize parameters
        my_patches = []
        filled = pd.DataFrame(columns=['ypos', 'on', 'off'])
        ypos_group = 0
        ymax = 0

        # loop over categories
        grouped = self.df.groupby('type')
        for cat, group in grouped:
            for ind, row in group.iterrows():
                # draw the event in the next free row
                ypos = ypos_group + 1
                while any((filled['ypos'] == ypos) & (((filled['on'] < (row['yearOn'] - 1)) & ((row['yearOn'] - 1) < filled['off'])) | ((filled['on'] < (row['yearOff'] - 1)) & ((row['yearOff'] + 1) < filled['off'])))):
                    ypos += 1
                    if ypos > ymax: ymax = ypos
                # draw event as rectangle
                rect = patches.Rectangle((int(row['yearOn']), -(ypos + linewidth)), row['length'], linewidth * 0.9, facecolor=self.c_df[self.c_df['types'] == cat].colors.unique()[0])
                ax.add_patch(rect)
                my_patches.append(rect)
                filled = filled.append({'ypos': ypos, 'on': row['yearOn'], 'off': row['yearOff']}, ignore_index=True)

            # start a new cateory in a new row
            ypos_group = ymax + 2

        ax.set_xlim(self.min, self.max)
        ax.set_ylim(-(ypos_group + 1), 0)

        def mouse_over(event):
            # mouse-over function to display event title
            for ind, row in self.df.iterrows():
                if my_patches[ind].contains(event)[0]:
                    self.label_value.set(row['title'])

        def mouse_click(event):
            for ind, row in self.df.iterrows():
                if my_patches[ind].contains(event)[0]:
                    basewidth = 300
                    img = img_google.get_tk_img(row['title'])
                    wpercent = (basewidth / float(img.size[0]))
                    hsize = int((float(img.size[1]) * float(wpercent)))
                    self._im = img.resize((basewidth, hsize), Image.ANTIALIAS)
                    self._image = ImageTk.PhotoImage(self._im)
                    self.img_label.configure(image=self._image)
                    self.label_value.set(row['title'])
                    return

        fig.canvas.mpl_connect('motion_notify_event', mouse_over)

        fig.canvas.mpl_connect('button_press_event', mouse_click)


if __name__ == "__main__":
    root = timeline()
    root.mainloop()
