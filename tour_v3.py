import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import pandas as pd
from ortools.sat.python import cp_model

from tools import dist, create_nodes

df = pd.read_csv('ie.csv')
nodes = create_nodes(df)
node_dic = {n.id: n for n in nodes}

for n in nodes:
    print(n.id, n.name)
dd = [dist(n, m) for n in nodes for m in nodes if n.id > m.id and n.county == m.county]
print(min(dd), max(dd), set(dd))
vehicles = [v for v in range(2)]

model = cp_model.CpModel()
solver = cp_model.CpSolver()

U = {(n.id, m.id, c): model.NewBoolVar(f"connection_{n.id}_{m.id}_{c}") for n in nodes
     for m in nodes for c in vehicles if n != m and dist(n, m) < 50}
assign = {(n.id, c): model.NewBoolVar(f"assign_{n.id}_{c}") for n in nodes for c in vehicles
          }
for c in vehicles:
    arcs = [(i, j, v) for (i, j, cc), v in U.items() if c == cc] + [(i, i, v.Not()) for (i, cc), v in assign.items() if
                                                                    c == cc]
    arcs += [(349, 0, True)]
    model.AddCircuit(arcs)

dublin_node = node_dic[0]
# out_expr = [n.id*U[0,n.id] for n in nodes if (0,n.id) in U]
# in_expr = [n.id*U[n.id,0] for n in nodes if (n.id,0) in U]
# model.Add( sum(in_expr) < sum(out_expr))

for c in vehicles:
    model.Add(assign[0, c] == 1)

for n in nodes:
    if n.id not in [0, 349]:
        expr = [assign[n.id, c] for c in vehicles]
        model.AddAtMostOne(expr)

for (i, j, c), v in U.items():
    model.Add(v <= assign[i, c])
    model.Add(v <= assign[j, c])

for cc in vehicles:
    expressions = [v for (i, j, c), v in U.items() if c == cc]
    coeffs = [dist(node_dic[i], node_dic[j]) for (i, j, c), v in U.items() if c == cc]
    model.Add(cp_model.LinearExpr.weighted_sum(expressions, coeffs) <= 2000)

expr_assign = [v for (i, c), v in assign.items()]
coeffs_assign = [node_dic[i].pop for (i, c), v in assign.items()]
model.Maximize(cp_model.LinearExpr.sum(expr_assign))

solver.parameters.max_time_in_seconds = 360
status = solver.Solve(model)
print(solver.status_name(status), solver.best_objective_bound)

fig = plt.figure(figsize=(8, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

KOLORS = ['r', 'b']
# Add map features
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
for c in vehicles:
    for n in nodes:
        lon, lat = n.long, n.lat
        ax.plot(lon, lat, 'ko', markersize=3, transform=ccrs.PlateCarree(), zorder=1)
        if solver.value(assign[n.id, c]) > 0:
            ax.scatter(lon, lat, c='gold', s=30, zorder=3)
        ax.text(lon, lat, s=n.id, fontsize=6)

for (i, j, c), v in U.items():
    if solver.value(v) > 0:
        x0, y0 = node_dic[i].long, node_dic[i].lat
        x1, y1 = node_dic[j].long, node_dic[j].lat
        plt.plot([x0, x1], [y0, y1], lw=1.5, c=KOLORS[c])

# ax.set_global
ax.gridlines(draw_labels=True)
plt.title('Ireland')
print(solver.objective_value)
plt.show()
