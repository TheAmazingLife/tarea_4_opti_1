"""
formulacion gg (gavish-graves) para atsp
implementa modelo con cplex y gurobi
"""

import time
from docplex.mp.model import Model
import gurobipy as gp
from gurobipy import GRB


def solve_gg_cplex(n, cost_matrix, time_limit=3600):
    """
    resuelve atsp usando formulacion gg (gavish-graves) con cplex
    
    args:
        n: numero de nodos
        cost_matrix: matriz de costos nxn
        time_limit: tiempo limite en segundos
    
    returns:
        dict con resultados: variables, restricciones, tiempo, gap, objetivo
    """
    model = Model(name='atsp_gg_cplex')
    
    # variables de decision x_ij binarias
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.binary_var(name=f'x_{i}_{j}')
    
    # variables f_ij continuas para flujo de commodities
    f = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                f[i, j] = model.continuous_var(lb=0, ub=n-1, name=f'f_{i}_{j}')
    
    # funcion objetivo: minimizar suma de costos
    obj = model.sum(cost_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.minimize(obj)
    
    # restricciones de conservacion de flujo del tour
    # cada nodo tiene exactamente una arista saliente
    for i in range(n):
        model.add_constraint(model.sum(x[i, j] for j in range(n) if j != i) == 1,
                           ctname=f'out_{i}')
    
    # cada nodo tiene exactamente una arista entrante
    for j in range(n):
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1,
                           ctname=f'in_{j}')
    
    # restricciones de flujo de commodities
    # nodo depot (nodo 0) envia n-1 unidades
    model.add_constraint(model.sum(f[0, j] for j in range(1, n)) == n - 1,
                       ctname='depot_flow')
    
    # cada nodo no-depot consume 1 unidad
    for j in range(1, n):
        flow_in = model.sum(f[i, j] for i in range(n) if i != j)
        flow_out = model.sum(f[j, k] for k in range(n) if k != j)
        model.add_constraint(flow_in - flow_out == 1, ctname=f'flow_cons_{j}')
    
    # restricciones de capacidad: flujo solo en aristas seleccionadas
    for i in range(n):
        for j in range(n):
            if i != j:
                model.add_constraint(f[i, j] <= (n - 1) * x[i, j],
                                   ctname=f'capacity_{i}_{j}')
    
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


def solve_gg_gurobi(n, cost_matrix, time_limit=3600):
    """
    resuelve atsp usando formulacion gg (gavish-graves) con gurobi
    
    args:
        n: numero de nodos
        cost_matrix: matriz de costos nxn
        time_limit: tiempo limite en segundos
    
    returns:
        dict con resultados: variables, restricciones, tiempo, gap, objetivo
    """
    model = gp.Model('atsp_gg_gurobi')
    model.setParam('OutputFlag', 0)
    model.setParam('TimeLimit', time_limit)
    
    # variables de decision x_ij binarias
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')
    
    # variables f_ij continuas para flujo de commodities
    f = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                f[i, j] = model.addVar(lb=0, ub=n-1, vtype=GRB.CONTINUOUS, name=f'f_{i}_{j}')
    
    model.update()
    
    # funcion objetivo: minimizar suma de costos
    obj = gp.quicksum(cost_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.setObjective(obj, GRB.MINIMIZE)
    
    # restricciones de conservacion de flujo del tour
    # cada nodo tiene exactamente una arista saliente
    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if j != i) == 1, name=f'out_{i}')
    
    # cada nodo tiene exactamente una arista entrante
    for j in range(n):
        model.addConstr(gp.quicksum(x[i, j] for i in range(n) if i != j) == 1, name=f'in_{j}')
    
    # restricciones de flujo de commodities
    # nodo depot (nodo 0) envia n-1 unidades
    model.addConstr(gp.quicksum(f[0, j] for j in range(1, n)) == n - 1, name='depot_flow')
    
    # cada nodo no-depot consume 1 unidad
    for j in range(1, n):
        flow_in = gp.quicksum(f[i, j] for i in range(n) if i != j)
        flow_out = gp.quicksum(f[j, k] for k in range(n) if k != j)
        model.addConstr(flow_in - flow_out == 1, name=f'flow_cons_{j}')
    
    # restricciones de capacidad: flujo solo en aristas seleccionadas
    for i in range(n):
        for j in range(n):
            if i != j:
                model.addConstr(f[i, j] <= (n - 1) * x[i, j], name=f'capacity_{i}_{j}')
    
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
