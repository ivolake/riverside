import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

L = np.random.randint(0,2,25)
L = L.reshape(5,5)

def show_g(A):
    for i in range(0,4):
        for j in range(0,4):
            print(A[i,j],end = ' ')
        print()
show_g(L)
fig = plt.figure(figsize = (5,5))
