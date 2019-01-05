digraph1 = {'1': {'2':45, '3':40},
          '2': {'4':15, '9':35},
          '3': {'5':45},
          '4': {'6':20},
          '5': {'6':10, '7':25},
          '6': {'8':40},
          '7': {'9':30},
          '8': {'3':50, '7':35, '10':5},
          '9': {'10':25},
          '10':{}}

digraph2 = {'1': {'2':45},
          '2': {'3':15},
          '3': {'4':45},
          '4': {'5':20},
          '5': {'6':10},
          '6': {'7':40},
          '7': {'8':30},
          '8': {'9':50},
          '9': {'10':25},
          '10':{}}

digraph = digraph1

r_nodes = ['1','2','3','5','6','8','9','10']

k = 3

start = '1'
goal = '10'

# def igetter(items,n):
#     '''
#     Получает массив словарей, каждый из одной пары элементов, и возвращает массив
#     из ключей этих словарей
#     '''
#     normal_items = []
#     for i in range(0,len(items)):
#         normal_items.append(items[0])
#     return normal_items

def dfs_vmrk_paths(graph, r_nodes, k, start, goal):                              # Depth-First Search — Поиск вглубину, функция выводит все VMRk пути из start в goal
    '''
    Функция ищет VMRk пути от вершины start до goal
    Возвращает генератор путей
    '''
    i = 0                           # счетчик запрщенных вершин
    stack = [(start, [start], i)]
    while stack:
        (vertex, path, i) = stack.pop()
        # --------------- CONDITIONS ---------------
        if vertex in r_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):
            if not ((next in r_nodes) & (i >= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next], i))
            # ---------------- ORIGINAL ----------------

def dfs_vmrk_paths_telecom_nets(graph, r_nodes, k, start, goal):                              # Depth-First Search — Поиск вглубину, функция выводит все VMRk пути из start в goal
    '''
    Функция ищет VMRk путь с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
    Возвращает путь - упорядоченное множество вершин.
    '''
    yield_stack = []                # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    i = 0                           # счетчик запрщенных вершин
    m = 200                           # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0                           # время прохождения по пути, t = m / v
    stack = [(start, ([start], t), i)]
    while stack:
        spop = stack.pop() # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        i = spop[2]
        # --------------- CONDITIONS ---------------
        if vertex in r_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):    # set({a : b, c : d}) == {a,c}
            if not ((next in r_nodes) & (i >= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    v = graph[vertex][next]
                    t += m / v
                    yield_stack.append((path + [next], t)) # вместо yield
                else:
                    v = graph[vertex][next]
                    t += m / v
                    stack.append((next, (path + [next], t), i))
            # ---------------- ORIGINAL ----------------

    tmin = 100000                    # 27,7 часов
    for _path_ in yield_stack:
        if _path_[1] <= tmin:
            tmin = _path_[1]
            fastest_path = _path_

    return fastest_path

def generate_separate_graph_and_weights(g):
    # g = {'1': {'2':45, '3':40},
    #      '2': {'4':15, '9':35},
    #      '3': {'5':45},
    #      '4': {'6':20},
    #      '5': {'6':10, '7':25},
    #      '6': {'8':40},
    #      '7': {'9':30},
    #      '8': {'3':50, '7':35, '10':5},
    #      '9': {'10':25},
    #      '10':{}}
    new_g = dict()                         # новый граф без весов
    edges_with_labels = dict()             # отдельный словарь для весов {('1','2') : weight1, ('3','4') : weight2}
    for vi in list(g.keys()):              # иду по вершинам графа. vi - текушая вершина
        neighbours = []
        for vj in list(g[vi].keys()):      # иду по соседям vi
            neighbours.append(vj)
            edges_with_labels.update({(vi,vj) : str(g[vi][vj])})

        new_g.update({vi:neighbours})

    return((new_g, edges_with_labels))

# (ng, ewl) = generate_separate_graph_and_weights(digraph)
# print(str(ng))
# print()
# print(str(ewl))

# path = dfs_vmrk_paths_telecom_nets(digraph, r_nodes, k, start, goal)
#
# print (path)
