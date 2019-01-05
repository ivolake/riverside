import matplotlib.pyplot as plt
import networkx as nx
from numpy import abs
from numpy import random # from random import randint
import os

def show_dict(d):
    if type(d) == type(dict()):
        print('{ ')
        for v in d.keys():
            print('{0} : {1}, '.format(v, d[v]))
        print(' }')
    elif type(d) == type(list()):
        print('[')
        for v in d:
            print(v, end = '')
            print(',  ')
        print(']')
    elif type(d) == type(tuple):
        print('(')
        for v in d:
            print(v, end = '')
            print(',  ')
        print(')')
    else:
        print(d)


def generate_pos(g):
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

def generate_path_edges(p):
    '''
    Превращает список вершин в список ребер
    '''
    result = []
    for i in range(0,len(p)-1):
        result.append((p[i],p[i+1]))
    return result

def generate_separate_graph_and_weights(g):
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


def draw_graph0(digraph, digraph_name, paths, ipos): # Standart reachability in digraph
    '''
    Рисует граф, сохраняя граф в директорию /output
    '''
    # ---------------------DRAWING---------------------
    G = nx.DiGraph(digraph) # создаю граф из образа graph
    figure_size = len(digraph.keys())
    fig = plt.figure(figsize = (int(13 * figure_size / 8), int(7 * figure_size / 8)), dpi = 100) # для  сохранения картинки с помощью fig.savefig()

    digraph_info = ('Paths: {0}\nReachability type:Standart digraph'.format(paths))

    ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
    ax.text(-0.14,0.02,digraph_info,fontname = 'sans-serif', fontstyle='normal',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5})

    # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
    G.add_nodes_from(G.nodes, color = '#949494') # brcmyk - colors
    #G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
    #G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
    node_color_attr = nx.get_node_attributes(G,'color')
    nodes  = node_color_attr.keys() # без list() работает в рисовалке
    nodes_colors = list(node_color_attr.values()) # без list() не работает в рисовалке

    # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
    G.add_edges_from(G.edges,color = 'black', width = 1) # сначала добавляем все ребра черными

    colooor = int('0x08e822',base = 16)
    for p in paths: # здесь добавляем все пути в виде последовательности ребер в объект графа
        path_edges = generate_path_edges(p) # превращаю последовательность вершин в последовательность ребер
        G.add_edges_from(path_edges, color='#0' +  hex(colooor)[2:], width = 2.5) # заново добавляю в граф списки ребер в путях другими цветами
        colooor += 100 * random.randint(1,500) # новый цвет для каждого пути в формате #f032ae


    edge_color_attr = nx.get_edge_attributes(G,'color')
    edge_width_attr = nx.get_edge_attributes(G,'width')
    edges = edge_color_attr.keys() # без list() работает в рисовалке
    edges_colors = edge_color_attr.values() # без list() работает в рисовалке
    edges_widths = list(edge_width_attr.values()) # без list() не работает в рисовалке

    # создаю координаты вершин графа
    if ipos == 1:
        pos = generate_pos(digraph)
    elif ipos == 2:
        pos = nx.circular_layout(G)
    elif ipos == 3:
        pos = nx.random_layout(G)

    # рисование
    nx.draw(G, pos = pos,
            edgelist=edges, edge_color=edges_colors, width = edges_widths,
            nodelist = nodes, node_color = nodes_colors, node_shape = 's',
            font_family = 'sans-serif', with_labels = True, font_weight = 'bold')
    # fig.savefig() сохраняет, понятное дело

    fig.savefig(os.getcwd() + '/output/{}.png'.format(digraph_name))
    plt.show()

