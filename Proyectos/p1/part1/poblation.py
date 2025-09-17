import random
from io_tsp import getDistance

def makeRandomTour(n: int) -> list[int]:
    if n <= 0:
        raise ValueError("n debe ser > 0")
    t = list(range(n))
    random.shuffle(t)
    return t

def nearestInsertionSeed(n: int, vec: list[int]) -> list[int]:
    """
    Variante con mantenimiento incremental de d_to_tour:
    - d_to_tour[j] = min distancia de la ciudad j a cualquier ciudad del tour actual.
    - Al insertar una ciudad c, solo actualizamos d_to_tour[j] = min(d_to_tour[j], d(j,c)).
    """
    if n < 3:
        # Tours triviales
        return list(range(n))

    start = random.randrange(n)
    tour = [start]
    remaining = set(range(n))
    remaining.remove(start)

    # segunda ciudad: más cercana a 'start'
    nearest = min(remaining, key=lambda j: getDistance(start, j, n, vec))
    tour.append(nearest)
    remaining.remove(nearest)

    # 'start' al final para evaluar inserciones en el lazo cerrado; se quita al final
    tour.append(start)

    # inicializar distancias mínimas al tour actual (start y nearest)
    d_to_tour = {}
    for j in remaining:
        d_to_tour[j] = min(
            getDistance(j, start, n, vec),
            getDistance(j, nearest, n, vec)
        )

    while remaining:
        # ciudad más "cercana" al tour (definición de nearest-insertion)
        c = min(remaining, key=lambda j: d_to_tour[j])

        # escoger mejor posición para insertar c (cheapest insertion)
        best_pos, best_inc = 0, float("inf")
        for k in range(len(tour) - 1):
            i, j = tour[k], tour[k + 1]
            inc = (getDistance(i, c, n, vec) +
                   getDistance(c, j, n, vec) -
                   getDistance(i, j, n, vec))
            if inc < best_inc:
                best_inc = inc
                best_pos = k + 1

        tour.insert(best_pos, c)
        remaining.remove(c)

        # actualizar d_to_tour sólo contra la ciudad recién insertada
        for j in remaining:
            dij = getDistance(j, c, n, vec)
            if dij < d_to_tour[j]:
                d_to_tour[j] = dij

    tour.pop()  # quitar el 'start' duplicado del cierre
    return tour

def initPopulation(n: int, vec: list[int], N: int, seedFrac: float = 0.25) -> list[list[int]]:
    if N <= 0:
        raise ValueError("N debe ser > 0")
    # clamp seedFrac
    seedFrac = max(0.0, min(1.0, float(seedFrac)))
    seedFrac = min(seedFrac, 0.25 if n < 200 else 0.10)


    # (opcional) limitar seeds cuando n es grande para evitar coste alto
    # p. ej.: seedFrac = min(seedFrac, 0.25 if n < 200 else 0.10)

    k = max(1, int(N * seedFrac))
    pop = [nearestInsertionSeed(n, vec) for _ in range(k)]
    pop += [makeRandomTour(n) for _ in range(N - k)]

    # deduplicar (mantener orden) y rellenar con tours aleatorios distintos
    seen = set()
    uniq = []
    for t in pop:
        key = tuple(t)
        if key not in seen:
            seen.add(key)
            uniq.append(t)

    while len(uniq) < N:
        t = makeRandomTour(n)
        key = tuple(t)
        if key not in seen:
            seen.add(key)
            uniq.append(t)

    return uniq
