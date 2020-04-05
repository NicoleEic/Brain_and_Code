import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import sys
import os
import numpy as np
import pandas as pd
from matplotlib.collections import PathCollection
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
from io import BytesIO
import urllib
from urllib.request import urlopen, Request
import urllib.parse
from PIL import Image
import requests


class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("My network")
        dd = os.path.join(os.sep, 'Users', 'neichert', 'code', 'projects', 'network')
        self.nodes_orig = pd.read_csv(os.path.join(dd, 'nodes.csv'))
        self.edges_orig = pd.read_csv(os.path.join(dd, 'edges.csv'))
        self.edges_orig['weight'] = np.where(self.edges_orig.category == 'partner', 2, 3)
        self.edges_orig['colour'] = np.where(self.edges_orig.category == 'descendant', 'red', 'blue')

        self.edges = []
        self.network = []
        self.pos = []
        self.cbuts = []
        self.tick_vals = {}
        self._im = []
        self._image = []

        self.frame_tick = tk.Frame(self.master)
        self.frame_tick.grid(row=1, column=0, sticky=tk.W)
        self.text = tk.Text(self.frame_tick)
        self.text.grid(row=1, column=0, sticky=tk.W)

        vsb = tk.Scrollbar(self.frame_tick)
        self.text.configure(width=30, yscrollcommand=vsb.set)
        vsb.grid(row=1, column=0, sticky=tk.E)

        self.frame_buttons = tk.Frame(self.master)
        self.frame_buttons.grid(row=0, column=0, sticky=tk.W)
        tk.Button(self.frame_buttons, text='select all', command=self.select_all_cbuts).grid()
        tk.Button(self.frame_buttons, text='deselect all', command=self.deselect_all_cbuts).grid()
        tk.Button(self.frame_buttons, text='refresh', command=self.click_refresh).grid()

        self.frame_network = tk.Frame(self.master)
        self.frame_network.grid(row=0, column=1, rowspan=2, sticky=tk.W)

        self.frame_info = tk.Frame(self.master)
        self.frame_info.grid(row=0, column=2, rowspan=2, sticky=tk.W)

        self.info_name_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_name_v, width=30).grid(row=0, sticky=tk.N)

        self.info_roman_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_roman_v, width=30).grid(row=1, sticky=tk.N)

        self.info_role_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_role_v, width=30).grid(row=2, sticky=tk.N)

        self.img_label = tk.Label(self.frame_info)
        self.img_label.grid(row=3)

        self.create_cbuts()
        self.update_edges()
        self.generate_network()
        self.draw_network()

    def reset_info(self):
        self.info_name_v.set("Click on a name for info.")
        self.info_roman_v.set("")
        self.info_role_v.set("")
        self.img_label.configure(image=[])

    def generate_network(self):
        self.network = nx.from_pandas_edgelist(self.edges, 'node1', 'node2', edge_attr=True)
        #self.network = self.network.to_directed()
        self.pos = nx.layout.spring_layout(self.network)

    def draw_network(self):
        def onpick(event):
            if isinstance(event.artist, PathCollection):
                ind = event.ind[0]  # event.ind is a single element array.
                node_name = list(self.pos.keys())[ind]
                self.info_name_v.set(node_name)
                node = self.nodes_orig[self.nodes_orig.name == node_name]
                if node.empty:
                    self.info_roman_v.set("no info entered")
                else:
                    self.info_roman_v.set(f'roman name: {node.roman.values[0]}')
                    self.info_role_v.set(f'role: {node.role.values[0]}')
                show_img(node_name)

        def show_img(node_name):
            def get_tk_img(query):
                rootdir = 'https://www.greekmythology.com'
                category = self.nodes_orig[self.nodes_orig.name == query].category.values[0]
                url = f'{rootdir}/{category}s/{query}/{query}.html'
                page = requests.get(url).text
                soup = BeautifulSoup(page, 'html.parser')
                for element in soup.find_all("img"):
                    my_url = element.get('data-src')
                    if my_url:
                        if '/images/mythology' in my_url:
                            req = Request(url=f'{rootdir}{my_url}', headers={'User-Agent': 'Mozilla/5.0'})
                            u = urlopen(req)
                            a = u.read()
                            u.close()
                            im = Image.open(BytesIO(a))
                            return im
            basewidth = 300
            img = get_tk_img(node_name)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            self._im = img.resize((basewidth, hsize), Image.ANTIALIAS)
            self._image = ImageTk.PhotoImage(self._im)
            self.img_label.configure(image=self._image)

        plt.close("all")
        for widget in self.frame_network.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        nodes = nx.draw_networkx_nodes(self.network, self.pos, ax=ax, node_size=10)
        nodes.set_picker(5)
        nx.draw_networkx_edges(self.network, self.pos, arrowstyle='->', arrowsize=15, width=1, edge_color=self.edges['colour'], ax=ax)
        nx.draw_networkx_labels(self.network, self.pos, ax=ax)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_network)
        canvas.draw()
        canvas.get_tk_widget().grid(sticky=tk.NSEW)
        fig.canvas.mpl_connect('pick_event', onpick)

    def create_cbuts(self):
        all_node_names = list(set(self.edges_orig['node1'].tolist() + self.edges_orig['node2'].tolist()))
        all_node_names.sort()
        for node_name in all_node_names:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.text, text=node_name, variable=var)
            cb.select()
            cb.grid()
            self.cbuts.append(cb)
            self.tick_vals[node_name] = var
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n")
        self.text.configure(state="disabled")

    def update_edges(self):
        ind_include = np.array([])
        for ind, row in self.edges_orig.iterrows():
            if self.tick_vals[row['node1']].get() or self.tick_vals[row['node2']].get():
                ind_include = np.append(ind_include, ind)
        self.edges = self.edges_orig.iloc[ind_include]
        self.reset_info()

    def select_all_cbuts(self):
        for i in self.cbuts:
            i.var = 1
            i.select()

    def deselect_all_cbuts(self):
        for i in self.cbuts:
            i.var = 0
            i.deselect()

    def click_refresh(self):
        self.update_edges()
        self.generate_network()
        self.draw_network()


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
