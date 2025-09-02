import math
from typing import List, Tuple

def triIndex(i: int, j: int, n: int) -> int:
    """
    Índice lineal del triángulo superior (i < j) en un vector de longitud n*(n-1)//2.
    Fórmula única para evitar duplicaciones y errores silenciosos.
    """
    if i == j:
        return 0
    if i > j:
        i, j = j, i
    return i * (n - 1) - (i * (i - 1)) // 2 + (j - i - 1)

def euc2dRounded(xi: float, yi: float, xj: float, yj: float) -> int:
    """
    Distancia EUC_2D estilo TSPLIB: int(d + 0.5) donde d = sqrt((dx)^2 + (dy)^2).
    """
    dx = xi - xj
    dy = yi - yj
    d = math.hypot(dx, dy)
    return int(d + 0.5)

def parseTsp(path: str) -> Tuple[str, List[Tuple[float, float]]]:
    """
    Parser mínimo para instancias TSPLIB con NODE_COORD_SECTION (EUC_2D).
    Devuelve: (nombre, lista de coordenadas).
    """
    name = "TSP"
    coords: List[Tuple[float, float]] = []
    in_coords = False
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            u = line.upper()
            if u.startswith("NAME"):
                try:
                    name = line.split(":", 1)[1].strip()
                except Exception:
                    pass
                continue
            if u.startswith("NODE_COORD_SECTION"):
                in_coords = True
                continue
            if u.startswith("EOF"):
                break
            if in_coords:
                parts = line.split()
                if len(parts) >= 3:
                    idx = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    while len(coords) < idx:
                        coords.append((0.0, 0.0))
                    coords[idx-1] = (x, y)
    coords = [c for c in coords if c != (0.0, 0.0)] or coords
    return name, coords

def buildDistanceMatrixCompressed(coords: List[Tuple[float, float]]) -> Tuple[int, List[int]]:
    """
    Construye vector comprimido del triángulo superior (simétrico) con distancias EUC_2D.
    """
    n = len(coords)
    m = n * (n - 1) // 2
    vec = [0] * m
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = euc2dRounded(xi, yi, xj, yj)
            vec[triIndex(i, j, n)] = d
    return n, vec

def getDistance(i: int, j: int, n: int, vec: List[int]) -> int:
    """Lookup O(1) en la matriz simétrica comprimida."""
    if i == j:
        return 0
    return vec[triIndex(i, j, n)]

def tourDistance(tour: List[int], n: int, vec: List[int]) -> int:
    """Costo de un tour cerrado usando los lookups comprimidos."""
    total = 0
    L = len(tour)
    for k in range(L):
        a = tour[k]
        b = tour[(k + 1) % L]
        total += getDistance(a, b, n, vec)
    return total