def draw_graph1(digraph, digraph_name, inc_nodes, k, paths, ipos): # Vertrex Mixed Reachability with degree of k
    '''
    Рисует граф, сохраняя граф в директорию /output
    '''
    # ---------------------DRAWING---------------------
    G = nx.DiGraph(digraph) # создаю граф из образа graph
    figure_size = len(digraph.keys())
    fig = plt.figure(figsize = (int(13 * figure_size / 8), int(7 * figure_size / 8)), dpi = 100) # для  сохранения картинки с помощью fig.savefig()

    paths_string = '{'
    for i in range(0, len(paths)-1):
        if i != len(paths)-1:
            paths_string += str(paths[i]) + ',\n'
        else:
            paths_string += str(paths[i]) + '\n}'

    digraph_info = ('Paths: {0}\nReachability type: VMR of k degree\nk = {1}'.format(paths_string,k))

    ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
    ax.text(-0.14, 0.05 + 0.01 * len(paths), digraph_info, fontname = 'sans-serif', fontstyle='normal',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5}) # pad - размер

    # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
    G.add_nodes_from(G.nodes, color = '#949494') # brcmyk - colors
    G.add_nodes_from(inc_nodes, color = '#636363')
    #G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
    #G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
    node_color_attr = nx.get_node_attributes(G,'color')
    nodes  = node_color_attr.keys() # без list() работает в рисовалке
    nodes_colors = list(node_color_attr.values()) # без list() не работает в рисовалке

    # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
    G.add_edges_from(G.edges,color = 'black', width = 1) # сначала добавляем все ребра черными
    colooor = int('0x08e822',base = 16) # началный цвет для добавочных ребер
    for p in paths: # здесь добавляем все пути в виде последовательности ребер в объект графа
        path_edges = generate_path_edges(p) # превращаю последовательность вершин в последовательность ребер
        hexcolooor = '#0' +  hex(colooor)[2:]
        G.add_edges_from(path_edges, color = hexcolooor, width = 2.5) # заново добавляю в граф списки ребер в путях другими цветами
        colooor += 100 * random.randint(1,500) # новый цвет для каждого пути в формате #f032ae
        if len(hexcolooor) > 7:
            hexcolooor = '#' + hex(colooor)[2:]


    edge_color_attr = nx.get_edge_attributes(G,'color')
    edge_width_attr = nx.get_edge_attributes(G,'width')
    edges = edge_color_attr.keys() # без list() работает в рисовалке
    edges_colors = edge_color_attr.values() # без list() работает в рисовалке
    edges_widths = list(edge_width_attr.values()) # без list() не работает в рисовалке

    # создаю координаты вершин графа
    if ipos == 1:
        pos = generate_pos(digraph)
    elif ipos == 2:
        pos = nx.circular_layout(G)
    elif ipos == 3:
        pos = nx.random_layout(G)

    # рисование
    nx.draw(G, pos = pos,
            edgelist=edges, edge_color=edges_colors, width = edges_widths,
            nodelist = nodes, node_color = nodes_colors, node_shape = 's',
            font_family = 'sans-serif', with_labels = True, font_weight = 'bold')

    # fig.savefig() сохраняет, понятное дело

    fig.savefig(os.getcwd() + '/output/{}.png'.format(digraph_name))
    plt.show()
    plt.close()

