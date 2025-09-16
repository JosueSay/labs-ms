import math

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

def degmin_to_rad(x: float) -> float:
    """
    Convierte un valor en grados.minutos (p. ej. 68.58 = 68° 58′) a radianes,
    según la convención de TSPLIB para EDGE_WEIGHT_TYPE = GEO.
    """
    deg = int(x)
    minutes = x - deg
    # Fórmula oficial TSPLIB: pi * (deg + 5.0 * minutes / 3.0) / 180.0
    return math.pi * (deg + 5.0 * minutes / 3.0) / 180.0

def geo_distance(lat_i: float, lon_i: float, lat_j: float, lon_j: float) -> int:
    """
    Distancia geográfica TSPLIB (GEO).
    TSPLIB da las coordenadas como (lat, lon) en grados.minutos.
    """
    R = 6378.388
    phi_i = degmin_to_rad(lat_i)
    lam_i = degmin_to_rad(lon_i)
    phi_j = degmin_to_rad(lat_j)
    lam_j = degmin_to_rad(lon_j)

    q1 = math.cos(lam_i - lam_j)
    q2 = math.cos(phi_i - phi_j)
    q3 = math.cos(phi_i + phi_j)
    return int(R * math.acos(0.5 * ((1.0 + q1) * q2 - (1.0 - q1) * q3)) + 1.0)

def parseTsp(path: str) -> tuple[str, str, list[tuple[float, float]]]:
    """
    Parser mínimo para instancias TSPLIB con NODE_COORD_SECTION.
    - Soporta EDGE_WEIGHT_TYPE: EUC_2D y GEO.
    - Devuelve (name, edge_weight_type, coords) donde:
        name: nombre de la instancia.
        edge_weight_type: 'EUC_2D' o 'GEO' (por ahora).
        coords: lista de (x, y) para EUC_2D o (lon, lat) en formato grados.minutos para GEO.
    """
    name = "instance"
    edge_weight_type = "EUC_2D"  # valor por defecto si no aparece en el archivo
    coords: list[tuple[float, float]] = []

    with open(path, "r", encoding="utf-8") as f:
        mode = "header"
        for line in f:
            line = line.strip()
            if not line:
                continue

            # NAME : XXX
            if line.startswith("NAME"):
                parts = line.split(":")
                if len(parts) > 1:
                    name = parts[1].strip()

            # EDGE_WEIGHT_TYPE : EUC_2D / GEO / ...
            if "EDGE_WEIGHT_TYPE" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    edge_weight_type = parts[1].strip()

            # Inicio de la sección de coordenadas
            if line.startswith("NODE_COORD_SECTION"):
                mode = "coords"
                continue

            # Fin de archivo TSPLIB
            if line.startswith("EOF"):
                break

            # Lectura de coordenadas
            if mode == "coords":
                parts = line.split()
                if len(parts) >= 3:
                    # El primer valor suele ser el índice (1..n), lo ignoramos.
                    x = float(parts[1])
                    y = float(parts[2])
                    coords.append((x, y))

    return name, edge_weight_type, coords

def buildDistanceMatrixCompressed(coords: list[tuple[float, float]],
                                  edge_weight_type: str = "EUC_2D") -> tuple[int, list[int]]:
    """
    Construye el vector comprimido del triángulo superior (simétrico) de la matriz de distancias.
    - El vector tiene longitud n*(n-1)//2 y almacena las distancias entre pares de nodos (i<j).
    - La indexación se hace con triIndex(i, j, n).
    """
    n = len(coords)
    vec = [0] * (n * (n - 1) // 2)
    for i, (xi, yi) in enumerate(coords):
        for j in range(i + 1, n):
            xj, yj = coords[j]
            if edge_weight_type == "GEO":
                # En TSPLIB GEO, coords se interpretan como (lat, lon).
                d = geo_distance(xi, yi, xj, yj)
            else:
                # Por defecto: EUC_2D (TSPLIB) con int(d + 0.5).
                d = euc2d_rounded(xi, yi, xj, yj)
            vec[triIndex(i, j, n)] = d
    return n, vec

def getDistance(i: int, j: int, n: int, vec: list[int]) -> int:
    """Lookup O(1) en la matriz simétrica comprimida."""
    if i == j:
        return 0
    if i > j:
        i, j = j, i
    return vec[triIndex(i, j, n)]

def tourDistance(tour: list[int], n: int, vec: list[int]) -> int:
    """Costo de un tour cerrado usando los lookups comprimidos."""
    s = 0
    for a, b in zip(tour, tour[1:]):
        s += getDistance(a, b, n, vec)
    s += getDistance(tour[-1], tour[0], n, vec)
    return s
