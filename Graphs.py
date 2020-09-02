import os

import functions as func
from Calculators import BaseCalculator, VMRkCalculator, MNRkCalculator, BaseTelnetCalculator, VMRkTelNetCalculator, \
    MNRkTelNetCalculator
from Paths import PathCollection, TNPathCollection


class BaseGraph:

    def __init__(self, config):
        self.config = config
        self.type = config.get('type')

        self._edges = None
        self._nodes = None
        self._struct, self._weighted = self._extract_graph(self.config.get('path'), self.type)

    @property
    def struct(self):
        return self._struct
    
    @struct.setter
    def struct(self, struct):
        self._struct = struct

    @property
    def edges(self):
        self._edges = func.get_edges(self._struct, self._weighted)
        return self._edges

    # @edges.setter
    # def edges(self, edges):
    #     self._edges = edges

    @property
    def nodes(self):
        self._nodes = list(self._struct.keys())
        return self._nodes

    # @nodes.setter
    # def nodes(self, nodes):
    #     self._nodes = nodes

    @property
    def weighted(self):
        # if self.type in ['simple', 'vmrk', 'mnrk']:
        #     self._weighted = False
        # elif self.type in ['telnet', 'vmrk_telnet', 'mnrk_telnet', 'vmrk_tb_telnet']:
        #     self._weighted = False
        # else:
        #     self._weighted = None
        #     print(f'Тип графа неизвестен: {self.type}')
        return self._weighted

    @weighted.setter
    def weighted(self, weighted):
        self._weighted = weighted



    def __repr__(self):
        return f'BaseGraph(type={self.type}, nodes={self.nodes}, weighted={self.weighted})'

    @staticmethod
    def _extract_graph(name, graph_type):
        """
            Функция считывает граф, заданный матрицей смежности, из файла. Допустимые типы файлов: .txt, .csv, .xls и .xlsx.
            В аргументе функции - путь до файла. Если файл лежит в той же директории,
            что и вызываемая программа, или на рабочем столе компьютера, можно указать просто название файла.
            Названия требуется указать с расширением.
            Возвращаемые данные - граф.
        """
        # Проверка существования файла
        if os.path.isfile(os.getcwd() + '/' + name):
            # пробуем найти в текущей директории
            path = os.getcwd() + '/' + name

        elif os.path.isfile(os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + name):
            # пробуем найти на рабочем столе
            path = os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + name
            # Почему разные слэши?
            # Потому что функция find() ищет в строке, которая создана обработчиком Windows, и там разделители директорий - \
            # А строку, которую прибавляю я ('Desktop/test1.txt'), обрабатывает Python-овский обработчик, и для него разделитель директорий - /

        elif os.path.isfile(name):
            path = name
        else:
            raise FileNotFoundError(name)

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            f.close()
        matrix = []
        nodes = eval('[' + lines[0][2:-1] + ']')
        for line in lines[1:]:
            matrix.append(eval('[' + line[1:][2:-1] + ']'))
        g = dict()
        weighted = False
        for i in range(0, len(matrix)):
            neighbours = dict()
            for j in range(0, len(matrix[i])):
                if matrix[i][j] not in [0, 1]:
                    weighted = True
                if (matrix[i][j] != 0) & (i != j):
                    neighbours.update({str(nodes[j]): matrix[i][j]})
            g.update({str(nodes[i]): neighbours})

        if graph_type in ['simple', 'vmrk', 'mnrk'] and weighted:
            print('В файле содержится взвешенный граф, но указанный тип подразумевает отсутствие весов на графе. Граф будет считан, как невзвешанный')
            g = func.deweight(g)
            weighted = False
        elif graph_type in ['simple', 'vmrk', 'mnrk'] and not weighted:
            g = func.deweight(g)
            weighted = False
        elif graph_type not in ['simple', 'vmrk', 'mnrk'] and not weighted:
            print('В файле содержится невзвешенный граф, но указанный тип подразумевает наличие весов у графа. Граф будет считан, как невзвешанный')

        return g, weighted

    def calculate(self, start: str, goal: str) -> PathCollection:
        return BaseCalculator(self.struct, start, goal).calculate()

class VMRkGraph(BaseGraph):

    def __init__(self, config):
        super().__init__(config)

        self.inc_nodes = config.get('options').get('inc_nodes')

    def __repr__(self):
        return f'VMRkGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, weighted={self.weighted})'

    def calculate(self, start: str, goal: str, k: int) -> PathCollection:
        return VMRkCalculator(self.struct, start, goal, self.inc_nodes, k).calculate()

class MNRkGraph(BaseGraph):

    def __init__(self, config):
        super().__init__(config)

        self.inc_nodes = config.get('options').get('inc_nodes')
        self.dec_nodes = config.get('options').get('dec_nodes')

    def __repr__(self):
        return f'MNRkGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, dec_nodes={self.dec_nodes}, weighted={self.weighted})'

    def calculate(self, start: str, goal: str, k: int) -> PathCollection:
        return MNRkCalculator(self.struct, start, goal, self.inc_nodes, self.dec_nodes, k).calculate()

class BaseTelNet(BaseGraph):

    def __init__(self, config):
        super().__init__(config)

    def __repr__(self):
        return f'BaseTelNetGraph(type={self.type}, nodes={self.nodes}, weighted={self.weighted})'

    @property
    def weights(self):
        return list(map(float, self.edges.values()))

    def calculate(self, start: str, goal: str, mass: float) -> TNPathCollection:
        return BaseTelnetCalculator(self.struct, start, goal, mass).calculate()

class VMRkTelNet(BaseTelNet):

    def __init__(self, config):
        super().__init__(config)

        self.inc_nodes = config.get('options').get('inc_nodes')

    def __repr__(self):
        return f'VMRkTelNetGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, weighted={self.weighted})'

    def calculate(self, start: str, goal: str, k: int) -> PathCollection:
        return VMRkTelNetCalculator(self.struct, start, goal, self.inc_nodes, k, mass).calculate()

class MNRkTelNet(BaseTelNet):

    def __init__(self, config):
        super().__init__(config)

        self.inc_nodes = config.get('options').get('inc_nodes')

    def __repr__(self):
        return f'VMRkTelNetGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, weighted={self.weighted})'

    def calculate(self, start: str, goal: str, k: int, mass: float) -> PathCollection:
        return MNRkTelNetCalculator(self.struct, start, goal, self.inc_nodes, self.dec_nodes, k, mass).calculate()

# TODO: сделать отдельные атрибуты калькуляторов в классах графов
