import math
from typing import List, Tuple

def triIndex(i: int, j: int, n: int) -> int:
    """
    Índice lineal del triángulo superior (i < j) en un vector de longitud n*(n-1)//2.
    Fórmula única para evitar duplicaciones y errores silenciosos.
    """
    if i == j:
        return -1  #No almacena
    if i > j:
        i, j = j, i  #i < j
    return i * (n - 1) - (i * (i - 1)) // 2 + (j - i - 1)

def euc2dRounded(xi: float, yi: float, xj: float, yj: float) -> int:
    """
    Distancia EUC_2D estilo TSPLIB: int(d + 0.5) donde d = sqrt((dx)^2 + (dy)^2).
    Esto evita discrepancias de ±1 respecto a round() en casos límite.
    """
    dx = xi - xj
    dy = yi - yj
    d = math.hypot(dx, dy)
    return int(d + 0.5)

def parseTsp(path: str) -> Tuple[str, List[Tuple[float, float]]]:
    """
    Parser mínimo para instancias TSPLIB con NODE_COORD_SECTION (EUC_2D).
    """
    coords = []
    name = ""
    dimension = None
    edge_weight_type = None
    in_node_section = False
    
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            
            if not line or line.startswith('COMMENT') or line == 'EOF':
                continue
            
            #Obtener nombre
            if line.startswith('NAME'):
                name = line.split(':')[1].strip()
            
            #Obtener dimension
            if line.startswith('DIMENSION'):
                dimension = int(line.split(':')[1].strip())
            
            #Validar tipo distancia
            if line.startswith('EDGE_WEIGHT_TYPE'):
                edge_weight_type = line.split(':')[1].strip()
                if edge_weight_type != 'EUC_2D':
                    raise ValueError(f"Se requiere EDGE_WEIGHT_TYPE=EUC_2D, no {edge_weight_type}")
            
            #Incionico parte con coords
            if line == 'NODE_COORD_SECTION':
                in_node_section = True
                continue
            
            #Procesameinto
            if in_node_section:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        x = float(parts[1])
                        y = float(parts[2])
                        coords.append((x, y))
                    except ValueError:
                        raise ValueError(f"Formato de coordenada inválido: {line}")
    
    # Validaciones
    if edge_weight_type != 'EUC_2D':
        raise ValueError("El archivo debe especificar EDGE_WEIGHT_TYPE=EUC_2D")
    
    if dimension is not None and len(coords) != dimension:
        raise ValueError(f"Dimensión especificada ({dimension}) no coincide con coordenadas leídas ({len(coords)})")
    
    return name, coords

def buildDistanceMatrixCompressed(coords: List[Tuple[float, float]]) -> Tuple[int, List[int]]:
    """
    Construye vector comprimido del triángulo superior (simétrico) con EUC_2D TSPLIB.
    """
    n = len(coords)
    vec_size = n * (n - 1) // 2
    vec = [0] * vec_size
    
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            dist = euc2dRounded(xi, yi, xj, yj)
            idx = triIndex(i, j, n)
            vec[idx] = dist
    
    return n, vec
    

def getDistance(i: int, j: int, n: int, vec: List[int]) -> int:
    """Lookup O(1) en la matriz simétrica comprimida."""
    if i == j:
        return 0
    idx = triIndex(i, j, n)
    return vec[idx]


def tourDistance(tour: List[int], n: int, vec: List[int]) -> int:
    """Costo de un tour cerrado usando los lookups comprimidos."""
    #fitness
    
    costo = 0
    tour_len = len(tour)
    
    for k in range(tour_len - 1):
        i = tour[k]
        j = tour[k + 1]
        costo += getDistance(i, j, n, vec)
    
    # Volver al inicio
    costo += getDistance(tour[-1], tour[0], n, vec)
    
    return costo

def calcular_fitness(tour: List[int], n: int, vec: List[int], epsilon: float = 1.0) -> float:
    """
    Fitness: f(π) = 1/(ε + L(π))
    """
    costo = tourDistance(tour, n, vec)
    return 1.0 / (epsilon + costo)

#apoyo par a repersentacion
def crear_permutacion_aleatoria(n: int) -> List[int]:
    """Crea una permutación aleatoria válida de n elementos."""
    import random
    permutacion = list(range(n))
    random.shuffle(permutacion)
    return permutacion
def validar_permutacion(permutacion: List[int], n: int) -> bool:
    """Valida que sea una permutación válida."""
    if len(permutacion) != n:
        return False
    return sorted(permutacion) == list(range(n))

