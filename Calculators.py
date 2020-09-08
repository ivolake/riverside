import json
from typing import List

from Paths import PathCollection, Path, TNPath, TNPathCollection, MPathCollection, MPath, TNMPath, \
    TNMPathCollection


class BaseCalculator:
    def __init__(self, graph: dict, start: str, goal: str):
        self.graph = graph
        self.start = start
        self.goal = goal

    def calculate(self) -> PathCollection:
        """
        Поиск с помощью DFS.
        Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
        Функция ищет все доступные пути от вершины start до goal
        Возвращает генератор путей.
        """


        paths = PathCollection([]) # контейнер для итоговых возможных путей
        stack = [(self.start, Path([self.start]))] # stack - список кортежей (вершина, путь) - (vertex, path)
        while stack:  # проход по всем элементам списка stack, пока stack не станет пустым
            (vertex, path) = stack.pop()  # pop() забирает (удаляет) из списка последний элемент и кладет в (vertex, path)
            for nextv in set(self.graph[vertex]) - set(path):  # проход переменной nextv (next vertex) по множеству A\B, где A - множество соседей вершины vertex,
                # а B - множество вершин, входящих в путь до goal. То есть результирующее множество
                # (по которому идет next) - это соседи минус вершины, включенные в путь
                if nextv == self.goal:  # если nextv это goal
                    paths.append(path + [nextv]) # то добавляем в возвращаемый PathCollection еще один путь + последняя вершина - goal.
                else:  # если next != goal
                    # добавляем в stack кортеж ()
                    stack.append((nextv, path + [nextv]))
        return paths

class VMRkCalculator(BaseCalculator):
    def __init__(self, graph: dict, start: str, goal: str, inc_nodes: list, k: int):
        BaseCalculator.__init__(self, graph, start, goal)

        self.inc_nodes = inc_nodes
        self.k = k

    def calculate(self) -> PathCollection:
        """
        Depth-First Search — Поиск вглубину, функция выводит все пути в графе типа VMRk из start в goal
        Функция ищет VMRk пути от вершины start до goal
        VMRk путь порядка k - путь, на котором увеливающие вершины встречаются не более k раз подряд.
        Возвращает список путей.
        """
        paths = MPathCollection([])
        i = 0  # счетчик запрщенных вершин
        stack = [(self.start, MPath([self.start], i))]
        while stack:
            (vertex, path) = stack.pop()
            i = path.i
            # --------------- CONDITIONS ---------------
            if vertex in self.inc_nodes:
                i += 1
            else:
                i = 0
            # --------------- CONDITIONS ---------------
            for nextv in set(self.graph[vertex]) - set(path):
                if (nextv not in self.inc_nodes) or (i < self.k):  # допустимость по условию VMRk
                    # ---------------- ORIGINAL ----------------
                    if nextv == self.goal:
                        path.path += [nextv]
                        path.i = i
                        paths.append(path)
                    else:
                        path.path += [nextv]
                        path.i = i
                        stack.append((nextv, path))
        return paths

class MNRkCalculator(BaseCalculator):
    def __init__(self, graph: dict, start: str, goal: str, inc_nodes: list, dec_nodes: list, k: int):
        BaseCalculator.__init__(self, graph, start, goal)

        self.inc_nodes = inc_nodes
        self.dec_nodes = dec_nodes
        self.k = k

    def calculate(self) -> PathCollection:
        """
        DMP - Поиск путей вгулбину в графе с магнитной достижимостью
        MNRk путь порядка k - на котором к концу пути значение магнитности равно k.
        Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
        Возвращает список путей.
        Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
        Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
        Если dec_nodes пустой, то dec_nodes становятся все вершины графа, кроме inc_nodes.
        """
        paths = PathCollection([])

        i = 0  # счетчик запрщенных вершин

        if not self.dec_nodes:
            self.dec_nodes = list(set(self.graph) - set(self.inc_nodes))

        stack = [(self.start, Path([self.start]), i)]
        while stack:
            (vertex, path, i) = stack.pop()  # print(' = ' + str())
            # --------------- CONDITIONS ---------------
            if vertex in self.inc_nodes:
                i += 1
            elif vertex in self.dec_nodes:
                i -= 1
            # --------------- CONDITIONS ---------------
            for nextv in set(self.graph[vertex]) - set(path):
                # ---------------- ORIGINAL ----------------
                if nextv == self.goal:
                    if nextv in self.inc_nodes:
                        i += 1
                    elif nextv in self.dec_nodes:
                        i -= 1
                    if i == self.k:
                        paths.append(path + [nextv])

                else:
                    stack.append((nextv, path + [nextv], i))
                # ---------------- ORIGINAL ----------------
        return paths

