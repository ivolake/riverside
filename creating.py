import os

import pandas as pd

def create_graph(file_path: str,
                 type: str,
                 nodes: list,
                 edges: [list, dict]):
    g_df = pd.DataFrame(index=nodes, columns=nodes)
    for n_i in nodes:
        for n_j in nodes:
            if (n_i, n_j) in edges:
                if type == 'non-weighted':
                    g_df.loc[n_i][n_j] = 1
                elif type == 'weighted':
                    g_df.loc[n_i][n_j] = edges.get((n_i, n_j), 0)
                else:
                    raise Exception('Указан неверный тип графа.')
    g_df.to_csv(os.path.abspath(file_path), sep=',')

def create_config():
    # TODO:
    #  Реализовать эту функцию
    """
    Функция, которая будет создавать конфигурационный файл по вводу пользователя
    :return:
    """
    ...
def create_traffic():
    # TODO:
    #  Реализовать эту функцию
    """
    Функция, которая будет создавать файл трафика по вводу пользователя
    :return:
    """
    ...