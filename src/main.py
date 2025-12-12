"""
programa principal para resolver instancias atsp
ejecuta 10 instancias con formulaciones mtz y gg usando cplex y gurobi
genera tabla de resultados en csv
"""

import os
import pandas as pd
from atsp_parser import parse_atsp_file
from mtz import solve_mtz_cplex, solve_mtz_gurobi
from gg import solve_gg_cplex, solve_gg_gurobi


def main():
    """
    funcion principal: resuelve 10 instancias atsp con 2 modelos y 2 solvers
    genera tabla de resultados en formato csv
    """
    # lista de instancias a resolver
    instances = [
        'br17.atsp',      # pequena
        'ftv33.atsp',     # pequena
        'ftv35.atsp',     # pequena
        'ftv38.atsp',     # pequena
        'ft53.atsp',      # mediana
        'ft70.atsp',      # mediana
        'ftv70.atsp',     # mediana
        'kro124p.atsp',   # mediana
        'ftv170.atsp',    # grande
        'rbg323.atsp'     # grande
    ]
    
    # directorio de instancias
    dataset_dir = './dataset/TSPLib/'
    
    # lista para almacenar resultados
    results = []
    
    # iterar sobre todas las instancias
    for instance_name in instances:
        print(f'\nprocesando instancia: {instance_name}')
        filepath = os.path.join(dataset_dir, instance_name)
        
        try:
            # leer instancia
            n, cost_matrix = parse_atsp_file(filepath)
            print(f'  numero de nodos: {n}')
            
            # resolver con mtz + cplex
            print('  resolviendo mtz + cplex...')
            try:
                result_mtz_cplex = solve_mtz_cplex(n, cost_matrix, time_limit=3600)
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'mtz',
                    'solver': 'cplex',
                    **result_mtz_cplex
                })
            except Exception as e:
                print(f'    error: {e}')
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'mtz',
                    'solver': 'cplex',
                    'num_vars': -1,
                    'num_constraints': -1,
                    'time': -1,
                    'gap': 100.0,
                    'objective': float('inf')
                })
            
            # resolver con mtz + gurobi
            print('  resolviendo mtz + gurobi...')
            try:
                result_mtz_gurobi = solve_mtz_gurobi(n, cost_matrix, time_limit=3600)
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'mtz',
                    'solver': 'gurobi',
                    **result_mtz_gurobi
                })
            except Exception as e:
                print(f'    error: {e}')
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'mtz',
                    'solver': 'gurobi',
                    'num_vars': -1,
                    'num_constraints': -1,
                    'time': -1,
                    'gap': 100.0,
                    'objective': float('inf')
                })
            
            # resolver con gg + cplex
            print('  resolviendo gg + cplex...')
            try:
                result_gg_cplex = solve_gg_cplex(n, cost_matrix, time_limit=3600)
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'gg',
                    'solver': 'cplex',
                    **result_gg_cplex
                })
            except Exception as e:
                print(f'    error: {e}')
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'gg',
                    'solver': 'cplex',
                    'num_vars': -1,
                    'num_constraints': -1,
                    'time': -1,
                    'gap': 100.0,
                    'objective': float('inf')
                })
            
            # resolver con gg + gurobi
            print('  resolviendo gg + gurobi...')
            try:
                result_gg_gurobi = solve_gg_gurobi(n, cost_matrix, time_limit=3600)
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'gg',
                    'solver': 'gurobi',
                    **result_gg_gurobi
                })
            except Exception as e:
                print(f'    error: {e}')
                results.append({
                    'instance': instance_name,
                    'nodes': n,
                    'model': 'gg',
                    'solver': 'gurobi',
                    'num_vars': -1,
                    'num_constraints': -1,
                    'time': -1,
                    'gap': 100.0,
                    'objective': float('inf')
                })
                
        except Exception as e:
            print(f'  error al procesar instancia: {e}')
            continue
    
    # crear dataframe con resultados
    df = pd.DataFrame(results)
    
    # guardar resultados en csv
    output_file = 'resultados_atsp.csv'
    df.to_csv(output_file, index=False)
    print(f'\nresultados guardados en: {output_file}')
    
    # mostrar resumen
    print('\nresumen de resultados:')
    print(df.to_string())
    
    return df


if __name__ == '__main__':
    main()