import math, os
import argparse
from ga import runGa
from viz import plotResults, makeGifFromFrames

def clamp01(x: float) -> float:
    try:
        if not math.isfinite(x): return 0.0
    except Exception:
        return 0.0
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def renormalize3(a: float, b: float, c: float):
    s = a + b + c
    if s == 0.0:
        return 0.2, 0.6, 0.2, True  # default razonable
    return a/s, b/s, c/s, abs(s - 1.0) > 1e-6

def main():
    parser = argparse.ArgumentParser(description="GA para TSP con validaciones.")
    parser.add_argument("--file", type=str, default="data/berlin52.tsp")
    parser.add_argument("--N", type=int, default=300)
    parser.add_argument("--maxIter", type=int, default=1500)
    parser.add_argument("--survivors", type=float, default=0.2)
    parser.add_argument("--crossover", type=float, default=0.6)
    parser.add_argument("--mutation", type=float, default=0.2)
    parser.add_argument("--pc", type=float, default=0.95)
    parser.add_argument("--pm", type=float, default=-1.0, help="-1 => usar 1/n como default")
    parser.add_argument("--elitism", type=float, default=0.05)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--scx", action="store_true", help="usar SCX (si se pasa este flag); por defecto OX")
    parser.add_argument("--twoOptProb", type=float, default=0.05)
    parser.add_argument("--stall", type=int, default=400, help="generaciones sin mejora para detener")
    parser.add_argument("--timeLimit", type=float, default=0.0, help="segundos (0 => sin límite)")
    parser.add_argument("--record", action="store_true", help="guardar frame .png en cada mejora")
    parser.add_argument("--framesDir", type=str, default="frames")
    parser.add_argument("--gifOut", type=str, default="", help="si se indica, genera GIF desde frames")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--estimate", type=int, default=0, help="n generaciones para estimar s/gen (no ejecuta el run completo)")
    parser.add_argument("--noPlot", action="store_true", help="no mostrar la figura final")
    parser.add_argument("--csv", type=str, default="", help="Ruta para escribir el trace CSV (opcional)")
    parser.add_argument("--eaxFrac", type=float, default=0.15)
    parser.add_argument("--edgeLambda", type=float, default=0.15)
    parser.add_argument("--edgeTopFrac", type=float, default=0.30)
    parser.add_argument("--edgeFreqPeriod", type=int, default=200)
    grp_ass = parser.add_mutually_exclusive_group()
    grp_ass.add_argument("--assortative", dest="assortative", action="store_true", default=True, help="emparejamiento por lejanía de aristas (ON por defecto)")
    grp_ass.add_argument("--noAssortative", dest="assortative", action="store_false", help="desactiva el emparejamiento por lejanía de aristas")
    parser.add_argument("--mem3OptSteps", type=int, default=4)
    parser.add_argument("--speciesPeriod", type=int, default=800)
    parser.add_argument("--speciesThresh", type=float, default=0.35)
    parser.add_argument("--speciesCullFrac", type=float, default=0.20)
    parser.add_argument("--catastropheFrac", type=float, default=0.20)
    parser.add_argument("--noFlocking", action="store_true", help="desactiva tie-break flocking en 2-opt")
    args = parser.parse_args()

    # --- Validaciones tempranas de archivo ---
    if not os.path.isfile(args.file) or os.path.getsize(args.file) == 0:
        raise SystemExit(f"[ERROR] Archivo no encontrado o vacío: {args.file}")

    # --- Clamp y renormalización de porcentajes ---
    s = clamp01(args.survivors)
    c = clamp01(args.crossover)
    m = clamp01(args.mutation)
    s, c, m, was_renorm = renormalize3(s, c, m)
    if was_renorm:
        print(f"[WARN] S/C/M renormalizados a sumar 1.0 -> {s:.3f}/{c:.3f}/{m:.3f}")

    # --- Validación de N, k, pc, pm, twoOptProb, elitism ---
    if args.N < 2:
        raise SystemExit("[ERROR] N debe ser >= 2")
    k = args.k
    if k < 2:
        print(f"[WARN] k < 2 -> ajustando a 2")
        k = 2
    if k > args.N:
        print(f"[WARN] k > N -> ajustando k={args.N}")
        k = args.N

    pc = clamp01(args.pc)
    if pc != args.pc:
        print(f"[WARN] pc fuera de [0,1] -> clamp a {pc:.3f}")

    # pm: permitir -1 (auto 1/n). Si no, clamp.
    pm = args.pm
    if pm >= 0.0:
        pm_clamped = clamp01(pm)
        if pm_clamped != pm:
            print(f"[WARN] pm fuera de [0,1] -> clamp a {pm_clamped:.3f}")
        pm = pm_clamped
    # elif pm < 0 -> se pasa como -1 (para auto 1/n en ga.run)

    twoOptProb = clamp01(args.twoOptProb)
    if twoOptProb != args.twoOptProb:
        print(f"[WARN] twoOptProb fuera de [0,1] -> clamp a {twoOptProb:.3f}")

    elitism = clamp01(args.elitism)
    if elitism != args.elitism:
        print(f"[WARN] elitism fuera de [0,1] -> clamp a {elitism:.3f}")

    if args.stall < 0:
        print(f"[WARN] stall < 0 -> ajustando a 0")
        args.stall = 0
    if args.timeLimit < 0:
        print(f"[WARN] timeLimit < 0 -> ajustando a 0")
        args.timeLimit = 0.0

    # --- Pre-cálculo informativo de S/C/M enteros (y avisos) ---
    S = max(1, int(args.N * s))
    C = max(0, int(args.N * c))
    M = max(0, args.N - S - C)
    if C == 0 and c > 0:
        print("[WARN] C=0 por redondeo aunque crossover>0. Este caso crea sobrecosto en ga.py (parentsNeeded=2).")
    if M == 0 and m > 0:
        print("[WARN] M=0 por redondeo aunque mutation>0. Revisa porcentajes o N.")

    # --- Backend matplotlib  ---
    headless = (os.environ.get("DISPLAY") is None)
    if args.noPlot or headless:
        os.environ.setdefault("MPLBACKEND", "Agg")

    # --- Rutas de salida ---
    if args.record:
        os.makedirs(args.framesDir, exist_ok=True)
    if args.gifOut:
        if os.path.exists(args.gifOut):
            print(f"[WARN] gifOut existe y será sobreescrito: {args.gifOut}")

    # ---- MODO ESTIMACIÓN ----
    if args.estimate > 0:
        res = runGa(coordsPath=args.file,
                    N=args.N, maxIter=args.estimate,
                    survivorsFrac=s, crossoverFrac=c, mutationFrac=m,
                    pc=pc, pm=None if pm < 0 else pm,
                    elitismFrac=elitism, tournamentK=k,
                    useSCX=args.scx, twoOptProb=twoOptProb,
                    stallGenerations=10**9, timeLimitSec=0,
                    recordImprovements=False, framesDir="__noop__", seed=args.seed, trace_csv=args.csv,
                    eaxFrac=args.eaxFrac,
                    edgeLambda=args.edgeLambda,
                    edgeTopFrac=args.edgeTopFrac,
                    edgeFreqPeriod=args.edgeFreqPeriod,
                    assortative=args.assortative,
                    mem3OptSteps=args.mem3OptSteps,
                    speciesPeriod=args.speciesPeriod,
                    speciesThresh=args.speciesThresh,
                    speciesCullFrac=args.speciesCullFrac,
                    catastropheFrac=args.catastropheFrac,
                    useFlocking=(not args.noFlocking))

        dt = res["elapsedSec"]
        gens = res["gensDone"]
        r = res["genPerSec"]
        s_gen = (dt / gens) if gens > 0 else float("inf")
        g_last = res["events"][-1]["gen"] if res["events"] else 0

        INF = float("inf")
        limit_time_gens = (r * args.timeLimit) if args.timeLimit > 0 else INF
        G_est = min(args.maxIter, g_last + args.stall, limit_time_gens)
        T_est = G_est / r if r > 0 else INF
        cause = ("maxIter" if G_est == args.maxIter else
                 ("stall" if G_est == g_last + args.stall else "timeLimit"))

        print(
            "\n=== ESTIMACIÓN (warmup) ====================================\n"
            f"\tTiempo total:\t{dt:.2f} s (~{dt/60:.2f} min)\n"
            f"\tGeneraciones:\t{gens}\n"
            f"\tVelocidad:\t{r:.2f} gen/s\t({s_gen:.4f} s/gen)\n"
            f"\tÚltima mejora:\tgen {g_last}\n"
            "-----------------------------------------------------------\n"
            f"\tTiempo estimado:\t{T_est:.1f} s (~{T_est/60:.2f} min)\n"
            f"\tCorte dominante:\t{cause}\n"
            "-----------------------------------------------------------\n"
            "\tNota:\tUsar mismos N/twoOptProb/porcentajes y sin --record/--gifOut.\n"
            "===========================================================\n"
        )
        return

    # ---- RUN REAL ----
    res = runGa(coordsPath=args.file,
                N=args.N,
                maxIter=args.maxIter,
                survivorsFrac=s,
                crossoverFrac=c,
                mutationFrac=m,
                pc=pc,
                pm=None if pm < 0 else pm,
                elitismFrac=elitism,
                tournamentK=k,
                useSCX=args.scx,
                twoOptProb=twoOptProb,
                stallGenerations=args.stall,
                timeLimitSec=args.timeLimit,
                recordImprovements=args.record,
                framesDir=args.framesDir,
                seed=args.seed,
                trace_csv=args.csv,
                eaxFrac=args.eaxFrac,
                edgeLambda=args.edgeLambda,
                edgeTopFrac=args.edgeTopFrac,
                edgeFreqPeriod=args.edgeFreqPeriod,
                assortative=args.assortative,
                mem3OptSteps=args.mem3OptSteps,
                speciesPeriod=args.speciesPeriod,
                speciesThresh=args.speciesThresh,
                speciesCullFrac=args.speciesCullFrac,
                catastropheFrac=args.catastropheFrac,
                useFlocking=(not args.noFlocking)
                )


    # --- métricas de tiempo ---
    dt = res["elapsedSec"]
    gens = res["gensDone"]
    r = res["genPerSec"]
    s_gen = (dt / gens) if gens > 0 else float("inf")

    print(
        "\n=== RESUMEN ================================================\n"
        f"\tInstancia:\t\t{res['name']}\n"
        f"\tMejor distancia:\t{res['bestCost']}\n"
        f"\tEventos (mejoras):\t{len(res['events'])}\n"
        f"\tMotivo de parada:\t{res['stoppedBy']}\n"
        "-----------------------------------------------------------\n"
        f"\tTiempo:\t\t\t{dt:.2f} s (~{dt/60:.2f} min)\n"
        f"\tGeneraciones:\t\t{gens}\n"
        f"\tVelocidad:\t\t{r:.2f} gen/s\t({s_gen:.4f} s/gen)\n"
        "-----------------------------------------------------------\n"
        f"\tMejor tour (0-index):\n\t- {res['bestTour']}\n"
        "===========================================================\n"
    )

    # Plot/GIF
    if not args.noPlot:
        plotResults(res["coords"], res["bestTour"], res["history"], title=res["name"])
    if args.gifOut:
        if not res["framesDir"]:
            print("\n[INFO]\n\tNo se grabaron frames; ejecuta con --record para generar GIF.\n-----------------------------------------------------------")
        else:
            makeGifFromFrames(res["framesDir"], args.gifOut, fps=5)
            print(f"\n[OK]\n\tGIF guardado en:\t{args.gifOut}\n-----------------------------------------------------------")

if __name__ == "__main__":
    main()