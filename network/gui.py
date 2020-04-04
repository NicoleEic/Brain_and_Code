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

        self.frame_tick = tk.Frame(root)
        self.frame_tick.pack(side=tk.LEFT)
        self.text = tk.Text(self.frame_tick, cursor="arrow")
        self.vsb = tk.Scrollbar(self.frame_tick, command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.pack(side=tk.LEFT, expand=True)
        self.vsb.pack()

        self.create_cbuts()
        self.update_nodes()

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack()

        self.btn_select = tk.Button(self.frame_buttons, text='select all', command=self.select_all_cbuts)
        self.btn_select.pack(side=tk.RIGHT)

        self.btn_deselect = tk.Button(self.frame_buttons, text='deselect all', command=self.deselect_all_cbuts)
        self.btn_deselect.pack(side=tk.RIGHT)

        self.btn_refresh = tk.Button(self.frame_buttons, text='refresh', command=self.click_refresh)
        self.btn_refresh.pack(side=tk.RIGHT)

        self.frame_network = tk.Frame(root)
        self.frame_network.pack(side=tk.RIGHT)

        self.generate_network()
        self.draw_network()

    def generate_network(self):
        self.edges = self.edges_orig[(self.edges_orig['node1'].isin(self.nodes.name)) | (self.edges_orig['node2'].isin(self.nodes.name))]
        g = nx.from_pandas_edgelist(self.edges, 'node1', 'node2', edge_attr=True)
        g.add_nodes_from(self.nodes.name)
        plt.show()
        self.network = g

    def draw_network(self):
        plt.close("all")
        for widget in self.frame_network.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        nx.draw(self.network, with_labels=True, ax=ax, edge_color=self.edges['colour'], node_size=10)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_network)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def create_cbuts(self):
        for ind, row in self.nodes_orig.iterrows():
            var = tk.IntVar()
            cb = tk.Checkbutton(self.text, text=row['name'], variable=var)
            self.cbuts.append(cb)
            self.cbuts[-1].pack()
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
