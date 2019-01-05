import matplotlib.pyplot as plt
import networkx as nx
# cd Documents\Python_Scripts\Networks_Science


graph1 = {'A': ['B', 'C'],
         'B': ['A', 'D', 'E'],
         'C': ['A', 'F'],
         'D': ['B'],
         'E': ['B', 'F'],
         'F': ['C', 'E']}

graph = graph1
graph_name = 'graph1'
def dfs_paths(graph, start, goal): # Depth-First Search — Поиск вглубину, функция выводит все возможные пути из start в goal
    stack = [(start, [start])]  # (vertex, path)
    while stack:
        (vertex, path) = stack.pop()
        for next in set(graph[vertex]) - set(path):
            if next == goal:
                yield path + [next]
            else:
                stack.append((next, path + [next]))




print(list(dfs_paths(graph, 'A', 'E')))
path =  list(dfs_paths(graph, 'A', 'E'))[0]

graph_info = ('Path: {0}\nStart: {1}\nGoal: {2}\nReachability type: '.format(path, path[0], path[len(path)-1]))

# ---------------------DRAWING---------------------
path_edges = [] # превращаю последовательность вершин в последовательность ребер
for i in range(0,len(path)-1):
    path_edges.append((path[i],path[i+1]))

G = nx.Graph(graph) # создаю граф из образа graph
fig = plt.figure() # для  сохранения картинки с помощью fig.savefig()

ax = fig.add_subplot(111) # добавляю текстовый бокс в окно
ax.text(-0.14,0.05,graph_info,fontname = 'sans-serif', fontstyle='normal',
        verticalalignment='top', horizontalalignment='left',
        transform=ax.transAxes, bbox={'facecolor': '#89ebf1', 'alpha': 0.7, 'pad': 5})

# в этом сегменте я задаю всем вершинам цвета,и некоторым в частности. Создаю списки с вершинами и их цветами
G.add_nodes_from(G.nodes, color = 'red')
G.add_node(path[len(path)-1],color='green')
G.add_node(path[0],color='blue')
node_color_attr = nx.get_node_attributes(G,'color')
nodes  = node_color_attr.keys() # без list() работает в рисовалке
nodes_colors = list(node_color_attr.values()) #без list() не работает в рисовалке

# в этом сегменте я задаю всем ребрам цвета,и некоторым в частности. Создаю списки с ребрами и их цветами
G.add_edges_from(G.edges,color = 'black')
G.add_edges_from(path_edges, color='green')
edge_color_attr = nx.get_edge_attributes(G,'color')
edges = edge_color_attr.keys() # без list() работает в рисовалке
edges_colors = edge_color_attr.values() # без list() работает в рисовалке

# рисование. draw_spring красиво рисует (вроде бы)
# fig.savefig() сохраняет, понятное дело
nx.draw_spring(G, edgelist=edges,edge_color=edges_colors, nodelist = nodes, node_color = nodes_colors, with_labels = True, font_weight = 'bold')
fig.savefig('C:/Users/bzakh/Documents/Python_Scripts/Networks_Science/test_output/{}.png'.format(graph_name))
plt.show()
