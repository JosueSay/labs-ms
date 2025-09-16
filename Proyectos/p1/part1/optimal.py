import os
import math
import matplotlib.pyplot as plt

# Lee un archivo .tour y devuelve la lista de nodos en el recorrido
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

# Lee un archivo .tsp y devuelve las coordenadas de los nodos
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

# Calcula distancia TSPLIB EUC_2D (redondeada a entero)
def tspDistance(a, b):
    xd = a[0] - b[0]
    yd = a[1] - b[1]
    return int(round(math.sqrt(xd*xd + yd*yd)))

# Calcula la distancia total de un tour dado (ciclo cerrado)
def resultDistance(coords, tour):
    total = 0
    for i in range(len(tour)):
        a = coords[tour[i]]
        b = coords[(tour[(i + 1) % len(tour)])]
        total += tspDistance(a, b)
    return total

# Dibuja el tour en un gráfico con matplotlib
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
    # Listar archivos en data/
    data_dir = "data"
    archivos = os.listdir(data_dir)
    print("Archivos disponibles en data/:")
    for idx, f in enumerate(archivos, 1):
        print(f"{idx}. {f}")

    # Selección por CLI
    idx_tsp = int(input("\nNúmero de archivo .tsp: ")) - 1
    idx_tour = int(input("Número de archivo .tour: ")) - 1

    ruta_tsp = os.path.join(data_dir, archivos[idx_tsp])
    ruta_tour = os.path.join(data_dir, archivos[idx_tour])

    # Procesar
    tour = readTourTSP(ruta_tour)
    coords = readCoordTSP(ruta_tsp)
    dist = resultDistance(coords, tour)

    nombre = os.path.splitext(os.path.basename(ruta_tsp))[0]
    print(f"\nDistancia total del tour: {dist}")
    graphResult(coords, tour, f"{nombre} – tour ({dist})")
