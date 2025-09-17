import random, time, os
from typing import Callable
from io_tsp import getDistance, parseTsp, buildDistanceMatrixCompressed, tourDistance
from poblation import initPopulation, makeRandomTour
from viz import saveFrame

def selectionTournament(pop: list[list[int]], fitness: Callable[[list[int]], int], k: int, num: int) -> list[list[int]]:
    sel = []
    for _ in range(num):
        cand = random.sample(pop, k)
        sel.append(min(cand, key=fitness)[:])
    return sel

def crossoverOX(p1: list[int], p2: list[int]) -> list[int]:
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

def crossoverSCX(p1: list[int], p2: list[int], n: int, vec: list[int]) -> list[int]:
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

def mutateInsertion(t: list[int]) -> None:
    n = len(t)
    i, j = sorted(random.sample(range(n), 2))
    gene = t.pop(j)
    t.insert(i, gene)

def mutateSwap(t: list[int]) -> None:
    i, j = random.sample(range(len(t)), 2)
    t[i], t[j] = t[j], t[i]

def apply2optOnce(t, n, vec, neighbors=None, first_improve=False):
    best_delta = 0
    best_move = None
    L = len(t)
    for i in range(L-1):
        a, b = t[i], t[(i+1)%L]
        for j in range(i+2, L if i>0 else L-1):
            c, d = t[j%L], t[(j+1)%L]
            if neighbors is not None:
                if not ((c in neighbors[a]) or (d in neighbors[a]) or
                        (c in neighbors[b]) or (d in neighbors[b])):
                    continue
            delta = (getDistance(a, c, n, vec) + getDistance(b, d, n, vec)
                     - getDistance(a, b, n, vec) - getDistance(c, d, n, vec))
            if first_improve and delta < 0:
                # aplicar y salir
                i1 = i+1
                if i1 < j:
                    t[i1:j+1] = reversed(t[i1:j+1])
                else:
                    seg = (t[i1:] + t[:j+1])[::-1]
                    m = len(t) - i1
                    t[i1:] = seg[:m]; t[:j+1] = seg[m:]
                return True
            if delta < best_delta:
                best_delta = delta; best_move = (i+1, j)
    if best_move:
        i1, j = best_move
        if i1 < j:
            t[i1:j+1] = reversed(t[i1:j+1])
        else:
            seg = (t[i1:] + t[:j+1])[::-1]
            m = len(t) - i1
            t[i1:] = seg[:m]; t[:j+1] = seg[m:]
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
          seed: int = 42) -> dict:
    assert abs((survivorsFrac + crossoverFrac + mutationFrac) - 1.0) < 1e-6, "S%+C%+M% debe ser 1.0"
    if N < 10: raise ValueError("N muy pequeño (mínimo recomendado 10)")
    random.seed(seed)

    t_build0 = time.time()
    name, edge_type, coords = parseTsp(coordsPath)
    n, vec = buildDistanceMatrixCompressed(coords, edge_type)
    t_parse_build = time.time() - t_build0

    
    def build_knn(n, vec, k=20):
        neigh = [None]*n
        for i in range(n):
            order = sorted(( (getDistance(i,j,n,vec), j) for j in range(n) if j!=i ))
            neigh[i] = [j for _, j in order[:k]]
        return neigh

    t_knn0 = time.time()
    neighbors = build_knn(n, vec, k=30 if n >= 200 else 20)
    t_knn = time.time() - t_knn0

    
    t0 = time.time()

    prof = {
        "elitist_memetic": 0.0,
        "selection": 0.0,
        "crossover": 0.0,
        "mutation_pure": 0.0,
        "mutation_light": 0.0,
        "twoopt_pool": 0.0,
        "anticlones": 0.0,
        "sort": 0.0,
    }
    t_init = 0.0  # initPopulation + primer sort


    if pm is None:
        pm = max(1.0/n, 0.002)
    elif pm == -1:
        pm = 1.0/n
    base_pm = pm

    base_twoopt = twoOptProb
    
        
    # --- cache de costos ---
    fitness_cache = {}
    def get_cost(t):
        key = tuple(t)
        c = fitness_cache.get(key)
        if c is None:
            c = tourDistance(t, n, vec)
            fitness_cache[key] = c
        return c
    fitness = get_cost  # usar cache en todo


    # def fitness(t): return tourDistance(t, n, vec)

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

    t_init0 = time.time()
    pop = initPopulation(n, vec, N, seedFrac=0.25)
    pop.sort(key=fitness)
    t_init = time.time() - t_init0
    
    best = pop[0][:]
    bestCost = fitness(best)
    history = [bestCost]
    events = [{"gen": 0, "bestCost": bestCost, "tour": best[:], "elapsedSec": 0.0}]

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
        
        if gen % 200 == 0:
            t_m0 = time.time()
            for e in survivors[:1]:
                improved = True
                while improved:
                    improved = apply2optOnce(e, n, vec, neighbors=neighbors, first_improve=True)
            prof["elitist_memetic"] += time.time() - t_m0

        # padres
        parentsNeeded = max(C*2, 2)
        t_s0 = time.time()
        parents = selectionTournament(pop, fitness, tournamentK, parentsNeeded)
        prof["selection"] += time.time() - t_s0

        # cruce
        t_c0 = time.time()
        childrenC = []
        for i in range(0, parentsNeeded, 2):
            p1, p2 = parents[i%len(parents)], parents[(i+1)%len(parents)]
            if random.random() < pc:
                child = crossoverSCX(p1, p2, n, vec) if useSCX else crossoverOX(p1, p2)
            else:
                child = p1[:]
            childrenC.append(child)
            if len(childrenC) >= C: break
        prof["crossover"] += time.time() - t_c0

        # mutación pura
        t_mp0 = time.time()
        childrenM = []
        for _ in range(M):
            base = random.choice(pop)[:]
            if random.random() < 0.5:
                mutateInsertion(base)
            else:
                mutateSwap(base)
            childrenM.append(base)
        prof["mutation_pure"] += time.time() - t_mp0

        # mutación ligera sobre hijos de cruce
        t_ml0 = time.time()
        for ch in childrenC:
            if random.random() < pm:
                (mutateInsertion if random.random() < 0.7 else mutateSwap)(ch)
        prof["mutation_light"] += time.time() - t_ml0

        # 2-opt ocasional
        t_2o0 = time.time()
        if twoOptProb > 0.0:
            total_children = len(childrenC) + len(childrenM)
            poolSize = int(twoOptProb * total_children)
            if poolSize > 0:
                pool = random.sample(childrenC + childrenM, k=poolSize)
                for t in pool:
                    apply2optOnce(t, n, vec, neighbors=neighbors, first_improve=False)
        prof["twoopt_pool"] += time.time() - t_2o0
                

        # nueva población
        newPop = survivors[:] + childrenC + childrenM
        # reinyectar elites
        newPop[:elites] = pop[:elites]
        
        # anti-clones: perturbar duplicados
        t_ac0 = time.time()
        seen = set(); dedup = []
        for t in newPop:
            k = tuple(t)
            if k in seen:
                mutateSwap(t); mutateInsertion(t)  # pequeña perturbación
                k = tuple(t)
                if k in seen:
                    t = makeRandomTour(n)
                    k = tuple(t)
            seen.add(k); dedup.append(t)
        prof["anticlones"] += time.time() - t_ac0
        newPop = dedup


        # ajuste de tamaño
        if len(newPop) > N:
            newPop = newPop[:N]
        elif len(newPop) < N:
            newPop += [makeRandomTour(n) for _ in range(N - len(newPop))]

        t_so0 = time.time()
        newPop.sort(key=fitness)
        prof["sort"] += time.time() - t_so0
        pop = newPop

        currBest = pop[0]; currCost = fitness(currBest)
        history.append(min(history[-1], currCost))

        if currCost < bestCost:
            elapsed_now = time.time() - t0
            gap = bestCost - currCost
            bestCost = currCost; best = currBest[:]; noImprove = 0
            events.append({"gen": gen, "bestCost": bestCost, "tour": best[:], "elapsedSec": elapsed_now})

            print(
                f"\n[gen {gen}] NUEVO BEST\n"
                f"\tcosto:\t\t{bestCost}\n"
                f"\tmejora Δ:\t{gap}\n"
                f"\tnoImprove:\t0\n"
                f"\ttiempo:\t\t{elapsed_now:.2f}s (~{elapsed_now/60:.2f} min)\n"
                "-----------------------------------------------------------"
            )
            pm = base_pm
            twoOptProb = base_twoopt

            
            if recordImprovements:
                saveFrame(coords, best, history, os.path.join(framesDir, f"frame_{len(events):04d}.png"), title=name)
        else:
            noImprove += 1
            if (noImprove % 500) == 0 and noImprove > 0:
                pm = min(pm * 1.5, 0.03)
                twoOptProb = min(twoOptProb + 0.05, 0.40)

    elapsed = time.time() - t0
    gens_done = len(history) - 1
    
    loop_accounted = t_init + sum(prof.values())
    otros = max(0.0, elapsed - loop_accounted)
    print("\n=== PERFIL DE TIEMPO ===============================")
    print(f"\tParse+matriz:\t{t_parse_build:.2f} s")
    print(f"\tVecinos (k-NN):\t{t_knn:.2f} s")
    print(f"\tInit+primer sort:\t{t_init:.2f} s")
    print(f"\tBucle (acumulado):\t{loop_accounted:.2f} s")
    print(f"\tOtros:\t\t\t{otros:.2f} s")
    for k, v in sorted(prof.items(), key=lambda kv: kv[1], reverse=True):
        pct = 100.0 * v / max(1e-9, elapsed)
        print(f"\t- {k:16s}: {v:8.2f} s  ({pct:4.1f}%)")
    print("===================================================")


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