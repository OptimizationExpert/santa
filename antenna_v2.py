import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ortools.sat.python import cp_model

random.seed(100)
df = pd.DataFrame()
n = 30
nodes = [i for i in range(n)]
df['x'] = [random.random() for i in nodes]
df['y'] = [random.random() for i in nodes]
df['pop'] = [10 * random.randint(2, 8) for i in nodes]


def dist(i, j):
    return int(10 * np.sqrt(((df.loc[i, 'x'] - df.loc[j, 'x']) ** 2 + (df.loc[i, 'y'] - df.loc[j, 'y']) ** 2)))


model = cp_model.CpModel()
solver = cp_model.CpSolver()
antennas = [a for a in range(10)]
R = 5
cap = 10

U = {(a, i): model.NewBoolVar(f"install_{a}_{i}")
     for a in antennas for i in nodes
     }

cover = {(a, i): model.NewBoolVar(f"cover_{a}_{i}")
         for a in antennas for i in nodes
         }

y = {i: model.NewBoolVar(f"covered_{i}")
     for i in nodes
     }

for a in antennas:
    expr = [U[a, i] for i in nodes]
    model.AddAtMostOne(expr)
for i in nodes:
    expr = [U[a, i] for a in antennas]
    model.AddAtMostOne(expr)
    expr = [U[a, j] for a in antennas for j in nodes if dist(i, j) <= R]
    model.Add(sum(expr) >= y[i])

expr_T = [v for (a, i), v in U.items()]
model.Add(sum(expr_T) <= 3)

expr_of = [v for i, v in y.items()]
model.Maximize(sum(expr_of))

stat = solver.solve(model)

print(solver.status_name(stat), solver.objective_value)
plt.figure(figsize=(6, 6))
plt.scatter(df['x'], df['y'], s=50)

for i in nodes:
    x, y = df.loc[i, 'x'], df.loc[i, 'y']
    plt.text(x, y, s=str(i), fontsize=8)
    expr = [solver.value(U[a, i]) for a in antennas]
    exprA = [a * solver.value(U[a, i]) for a in antennas]
    coef = 1 / 10
    A = int(sum(exprA))
    if sum(expr) > 0:
        plt.scatter(x, y, s=100, c='r')
        Xvec = [x + coef * R * np.cos(th) for th in np.linspace(0, 2 * np.pi, 100)]
        Yvec = [y + coef * R * np.sin(th) for th in np.linspace(0, 2 * np.pi, 100)]
        plt.scatter(Xvec, Yvec, s=10, c='b')

plt.show()

print(dist(0, 24), dist(1, 11))
