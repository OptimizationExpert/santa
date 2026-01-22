from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

model.Minimize()
stat = solver.solve(model)
print(solver.status_name(stat), solver.objective_value)
