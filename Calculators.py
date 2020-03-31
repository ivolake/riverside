from collections import Generator, Iterable

from Graphs import BaseGraph
from Paths import PathCollection, Path, TNPath, TNPathCollection


class BaseCalculator:
    def __init__(self, graph: BaseGraph, start: str, goal: str):
        self.graph = graph.get_struct()
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

class BaseTelnetCalculator(BaseCalculator):
    def __init__(self, graph: BaseGraph, start: str, goal: str, mass: float):
        super().__init__(graph, start, goal)

        self.mass = mass

    def calculate(self) -> PathCollection:
        '''
        DVPTN — Поиск вглубину всех путей в обычном взвешенном графе, функция выводит быстрейший путь из start в goal
        Функция ищет простой путь в обычном взвешенном графе с наименьшим временем передачи Пакета Виртуального Вызова от вершины start до goal.
        Возвращает путь - упорядоченное множество вершин.
        Параметр check отвечает за режим работы функции. Если check == 0, то она возвращает быстрейший путь.
        Если check == 1, то она возвращает массив всех возможных путей.
        '''

        # TODO: Внедрить класс Path в эту и последующую фукнции
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


