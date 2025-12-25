import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

n = 10  # 10 nodes
m = 20  # 20 edges
seed = 20160  # seed random number generators for reproducibility

# Use seed for reproducibility
G = nx.gnm_random_graph(n, m, seed=seed)

# some properties
print("node degree clustering")
for v in nx.nodes(G):
    print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")

print()
print("the adjacency list")
for line in nx.generate_adjlist(G):
    print(line)

pos = nx.spring_layout(G, seed=seed)  # Seed for reproducible layout
nx.draw(G, pos=pos)
plt.show()


def dist(i, j):
    x0, y0 = pos[i][0], pos[i][1]
    x1, y1 = pos[j][0], pos[j][1]
    return int(100 * ((x0 - x1) ** 2 + (y0 - y1) ** 2))


data = {}
for (i, j) in G.edges:
    data[i, j] = dist(i, j)
    data[j, i] = dist(i, j)

print('alireza', data)

nodes = [n for n in G.nodes]

model = cp_model.CpModel()
solver = cp_model.CpSolver()

x = {(i, j): model.NewBoolVar(f"select_{i}_{j}") for (i, j) in data}
flow = {(i, j): model.NewIntVar(0, 10, f"flow_{i}_{j}") for (i, j) in data}

for i in nodes:
    expr = [x[i, j] for j in nodes if (i, j) in data]
    out_go = [flow[i, j] for j in nodes if (i, j) in data]
    in_go = [flow[j, i] for j in nodes if (i, j) in data]
    if i == 7:
        model.Add(9 - 0 == sum(out_go) - sum(in_go))
    else:
        model.Add(0 - 1 == sum(out_go) - sum(in_go))

for (i, j) in data:
    model.Add(flow[i, j] <= 10 * x[i, j])

expr = [x[i, j] for (i, j) in data]
# model.Add(sum(expr) ==9)

expr_of = [x[i, j] * data[i, j] for (i, j) in x]
model.Minimize(sum(expr_of))

stat = solver.solve(model)
print(solver.status_name(stat), solver.objective_value)

for (i, j) in data:

    x0, y0 = pos[i][0], pos[i][1]
    x1, y1 = pos[j][0], pos[j][1]
    plt.scatter(x0, y0, s=100, alpha=0.6)
    plt.scatter(x1, y1, s=100, alpha=0.6)
    plt.text(x0, y0, s=str(i))
    plt.text(x1, y1, s=str(j))
    plt.plot([x0, x1], [y0, y1], c='grey', lw=0.4)
    if solver.value(x[i, j]) > 0:
        plt.plot([x0, x1], [y0, y1], c='r', lw=2)

plt.show()
