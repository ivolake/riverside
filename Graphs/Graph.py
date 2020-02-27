from abc import ABC
import os

import functions as func

class BaseGraph(ABC):

    def __init__(self, config):
        self.config = config
        self.type = config.get('graph_type')

        self.weighted = False
        self.struct = self._extract_graph(config.get('graph_path'))

        self.nodes = self.get_nodes()
        self.edges = self.get_edges()


    def __repr__(self):
        return f'Graph(type={self.type}, nodes={self.nodes}, weighted={self.weighted})'

    def get_struct(self):
        return self.struct

    def _extract_graph(self, name):
        """
            Если info = False (по умолчанию)
            Функция считывает граф, заданный матрицей смежности, из файла. Допустимые типы файлов: .txt, .csv, .xls и .xlsx.
            В аргументе функции - путь до файла. Если файл лежит в той же директории,
            что и вызываемая программа, или на рабочем столе компьютера, можно указать просто название файла.
            Названия требуется указать с расширением.
            Возвращаемые данные - граф.
            Пример:

            digraph = extract('d1.txt')

            Если info = True
            Функция дополнительно считывает inc_nodes и dec_nodes из файла %fname%_info.txt
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
        self.nodes = eval('[' + lines[0][2:-1] + ']')
        for line in lines[1:]:
            matrix.append(eval('[' + line[1:][2:-1] + ']'))
        g = dict()
        for i in range(0, len(matrix)):
            neighbours = dict()
            for j in range(0, len(matrix[i])):
                if matrix[i][j] not in [0, 1]:
                    self.weighted = True
                if (matrix[i][j] != 0) & (i != j):
                    neighbours.update({str(self.nodes[j]): matrix[i][j]})
            g.update({str(self.nodes[i]): neighbours})

        if not self.weighted:
            (self.struct, self.edges) = func.generate_separate_graph_and_weights(g)  # shit is shit

        return g
        
    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

