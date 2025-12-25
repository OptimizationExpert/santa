import random

import matplotlib.pyplot as plt
import pandas as pd
from ortools.sat.python import cp_model

df = pd.DataFrame()
n = 30
nodes = [i for i in range(n)]
df['x'] = [random.random() for i in nodes]
df['y'] = [random.random() for i in nodes]
df['pop'] = [10 * random.randint(2, 8) for i in nodes]


def dist(i, j):
    return int(50 * ((df.loc[i, 'x'] - df.loc[j, 'x']) ** 2 + (df.loc[i, 'y'] - df.loc[j, 'y']) ** 2))


print(df)

print(dist(2, 24))

model = cp_model.CpModel()
solver = cp_model.CpSolver()
antennas = [a for a in range(10)]
R = 12
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

for i in nodes:
    expr = [U[a, j] for a in antennas for j in nodes if dist(i, j) <= R]
    model.Add(sum(expr) >= y[i])

for (a, i), v in cover.items():
    # i is coverred by a
    model.Add(v <= y[i])
    expr = [U[a, j] for j in nodes if dist(i, j) <= R]
    model.Add(v <= sum(expr))

for i, v in y.items():
    expr = [cover[a, i] for a in antennas]
    model.Add(v <= sum(expr))

for a in antennas:
    expr = [cover[a, i] for i in nodes]
    model.Add(sum(expr) <= cap)

expr_of = [v for i, v in y.items()]
model.Maximize(sum(expr_of))

stat = solver.solve(model)

print(solver.status_name(stat), solver.objective_value)
plt.figure(figsize=(6, 6))
plt.scatter(df['x'], df['y'], s=50)

for i in nodes:
    expr = [solver.value(U[a, i]) for a in antennas]
    exprA = [a * solver.value(U[a, i]) for a in antennas]

    A = int(sum(exprA))
    if sum(expr) > 0:
        x, y = df.loc[i, 'x'], df.loc[i, 'y']
        plt.scatter(x, y, s=100, c='r')
        for j in nodes:
            if solver.value(cover[A, j]):
                x1, y1 = df.loc[j, 'x'], df.loc[j, 'y']
                plt.plot([x, x1], [y, y1])
plt.show()

for (a, i), v in cover.items():
    if solver.value(v) > 0:
        print('Covered by ', a, i)
