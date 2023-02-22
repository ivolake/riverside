import json
import math
import random
import string
from typing import Tuple, List, Iterable
import operator as op


class FineDict(dict):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return json.dumps(self, indent=4)


class Representation:
    def __init__(self, representing_obj, representing_fields: List = None):
        self.representing_obj = representing_obj

        if representing_fields is not None:
            self.representing_fields = representing_fields
        else:
            self.representing_fields = self.representing_obj.__dict__

    def __call__(self):
        representing_fields_str = []
        for f in self.representing_fields:
            representing_fields_str.append(f'{f}={op.attrgetter(f)(self.representing_obj)}')

        return f'{self.representing_obj.__class__.__name__}({", ".join(representing_fields_str)})'


def generate_pos(g: dict) -> dict:
    """
    Задает позиции для вершин графа осциллирующими около двух парабол, сложенных овалом
    """
    positions = dict()
    V = list(g.keys())
    l_V = len(V)
    x = 0
    y = 3
    positions.update({V[0]: [x, y]})

    if (l_V % 2 != 0):  # если количество вершин нечетно то:
        p = 1
    else:
        p = 0

    for i in range(1, l_V - p):
        X = x + ((i + 1) // 2) - 0.2
        if (i % 2 == 1):
            if ((i + 3) % 4 == 0):
                Y = 2 - ((i - (l_V - p) // 2) ** 2 - (
                            l_V - p) ** 2 // 4 - 0.3) * 0.25 + 3  # или вместо 3 5*random.ranf() + 10
            else:
                Y = 2 - ((i - (l_V - p) // 2) ** 2 - (l_V - p) ** 2 // 4 - 0.3) * 0.25 - 3
        else:
            if (i % 4 == 0):
                Y = -2 + ((i - (l_V - p) // 2) ** 2 - (l_V - p) ** 2 // 4) * 0.25 + 3
            else:
                Y = -2 + ((i - (l_V - p) // 2) ** 2 - (
                            l_V - p) ** 2 // 4) * 0.25 - 3  # умное распределние высот по параболе (бизигзапарабольное распределение)

        positions.update({V[i]: [X, Y]})

        # positions.update({V[i]: [x + ((i+1) // 2), y + ( (2) if (i % 2 == 1) else (-2)) ]}) # если i четный, то прибавляем -2, нечетный -- +2
        # positions.update({V[i]: [x + ((i+1) // 2), y + (   ( 2 - (abs(i - (l_V - p) // 2) - (l_V - p) // 2) * 0.25 ) if (i % 2 == 1)     else (-2 + (abs(i - (l_V - p) // 2) - (l_V - p) // 2) * 0.25 )   ) ]}) # умное распределние высот по графику модуля
    if (p == 1):
        positions.update({V[l_V - 2]: [x + l_V // 2, y]})
        positions.update({V[l_V - 1]: [x + l_V // 2 + 1, y]})
    else:
        positions.update({V[l_V - 1]: [x + l_V // 2, y]})

    return positions


def generate_path_edges(p: list) -> list:
    """
    Превращает список вершин в список ребер
    """
    result = []
    for i in range(0, len(p) - 1):
        result.append((p[i], p[i + 1]))
    return result


def generate_separate_graph_and_weights(g: dict) -> Tuple[dict, dict]:
    """
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

    """

    new_g = dict()  # новый граф без весов в стандартном виде
    edges_with_labels = dict()  # отдельный словарь для весов {('1','2') : weight1, ('3','4') : weight2}
    for vi in list(g.keys()):  # иду по вершинам графа. vi - текушая вершина
        neighbours = []
        for vj in list(g[vi].keys()):  # иду по соседям vi
            neighbours.append(vj)
            edges_with_labels.update({(vi, vj): str(g[vi][vj])})

        new_g.update({vi: neighbours})

    return new_g, edges_with_labels


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
        for vi in graph.keys():  # иду по вершинам графа. vi - текушая вершина
            neighbours = []
            for vj in graph[vi]:  # иду по соседям vi
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


def damerau_levenshtein_distance(s1, s2):
    """
    Смысл: сколько операций добавления, удаления, перестановки или подстановки символов нужно совершить, чтобы строки стали равны
    """
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition
    return d[lenstr1 - 1, lenstr2 - 1]

def huffman_distance(s1, s2):
    """
    Смысл: сколько операций добавления или удаления символа нужно совершить, чтобы строки стали равны
    """
    s1, s2 = sorted((s1, s2), key=len)
    d = 0
    for i in range(0, len(s1)):
        if s1[i] != s2[i]:
            d += 1
    return d


def ID_random_insertion(info):
    """
    ID - Information Distortion
    Операция по случайной вставке
    Parameters
    ----------
    info

    Returns
    -------

    """
    i = random.randint(0, len(info))
    return info[0:i] + random.choice(string.printable[:-2]) + info[i:]


def ID_random_deletion(info):
    """
    ID - Information Distortion
    Операция по случайному удалению
    Parameters
    ----------
    info

    Returns
    -------

    """
    i = random.randint(0, len(info))
    return info[0:i] + info[i + 1:]


def ID_random_substitution(info):
    """
    ID - Information Distortion
    Операция по случайной замене
    Parameters
    ----------
    info

    Returns
    -------

    """
    i = random.randint(0, len(info))
    return info[0:i] + random.choice(string.printable[:-2]) + info[i + 1:]

def information_distortion(info: str, dist_level: int = 1):
    distorted = info
    for i in range(0, random.randint(0, dist_level)):
        distorted = random.choice([ID_random_insertion,
                                   ID_random_deletion,
                                   ID_random_substitution])(distorted)
    return distorted

def get_vals_from_inherited_keys(d, key):
    """
    Parameters
    ----------
    d - dict
    keys - keys in format "key" or "key1.key2"

    Returns
    -------
    values
    """

    value = ''
    key_list = key.split('.')
    inner_d = d
    if len(key_list) > 1:
        for i in range(0, len(key_list) - 1):
            inner_d = inner_d[key_list[i]]
            if isinstance(inner_d, list):
                value = int(inner_d[key_list[i + 1]])
            elif isinstance(inner_d, dict):
                value = inner_d[key_list[i + 1]]
            else:
                value = inner_d
    else:
        value = inner_d[key_list[0]]

    return value

def set_vals_from_inherited_keys(d, key, value):
    """
    Parameters
    ----------
    d - dict
    keys - keys in format "key" or "key1.key2"
    value - value to set

    Returns
    -------
    values
    """
    new_d = d
    key_list = key.split('.')
    attrs = '"]["'.join(key_list)
    exec('new_d["%s"] = %s' % (attrs, value))
    return new_d

def filled_space_factor_formulae(n: float,
                                 params: dict):
    filled_space_factor_low = params['filled_space_factor_low']
    filled_space_factor_high = params['filled_space_factor_high']
    filled_space_factor_plateau = params['filled_space_factor_plateau']
    """
    Функция расчета коэффициента замедления работы узла 
    вследствие его нагрузки
    """

    if n == 0:
        factor = 1
    else:
        factor = 1 - math.exp(n - 1 / n) * (filled_space_factor_high - filled_space_factor_low)
        factor = factor if factor > filled_space_factor_plateau else filled_space_factor_plateau
    return round(factor, 4)
