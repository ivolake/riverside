from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
from numpy import random
# from random import randint
import os

from DrawersSupport import PlaneGraphParams, TextBoxParams
from Graphs import BaseGraph
from Paths import PathCollection, MPathCollection
from config import OUTPUT_PATH
from functions import generate_separate_graph_and_weights, generate_pos, generate_path_edges



class BaseDrawer():
    def __init__(self, graph: BaseGraph, inc_nodes: list = None, dec_nodes: list = None):
        self.graph = graph

        if inc_nodes is None:
            self.inc_nodes = inc_nodes

        if dec_nodes is not None:
            self.dec_nodes = dec_nodes

        self.dpi = 100

        self.plane_graph_params = PlaneGraphParams(nodes_count=self.nodes_count)

        self.standard_nodes_color = '#949494'
        self.inc_nodes_color = '#5dff4f'
        self.dec_nodes_color = '#fc2a2a'

        self.edges_neutral_color = 'black'
        self.edges_neutral_width = 1

        self.edges_label_bbox = {
            'facecolor': '#ffffff',
            'edgecolor': '#ffffff',
            'alpha': 0.6,
            'pad': 0}

        self.weights_label_pos = 0.4 # или (0.5 * random.ranf() + 0.25)
        self.weights_font_size = 15

        self.node_shape = 's'
        self.node_size = 400
        self.node_font_size = 16
        self.node_neutral_color = '#949494'

        self.font_family = 'sans-serif'
        self.font_weight = 'bold'

        self.first_path_hex_color = '0x08e822'
        self.path_edges_width = 2.5


    @property
    def nodes_count(self):
        return len(self.graph.nodes)

    @property
    def figure_size(self) -> Tuple[int, int]:
        return (int(13 * self.nodes_count / 8), int(7 * self.nodes_count / 8))

    def draw_graph(self, file_name: str = None, ipos: int = 0, show: bool = True):
        """
        Рисует граф без путей, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------

        # TODO:
        #  Переделать большую draw_graph в множество функций, чтобы исключить многократное повторение кода

        (raw_graph, edges_labels) = generate_separate_graph_and_weights(self.graph.struct)  # превращаю взвешенный граф в
        # читабельный для программы вид

        G = nx.DiGraph(raw_graph)  # создаю граф из образа digraph
        fig = plt.figure(figsize=self.plane_graph_params.figure_size, # здесь деление на 11, а не на 8, как в осталных
                         dpi=self.dpi)  # для  сохранения картинки с помощью fig.savefig()
        # Size in pixels = figsize * dpi

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        G.add_nodes_from(G.nodes, color=self.standard_nodes_color)  # brcmyk - colors
        G.add_nodes_from(self.inc_nodes, color=self.inc_nodes_color)
        G.add_nodes_from(self.dec_nodes, color=self.dec_nodes_color)
        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(G, 'color')
        nodes = node_color_attr.keys()  # без list() работает в рисовалке
        nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        G.add_edges_from(G.edges, color=self.edges_neutral_color, width=self.edges_neutral_width)  # добавляем все ребра черными

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
                nodelist=nodes, node_color=nodes_colors, node_shape=self.node_shape,
                node_size=self.plane_graph_params.node_size, font_size=self.plane_graph_params.node_font_size,
                font_family=self.font_family, with_labels=True, font_weight=self.font_weight)
        # fig.savefig() сохраняет, понятное дело

        if edges_labels:
            # рисую значения весов на графе
            nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edges_labels, label_pos=self.weights_label_pos,
                                         font_size=self.weights_font_size, bbox=self.edges_label_bbox)

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
        fig = plt.figure(figsize=self.figure_size,
                         dpi=100)  # для  сохранения картинки с помощью fig.savefig()



        ax = fig.add_subplot(111)  # добавляю текстовый бокс в окно

        text_box_params = TextBoxParams(paths=paths, graph_info={
            'graph_type': self.graph.type
        })

        ax.text(text_box_params.x, text_box_params.y, text_box_params.digraph_info, fontname=self.font_family,
                fontstyle=text_box_params.fontstyle, fontsize=text_box_params.fontsize,
                verticalalignment=text_box_params.vertical_alignment,
                horizontalalignment=text_box_params.horizontal_alignment,
                transform=ax.transAxes, bbox=text_box_params.bbox)  # pad - размер

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        G.add_nodes_from(G.nodes, color=self.node_neutral_color)  # brcmyk - colors
        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(G, 'color')
        nodes = node_color_attr.keys()  # без list() работает в рисовалке
        nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        G.add_edges_from(G.edges, color=self.edges_neutral_color, width=self.edges_neutral_width)  # сначала добавляем все ребра черными

        dec_color = int(self.first_path_hex_color, base=16) # из формата '0xffffff' в '#ffffff'
        for p in paths:  # здесь добавляем все пути в виде последовательности ребер в объект графа
            path_edges = generate_path_edges(p)  # превращаю последовательность вершин в последовательность ребер
            hex_color = '#0' + hex(dec_color)[2:]
            if len(hex_color) > 7:
                hex_color = '#' + hex(dec_color)[2:]
            G.add_edges_from(path_edges, color=hex_color,
                             width=self.path_edges_width)  # заново добавляю в граф списки ребер в путях другими цветами
            dec_color += 100 * random.randint(1, 500)  # новый цвет для каждого пути в формате #f032ae (десятичный вид
                                                       # используется для обеспечения ротации цветов)

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
                nodelist=nodes, node_color=nodes_colors, node_shape=self.node_shape,
                node_size=self.node_size, font_size=self.node_font_size,
                font_family=self.font_family, with_labels=True, font_weight=self.font_weight)
        # fig.savefig() сохраняет, понятное дело

        if file_name:
            fig.savefig(OUTPUT_PATH.format(file_name))
        if show:
            plt.show()
            plt.close()


class VMRkDrawer(BaseDrawer):
    def __init__(self, graph: BaseGraph, inc_nodes: list = None):
        if inc_nodes is None:
            inc_nodes = []

        BaseDrawer.__init__(self, graph, inc_nodes)

    def draw_graph_with_paths(self, paths: MPathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        G = nx.DiGraph(self.graph.struct)  # создаю граф из образа graph
        fig = plt.figure(figsize=self.figure_size,
                         dpi=self.dpi)  # для  сохранения картинки с помощью fig.savefig()

        text_box_params = TextBoxParams(paths=paths, graph_info={
            'graph_type': self.graph.type,
            'k': self.graph.calc_request.get('k')
        })
        ax = fig.add_subplot(111)  # добавляю текстовый бокс в окно
        ax.text(text_box_params.x, text_box_params.y, text_box_params.digraph_info, fontname=self.font_family,
                fontstyle=text_box_params.fontstyle, fontsize=text_box_params.fontsize,
                verticalalignment=text_box_params.vertical_alignment,
                horizontalalignment=text_box_params.horizontal_alignment,
                transform=ax.transAxes, bbox=text_box_params.bbox)  # pad - размер

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        G.add_nodes_from(G.nodes, color=self.node_neutral_color)  # brcmyk - colors
        G.add_nodes_from(self.inc_nodes, color=self.inc_nodes_color)

        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(G, 'color')
        nodes = node_color_attr.keys()  # без list() работает в рисовалке
        nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        G.add_edges_from(G.edges, color=self.edges_neutral_color, width=self.edges_neutral_width)  # сначала добавляем все ребра черными
        dec_color = int(self.first_path_hex_color, base=16)  # началный цвет для добавочных ребер
        for p in paths:  # здесь добавляем все пути в виде последовательности ребер в объект графа
            path_edges = generate_path_edges(p)  # превращаю последовательность вершин в последовательность ребер
            hex_color = '#0' + hex(dec_color)[2:]
            if len(hex_color) > 7:
                hex_color = '#' + hex(dec_color)[2:]
            G.add_edges_from(path_edges, color=hex_color,
                             width=self.path_edges_width)  # заново добавляю в граф списки ребер в путях другими цветами
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
                nodelist=nodes, node_color=nodes_colors, node_shape=self.node_shape,
                node_size=self.node_size, font_size=self.node_font_size, font_family=self.font_family,
                with_labels=True, font_weight=self.font_weight)

        # fig.savefig() сохраняет, понятное дело

        if file_name:
            fig.savefig(OUTPUT_PATH.format(file_name))
        if show:
            plt.show()
            plt.close()


class MNRkDrawer(BaseDrawer):
    def __init__(self, graph: BaseGraph, inc_nodes: list = None, dec_nodes: list = None):
        if inc_nodes is None:
            inc_nodes = []
        if dec_nodes is None:
            dec_nodes = []

        BaseDrawer.__init__(self, graph, inc_nodes, dec_nodes)

    def draw_graph_with_paths(self, paths: PathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        ...


class BaseTelNetDrawer(BaseDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self, paths: PathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        ...


class VMRkTelNetDrawer(BaseTelNetDrawer, VMRkDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self, paths: PathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        ...


class MNRkTelNetDrawer(BaseTelNetDrawer, MNRkDrawer):
    def __init__(self):
        ...

    def draw_graph_with_paths(self, paths: PathCollection, file_name: str = None, ipos: int = 0, show: bool = True):
        ...