import os
import numpy as np
import pandas as pd

from utils.fs import ensureDir
from sim.styles import applyPlotStyle, getAxes, saveOrShow

def getFiguresDir(cfg):
    figures_dir = os.path.join(cfg["run_results_dir"], "figures")
    ensureDir(figures_dir)
    return figures_dir


def movingAverage(y, window):
    if window is None or window <= 1 or window > len(y):
        return None
    y = np.asarray(y, dtype=float)
    kernel = np.ones(int(window), dtype=float) / float(window)
    return np.convolve(y, kernel, mode="valid")


def mergeBusyBlocks(times, states, min_duration):
    # fusiona segmentos busy contiguos e ignora toggles muy cortos
    blocks = []
    busy = False
    start = None
    for i in range(len(states)):
        t = times[i]
        s = states[i] > 0.5
        if s and not busy:
            busy, start = True, t
        elif not s and busy:
            end = t
            if (end - start) >= min_duration:
                blocks.append((start, end))
            busy = False
    # si terminó ocupado
    if busy and len(times):
        end = times[-1]
        if (end - start) >= min_duration:
            blocks.append((start, end))
    # fusionar bloques muy cercanos (gaps pequeños)
    merged = []
    if not blocks:
        return merged
    cur_s, cur_e = blocks[0]
    for s, e in blocks[1:]:
        if s - cur_e <= min_duration:  # une gaps pequeños
            cur_e = e
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged


def binAverage(times, values, nbins=60):
    # promedia valores por intervalos uniformes de tiempo
    times = np.asarray(times, float)
    values = np.asarray(values, float)
    if len(times) == 0:
        return np.array([]), np.array([])
    t0, t1 = times.min(), times.max()
    if t1 <= t0:
        return np.array([]), np.array([])
    edges = np.linspace(t0, t1, nbins + 1)
    idx = np.digitize(times, edges) - 1
    out_x, out_y = [], []
    for b in range(nbins):
        mask = idx == b
        if mask.any():
            out_x.append(0.5 * (edges[b] + edges[b + 1]))
            out_y.append(values[mask].mean())
    return np.array(out_x), np.array(out_y)


