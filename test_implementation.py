"""
script de prueba para validar implementacion con br17.atsp
"""

import sys
sys.path.append('src')
from atsp_parser import parse_atsp_file
from mtz import solve_mtz_cplex, solve_mtz_gurobi

# probar parser
print("probando parser de archivos atsp...")
n, cost_matrix = parse_atsp_file('dataset/TSPLib/br17.atsp')
print(f"dimension: {n}")
print(f"primeras filas de matriz de costos:")
print(cost_matrix[:3, :3])

# probar mtz con cplex (tiempo corto para prueba)
print("\nprobando mtz con cplex (30 segundos)...")
try:
    result = solve_mtz_cplex(n, cost_matrix, time_limit=30)
    print(f"variables: {result['num_vars']}")
    print(f"restricciones: {result['num_constraints']}")
    print(f"tiempo: {result['time']:.2f}s")
    print(f"gap: {result['gap']:.2f}%")
    print(f"objetivo: {result['objective']:.2f}")
except Exception as e:
    print(f"error: {e}")

# probar mtz con gurobi (tiempo corto para prueba)
print("\nprobando mtz con gurobi (30 segundos)...")
try:
    result = solve_mtz_gurobi(n, cost_matrix, time_limit=30)
    print(f"variables: {result['num_vars']}")
    print(f"restricciones: {result['num_constraints']}")
    print(f"tiempo: {result['time']:.2f}s")
    print(f"gap: {result['gap']:.2f}%")
    print(f"objetivo: {result['objective']:.2f}")
except Exception as e:
    print(f"error: {e}")

print("\nprueba completada!")
