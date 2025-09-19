from typing import Callable
import random, time, os, csv, heapq
from concurrent.futures import ProcessPoolExecutor

from io_tsp import getDistance, parseTsp, buildDistanceMatrixCompressed, tourDistance
from poblation import initPopulation, makeRandomTour
from viz import saveFrame

# ---------- Globals compartidos con los workers 2-opt ----------
G_n = None
G_vec = None
G_neighbors = None
G_useFlocking = True

def initTwoOptGlobals(n, vec, neighbors, useFlocking=True):
    """Inicializador del pool de procesos (memoria compartida vía globals)."""
    global G_n, G_vec, G_neighbors, G_useFlocking
    G_n, G_vec, G_neighbors, G_useFlocking = n, vec, neighbors, useFlocking

def twoOptWorker(t):
    """Mejora local acotada (first-improve) en proceso separado."""
    t = t[:]
    for _ in range(12):
        if not apply2optOnce(t, G_n, G_vec, neighbors=G_neighbors, first_improve=True, useFlocking=G_useFlocking):
            break
    return t

# ---------- Operadores y utilidades deterministas ----------
def doubleBridgeKick(t):
    """Diversificación estilo Lin-Kernighan (double-bridge). Determinista por seed."""
    L = len(t)
    a, b, c, d = sorted(random.sample(range(L), 4))
    A, B, C, D, E = t[:a], t[a:b], t[b:c], t[c:d], t[d:]
    return A + D + C + B + E

def selectionTournament(pop: list[list[int]], fitness: Callable[[list[int]], int], k: int, num: int) -> list[list[int]]:
    """Selección por torneo. Determinista por seed (random.sample usa RNG)."""
    sel = []
    for _ in range(num):
        cand = random.sample(pop, k)
        sel.append(min(cand, key=lambda t: (fitness(t), tuple(t)))[:])  # empates estables
    return sel

def crossoverOX(p1: list[int], p2: list[int]) -> list[int]:
    """Order Crossover (OX)."""
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [-1] * n
    child[a:b+1] = p1[a:b+1]
    fill = [x for x in p2 if x not in child]
    idx = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = fill[idx]; idx += 1
    return child

# ======== Helpers de aristas / diversidad / emparejamiento ========
def edgeKey(u, v):
    return (u, v) if u < v else (v, u)

def buildEdgeSet(tour):
    n = len(tour)
    E = []
    for a, b in zip(tour, tour[1:]):
        E.append(edgeKey(a, b))
    E.append(edgeKey(tour[-1], tour[0]))
    return frozenset(E)

def jaccardEdgeDistance(Ea, Eb):
    # 1 - |A∩B|/|A∪B|
    inter = len(Ea & Eb)
    union = len(Ea | Eb)
    return 1.0 - (inter / union if union else 0.0)

def buildEdgeHistogram(pop, topFrac=0.30):
    """Frecuencia normalizada de aristas en el top de la población (ya ordenada)."""
    top = max(1, int(len(pop) * topFrac))
    freq = {}
    for t in pop[:top]:
        eSet = buildEdgeSet(t)
        for e in eSet:
            freq[e] = freq.get(e, 0) + 1
    norm = float(top)
    for k in list(freq.keys()):
        freq[k] = freq[k] / norm
    return freq

def assortativePairs(parents, numPairs, edgeSets=None):
    """Empareja por máxima lejanía de aristas (determinista por orden estable)."""
    pairs = []
    rem = parents[:]
    if edgeSets is None:
        edgeSets = {id(t): buildEdgeSet(t) for t in rem}
    while len(pairs) < numPairs and len(rem) >= 2:
        p1 = rem.pop(0)
        e1 = edgeSets[id(p1)]
        best = None
        bestKey = None
        for candidate in rem:
            d = jaccardEdgeDistance(e1, edgeSets[id(candidate)])
            key = (d, tuple(candidate))
            if best is None or key > bestKey:
                best, bestKey = candidate, key
        rem.remove(best)
        pairs.append((p1, best))
    return pairs

