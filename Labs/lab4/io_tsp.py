import math
from typing import List, Tuple

def triIndex(i: int, j: int, n: int) -> int:
    """
    Índice lineal del triángulo superior (i < j) en un vector de longitud n*(n-1)//2.
    Fórmula única para evitar duplicaciones y errores silenciosos.
    """
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
    Devuelve (name, coords) con coords indexado 0..n-1 respetando el id-1.
    """
    name = "instance"
    coords_dict = {}
    in_coords = False
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            u = s.upper()
            if u.startswith("NAME"):
                # NAME : berlin52
                try:
                    name = s.split(":")[1].strip()
                except Exception:
                    pass
            if u.startswith("NODE_COORD_SECTION"):
                in_coords = True
                continue
            if u == "EOF":
                break
            if in_coords:
                parts = s.split()
                if len(parts) >= 3:
                    i = int(parts[0])
                    x = float(parts[1]); y = float(parts[2])
                    coords_dict[i] = (x, y)

    # ordenar por id y convertir a lista 0..n-1
    if not coords_dict:
        raise ValueError(f"No se encontraron coordenadas en {path}")
    max_id = max(coords_dict.keys())
    coords = [None] * max_id
    for k, v in coords_dict.items():
        coords[k-1] = v
    # filtrar posibles None si ids no son 1..n
    coords = [c for c in coords if c is not None]
    return name, coords

def buildDistanceMatrixCompressed(coords: List[Tuple[float, float]]) -> Tuple[int, List[int]]:
    """
    Construye vector comprimido del triángulo superior (simétrico) con EUC_2D TSPLIB.
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
    if i > j:
        i, j = j, i
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
