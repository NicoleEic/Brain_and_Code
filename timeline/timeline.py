import os
import sys
import pandas as pd
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import pdb
from bs4 import BeautifulSoup
import requests
sys.path.append('../')
from my_functions import img_google


class timeline(tk.Tk):
    def __init__(self, filename=os.path.join(os.path.dirname(sys.argv[0]), 'some_dates.csv')):
        tk.Tk.__init__(self)
        self.title("timeline")

        # default time range for the timeline
        self.min = 1500
        self.max = 2000

        colors = pd.Series(['b', 'g', 'r', 'c', 'm', 'y', 'k'])

        self.filename = filename
        self.loadData()

        # Field and label for 'from'
        self.yearOn_label = tk.Label(text="From:")
        self.yearOn_label.grid(row=0, column=0, sticky=tk.W)

        entryText = tk.StringVar()
        self.yearOn_entry = tk.Entry(textvariable=entryText, width=4)
        entryText.set(self.min)
        self.yearOn_entry .grid(row=0, column=1, sticky=tk.W)
        self.yearOn_entry.focus_set()

        # Field and label for 'To'
        self.yearOff_label = tk.Label(text="To:")
        self.yearOff_label.grid(row=0, column=2, sticky=tk.W)

        entryText = tk.StringVar()
        self.yearOff_entry = tk.Entry(textvariable=entryText, width=4)
        entryText.set(self.max)
        self.yearOff_entry.grid(row=0, column=3, sticky=tk.W)

        # OK button
        self._sett_button = tk.Button(text="OK", command=self.reset)
        self._sett_button.grid(row=0, column=4, sticky=tk.W)
        self.bind('<Return>', self.reset)

        # toggles for categories displayed

        # create dataframe to store information about categories
        self.c_df = pd.DataFrame({'types': self.df_orig['type'].unique()})
        self.c_df['colors'] = colors[0:len(self.c_df)]
        self.c_df = self.c_df.sort_values('types')

        # make one toggle field for each category
        for i, row in self.c_df.iterrows():
            self.c_df.loc[i, 'toggle'] = tk.IntVar()
            check_button = tk.Checkbutton(self, text=row['types'], variable=self.c_df.loc[i, 'toggle'], command=self.reset)
            self.c_df.loc[i, 'toggle'].set(1)
            check_button.grid(row=i + 2, column=5, sticky='w')

        # label for item title
        self.label_value = tk.StringVar()
        self.label = tk.Label(textvariable=self.label_value)
        self.label.grid(row=2, column=0, columnspan=3, sticky=tk.W)

        # #Todo: img - to show one mouseover - doesn't work
        self.img_label = tk.Label()
        self.img_label.grid(row=1, column=5)

        self.prepare_df()
        self.draw()

    def loadData(self):
        # Todo: add option to browse through folder
        self.df_orig = pd.read_csv(self.filename)

    def reset(self, *args):
        self.min = int(self.yearOn_entry.get())
        self.max = int(self.yearOff_entry.get())
        self.label_value.set("..........")
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
        self.df['length'] = self.df['yearOff'] - self.df['yearOn']

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
        fig = plt.figure(figsize=(8, 8), dpi=80)
        ax = plt.subplot(111)
        a = FigureCanvasTkAgg(fig, self)
        a.get_tk_widget().grid(column=0, row=1, columnspan=5, sticky=tk.W)

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
            ypos_group = ymax + 1

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
