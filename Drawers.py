import matplotlib.pyplot as plt
import networkx as nx
from numpy import random
# from random import randint
import os

class BaseDrawer():
    def __init__(self):
        ...

    def draw_graph(self):
        ...

    def draw_graph_with_paths(self):
        ...


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