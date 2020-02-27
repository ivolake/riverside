from abc import ABC
import os


class BaseGraph(ABC):

    def __init__(self, config):
        self.config = config
        self.type = config.get('graph_type')
        self.struct = self.extract_graph(config.get('graph_path'))

        self.nodes = self.get_nodes(self.struct)
        self.edges = self.get_edges(self.struct)

        # self.oriented = ???

    def __repr__(self):
        pass

    def get_struct(self):
        pass

    def extract_graph(self, name):
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
        # CHECKING THE EXISTENCE
        if os.path.isfile(os.getcwd() + '/' + name):
            # пробуем найти в текущей директории
            path = os.getcwd() + '/' + name

        elif os.path.isfile(os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname):
            # пробуем найти на рабочем столе
            path = os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname
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
        vertexes = eval('[' + lines[0][2:-1] + ']')
        for line in lines[1:]:
            matrix.append(eval('[' + line[1:][2:-1] + ']'))
        g = dict()
        for i in range(0, len(matrix)):
            neighbours = dict()
            for j in range(0, len(matrix[i])):
                if matrix[i][j] not in [0, 1]:
                    is_weighted = True
                if (matrix[i][j] != 0) & (i != j):
                    neighbours.update({str(vertexes[j]): matrix[i][j]})
            g.update({str(vertexes[i]): neighbours})
        return g
        
    def get_nodes(self):
        pass

    def get_edges(self):
        pass