def eaxLite(p1: list[int], p2: list[int], n: int, vec: list[int], neighbors=None) -> list[int]:
    """
      - Alterna aristas de p1 y p2 (next/prev) para construir el hijo.
      - Si los candidatos del padre activo están usados, intenta con el otro padre.
      - Si sigue vacío, recurre a KNN; si aún así no hay, usa todos los no usados.
      - Empates rotos por (dist, idx) para estabilidad.
    """
    # Adyacencias (siguiente y anterior) de ambos padres
    next1 = {p1[i]: p1[(i + 1) % n] for i in range(n)}
    prev1 = {p1[(i + 1) % n]: p1[i] for i in range(n)}
    next2 = {p2[i]: p2[(i + 1) % n] for i in range(n)}
    prev2 = {p2[(i + 1) % n]: p2[i] for i in range(n)}

    child = [p1[0]]
    used = {p1[0]}
    cur = p1[0]
    use_from_p1 = True  # alternamos entre p1 y p2

    while len(child) < n:
        cands = []

        # 1) Intentar con el padre activo (next y prev)
        if use_from_p1:
            for nxt in (next1[cur], prev1[cur]):
                if nxt not in used:
                    cands.append(nxt)
        else:
            for nxt in (next2[cur], prev2[cur]):
                if nxt not in used:
                    cands.append(nxt)

        # 2) Si vacío, intentar con el otro padre
        if not cands:
            if use_from_p1:
                for nxt in (next2[cur], prev2[cur]):
                    if nxt not in used:
                        cands.append(nxt)
            else:
                for nxt in (next1[cur], prev1[cur]):
                    if nxt not in used:
                        cands.append(nxt)

        # 3) Si vacío y hay KNN, tomar algunos vecinos no usados
        if not cands and neighbors is not None:
            cands = [j for j in neighbors[cur] if j not in used][:8]

        # 4) Si aún vacío, caer a TODOS los no usados
        if not cands:
            unused = (set(range(n)) - used)
            nxt = min(unused, key=lambda j: (getDistance(cur, j, n, vec), j))
        else:
            nxt = min(cands, key=lambda j: (getDistance(cur, j, n, vec), j))

        child.append(nxt)
        used.add(nxt)
        cur = nxt
        use_from_p1 = not use_from_p1  # alternar

    return child

# ======== SCX con Edge-Histogram ========
def crossoverSCX(p1: list[int], p2: list[int], n: int, vec: list[int],
                 edgeFreq=None, edgeLambda=0.15) -> list[int]:
    """SCX con desempate determinista por índice, sesgado por histograma de aristas."""
    current = p1[0]
    child = [current]
    unused = set(range(n)) - {current}
    next1 = {p1[i]: p1[(i+1) % n] for i in range(n)}
    next2 = {p2[i]: p2[(i+1) % n] for i in range(n)}

    def score(u, v):
        base = getDistance(u, v, n, vec)
        if edgeFreq:
            base -= edgeLambda * edgeFreq.get(edgeKey(u, v), 0.0)
        return (base, v)  # desempate por índice

    while unused:
        cands = []
        for nxt in (next1[current], next2[current]):
            if nxt in unused:
                cands.append(nxt)
        if cands:
            nxt = min(cands, key=lambda j: score(current, j))
        else:
            nxt = min(unused, key=lambda j: score(current, j))
        child.append(nxt)
        unused.remove(nxt)
        current = nxt
    return child

def mutateInsertion(t: list[int]) -> None:
    """Inserción (determinista por seed)."""
    n = len(t)
    i, j = sorted(random.sample(range(n), 2))
    gene = t.pop(j)
    t.insert(i, gene)

def mutateSwap(t: list[int]) -> None:
    """Swap simple (determinista por seed)."""
    i, j = random.sample(range(len(t)), 2)
    t[i], t[j] = t[j], t[i]

