import math
from typing import List, Tuple

def triIndex(i: int, j: int, n: int) -> int:
    """
    Índice lineal del triángulo superior (i < j) en un vector de longitud n*(n-1)//2.
    Fórmula única para evitar duplicaciones y errores silenciosos.
    """
    # Requiere i < j
    return i * (n - 1) - (i * (i - 1)) // 2 + (j - i - 1)

def euc2d_rounded(xi: float, yi: float, xj: float, yj: float) -> int:
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
    name = "instance"
    coords: List[Tuple[float, float]] = []
    with open(path, "r", encoding="utf-8") as f:
        mode = "header"
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("NAME"):
                parts = line.split(":")
                if len(parts) > 1:
                    name = parts[1].strip()
            if line.startswith("NODE_COORD_SECTION"):
                mode = "coords"
                continue
            if line.startswith("EOF"):
                break
            if mode == "coords":
                parts = line.split()
                if len(parts) >= 3:
                    x = float(parts[1]); y = float(parts[2])
                    coords.append((x, y))
    return name, coords

def buildDistanceMatrixCompressed(coords: List[Tuple[float, float]]) -> Tuple[int, List[int]]:
    """
    Construye vector comprimido del triángulo superior (simétrico) con EUC_2D TSPLIB.
    """
    n = len(coords)
    vec = [0] * (n * (n - 1) // 2)
    for i, (xi, yi) in enumerate(coords):
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = euc2d_rounded(xi, yi, xj, yj)  # <-- TSPLIB exacto: int(d + 0.5)
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
    s = 0
    for a, b in zip(tour, tour[1:]):
        s += getDistance(a, b, n, vec)
    s += getDistance(tour[-1], tour[0], n, vec)
    return s