def draw_graph2(digraph, digraph_name, inc_nodes, k, path, time, mass, ipos): # VMRk with weights and masses
    '''
    Рисует граф, сохраняя граф в директорию /output
    '''
    # ---------------------DRAWING---------------------
    (new_digraph, edges_labels) = generate_separate_graph_and_weights(digraph) # превращаю взвешенный граф в читабельный для программы вид

    G = nx.DiGraph(new_digraph) # создаю граф из образа new_graph
    figure_size = len(digraph.keys())
    fig = plt.figure(figsize = (int(13 * figure_size / 8), int(7 * figure_size / 8)), dpi = 100) # для  сохранения картинки с помощью fig.savefig()

    digraph_info = ('Path: {0}\nTime: {1} s\nMass: {2} mbytes\nReachability type: VMR of k degree\nk = {3}'.format(path, time, mass ,k))

    ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
    ax.text(-0.14,0.02,digraph_info,fontname = 'sans-serif', fontstyle='normal',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5}) # pad - размер

    # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
    G.add_nodes_from(G.nodes, color = '#949494') # brcmyk - colors
    G.add_nodes_from(inc_nodes, color = '#636363')
    #G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
    #G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
    node_color_attr = nx.get_node_attributes(G,'color')
    nodes  = node_color_attr.keys() # без list() работает в рисовалке
    nodes_colors = list(node_color_attr.values()) # без list() не работает в рисовалке

    # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
    G.add_edges_from(G.edges,color = 'black', width = 1) # сначала добавляем все ребра черными
    path_edges = generate_path_edges(path) # превращаю последовательность вершин в последовательность ребер
    G.add_edges_from(path_edges, color='#08e822', width = 2.5) # заново добавляю в граф списки ребер в путях другими цветами

    edge_color_attr = nx.get_edge_attributes(G,'color')
    edge_width_attr = nx.get_edge_attributes(G,'width')
    edges = edge_color_attr.keys() # без list() работает в рисовалке
    edges_colors = edge_color_attr.values() # без list() работает в рисовалке
    edges_widths = list(edge_width_attr.values()) # без list() не работает в рисовалке

    # создаю координаты вершин графа
    if ipos == 1:
        pos = generate_pos(digraph)
    elif ipos == 2:
        pos = nx.circular_layout(G)
    elif ipos == 3:
        pos = nx.random_layout(G)

    # рисование
    nx.draw(G, pos = pos,
            edgelist=edges, edge_color=edges_colors, width = edges_widths,
            nodelist = nodes, node_color = nodes_colors, node_shape = 's',
            font_family = 'sans-serif', with_labels = True, font_weight = 'bold')

    # рисую значения весов на графе
    nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = edges_labels, label_pos = 0.5, font_size = 15, bbox={'facecolor': '#ffffff', 'edgecolor': '#ffffff', 'alpha': 0.6, 'pad': 0}) # label_pos = (0.5 * random.ranf() + 0.25)
    # fig.savefig() сохраняет, понятное дело

    fig.savefig(os.getcwd() + '/output/{}.png'.format(digraph_name))
    plt.show()
    plt.close()