def apply2optOnce(t, n, vec, neighbors=None, first_improve=False, useFlocking=True):
    """Un paso 2-opt. Con KNN opcional. Empates rotos por índice/“flocking” para estabilidad/calidad."""
    best_delta = 0
    best_move = None  # (i1, j, tieScore)
    L = len(t)
    for i in range(L - 1):
        a, b = t[i], t[(i + 1) % L]
        for j in range(i + 2, L if i > 0 else L - 1):
            c, d = t[j % L], t[(j + 1) % L]
            if neighbors is not None:
                if not ((c in neighbors[a]) or (d in neighbors[a]) or (c in neighbors[b]) or (d in neighbors[b])):
                    continue
            # delta y tie-break “flocking” (preferir menor arista añadida)
            new1 = getDistance(a, c, n, vec)
            new2 = getDistance(b, d, n, vec)
            old1 = getDistance(a, b, n, vec)
            old2 = getDistance(c, d, n, vec)
            delta = (new1 + new2) - (old1 + old2)
            tieScore = max(new1, new2) if useFlocking else 0

            if first_improve and delta < 0:
                i1 = i + 1
                if i1 < j:
                    t[i1:j+1] = reversed(t[i1:j+1])
                else:
                    seg = (t[i1:] + t[:j+1])[::-1]
                    m = len(t) - i1
                    t[i1:] = seg[:m]; t[:j+1] = seg[m:]
                return True
            if (delta < best_delta) or (delta == best_delta and best_move and tieScore < best_move[2]):
                best_delta = delta; best_move = (i + 1, j, tieScore)
    if best_move:
        i1, j, _ = best_move
        if i1 < j:
            t[i1:j+1] = reversed(t[i1:j+1])
        else:
            seg = (t[i1:] + t[:j+1])[::-1]
            m = len(t) - i1
            t[i1:] = seg[:m]; t[:j+1] = seg[m:]
        return True
    return False

# ======== 3-opt ========
def apply3optOnce(t, n, vec, neighbors=None):
    """Una iteración 3-opt first-improve con KNN. Retorna True/False si aplicó."""
    L = len(t)
    # probamos dos variantes simples
    for i in range(L - 2):
        a, b = t[i], t[(i + 1) % L]
        for j in range(i + 1, L - 1):
            c, d = t[j % L], t[(j + 1) % L]
            if neighbors is not None:
                if (c not in neighbors[a]) and (d not in neighbors[a]) and (c not in neighbors[b]) and (d not in neighbors[b]):
                    continue
            for k in range(j + 1, L if i > 0 else L - 1):
                e, f = t[k % L], t[(k + 1) % L]
                # v1: revertir (b..c) y (d..e)
                delta1 = (
                    getDistance(a, c, n, vec) + getDistance(b, d, n, vec) + getDistance(e, f, n, vec)
                    - getDistance(a, b, n, vec) - getDistance(c, d, n, vec) - getDistance(e, f, n, vec)
                )
                if delta1 < 0:
                    i1 = i + 1
                    t[i1:j+1] = reversed(t[i1:j+1])
                    t[j+1:k+1] = reversed(t[j+1:k+1])
                    return True
                # v2: revertir (b..e)
                delta2 = (
                    getDistance(a, e, n, vec) + getDistance(b, f, n, vec) + getDistance(c, d, n, vec)
                    - getDistance(a, b, n, vec) - getDistance(e, f, n, vec) - getDistance(c, d, n, vec)
                )
                if delta2 < 0:
                    seg = t[i+1:k+1]; seg.reverse()
                    t[i+1:k+1] = seg
                    return True
    return False

# ---------- Trace CSV ----------
def openTrace(path: str, header: list[str]):
    if not path:
        return None, None
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    f = open(path, "w", newline="", encoding="utf-8")
    w = csv.writer(f)
    w.writerow(header)
    return f, w

def writeTrace(writer, row: list):
    if writer:
        writer.writerow(row)

