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


class MainApplication:
    def __init__(self, master):
        self.master = master

        master.title("My network")
        dd = os.path.join(os.sep, 'Users', 'neichert', 'code', 'projects', 'network')
        self.nodes_orig = pd.read_csv(os.path.join(dd, 'nodes.csv'))
        self.edges_orig = pd.read_csv(os.path.join(dd, 'edges.csv'))
        self.edges_orig['weight'] = np.where(self.edges_orig.category == 'partner', 2, 3)
        self.edges_orig['colour'] = np.where(self.edges_orig.category == 'partner', 'red', 'blue')

        self.nodes = []
        self.edges = []
        self.network = []
        self.cbuts = []
        self.tick_vals = {}

        self.frame_tick = tk.Frame(self.master)
        self.frame_tick.grid(row=0, column=0, sticky=tk.W)
        self.text = tk.Text(self.frame_tick)
        self.text.grid(row=0, column=0, sticky=tk.W)

        self.vsb = tk.Scrollbar(self.frame_tick)
        self.text.configure(width=30, yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=0, sticky=tk.E)

        self.create_cbuts()
        self.update_nodes()

        self.frame_buttons = tk.Frame(self.master)
        self.frame_buttons.grid(row=1, column=0, sticky=tk.W)

        self.btn_select = tk.Button(self.frame_buttons, text='select all', command=self.select_all_cbuts)
        self.btn_select.grid()

        self.btn_deselect = tk.Button(self.frame_buttons, text='deselect all', command=self.deselect_all_cbuts)
        self.btn_deselect.grid()

        self.btn_refresh = tk.Button(self.frame_buttons, text='refresh', command=self.click_refresh)
        self.btn_refresh.grid()

        self.frame_network = tk.Frame(self.master)
        self.frame_network.grid(row=0, column=1, rowspan=2, sticky=tk.W)

        self.generate_network()
        self.draw_network()

    def generate_network(self):
        self.edges = self.edges_orig[(self.edges_orig['node1'].isin(self.nodes.name)) | (self.edges_orig['node2'].isin(self.nodes.name))]
        g = nx.from_pandas_edgelist(self.edges, 'node1', 'node2', edge_attr=True)
        g.add_nodes_from(self.nodes.name)
        self.network = g

    def draw_network(self):
        plt.close("all")
        for widget in self.frame_network.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        nx.draw(self.network, with_labels=True, ax=ax, edge_color=self.edges['colour'], node_size=10)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_network)
        canvas.draw()
        canvas.get_tk_widget().grid(sticky=tk.NSEW)

    def create_cbuts(self):
        for ind, row in self.nodes_orig.iterrows():
            var = tk.IntVar()
            cb = tk.Checkbutton(self.text, text=row['name'], variable=var)
            self.cbuts.append(cb)
            self.cbuts[-1].grid()
            if row['tick_var'] == 1:
                self.cbuts[-1].select()
            self.tick_vals[row['name']] = var
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n")
        self.text.configure(state="disabled")

    def update_nodes(self):
        ind_include = np.array([])
        for ind, row in self.nodes_orig.iterrows():
            if self.tick_vals[row['name']].get():
                ind_include = np.append(ind_include, ind)
        self.nodes = self.nodes_orig.iloc[ind_include]

    def select_all_cbuts(self):
        for i in self.cbuts:
            i.var = 1
            i.select()

    def deselect_all_cbuts(self):
        for i in self.cbuts:
            i.var = 0
            i.deselect()

    def click_refresh(self):
        self.update_nodes()
        self.generate_network()
        self.draw_network()


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
