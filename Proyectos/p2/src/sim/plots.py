import os
import numpy as np
import pandas as pd

from sim.styles import applyPlotStyle, getAxes, saveOrShow
from utils.fs import ensureDir


def getFiguresDir(cfg):
    # arma la ruta donde se guardan las figuras
    figures_dir = os.path.join(cfg["run_results_dir"], "figures")
    ensureDir(figures_dir)  # crea el directorio si no existe
    return figures_dir


def movingAverage(y, window):
    # valida ventana antes de calcular
    if window is None or window <= 1 or window > len(y):
        return None
    y = np.asarray(y, dtype=float)
    kernel = np.ones(int(window), dtype=float) / float(window)  # kernel promedio
    return np.convolve(y, kernel, mode="valid")


def mergeBusyBlocks(times, states, min_duration):
    # arma bloques busy ignorando cambios muy cortos
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
            # agrega solo si dura lo suficiente
            if (end - start) >= min_duration:
                blocks.append((start, end))
            busy = False

    # si el último segmento quedó abierto
    if busy and len(times):
        end = times[-1]
        if (end - start) >= min_duration:
            blocks.append((start, end))

    # junta bloques separados por gaps pequeños
    merged = []
    if not blocks:
        return merged

    cur_s, cur_e = blocks[0]
    for s, e in blocks[1:]:
        # une si el gap es menor al mínimo
        if s - cur_e <= min_duration:
            cur_e = e
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e

    merged.append((cur_s, cur_e))
    return merged


def binAverage(times, values, nbins=60):
    # promedia valores en bins uniformes sobre el rango de tiempo
    times = np.asarray(times, float)
    values = np.asarray(values, float)

    if len(times) == 0:
        return np.array([]), np.array([])

    t0, t1 = times.min(), times.max()
    if t1 <= t0:
        return np.array([]), np.array([])

    edges = np.linspace(t0, t1, nbins + 1)  # bordes de cada bin
    idx = np.digitize(times, edges) - 1     # asigna cada tiempo a un bin

    out_x, out_y = [], []
    for b in range(nbins):
        mask = idx == b  # elementos que caen en este bin
        if mask.any():
            out_x.append(0.5 * (edges[b] + edges[b + 1]))  # centro del bin
            out_y.append(values[mask].mean())              # promedio de valores del bin

    return np.array(out_x), np.array(out_y)


def plotLqEvolution(cfg, window=15, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)
    path_csv = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")

    df = pd.read_csv(path_csv).sort_values("timestamp_sim")
    t = df["timestamp_sim"].values
    lq = df["Lq"].values

    fig, ax = getAxes(title="Evolución temporal de la cola", xlabel="Tiempo sim (h)", ylabel="Lq")

    # serie original para ver ruido y variaciones rápidas
    ax.plot(t, lq, alpha=0.35, label="Lq(t) crudo")

    if window and window > 1:
        # se calcula el promedio móvil si el tamaño de ventana lo permite
        ma = movingAverage(lq, window)
        if ma is not None:
            t_ma = t[window - 1 :]
            # serie suavizada para ver tendencia general
            ax.plot(t_ma, ma, label=f"Lq(t) suavizado (w={window})")

    ax.legend(loc="best")

    out = os.path.join(figures_dir, "queue_length_evolution.png")

    # si show es false se guarda, si no se muestra en pantalla
    saveOrShow(fig, out if not show else None)

    return out


def plotLqHistogram(cfg, bins=20, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)

    # carga los datos de longitudes de cola
    path_csv = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")
    df = pd.read_csv(path_csv)

    # arma el histograma
    fig, ax = getAxes(title="Histograma de Lq", xlabel="Lq", ylabel="Frecuencia")
    ax.hist(df["Lq"].values, bins=bins)

    # guarda o muestra la figura
    out = os.path.join(figures_dir, "queue_length_hist.png")
    saveOrShow(fig, out if not show else None)
    return out


