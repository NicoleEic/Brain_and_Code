#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Nicole Eichert <n.eichert@googlemail.com>
#
# Distributed under terms of the MIT license.

import networkx as nx
import numpy as np
import os
import pandas as pd
import requests
import sys
import tkinter as tk
import webbrowser
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import ttk
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from urllib.request import urlopen, Request


class Gmn:
    def __init__(self, master):
        self.master = master
        master.title("GMN - Greek Mythology Network")

        # data paths
        self.dd = os.path.join(os.path.dirname(__file__), 'assets')
        self.nodes = pd.read_csv(os.path.join(self.dd, 'nodes.csv'))

        self.edges_full = pd.read_csv(os.path.join(self.dd, 'edges.csv'))
        self.add_columns()
        self.website = 'https://www.greekmythology.com'

        # initialize attributes
        self.edges_selected = []
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
        self.frame_network.grid(row=0, column=1, rowspan=2)

        # build frame_info
        self.frame_info = tk.Frame(self.master)
        self.frame_info.grid(row=0, column=2)

        labelfont = ('Courir', 20, 'bold')
        tk.Label(self.frame_info, text='-> partner', font=labelfont, fg="plum").grid(row=0)
        tk.Label(self.frame_info, text='-> descendant', font=labelfont, fg="lightgreen").grid(row=1)

        self.info_info_v = tk.StringVar()
        self.info_info_v.set("Click on a name for info.")
        tk.Label(self.frame_info, textvariable=self.info_info_v).grid(row=2)

        self.info_name_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_name_v).grid(row=3)

        self.img_label = tk.Label(self.frame_info)
        self.img_label.grid(row=4)

        self.info_credit_v = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.info_credit_v).grid(row=5)

        self.info_btn_v = tk.StringVar()
        tk.Button(self.frame_info, textvariable=self.info_btn_v, command=self.open_website).grid(row=6)

        tk.Button(self.frame_info, text='Enter new edges', command=self.add_edges).grid(row=7)

        # start up app
        self.default_selection_nodes()
        self.update_edges()
        self.reset_info()
        self.create_treeview()
        self.generate_network()
        self.draw_network()

    # add new columns to dataframes
    def add_columns(self):
        self.nodes['enabled'] = [True if name in list(set(self.edges_full['node1'].tolist() + self.edges_full['node2'].tolist())) else False for name in self.nodes['name']]
        self.nodes = self.nodes.sort_values(by=['enabled', 'name'], ascending=(False, True))
        self.nodes['show'] = self.nodes['enabled']
        #self.nodes['ID'] = 'not defined'
        self.edges_full['width'] = np.where(self.edges_full.category == 'partner', 3, 3)
        self.edges_full['colour'] = np.where(self.edges_full.category == 'partner', 'plum', 'lightgreen')

    # default settings for which nodes will be displayed
    def default_selection_nodes(self):
        self.nodes['show'] = False
        self.nodes.loc[self.nodes['name'].isin(['Chaos', 'Rhea']), 'show'] = True

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
        self.nodes['show'] = self.nodes['enabled']
        for ind, node in self.nodes[self.nodes['show'] == True].iterrows():
            my_id = node['ID']
            name = node['name']
            if node['show']:
                self.tree.item(my_id, text=f'X {name}')
                self.nodes.loc[self.nodes.name == name, 'show'] = True

    def action_click_deselect_all(self):
        self.nodes['show'] = False
        for child in self.tree.get_children():
            for sub_child in self.tree.get_children(child):
                name = self.tree.item(sub_child)['values'][0]
                self.tree.item(sub_child, text=f'_ {name}')

    def action_click_refresh(self):
        self.update_edges()
        if self.edges_selected.empty:
            self.info_info_v.set('no nodes selected')
            self.reset_info()
        else:
            self.generate_network()
            self.draw_network()
            self.info_info_v.set("Click on a name for info.")
            self.reset_info()

    # callback for double click on label
    def action_double_click(self, event):
        my_id = self.tree.selection()[0]
        self.name = self.tree.item(my_id)['values'][0]
        if self.name in self.nodes.name.to_list():
            node = self.nodes[self.nodes.ID == my_id]
            if node['enabled'].values[0]:
                if node['show'].values[0]:
                    self.tree.item(my_id, text=f'_ {self.name}')
                    self.nodes.loc[self.nodes.name == self.name, 'show'] = False
                else:
                    self.tree.item(my_id, text=f'X {self.name}')
                    self.nodes.loc[self.nodes.name == self.name, 'show'] = True
            else:
                self.info_info_v.set('no links entered')
                self.update_info()
        elif self.name in self.nodes.category.to_list():
            subset = self.nodes[(self.nodes['category'] == self.name) & (self.nodes['enabled'] == True)]
            if any([item == False for item in subset.show.to_list()]):
                for ind, node in subset.iterrows():
                    name = node['name']
                    self.tree.item(node['ID'], text=f'X {name}')
                    self.nodes.loc[self.nodes.name == name, 'show'] = True
            elif all([item == True for item in subset.show.to_list()]):
                for ind, node in subset.iterrows():
                    name = node['name']
                    self.tree.item(node['ID'], text=f'_ {name}')
                    self.nodes.loc[self.nodes.name == name, 'show'] = False

    # clear info frame
    def reset_info(self):
        self.name = []
        self.info_name_v.set("")
        self.img_label.configure(image=[])
        self.info_credit_v.set("")
        self.info_btn_v.set('...')

    # populate info frame
    def update_info(self):
        if self.name in self.nodes.name.to_list():
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
        category = self.nodes[self.nodes.name == self.name].category.values[0]
        url = f'{self.website}/{category}s/{self.name}/{self.name}.html'
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
        #self.network = nx.from_pandas_edgelist(self.edges_selected, 'node1', 'node2', edge_attr=True)
        self.network = nx.from_pandas_edgelist(self.edges_selected, source='node1', target='node2', create_using = nx.DiGraph(), edge_attr=True)
        #self.network = self.network.to_directed()
        #self.pos = nx.layout.spring_layout(self.network)
        self.pos = nx.nx_agraph.graphviz_layout(self.network)

    # draw network
    def draw_network(self):
        plt.close("all")
        for widget in self.frame_network.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        nodes = nx.draw_networkx_nodes(self.network, self.pos, ax=ax, node_size=10, node_color='w')
        nodes.set_picker(5)
        nx.draw_networkx_edges(self.network, self.pos,
                               arrowstyle='->', arrowsize=15,
                               min_source_margin=10, min_target_margin=10,
                               width=list(nx.get_edge_attributes(self.network, 'width').values()),
                               edge_color=nx.get_edge_attributes(self.network, 'colour').values(),
                               connectionstyle='arc3,rad=0.2', ax=ax)
        nx.draw_networkx_labels(self.network, self.pos, font_weight='bold', ax=ax)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_network)
        canvas.draw()

        canvas.get_tk_widget().grid()
        fig.canvas.mpl_connect('pick_event', self.action_click_name)

    # generate treeview based on info in nodes and edges
    def create_treeview(self):
        for cat, subset in self.nodes.groupby('category'):
            self.tree.insert('', 'end', cat, values=cat, text=cat)
            for ind, node in subset.iterrows():
                node_name = str(node['name'])
                my_id = self.tree.insert(cat, 'end', values=node_name, tag=node['enabled'])
                self.nodes.at[ind, 'ID'] = my_id
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
        for ind, row in self.edges_full.iterrows():
            if row['node1'] in self.nodes[self.nodes.show == True].name.tolist() \
                    or row['node2'] in self.nodes[self.nodes.show == True].name.tolist():
                ind_include = np.append(ind_include, ind)
        self.edges_selected = self.edges_full.iloc[ind_include]

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
                    req = Request(url=f'{self.website}{sub_url}', headers={'User-Agent': 'Mozilla/5.0'})
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
        self.info_credit_v.set(f'Source: {self.website}')
        # self._image = []
        # self.info_credit_v.set("no image found")

    def add_edges(self):
        self.edges_full = EdgeEntry(self).return_df()
        self.add_columns()
        self.default_selection_nodes()
        self.update_edges()
        self.reset_info()
        self.tree.delete(*self.tree.get_children())
        self.create_treeview()
        self.generate_network()
        self.draw_network()


