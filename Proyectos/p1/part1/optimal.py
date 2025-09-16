import math
import matplotlib.pyplot as plt

def readTourTSP(ruta_tour):
    tour = []
    in_section = False
    with open(ruta_tour, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith("TOUR_SECTION"):
                in_section = True
                continue
            if not in_section:
                continue
            if line == "-1" or line.upper() == "EOF":
                break
            tour.append(int(line))
    return tour

def readCoordTSP(ruta_tsp):
    coords = {}
    in_section = False
    with open(ruta_tsp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            u = line.upper()
            if u.startswith("NODE_COORD_SECTION"):
                in_section = True
                continue
            if not in_section:
                continue
            if u == "EOF":
                break
            partes = line.split()
            if len(partes) >= 3:
                i = int(partes[0])
                x = float(partes[1])
                y = float(partes[2])
                coords[i] = (x, y)
    return coords

def tspDistance(a, b):
    # distancia TSPLIB EUC_2D (redondeada)
    xd = a[0] - b[0]
    yd = a[1] - b[1]
    return int(round(math.sqrt(xd*xd + yd*yd)))

def resultDistance(coords, tour):
    total = 0
    for i in range(len(tour)):
        a = coords[tour[i]]
        b = coords[tour[(i + 1) % len(tour)]]
        total += tspDistance(a, b)
    return total

def graphResult(coords, tour, titulo="Solución TSP"):
    puntos = [coords[i] for i in tour] + [coords[tour[0]]]
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]

    plt.figure()
    plt.plot(xs, ys, marker='o', linewidth=1)
    for i in tour:
        x, y = coords[i]
        plt.text(x, y, str(i), fontsize=8)
    plt.title(titulo)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    
    ruta_tsp = "data/berlin52.tsp"
    ruta_tour = "data/berlin52.opt.tour"
    
    # ruta_tsp = "data/eil101.tsp"
    # ruta_tour = "data/eil101.opt.tour"

    tour = readTourTSP(ruta_tour)
    coords = readCoordTSP(ruta_tsp)

    dist = resultDistance(coords, tour)
    print(f"Distancia total del tour: {dist}")

    graphResult(coords, tour, f"berlin52 – tour óptimo ({dist})")
    # graphResult(coords, tour, f"eil101 – tour óptimo ({dist})")
