import random, time, os, math, statistics
from typing import List, Callable, Dict
from io_tsp import getDistance, parseTsp, buildDistanceMatrixCompressed, tourDistance
from poblation import initPopulation, makeRandomTour
from viz import saveFrame

def selectionTournament(pop: List[List[int]], fitness: Callable[[List[int]], int], k: int, num: int) -> List[List[int]]:
    sel = []
    for _ in range(num):
        cand = random.sample(pop, k)
        cand.sort(key=fitness)
        sel.append(cand[0][:])
    return sel

def crossoverOX(p1: List[int], p2: List[int]) -> List[int]:
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [-1]*n
    child[a:b+1] = p1[a:b+1]
    fill = [x for x in p2 if x not in child]
    idx = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = fill[idx]; idx += 1
    return child

def crossoverSCX(p1: List[int], p2: List[int], n: int, vec: List[int]) -> List[int]:
    current = p1[0]
    child = [current]
    unused = set(range(n)) - {current}
    next1 = {p1[i]: p1[(i+1)%n] for i in range(n)}
    next2 = {p2[i]: p2[(i+1)%n] for i in range(n)}
    while unused:
        cands = []
        for nxt in (next1[current], next2[current]):
            if nxt in unused: cands.append(nxt)
        if cands:
            nxt = min(cands, key=lambda j: getDistance(current, j, n, vec))
        else:
            nxt = min(unused, key=lambda j: getDistance(current, j, n, vec))
        child.append(nxt)
        unused.remove(nxt)
        current = nxt
    return child

def mutateInsertion(t: List[int]) -> None:
    n = len(t)
    i, j = sorted(random.sample(range(n), 2))
    gene = t.pop(j)
    t.insert(i, gene)

def mutateSwap(t: List[int]) -> None:
    i, j = random.sample(range(len(t)), 2)
    t[i], t[j] = t[j], t[i]

def apply2optOnce(t: List[int], n: int, vec: List[int]) -> bool:
    best_delta = 0
    best_move = None
    L = len(t)
    for i in range(L-1):
        a, b = t[i], t[(i+1)%L]
        for j in range(i+2, L if i>0 else L-1):
            c, d = t[j%L], t[(j+1)%L]
            delta = (getDistance(a, c, n, vec) + getDistance(b, d, n, vec)
                     - getDistance(a, b, n, vec) - getDistance(c, d, n, vec))
            if delta < best_delta:
                best_delta = delta; best_move = (i+1, j)
    if best_move:
        i1, j = best_move
        if i1 < j:
            t[i1:j+1] = reversed(t[i1:j+1])
        else:
            seg = (t[i1:] + t[:j+1])[::-1]
            m = len(t) - i1
            t[i1:] = seg[:m]
            t[:j+1] = seg[m:]
        return True
    return False

def _hamming(a: List[int], b: List[int]) -> int:
    return sum(1 for i in range(len(a)) if a[i] != b[i])