def auxECDF(x):
    # ordena y genera la ecdf
    x = np.sort(np.asarray(x, dtype=float))
    y = np.arange(1, len(x) + 1) / len(x) if len(x) else np.array([])
    return x, y


def plotTimesECDF(cfg, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)

    # carga los tiempos del sistema
    path_csv = os.path.join(cfg["run_data_dir"], "queue_times.csv")
    df = pd.read_csv(path_csv)

    # genera las curvas ecdf
    fig, ax = getAxes(title="ECDF de tiempos", xlabel="Horas", ylabel="F(x)")
    for col in ["wait_time", "service_time", "system_time"]:
        x = df[col].dropna().values
        if len(x):
            xx, yy = auxECDF(x)
            ax.plot(xx, yy, label=col)
    ax.legend(loc="best")

    # exporta la figura
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

    fig, ax = getAxes(
        title="Llegada vs tiempo en sistema (densidad)",
        xlabel="t_arrival (h)",
        ylabel="system_time (h)"
    )
    hb = ax.hexbin(t_arr, sys_t, gridsize=gridsize, mincnt=1)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("conteo")

    # calcula tendencia usando medianas por bin
    if len(df) > 5:
        nbins = min(25, max(5, len(df) // 20))
        bins = np.linspace(t_arr.min(), t_arr.max(), nbins + 1)

        idx = np.digitize(t_arr, bins)
        med_x, med_y = [], []

        for b in range(1, nbins + 1):
            mask = idx == b
            # solo usa bins con suficientes puntos
            if mask.sum() >= 3:
                med_x.append(t_arr[mask].mean())
                med_y.append(np.median(sys_t[mask]))

        # agrega línea de tendencia si hay datos
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

    fig, ax = getAxes(
        title="Clientes atendidos (acumulado)",
        xlabel="t_end_service (h)",
        ylabel="clientes"
    )

    # escalón porque el conteo es acumulado
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

    # genera una curva acumulada por tipo de evento
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
    figures_dir = getFiguresDir(cfg)

    path_lq = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")
    path_rho = os.path.join(cfg["run_data_dir"], "server_utilization.csv")

    # lecturas base ordenadas por tiempo
    lq = pd.read_csv(path_lq).sort_values("timestamp_sim")
    rho = pd.read_csv(path_rho).sort_values("timestamp_sim")

    t = lq["timestamp_sim"].values
    Lq = lq["Lq"].values

    fig, ax = getAxes(title="Cola con bloques de ocupación", xlabel="Tiempo sim (h)", ylabel="Lq")

    # traza la serie cruda
    ax.plot(t, Lq, alpha=0.2, label="Lq(t) crudo")

    # aplica suavizado si corresponde
    if lq_window and lq_window > 1:
        ma = movingAverage(Lq, lq_window)
        if ma is not None:
            ax.plot(t[lq_window - 1:], ma, linewidth=2.0, label=f"Lq suavizado (w={lq_window})")

    # identifica rangos con alta ocupación
    rt = rho["timestamp_sim"].values
    rv = rho["rho_instant"].values.astype(float)
    min_busy_h = float(min_busy_minutes) / 60.0
    blocks = mergeBusyBlocks(rt, rv, min_duration=min_busy_h)

    # pinta los bloques sobre la figura
    for s, e in blocks:
        ax.axvspan(s, e, alpha=0.08, color="gray")

    ax.legend(loc="best")

    out = os.path.join(figures_dir, "queue_and_busy_bands.png")
    saveOrShow(fig, out if not show else None)
    return out


def plotServerUtilization(cfg, nbins=60, show=False):
    applyPlotStyle()
    figures_dir = getFiguresDir(cfg)

    path_rho = os.path.join(cfg["run_data_dir"], "server_utilization.csv")

    rho = pd.read_csv(path_rho).sort_values("timestamp_sim")
    t = rho["timestamp_sim"].values
    r = rho["rho_instant"].values.astype(float)

    # promedio por intervalo
    tx, ry = binAverage(t, r, nbins=max(30, nbins))

    fig, ax = getAxes(
        title="Ocupación del servidor",
        xlabel="Tiempo sim (h)",
        ylabel="ρ"
    )

    if len(tx) > 1:
        bar_width = (tx[1] - tx[0]) * 0.9
        ax.bar(
            tx, ry,
            width=bar_width,
            alpha=0.5,
            color="#4A90E2",
            label="ρ promedio por intervalo"
        )
    elif len(tx) == 1:
        ax.plot(
            tx, ry,
            marker="o",
            linestyle="",
            color="#4A90E2",
            label="ρ promedio por intervalo"
        )
    if len(t):
        cum = np.cumsum(r) / np.arange(1, len(r) + 1)
        ax.plot(
            t, cum,
            linestyle="--",
            linewidth=2,
            color="#F5A623",
            label="ρ acumulado"
        )

    # límites y leyenda
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

    # se filtran métricas que tengan valores en ambas fuentes
    idx = [i for i, (t, s) in enumerate(zip(theory, sim)) if pd.notnull(t) and pd.notnull(s)]
    if not idx:
        return None

    labels = [labels[i] for i in idx]
    theory = [theory[i] for i in idx]
    sim = [sim[i] for i in idx]

    x = np.arange(len(labels))
    width = 0.38

    fig, ax = getAxes(title="Teoría vs Simulación (última réplica)")

    # barras lado a lado para comparación rápida
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
    results["queue_and_busy_bands"] = plotQueueLenWithBusyBands(cfg, lq_window=lq_window, min_busy_minutes=5, show=show)
    results["server_utilization"] = plotServerUtilization(cfg, nbins=60, show=show)
    results["theory_vs_sim_bars"] = plotTheoryVsSimBars(cfg, show=show)
    return results


def buildLqEvolutionFigureFromSeries(queue_series, window=15):
    # arma la figura de evolución de lq para streamlit
    applyPlotStyle()
    fig, ax = getAxes(title="Evolución temporal de la cola", xlabel="Tiempo sim (h)", ylabel="Lq")

    if not queue_series:
        # evita fallar cuando no hay datos
        return fig

    df = pd.DataFrame(queue_series).sort_values("timestamp_sim")
    t = df["timestamp_sim"].values
    lq = df["Lq"].values

    # traza la serie cruda
    ax.plot(t, lq, alpha=0.35, label="Lq(t) crudo")

    if window and window > 1 and len(lq) >= window:
        ma = movingAverage(lq, window)
        if ma is not None:
            # ajusta el eje temporal para el promedio móvil
            t_ma = t[window - 1 :]
            ax.plot(t_ma, ma, label=f"Lq(t) suavizado (w={window})")

    ax.legend(loc="best")
    return fig


def buildRhoEvolutionFigureFromSeries(events_series):
    applyPlotStyle()

    # crea la figura base para mostrar eventos acumulados
    fig, ax = getAxes(title="Eventos acumulados",
                      xlabel="tiempo sim (h)",
                      ylabel="acumulado")

    if not events_series:
        return fig

    df = pd.DataFrame(events_series)

    # verificamos que existan las columnas clave
    if {"timestamp_sim", "event_type"}.issubset(df.columns):
        df = df.sort_values("timestamp_sim")

        # graficamos cada tipo de evento como serie acumulada
        for ev in ["arrival", "service_start", "service_end"]:
            sub = df[df["event_type"] == ev]
            if not sub.empty:
                t_ev = sub["timestamp_sim"].values
                y_ev = np.arange(1, len(sub) + 1)
                ax.step(t_ev, y_ev, where="post", label=ev)

        ax.legend(loc="best")

    return fig


def buildQueueAndBusyBandsFromSeries(queue_series, rho_series, lq_window=15, min_busy_minutes=5):
    applyPlotStyle()

    # figura base para mostrar Lq y zonas de ocupación
    fig, ax = getAxes(title="Cola con bloques de ocupación",
                      xlabel="Tiempo sim (h)",
                      ylabel="Lq")

    if not queue_series or not rho_series:
        return fig

    lq = pd.DataFrame(queue_series).sort_values("timestamp_sim")
    rho = pd.DataFrame(rho_series).sort_values("timestamp_sim")

    t = lq["timestamp_sim"].values
    Lq = lq["Lq"].values

    # serie Lq original, sin suavizar
    ax.plot(t, Lq, alpha=0.2, label="Lq(t) crudo")

    # suavizado opcional con ventana móvil
    if lq_window and lq_window > 1 and len(Lq) >= lq_window:
        ma = movingAverage(Lq, lq_window)
        if ma is not None:
            ax.plot(t[lq_window - 1:], ma, linewidth=2.0,
                    label=f"Lq suavizado (w={lq_window})")

    rt = rho["timestamp_sim"].values
    rv = rho["rho_instant"].values.astype(float)

    # convertimos minutos ocupados a horas para filtrar bloques
    min_busy_h = float(min_busy_minutes) / 60.0

    # obtenemos bloques de tiempo donde rho > umbral definido
    blocks = mergeBusyBlocks(rt, rv, min_duration=min_busy_h)

    # pintamos las franjas de ocupación
    for s, e in blocks:
        ax.axvspan(s, e, alpha=0.08, color="gray")

    ax.legend(loc="best")
    return fig


def buildServerUtilizationFromSeries(rho_series, nbins=60):
    # versión en memoria sin tendencia ni teoría
    applyPlotStyle()
    fig, ax = getAxes(
        title="Ocupación del servidor",
        xlabel="Tiempo sim (h)",
        ylabel="ρ"
    )

    if not rho_series:
        return fig

    rho = pd.DataFrame(rho_series).sort_values("timestamp_sim")
    t = rho["timestamp_sim"].values
    r = rho["rho_instant"].values.astype(float)

    if not len(t):
        return fig

    # promedio por intervalos
    tx, ry = binAverage(t, r, nbins=max(30, nbins))

    # === promedio por intervalo (azul) ===
    if len(tx) > 1:
        bar_width = (tx[1] - tx[0]) * 0.9
        ax.bar(
            tx, ry,
            width=bar_width,
            alpha=0.5,
            color="#4A90E2",
            label="ρ promedio por intervalo"
        )
    elif len(tx) == 1:
        ax.plot(
            tx, ry,
            marker="o",
            linestyle="",
            color="#4A90E2",
            label="ρ promedio por intervalo"
        )

    # === ρ acumulado (naranja) ===
    cum = np.cumsum(r) / np.arange(1, len(r) + 1)
    ax.plot(
        t, cum,
        linestyle="--",
        linewidth=2,
        color="#F5A623",
        label="ρ acumulado"
    )

    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="best")
    return fig


def buildTheoryVsSimBarsFromSummary(last_row_dict):
    # compara teoría vs simulación para el último estado
    applyPlotStyle()
    fig, ax = getAxes(title="Teoría vs Simulación (estado actual)")

    labels = ["ρ", "L", "Lq", "W", "Wq"]
    theory = [
        last_row_dict.get("rho_theory"),
        last_row_dict.get("L_theory"),
        last_row_dict.get("Lq_theory"),
        last_row_dict.get("W_theory"),
        last_row_dict.get("Wq_theory"),
    ]
    sim = [
        last_row_dict.get("rho_sim"),
        last_row_dict.get("L_sim"),
        last_row_dict.get("Lq_sim"),
        last_row_dict.get("W_sim"),
        last_row_dict.get("Wq_sim"),
    ]

    # filtra métricas que tengan ambos valores
    idx = [i for i, (t, s) in enumerate(zip(theory, sim)) if pd.notnull(t) and pd.notnull(s)]
    if not idx:
        return fig

    labels = [labels[i] for i in idx]
    theory = [theory[i] for i in idx]
    sim = [sim[i] for i in idx]

    x = np.arange(len(labels))
    width = 0.38

    # barras comparativas
    ax.bar(x - width / 2, theory, width, label="Teoría")
    ax.bar(x + width / 2, sim, width, label="Simulación")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="best")
    return fig
