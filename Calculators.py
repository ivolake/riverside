from collections import Generator, Iterable

from Graph import BaseGraph
from Paths import PathCollection, Path, TNPath, TNPathCollection


class BaseCalculator:
    def __init__(self, graph: BaseGraph, start: str, goal: str):
        self.graph = graph.get_struct()
        self.start = start
        self.goal = goal

    def calculate(self) -> Generator:
        """
        Поиск с помощью DFS.
        Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
        Функция ищет все доступные пути от вершины start до goal
        Возвращает генератор путей.
        """
        paths = []
        # TODO: Внедрить класс Path в эту и последующую фукнции
        stack = [(self.start, [self.start])]  # stack - список кортежей (вершина, путь) - (vertex, path)
        while stack:  # проход по всем элементам списка stack, пока stack не станет пустым
            (vertex, path) = stack.pop()  # pop() забирает (удаляет) из списка последний элемент и кладет в (vertex, path)
            for next in set(self.graph[vertex]) - set(path):  # проход переменной next по множеству A\B, где A - множество соседей вершины vertex,
                # а B - множество вершин, входящих в путь до goal. То есть результирующее множество
                # (по которому идет next) - это соседи минус вершины, включенные в путь
                if next == self.goal:  # если next это goal
                    yield path + [next]  # то добавляем в возвращаемый генератор еще один путь + последняя вершина - goal.
                else:  # если next != goal
                    # добавляем в stack кортеж ()
                    stack.append((next, path + [next]))

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
        yield_stack = []  # массив кортежей правильных путей и их длительностей (путь, время пути) всех итоговых путей
        # m = 200                       # размер (масса) Пакета Виртуального Вызова - 2 мбита
        t = 0  # время прохождения по пути, t = m / v
        stack = [(self.start, ([self.start], t))]

        while stack:

            spop = stack.pop()  # spop = (vertex, {path : t}, i)
            vertex = spop[0]
            path = spop[1][0]
            t = spop[1][1]
            for next in set(self.graph[vertex]) - set(path):  # set({a : b, c : d}) == {a,c}
                # ---------------- ORIGINAL START ----------
                if next == self.goal:
                    v = self.graph[vertex][next]
                    t += self.mass / v
                    yield (path + [next], t)  # вместо yield
                    t -= self.mass / v  # otherwise time is COLLAPSING
                else:
                    v = self.graph[vertex][next]
                    t += self.mass / v
                    stack.append((next, (path + [next], t)))
                    t -= self.mass / v
                # ---------------- ORIGINAL END ------------
        return yield_stack

    def calculate_fastest(self, paths: Generator = None) -> Path:
        if paths is None:
            paths = list(self.calculate())
        fastest_path = ([], 0)
        tmin = 100000  # 27,7 часов
        # ipath = 0
        for _path_ in paths:
            if _path_[1] <= tmin:
                tmin = _path_[1]
                fastest_path = _path_
        return fastest_path


