import networkx as nx
import matplotlib.pyplot as plt

digraph1 = {'A': ['B', 'C'],
           'B': ['A', 'D', 'C'],
           'C': ['A', 'B', 'F', 'D'],
           'D': ['B','C'],
           'E': ['F'],
           'F': ['C', 'E','G'],
           'G': []}

digraph2 = {'A': ['B', 'C'],
           'B': ['A', 'D', 'C'],
           'C': ['A', 'B', 'F', 'D'],
           'D': ['B','C'],
           'E': ['F','G'],
           'F': ['C', 'E','F','G'],
           'G': ['H'],
           'H': []}

digraph = digraph2

D = nx.DiGraph(digraph)

def generate_pos(g):
    positions = dict()
    V = list(g.keys())
    l_V = len(V)
    x = 0
    y = 2
    positions.update({V[0]: [x, y]})

    if (l_V % 2 != 0): # если количество вершин нечетно то:
        p = 1
    else:
        p = 0

    for i in range(1, l_V - p):
        positions.update({V[i]: [x + ((i+1) // 2), y + (2 if (i % 2 == 1) else (-2)) ]}) # если i четный, то прибавляем -2, нечетный -- +2

    if (p == 1):
        positions.update({V[l_V-2]: [x + l_V // 2, y]})
        positions.update({V[l_V-1]: [x + l_V // 2 + 1, y]})
    else:
        positions.update({V[l_V-1]: [x + l_V // 2 + 1, y]})

    return positions


pos = generate_pos(digraph)

print(pos)



nx.draw(D, pos = pos, with_labels=True, font_weight='bold')
plt.axis('on')
plt.show()
