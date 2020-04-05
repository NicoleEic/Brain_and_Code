import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import os
import numpy as np
import pandas as pd
from ast import literal_eval
from matplotlib.collections import PathCollection


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

        self.frame_tick = tk.Frame(self.master)
        self.frame_tick.grid(row=1, column=0, sticky=tk.W)
        self.text = tk.Text(self.frame_tick)
        self.text.grid(row=1, column=0, sticky=tk.W)

        self.vsb = tk.Scrollbar(self.frame_tick)
        self.text.configure(width=30, yscrollcommand=self.vsb.set)
        self.vsb.grid(row=1, column=0, sticky=tk.E)

        self.create_cbuts()
        self.update_edges()

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
        tk.Label(self.frame_info, textvariable=self.info_name_v).grid(row=0)
        self.info_name_v.set("Click on a name for info.")

        self.generate_network()
        self.draw_network()

    def generate_network(self):
        self.network = nx.from_pandas_edgelist(self.edges, 'node1', 'node2', edge_attr=True)
        self.network = self.network.to_directed()
        self.pos = nx.layout.spring_layout(self.network)

    def draw_network(self):
        def onpick(event):
            if isinstance(event.artist, PathCollection):
                ind = event.ind[0]  # event.ind is a single element array.
                node_name = list(self.pos.keys())[ind]
                self.info_name_v.set(node_name)

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
