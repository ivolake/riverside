from itertools import chain
from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
from numpy import random
# from random import randint
# import os

from DrawersSupport import TextBoxParams, BaseDrawerConfig
import Graphs
from Paths import PathCollection
from config import OUTPUT_PATH
from additions import generate_separate_graph_and_weights, generate_pos, generate_path_edges


class BaseDrawer:
    def __init__(self, graph: 'Graphs.BaseGraph'):
    # def __init__(self, graph):
        self.graph = graph

        self.drawer_config = BaseDrawerConfig()

        self._paths = None
        self._tb_params = None


    @property
    def nodes_count(self):
        return len(self.graph.nodes)

    @property
    def figure_size(self) -> Tuple[int, int]:
        if self._paths is not None:
            return int(13 * self.nodes_count / 9), int(7 * self.nodes_count / 9)
        else:
            return int(13 * self.nodes_count / 11), int(7 * self.nodes_count / 11)

    @property
    def _nodes_colors(self):
        return nx.get_node_attributes(self.G, 'color')

    @property
    def _edges_colors(self):
        return nx.get_edge_attributes(self.G, 'color')

    @property
    def _edges_widths(self):
        return nx.get_edge_attributes(self.G, 'width')

    @property
    def edges_colors(self):
        return self._edges_colors.values()  # без list() работает в рисовалке

    @property
    def edges_widths(self):
        return list(self._edges_widths.values())  # без list() не работает в рисовалке



    def initial_configuring(self,
                            paths: PathCollection = None,
                            tb_params: dict = None,
                            **kwargs):
        """

        Parameters
        ----------
        paths - пути для вывода
        tb_params - словарь с ключами из наименований узлов-ведер
        **kwargs
         k - порядок путей на графе

        Returns
        -------

        """

        self._paths = paths
        self._tb_params = tb_params

        if 'k' in kwargs.keys():
            self._k = kwargs['k']

        if self.graph.weighted:
            (self.raw_graph, self.edges_labels) = generate_separate_graph_and_weights(self.graph.struct)  # превращаю взвешенный граф в невзвешенный
        else:
            (self.raw_graph, self.edges_labels) = self.graph.struct, None
        # читабельный для программы вид

        self.G = nx.DiGraph(self.raw_graph)
        self.fig = plt.figure(figsize=self.figure_size,
                         dpi=self.drawer_config.dpi)
        self.ax = self.fig.add_subplot(111)
        # Size in pixels = figsize * dpi

    def set_colors_to_nodes(self):
        self.G.add_nodes_from(self.G.nodes, color=self.drawer_config.standard_nodes_color)  # brcmyk - colors
        if hasattr(self.graph, 'inc_nodes'):
            self.G.add_nodes_from(self.graph.inc_nodes, color=self.drawer_config.inc_nodes_color)
        if hasattr(self.graph, 'dec_nodes'):
            self.G.add_nodes_from(self.graph.dec_nodes, color=self.drawer_config.dec_nodes_color)
        # G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
        # G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
        node_color_attr = nx.get_node_attributes(self.G, 'color')

        self.nodes = node_color_attr.keys()  # без list() работает в рисовалке
        self.nodes_colors = list(node_color_attr.values())  # без list() не работает в рисовалке

    def set_colors_to_edges(self):

        self.G.add_edges_from(self.G.edges, color=self.drawer_config.edge_neutral_color,
                              width=self.drawer_config.edge_neutral_width)  # добавляем все ребра черными
        # if self._paths and self._n > 0:
        #     dec_color = int(self.drawer_config.first_path_hex_color, base=16)  # из формата '0xffffff' в '#ffffff'
        #     for i, p in enumerate(self._paths):  # здесь добавляем все пути в виде последовательности ребер в объект графа
        #         if i < self._n:
        #             path_edges = generate_path_edges(p)  # превращаю последовательность вершин в последовательность ребер
        #             hex_color = '#0' + hex(dec_color)[2:]
        #             if len(hex_color) > 7:
        #                 hex_color = '#' + hex(dec_color)[2:]
        #             self.G.add_edges_from(path_edges, color=hex_color,
        #                              width=self.drawer_config.path_edges_width)  # заново добавляю в граф списки ребер в путях другими цветами
        #             dec_color += 100 * random.randint(1,500)  # новый цвет для каждого пути в формате #f032ae (десятичный вид
        #             # используется для обеспечения ротации цветов)

        if self._paths:
            dec_color = int(self.drawer_config.first_path_hex_color, base=16)  # из формата '0xffffff' в '#ffffff'
            for p in self._paths:  # здесь добавляем все пути в виде последовательности ребер в объект графа
                path_edges = generate_path_edges(p)  # превращаю последовательность вершин в последовательность ребер
                hex_color = '#0' + hex(dec_color)[2:]
                if len(hex_color) > 7:
                    hex_color = '#' + hex(dec_color)[2:]
                self.G.add_edges_from(path_edges, color=hex_color,
                                 width=self.drawer_config.path_edges_width)  # заново добавляю в граф списки ребер в путях другими цветами
                dec_color += 100 * random.randint(1,500)  # новый цвет для каждого пути в формате #f032ae (десятичный вид
                # используется для обеспечения ротации цветов)

    def set_pos(self, ipos: int):
        if ipos == 1:
            self.pos = generate_pos(self.raw_graph)
        elif ipos == 2:
            self.pos = nx.circular_layout(self.G)
        elif ipos == 3:
            self.pos = nx.random_layout(self.G)
        else:
            raise Exception(f'ipos parameter (ipos={ipos}) is incorrect')

    def add_text_box(self):
        graph_info = {
            'graph_type': self.graph.type
        }

        if self.graph.type in ['vmrk', 'vmrk_telnet']:
            graph_info.update({'k_min': self._paths.get_path_of_smallest_magnitude().i})
        elif self.graph.type in ['mnrk', 'mnrk_telnet']:
            graph_info.update({'k': self._k})
        else:
            pass

        text_box_params = TextBoxParams(paths=self._paths,
                                        graph_info=graph_info)

        self.ax.text(text_box_params.x, text_box_params.y, text_box_params.digraph_info,
                fontname=self.drawer_config.font_family,
                fontstyle=text_box_params.fontstyle, fontsize=text_box_params.fontsize,
                verticalalignment=text_box_params.vertical_alignment,
                horizontalalignment=text_box_params.horizontal_alignment,
                transform=self.ax.transAxes, bbox=text_box_params.bbox)  # pad - размер

    def _draw(self):
        # nx.draw(self.G, pos=self.pos,
        #         edgelist=self.edges, edge_color=self.edges_colors, width=self.edges_widths,
        #         nodelist=self.nodes, node_color=self.nodes_colors, node_shape=self.drawer_config.node_shape,
        #         node_size=self.plane_graph_params.node_size, font_size=self.plane_graph_params.node_font_size,
        #         font_family=self.drawer_config.font_family, with_labels=True,
        #         font_weight=self.drawer_config.font_weight)

        # Убирание границ
        for spine in self.ax.spines:
            self.ax.spines[spine].set_visible(False)

        if self._tb_params:
            base_nodes = list(set(self.nodes) - set(self._tb_params.keys()))
            base_nodes_colors = [self._nodes_colors[nid] for nid in base_nodes]

            tb_nodes = list(self._tb_params.keys())
            tb_nodes_colors = [self._nodes_colors[nid] for nid in tb_nodes]

            nx.draw_networkx_nodes(
                G=self.G, pos=self.pos, nodelist=base_nodes, node_size=self.drawer_config.node_size_default,
                node_color=base_nodes_colors, node_shape=self.drawer_config.node_shape_default,
                linewidths=self.drawer_config.node_borders_width, edgecolors=self.drawer_config.node_borders_color,
                ax=self.ax, alpha=1, cmap=None, vmin=None, vmax=None, label=None)

            nx.draw_networkx_nodes(
                G=self.G, pos=self.pos, nodelist=tb_nodes, node_size=self.drawer_config.node_size_tb,
                node_color=tb_nodes_colors, node_shape=self.drawer_config.node_shape_tb,
                linewidths=self.drawer_config.node_borders_width, edgecolors=self.drawer_config.node_borders_color,
                ax=self.ax, alpha=1, cmap=None, vmin=None, vmax=None, label=None)
        else:
            nx.draw_networkx_nodes(
                G=self.G, pos=self.pos, nodelist=self.nodes, node_size=self.drawer_config.node_size_default,
                node_color=self.nodes_colors, node_shape=self.drawer_config.node_shape_default,
                linewidths=self.drawer_config.node_borders_width, edgecolors=self.drawer_config.node_borders_color,
                ax=self.ax, alpha=1, cmap=None, vmin=None, vmax=None, label=None)

        if self._paths:

            paths_edges = list(chain.from_iterable(list(map(generate_path_edges, self._paths))))
            paths_edges_colors = [self._edges_colors[pe] for pe in paths_edges]
            paths_edges_widths = [self._edges_widths[pe] for pe in paths_edges]

            edges_without_paths_edges = list(set(list(self.graph.edges)) - set(paths_edges))
            edges_without_paths_edges_colors = [self._edges_colors[pe] for pe in edges_without_paths_edges]
            edges_without_paths_edges_widths = [self._edges_widths[pe] for pe in edges_without_paths_edges]

            nx.draw_networkx_edges(
                G=self.G, pos=self.pos, edgelist=edges_without_paths_edges,
                width=edges_without_paths_edges_widths, edge_color=edges_without_paths_edges_colors,
                style=self.drawer_config.edge_style, arrowstyle=self.drawer_config.arrowstyle,
                arrowsize=self.drawer_config.arrowsize, arrows=self.drawer_config.arrows,
                connectionstyle=self.drawer_config.connectionstyle,
                min_source_margin=self.drawer_config.min_source_marg,
                min_target_margin=self.drawer_config.min_target_marg,
                ax=self.ax, alpha=0.7, edge_cmap=None, edge_vmin=None, edge_vmax=None, label=None)

            nx.draw_networkx_edges(
                G=self.G, pos=self.pos, edgelist=paths_edges,
                width=paths_edges_widths, edge_color=paths_edges_colors,
                style=self.drawer_config.edge_style, arrowstyle=self.drawer_config.arrowstyle,
                arrowsize=self.drawer_config.arrowsize, arrows=self.drawer_config.arrows,
                connectionstyle=self.drawer_config.connectionstyle,
                min_source_margin=self.drawer_config.min_source_marg,
                min_target_margin=self.drawer_config.min_target_marg,
                ax=self.ax, alpha=0.7, edge_cmap=None, edge_vmin=None, edge_vmax=None, label=None)
        else:
            nx.draw_networkx_edges(
                G=self.G, pos=self.pos, edgelist=self.graph.edges, width=self.edges_widths, edge_color=self.edges_colors,
                style=self.drawer_config.edge_style, arrowstyle=self.drawer_config.arrowstyle,
                arrowsize=self.drawer_config.arrowsize, arrows=self.drawer_config.arrows,
                connectionstyle=self.drawer_config.connectionstyle,
                min_source_margin=self.drawer_config.min_source_marg,
                min_target_margin=self.drawer_config.min_target_marg,
                ax=self.ax, alpha=1, edge_cmap=None, edge_vmin=None, edge_vmax=None, label=None)

        nx.draw_networkx_labels(
            G=self.G, pos=self.pos, font_size=self.drawer_config.node_font_size,
            font_color=self.drawer_config.font_color, font_family=self.drawer_config.font_family,
            font_weight=self.drawer_config.font_weight, bbox=self.drawer_config.node_label_bbox,
            horizontalalignment=self.drawer_config.node_label_horizontalalignment,
            verticalalignment=self.drawer_config.node_label_verticalalignment,
            ax=self.ax, alpha=None, labels=None)

        if self.graph.weighted and self.edges_labels is not None:
            # рисую значения весов на графе
            nx.draw_networkx_edge_labels(self.G, pos=self.pos, edge_labels=self.edges_labels,
                                         label_pos=self.drawer_config.weights_label_pos,
                                         font_size=self.drawer_config.weights_font_size,
                                         bbox=self.drawer_config.edge_label_bbox)

    def save_or_show(self, file_name, show):
        if file_name:
            self.fig.savefig(OUTPUT_PATH.format(file_name))
        if show:
            plt.show()
            plt.close()

    def draw_graph(self,
                   file_name: str = None,
                   ipos: int = 1,
                   show: bool = True):
        """
        Рисует граф без путей, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------

        # Определение переменной графа в терминах networkx и прочее
        self.initial_configuring()

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        self.set_colors_to_nodes()

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        self.set_colors_to_edges()

        # создаю координаты вершин графа
        self.set_pos(ipos)

        # рисование
        self._draw()

        self.save_or_show(file_name, show)

    def draw_graph_with_paths(self,
                              paths: PathCollection,
                              file_name: str = None,
                              ipos: int = 1,
                              show: bool = True,
                              **kwargs):
        """
            Рисует граф, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------
        self.initial_configuring(paths=paths, **kwargs)

        self.add_text_box()

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        self.set_colors_to_nodes()

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        self.set_colors_to_edges()

        # создаю координаты вершин графа
        self.set_pos(ipos=ipos)

        # рисование
        self._draw()

        self.save_or_show(file_name, show)


    def draw_graph_with_tb_nodes(self,
                                 tb_params: dict,
                                 file_name: str = None,
                                 ipos: int = 1,
                                 show: bool = True,
                                 **kwargs):
        """
        Рисует граф без путей, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------

        # Определение переменной графа в терминах networkx и прочее
        self.initial_configuring(tb_params=tb_params, **kwargs)

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        self.set_colors_to_nodes()

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        self.set_colors_to_edges()

        # создаю координаты вершин графа
        self.set_pos(ipos)

        # рисование
        self._draw()

        self.save_or_show(file_name, show)


    def draw_graph_with_tb_nodes_and_paths(self,
                                          paths: PathCollection,
                                          tb_params: dict,
                                          file_name: str = None,
                                          ipos: int = 1,
                                          show: bool = True,
                                          **kwargs):
        """
            Рисует граф, сохраняя граф в директорию /output
        """
        # ---------------------DRAWING---------------------
        self.initial_configuring(paths=paths, tb_params=tb_params, **kwargs)

        self.add_text_box()

        # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
        self.set_colors_to_nodes()

        # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
        self.set_colors_to_edges()

        # создаю координаты вершин графа
        self.set_pos(ipos=ipos)

        # рисование
        self._draw()

        self.save_or_show(file_name, show)