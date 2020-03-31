
def get_path(digraph, start, goal):
    """
    Поиск с помощью DFS.
    Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    Функция ищет все доступные пути от вершины start до goal
    Возвращает генератор путей.
    """

    stack = [(start, [start])]  # stack - список кортежей (вершина, путь) - (vertex, path)
    while stack:  # проход по всем элементам списка stack, пока stack не станет пустым
        (vertex, path) = stack.pop()  # pop() забирает (удаляет) из списка последний элемент и кладет в (vertex, path)
        for next in set(digraph[vertex]) - set(
                path):  # проход переменной next по множеству A\B, где A - множество соседей вершины vertex,
            # а B - множество вершин, входящих в путь до goal. То есть результирующее множество
            # (по которому идет next) - это соседи минус вершины, включенные в путь
            if next == goal:  # если next это goal
                yield path + [next]  # то добавляем в возвращаемый генератор еще один путь + последняя вершина - goal.
            else:  # если next != goal
                # добавляем в stack кортеж ()
                stack.append((next, path + [next]))


def get_paths_telecom_nets(digraph, start, goal, mass, check=0):
    '''
    DVPTN — Поиск вглубину всех путей в обычном взвешенном графе, функция выводит быстрейший путь из start в goal
    Функция ищет простой путь в обычном взвешенном графе с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
    Возвращает путь - упорядоченное множество вершин.
    Параметр check отвечает за режим работы функции. Если check == 0, то она возвращает быстрейший путь.
    Если check == 1, то она возвращает массив всех возможных путей.
    '''
    yield_stack = []  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0  # время прохождения по пути, t = m / v
    stack = [(start, ([start], t))]

    while stack:

        spop = stack.pop()  # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        for next in set(digraph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
            # ---------------- ORIGINAL START ----------
            if next == goal:
                v = digraph[vertex][next]
                t += mass / v
                yield_stack.append((path + [next], t))  # вместо yield
                t -= mass / v  # otherwise time is COLLAPSING
            else:
                v = digraph[vertex][next]
                t += mass / v
                stack.append((next, (path + [next], t)))
                t -= mass / v
            # ---------------- ORIGINAL END ------------
    if check == 0:
        fastest_path = ([], 0)
        tmin = 100000  # 27,7 часов
        # ipath = 0
        for _path_ in yield_stack:
            if _path_[1] <= tmin:
                tmin = _path_[1]
                fastest_path = _path_
        return fastest_path
    else:
        return yield_stack


def get_vmrk_paths(digraph, inc_nodes, k, start, goal):
    '''
    Depth-First Search — Поиск вглубину, функция выводит все пути в графе типа VMRk из start в goal
    Функция ищет VMRk пути от вершины start до goal
    Возвращает генератор путей.
    '''
    i = 0  # счетчик запрщенных вершин
    stack = [(start, [start], i)]
    while stack:
        (vertex, path, i) = stack.pop()
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS ---------------
        for next in set(digraph[vertex]) - set(path):
            if not ((next in inc_nodes) & (i >= k)):  # допустимость по условию VMRk
                # ---------------- ORIGINAL ----------------
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next], i))


