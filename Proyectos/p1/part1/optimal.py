import os
import math
import matplotlib.pyplot as plt

# Convierte grados.minutos TSPLIB a radianes (GEO).
def degminToRad(x: float) -> float:
    """Convierte un valor grados.minutos (p.ej., 68.58) a radianes según TSPLIB."""
    deg = int(x)
    minutes = x - deg
    return math.pi * (deg + 5.0 * minutes / 3.0) / 180.0

# Distancia EUC_2D TSPLIB: int(d + 0.5).
def euc2dRounded(xi: float, yi: float, xj: float, yj: float) -> int:
    """Calcula distancia EUC_2D redondeada estilo TSPLIB como int(d + 0.5)."""
    d = math.hypot(xi - xj, yi - yj)
    return int(d + 0.5)

# Distancia GEO TSPLIB con R=6378.388 y redondeo int(... + 1.0).
def geoDistance(lat_i: float, lon_i: float, lat_j: float, lon_j: float) -> int:
    """Calcula distancia GEO TSPLIB usando la fórmula oficial e int(R*acos(...)+1.0)."""
    R = 6378.388
    phi_i = degminToRad(lat_i)
    lam_i = degminToRad(lon_i)
    phi_j = degminToRad(lat_j)
    lam_j = degminToRad(lon_j)
    q1 = math.cos(lam_i - lam_j)
    q2 = math.cos(phi_i - phi_j)
    q3 = math.cos(phi_i + phi_j)
    return int(R * math.acos(0.5 * ((1.0 + q1) * q2 - (1.0 - q1) * q3)) + 1.0)

# Lee un .tsp: nombre, tipo de arista y coordenadas (dict: id -> (x,y) o (lat,lon)).
def parseTsp(path: str) -> tuple[str, str, dict[int, tuple[float, float]]]:
    """Parsea un archivo .tsp (NODE_COORD_SECTION) y devuelve (name, edgeType, coords)."""
    name = "instance"
    edge_type = "EUC_2D"
    coords: dict[int, tuple[float, float]] = {}
    in_section = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            u = s.upper()
            if u.startswith("NAME"):
                parts = s.split(":")
                if len(parts) > 1:
                    name = parts[1].strip()
            if "EDGE_WEIGHT_TYPE" in u:
                parts = s.split(":")
                if len(parts) > 1:
                    edge_type = parts[1].strip().upper()
            if u.startswith("NODE_COORD_SECTION"):
                in_section = True
                continue
            if u == "EOF":
                break
            if in_section:
                parts = s.split()
                if len(parts) >= 3:
                    i = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coords[i] = (x, y)
    return name, edge_type, coords

# Lee un .tour y devuelve la lista de nodos en orden (1-index en TSPLIB).
def readTourTsp(path: str) -> list[int]:
    """Lee un archivo .tour (TSPLIB) y devuelve la secuencia de nodos del recorrido."""
    tour: list[int] = []
    in_section = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            u = s.upper()
            if u.startswith("TOUR_SECTION"):
                in_section = True
                continue
            if not in_section:
                continue
            if s == "-1" or u == "EOF":
                break
            tour.append(int(s))
    return tour

# Calcula la distancia entre dos nodos según edge_type (EUC_2D o GEO).
def nodeDistance(p: tuple[float, float], q: tuple[float, float], edge_type: str) -> int:
    """Devuelve la distancia TSPLIB entre dos puntos según el tipo de arista."""
    if edge_type == "GEO":
        return geoDistance(p[0], p[1], q[0], q[1])
    # Por defecto EUC_2D si es desconocido.
    return euc2dRounded(p[0], p[1], q[0], q[1])

# Suma la distancia total de un tour cerrado según edge_type.
def tourDistance(coords: dict[int, tuple[float, float]], tour: list[int], edge_type: str) -> int:
    """Devuelve la distancia total del tour (ciclo) usando la métrica seleccionada."""
    total = 0
    n = len(tour)
    for idx in range(n):
        a = coords[tour[idx]]
        b = coords[tour[(idx + 1) % n]]
        total += nodeDistance(a, b, edge_type)
    return total

# Grafica el tour con opción de etiquetar nodos o no.
def graphTour(coords: dict[int, tuple[float, float]], tour: list[int], title: str,
              show_labels: bool, show_points: bool, marker_size: float = 2) -> None:
    """Dibuja el tour; opcionalmente muestra etiquetas y/o puntos (o ninguno)."""
    points = [coords[i] for i in tour] + [coords[tour[0]]]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    plt.figure()
    plt.plot(xs, ys, '-', linewidth=1)
    if show_points:
        plt.plot(xs, ys, linestyle='None', marker='o', markersize=marker_size)
    if show_labels:
        for i in tour:
            x, y = coords[i]
            plt.text(x, y, str(i), fontsize=8)

    plt.title(title)
    plt.xlabel("X / Lat"); plt.ylabel("Y / Lon")
    plt.axis('equal'); plt.tight_layout(); plt.show()


def main() -> None:
    """Provee un menú simple para elegir .tsp y .tour, calcular y graficar con o sin etiquetas."""
    data_dir = "data"
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    tsp_files = [f for f in files if f.lower().endswith(".tsp")]
    tour_files = [f for f in files if f.lower().endswith(".tour")]

    if not tsp_files:
        print("No se encontraron archivos .tsp en data/")
        return
    if not tour_files:
        print("No se encontraron archivos .tour en data/")
        return

    print("Archivos .tsp:")
    for idx, f in enumerate(tsp_files, 1):
        print(f"{idx}. {f}")
    i_tsp = int(input("\nNúmero de archivo .tsp: ")) - 1
    tsp_path = os.path.join(data_dir, tsp_files[i_tsp])

    print("\nArchivos .tour:")
    for idx, f in enumerate(tour_files, 1):
        print(f"{idx}. {f}")
    i_tour = int(input("\nNúmero de archivo .tour: ")) - 1
    tour_path = os.path.join(data_dir, tour_files[i_tour])

    name, edge_type, coords = parseTsp(tsp_path)
    tour = readTourTsp(tour_path)

    print("\nMarcado de nodos:")
    print("1) Con etiquetas (IDs)")
    print("2) Con puntos")
    print("3) Con puntos + etiquetas")
    print("4) Sin marcadores")
    opt = input("Opción (1-4): ").strip()
    show_labels = opt in ("1", "3")
    show_points = opt in ("2", "3")

    dist = tourDistance(coords, tour, edge_type)
    print(f"\nInstancia: {name} | EDGE_WEIGHT_TYPE: {edge_type}")
    print(f"Distancia total del tour: {dist}")

    title = f"{name} - tour ({edge_type}, {dist})"
    graphTour(coords, tour, title, show_labels, show_points, marker_size=2)

if __name__ == "__main__":
    main()
