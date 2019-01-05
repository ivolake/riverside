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

digraph = digraph1

def generate_pos(g):
    positions = dict()
    V = list(g.keys())
    print('V: ' + str(V))
    l_V = len(V)
    print('l_v: ' + str(l_V))
    x = 0
    y = 2
    positions.update({V[0]: [x, y]})
    print('positions: ' + str(positions))

    if (l_V % 2 != 0): # если количество вершин нечетно то:
        p = 1
        print('p: '+str(p))
    else:
        p = 0
        print('p: '+str(p))

    for i in range(1, l_V - p):
        positions.update({V[i]: [x + ((i+1) // 2), y + (2 if (i % 2 == 1) else (-2)) ]}) # если i четный, то прибавляем -2, нечетный -- +2
        print('i: '+str(i)+ '\npositions: '+ str(positions))

    if (p == 1):
        positions.update({V[l_V-2]: [x + l_V // 2, y]})
        positions.update({V[l_V-1]: [x + l_V // 2 + 1, y]})
        print('p: '+str(p)+ '\npositions: '+ str(positions))

    else:
        positions.update({V[l_V-1]: [x + l_V // 2 + 1, y]})
        print('p: '+str(p)+ '\npositions: '+ str(positions))

    return positions


pos_ = generate_pos(digraph)

print(pos_)










# from graphviz import Digraph
# A = Digraph(name = 'Strange things', comment='The Round Table')
# A.node('A', 'King Arthur')
# A.node('B')
# A.node('L', 'Sir Lancelot the Brave')
# A.node('C')
#
# A.edges(['AB', 'AL'])
# A.edge('B', 'L', constraint='false')
# A.edge('B','C',label = 'BC__',constraint = 'true')
# print(A.source)
# A.render(r'test_output\table.gv',view = True)
