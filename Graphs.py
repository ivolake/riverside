import os

import additions as adds
from Calculators import BaseCalculator, VMRkCalculator, MNRkCalculator, BaseTelNetCalculator, VMRkTelNetCalculator, \
    MNRkTelNetCalculator
from Drawers import BaseDrawer
from Paths import PathCollection, MPathCollection


class BaseGraph:

    def __init__(self, config):
        self.config = config
        self.type = config.get('type')
        self._graph_path = self.config.get('path')

        self.__edges = None
        self.__nodes = None
        self.__struct, self.__weighted = self._extract_graph(self._graph_path, self.type)


    def __repr__(self):
        return f'BaseGraph(type={self.type}, nodes={self.nodes}, weighted={self.weighted})'

    @property
    def struct(self):
        return self.__struct
    
    @struct.setter
    def struct(self, value):
        self.__struct = value

    @property
    def edges(self):
        """
        Если не взвешенный граф, то это список вида list[v_i, v_j].
        Если взвешенный граф, то это словарь вида dict[(v_i, v_j): w].
        Здесь v_i, v_j - названия вершин.
        Returns
        -------
        list or dict
        """
        self.__edges = adds.get_edges(self.__struct, self.__weighted)
        return self.__edges

    # @edges.setter
    # def edges(self, edges):
    #     self._edges = edges

    @property
    def nodes(self):
        self.__nodes = list(self.__struct.keys())
        return self.__nodes

    # @nodes.setter
    # def nodes(self, nodes):
    #     self._nodes = nodes

    @property
    def weighted(self):
        # if self.type in ['standard', 'vmrk', 'mnrk']:
        #     self._weighted = False
        # elif self.type in ['telnet', 'vmrk_telnet', 'mnrk_telnet', 'vmrk_tb_telnet']:
        #     self._weighted = False
        # else:
        #     self._weighted = None
        #     print(f'Тип графа неизвестен: {self.type}')
        return self.__weighted

    # @weighted.setter
    # def weighted(self, value):
    #     self.__weighted = value

    @property
    def drawer(self):
        return BaseDrawer(graph=self)

    @property
    def calculator(self):
        return BaseCalculator(graph=self.struct)


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
        nodes = eval('[' + lines[0][1:-1] + ']')
        for line in lines[1:]:
            matrix.append(eval('[' + line[line.index(',')+1:] + ']'))
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

        if graph_type in ['standard', 'vmrk', 'mnrk'] and weighted:
            print(
                'В файле содержится взвешенный граф, но указанный тип подразумевает отсутствие весов на графе. Граф будет считан, как невзвешанный')
            g = adds.deweight(g)
            weighted = False
        elif graph_type in ['standard', 'vmrk', 'mnrk'] and not weighted:
            g = adds.deweight(g)
            weighted = False
        elif graph_type not in ['standard', 'vmrk', 'mnrk'] and not weighted:
            print(
                'В файле содержится невзвешенный граф, но указанный тип подразумевает наличие весов у графа. Граф будет считан, как невзвешанный')

        return g, weighted

    def calculate(self,
                  start: str,
                  goal: str,
                  **kwargs) -> PathCollection:
        return self.calculator.calculate(start=start, goal=goal, **kwargs)

    def calculate_total(self,
                        start: str,
                        goal: str,
                        **kwargs) -> MPathCollection:
        return self.calculator.calculate_total(start=start, goal=goal, **kwargs)

    def draw_graph(self,
                   file_name: str = None,
                   ipos: int = 1,
                   show: bool = True) -> None:
        self.drawer.draw_graph(file_name=file_name, ipos=ipos, show=show)

    def draw_graph_with_paths(self,
                              paths: PathCollection,
                              file_name: str = None,
                              ipos: int = 1,
                              show: bool = True,
                              **kwargs) -> None:
        self.drawer.draw_graph_with_paths(paths=paths, file_name=file_name, ipos=ipos, show=show, **kwargs)

    def draw_graph_with_tb_nodes(self,
                                 tb_params: dict,
                                 file_name: str = None,
                                 ipos: int = 1,
                                 show: bool = True,
                                 **kwargs) -> None:
        self.drawer.draw_graph_with_tb_nodes(tb_params=tb_params, file_name=file_name, ipos=ipos, show=show, **kwargs)

    def draw_graph_with_tb_nodes_and_paths(self,
                                           paths: PathCollection,
                                           tb_params: dict,
                                           file_name: str = None,
                                           ipos: int = 1,
                                           show: bool = True,
                                           **kwargs) -> None:
        self.drawer.draw_graph_with_tb_nodes_and_paths(paths=paths, tb_params=tb_params, file_name=file_name, ipos=ipos, show=show, **kwargs)