def draw_graph3(digraph, digraph_name, inc_nodes, dec_nodes, k, paths, ipos): # Magnetic Reachability with degree of k
    '''
    Рисует граф, сохраняя граф в директорию /output
    '''
    # ---------------------DRAWING---------------------
    (new_digraph, edges_labels) = generate_separate_graph_and_weights(digraph) # превращаю взвешенный граф в читабельный для программы вид

    G = nx.DiGraph(new_digraph) # создаю граф из образа new_graph
    figure_size = len(digraph.keys())
    fig = plt.figure(figsize = (int(13 * figure_size / 8), int(7 * figure_size / 8)), dpi = 100) # для  сохранения картинки с помощью fig.savefig()

    paths_string = '{'
    for i in range(0, len(paths)-1):
        if i != len(paths)-1:
            paths_string += str(paths[i]) + ',\n'
        else:
            paths_string += str(paths[i]) + '\n}'

    digraph_info = ('Green nodes increments, Red - decrements the magnetization\nPaths: {0}\nReachability type: MnR of k degree\nk = {1}'.format(paths_string, k))

    ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
    ax.text(-0.14, 0.05 + 0.01 * len(paths), digraph_info, fontname = 'sans-serif', fontstyle='normal',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5}) # pad - размер

    # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
    G.add_nodes_from(G.nodes, color = '#949494') # brcmyk - colors
    G.add_nodes_from(inc_nodes, color = '#007a2a')
    G.add_nodes_from(dec_nodes, color = '#830010')
    #G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
    #G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
    node_color_attr = nx.get_node_attributes(G,'color')
    nodes  = node_color_attr.keys() # без list() работает в рисовалке
    nodes_colors = list(node_color_attr.values()) # без list() не работает в рисовалке

    # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
    G.add_edges_from(G.edges,color = 'black', width = 1) # сначала добавляем все ребра черными
    colooor = int('0x08e822',base = 16) # началный цвет для добавочных ребер
    for p in paths: # здесь добавляем все пути в виде последовательности ребер в объект графа
        path_edges = generate_path_edges(p) # превращаю последовательность вершин в последовательность ребер
        hexcolooor = '#0' +  hex(colooor)[2:]
        G.add_edges_from(path_edges, color = hexcolooor, width = 2.5) # заново добавляю в граф списки ребер в путях другими цветами
        colooor += 100 * random.randint(1,500) # новый цвет для каждого пути в формате #f032ae
        if len(hexcolooor) > 7:
            hexcolooor = '#' + hex(colooor)[2:]

    edge_color_attr = nx.get_edge_attributes(G,'color')
    edge_width_attr = nx.get_edge_attributes(G,'width')
    edges = edge_color_attr.keys() # без list() работает в рисовалке
    edges_colors = edge_color_attr.values() # без list() работает в рисовалке
    edges_widths = list(edge_width_attr.values()) # без list() не работает в рисовалке

    # создаю координаты вершин графа
    if ipos == 1:
        pos = generate_pos(digraph)
    elif ipos == 2:
        pos = nx.circular_layout(G)
    elif ipos == 3:
        pos = nx.random_layout(G)

    # рисование
    nx.draw(G, pos = pos,
            edgelist=edges, edge_color=edges_colors, width = edges_widths,
            nodelist = nodes, node_color = nodes_colors, node_shape = 's',
            font_family = 'sans-serif', with_labels = True, font_weight = 'bold')

    # рисую значения весов на графе (в draw3 не нужно)
    # nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = edges_labels, label_pos = 0.5, font_size = 15, bbox={'facecolor': '#ffffff', 'edgecolor': '#ffffff', 'alpha': 0.6, 'pad': 0}) # label_pos = (0.5 * random.ranf() + 0.25)

    # fig.savefig() сохраняет, понятное дело

    fig.savefig(os.getcwd() + '/output/{}.png'.format(digraph_name))
    plt.show()
    plt.close()

def draw_graph4(digraph, digraph_name, inc_nodes, dec_nodes, k, path, time, mass, ipos): # MnRk with weights and masses
    '''
    Рисует граф, сохраняя граф в директорию /output
    '''
    # ---------------------DRAWING---------------------
    (new_digraph, edges_labels) = generate_separate_graph_and_weights(digraph) # превращаю взвешенный граф в читабельный для программы вид

    G = nx.DiGraph(new_digraph) # создаю граф из образа new_graph
    figure_size = len(digraph.keys())
    fig = plt.figure(figsize = (int(13 * figure_size / 8), int(7 * figure_size / 8)), dpi = 100) # для  сохранения картинки с помощью fig.savefig()

    digraph_info = ('Green nodes increments, Red - decrements the magnetization\nPath: {0}\nTime: {1} s\nMass: {2} mbytes\nReachability type: MnR of k degree\nk = {3}'.format(path, time, mass ,k))

    ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
    ax.text(-0.14,0.02,digraph_info,fontname = 'sans-serif', fontstyle='normal',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5}) # pad - размер

    # в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
    G.add_nodes_from(G.nodes, color = '#949494') # brcmyk - colors
    G.add_nodes_from(inc_nodes, color = '#007a2a')
    G.add_nodes_from(dec_nodes, color = '#830010')
    #G.add_node(path[0],color='green')                     # окрашиваю первую вершину пути в зеленый
    #G.add_node(path[len(path)-1],color='blue')            # окрашиваю последнюю вершину пути в синий
    node_color_attr = nx.get_node_attributes(G,'color')
    nodes  = node_color_attr.keys() # без list() работает в рисовалке
    nodes_colors = list(node_color_attr.values()) # без list() не работает в рисовалке

    # в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
    G.add_edges_from(G.edges,color = 'black', width = 1) # сначала добавляем все ребра черными
    path_edges = generate_path_edges(path) # превращаю последовательность вершин в последовательность ребер
    G.add_edges_from(path_edges, color='#08e822', width = 2.5) # заново добавляю в граф списки ребер в путях другими цветами

    edge_color_attr = nx.get_edge_attributes(G,'color')
    edge_width_attr = nx.get_edge_attributes(G,'width')
    edges = edge_color_attr.keys() # без list() работает в рисовалке
    edges_colors = edge_color_attr.values() # без list() работает в рисовалке
    edges_widths = list(edge_width_attr.values()) # без list() не работает в рисовалке

    # создаю координаты вершин графа
    if ipos == 1:
        pos = generate_pos(digraph)
    elif ipos == 2:
        pos = nx.circular_layout(G)
    elif ipos == 3:
        pos = nx.random_layout(G)

    # рисование
    nx.draw(G, pos = pos,
            edgelist=edges, edge_color=edges_colors, width = edges_widths,
            nodelist = nodes, node_color = nodes_colors, node_shape = 's',
            font_family = 'sans-serif', with_labels = True, font_weight = 'bold')

    # рисую значения весов на графе
    nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = edges_labels, label_pos = 0.5, font_size = 15, bbox={'facecolor': '#ffffff', 'edgecolor': '#ffffff', 'alpha': 0.6, 'pad': 0}) # label_pos = (0.5 * random.ranf() + 0.25)
    # fig.savefig() сохраняет, понятное дело

    fig.savefig(os.getcwd() + '/output/{}.png'.format(digraph_name))
    plt.show()
    plt.close()