# ===========================================================
#                  EJECUCIÓN DEL GA (RUNNER)
# ===========================================================
def runGa(coordsPath: str,
          N: int = 300,
          maxIter: int = 1500,
          survivorsFrac: float = 0.2,
          crossoverFrac: float = 0.6,
          mutationFrac: float = 0.2,
          pc: float = 0.95,
          pm: float = None,
          elitismFrac: float = 0.05,
          tournamentK: int = 5,
          useSCX: bool = True,
          twoOptProb: float = 0.05,
          stallGenerations: int = 400,
          timeLimitSec: float = 0.0,
          recordImprovements: bool = False,
          framesDir: str = "frames",
          seed: int = 42,
          trace_csv: str | None = None,
          eaxFrac: float = 0.15,
          edgeLambda: float = 0.15,
          edgeTopFrac: float = 0.30,
          edgeFreqPeriod: int = 200,
          assortative: bool = True,
          mem3OptSteps: int = 4,
          speciesPeriod: int = 800,
          speciesThresh: float = 0.35,
          speciesCullFrac: float = 0.20,
          catastropheFrac: float = 0.20,
          useFlocking: bool = True
          ) -> dict:

    # ---------- Validaciones y semilla ----------
    assert abs((survivorsFrac + crossoverFrac + mutationFrac) - 1.0) < 1e-6, "S%+C%+M% debe ser 1.0"
    if N < 10:
        raise ValueError("N muy pequeño (mínimo recomendado 10)")
    random.seed(seed)

    # ---------- Parseo y matriz de distancias ----------
    tBuild0 = time.time()
    name, edgeType, coords = parseTsp(coordsPath)
    n, vec = buildDistanceMatrixCompressed(coords, edgeType)
    tParseBuild = time.time() - tBuild0

    # ---------- Dimensión LP teórica ----------
    # TSP no dirigido: variables de aristas (i<j) = n*(n-1)/2, restricciones de grado = n
    lpEdgeVars = n * (n - 1) // 2
    lpDegreeCons = n

    # ---------- Trace ----------
    tracePath = trace_csv
    header = [
        "event","gen","elapsedSec","bestCost","delta","popBestCost","poolSize",
        "instance","edgeType","nCities","populationN","maxIter",
        "survivorsFrac","crossoverFrac","mutationFrac",
        "pc","pm","elitismFrac","tournamentK","useSCX","twoOptProb",
        "stallGenerations","timeLimitSec","seed",
        "lpEdgeVars","lpDegreeCons"
    ]
    traceFile, traceWriter = openTrace(tracePath, header)

    # ---------- KNN para filtrar 2-opt (heap: O(n log k)) ----------
    def buildKnn(n, vec, k=20):
        neigh = [None] * n
        for i in range(n):
            cand = ((getDistance(i, j, n, vec), j) for j in range(n) if j != i)
            topk = heapq.nsmallest(k, cand)  # no ordena todo
            neigh[i] = [j for _, j in topk]
        return neigh

    tKnn0 = time.time()
    neighbors = buildKnn(n, vec, k=30 if n >= 200 else 20)
    tKnn = time.time() - tKnn0

    # ---------- Pool de procesos para 2-opt ----------
    workers = max(1, (os.cpu_count() or 2) - 1)
    executor = ProcessPoolExecutor(
        max_workers=workers,
        initializer=initTwoOptGlobals,
        initargs=(n, vec, neighbors, useFlocking)
    )

    # ---------- Reloj global ----------
    t0 = time.time()

    # ---------- Perfilador ----------
    prof = {
        "elitist_memetic": 0.0,
        "memetic_3opt": 0.0,
        "selection": 0.0,
        "assortative": 0.0,
        "crossover": 0.0,
        "crossover_eax": 0.0,
        "mutation_pure": 0.0,
        "mutation_light": 0.0,
        "twoopt_pool": 0.0,
        "edge_hist": 0.0,
        "speciation": 0.0,
        "catastrophe": 0.0,
        "anticlones": 0.0,
        "sort": 0.0,
    }
    tInit = 0.0

    # ---------- Parámetros base (constantes, no pisar CLI) ----------
    if pm is None:
        pm = max(1.0/n, 0.002)
    elif pm == -1:
        pm = 1.0/n
    basePm = pm
    baseTwoOpt = twoOptProb
    baseK = tournamentK

    # ---------- Cache de costos ----------
    fitnessCache = {}
    def fitness(t):
        key = tuple(t)
        c = fitnessCache.get(key)
        if c is None:
            c = tourDistance(t, n, vec)
            fitnessCache[key] = c
        return c

    # ---------- Resumen de arranque ----------
    print(
        "\n=== RUN GA =================================================\n"
        f"\tInstancia:\t{name}\n"
        f"\tN:\t\t{N}\n"
        f"\tmaxIter:\t{maxIter}\n"
        f"\tS/C/M:\t\t{survivorsFrac:.2f} / {crossoverFrac:.2f} / {mutationFrac:.2f}\n"
        f"\tpc / pm:\t{pc:.2f} / {pm:.4f}\n"
        f"\telitismo:\t{elitismFrac:.2f}\n"
        f"\tselección:\ttorneo k={tournamentK}\n"
        f"\tcruce:\t\t{'SCX' if useSCX else 'OX'}\n"
        f"\t2-optProb:\t{twoOptProb:.2f}\n"
        "-----------------------------------------------------------"
    )

    # ---------- Población inicial ----------
    tInit0 = time.time()
    pop = initPopulation(n, vec, N, seedFrac=0.25)
    pop.sort(key=lambda t: (fitness(t), tuple(t)))
    tInit = time.time() - tInit0

    best = pop[0][:]
    bestCost = fitness(best)
    history = [bestCost]
    events = [{"gen": 0, "bestCost": bestCost, "tour": best[:], "elapsedSec": 0.0}]

    print(f"\n[gen 0]\n\tbest:\t\t{bestCost}\n\tciudades:\t{n}\n-----------------------------------------------------------")

    # fila meta (una sola vez)
    writeTrace(traceWriter, [
        "meta", 0, f"{0.0:.6f}", bestCost, "", bestCost, "",
        name, edgeType, n, N, maxIter,
        f"{survivorsFrac:.6f}", f"{crossoverFrac:.6f}", f"{mutationFrac:.6f}",
        f"{pc:.6f}", f"{pm:.6f}", f"{elitismFrac:.6f}", tournamentK, int(bool(useSCX)), f"{twoOptProb:.6f}",
        stallGenerations, f"{timeLimitSec:.6f}", seed,
        lpEdgeVars, lpDegreeCons
    ])

    if recordImprovements:
        os.makedirs(framesDir, exist_ok=True)
        saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)

    # ---------- Tamaños de operadores ----------
    S = max(1, int(N * survivorsFrac))
    C = max(0, int(N * crossoverFrac))
    M = max(0, N - S - C)
    elites = max(1, int(N * elitismFrac))

    # ---------- Estado Edge-Histogram ----------
    tEH0 = time.time()
    edgeFreq = buildEdgeHistogram(pop, topFrac=edgeTopFrac)
    prof["edge_hist"] += time.time() - tEH0
    nextEdgeFreqUpdate = edgeFreqPeriod
    edgeSetCache = {}  # cache para emparejamiento / especies

    species = None
    def rebuildSpecies():
        nonlocal species
        tSP0 = time.time()
        reps = []  # [(rep_edgeSet, indices)]
        species = []
        for idx, t in enumerate(pop):
            Et = edgeSetCache.get(id(t))
            if Et is None:
                Et = buildEdgeSet(t); edgeSetCache[id(t)] = Et
            assigned = False
            for k, (Er, members) in enumerate(reps):
                if jaccardEdgeDistance(Et, Er) <= speciesThresh:
                    members.append(idx); assigned = True; break
            if not assigned:
                reps.append((Et, [idx]))
        species = [m for _, m in reps]
        prof["speciation"] += time.time() - tSP0

    noImprove = 0

    try:
        for gen in range(1, maxIter + 1):
            # Mantener constantes los parámetros elegidos por CLI
            pm = basePm
            twoOptProb = baseTwoOpt
            tournamentK = baseK

            # ---------- Sobrevivientes + memético suave periódico ----------
            survivors = pop[:S]
            if gen % 300 == 0:
                tM0 = time.time()
                for e in survivors[:2]:   # menos trabajo
                    # 2-opt
                    steps = 0
                    while steps < 8 and apply2optOnce(e, n, vec, neighbors=neighbors, first_improve=True, useFlocking=useFlocking):
                        steps += 1
                prof["elitist_memetic"] += time.time() - tM0

                # 3-opt acotado
                t3o0 = time.time()
                for e in survivors[:2]:
                    steps3 = 0
                    while steps3 < mem3OptSteps and apply3optOnce(e, n, vec, neighbors=neighbors):
                        steps3 += 1
                prof["memetic_3opt"] += time.time() - t3o0

            # ---------- Selección ----------
            parentsNeeded = max(C * 2, 2)
            tS0 = time.time()
            parents = selectionTournament(pop, fitness, tournamentK, parentsNeeded)
            prof["selection"] += time.time() - tS0

            # ---------- Emparejamiento assortative ----------
            pairsNeeded = max(1, C)
            tAS0 = time.time()
            if assortative:
                for t in parents:
                    if id(t) not in edgeSetCache:
                        edgeSetCache[id(t)] = buildEdgeSet(t)
                pairs = assortativePairs(parents, pairsNeeded, edgeSets=edgeSetCache)
            else:
                pairs = [(parents[i % len(parents)], parents[(i + 1) % len(parents)]) for i in range(0, pairsNeeded)]
            prof["assortative"] += time.time() - tAS0

            # ---------- Cruce ----------
            tC0 = time.time()
            childrenC = []
            eaxBudget = int(eaxFrac * pairsNeeded)
            tEAX = 0.0
            for idx, (p1, p2) in enumerate(pairs):
                if random.random() < pc:
                    if idx < eaxBudget:
                        t0_eax = time.time()
                        child = eaxLite(p1, p2, n, vec, neighbors)
                        tEAX += (time.time() - t0_eax)
                    else:
                        if useSCX:
                            child = crossoverSCX(p1, p2, n, vec, edgeFreq=edgeFreq, edgeLambda=edgeLambda)
                        else:
                            child = crossoverOX(p1, p2)
                else:
                    child = p1[:]
                childrenC.append(child)
            prof["crossover"] += time.time() - tC0
            prof["crossover_eax"] += tEAX

            # ---------- Mutación pura ----------
            tMp0 = time.time()
            childrenM = []
            for _ in range(M):
                base = random.choice(pop)[:]
                (mutateInsertion if random.random() < 0.5 else mutateSwap)(base)
                childrenM.append(base)
            prof["mutation_pure"] += time.time() - tMp0

            # ---------- Mutación ligera ----------
            tMl0 = time.time()
            for ch in childrenC:
                if random.random() < pm:
                    (mutateInsertion if random.random() < 0.7 else mutateSwap)(ch)
            prof["mutation_light"] += time.time() - tMl0

            # ---------- 2-opt pool paralelo (top por fitness) ----------
            t2o0 = time.time()
            lastPoolSize = 0
            if twoOptProb > 0.0:
                totalChildren = len(childrenC) + len(childrenM)
                poolSize = int(twoOptProb * totalChildren)
                lastPoolSize = poolSize
                if poolSize > 0:
                    candidates = sorted(childrenC + childrenM, key=lambda t: (fitness(t), tuple(t)))
                    poolTours = candidates[:poolSize]
                    results = list(executor.map(
                        twoOptWorker, poolTours,
                        chunksize=max(1, poolSize // (workers * 2))
                    ))
                    # Reemplazo estable
                    where = {id(t): ('C', i) for i, t in enumerate(childrenC)}
                    where.update({id(t): ('M', i) for i, t in enumerate(childrenM)})
                    for old, new in zip(poolTours, results):
                        lst, j = where[id(old)]
                        if lst == 'C':
                            childrenC[j] = new
                        else:
                            childrenM[j] = new
            prof["twoopt_pool"] += time.time() - t2o0

            # ---------- Recomposición + élites + anticlones ----------
            newPop = survivors[:] + childrenC + childrenM
            newPop[:elites] = pop[:elites]

            tAc0 = time.time()
            seen = set(); dedup = []
            for t in newPop:
                k = tuple(t)
                if k in seen:
                    mutateSwap(t); mutateInsertion(t)
                    k = tuple(t)
                    if k in seen:
                        t = makeRandomTour(n)
                        k = tuple(t)
                seen.add(k); dedup.append(t)
            newPop = dedup
            prof["anticlones"] += time.time() - tAc0

            # Ajustar tamaño N
            if len(newPop) > N:
                newPop = newPop[:N]
            elif len(newPop) < N:
                newPop += [makeRandomTour(n) for _ in range(N - len(newPop))]

            # ---------- Orden estable ----------
            tSo0 = time.time()
            newPop.sort(key=lambda t: (fitness(t), tuple(t)))
            prof["sort"] += time.time() - tSo0
            pop = newPop

            # ---------- Actualización Edge-Histogram ----------
            if edgeFreqPeriod > 0 and gen >= nextEdgeFreqUpdate:
                tEH0 = time.time()
                edgeFreq = buildEdgeHistogram(pop, topFrac=edgeTopFrac)
                prof["edge_hist"] += time.time() - tEH0
                nextEdgeFreqUpdate += edgeFreqPeriod

            # ---------- Especiación periódica (NEW) ----------
            if speciesPeriod > 0 and (gen % speciesPeriod) == 0:
                rebuildSpecies()

            # ---------- Actualización de mejor ----------
            currBest = pop[0]
            currCost = fitness(currBest)
            history.append(min(history[-1], currCost))

            if currCost < bestCost:
                elapsedNow = time.time() - t0
                delta = bestCost - currCost
                bestCost = currCost
                best = currBest[:]
                noImprove = 0
                events.append({"gen": gen, "bestCost": bestCost, "tour": best[:], "elapsedSec": elapsedNow})
                print(
                    f"\n[gen {gen}] NUEVO BEST\n"
                    f"\tcosto:\t\t{bestCost}\n"
                    f"\tmejora delta:\t{delta}\n"
                    f"\tnoImprove:\t0\n"
                    f"\ttiempo:\t\t{elapsedNow:.2f}s (~{elapsedNow/60:.2f} min)\n"
                    "-----------------------------------------------------------"
                )
                writeTrace(traceWriter, [
                    "improve", gen, f"{elapsedNow:.6f}", bestCost, delta, currCost, lastPoolSize,
                    name, edgeType, n, N, maxIter,
                    f"{survivorsFrac:.6f}", f"{crossoverFrac:.6f}", f"{mutationFrac:.6f}",
                    f"{pc:.6f}", f"{pm:.6f}", f"{elitismFrac:.6f}", tournamentK, int(bool(useSCX)), f"{twoOptProb:.6f}",
                    stallGenerations, f"{timeLimitSec:.6f}", seed,
                    lpEdgeVars, lpDegreeCons
                ])
                if recordImprovements:
                    saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)
            else:
                noImprove += 1
                # Catástrofes
                catPeriod = max(1, stallGenerations // 2)
                if catastropheFrac > 0 and (noImprove % catPeriod) == 0:
                    tCT0 = time.time()
                    replaceK = max(1, int(N * catastropheFrac))
                    worstIdx = list(range(len(pop)-replaceK, len(pop)))
                    baseTour = best[:]  # determinista
                    newOnes = []
                    for _ in worstIdx:
                        cand = doubleBridgeKick(baseTour[:])
                        steps = 0
                        while steps < 6 and apply2optOnce(cand, n, vec, neighbors=neighbors, first_improve=True, useFlocking=useFlocking):
                            steps += 1
                        newOnes.append(cand)
                    for i, idxW in enumerate(worstIdx):
                        pop[idxW] = newOnes[i]
                    pop.sort(key=lambda t: (fitness(t), tuple(t)))
                    noImprove = 0
                    prof["catastrophe"] += time.time() - tCT0

                # Extinción
                if species and (gen % speciesPeriod) == 0 and len(species) > 1:
                    tSPX0 = time.time()
                    speciesScore = []
                    for mems in species:
                        bestIn = min((fitness(pop[i]) for i in mems))
                        speciesScore.append((bestIn, mems))
                    worstSpecies = max(speciesScore, key=lambda x: (x[0], len(x[1])))
                    mems = sorted(worstSpecies[1], reverse=True)
                    toKill = max(1, int(len(mems) * speciesCullFrac))
                    for _ in range(toKill):
                        idx = mems.pop(0) if mems else len(pop)-1
                        tnew = makeRandomTour(n)
                        steps = 0
                        while steps < 6 and apply2optOnce(tnew, n, vec, neighbors=neighbors, first_improve=True, useFlocking=useFlocking):
                            steps += 1
                        pop[idx] = tnew
                    pop.sort(key=lambda t: (fitness(t), tuple(t)))
                    noImprove = 0
                    prof["speciation"] += time.time() - tSPX0

                # Kick periódico determinista (conservado)
                if (noImprove % 3000) == 0:
                    cand = doubleBridgeKick(best[:])
                    changed = True
                    while changed:
                        changed = apply2optOnce(cand, n, vec, neighbors=None, first_improve=False, useFlocking=useFlocking)
                    cst = tourDistance(cand, n, vec)
                    if cst < bestCost:
                        best, bestCost, noImprove = cand, cst, 0

            # ---------- Paradas por tiempo / estancamiento ----------
            if timeLimitSec > 0 and (time.time() - t0) >= timeLimitSec:
                writeTrace(traceWriter, [
                    "stop", gen, f"{(time.time()-t0):.6f}", bestCost, "", currCost, "",
                    name, edgeType, n, N, maxIter,
                    f"{survivorsFrac:.6f}", f"{crossoverFrac:.6f}", f"{mutationFrac:.6f}",
                    f"{pc:.6f}", f"{pm:.6f}", f"{elitismFrac:.6f}", tournamentK, int(bool(useSCX)), f"{twoOptProb:.6f}",
                    stallGenerations, f"{timeLimitSec:.6f}", seed,
                    lpEdgeVars, lpDegreeCons
                ])
                break
            if noImprove >= stallGenerations:
                writeTrace(traceWriter, [
                    "stop", gen, f"{(time.time()-t0):.6f}", bestCost, "", currCost, "",
                    name, edgeType, n, N, maxIter,
                    f"{survivorsFrac:.6f}", f"{crossoverFrac:.6f}", f"{mutationFrac:.6f}",
                    f"{pc:.6f}", f"{pm:.6f}", f"{elitismFrac:.6f}", tournamentK, int(bool(useSCX)), f"{twoOptProb:.6f}",
                    stallGenerations, f"{timeLimitSec:.6f}", seed,
                    lpEdgeVars, lpDegreeCons
                ])
                break

    finally:
        executor.shutdown(wait=True)

    # ---------- Métricas ----------
    elapsed = time.time() - t0
    gensDone = len(history) - 1
    loopAccounted = tInit + sum(prof.values())
    otros = max(0.0, elapsed - loopAccounted)

    print("\n=== PERFIL DE TIEMPO ===============================")
    print(f"\tParse+matriz:\t{tParseBuild:.2f} s")
    print(f"\tVecinos (k-NN):\t{tKnn:.2f} s")
    print(f"\tInit+primer sort:\t{tInit:.2f} s")
    print(f"\tBucle (acumulado):\t{loopAccounted:.2f} s")
    print(f"\tOtros:\t\t\t{otros:.2f} s")
    for k, v in sorted(prof.items(), key=lambda kv: kv[1], reverse=True):
        pct = 100.0 * v / max(1e-9, elapsed)
        print(f"\t- {k:16s}: {v:8.2f} s  ({pct:4.1f}%)")
    print("===================================================")

    # ---------- Finisher 2-opt global ----------
    changed = True
    while changed:
        changed = apply2optOnce(best, n, vec, neighbors=None, first_improve=False, useFlocking=useFlocking)
    bestCost = tourDistance(best, n, vec)

    # fila end
    writeTrace(traceWriter, [
        "end", gensDone, f"{elapsed:.6f}", bestCost, "", bestCost, "",
        name, edgeType, n, N, maxIter,
        f"{survivorsFrac:.6f}", f"{crossoverFrac:.6f}", f"{mutationFrac:.6f}",
        f"{pc:.6f}", f"{pm:.6f}", f"{elitismFrac:.6f}", tournamentK, int(bool(useSCX)), f"{twoOptProb:.6f}",
        stallGenerations, f"{timeLimitSec:.6f}", seed,
        lpEdgeVars, lpDegreeCons
    ])
    if traceFile:
        traceFile.close()

    return {
        "name": name,
        "coords": coords,
        "bestTour": best,
        "bestCost": bestCost,
        "history": history,
        "events": events,
        "framesDir": framesDir if recordImprovements else None,
        "stoppedBy": ("stall" if noImprove >= stallGenerations else
                      ("time" if (timeLimitSec > 0 and (time.time() - t0) >= timeLimitSec) else
                       ("maxIter" if len(history)-1 >= maxIter else "unknown"))),
        "elapsedSec": elapsed,
        "gensDone": gensDone,
        "genPerSec": (gensDone / elapsed) if elapsed > 0 else 0.0
    }
