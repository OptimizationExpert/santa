import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import pandas as pd
from ortools.sat.python import cp_model

from tools import dist, create_nodes

df = pd.read_csv('ie.csv')
nodes = create_nodes(df)
node_dic = {n.id: n for n in nodes}

charger_ids = [0, 255, 260, 348, 327, 298, 291, 273, 202]
charger_nodes = [n for n in nodes if n.id in charger_ids]
dd = [dist(n, m) for n in nodes for m in nodes if n.id > m.id and n.county == m.county]
print(min(dd), max(dd), set(dd))

model = cp_model.CpModel()
solver = cp_model.CpSolver()

U = {(n.id, m.id): model.NewBoolVar(f"connection_{n.id}_{m.id}") for n in nodes
     for m in nodes if n != m and dist(n, m) < 60}
assign = {n.id: model.NewBoolVar(f"assign_{n.id}") for n in nodes
          }
BESS = {n.id: model.NewIntVar(0, 100, f"battery_{n.id}") for n in nodes
        }
print('alireza', len(U))
arcs = [(i, j, v) for (i, j), v in U.items()] + [(i, i, v.Not()) for i, v in assign.items()]
model.AddCircuit(arcs)

dublin_node = node_dic[0]
out_expr = [n.id * U[0, n.id] for n in nodes if (0, n.id) in U]
in_expr = [n.id * U[n.id, 0] for n in nodes if (n.id, 0) in U]
# model.Add( sum(in_expr) < sum(out_expr))


# model.Add(BESS[0] == 1000)
model.Add(assign[0] == 1)

for (i, j), v in U.items():
    model.Add(v <= assign[i])
    model.Add(v <= assign[j])
    model.Add(BESS[j] <= 100 * assign[j])
    model.Add(BESS[i] <= 100 * assign[i])

    if i not in charger_nodes and j not in charger_nodes:
        model.Add(BESS[j] == BESS[i] - int(dist(node_dic[i], node_dic[j]))).OnlyEnforceIf(v)

expressions = [v for (i, j), v in U.items()]
coeffs = [dist(node_dic[i], node_dic[j]) for (i, j), v in U.items()]
# model.Minimize(cp_model.LinearExpr.weighted_sum(expressions,coeffs))
model.Add(cp_model.LinearExpr.weighted_sum(expressions, coeffs) <= 4000)

expr_assign = [v for i, v in assign.items()]
coeffs_assign = [node_dic[i].pop for i, v in assign.items()]
# model.Maximize(cp_model.LinearExpr.weighted_sum(expr_assign,coeffs_assign) )
model.Maximize(cp_model.LinearExpr.sum(expr_assign))

solver.parameters.max_time_in_seconds = 240
status = solver.Solve(model)
print(solver.status_name(status), solver.best_objective_bound)

fig = plt.figure(figsize=(8, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

for n in nodes:
    lon, lat = n.long, n.lat
    if solver.value(assign[n.id]) > 0:
        ax.scatter(lon, lat, c='gold', s=30, zorder=2)
    else:
        ax.plot(lon, lat, 'ko', markersize=3, transform=ccrs.PlateCarree())
    ax.text(lon, lat, s=n.id, fontsize=6)

for (i, j), v in U.items():
    if solver.value(v) > 0:
        x0, y0 = node_dic[i].long, node_dic[i].lat
        x1, y1 = node_dic[j].long, node_dic[j].lat
        plt.plot([x0, x1], [y0, y1], lw=1, c='r')
        print(i, j, solver.value(BESS[i]), solver.value(BESS[j]), dist(node_dic[i], node_dic[j]))
for node in charger_nodes:
    x0, y0 = node.long, node.lat
    plt.scatter(x0, y0, s=80, c='r', alpha=0.8, zorder=3)

for i, v in assign.items():
    if solver.value(v):
        print('Nestle', i)

# ax.set_global
ax.gridlines(draw_labels=True)
plt.title('Ireland')
print(solver.objective_value)
a = solver.value(cp_model.LinearExpr.weighted_sum(expressions, coeffs))
print('Distance = ', a)
plt.show()

# 3956.0
# 3842.0