'''
BBox docs?


Valid :class:`~matplotlib.lines.Line2D` kwargs are

  agg_filter: a filter function, which takes a (m, n, 3) float array and a dpi value, and returns a (m, n, 3) array
  alpha: float (0.0 transparent through 1.0 opaque)
  animated: bool
  antialiased or aa: bool
  clip_box: a `.Bbox` instance
  clip_on: bool
  clip_path: [(`~matplotlib.path.Path`, `.Transform`) | `.Patch` | None]
  color or c: any matplotlib color
  contains: a callable function
  dash_capstyle: ['butt' | 'round' | 'projecting']
  dash_joinstyle: ['miter' | 'round' | 'bevel']
  dashes: sequence of on/off ink in points
  drawstyle: ['default' | 'steps' | 'steps-pre' | 'steps-mid' | 'steps-post']
  figure: a `.Figure` instance
  fillstyle: ['full' | 'left' | 'right' | 'bottom' | 'top' | 'none']
  gid: an id string
  label: object
  linestyle or ls: ['solid' | 'dashed', 'dashdot', 'dotted' | (offset, on-off-dash-seq) | ``'-'`` | ``'--'`` | ``'-.'`` | ``':'`` | ``'None'`` | ``' '`` | ``''``]
  linewidth or lw: float value in points
  marker: :mod:`A valid marker style <matplotlib.markers>`
  markeredgecolor or mec: any matplotlib color
  markeredgewidth or mew: float value in points
  markerfacecolor or mfc: any matplotlib color
  markerfacecoloralt or mfcalt: any matplotlib color
  markersize or ms: float
  markevery: [None | int | length-2 tuple of int | slice | list/array of int | float | length-2 tuple of float]
  path_effects: `.AbstractPathEffect`
  picker: float distance in points or callable pick function ``fn(artist, event)``
  pickradius: float distance in points
  rasterized: bool or None
  sketch_params: (scale: float, length: float, randomness: float)
  snap: bool or None
  solid_capstyle: ['butt' | 'round' |  'projecting']
  solid_joinstyle: ['miter' | 'round' | 'bevel']
  transform: a :class:`matplotlib.transforms.Transform` instance
  url: a url string
  visible: bool
  xdata: 1D array
  ydata: 1D array
  zorder: float

'''
