import random
from typing import List
from io_tsp import getDistance

def hamming_distance(a: List[int], b: List[int]) -> int:
    """Distancia de Hamming entre dos permutaciones."""
    return sum(1 for x, y in zip(a, b) if x != y)

def mean_hamming(pop: List[List[int]]) -> float:
    """Hamming medio entre individuos (usa muestra si N es grande)."""
    N = len(pop)
    if N < 2:
        return 0.0
    idxs = random.sample(range(N), k=min(N, 80))
    pairs = 0
    acc = 0
    for i in range(len(idxs) - 1):
        a = pop[idxs[i]]
        b = pop[idxs[i + 1]]
        acc += hamming_distance(a, b)
        pairs += 1
    return (acc / pairs) if pairs > 0 else 0.0

def makeRandomTour(n: int) -> List[int]:
    """Genera un tour aleatorio (80% de la población inicial)."""
    t = list(range(n))
    random.shuffle(t)
    return t

def nearest_neighbor_seed(n: int, vec: List[int]) -> List[int]:
    """Construye un tour heurístico con nearest-neighbor."""
    start = random.randrange(n)
    tour = [start]
    unused = set(range(n))
    unused.remove(start)
    curr = start
    while unused:
        nxt = min(unused, key=lambda j: getDistance(curr, j, n, vec))
        tour.append(nxt)
        unused.remove(nxt)
        curr = nxt
    return tour

def strong_shuffle(t: List[int]) -> None:
    """Aplica varios swaps/insertions para diversificar una semilla."""
    L = len(t)
    ops = max(3, L // 10)
    for _ in range(ops):
        if random.random() < 0.6:
            i, j = sorted(random.sample(range(L), 2))
            gene = t.pop(j)
            t.insert(i, gene)
        else:
            i, j = random.sample(range(L), 2)
            t[i], t[j] = t[j], t[i]

def initPopulation(n: int, vec: List[int], N: int, seedFrac: float = 0.25) -> List[List[int]]:
    """
    MÓDULO E — Inicialización de población:
      - 80% random tours.
      - 20% semillas heurísticas NN con shuffle fuerte.
      - Regla anti-concentración: rehacer últimos si hamming medio < 0.2n.
    """
    if N <= 0:
        return []
    num_seed = max(1, int(N * 0.20))
    num_rand = max(0, N - num_seed)
    pop: List[List[int]] = []
    for _ in range(num_rand):
        pop.append(makeRandomTour(n))
    for _ in range(num_seed):
        t = nearest_neighbor_seed(n, vec)
        strong_shuffle(t)
        pop.append(t)

    theta_H = int(0.2 * n)
    for _ in range(3):  # intentar hasta 3 veces aumentar diversidad
        mh = mean_hamming(pop)
        if mh >= theta_H:
            break
        k = max(1, int(0.1 * N))
        for i in range(1, k + 1):
            pop[-i] = makeRandomTour(n)

    return pop