def get_vmrk_paths_telecom_nets(digraph, inc_nodes, k, start, goal, mass, check=0):  # DVPTN — Поиск вглубину всех путей во взвешенном графе типа VMRk, функция выводит быстрейший путь из start в goal
    '''
    Функция ищет VMRk путь с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
    Возвращает путь - упорядоченное множество вершин.
    Параметр check отвечает за режим работы функции. Если check == 0, то она возвращает быстрейший путь.
    Если check == 1, то она возвращает массив всех возможных путей.
    '''
    yield_stack = []  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    i = 0  # счетчик запрещенных вершин
    # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0  # время прохождения по пути, t = m / v
    stack = [(start, ([start], t), i)]

    while stack:

        spop = stack.pop()  # spop = (vertex, {path : t}, i)
        vertex = spop[0]
        path = spop[1][0]
        t = spop[1][1]
        i = spop[2]
        # --------------- CONDITIONS START --------
        if vertex in inc_nodes:
            i += 1
        else:
            i = 0
        # --------------- CONDITIONS END ----------
        for next in set(digraph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
            if not ((next in inc_nodes) & (i >= k)):  # допустимость по условию VMRk
                # ---------------- ORIGINAL START ----------
                if next == goal:
                    v = digraph[vertex][next]
                    t += mass / v
                    yield_stack.append((path + [next], t))  # вместо yield
                    t -= mass / v  # otherwise time is COLLAPSINGs
                else:
                    v = digraph[vertex][next]
                    t += mass / v
                    stack.append((next, (path + [next], t), i))
                    t -= mass / v
            # ---------------- ORIGINAL END ------------
    print()  # echo
    if check == 0:
        fastest_path = ([], 0)
        tmin = 100000  # 27,7 часов
        ipath = 0
        for _path_ in yield_stack:
            if _path_[1] <= tmin:
                tmin = _path_[1]
                fastest_path = _path_
        return fastest_path
    else:
        return yield_stack


def get_mnrk_paths(digraph, inc_nodes, k, start, goal, dec_nodes=[], check=0):
    '''
    DMP - Поиск путей вгулбину в графе с магнитной достижимостью
    Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
    Возвращает генератор путей.
    Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
    Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
    Если dec_nodes пустой, то dec_nodes становятся все вершины графа, кроме inc_nodes.
    Параметр check отвечает за режим работы функции.
    Если check = 0 (значение по умолчанию), то функция выдаст только те пути,
    мангитность которых соответствует заданному порядку k.
    Если check = 1, то она будет работать в режиме проверки,
    то есть выведет все возможные пути из start в goal с их порядками магнитности.
    Если check = 2,
    то она выдаст словарь, в котором ключ - порядок магнитности, а значение - количество путей с таким порядком.

    '''
    i = 0  # счетчик запрщенных вершин
    if dec_nodes == []:
        dec_nodes = list(set(digraph) - set(inc_nodes))

    if check == 2:
        result_dict = dict()

    stack = [(start, [start], i)]
    while stack:
        (vertex, path, i) = stack.pop()  # print(' = ' + str())
        # --------------- CONDITIONS ---------------
        if vertex in inc_nodes:
            i += 1
        elif vertex in dec_nodes:
            i -= 1
        # --------------- CONDITIONS ---------------
        for next in set(digraph[vertex]) - set(path):
            # ---------------- ORIGINAL ----------------
            if next == goal:
                if next in inc_nodes:
                    i += 1
                elif next in dec_nodes:
                    i -= 1
                if check == 0:
                    if i == k:
                        yield path + [next]

                elif check == 1:
                    yield (path + [next], i)

                elif check == 2:
                    if i in result_dict.keys():
                        result_dict[i] += 1
                    else:
                        result_dict.update({i: 1})

            else:
                stack.append((next, path + [next], i))
            # ---------------- ORIGINAL ----------------
    if check == 2:
        yield result_dict


def get_mnrk_paths_telecom_nets(digraph, inc_nodes, k, start, goal, mass, dec_nodes=[], check=0):
    '''
    DMPTN - Поиск вглубину всех путей во взвешенном графе с магнитной достижимостью, функция выводит быстрейший путь из start в goal
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
        dec_nodes = list(set(digraph) - set(inc_nodes))

    if check == 2:
        result_dict = dict()

    yield_stack = []  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
    i = 0  # счетчик запрещенных вершин
    # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
    t = 0  # время прохождения по пути, t = m / v
    stack = [(start, ([start], t), i)]
    while stack:
        spop = stack.pop()  # spop = (vertex, {path : t}, i)
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
        for next in set(digraph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
            if next == goal:
                if next in inc_nodes:
                    i += 1
                elif next in dec_nodes:
                    i -= 1
                if check == 0:
                    if i == k:
                        v = digraph[vertex][next]
                        t += mass / v
                        yield_stack.append((path + [next], t, i))  # вместо yield
                        t -= mass / v
                elif check == 1:
                    v = digraph[vertex][next]
                    t += mass / v
                    yield_stack.append((path + [next], t, i))  # вместо yield
                    t -= mass / v
                elif check == 2:
                    if i in result_dict.keys():
                        result_dict[i] += 1
                    else:
                        result_dict.update({i: 1})
            else:
                v = digraph[vertex][next]
                t += mass / v
                stack.append((next, (path + [next], t), i))
                t -= mass / v

    # if check == 0:
    #     show_dict(yield_stack)
    print()  # echo

    fastest_path = ([], 0)
    tmin = 100000  # 27,7 часов
    ipath = 0
    for _path_ in yield_stack:
        ipath += 1
        if _path_[1] <= tmin:
            tmin = _path_[1]
            fastest_path = _path_[:2]

    if check == 1:
        pass
        # show_dict(yield_stack)
        # print()

    if check != 2:
        return fastest_path  # check == 0 or check == 1
    else:
        return result_dict


def calculate_time_of_path(graph, path, mass):
    time = 0
    for i in range(len(path) - 1):
        time += mass / graph[path[i]][path[i+1]]
    return time