class BaseTelNetCalculator(BaseCalculator):
    def __init__(self, graph: dict, start: str, goal: str, mass: float):
        BaseCalculator.__init__(self, graph, start, goal)

        self.mass = mass

    def calculate(self) -> TNPathCollection:
        """
        DPTN — Поиск вглубину всех путей в обычном взвешенном графе, функция выводит быстрейший путь из start в goal
        Функция ищет простой путь в обычном взвешенном графе с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
        Возвращает путь - упорядоченное множество вершин.
        Параметр check отвечает за режим работы функции. Если check == 0, то она возвращает быстрейший путь.
        Если check == 1, то она возвращает массив всех возможных путей.
        """

        paths = TNPathCollection([])  # массив правильных путей и их длительностей
        # m = 200                     # размер (масса) Пакета Виртуального Вызова - 2 мбита
        t = 0  # время прохождения по пути, t = m / v
        stack = [(self.start, TNPath([self.start], t))]

        while stack:

            spop = stack.pop()  # верхний элемент стэка
            vertex = spop[0]
            path = spop[1].path
            t = spop[1].time
            for nextv in set(self.graph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
                # ---------------- ORIGINAL START ----------
                if nextv == self.goal:
                    v = self.graph[vertex][nextv]
                    t += self.mass / v
                    paths.append(TNPath(path + [nextv], t))  # вместо yield
                    t -= self.mass / v  # otherwise time is COLLAPSING
                else:
                    v = self.graph[vertex][nextv]
                    t += self.mass / v
                    stack.append((nextv, TNPath(path + [nextv], t)))
                    t -= self.mass / v
                # ---------------- ORIGINAL END ------------
        return paths

class VMRkTelNetCalculator(BaseTelNetCalculator, VMRkCalculator):
    def __init__(self, graph: dict, start: str, goal: str, inc_nodes: list, k: int, mass: float):
        BaseTelNetCalculator.__init__(self, graph, start, goal, mass)
        VMRkCalculator.__init__(self, graph, start, goal, inc_nodes, k)


    def calculate(self) -> TNPathCollection:
        """
        DVPTN — Поиск вглубину всех путей во взвешенном графе типа VMRk, функция выводит быстрейший путь из start в goal
        Функция ищет VMRk путь с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
        Возвращает массив всех возможных путей.
        """
        paths = TNMPathCollection([])  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
        i = 0  # счетчик запрещенных вершин
        t = 0  # время прохождения по пути, t = m / v
        stack = [(self.start, TNMPath([self.start], i, t))]

        while stack:

            spop = stack.pop()  # spop = (vertex, {path : t}, i)
            vertex = spop[0]
            path = spop[1].path
            t = spop[1].time
            i = spop[1].i
            # --------------- CONDITIONS START --------
            if vertex in self.inc_nodes:
                i += 1
            else:
                i = 0
            # --------------- CONDITIONS END ----------
            for nextv in set(self.graph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
                if (nextv not in self.inc_nodes) or (i < self.k):  # допустимость по условию VMRk
                    # ---------------- ORIGINAL START ----------
                    if nextv == self.goal:
                        v = self.graph[vertex][nextv]
                        t += self.mass / v

                        paths.append(TNMPath(path + [nextv], i, t))  # вместо yield
                        t -= self.mass / v  # otherwise time is COLLAPSING
                    else:
                        v = self.graph[vertex][nextv]
                        t += self.mass / v
                        stack.append((nextv, TNMPath(path + [nextv], i, t)))
                        t -= self.mass / v
                # ---------------- ORIGINAL END ------------
        return paths

class MNRkTelNetCalculator(BaseTelNetCalculator, MNRkCalculator):
    def __init__(self, graph: dict, start: str, goal: str, inc_nodes: list, dec_nodes: list, k: int, mass: float):
        BaseTelNetCalculator.__init__(self, graph, start, goal, mass)
        MNRkCalculator.__init__(self, graph, start, goal, inc_nodes, dec_nodes, k)


    def calculate(self) -> TNPathCollection:
        """
        DMPTN - Поиск вглубину всех путей во взвешенном графе с магнитной достижимостью, функция выводит быстрейший путь из start в goal
        Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
        Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
        Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
        Параметр check отвечает за режим работы функции.
        Функция вернет пути, соответствующие заданному порядку k.
        """
        if not self.dec_nodes:
            self.dec_nodes = list(set(self.graph) - set(self.inc_nodes))

        paths = TNPathCollection([])  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
        i = 0  # счетчик запрещенных вершин
        # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
        t = 0  # время прохождения по пути, t = m / v
        stack = [(self.start, TNPath([self.start], t), i)]
        while stack:
            spop = stack.pop()  # spop = (vertex, {path : t}, i)
            vertex = spop[0]
            path = spop[1].path
            t = spop[1].time
            i = spop[2]
            # --------------- CONDITIONS ---------------
            if vertex in self.inc_nodes:
                i += 1
            elif vertex in self.dec_nodes:
                i -= 1
            # --------------- CONDITIONS ---------------
            for nextv in set(self.graph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
                if nextv == self.goal:
                    if nextv in self.inc_nodes:
                        i += 1
                    elif nextv in self.dec_nodes:
                        i -= 1
                    if i == self.k:
                        v = self.graph[vertex][nextv]
                        t += self.mass / v
                        paths.append(TNPath(path + [nextv], t))  # вместо yield
                        t -= self.mass / v
                else:
                    v = self.graph[vertex][nextv]
                    t += self.mass / v
                    stack.append((nextv, TNPath(path + [nextv], t), i))
                    t -= self.mass / v

        return paths

    def calculate_total(self):
        """
        DMPTN - Поиск вглубину всех путей во взвешенном графе с магнитной достижимостью, функция выводит быстрейший путь из start в goal
        Функция ищет пути от вершины start до goal, удовлетворяющие магнтиности порядка k.
        Параметр inc_nodes принимает множество увеличивающих магнтиность вершин.
        Параметр dec_nodes принимает множество уменьшающих магнтиность вершин.
        Функция вернет все возможные пути из start в goal с их порядками магнитности

        """
        if not self.dec_nodes:
            self.dec_nodes = list(set(self.graph) - set(self.inc_nodes))

        paths = TNMPathCollection([])
        i = 0  # счетчик запрещенных вершин

        t = 0  # время прохождения по пути, t = m / v
        stack = [(self.start, TNMPath([self.start], i, t))]
        while stack:
            spop = stack.pop()  # spop = (vertex, {path : t}, i)
            vertex = spop[0]
            path = spop[1].path
            t = spop[1].time
            i = spop[1].i
            # --------------- CONDITIONS ---------------
            if vertex in self.inc_nodes:
                i += 1
            elif vertex in self.dec_nodes:
                i -= 1
            # --------------- CONDITIONS ---------------
            for nextv in set(self.graph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
                if nextv == self.goal:
                    if nextv in self.inc_nodes:
                        i += 1
                    elif nextv in self.dec_nodes:
                        i -= 1

                    v = self.graph[vertex][nextv]
                    t += self.mass / v
                    paths.append(TNMPath(path + [nextv], i, t))  # вместо yield
                    t -= self.mass / v
                else:
                    v = self.graph[vertex][nextv]
                    t += self.mass / v
                    stack.append((nextv, TNMPath(path + [nextv], i, t)))
                    t -= self.mass / v

        return paths
