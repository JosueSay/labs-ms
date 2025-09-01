import random, time, os
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
    # número de candidatos al azar cuando no hay candidatos de padres
    fallbackK = 20 if n > 50 else n  # acota costo en instancias grandes
    while unused:
        cands = []
        for nxt in (next1[current], next2[current]):
            if nxt in unused: cands.append(nxt)
        if cands:
            nxt = min(cands, key=lambda j: getDistance(current, j, n, vec))
        else:
            # Fallback acotado: muestrea hasta fallbackK de 'unused'
            if len(unused) <= fallbackK:
                pool = unused
            else:
                pool = set(random.sample(list(unused), fallbackK))
            nxt = min(pool, key=lambda j: getDistance(current, j, n, vec))
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

def apply2optOnce(t: List[int], n: int, vec: List[int],
                  maxPairs: int = 0) -> bool:
    """
    Explora pares (i, j) no adyacentes; ahora incluye el caso wrap-around
    (i=0, j=L-1). Si maxPairs>0, corta tras revisar ese número de pares.
    """
    best_delta = 0
    best_move = None
    L = len(t)
    checked = 0

    # i en [0..L-2], j en [i+2..L-1]  -> incluye (i=0, j=L-1)
    for i in range(L - 1):
        a, b = t[i], t[(i + 1) % L]
        for j in range(i + 2, L):
            c, d = t[j % L], t[(j + 1) % L]
            # Evitar revertir segmento de longitud 0 o tocar misma arista dos veces (no aplica aquí)
            delta = (getDistance(a, c, n, vec) + getDistance(b, d, n, vec)
                     - getDistance(a, b, n, vec) - getDistance(c, d, n, vec))
            checked += 1
            if delta < best_delta:
                best_delta = delta
                best_move = (i + 1, j)
            if maxPairs > 0 and checked >= maxPairs:
                break
        if maxPairs > 0 and checked >= maxPairs:
            break

    if best_move:
        i1, j = best_move
        if i1 < j:
            t[i1:j + 1] = reversed(t[i1:j + 1])
        else:
            seg = (t[i1:] + t[:j + 1])[::-1]
            m = len(t) - i1
            t[i1:] = seg[:m]
            t[:j + 1] = seg[m:]
        return True
    return False

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
          seed: int = 42) -> Dict:
    
    framesSaved = 0
    recordEvery = 1
    maxFrames   = 1000

    assert abs((survivorsFrac + crossoverFrac + mutationFrac) - 1.0) < 1e-6, "S%+C%+M% debe ser 1.0"
    if N < 10: raise ValueError("N muy pequeño (mínimo recomendado 10)")
    random.seed(seed)
    t0 = time.time()

    name, coords = parseTsp(coordsPath)
    n, vec = buildDistanceMatrixCompressed(coords)
    
    if pm is None:
        pm = max(1.0/n, 0.002)

    # --- caché de fitness por generación ---
    def makeFitnessCached():
        cache: Dict[tuple, int] = {}
        def f(t: List[int]) -> int:
            key = tuple(t)
            v = cache.get(key)
            if v is None:
                v = tourDistance(t, n, vec)
                cache[key] = v
            return v
        return f

    fitness = makeFitnessCached()

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

    pop = initPopulation(n, vec, N, seedFrac=0.25)
    pop.sort(key=fitness)
    best = pop[0][:]
    bestCost = fitness(best)
    history = [bestCost]
    events = [{"gen": 0, "bestCost": bestCost, "tour": best[:] }]

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
        
        # --- fitness cache NUEVO por generación ---
        fitness = makeFitnessCached()

        childrenC = []
        if C > 0:
            # padres
            parentsNeeded = C * 2
            parents = selectionTournament(pop, fitness, tournamentK, parentsNeeded)

            # cruce
            for i in range(0, parentsNeeded, 2):
                p1, p2 = parents[i % len(parents)], parents[(i + 1) % len(parents)]
                if random.random() < pc:
                    child = crossoverSCX(p1, p2, n, vec) if useSCX else crossoverOX(p1, p2)
                else:
                    # evitar clonar SIEMPRE p1 cuando no cruza
                    child = (p1[:] if random.random() < 0.5 else p2[:])
                childrenC.append(child)
                if len(childrenC) >= C:
                    break

        # mutación pura
        childrenM = []
        for _ in range(M):
            base = random.choice(pop)[:]
            if random.random() < 0.5:
                mutateInsertion(base)
            else:
                mutateSwap(base)
            childrenM.append(base)

        # --- mutación ligera ADAPTATIVA sobre hijos de cruce ---
        
        # sube suavemente con el estancamiento, tope 1.0
        pmEff = min(1.0, pm * (1.0 + noImprove / max(1, stallGenerations)))
        for ch in childrenC:
            if random.random() < pmEff:
                (mutateInsertion if random.random() < 0.7 else mutateSwap)(ch)

        # --- 2-opt ocasional: múltiples pases con límite de pares ---
        if twoOptProb > 0.0:
            hijosNuevos = childrenC + childrenM
            poolSize = max(1, int(twoOptProb * len(hijosNuevos)))
            pool = random.sample(hijosNuevos, k=poolSize)
            twoOptPasses = 2            # intenta hasta 2 mejoras por individuo
            twoOptMaxPairs = 0          # 0 = sin límite; p.ej. 2000 para throttling
            for t_ in pool:
                for _ in range(twoOptPasses):
                    improved = apply2optOnce(t_, n, vec, maxPairs=twoOptMaxPairs)
                    if not improved:
                        break

        # nueva población
        newPop = survivors[:] + childrenC + childrenM
        # reinyectar elites
        newPop[:elites] = pop[:elites]

        # ajuste de tamaño
        if len(newPop) > N:
            newPop = newPop[:N]
        elif len(newPop) < N:
            newPop += [makeRandomTour(n) for _ in range(N - len(newPop))]

        # sacudir duplicados si hay pocos únicos
        def shakeDuplicates(popList: List[List[int]], minUniqueFrac: float = 0.6):
            uniq = {}
            order = []
            for idx, t in enumerate(popList):
                key = tuple(t)
                order.append(key)
                uniq.setdefault(key, []).append(idx)
            uniqueFrac = len(uniq) / max(1, len(popList))
            if uniqueFrac >= minUniqueFrac:
                return  # OK

            # Sacudir: para cada grupo duplicado, deja el primero y muta los demás
            for key, idxs in uniq.items():
                for j in idxs[1:]:
                    if random.random() < 0.7:
                        mutateInsertion(popList[j])
                    else:
                        mutateSwap(popList[j])
                    # pequeña 2-opt puntual
                    apply2optOnce(popList[j], n, vec, maxPairs=500)

        shakeDuplicates(newPop, minUniqueFrac=0.6)

        newPop.sort(key=fitness)
        pop = newPop

        currBest = pop[0]; currCost = fitness(currBest)
        history.append(min(history[-1], currCost))

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
            if recordImprovements and (framesSaved < maxFrames) and (len(events) % recordEvery == 1):
                saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)
                framesSaved += 1

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
        "genPerSec": (gens_done / elapsed) if elapsed > 0 else 0.0
    }

