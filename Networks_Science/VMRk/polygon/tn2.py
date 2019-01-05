from pandas import read_csv, read_excel
import os

def show_dict(d):
    print('{ ')
    for v in d.keys():
        print('{0} : {1}'.format(v, d[v]))
    print(' }')

def generate_separate_graph_and_weights(g):
    '''
    Функция для взвешенных графов, которая рабивает такой граф на невзвешенный граф и словарь с ребрами и их весами
    Пример:
        Входные данные:

        g = {'1': {'2':45, '3':40},
             '2': {'4':15, '9':35},
             '3': {'5':45},
             '4': {'6':20},
             '5': {'6':10, '7':25},
             '6': {'8':40},
             '7': {'9':30},
             '8': {'3':50, '7':35, '10':5},
             '9': {'10':25},
             '10':{}}

        Выходные данные:

        (new_g, edges_with_labels)
        new_g = {'1': ['2', '3'],
                 '2': ['4', '9'],
                 '3': ['5'],
                 '4': ['6'],
                 '5': ['6', '7'],
                 '6': ['8'],
                 '7': ['9'],
                 '8': ['3', '7', '10'],
                 '9': ['10'],
                 '10': []}

        edges_with_labels = {('1', '2'): '45',
                             ('1', '3'): '40',
                             ('2', '4'): '15',
                             ('2', '9'): '35',
                             ('3', '5'): '45',
                             ('4', '6'): '20',
                             ('5', '6'): '10',
                             ('5', '7'): '25',
                             ('6', '8'): '40',
                             ('7', '9'): '30',
                             ('8', '3'): '50',
                             ('8', '7'): '35',
                             ('8', '10'): '5',
                             ('9', '10'): '25'}

    '''

    new_g = dict()                         # новый граф без весов в стандартном виде
    edges_with_labels = dict()             # отдельный словарь для весов {('1','2') : weight1, ('3','4') : weight2}
    for vi in list(g.keys()):              # иду по вершинам графа. vi - текушая вершина
        neighbours = []
        for vj in list(g[vi].keys()):      # иду по соседям vi
            neighbours.append(vj)
            edges_with_labels.update({(vi,vj) : str(g[vi][vj])})

        new_g.update({vi:neighbours})

    return((new_g, edges_with_labels))

def extract(fname):
    '''
    Функция считывает граф, заданный матрицей смежности, из файла. Допустимые типы файлов: .txt, .csv, .xls и .xlsx.
    В аргументе функции - путь до файла. Если файл лежит в той же директории,
    что и вызываемая программа, или на рабочем столе компьютера, можно указать просто название файла.
    Названия требуется указать с расширением.
    Возвращаемые данные - граф.
    Пример:

    digraph = extract('d1.txt')
    '''
    if os.path.isfile(os.getcwd() + '/' + fname):
        # пробуем найти в текущей директории
        fpath = os.getcwd() + '/' + fname

    elif os.path.isfile(os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname):
        # пробуем найти на рабочем столе
        fpath = os.getcwd()[:os.getcwd().find(u'Documents\\')] + 'Desktop/' + fname
        # Почему разные слэши?
        # Потому что функция find() ищет в строке, которая создана обработчиком Windows, и там разделители директорий - \
        # А строку, которую прибавляю я ('Desktop/test1.txt'), обрабатывает Python-овский обработчик, и для него разделитель директорий - /

    elif os.path.isfile(fname):
        fpath = fname

    else:
        print('File not found.')
        exit()


    enh = fpath[fpath.rfind('.'):len(fpath)]
    # print(enh)
    g = dict()
    is_weighted = False # Является ли взвешенным. Изначально считается, что нет
                        # Если в матрице встретятся иные, чем 0 и 1, числа, то он определится как взвешенный и не будет преобразован.
                        # Если встретятся только 0 и 1, то он будет преобразован.
    if (enh == '.csv') | (enh == '.txt'):
        g_df = read_csv(fpath, header = 0, index_col = 0, sep = ', ', engine = 'python') # print(g_df.loc[2, '1'])

    elif (enh == '.xls') | (enh == '.xlsx'):
        g_df = read_excel(fpath, engine = 'python') # print(g_df.loc[2, 1])

    print(g_df)

    for i in range(0,len(g_df.index)):
        neighbours = dict()

        for j in range(0,len(g_df.columns)):
            if g_df.loc[g_df.index[i], g_df.columns[j]] not in [0,1]:
                is_weighted = True

            if (g_df.loc[g_df.index[i], g_df.columns[j]] != 0) & (i != j):
                neighbours.update({str(g_df.index[j]) : g_df.loc[g_df.index[i], g_df.columns[j]]})

        g.update({str(g_df.columns[i]) : neighbours})

    if not is_weighted:
        (g, shit) = generate_separate_graph_and_weights(g) # shit is shit

    # show_dict(g)
    return g


g = extract(input())
show_dict(g)
# file_path = os.getcwd() + '/' + 'test1.txt'  #input()
# g_df = read_csv(file_path, header = 0, index_col = 0, sep = ', ')
# print(g_df)
# print(g_df.index)
# print(g_df.columns)
# print()



# print(g_df.columns[2])
# print(g_df.info())
