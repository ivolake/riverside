import drawing as drawing_module
from pandas import read_csv, read_excel
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

def choose(digraph_N = 0, incrementation_nodes_N = 0, decrementation_nodes_N = 0):
    '''
    Эта функция -- интерпритатор ввода.
    digraph_N - Переменная, содержащая номер графа из базы данных. Отсчет начинается с 0.
    incrementation_nodes_N - Переменная, содержащаю номер массива повышающих вершин. Отсчет начинается с 0.
    decrementation_nodes_N - Переменная, содержащая номер массива понижающих вершин.
    Возвращает массив
    stack = (digraphs[digraph_N], restricred_nodes[incrementation_nodes_N], decrementation_nodes[decrementation_nodes_N])
    '''
    # DATA
    digraphs = []
    incrementation_nodes = []
    decrementation_nodes = []

    digraphs.append({})

    digraphs.append({'1': ['2', '3'],
              '2': ['4', '9'],
              '3': ['5'],
              '4': ['6'],
              '5': ['6', '7'],
              '6': ['8'],
              '7': ['9'],
              '8': ['3','7','10'],
              '9': ['10'],
              '10': []})

    digraphs.append({'1': ['2', '3', '9'],
              '2': ['4'],
              '3': ['5', '10'],
              '4': ['6', '7'],
              '5': ['6'],
              '6': ['8'],
              '7': ['5'],
              '8': ['17'],
              '9': ['19'],
              '10': ['11', '17'],
              '11':['12'],
              '12':['13'],
              '13':['15'],
              '14':[],
              '15':['16', '18'],
              '16':['20'],
              '17':['20'],
              '18':['20'],
              '19':['20'],
              '20':[],
              })

    digraphs.append({'1': {'2':45, '3':40},
              '2': {'4':15, '9':35},
              '3': {'5':45},
              '4': {'6':20},
              '5': {'6':10, '7':25},
              '6': {'8':40},
              '7': {'9':30},
              '8': {'3':50, '7':35, '10':5},
              '9': {'10':25},
              '10':{}})

    incrementation_nodes.append([])
    incrementation_nodes.append(['1','2','3','5','6','8','9','10'])
    incrementation_nodes.append(['1','2','3','4','5','6','8','11','12','13','15','16','20'])
    incrementation_nodes.append(['1','3','4','9'])
    incrementation_nodes.append(['1','3','4','6'])
    incrementation_nodes.append(['1','2','3','6','8','9'])
    incrementation_nodes.append(['1','2','3','5','10','11','14','15','17'])

    decrementation_nodes.append([])
    decrementation_nodes.append(['4','5','7','10'])
    decrementation_nodes.append(['4','6','7','8','9','16'])

    stack = (digraphs[digraph_N], incrementation_nodes[incrementation_nodes_N], decrementation_nodes[decrementation_nodes_N])

    return stack

def extract(fname, flag = False):
    '''
    Если flag = False (по умолчанию)
    Функция считывает граф, заданный матрицей смежности, из файла. Допустимые типы файлов: .txt, .csv, .xls и .xlsx.
    В аргументе функции - путь до файла. Если файл лежит в той же директории,
    что и вызываемая программа, или на рабочем столе компьютера, можно указать просто название файла.
    Названия требуется указать с расширением.
    Возвращаемые данные - граф.
    Пример:

    digraph = extract('d1.txt')

    Если flag = True
    Функция дополнительно считывает inc_nodes и dec_nodes из файла %fname%_info.txt
    '''
    # CHECKING THE EXISTENCE
    if os.path.isfile(os.getcwd() + '/' + fname):
        # пробуем найти в текущей директории
        fpath = os.getcwd() + '/' + fname

    elif os.path.isfile(os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname):
        # пробуем найти на рабочем столе
        fpath = os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname
        # Почему разные слэши?
        # Потому что функция find() ищет в строке, которая создана обработчиком Windows, и там разделители директорий - \
        # А строку, которую прибавляю я ('Desktop/test1.txt'), обрабатывает Python-овский обработчик, и для него разделитель директорий - /

    elif os.path.isfile(fname):
        fpath = fname

    else:
        print('File not found.')
        exit()

    # EXECUTUING THE GRAPH
    suf = fpath[fpath.rfind('.'):len(fpath)]
    g = dict()          # для самого графа
    is_weighted = False # Является ли взвешенным. Изначально считается, что нет
                        # Если в матрице встретятся иные, чем 0 и 1, числа, то он определится как взвешенный и не будет преобразован.
                        # Если встретятся только 0 и 1, то он будет преобразован.
    if (suf == '.csv') | (suf == '.txt'):
        g_df = read_csv(fpath, header = 0, index_col = 0, sep = ', ', engine = 'python') # print(g_df.loc[2, '1'])

    elif (suf == '.xls') | (suf == '.xlsx'):
        g_df = read_excel(fpath, engine = 'python') # print(g_df.loc[2, 1])

    # print(g_df)

    for i in range(0,len(g_df.index)):
        neighbours = dict()

        for j in range(0,len(g_df.columns)):
            if g_df.loc[g_df.index[i], g_df.columns[j]] not in [0,1]:
                is_weighted = True

            if (g_df.loc[g_df.index[i], g_df.columns[j]] != 0) & (i != j):
                neighbours.update({str(g_df.index[j]) : g_df.loc[g_df.index[i], g_df.columns[j]]})

        g.update({str(g_df.columns[i]) : neighbours})


    if not is_weighted:
        (g, shit) = drawing_module.generate_separate_graph_and_weights(g) # shit is shit

    # if flag:
    #     # EXECUTING ADDITIONAL INFORAMTION (INC AND DEC NODES LISTS)
    #     if os.path.isfile(fpath[:fpath.rfind('.')] + '_info.txt'):
    #         # пробуем найти в текущей директории
    #         info_fpath = fpath[:fpath.rfind('.')] + '_info.txt'
    #     else:
    #         print('Information file containing inc or/and dec nodes not found.')
    #         print('Check the name of the file, it needs to be the same as the graph template file name, but with "_info" in the end and with .txt suffix.')
    #         print('Eg: grap.csv and graph_info.txt')
    #         print('Also, info file must be in the same directory, as template.')
    #
    #     ig_df = read_csv(info_fpath, header = 0, index_col = 0, sep = ', ', engine = 'python')
    #
    #     if len(ig_df.index) == 1:
    #
    #     elif len(ig_df.index) == 2:
    #
    #     else:
    #         print('File is empty or contains unnecessery information (more than 2 rows)')


    show_dict(g)
    return g


