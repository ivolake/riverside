# cd Documents\Python_Scripts\Networks_Science\VMRk\polygon
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


def dfs_paths(graph, start, goal):                                               # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
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
                stack.append((next, path + [next]))  # добавляем в stack кортеж ()

def dfs_vmrk_paths(graph, r_nodes, k, start, goal):                              # Depth-First Search — Поиск вглубину, функция выводит все путив графе типа VMRk из start в goal
    '''
    Функция ищет VMRk пути от вершины start до goal
    Возвращает генератор путей.
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

def dfs_vmrk_paths_telecom_nets_with_logs(graph, r_nodes, k, start, goal, m, check = 0):   # DVPTN — Поиск вглубину всех путей в графе типа VMRk, функция выводит быстрейший путь из start в goal
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
    iii = 0
    while stack:
        iii += 1
        print('-----------------------------------------------')
        print('stack on {0} = '.format(iii))
        show_dict(stack)
        print(str(iii) + ' spop: ')
        spop = stack.pop() # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        i = spop[2]
        print('vertex = ' + vertex)
        print('path head to this vertex = ' + str(path))
        # --------------- CONDITIONS ---------------
        if vertex in r_nodes:
            i += 1
        else:
            i = 0
        print('stricting i = ' + str(i))
        # --------------- CONDITIONS ---------------
        print('set(graph[vertex]) - set(path) = ' + str(set(graph[vertex]) - set(path)))
        for next in set(graph[vertex]) - set(path):    # set({a : b, c : d}) == {a,c}
            print('   next = ' + next) #print(' = ' + )
            print('   accesible with VMRk [not ((next in r_nodes) & (i >= k))] = ' + str(not ((next in r_nodes) & (i >= k))))
            if not ((next in r_nodes) & (i >= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                print('   goal? : ' + str(next == goal))
                if next == goal:
                    v = graph[vertex][next]
                    t += m / v
                    print('    from {0} to {1} t = '.format(vertex, next) + str(t))
                    print('    added path + t = ' + str((path + [next], t)))
                    yield_stack.append((path + [next], t)) # вместо yield
                    t -= m / v # otherwise time is COLLAPSINGs
                else:
                    v = graph[vertex][next]
                    t += m / v
                    print('    from {0} to {1} t = '.format(vertex, next) + str(t))
                    print('    added to stack = ' + str((next, (path + [next], t), i)))
                    stack.append((next, (path + [next], t), i))
                    t -= m / v
            print('yield_stack now = ')
            show_dict(yield_stack)
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

def dfs_vmrk_paths_telecom_nets(graph, r_nodes, k, start, goal, m, check = 0):   # DVPTN — Поиск вглубину всех путей в графе типа VMRk, функция выводит быстрейший путь из start в goal
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



def dfs_mnrk_parks(graph, inc_nodes, k, start, goal, dec_nodes = [], check = 0):
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


def dfs_mnrk_parks_telecom_nets(graph, inc_nodes, k, start, goal, m, dec_nodes = [], check = 0):
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
    tmin = 100000                    # 27,7 часов
    ipath = 0
    fastest_path = ([],0)
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
        return result_dict  # check == 2

a = 2

def ab():
    global a # вытаскивание из глобального пространства переменной а
    b = a
    print(b)
    show_dict(globals())

digraph1 = {
'1': {'2':45, '3':40},
'2': {'4':15, '9':35},
'3': {'5':45},
'4': {'6':20},
'5': {'6':10, '7':25},
'6': {'8':40},
'7': {'9':30},
'8': {'3':50, '7':35, '10':5},
'9': {'10':25},
'10':{}
}

digraph2 = {
'1': {'2':45},
'2': {'3':15},
'3': {'4':45},
'4': {'5':20},
'5': {'6':10},
'6': {'7':40},
'7': {'8':30},
'8': {'9':50},
'9': {'10':25},
'10':{}
}

digraph3 = {
'1': ['2', '3'],
'2': ['4', '9'],
'3': ['5'],
'4': ['6'],
'5': ['6', '7'],
'6': ['8'],
'7': ['9'],
'8': ['3','7','10'],
'9': ['10'],
'10': []
}

digraph4 = {
'1' : {'3': 13, '4': 32},
'2' : {'1': 40, '6': 18, '7': 25, '12': 21},
'3' : {'4': 14, '5': 22},
'4' : {'2': 29},
'5' : {'7': 31, '10': 11},
'6' : {'5': 26, '8': 15},
'7' : {'9': 39, '10': 27},
'8' : {'14': 20},
'9' : {'10': 11, '11': 10, '12': 30, '13': 33, '17': 28},
'10' : {'12': 34, '18': 9},
'11' : {'6': 35},
'12' : {'14': 24},
'13' : {'15': 19},
'14' : {'16': 21},
'15' : {'11': 26, '18': 19},
'16' : {'15': 36, '18': 38},
'17' : {'18': 29},
'18' : {'7': 41}
 }

digraph = digraph4
inc_nodes1 = ['1','2','3','5','6','8','9','10']
inc_nodes2 = ['1','2','3','6','8','9']
inc_nodes4 = ['1','2','3','5','10','11','14','15','17']
inc_nodes5 = ['1','3','4','9']
inc_nodes = inc_nodes4

dec_nodes1 = ['4','5','7','10']
dec_nodes4 = ['4','6','7','8','9','16']
dec_nodes = dec_nodes4
k = 3

c = int(input())
start = '10'
goal = '9'
m = 20


# print(dfs_vmrk_paths_telecom_nets(digraph, inc_nodes, k, start, goal, m))
# print(list(dfs_mnrk_parks(digraph, inc_nodes, k, start, goal, dec_nodes, c)))
show_dict(dfs_mnrk_parks_telecom_nets(digraph, inc_nodes, k, start, goal, m, dec_nodes,  c))
# print(dfs_mnrk_parks_telecom_nets(digraph, inc_nodes, k, start, goal, m, c, dec_nodes))
# show_dict(digraph)
# print(list(dfs_vmrk_paths(digraph, inc_nodes, k, start, goal)))
