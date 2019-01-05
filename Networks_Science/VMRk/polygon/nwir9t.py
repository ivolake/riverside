# cd Documents\Python_Scripts\Networks_Science
digraph1 = {'1': ['2', '3'],
          '2': ['4', '9'],
          '3': ['5'],
          '4': ['6'],
          '5': ['6', '7'],
          '6': ['8'],
          '7': ['9'],
          '8': ['3','7','10'],
          '9': ['10'],
          '10': []}

digraph2 = {'1': ['2', '3'],
          '2': ['4', '9'],
          '3': ['5'],
          '4': ['6'],
          '5': ['6', '7'],
          '6': ['8'],
          '7': ['9'],
          '8': ['10'],
          '9': ['10'],
          '10': []}

digraph3 = {'1': ['2', '3'],
          '2': ['4', '9'],
          '3': ['5'],
          '4': ['6'],
          '5': ['6', '7'],
          '6': ['8','5'],
          '7': ['9'],
          '8': ['3','7','10'],
          '9': ['10'],
          '10': []}


restricted_nodes = ['1','2','3','5','6','8','9','10']


digraph = digraph3
digraph_name = 'digraph1'


# НИЖЕ ХЕРНЯ
# def my_dfs_vmrk_path(graph, r_nodes, k, start, goal):
#     curr_node = start
#     i = 0
#     I = 0
#     path = []
#     visited = set()
#
#     print('graph = ' + str(graph))
#     print('start = ' + str(start))
#     print('goal = ' + str(goal))
#     print('r_nodes = ' + str(r_nodes))
#
#     while curr_node != goal:
#         I += 1;
#         print('I_' + str(I)+':',end = ' -------------------------------------\n')
#         print('curr_node = ' + str(curr_node))
#         print('curr_node in r_nodes = ' + str(curr_node in r_nodes))
#         print('restr count i = ' +  str(i))
#         print('(curr_node in r_nodes) = ' + str(curr_node in r_nodes))
#         print('(curr_node not in visited) = ' + str(curr_node not in visited))
#         print('(i <= k) = ' + str(i <= k))
#
#         if (curr_node in r_nodes) & (curr_node not in visited) & (i <= k):
#             i += 1
#         elif (curr_node not in r_nodes):
#             i = 0
#
#         print('after proc curr_node restr count i = ' +  str(i))
#         print('visited = ' + str(visited))
#         print('path = ' + str(path))
#
#         curr_nei = graph[curr_node]
#
#         print('curr_nei = ' + str(curr_nei))
#         print('set(curr_nei) - set(visited) - set(curr_node) = ' + str(set(curr_nei) - set(visited) - set(curr_node)))
#         print('(i > k) = ' + str(i > k))
#
#         if (((set(curr_nei) - set(visited) - set(curr_node)) == {}) | (i > k)):
#             visited.add(curr_node)
#             if curr_node != start:
#                 curr_node = path.pop()
#             if curr_node in r_nodes:
#                 i -= 1
#         else:
#             for next_node in (set(curr_nei) - set(visited) - set(curr_node)):
#                 print('next_node = ' + str(next_node))
#                 print('(next_node not in visited) & (i <= k) = ' + str((next_node not in visited) & (i <= k)))
#                 if (next_node not in visited) & (i <= k):
#                     visited.add(curr_node)
#                     path.append(curr_node)
#                     curr_node = next_node
#
#                     break
#                 elif (next_node not in visited) & (i >= k):
#                     visited.add(next_node)
#
#         print('after nexting curr_node = ' + str(curr_node) + ' path = ' + str(path))
#         print('i = ' + str(i) + ' (curr_node == goal) & (i == k) = ' +  str((curr_node == goal) & (i == k)))
#         if (curr_node == goal) & (i == k):
#             curr_node = path.pop()
#
#     return path + [goal]


# Мои аналоги dfs_paths
def my_dfs_path(graph,start,goal):
    curr_node = start
    path = []                                                  # текущий путь
    visited = []
    while curr_node != goal:
        curr_nei = graph[curr_node]

        if (set(curr_nei) - set(visited)) == {}:
            curr_node = path.pop()
        else:
            for next_node in (set(curr_nei) - set(visited)):
                if next_node not in visited:
                    visited.append(curr_node)
                    path.append(curr_node)
                    curr_node = next_node
                    break

    return path + [goal]

def my_dfs_paths(graph,start,goal):
    stack = []
    i = 0
    while i<=len(graph.keys()) ** 2:
        print ('i = ' + str(i))



        curr_node = start
        path = []                                                  # текущий путь
        visited = []
        while curr_node != goal:
            curr_nei = graph[curr_node]

            if (set(curr_nei) - set(visited)) == {}:
                curr_node = path.pop()
            else:
                for next_node in (set(curr_nei) - set(visited)):
                    if next_node not in visited:
                        visited.append(curr_node)
                        path.append(curr_node)
                        curr_node = next_node
                        break

        p = path + [goal]



        print ('path = ' + str(path))
        print ('stack = ' + str(stack))
        if path in stack:
            i += 1
        else:
            stack.append(path)

    for p in stack:
        yield p

