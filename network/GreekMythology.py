import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
from urllib.request import urlopen, Request
from PIL import Image
import requests
import webbrowser

# TODO: change symbol when de/select all items upon double click on category
# TODO: fix colours edges


class GreekMythology:
    def __init__(self, master):
        self.master = master
        master.title("My network")

        # data paths
        dd = os.path.join(os.sep, 'Users', 'neichert', 'code', 'projects', 'network')
        self.nodes_orig = pd.read_csv(os.path.join(dd, 'nodes.csv'))
        self.edges_orig = pd.read_csv(os.path.join(dd, 'edges.csv'))
        self.rootdir = 'https://www.greekmythology.com'

        # add new columns to dataframes
        self.nodes_orig['enabled'] = [True if name in list(set(self.edges_orig['node1'].tolist() + self.edges_orig['node2'].tolist())) else False for name in self.nodes_orig['name']]
        self.nodes_orig['show'] = self.nodes_orig['enabled']
        self.nodes_orig['ID'] = 'not defined'
        self.edges_orig['weight'] = np.where(self.edges_orig.category == 'partner', 2, 3)
        self.edges_orig['colour'] = np.where(self.edges_orig.category == 'descendant', 'red', 'blue')

        # initialize attributes
        self.edges = []
        self.network = []
        self.pos = []
        self._im = []
        self._image = []
        self.name = []

        # build frame_treeview
        self.frame_treeview = tk.Frame(self.master)
        self.frame_treeview.grid(row=0, column=0, sticky=tk.W)

        self.tree = ttk.Treeview(self.frame_treeview, height=25)
        self.tree.grid(row=1, column=0, sticky=tk.E)

        vsb = tk.Scrollbar(self.frame_treeview, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=0, sticky=tk.E)
        self.tree.configure(yscrollcommand=vsb.set)

        # build frame_buttons
        self.frame_buttons = tk.Frame(self.master)
        self.frame_buttons.grid(row=1, column=0, sticky=tk.W)
        tk.Label(self.frame_buttons, text='double click label to de/select').grid()

        self.btn_text = tk.StringVar()
        self.btn_text.set('expand all')
        tk.Button(self.frame_buttons, textvariable=self.btn_text, command=self.action_click_expand_all).grid()

        tk.Button(self.frame_buttons, text='select all', command=self.action_click_select_all).grid()
        tk.Button(self.frame_buttons, text='deselect all', command=self.action_click_deselect_all).grid()
        tk.Button(self.frame_buttons, text='refresh', command=self.action_click_refresh).grid()

        # build frame_network
        self.frame_network = tk.Frame(self.master)
        self.frame_network.grid(row=0, column=1, rowspan=2, sticky=tk.W)

        # build frame_info
        self.frame_info = tk.Frame(self.master)
        self.frame_info.grid(row=0, column=2, rowspan=2, sticky=tk.W)

        self.info_info_v = tk.StringVar()
        self.info_info_v.set("Click on a name for info.")
        tk.Label(self.frame_info, textvariable=self.info_info_v, width=30).grid(row=0, sticky=tk.N)

        self.info_name_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_name_v, width=30).grid(row=1, sticky=tk.N)

        self.img_label = tk.Label(self.frame_info)
        self.img_label.grid(row=2)

        self.info_credit_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_credit_v, width=30).grid(row=3, sticky=tk.N)

        self.info_btn_v = tk.StringVar()
        tk.Button(self.frame_info, textvariable=self.info_btn_v, command=self.open_website).grid(row=4, sticky=tk.N)

        # start up app
        self.default_selection_nodes()
        self.update_edges()
        self.reset_info()
        self.create_treeview()
        self.generate_network()
        self.draw_network()

    # default settings for which nodes will be displayed
    def default_selection_nodes(self):
        self.nodes_orig['show'] = False
        self.nodes_orig.loc[self.nodes_orig.name == 'Zeus', 'show'] = True

    # callback buttons
    def action_click_expand_all(self):
        if self.btn_text.get() == 'expand all':
            self.btn_text.set('close all')
            for child in self.tree.get_children():
                self.tree.item(child, open=True)
        else:
            self.btn_text.set('expand all')
            for child in self.tree.get_children():
                self.tree.item(child, open=False)

    def action_click_select_all(self):
        self.nodes_orig['show'] = self.nodes_orig['enabled']
        for ind, node in self.nodes_orig[self.nodes_orig['show'] == True].iterrows():
            my_id = node['ID']
            name = node['name']
            if node['show']:
                self.tree.item(my_id, text=f'X {name}')
                self.nodes_orig.loc[self.nodes_orig.name == name, 'show'] = True

    def action_click_deselect_all(self):
        self.nodes_orig['show'] = False
        for child in self.tree.get_children():
            for sub_child in self.tree.get_children(child):
                name = self.tree.item(sub_child)['values'][0]
                self.tree.item(sub_child, text=f'_ {name}')

    def action_click_refresh(self):
        self.update_edges()
        if self.edges.empty:
            self.info_info_v.set('no nodes selected')
            self.reset_info()
        else:
            self.generate_network()
            self.draw_network()
            self.info_info_v.set("Click on a name for info.")

    # callback for double click on label
    def action_double_click(self, event):
        my_id = self.tree.selection()[0]
        self.name = self.tree.item(my_id)['values'][0]
        if self.name in self.nodes_orig.name.to_list():
            node = self.nodes_orig[self.nodes_orig.ID == my_id]
            if node['enabled'].values[0]:
                if node['show'].values[0]:
                    self.tree.item(my_id, text=f'_ {self.name}')
                    self.nodes_orig.loc[self.nodes_orig.name == self.name, 'show'] = False
                else:
                    self.tree.item(my_id, text=f'X {self.name}')
                    self.nodes_orig.loc[self.nodes_orig.name == self.name, 'show'] = True
            else:
                self.info_info_v.set('no links entered')
                self.update_info()
        elif self.name in self.nodes_orig.category.to_list():
            subset = self.nodes_orig[(self.nodes_orig['category'] == self.name) & (self.nodes_orig['enabled'] == True)]
            if any([item == False for item in subset.show.to_list()]):
                for ind, node in subset.iterrows():
                    name = node['name']
                    self.tree.item(node['ID'], text=f'X {name}')
                    self.nodes_orig.loc[self.nodes_orig.name == name, 'show'] = True
            elif all([item == True for item in subset.show.to_list()]):
                for ind, node in subset.iterrows():
                    name = node['name']
                    self.tree.item(node['ID'], text=f'_ {name}')
                    self.nodes_orig.loc[self.nodes_orig.name == name, 'show'] = False

    # clear info frame
    def reset_info(self):
        self.name = []
        self.info_name_v.set("")
        self.img_label.configure(image=[])
        self.info_credit_v.set("")
        self.info_btn_v.set('...')

    # populate info frame
    def update_info(self):
        if self.name in self.nodes_orig.name.to_list():
            self.info_info_v.set("")
            self.info_name_v.set(self.name)
            try:
                self.show_img()
                self.info_btn_v.set('Open website')
            except:
                self.info_info_v.set('Cannot load image')
                self.reset_info()
        else:
            self.info_info_v.set('name not in nodes list')
            self.reset_info()

    # compose url from node name and category
    def get_url(self):
        category = self.nodes_orig[self.nodes_orig.name == self.name].category.values[0]
        url = f'{self.rootdir}/{category}s/{self.name}/{self.name}.html'
        return url

    # callback to click on node in network
    def action_click_name(self, event):
        if isinstance(event.artist, PathCollection):
            ind = event.ind[0]
            name = list(self.pos.keys())[ind]
            self.name = name
            self.update_info()

    # generate network from selection of edges
    def generate_network(self):
        self.network = nx.from_pandas_edgelist(self.edges, 'node1', 'node2', edge_attr=True)
        self.pos = nx.layout.spring_layout(self.network)

    # draw network
    def draw_network(self):
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
        fig.canvas.mpl_connect('pick_event', self.action_click_name)

    # generate treeview based on info in nodes and edges
    def create_treeview(self):
        for cat, subset in self.nodes_orig.groupby('category'):
            self.tree.insert('', 'end', cat, values=cat, text=cat)
            for ind, node in subset.iterrows():
                node_name = str(node['name'])
                my_id = self.tree.insert(cat, 'end', values=node_name, tag=node['enabled'])
                self.nodes_orig.at[ind, 'ID'] = my_id
                if node['show']:
                    self.tree.item(my_id, text=f'X {node_name}')
                else:
                    self.tree.item(my_id, text=f'_ {node_name}')
        self.tree.tag_configure(False, foreground='grey')
        self.tree.bind("<Double-1>", self.action_double_click)
        self.tree.item('Olympian', open=True)

    # update edges based on selection in treeview
    def update_edges(self):
        ind_include = np.array([])
        for ind, row in self.edges_orig.iterrows():
            if row['node1'] in self.nodes_orig[self.nodes_orig.show == True].name.tolist() \
                    or row['node2'] in self.nodes_orig[self.nodes_orig.show == True].name.tolist():
                ind_include = np.append(ind_include, ind)
        self.edges = self.edges_orig.iloc[ind_include]
        self.reset_info()

    # open mythology website
    def open_website(self):
        try:
            url = self.get_url()
            webbrowser.open(url, new=2)
        except:
            print(url)
            self.info_info_v.set('could not open url')

    # scrap image from website
    def get_tk_img(self):
        url = self.get_url()
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        for element in soup.find_all("img"):
            sub_url = element.get('data-src')
            if sub_url:
                if '/images/mythology' in sub_url:
                    req = Request(url=f'{self.rootdir}{sub_url}', headers={'User-Agent': 'Mozilla/5.0'})
                    u = urlopen(req)
                    a = u.read()
                    u.close()
                    im = Image.open(BytesIO(a))
                    return im

    # place image in frame
    def show_img(self):
        img = self.get_tk_img()
        basewidth = 300
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        self._im = img.resize((basewidth, hsize), Image.ANTIALIAS)
        self._image = ImageTk.PhotoImage(self._im)
        self.img_label.configure(image=self._image)
        self.info_credit_v.set(f'Source: {self.rootdir}')
        # self._image = []
        # self.info_credit_v.set("no image found")


if __name__ == "__main__":
    root = tk.Tk()
    GreekMythology(root)
    root.mainloop()
