from collections import Iterable
from typing import Tuple


def generate_pos(g: dict) -> dict:
    '''
    Создает позиции для вершин графа в виде вытянутого шестиугольнка
    '''
    positions = dict()
    V = list(g.keys())
    l_V = len(V)
    x = 0
    y = 3
    positions.update({V[0]: [x, y]})

    if (l_V % 2 != 0): # если количество вершин нечетно то:
        p = 1
    else:
        p = 0

    for i in range(1, l_V - p):
        X = x + ((i+1) // 2) - 0.2
        if (i % 2 == 1):
            if ((i+3) % 4 == 0):
                Y =  2 - ((i - (l_V - p) // 2) ** 2 - (l_V - p) ** 2 // 4 - 0.3) * 0.25 + 3 # или вместо 3 5*random.ranf() + 10
            else:
                Y =  2 - ((i - (l_V - p) // 2) ** 2 - (l_V - p) ** 2 // 4 - 0.3) * 0.25 - 3
        else:
            if (i % 4 == 0):
                Y =  -2 + ((i - (l_V - p) // 2) ** 2  - (l_V - p) ** 2 // 4) * 0.25 + 3
            else:
                Y =  -2 + ((i - (l_V - p) // 2) ** 2  - (l_V - p) ** 2 // 4) * 0.25 - 3 # умное распределние высот по параболе (бизигзапарабольное распределение)

        positions.update({V[i]: [X, Y]})


        # positions.update({V[i]: [x + ((i+1) // 2), y + ( (2) if (i % 2 == 1) else (-2)) ]}) # если i четный, то прибавляем -2, нечетный -- +2
        # positions.update({V[i]: [x + ((i+1) // 2), y + (   ( 2 - (abs(i - (l_V - p) // 2) - (l_V - p) // 2) * 0.25 ) if (i % 2 == 1)     else (-2 + (abs(i - (l_V - p) // 2) - (l_V - p) // 2) * 0.25 )   ) ]}) # умное распределние высот по графику модуля
    if (p == 1):
        positions.update({V[l_V-2]: [x + l_V // 2, y]})
        positions.update({V[l_V-1]: [x + l_V // 2 + 1, y]})
    else:
        positions.update({V[l_V-1]: [x + l_V // 2, y]})

    return positions

def generate_path_edges(p: list) -> list:
    '''
    Превращает список вершин в список ребер
    '''
    result = []
    for i in range(0,len(p)-1):
        result.append((p[i],p[i+1]))
    return result

def generate_separate_graph_and_weights(g: dict) -> Tuple[dict, dict]:
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
            edges_with_labels.update({(vi,vj) : str(g[vi][vj])})

        new_g.update({vi:neighbours})

    return((new_g, edges_with_labels))

def deweight(graph: dict) -> Iterable:
    """
    Превращает взвешенный граф в невзвешенный
    :param graph:
    :return:
    """
    for v in list(graph.keys()):
        graph[v] = list(graph[v].keys())
    return graph

def get_edges(graph: dict, weighted: bool):
    """
    Возвращает ребра графа
    :param graph:
    :param weighted:
    :return:
    """
    if not weighted:
        edges = []
        for vi in list(graph.keys()):  # иду по вершинам графа. vi - текушая вершина
            neighbours = []
            for vj in list(graph[vi].keys()):  # иду по соседям vi
                neighbours.append(vj)
                edges.append((vi, vj))
    else:
        edges = dict()
        for vi in list(graph.keys()):  # иду по вершинам графа. vi - текушая вершина
            neighbours = []
            for vj in list(graph[vi].keys()):  # иду по соседям vi
                neighbours.append(vj)
                edges.update({(vi, vj): float(graph[vi][vj])})
    return edges
