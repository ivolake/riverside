import networkx as nx
import matplotlib.pyplot as plt

graph = {'A': ['B', 'C'],
         'B': ['A', 'D', 'C'],
         'C': ['A', 'B', 'F', 'D'],
         'D': ['B','C'],
         'E': ['F'],
         'F': ['C', 'E']}

G = nx.Graph(graph)
G.add_edges_from(G.edges,color = 'black')
# print(nx.get_edge_attributes(G,'color'))
G.add_edges_from([('B', 'C'), ('C', 'D')], color='red')
G.add_edges_from([('A', 'B', {'color': 'blue'}), ('C','D', {'color': 'green'})])
edge_color_attr = nx.get_edge_attributes(G,'color')
# print(edge_color_attr)
edges = edge_color_attr.keys()
# print(edges)
colors = edge_color_attr.values()
# print(colors)
# edges,colors = zip(*nx.get_edge_attributes(G,'color').items())
# print(*nx.get_edge_attributes(G,'color').items())
nx.draw(G, edgelist=edges,edge_color=colors, with_labels=True, font_weight='bold')
plt.show()


# plt.subplot(152)
# nx.draw_spring(G, with_labels=True, font_weight='bold')
#
# plt.subplot(153)
# nx.draw_random(G, with_labels=True, font_weight='bold')
#
# plt.subplot(154)
# nx.draw_circular(G, with_labels=True, font_weight='bold')
#
# plt.subplot(155)
# nx.draw_spectral(G, with_labels=True, font_weight='bold')
