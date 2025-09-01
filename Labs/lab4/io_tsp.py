import math
from typing import List, Tuple

def triIndex(i: int, j: int, n: int) -> int:
    """
    Índice lineal del triángulo superior (i < j) en un vector de longitud n*(n-1)//2.
    Fórmula única para evitar duplicaciones y errores silenciosos.
    """
    # Requiere i < j
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

def buildDistanceMatrixCompressed(coords: List[Tuple[float, float]]) -> Tuple[int, List[int]]:
    """
    Construye vector comprimido del triángulo superior (simétrico) con EUC_2D TSPLIB.
    """


def getDistance(i: int, j: int, n: int, vec: List[int]) -> int:
    """Lookup O(1) en la matriz simétrica comprimida."""


def tourDistance(tour: List[int], n: int, vec: List[int]) -> int:
    """Costo de un tour cerrado usando los lookups comprimidos."""

