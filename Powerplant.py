from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

plants = [g for g in range(3)]
pmax = {0: 100, 1: 150, 2: 200}
pmin = {0: 50, 1: 10, 2: 20}
a = {0: 5, 1: 2, 2: 1}
c = {0: 900, 1: 100, 2: 70}
demand = 380

P = {g: model.NewIntVar(0 * pmin[g], pmax[g], f"power gen {g}")
     for g in plants
     }
U = {g: model.NewBoolVar(f"On/off {g}")
     for g in plants
     }
model.Add(sum(P[g] for g in plants) >= demand)

for g in plants:
    model.Add(P[g] <= pmax[g] * U[g])
    model.Add(P[g] >= pmin[g] * U[g])

expr_of = [a[g] * P[g] + c[g] * U[g] for g in plants]
model.Minimize(sum(expr_of))

stat = solver.solve(model)
print(solver.status_name(stat), solver.objective_value)

for g, v in P.items():
    if solver.value(v) > 0:
        print(g, solver.value(v))
