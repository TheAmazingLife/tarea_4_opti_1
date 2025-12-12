"""
formulacion mtz (miller-tucker-zemlin) para atsp
implementa modelo con cplex y gurobi
"""

import time
from docplex.mp.model import Model
import gurobipy as gp
from gurobipy import GRB


def solve_mtz_cplex(n, cost_matrix, time_limit=3600):
    """
    resuelve atsp usando formulacion mtz con cplex
    
    args:
        n: numero de nodos
        cost_matrix: matriz de costos nxn
        time_limit: tiempo limite en segundos
    
    returns:
        dict con resultados: variables, restricciones, tiempo, gap, objetivo
    """
    model = Model(name='atsp_mtz_cplex')
    
    # variables de decision x_ij binarias
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.binary_var(name=f'x_{i}_{j}')
    
    # variables u_i continuas para posicion en tour
    u = {}
    for i in range(n):
        if i == 0:
            u[i] = model.continuous_var(lb=1, ub=1, name=f'u_{i}')
        else:
            u[i] = model.continuous_var(lb=1, ub=n, name=f'u_{i}')
    
    # funcion objetivo: minimizar suma de costos
    obj = model.sum(cost_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.minimize(obj)
    
    # restricciones de conservacion de flujo
    # cada nodo tiene exactamente una arista saliente
    for i in range(n):
        model.add_constraint(model.sum(x[i, j] for j in range(n) if j != i) == 1, 
                           ctname=f'out_{i}')
    
    # cada nodo tiene exactamente una arista entrante
    for j in range(n):
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1,
                           ctname=f'in_{j}')
    
    # restricciones de eliminacion de subtours (mtz)
    # formulacion ajustada segun roberti & toth (ecuacion 10)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(u[i] - u[j] + (n - 1) * x[i, j] <= n - 2,
                                   ctname=f'mtz_{i}_{j}')
    
    # configurar parametros del solver
    model.parameters.timelimit = time_limit
    model.parameters.mip.display = 0
    
    # resolver
    start_time = time.time()
    solution = model.solve()
    solve_time = time.time() - start_time
    
    # extraer resultados
    num_vars = model.number_of_variables
    num_constraints = model.number_of_constraints
    
    if solution:
        obj_value = solution.objective_value
        gap = model.solve_details.mip_relative_gap * 100
    else:
        obj_value = float('inf')
        gap = 100.0
    
    return {
        'num_vars': num_vars,
        'num_constraints': num_constraints,
        'time': solve_time,
        'gap': gap,
        'objective': obj_value
    }


def solve_mtz_gurobi(n, cost_matrix, time_limit=3600):
    """
    resuelve atsp usando formulacion mtz con gurobi
    
    args:
        n: numero de nodos
        cost_matrix: matriz de costos nxn
        time_limit: tiempo limite en segundos
    
    returns:
        dict con resultados: variables, restricciones, tiempo, gap, objetivo
    """
    model = gp.Model('atsp_mtz_gurobi')
    model.setParam('OutputFlag', 0)
    model.setParam('TimeLimit', time_limit)
    
    # variables de decision x_ij binarias
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')
    
    # variables u_i continuas para posicion en tour
    u = {}
    for i in range(n):
        if i == 0:
            u[i] = model.addVar(lb=1, ub=1, vtype=GRB.CONTINUOUS, name=f'u_{i}')
        else:
            u[i] = model.addVar(lb=1, ub=n, vtype=GRB.CONTINUOUS, name=f'u_{i}')
    
    model.update()
    
    # funcion objetivo: minimizar suma de costos
    obj = gp.quicksum(cost_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.setObjective(obj, GRB.MINIMIZE)
    
    # restricciones de conservacion de flujo
    # cada nodo tiene exactamente una arista saliente
    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if j != i) == 1, name=f'out_{i}')
    
    # cada nodo tiene exactamente una arista entrante
    for j in range(n):
        model.addConstr(gp.quicksum(x[i, j] for i in range(n) if i != j) == 1, name=f'in_{j}')
    
    # restricciones de eliminacion de subtours (mtz)
    # formulacion ajustada segun roberti & toth (ecuacion 10)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.addConstr(u[i] - u[j] + (n - 1) * x[i, j] <= n - 2, name=f'mtz_{i}_{j}')
    
    # resolver
    start_time = time.time()
    model.optimize()
    solve_time = time.time() - start_time
    
    # extraer resultados
    num_vars = model.NumVars
    num_constraints = model.NumConstrs
    
    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        obj_value = model.ObjVal if model.SolCount > 0 else float('inf')
        gap = model.MIPGap * 100 if model.SolCount > 0 else 100.0
    else:
        obj_value = float('inf')
        gap = 100.0
    
    return {
        'num_vars': num_vars,
        'num_constraints': num_constraints,
        'time': solve_time,
        'gap': gap,
        'objective': obj_value
    }
