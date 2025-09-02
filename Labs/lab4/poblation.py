import random
from typing import List
from io_tsp import getDistance

def makeRandomTour(n: int) -> List[int]:
    """
    Crea un tour aleatorio 0..n-1 (permuta).
    """
    t = list(range(n))
    random.shuffle(t)
    return t

def _hamming_distance(a: List[int], b: List[int]) -> int:
    """
    Distancia de Hamming entre permutaciones (número de posiciones diferentes).
    """
    return sum(1 for i in range(len(a)) if a[i] != b[i])

def _avg_hamming_to_set(x: List[int], pop: List[List[int]]) -> float:
    """
    Hamming promedio del individuo x contra todos los miembros en pop.
    """
    if not pop:
        return float('inf')
    n = len(x)
    return sum(_hamming_distance(x, y) for y in pop) / len(pop)

def _strong_shuffle(t: List[int], strength: int = 8) -> None:
    """
    'Shuffle fuerte': aplica varias mutaciones simples para des-correlacionar
    las semillas heurísticas. Mezcla inserción y swap.
    """
    for _ in range(strength):
        if random.random() < 0.7:
            # insertion
            i, j = sorted(random.sample(range(len(t)), 2))
            gene = t.pop(j)
            t.insert(i, gene)
        else:
            # swap
            i, j = random.sample(range(len(t)), 2)
            t[i], t[j] = t[j], t[i]

def nearestInsertionSeed(n: int, vec: List[int]) -> List[int]:
    """
    Semilla heurística (Nearest Insertion):
    1) arranca con ciudad aleatoria y su vecino más cercano,
    2) mientras queden ciudades, elige la ciudad sin visitar más cercana
       a alguna del tour y la inserta en el lugar de menor incremento de costo.
    """
    if n <= 2:
        return list(range(n))

    start = random.randrange(n)
    # vecino más cercano a start
    nearest = min((j for j in range(n) if j != start),
                  key=lambda j: getDistance(start, j, n, vec))
    tour = [start, nearest]
    unused = set(range(n)) - set(tour)

    while unused:
        # escoger ciudad más cercana a cualquier nodo del tour
        candidate = min(unused, key=lambda u: min(getDistance(u, v, n, vec) for v in tour))

        # insertar en la posición que minimiza el incremento de costo
        best_pos, best_delta = 0, float('inf')
        L = len(tour)
        for i in range(L):
            a = tour[i]
            b = tour[(i + 1) % L]
            delta = (getDistance(a, candidate, n, vec) +
                     getDistance(candidate, b, n, vec) -
                     getDistance(a, b, n, vec))
            if delta < best_delta:
                best_delta, best_pos = delta, i + 1

        tour.insert(best_pos, candidate)
        unused.remove(candidate)

    return tour

def initPopulation(n: int, vec: List[int], N: int, seedFrac: float = 0.20) -> List[List[int]]:
    """
    MÓDULO E — Inicialización con diversidad:
    - 80% aleatorio, 20% semillas heurísticas (nearestInsertion) + shuffle fuerte.
    - Regla anti-concentración: si Hamming medio (respecto a la población actual)
      del último añadido < θ_H (= 0.2n), rehacer ese individuo (hasta MAX_TRIES).

    Devuelve una lista de N tours.
    """
    if N < 2:
        return [list(range(n))]

    num_seeds = max(1, int(N * seedFrac))
    num_random = N - num_seeds
    theta_H = 0.2 * n
    MAX_TRIES = 25

    pop: List[List[int]] = []

    # 1) Semillas heurísticas + shuffle fuerte
    for _ in range(num_seeds):
        tries = 0
        while True:
            t = nearestInsertionSeed(n, vec)
            _strong_shuffle(t, strength=8)
            avg_h = _avg_hamming_to_set(t, pop)
            if avg_h >= theta_H or tries >= MAX_TRIES:
                pop.append(t)
                break
            tries += 1

    # 2) Aleatorios (80%)
    for _ in range(num_random):
        tries = 0
        while True:
            t = makeRandomTour(n)
            avg_h = _avg_hamming_to_set(t, pop)
            if avg_h >= theta_H or tries >= MAX_TRIES:
                pop.append(t)
                break
            tries += 1

    return pop
