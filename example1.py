from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

PEOPLE = ['Alice', 'Bob', 'Carol', 'Dave', 'Eve']
GIFTS = ['Book', 'Toy', 'Chocolate', 'Water', 'Flowers']
GIFTCOSTS = [10, 20, 5, 15, 7]
HAPPINESS = {
    'Book': [3, 2, 5, 1, 4],
    'Toy': [5, 2, 4, 3, 1],
    'Chocolate': [1, 3, 4, 5, 2],
    'Water': [2, 5, 3, 4, 1],
    'Flowers': [4, 3, 1, 2, 5]}
BUDGET = 50

x = {(p, g): model.NewBoolVar(f"assign_{p}_{g}")
     for p in PEOPLE for g in GIFTS
     }

for p in PEOPLE:
    expr = [x[p, g] for g in GIFTS]
    # model.Add( sum(expr)  == 1)
    model.AddExactlyOne(expr)

expr_cost = [GIFTCOSTS[GIFTS.index(g)] * x[p, g] for g in GIFTS for p in PEOPLE]
model.Add(sum(expr_cost) <= BUDGET)

expr_of = [HAPPINESS[g][PEOPLE.index(p)] * x[p, g] for g in GIFTS for p in PEOPLE]
model.Maximize(sum(expr_of))

stat = solver.solve(model)
print(solver.status_name(stat), solver.objective_value)

for (p, g), v in x.items():
    if solver.value(v) > 0:
        print(p, g)