# Мои модификации dfs_paths
def dfs_paths(graph, start, goal):                   # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    '''
    Функция ищет все доступные пути от вершины start, и если находит вершину goal, записывает ее в yield
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

def dfs_vmrk_paths(graph, r_nodes, k, start, goal):                   # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    '''
    Функция ищет VMRk пути от вершины start до goal
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
            if not ((next in r_nodes) & (i>= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next], i))
            # ---------------- ORIGINAL ----------------

# Логированные функции для отладки
def dfs_vmrk_paths_log(graph, r_nodes, k, start, goal):                   # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    '''
    Функция ищет VMRk пути от вершины start до goal
    '''
    i = 0                           # счетчик запрщенных вершин
    stack = [(start, [start], i)]
    print('graph = ' + str(graph))
    print('r_nodes = ' + str(r_nodes))
    print('start = ' + str(start))
    print('goal = ' + str(goal))
    print('stack = ' + str(stack))
    print('i = ' + str(i))
    I = 0
    while stack:
        I += 1;
        print(str(I)+':',end = '*********************************\n')
        (vertex, path, i) = stack.pop()
        print('(vertex, path, i) = ' + str((vertex, path, i)) + u' и stack = ' + str(stack))
        print('(vertex in r_nodes) = ' + str(vertex in r_nodes))
        print('i = ' + str(i))
        # --------------- CONDITIONS ---------------
        if vertex in r_nodes:
            i += 1
        else:
            i = 0
        print('after checking: i = ' + str(i))
        # --------------- CONDITIONS ---------------
        print('graph[vertex] = ' + str(graph[vertex]))
        print('set(graph[vertex]) = ' + str(set(graph[vertex])))
        print('set(graph[vertex]) - set(path) = ' + str(set(graph[vertex]) - set(path)))
        for next in set(graph[vertex]) - set(path):
            print('next = ' + str(next))
            print('next == goal: ' + str(next == goal))
            print('(next in r_nodes) = ' + str(next in r_nodes))
            print('((next in r_nodes) & (i>= k)) = ' + str((next in r_nodes) & (i>= k)))
            if not ((next in r_nodes) & (i>= k)):     # допустимость по условию VMRk
            # ---------------- ORIGINAL ----------------
                if next == goal:
                    yield path + [next]
                    print('path + [next] = ' + str(path + [next]))
                    print('stack = ' + str(stack))
                else:
                    stack.append((next, path + [next], i))
                    print('stack = ' + str(stack))
            # ---------------- ORIGINAL ----------------

def dfs_paths_log(graph, start, goal):                   # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    '''
    Функция ищет все доступные пути от вершины start, и если находит вершину goal, записывает ее в yield
    '''
    stack = [(start, [start])]                       # stack - список кортежей (вершина, путь) - (vertex, path)
    print('graph = ' + str(graph))
    print('start = ' + str(start))
    print('goal = ' + str(goal))
    print('stack = ' + str(stack))
    I = 0
    while stack:                                     # проход по всем элементам списка stack, пока stack не станет пустым
        I += 1;
        print(str(I)+':\n',end = '')
        (vertex, path) = stack.pop()                 # pop() забирает (удаляет) из списка последний элемент и кладет в (vertex, path)
        print('(vertex,path) = ' + str((vertex, path)) + u' и stack = ' + str(stack))
        print('graph[vertex] = ' + str(graph[vertex]))
        print('set(graph[vertex]) = ' + str(set(graph[vertex])))
        print('set(graph[vertex]) - set(path) = ' + str(set(graph[vertex]) - set(path)))
        for next in set(graph[vertex]) - set(path):  # проход переменной next по множеству A\B, где A - множество соседей вершины vertex,
            print('next = ' + str(next))
            print('next == goal: ' + str(next == goal))
                                                     # а B - множество вершин, входящих в путь до goal. То есть результирующее множество
                                                     # (по которому идет next) - это соседи минус вершины, включенные в путь
            if next == goal:                         # если next это goal
                yield path + [next]
                print('path + [next] = ' + str(path + [next]))
                print('stack = ' + str(stack))               # то добавляем в возвращаемый генератор еще один путь + последняя вершина - goal.
            else:                                    # если next != goal
                stack.append((next, path + [next]))  # добавляем в stack кортеж ()
                print('stack = ' + str(stack))


# print(list(my_dfs_paths(digraph, '1', '10')))
# print(my_dfs_path(digraph,'1','10')) # РАБОТАЕЕЕТ
print(list(dfs_vmrk_paths(digraph, restricted_nodes, 2, '1', '7')))