class VMRkGraph(BaseGraph):

    def __init__(self, config):
        BaseGraph.__init__(self, config)

        self.inc_nodes = config.get('options').get('inc_nodes')
        self.inc_nodes = list(map(str, self.inc_nodes))

    @property
    def calculator(self):
        return VMRkCalculator(graph=self.struct, inc_nodes=self.inc_nodes)

    def __repr__(self):
        return f'VMRkGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, weighted={self.weighted})'


    def get_total_magnitudes_distribution(self):
        total_mc = adds.FineDict()
        for s in self.nodes:
            for g in self.nodes:
                paths = self.calculate_total(start=s, goal=g)
                p_mc = paths.get_magnitudes_counts()
                for k in p_mc:
                    if k not in total_mc.keys():
                        total_mc.update({k: 0})
                    else:
                        total_mc[k] += 1
        return total_mc


class MNRkGraph(BaseGraph):

    def __init__(self, config):
        BaseGraph.__init__(self, config)

        self.inc_nodes = config.get('options').get('inc_nodes')
        self.inc_nodes = list(map(str, self.inc_nodes))
        self.dec_nodes = config.get('options').get('dec_nodes')
        self.dec_nodes = list(map(str, self.dec_nodes))

    @property
    def calculator(self):
        return MNRkCalculator(graph=self.struct, inc_nodes=self.inc_nodes, dec_nodes=self.dec_nodes)

    def __repr__(self):
        return f'MNRkGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, dec_nodes={self.dec_nodes}, weighted={self.weighted})'


    def get_total_magnitudes_distribution(self):
        total_mc = adds.FineDict()
        for s in self.nodes:
            for g in self.nodes:
                paths = self.calculate_total(start=s, goal=g)
                p_mc = paths.get_magnitudes_counts()
                for k in p_mc:
                    if k not in total_mc.keys():
                        total_mc.update({k: 0})
                    else:
                        total_mc[k] += 1
        return total_mc


class BaseTelNet(BaseGraph):

    def __init__(self, config):
        BaseGraph.__init__(self, config)

    @property
    def calculator(self):
        return BaseTelNetCalculator(graph=self.struct)

    @property
    def weights(self):
        return list(map(float, self.edges.values()))

    def __repr__(self):
        return f'BaseTelNetGraph(type={self.type}, nodes={self.nodes}, weighted={self.weighted})'


class VMRkTelNet(BaseTelNet, VMRkGraph):

    def __init__(self, config):
        BaseTelNet.__init__(self, config)
        VMRkGraph.__init__(self, config)

    @property
    def calculator(self):
        return VMRkTelNetCalculator(graph=self.struct, inc_nodes=self.inc_nodes)

    def __repr__(self):
        return f'VMRkTelNetGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, weighted={self.weighted})'


class MNRkTelNet(BaseTelNet, MNRkGraph):

    def __init__(self, config):
        BaseTelNet.__init__(self, config)
        MNRkGraph.__init__(self, config)

    @property
    def calculator(self):
        return MNRkTelNetCalculator(graph=self.struct, inc_nodes=self.inc_nodes, dec_nodes=self.dec_nodes)

    def __repr__(self):
        return f'MNRkTelNetGraph(type={self.type}, nodes={self.nodes}, inc_nodes={self.inc_nodes}, dec_nodes={self.dec_nodes}, weighted={self.weighted})'
