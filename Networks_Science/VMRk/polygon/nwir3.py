import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# cd Documents\Python_Scripts\Networks_Science

graph = {'A': ['B', 'C'],
         'B': ['A', 'D', 'E'],
         'C': ['A', 'F'],
         'D': ['B'],
         'E': ['B', 'F'],
         'F': ['C', 'E']}

# a = set('hello world')
# b = set('world')
# print(a)
# print(b)
# print(a-b)

def dfs(graph, start): #Depth-First Search — Поиск вглубину, функция выводит достижимые вершины из данной
    visited, stack = [], [start] # посещенные и непосещенные вершины, начинается с той, от которой идем (то есть как бы из пустой вершины)
    while stack:
        vertex = stack.pop() #забираем верхний элемент из стэка необработанных вершин,то есть начальную
        if vertex not in visited: # если вершина не посещена
            visited.append(vertex)
            stack.extend(set(graph[vertex]) - set(visited)) # убираем из множества соседних вершин
    return visited                                          #  для вершины vertex (с неповторяющимися  элементами) множество посещенных вершнм

print(dfs(graph, 'A'))

def dfs_paths(graph, start, goal):
    stack = [(start, [start])]  # (vertex, path)
    while stack:
        (vertex, path) = stack.pop()
        for next in set(graph[vertex]) - set(path):
            if next == goal:
                yield path + [next]
            else:
                stack.append((next, path + [next]))

print(list(dfs_paths(graph, 'A', 'F')))

# from queue import deque
#
#
# def bfs(graph, start):
#     visited, queue = [], deque([start])
#     while queue:
#         vertex = queue.pop()
#         if vertex not in visited:
#             visited.append(vertex)
#             queue.extendleft(set(graph[vertex]) - set(visited))
#     return visited
#
# print(bfs(graph, 'A'))
#
# def bfs_paths(graph, start, goal):
#     queue = deque([(start, [start])])
#     while queue:
#         (vertex, path) = queue.pop()
#         for next in set(graph[vertex]) - set(path):
#             if next == goal:
#                 yield path + [next]
#             else:
#                 queue.appendleft((next, path+[next]))
#
# print(list(bfs_paths(graph, 'A', 'F')))

L = np.random.randint(0,2,25)
L = L.reshape(5,5)
dfL = pd.DataFrame(data = L, index = ['1','2','3','4','5'], columns = ['1','2','3','4','5'])
# G = dict(zip(dfL,L))
print(dfL)
fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
ax.set_xlim((2, 8))
ax.set_ylim((2, 8))

circles = []
for i in range(1,6):
    for j in range(1,6):
        circles.append(plt.Circle((2 + j,8 - i), 0.2, color='#46f5a3')) #0.01 + j//9, 0.95 - i//9
        plt.text(2 + j-0.09,8 - i - 0.09,dfL.loc[str(j),str(i)])




for c in circles:
    ax.add_artist(c)

plt.show()
fig.savefig('plotcircles2.png')
