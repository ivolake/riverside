import matplotlib.pyplot as plt
import networkx as nx
from numpy import random
# from random import randint
import os

from Graphs import BaseGraph
from Paths import PathCollection
from config import OUTPUT_PATH
from functions import generate_separate_graph_and_weights, generate_pos, generate_path_edges


class BaseDrawer():
    def __init__(self, graph: BaseGraph, inc_nodes=None, dec_nodes=None):
        if dec_nodes is None:
            dec_nodes = []
        if inc_nodes is None:
            inc_nodes = []
        self.graph = graph
        self.inc_nodes = inc_nodes
        self.dec_nodes = dec_nodes

    def draw_graph(self, file_name: str = None, ipos: int = 0, show: bool = True):
        """
        Рисует граф без путей, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------
        (raw_graph, edges_labels) = generate_separate_graph_and_weights(self.graph.struct)  # превращаю взвешенный граф в
                                                                                       # читабельный для программы вид

        figure_size = len(raw_graph.keys())
        G = nx.DiGraph(raw_graph)  # создаю граф из образа digraph
        fig = plt.figure(figsize=(int(13 * figure_size / 11), int(7 * figure_size / 11)),
                         dpi=100)  # для  сохранения картинки с помощью fig.savefig()
        # Size in pixels = figsize * dpi

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        G.add_nodes_from(G.nodes, color='#949494')  # brcmyk - colors
        G.add_nodes_from(self.inc_nodes, color='#5dff4f')
        G.add_nodes_from(self.dec_nodes, color='#fc2a2a')
        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(G, 'color')
        nodes = node_color_attr.keys()  # без list() работает в рисовалке
        nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        G.add_edges_from(G.edges, color='black', width=1)  # добавляем все ребра черными

        edge_color_attr = nx.get_edge_attributes(G, 'color')
        edge_width_attr = nx.get_edge_attributes(G, 'width')
        edges = edge_color_attr.keys()  # без list() работает в рисовалке
        edges_colors = edge_color_attr.values()  # без list() работает в рисовалке
        edges_widths = list(edge_width_attr.values())  # без list() не работает в рисовалке

        # создаю координаты вершин графа
        if ipos == 1:
            pos = generate_pos(raw_graph)
        elif ipos == 2:
            pos = nx.circular_layout(G)
        elif ipos == 3:
            pos = nx.random_layout(G)
        else:
            raise Exception(f'ipos parameter ({ipos}) is incorrect')

        # рисование
        nx.draw(G, pos=pos,
                edgelist=edges, edge_color=edges_colors, width=edges_widths,
                nodelist=nodes, node_color=nodes_colors, node_shape='s',
                node_size=450, font_size=16, font_family='sans-serif',
                with_labels=True, font_weight='bold')
        # fig.savefig() сохраняет, понятное дело

        if edges_labels != list():
            # рисую значения весов на графе
            nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edges_labels, label_pos=0.4, font_size=15,
                                         bbox={'facecolor': '#ffffff', 'edgecolor': '#ffffff', 'alpha': 0.6,
                                               'pad': 0})  # label_pos = (0.5 * random.ranf() + 0.25)

        if file_name:
            fig.savefig(OUTPUT_PATH.format(file_name))
        if show:
            plt.show()
            plt.close()

    def draw_graph_with_paths(self, paths: PathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        '''
            Рисует граф, сохраняя граф в директорию /output
            '''
        # ---------------------DRAWING---------------------
        G = nx.DiGraph(self.graph.struct)  # создаю граф из образа graph
        figure_size = len(self.graph.struct.keys())

        fig = plt.figure(figsize=(int(13 * figure_size / 8), int(7 * figure_size / 8)),
                         dpi=100)  # для  сохранения картинки с помощью fig.savefig()

        paths_string = '{'

        L = len(paths) if len(paths) <= 10 else 10

        for i in range(0, L):
            if i != L - 1:
                paths_string += str(paths[i]) + ', ' + '\n' * (i % 2)
            else:
                paths_string += str(paths[i]) + '\n}'

        digraph_info = ('Paths: {0}\nReachability type: Standart digraph'.format(paths_string))

        ax = fig.add_subplot(111)  # добавляю текстовый бокс в окно
        ax.text(-0.14, 0.03 + 0.012 * len(paths), digraph_info, fontname='sans-serif', fontstyle='normal', fontsize=15,
                verticalalignment='top', horizontalalignment='left',
                transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5})  # pad - размер
        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        G.add_nodes_from(G.nodes, color='#949494')  # brcmyk - colors
        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(G, 'color')
        nodes = node_color_attr.keys()  # без list() работает в рисовалке
        nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        G.add_edges_from(G.edges, color='black', width=1)  # сначала добавляем все ребра черными

        dec_color = int('0x08e822', base=16)
        for p in paths:  # здесь добавляем все пути в виде последовательности ребер в объект графа
            path_edges = generate_path_edges(p)  # превращаю последовательность вершин в последовательность ребер
            hex_color = '#0' + hex(dec_color)[2:]
            if len(hex_color) > 7:
                hex_color = '#' + hex(dec_color)[2:]
            G.add_edges_from(path_edges, color=hex_color,
                             width=2.5)  # заново добавляю в граф списки ребер в путях другими цветами
            dec_color += 100 * random.randint(1, 500)  # новый цвет для каждого пути в формате #f032ae

        edge_color_attr = nx.get_edge_attributes(G, 'color')
        edge_width_attr = nx.get_edge_attributes(G, 'width')
        edges = edge_color_attr.keys()  # без list() работает в рисовалке
        edges_colors = edge_color_attr.values()  # без list() работает в рисовалке
        edges_widths = list(edge_width_attr.values())  # без list() не работает в рисовалке

        # создаю координаты вершин графа
        if ipos == 1:
            pos = generate_pos(self.graph.struct)
        elif ipos == 2:
            pos = nx.circular_layout(G)
        elif ipos == 3:
            pos = nx.random_layout(G)
        else:
            raise Exception(f'ipos parameter ({ipos}) is incorrect')

        # рисование
        nx.draw(G, pos=pos,
                edgelist=edges, edge_color=edges_colors, width=edges_widths,
                nodelist=nodes, node_color=nodes_colors, node_shape='s',
                node_size=400, font_size=16, font_family='sans-serif',
                with_labels=True, font_weight='bold')
        # fig.savefig() сохраняет, понятное дело

        if file_name:
            fig.savefig(OUTPUT_PATH.format(file_name))
        if show:
            plt.show()
            plt.close()


class VMRkDrawer(BaseDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self):
        ...


class MNRkDrawer(BaseDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self):
        ...


class BaseTelNetDrawer(BaseDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self):
        ...


class VMRkTelNetDrawer(BaseTelNetDrawer, VMRkDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self):
        ...


class MNRkTelNetDrawer(BaseTelNetDrawer, MNRkDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self):
        ...