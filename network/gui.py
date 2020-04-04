import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

DD = os.path.join(os.sep, 'Users', 'neichert', 'code', 'projects', 'network')

nodes = pd.read_csv(os.path.join(DD, 'nodes.csv'))
node_names = nodes.name.tolist()
edges = pd.read_csv(os.path.join(DD, 'edges.csv'))
edges['weight'] = np.where(edges.category == 'partner', 2, 3)
edge_pairs_w = [tuple(x) for x in edges[['node1', 'node2', 'weight']].values]
#node_names = list(set(edges[['node1', 'node2']].values.reshape(-1).tolist()))

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_weighted_edges_from(edge_pairs_w)

root = tk.Tk()
root.wm_title("My network")

fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
ax = fig.add_subplot(111)
nx.draw(G, with_labels=True, ax=ax)

frame_network = tk.Frame(root)
frame_network.pack(side=tk.LEFT)

canvas = FigureCanvasTkAgg(fig, master=frame_network)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

bottomframe = tk.Frame(root)
bottomframe.pack(side=tk.RIGHT)

# initialize nodes tickbox list
tick_vars = {}
for node_name in node_names:
    node = nodes[nodes.name == node_name]
    var = tk.IntVar()
    cb = tk.Checkbutton(bottomframe, text=node.name.values[0], variable=var)
    if node.tick_var.values[0] == 1:
        cb.select()
    cb.pack()
    tick_vars[node_name] = var


def check_tick_vars():
    values = [(node_name, var.get()) for node_name, var in tick_vars.items()]
    print(values)

button = tk.Button(bottomframe, text="Quit", command=root.quit())
button.pack()

check_tick_vars()
tk.mainloop()
