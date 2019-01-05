import matplotlib.pyplot as plt
import networkx as nx
# cd Documents\Python_Scripts\Networks_Science

# G = nx.petersen_graph()
#
# plt.subplot(121)
# nx.draw(G, with_labels=True, font_weight='bold')
#
# plt.subplot(122)
# nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
#
# plt.show()

G = nx.Graph()
# example graph
for color in "bgrcmyk":
    G.add_edge('s'+color,'t'+color, color=color)

# edge_color_attr = nx.get_edge_attributes(G,'color')
# edges = edge_color_attr.keys()
# colors = edge_color_attr.values()
edges,colors = zip(*nx.get_edge_attributes(G,'color').items())
nx.draw(G,edgelist=edges,edge_color=colors,width=10)
plt.show()