class EdgeEntry:
    def __init__(self, parent):
        self.master = tk.Toplevel()
        self.master.title("Enter a new edge")
        self.dd = parent.dd
        self.column_headers = ['node1', 'node2', 'category', 'comment']
        self.nodes = parent.nodes
        self.edges_full = parent.edges_full[self.column_headers]
        # set up fields
        self.dict_fields = {}
        for ind, field in enumerate(self.column_headers):
            tk.Label(self.master, text=field, width=20).grid(row=0, column=ind)
            var = tk.StringVar()
            self.dict_fields[field] = var
            tk.Entry(self.master, textvariable=var).grid(row=1, column=ind)
        tk.Button(self.master, text='Add entry', command=self.add_entry).grid(row=2, column=0)
        tk.Button(self.master, text='Safe to file', command=self.save).grid(row=2, column=1)
        tk.Button(self.master, text='Done', command=self.close).grid(row=2, column=2)

    def add_entry(self):
        self.edges_full.loc[len(self.edges_full)] = [field.get() for field in self.dict_fields.values()]
        for field in self.dict_fields.values():
            field.set("")

    def save(self):
        self.edges_full[self.column_headers].to_csv(os.path.join(self.dd, 'edges.csv'), index=False)

    def close(self):
        self.master.destroy()

    def return_df(self):
        self.master.wait_window()
        return self.edges_full


def main():
    root = tk.Tk()
    Gmn(root)
    root.mainloop()


if __name__ == "__main__":
    main()