def _diversity_metrics(pop: List[List[int]], fitness: Callable[[List[int]], int]) -> Dict[str, float]:
    """
    Calcula:
      - hamming_mean: promedio de Hamming en todas las parejas (muestra si N es grande).
      - std_cost: desviación estándar de los costos en la población.
    """
    N = len(pop)
    if N < 2:
        return {"hamming_mean": 0.0, "std_cost": 0.0}
    # Muestra limitada para O(N) si la población es grande
    sample_idx = list(range(N))
    if N > 80:
        sample_idx = random.sample(sample_idx, 80)
    pairs = 0
    acc_h = 0
    for i in range(len(sample_idx)):
        for j in range(i+1, len(sample_idx)):
            acc_h += _hamming(pop[sample_idx[i]], pop[sample_idx[j]])
            pairs += 1
    hmean = acc_h / pairs if pairs > 0 else 0.0
    costs = [fitness(ind) for ind in pop]
    stdc = statistics.pstdev(costs) if len(costs) > 1 else 0.0
    return {"hamming_mean": hmean, "std_cost": stdc}

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
          stallGenerations: int = 500,  # τ = 500 (Módulo K)
          timeLimitSec: float = 0.0,
          recordImprovements: bool = False,
          framesDir: str = "frames",
          seed: int = 42) -> Dict:
    """
    Ejecuta el GA para TSP con:
      - Módulo E: initPopulation con diversidad.
      - Módulo J: ensamblaje generacional con elitismo + anti-clones.
      - Módulo K: paro por maxIter/estancamiento/tiempo + logging de diversidad.
      - Módulo L: frames en mejoras (saveFrame) y salida para plotResults.
    """
    assert abs((survivorsFrac + crossoverFrac + mutationFrac) - 1.0) < 1e-6, "S%+C%+M% debe ser 1.0"
    if N < 10: raise ValueError("N muy pequeño (mínimo recomendado 10)")
    random.seed(seed)
    t0 = time.time()

    name, coords = parseTsp(coordsPath)
    n, vec = buildDistanceMatrixCompressed(coords)
    if pm is None:
        pm = max(1.0/n, 0.002)

    def fitness(t): return tourDistance(t, n, vec)

    if recordImprovements:
        os.makedirs(framesDir, exist_ok=True)

    # -------- resumen de arranque --------
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

    # MÓDULO E — Inicialización con diversidad (80/20 + anti-concentración)
    pop = initPopulation(n, vec, N, seedFrac=0.20)
    pop.sort(key=fitness)
    best = pop[0][:]
    bestCost = fitness(best)
    history = [bestCost]
    events = [{"gen": 0, "bestCost": bestCost, "tour": best[:] }]
    diversity_log = []

    div = _diversity_metrics(pop, fitness)
    diversity_log.append({"gen": 0, **div})

    print(f"\n[gen 0]\n\tbest:\t\t{bestCost}\n\tciudades:\t{n}\n-----------------------------------------------------------")

    if recordImprovements:
        saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)

    S = max(1, int(N*survivorsFrac))
    C = max(0, int(N*crossoverFrac))
    M = max(0, N - S - C)
    elites = max(1, int(N*elitismFrac))

    noImprove = 0

    for gen in range(1, maxIter+1):
        # límites
        if timeLimitSec > 0 and (time.time() - t0) >= timeLimitSec:
            print(
                "\n[STOP]\n"
                "\tCausa:\t\tlímite de tiempo\n"
                f"\tTiempo:\t\t{timeLimitSec}s\n"
                f"\tGeneración:\t{gen}\n"
                "-----------------------------------------------------------"
            )
            break
        if noImprove >= stallGenerations:
            print(
                "\n[STOP]\n"
                "\tCausa:\t\testancamiento\n"
                f"\tSin mejora:\t{stallGenerations} generaciones\n"
                f"\tGeneración:\t{gen}\n"
                "-----------------------------------------------------------"
            )
            break

        # sobrevivientes
        survivors = pop[:S]
        # padres
        parentsNeeded = max(C*2, 2)
        parents = selectionTournament(pop, fitness, tournamentK, parentsNeeded)

        # cruce
        childrenC = []
        for i in range(0, parentsNeeded, 2):
            p1, p2 = parents[i%len(parents)], parents[(i+1)%len(parents)]
            if random.random() < pc:
                child = crossoverSCX(p1, p2, n, vec) if useSCX else crossoverOX(p1, p2)
            else:
                child = p1[:]
            childrenC.append(child)
            if len(childrenC) >= C: break

        # mutación pura
        childrenM = []
        for _ in range(M):
            base = random.choice(pop)[:]
            if random.random() < 0.5:
                mutateInsertion(base)
            else:
                mutateSwap(base)
            childrenM.append(base)

        # mutación ligera sobre hijos de cruce
        for ch in childrenC:
            if random.random() < pm:
                (mutateInsertion if random.random() < 0.7 else mutateSwap)(ch)

        # 2-opt ocasional
        if twoOptProb > 0.0:
            poolSize = max(1, int(twoOptProb*(len(childrenC)+len(childrenM))))
            pool = random.sample(childrenC + childrenM, k=poolSize)
            for t in pool:
                apply2optOnce(t, n, vec)

        # =========================
        # MÓDULO J — ENSAMBLAJE
        #   1) Copiar élites.
        #   2) Rellenar con mejores de S ∪ C ∪ M hasta N.
        #   Anti-clones: si es idéntico a alguien ya en P(t+1), forzar UNA mutación.
        # =========================
        candidates = survivors + childrenC + childrenM
        candidates.sort(key=fitness)

        newPop: List[List[int]] = []
        # 1) ÉLITES (del pop anterior, ya ordenado)
        elites_block = [ind[:] for ind in pop[:elites]]
        newPop.extend(elites_block)

        # 2) RELLENO con anti-clones
        i = 0
        while len(newPop) < N and i < len(candidates):
            cand = candidates[i][:]
            is_clone = any(cand == e for e in newPop)
            if is_clone:
                # mutación extra (una sola vez)
                (mutateInsertion if random.random() < 0.7 else mutateSwap)(cand)
                # si aún queda igual, lo omitimos para no entrar en lazo
                if any(cand == e for e in newPop):
                    i += 1
                    continue
            newPop.append(cand)
            i += 1

        # si faltan, rellenar con tours aleatorios
        while len(newPop) < N:
            newPop.append(makeRandomTour(n))

        newPop.sort(key=fitness)
        pop = newPop

        currBest = pop[0]; currCost = fitness(currBest)
        history.append(min(history[-1], currCost))

        # MÓDULO K — LOGGING de diversidad
        div = _diversity_metrics(pop, fitness)
        diversity_log.append({"gen": gen, **div})

        if currCost < bestCost:
            gap = bestCost - currCost
            bestCost = currCost; best = currBest[:]; noImprove = 0
            events.append({"gen": gen, "bestCost": bestCost, "tour": best[:] })
            print(
                f"\n[gen {gen}] NUEVO BEST\n"
                f"\tcosto:\t\t{bestCost}\n"
                f"\tmejora Δ:\t{gap}\n"
                f"\tnoImprove:\t0\n"
                "-----------------------------------------------------------"
            )
            if recordImprovements:
                saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)
        else:
            noImprove += 1

    elapsed = time.time() - t0
    gens_done = len(history) - 1

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
        "gensDone": gens_done,
        "genPerSec": (gens_done / elapsed) if elapsed > 0 else 0.0,
        # logs Módulo K:
        "diversity": diversity_log,  # [{gen, hamming_mean, std_cost}, ...]
    }