def dfs_paths(graph, start, goal):                                                                    # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    '''
    Функция ищет все доступные пути от вершины start до goal
    Возвращает генератор путей.

    '''
    stack = [(start, [start])]                       # stack - список кортежей (вершина, путь) - (vertex, path)
    while stack:                                     # проход по всем элементам списка stack, пока stack не станет пустым
        (vertex, path) = stack.pop()                 # pop() забирает (удаляет) из списка последний элемент и кладет в (vertex, path)
        for next in set(graph[vertex]) - set(path):  # проход переменной next по множеству A\B, где A - множество соседей вершины vertex,
                                                     # а B - множество вершин, входящих в путь до goal. То есть результирующее множество
                                                     # (по которому идет next) - это соседи минус вершины, включенные в путь
            if next == goal:                         # если next это goal
                yield path + [next]                  # то добавляем в возвращаемый генератор еще один путь + последняя вершина - goal.
            else:                                    # если next != goal
                                                     # добавляем в stack кортеж ()
                stack.append((next, path + [next]))

def dfs_vmrk_paths(graph, inc_nodes, k, start, goal):                                                   # Depth-First Search — Поиск вглубину, функция выводит все пути в графе типа VMRk из start в goal
    '''
    Функция ищет VMRk пути от вершины start до goal
    Возвращает генератор путей.
    '''
    i = 0                           # счетчик запрщенных вершин
    stack = [(start, [start], i)]
    while stack:
        (vertex, path, i) = stack.pop()
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):
            if not ((next in inc_nodes) & (i >= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next], i))

def dfs_vmrk_paths_telecom_nets(graph, inc_nodes, k, start, goal, m, check = 0):                        # DVPTN — Поиск вглубину всех путей во взвешенном графе типа VMRk, функция выводит быстрейший путь из start в goal
    '''
    Функция ищет VMRk путь с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
    Возвращает путь - упорядоченное множество вершин.
    Параметр check отвечает за режим работы функции. Если check == 0, то она возвращает быстрейший путь.
    Если check == 1, то она возвращает массив всех возможных путей.
    '''
    yield_stack = []                # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    i = 0                           # счетчик запрещенных вершин
    # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0                           # время прохождения по пути, t = m / v
    stack = [(start, ([start], t), i)]

    while stack:

        spop = stack.pop() # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        i = spop[2]
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):    # set({a : b, c : d}) == {a,c}
            if not ((next in inc_nodes) & (i >= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    v = graph[vertex][next]
                    t += m / v
                    yield_stack.append((path + [next], t)) # вместо yield
                    t -= m / v # otherwise time is COLLAPSINGs
                else:
                    v = graph[vertex][next]
                    t += m / v
                    stack.append((next, (path + [next], t), i))
                    t -= m / v
            # ---------------- ORIGINAL ----------------
    print() # echo
    if check == 0:
        fastest_path = ([],0)
        tmin = 100000                    # 27,7 часов
        ipath = 0
        for _path_ in yield_stack:
            if _path_[1] <= tmin:
                tmin = _path_[1]
                fastest_path = _path_
        return fastest_path
    else:
        return yield_stack

def dfs_mnrk_paths(graph, inc_nodes, k, start, goal, dec_nodes = [], check = 0):                  # DMP - Поиск путей вгулбину в графе с магнитной достижимостью
    '''
    Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
    Возвращает генератор путей.
    Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
    Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
    Параметр check отвечает за режим работы функции. Если check = 0 (значение по умолчанию), то функция выдаст только те пути,
    мангитность которых соответствует заданному порядку k. Если check = 1, то она будет работать в режиме проверки,
    то есть выведет все возможные пути из start в goal с их порядками магнитности. Если check = 2,
    то она выдаст словарь, в котором ключ - порядок магнитности, а значение - количество путей с таким порядком.

    '''
    i = 0                           # счетчик запрщенных вершин
    if dec_nodes == []:
        dec_nodes = list(set(graph) - set(inc_nodes))

    if check ==  2:
        result_dict = dict()

    stack = [(start, [start], i)]
    while stack:
        (vertex, path, i) = stack.pop()    # print(' = ' + str())
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        elif vertex in dec_nodes:
            i -= 1
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):
            # ---------------- ORIGINAL ----------------
            if next == goal:
                if check == 0:
                    if i == k:
                        yield path + [next]

                elif check == 1:
                    yield (path + [next], i)

                elif check == 2:
                    if i in result_dict.keys():
                        result_dict[i] += 1
                    else:
                        result_dict.update({i:1})

            else:
                stack.append((next, path + [next], i))
            # ---------------- ORIGINAL ----------------
    if check == 2:
        yield result_dict

def dfs_mnrk_paths_telecom_nets(graph, inc_nodes, k, start, goal, m, dec_nodes = [], check = 0):  # DMPTN - Поиск вглубину всех путей во взвешенном графе с магнитной достижимостью, функция выводит быстрейший путь из start в goal
    '''
    Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
    Возвращает путь - упорядоченный массив вершин, если check != 2.
    Возвращает словарь (подробно см. ниже), если check == 2.
    Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
    Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
    Параметр check отвечает за режим работы функции. Если check == 0 (значение по умолчанию),
    то функция вернет самый быстрый путь из соответствующих заданному порядку k. Если check == 1, то она будет работать в режиме проверки,
    то есть выведет все возможные пути из start в goal с их порядками магнитности. Вернет самый быстрый путь из всех возможных. Если check == 2,
    то она выдаст словарь, в котором ключ - порядок магнитности, а значение - количество путей с таким порядком.
    '''
    if dec_nodes == []:
        dec_nodes = list(set(graph) - set(inc_nodes))

    if check ==  2:
        result_dict = dict()

    yield_stack = []                # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    i = 0                           # счетчик запрещенных вершин
    # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0                           # время прохождения по пути, t = m / v
    stack = [(start, ([start], t), i)]
    while stack:
        spop = stack.pop() # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        i = spop[2]
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        elif vertex in dec_nodes:
            i -= 1
        # --------------- CONDITIONS ---------------
        for next in set(graph[vertex]) - set(path):    # set({a : b, c : d}) == {a,c}
            if next == goal:
                    if check == 0:
                        if i == k:
                            v = graph[vertex][next]
                            t += m / v
                            yield_stack.append((path + [next], t, i)) # вместо yield
                            t -= m / v
                    elif check == 1:
                        v = graph[vertex][next]
                        t += m / v
                        yield_stack.append((path + [next], t, i)) # вместо yield
                        t -= m / v
                    elif check == 2:
                        if i in result_dict.keys():
                            result_dict[i] += 1
                        else:
                            result_dict.update({i:1})
            else:
                v = graph[vertex][next]
                t += m / v
                stack.append((next, (path + [next], t), i))
                t -= m / v




    # if check == 0:
    #     show_dict(yield_stack)
    print() # echo

    fastest_path = ([],0)
    tmin = 100000                    # 27,7 часов
    ipath = 0
    for _path_ in yield_stack:
        ipath += 1
        if _path_[1] <= tmin:
            tmin = _path_[1]
            fastest_path = _path_

    if check == 1:
        show_dict(yield_stack)
        print()

    if check != 2:
        return fastest_path # check == 0 or check == 1
    else:
        return result_dict



def main(type, a1, a2, a3, a4, a5 = '', a6 = '', a7 = '', a8 = '', a9 = ''):

# (type, digraph, digraph_name, inc_nodes, dec_nodes, k, path, time, mass, ipos)

    if type == '0':
        drawing_module.draw_graph0(digraph = a1, digraph_name = a2, path = a3, ipos = a4) # (digraph, digraph_name, paths, ipos)

    elif type == '1':
        drawing_module.draw_graph1(digraph = a1, digraph_name = a2, inc_nodes = a3, k = a4, paths = a5, ipos = a6) # (digraph, digraph_name, inc_nodes, k, paths, ipos)

    elif type == '2':
        drawing_module.draw_graph2(digraph = a1, digraph_name = a2, inc_nodes = a3, k = a4, path = a5, time = a6, mass = a7, ipos = a8) # (digraph, digraph_name, inc_nodes, k, path, time, mass, ipos)

    elif type == '3':
        drawing_module.draw_graph3(digraph = a1, digraph_name = a2, inc_nodes = a3, dec_nodes = a4, k = a5, paths = a6, ipos = a7) # (digraph, digraph_name, inc_nodes, dec_nodes, k, paths, ipos)

    elif type == '4':
        drawing_module.draw_graph4(digraph = a1, digraph_name = a2, inc_nodes = a3, dec_nodes = a4, k = a5, path = a6, time = a7, mass = a8, ipos = a9) # (digraph, digraph_name, inc_nodes, dec_nodes, k, path, time, mass, ipos)
