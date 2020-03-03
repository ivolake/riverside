from collections import Iterable

from Graph import BaseGraph, VMRkGraph, MNRkGraph

def get_graph(config: dict) -> BaseGraph:
    graph_type = config.get('type')
    if graph_type == 'simple':
        return BaseGraph(config)
    elif graph_type == 'vmrk':
        return VMRkGraph(config)
    elif graph_type == 'mnrk':
        return MNRkGraph(config)
    elif graph_type == 'telnet':
        pass
    elif graph_type == 'vmrk_telnet':
        pass
    elif graph_type == 'mnrk_telnet':
        pass
    elif graph_type == 'vmrk_tb_telnet':
        pass
    elif graph_type == 'mnrk_tb_telnet':
        pass
    else:
        raise Exception('Wrong graph type declared in config')

def generate_separate_graph_and_weights(g: dict) -> (dict, dict):
    '''
    Функция для взвешенных графов, которая рабивает такой граф на невзвешенный граф и словарь с ребрами и их весами
    Пример:
        Входные данные:

        g = {'1': {'2':45, '3':40},
             '2': {'4':15, '9':35},
             '3': {'5':45},
             '4': {'6':20},
             '5': {'6':10, '7':25},
             '6': {'8':40},
             '7': {'9':30},
             '8': {'3':50, '7':35, '10':5},
             '9': {'10':25},
             '10':{}}

        Выходные данные:

        (new_g, edges_with_labels)
        new_g = {'1': ['2', '3'],
                 '2': ['4', '9'],
                 '3': ['5'],
                 '4': ['6'],
                 '5': ['6', '7'],
                 '6': ['8'],
                 '7': ['9'],
                 '8': ['3', '7', '10'],
                 '9': ['10'],
                 '10': []}

        edges_with_labels = {('1', '2'): '45',
                             ('1', '3'): '40',
                             ('2', '4'): '15',
                             ('2', '9'): '35',
                             ('3', '5'): '45',
                             ('4', '6'): '20',
                             ('5', '6'): '10',
                             ('5', '7'): '25',
                             ('6', '8'): '40',
                             ('7', '9'): '30',
                             ('8', '3'): '50',
                             ('8', '7'): '35',
                             ('8', '10'): '5',
                             ('9', '10'): '25'}

    '''

    new_g = dict()                         # новый граф без весов в стандартном виде
    edges_with_labels = dict()             # отдельный словарь для весов {('1','2') : weight1, ('3','4') : weight2}
    for vi in list(g.keys()):              # иду по вершинам графа. vi - текушая вершина
        neighbours = []
        for vj in list(g[vi].keys()):      # иду по соседям vi
            neighbours.append(vj)
            edges_with_labels.update({(vi, vj): str(g[vi][vj])})

        new_g.update({vi: neighbours})

    return new_g, edges_with_labels

def deweight(edges: dict) -> Iterable:
    result = []
    for edge in edges:
        result.append(edge)
    return result