def plotLqEvolution(cfg, window=15, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")

    df = pd.read_csv(path_csv).sort_values("timestamp_sim")
    t = df["timestamp_sim"].values
    lq = df["Lq"].values

    fig, ax = getAxes(title="Evolución temporal de la cola", xlabel="Tiempo sim (h)", ylabel="Lq")
    ax.plot(t, lq, alpha=0.35, label="Lq(t) crudo")
    if window and window > 1:
        ma = movingAverage(lq, window)
        if ma is not None:
            t_ma = t[window - 1 :]
            ax.plot(t_ma, ma, label=f"Lq(t) suavizado (w={window})")
    ax.legend(loc="best")

    out = os.path.join(figures_dir, "queue_length_evolution.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotLqHistogram(cfg, bins=20, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")

    df = pd.read_csv(path_csv)
    fig, ax = getAxes(title="Histograma de Lq", xlabel="Lq", ylabel="Frecuencia")
    ax.hist(df["Lq"].values, bins=bins)
    out = os.path.join(figures_dir, "queue_length_hist.png")
    saveOrShow(fig, out if not show else None)
    return out


def auxECDF(x):
    x = np.sort(np.asarray(x, dtype=float))
    y = np.arange(1, len(x) + 1) / len(x) if len(x) else np.array([])
    return x, y


def plotTimesECDF(cfg, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_times.csv")
    df = pd.read_csv(path_csv)

    fig, ax = getAxes(title="ECDF de tiempos", xlabel="Horas", ylabel="F(x)")
    for col in ["wait_time", "service_time", "system_time"]:
        x = df[col].dropna().values
        if len(x):
            xx, yy = auxECDF(x)
            ax.plot(xx, yy, label=col)
    ax.legend(loc="best")

    out = os.path.join(figures_dir, "times_ecdf.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotArrivalVsSystemHexbin(cfg, gridsize=40, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_times.csv")
    df = pd.read_csv(path_csv)

    t_arr = df["t_arrival"].values
    sys_t = df["system_time"].values

    fig, ax = getAxes(title="Llegada vs tiempo en sistema (densidad)", xlabel="t_arrival (h)", ylabel="system_time (h)")
    hb = ax.hexbin(t_arr, sys_t, gridsize=gridsize, mincnt=1)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("conteo")

    # mediana por bins (tendencia)
    if len(df) > 5:
        nbins = min(25, max(5, len(df) // 20))
        bins = np.linspace(t_arr.min(), t_arr.max(), nbins + 1)
        idx = np.digitize(t_arr, bins)
        med_x, med_y = [], []
        for b in range(1, nbins + 1):
            mask = idx == b
            if mask.sum() >= 3:
                med_x.append(t_arr[mask].mean())
                med_y.append(np.median(sys_t[mask]))
        if med_x:
            ax.plot(med_x, med_y, linestyle="--", label="mediana por bin")
            ax.legend(loc="best")

    out = os.path.join(figures_dir, "arrival_vs_system_hexbin.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotCumulativeServed(cfg, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_times.csv")

    df = pd.read_csv(path_csv).sort_values("t_end_service")
    y = np.arange(1, len(df) + 1)

    fig, ax = getAxes(title="Clientes atendidos (acumulado)", xlabel="t_end_service (h)", ylabel="clientes")
    ax.step(df["t_end_service"].values, y, where="post")
    out = os.path.join(figures_dir, "cumulative_served.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotEventsCumulative(cfg, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "raw_events.csv")
    df = pd.read_csv(path_csv).sort_values("timestamp_sim")

    fig, ax = getAxes(title="Eventos acumulados", xlabel="Tiempo sim (h)", ylabel="acumulado")
    for ev in ["arrival", "service_start", "service_end"]:
        sub = df[df["event_type"] == ev]
        if not sub.empty:
            t = sub["timestamp_sim"].values
            y = np.arange(1, len(sub) + 1)
            ax.step(t, y, where="post", label=ev)
    ax.legend(loc="best")

    out = os.path.join(figures_dir, "events_cumulative.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotQueueLenWithBusyBands(cfg, lq_window=15, min_busy_minutes=5, show=False):
    applyPlotStyle()
    figures_dir = os.path.join(cfg["run_results_dir"], "figures")
    ensureDir(figures_dir)

    path_lq = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")
    path_rho = os.path.join(cfg["run_data_dir"], "server_utilization.csv")

    lq = pd.read_csv(path_lq).sort_values("timestamp_sim")
    rho = pd.read_csv(path_rho).sort_values("timestamp_sim")

    t = lq["timestamp_sim"].values
    Lq = lq["Lq"].values

    fig, ax = getAxes(title="Cola con bloques de ocupación", xlabel="Tiempo sim (h)", ylabel="Lq")

    # línea cruda y suavizada (sin saturar de detalles)
    ax.plot(t, Lq, alpha=0.2, label="Lq(t) crudo")
    if lq_window and lq_window > 1:
        ma = movingAverage(Lq, lq_window)
        if ma is not None:
            ax.plot(t[lq_window - 1:], ma, linewidth=2.0, label=f"Lq suavizado (w={lq_window})")

    # bloques de ocupación: fusiona y filtra micro-períodos
    rt = rho["timestamp_sim"].values
    rv = rho["rho_instant"].values.astype(float)
    min_busy_h = float(min_busy_minutes) / 60.0
    blocks = mergeBusyBlocks(rt, rv, min_duration=min_busy_h)
    for s, e in blocks:
        ax.axvspan(s, e, alpha=0.08, color="gray")

    ax.legend(loc="best")
    out = os.path.join(figures_dir, "queue_and_busy_bands.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotServerUtilization(cfg, nbins=60, show=False):
    applyPlotStyle()
    figures_dir = os.path.join(cfg["run_results_dir"], "figures")
    ensureDir(figures_dir)

    path_rho = os.path.join(cfg["run_data_dir"], "server_utilization.csv")
    path_summary = os.path.join(cfg["run_data_dir"], "summary_metrics.csv")

    rho = pd.read_csv(path_rho).sort_values("timestamp_sim")
    t = rho["timestamp_sim"].values
    r = rho["rho_instant"].values.astype(float)

    # promedio por bin (duty cycle por intervalo)
    tx, ry = binAverage(t, r, nbins=max(30, nbins))

    fig, ax = getAxes(title="Ocupación del servidor", xlabel="Tiempo sim (h)", ylabel="ρ")
    # barras/área de duty cycle por intervalo
    if len(tx):
        ax.bar(tx, ry, width=(tx[1] - tx[0]) * 0.9, alpha=0.35, label="ρ promedio por intervalo")
        ax.plot(tx, ry, linewidth=1.5, label="tendencia ρ")

    # promedio acumulado sobre muestras originales (línea suave)
    if len(t):
        cum = np.cumsum(r) / np.arange(1, len(r) + 1)
        ax.plot(t, cum, linestyle="--", label="ρ acumulado")

    # líneas de referencia (teoría y promedio sim guardado)
    rho_avg = None
    rho_theory = None
    if os.path.isfile(path_summary):
        sm = pd.read_csv(path_summary)
        if not sm.empty:
            last = sm.iloc[-1]
            rho_avg = last.get("rho_sim", None)
            rho_theory = last.get("rho_theory", None)

    if rho_avg is not None and not pd.isna(rho_avg) and len(t):
        ax.hlines(y=rho_avg, xmin=t.min(), xmax=t.max(), linestyles=":", label=f"ρ sim ~ {rho_avg:.3f}")
    if rho_theory is not None and not pd.isna(rho_theory) and len(t):
        ax.hlines(y=rho_theory, xmin=t.min(), xmax=t.max(), linestyles="--", label=f"ρ teoría = {rho_theory:.3f}")

    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="best")

    out = os.path.join(figures_dir, "server_utilization.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotTheoryVsSimBars(cfg, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_summary = os.path.join(cfg["run_data_dir"], "summary_metrics.csv")

    sm = pd.read_csv(path_summary)
    if sm.empty:
        return None
    last = sm.iloc[-1]

    labels = ["ρ", "L", "Lq", "W", "Wq"]
    theory = [last.get("rho_theory"), last.get("L_theory"), last.get("Lq_theory"), last.get("W_theory"), last.get("Wq_theory")]
    sim =    [last.get("rho_sim"),    last.get("L_sim"),    last.get("Lq_sim"),    last.get("W_sim"),    last.get("Wq_sim")]

    idx = [i for i, (t, s) in enumerate(zip(theory, sim)) if pd.notnull(t) and pd.notnull(s)]
    if not idx:
        return None
    labels = [labels[i] for i in idx]
    theory = [theory[i] for i in idx]
    sim = [sim[i] for i in idx]

    x = np.arange(len(labels))
    width = 0.38
    fig, ax = getAxes(title="Teoría vs Simulación (última réplica)")
    ax.bar(x - width / 2, theory, width, label="Teoría")
    ax.bar(x + width / 2, sim, width, label="Simulación")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="best")

    out = os.path.join(figures_dir, "theory_vs_sim_bars.png")
    saveOrShow(fig, out if not show else None)
    return out


def generateAllFigures(cfg, show=False, lq_window=15):
    results = {}
    results["queue_length_evolution"] = plotLqEvolution(cfg, window=lq_window, show=show)
    results["queue_length_hist"] = plotLqHistogram(cfg, show=show)
    results["times_ecdf"] = plotTimesECDF(cfg, show=show)
    results["arrival_vs_system_hexbin"] = plotArrivalVsSystemHexbin(cfg, show=show)
    results["cumulative_served"] = plotCumulativeServed(cfg, show=show)
    results["events_cumulative"] = plotEventsCumulative(cfg, show=show)
    # ← usan las dos nuevas
    results["queue_and_busy_bands"] = plotQueueLenWithBusyBands(cfg, lq_window=lq_window, min_busy_minutes=5, show=show)
    results["server_utilization"] = plotServerUtilization(cfg, nbins=60, show=show)
    results["theory_vs_sim_bars"] = plotTheoryVsSimBars(cfg, show=show)
    return results
