"""
parser de archivos atsp de tsplib
lee y procesa archivos .atsp
"""

import numpy as np


def parse_atsp_file(filepath):
    """
    lee archivo atsp de tsplib y retorna dimension y matriz de costos
    maneja multiples formatos de archivos atsp
    
    args:
        filepath: ruta al archivo .atsp
    
    returns:
        n: numero de nodos
        cost_matrix: matriz numpy de costos nxn
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # reemplazar EOF si aparece en medio de numeros
    content = content.replace('EOF', ' ')
    lines = content.split('\n')
    
    # buscar dimension
    n = 0
    edge_weight_section_found = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # formato estandar: "DIMENSION: XX" o "DIMENSION:XX"
        if line_stripped.startswith('DIMENSION'):
            try:
                n = int(line_stripped.split(':')[1].strip())
            except:
                pass
        
        # formato alternativo: linea con solo un numero (dimension)
        if n == 0 and line_stripped.isdigit() and int(line_stripped) > 0:
            n = int(line_stripped)
        
        # detectar inicio de seccion de pesos
        if line_stripped.startswith('EDGE_WEIGHT_SECTION'):
            edge_weight_section_found = True
    
    # buscar seccion de pesos
    start_idx = 0
    
    if edge_weight_section_found:
        # formato estandar con seccion explicita
        for i, line in enumerate(lines):
            if line.strip().startswith('EDGE_WEIGHT_SECTION'):
                start_idx = i + 1
                break
    else:
        # formato alternativo: buscar primera linea con numeros grandes
        for i, line in enumerate(lines):
            parts = line.strip().split()
            # detectar linea con matriz de costos (varios numeros grandes)
            if len(parts) >= 5:
                try:
                    # intentar convertir los primeros valores a enteros
                    test_vals = [int(p) for p in parts[:5]]
                    # si son numeros grandes, probablemente es la matriz
                    if any(v > 100 for v in test_vals):
                        start_idx = i
                        break
                except:
                    continue
    
    # leer matriz de costos
    matrix_data = []
    for i in range(start_idx, len(lines)):
        line_stripped = lines[i].strip()
        
        # detener si ya tenemos suficientes datos
        if len(matrix_data) >= n * n:
            break
        if line_stripped == '':
            continue
        
        # separar por espacios o tabs y convertir a enteros
        values = line_stripped.split()
        for v in values:
            if len(matrix_data) >= n * n:
                break
            try:
                matrix_data.append(int(v))
            except:
                # ignorar valores no numericos
                pass
    
    # convertir a matriz nxn
    cost_matrix = np.array(matrix_data[:n*n]).reshape(n, n)
    
    # reemplazar valores diagonales grandes (9999 o mayores) por 0
    for i in range(n):
        if cost_matrix[i, i] >= 9999:
            cost_matrix[i, i] = 0
    
    return n, cost_matrix
