import pulp
import numpy as np

def read_coords(filename):
    """Lee coordenadas de un archivo .tsp simple (formato TSPLIB)."""
    coords = []
    with open(filename) as f:
        start = False
        for line in f:
            if "NODE_COORD_SECTION" in line:
                start = True
                continue
            if start:
                if "EOF" in line or line.strip() == "":
                    break
                parts = line.strip().split()
                if len(parts) >= 3:
                    coords.append((float(parts[1]), float(parts[2])))
    return np.array(coords)

def calc_dist_matrix(coords):
    n = len(coords)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                D[i, j] = np.linalg.norm(coords[i] - coords[j])
    return D

def solve_tsp_pulp(D):
    n = D.shape[0]
    prob = pulp.LpProblem("TSP", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(n) if i != j), cat="Binary")
    u = pulp.LpVariable.dicts("u", (i for i in range(n)), lowBound=0, upBound=n-1, cat="Continuous")

    # Objetivo
    prob += pulp.lpSum(D[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j)

    # Restricciones de entrada/salida
    for i in range(n):
        prob += pulp.lpSum(x[i, j] for j in range(n) if i != j) == 1
        prob += pulp.lpSum(x[j, i] for j in range(n) if i != j) == 1

    # Restricciones MTZ para eliminar subciclos
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    # Resolver
    solver = pulp.PULP_CBC_CMD(msg=1)
    prob.solve(solver)

    # Extraer solución
    tour = []
    visited = set()
    current = 0
    for _ in range(n):
        for j in range(n):
            if current != j and pulp.value(x[current, j]) > 0.5:
                tour.append(current)
                visited.add(current)
                current = j
                break
    tour.append(current)  # Regresar al inicio

    cost = pulp.value(prob.objective)
    return tour, cost

def main():
    # Escenario 1: instancia pequeña
    coords1 = read_coords("Proyectos/p1/part1/data/berlin52.tsp")
    D1 = calc_dist_matrix(coords1)
    tour1, cost1 = solve_tsp_pulp(D1)
    print("Escenario 1 (berlin52):")
    print("Tour:", tour1)
    print("Costo:", cost1)
    print()

    # Escenario 2: instancia personalizada 
    coords2 = read_coords("Proyectos/p1/part1/data/cherry189.tsp")
    D2 = calc_dist_matrix(coords2)
    tour2, cost2 = solve_tsp_pulp(D2)
    print("Escenario 2 (cherry189):")
    print("Tour:", tour2)
    print("Costo:", cost2)
    print()

    # Escenario 3: instancia mediana 
    coords3 = read_coords("Proyectos/p1/part1/data/eil101.tsp")
    D3 = calc_dist_matrix(coords3)
    tour3, cost3 = solve_tsp_pulp(D3)
    print("Escenario 3 (eil101):")
    print("Tour:", tour3)
    print("Costo:", cost3)
    print()

if __name__ == "__main__":
    main()