# Proyectos/p1/part2/tsp_pulp.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../part1")))

import time
import csv
import pulp
import numpy as np
from io_tsp import parseTsp, buildDistanceMatrixCompressed, getDistance


def build_full_distance(n, vec):
    """Expande el vector comprimido (triángulo sup) a una matriz simétrica n x n."""
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            dij = getDistance(i, j, n, vec)
            D[i, j] = D[j, i] = float(dij)
    return D


def solve_tsp_pulp(D, time_limit=3600, msg=1):
    """
    Resuelve TSP (formulación MTZ) con PuLP/CBC.
    - time_limit: segundos máximos para CBC (por instancia).
    """
    n = D.shape[0]
    prob = pulp.LpProblem("TSP", pulp.LpMinimize)

    # Variables
    x = pulp.LpVariable.dicts(
        "x",
        ((i, j) for i in range(n) for j in range(n) if i != j),
        cat="Binary"
    )
    u = pulp.LpVariable.dicts(
        "u",
        (i for i in range(n)),
        lowBound=0,
        upBound=n - 1,
        cat="Continuous"
    )

    # Objetivo
    prob += pulp.lpSum(D[i, j] * x[(i, j)] for i in range(n) for j in range(n) if i != j)

    # Restricciones de entrada/salida
    for i in range(n):
        prob += pulp.lpSum(x[(i, j)] for j in range(n) if j != i) == 1
        prob += pulp.lpSum(x[(j, i)] for j in range(n) if j != i) == 1

    # Restricciones MTZ (eliminan subciclos)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[(i, j)] <= n - 1

    # Solver con límite de tiempo
    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit)

    t0 = time.time()
    prob.solve(solver)
    seconds = time.time() - t0

    status_str = pulp.LpStatus[prob.status]
    obj = float(pulp.value(prob.objective)) if pulp.value(prob.objective) is not None else float("nan")

    # Reconstrucción del tour
    def is_one(v): return v is not None and v > 0.5
    succ = [-1] * n
    for i in range(n):
        for j in range(n):
            if i != j and is_one(pulp.value(x.get((i, j)))):
                succ[i] = j
                break

    tour = []
    if all(s != -1 for s in succ):
        start = 0
        cur = start
        for _ in range(n):
            tour.append(cur)
            cur = succ[cur]
            if cur == start:
                break
        if len(tour) != n or succ[tour[-1]] != start:
            tour = []

    return {"status": status_str, "objective": obj, "seconds": seconds, "tour": tour}


def run_instances(instances, data_dir, csv_out="pulp_results.csv", time_limit=3600, msg=1):
    """Corre las instancias y guarda resultados en CSV."""
    rows = []
    os.makedirs(os.path.dirname(csv_out) or ".", exist_ok=True)

    for fname in instances:
        tsp_path = os.path.join(data_dir, fname)
        print(f"\n=== Resolviendo {fname} ===")
        name, edge_type, coords = parseTsp(tsp_path)
        n, vec = buildDistanceMatrixCompressed(coords, edge_type)
        D = build_full_distance(n, vec)

        res = solve_tsp_pulp(D, time_limit=time_limit, msg=msg)

        print(f"Instancia: {name} | EDGE_WEIGHT_TYPE: {edge_type} | n={n}")
        print(f"Status: {res['status']}")
        print(f"Objective: {res['objective']:.6f}")
        print(f"Tiempo (s): {res['seconds']:.2f}")
        if res["tour"]:
            print(f"Tour (0-index): {res['tour']} (cerrado en {res['tour'][0]})")
        else:
            print("Tour: (no reconstruido o solución parcial)")

        rows.append({
            "instance": name,
            "nCities": n,
            "edgeType": edge_type,
            "status": res["status"],
            "objective": f"{res['objective']:.6f}",
            "seconds": f"{res['seconds']:.2f}"
        })

    # Guardar CSV
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["instance", "nCities", "edgeType", "status", "objective", "seconds"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"\n[OK] CSV guardado en: {csv_out}")


def main():
    data_dir = "Proyectos/p1/part1/data"
    instances = ["cherry189.tsp", "eil101.tsp", "gr229.tsp"]

    run_instances(
        instances=instances,
        data_dir=data_dir,
        csv_out="Proyectos/p1/part2/pulp_results.csv",
        time_limit=3600,   # 1 hora por instancia
        msg=1
    )


if __name__ == "__main__":
    main()
