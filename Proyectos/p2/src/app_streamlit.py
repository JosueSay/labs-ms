import sys
import os
import subprocess
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from core.metrics import buildSummaryMetrics
from core.controller import SimulationController

from io_mm1.config_loader import loadConfig
from io_mm1.writers import (
    saveEffectiveConfig,
    saveRawEvents,
    saveQueueTimes,
    saveQueueLengthSeries,
    saveServerUtilizationSeries,
    saveSummaryMetrics,
    saveReportResumen,
)

from sim.plots import (
    generateAllFigures,
    buildLqEvolutionFigureFromSeries,
    buildRhoEvolutionFigureFromSeries,
    buildQueueAndBusyBandsFromSeries,
    buildServerUtilizationFromSeries,
    buildTheoryVsSimBarsFromSummary,
)


def initSession():
    # inicializa config y controlador en session_state
    if "cfg" not in st.session_state:
        cfg_path = os.path.join("configs", "default.yaml")
        cfg = loadConfig(cfg_path)
        st.session_state["cfg"] = cfg

    if "controller" not in st.session_state:
        cfg = st.session_state["cfg"]
        model_cfg = cfg["model"]
        model_params = cfg["model_params"]
        sim_cfg = cfg["simulation"]
        seed = cfg["project"]["seed"]
        controller = SimulationController(model_cfg, model_params, sim_cfg, rng_seed=seed)
        st.session_state["controller"] = controller

    if "last_snapshot" not in st.session_state:
        st.session_state["last_snapshot"] = None
        
    if "auto_loop" not in st.session_state:
        st.session_state["auto_loop"] = False        


def runTick():
    controller = st.session_state["controller"]

    # snapshot rápido para ver estado actual
    snap_before = controller.getSnapshot(include_series=False)

    # solo avanzar si NO está pausado, NO terminado y hay velocidad
    if not snap_before.get("paused", False) and not snap_before.get("ended", False) and controller.speed > 0:
        _ = controller.tick(collect_series=True)

    full_snapshot = controller.getSnapshot(include_series=True, max_points=None)
    st.session_state["last_snapshot"] = full_snapshot
    return full_snapshot


def buildSimResultForOutputs(controller, warmup_minutes):
    # arma sim_result compatible con metrics.buildSummaryMetrics y writers
    model = controller.model
    if model is None:
        return None

    start_time = model.initial_time
    end_time = model.sim_time
    total_duration = max(1e-12, end_time - start_time)
    rho_avg = min(1.0, max(0.0, model.busy_time_accum / total_duration))

    warmup_hours = max(0.0, float(warmup_minutes) / 60.0)

    sim_result = {
        "raw_events": model.raw_events,
        "queue_times": model.queue_times,
        "queue_length_series": model.series_queue_len,
        "server_utilization_series": model.series_utilization,
        "rho_avg": rho_avg,
        "start_time": start_time,
        "end_time": end_time,
        "warmup_hours": warmup_hours,
    }
    return sim_result


def saveOutputsFromController():
    # usa el estado actual del controlador para guardar csvs, reporte y figuras
    cfg = st.session_state["cfg"]
    controller = st.session_state["controller"]
    sim_cfg = cfg["simulation"]

    sim_result = buildSimResultForOutputs(controller, warmup_minutes=sim_cfg.get("warmup_minutes"))
    if sim_result is None:
        st.warning("No hay resultados de simulación para guardar")
        return

    summary = buildSummaryMetrics(cfg, sim_result)

    # guardado en disco usando writers
    saveEffectiveConfig(cfg)
    saveServerUtilizationSeries(cfg, sim_result.get("server_utilization_series"))
    saveQueueLengthSeries(cfg, sim_result.get("queue_length_series"))
    saveQueueTimes(cfg, sim_result.get("queue_times"))
    saveRawEvents(cfg, sim_result.get("raw_events"))
    saveSummaryMetrics(cfg, summary)
    saveReportResumen(cfg, summary)

    # generar figuras png usando los csv recién guardados
    generateAllFigures(cfg, show=False, lq_window=15)

    st.success(
        f"Archivos guardados en:\n"
        f"- Datos: {cfg['run_data_dir']}\n"
        f"- Resultados: {cfg['run_results_dir']}\n"
        f"- Figuras: {os.path.join(cfg['run_results_dir'])}"
    )


def launchPygameWindow():
    # lanza la ventana pygame en un proceso separado
    script_path = os.path.join("src", "sim", "pygame_app.py")
    if not os.path.isfile(script_path):
        st.warning("No existe src/sim/pygame_app.py, crea ese archivo para habilitar la simulación visual")
        return

    try:
        env = os.environ.copy()
        src_path = os.path.abspath("src")
        prev = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = src_path if not prev else prev + os.pathsep + src_path

        subprocess.Popen([sys.executable, script_path], env=env)
        st.info("Ejecución de pygame lanzado en una ventana separada.")
    except Exception as ex:
        st.error(f"Error al lanzar pygame: {ex}")


def renderControls(snapshot):
    cfg = st.session_state["cfg"]
    controller = st.session_state["controller"]
    model_cfg = cfg["model"]
    sim_cfg = cfg["simulation"]

    st.sidebar.header("Controles de simulación")

    # λ
    lambda_val = st.sidebar.slider(
        "Tasa de llegada - λ (lambda)",
        min_value=1.0,
        max_value=30.0,
        value=float(model_cfg["lambda"]),
        step=0.5,
        key="lambda_slider",
    )

    # μ
    mu_val = st.sidebar.slider(
        "Tasa de servicio - μ (mu)",
        min_value=1.0,
        max_value=40.0,
        value=float(model_cfg["mu"]),
        step=0.5,
        key="mu_slider",
    )

    if mu_val <= lambda_val:
        st.sidebar.warning("Para estabilidad se recomienda μ > λ")

    # Actualizar modelo y cfg en memoria
    controller.updateParams(lambda_rate=lambda_val, mu_rate=mu_val)
    model_cfg["lambda"] = lambda_val
    model_cfg["mu"] = mu_val

    # Velocidad
    speed_val = st.sidebar.slider(
        "Velocidad (factor)",
        min_value=0.0,
        max_value=3600.0,
        value=float(controller.speed),
        step=10.0,
        help="0 = pausado y 3600 = 1h de simulación por segundo real (aproximado)",
        key="speed_slider",
    )
    controller.setSpeed(speed_val)

    # Duración de simulación
    sim_hours = sim_cfg["sim_time_hours"]
    sim_hours_new = st.sidebar.slider(
        "Duración total de simulación (h)",
        min_value=1.0,
        max_value=48.0,
        value=float(sim_hours),
        step=1.0,
        key="sim_hours_slider",
    )
    if sim_hours_new != sim_hours:
        sim_cfg["sim_time_hours"] = sim_hours_new
        controller.setEndTimeHours(sim_hours_new)

    st.sidebar.markdown("---")

    # Botones

    paused = snapshot.get("paused", True)
    ended = snapshot.get("ended", False)
    is_running = (not paused) and (not ended) and controller.speed > 0

    if "simulation_started" not in st.session_state:
        st.session_state["simulation_started"] = False

    if ended:
        st.session_state["simulation_started"] = False

    _, col_start, col_toggle, col_reset, _ = st.sidebar.columns([1, 2, 2, 2, 1])

    # START
    start_btn_type = "primary" if st.session_state["simulation_started"] else "secondary"
    start_clicked = col_start.button("▶ Iniciar", type=start_btn_type)

    # TOGGLE (pausa / reanudar)
    toggle_label = "⏸ Pausa" if is_running else "▶ Reanudar"
    if st.session_state["simulation_started"] and paused and not ended:
        toggle_type = "primary"     # Reanudar activo
    else:
        toggle_type = "secondary"   # Pausa o inactivo

    toggle_clicked = col_toggle.button(toggle_label, type=toggle_type)

    # RESET
    reset_clicked = col_reset.button("⟲ Reiniciar", type="secondary")

    if start_clicked:
        controller.resetSimulation()
        controller.startSimulation()
        controller.resumeSimulation()
        if controller.speed <= 0:
            controller.setSpeed(3600.0)
        st.session_state["last_snapshot"] = None
        st.session_state["auto_loop"] = True
        st.session_state["simulation_started"] = True
        st.rerun()

    if toggle_clicked:
        if is_running:
            controller.pauseSimulation()
            st.session_state["auto_loop"] = False
        else:
            controller.resumeSimulation()
            st.session_state["auto_loop"] = True
        st.rerun()

    if reset_clicked:
        controller.resetSimulation()
        st.session_state["last_snapshot"] = None
        st.session_state["simulation_started"] = False
        st.rerun()

    st.sidebar.markdown("---")
    _, col1, col2, _ = st.sidebar.columns([1, 2, 2, 1])

    if col1.button("Generar reporte"):
        saveOutputsFromController()

    if col2.button("Ver simulación"):
        launchPygameWindow()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; font-size: 0.85rem; color: gray;">
            <strong>Modo: {cfg['simulation'].get('mode')} -
            Repeticiones configuradas: {cfg['simulation'].get('replications')}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderMetrics(snapshot):
    controller = st.session_state["controller"]
    model_state = snapshot.get("model_state", {}) or {}

    sim_time = model_state.get("sim_time", 0.0)
    queue_length = model_state.get("queue_length", 0)
    server_state = model_state.get("server_state", "idle")
    n_created = model_state.get("n_customers_created", 0)
    n_completed = model_state.get("n_customers_completed", 0)
    rho_avg = model_state.get("rho_avg_so_far", None)
    end_time = snapshot.get("end_time", None)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("**Tiempo de simulación (horas)**", f"{sim_time:.3f}")
    col2.metric("**Clientes en cola (Lq)**", str(queue_length))
    col3.metric("**Clientes creados (conteo)**", str(n_created))
    col4.metric("**Clientes completados (conteo)**", str(n_completed))

    col5, col6 = st.columns(2)
    col5.metric("Estado del servidor", server_state)

    if rho_avg is not None:
        # ρ = utilización promedio del servidor en porcentaje de ocupación
        col6.metric("**Promedio de utilización (ρ)**", f"{rho_avg:.3f}")
    else:
        col6.metric("**Promedio de utilización (ρ)**", "N/A")


    caption_text = (
        f"<strong>Pausado: {snapshot.get('paused')} - Terminado: {snapshot.get('ended')} - Velocidad: {controller.speed:.1f}</strong>"
    )

    if end_time is not None and end_time > 0:
        progress = min(100.0, max(0.0, 100.0 * sim_time / end_time))
        caption_text += f" <strong> - Progreso: {progress:.1f}% (objetivo {end_time:.2f} h)</strong>"

    st.markdown(
        f"""
        <div style="text-align:center; opacity:0.6; font-size:0.8rem;">
            {caption_text}
        </div>
        """,
        unsafe_allow_html=True
    )



    if snapshot.get("ended"):
        st.success(f"Simulación terminada (t = {sim_time:.3f} h, objetivo {end_time:.3f} h)")


def renderCharts(snapshot):
    cfg = st.session_state["cfg"]
    controller = st.session_state["controller"]
    model = controller.model

    queue_series = snapshot.get("queue_length_series", []) or []
    rho_series = snapshot.get("server_utilization_series", []) or []
    queue_times = getattr(model, "queue_times", []) or []
    raw_events = getattr(model, "raw_events", []) or []

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    # 1) evolución de Lq
    with row1_col1:
        if queue_series:
            fig_q = buildLqEvolutionFigureFromSeries(queue_series, window=15)
            st.pyplot(fig_q, width='stretch')
        else:
            st.info("Sin datos de cola aún")

    # 2) eventos acumulados
    with row1_col2:
        if raw_events:
            fig_ev = buildRhoEvolutionFigureFromSeries(raw_events)
            st.pyplot(fig_ev, width="stretch")
        else:
            st.info("Sin eventos registrados aún")

    # 3) histograma de Lq
    with row1_col3:
        if queue_series:
            df_q = pd.DataFrame(queue_series)
            if "Lq" in df_q.columns:
                fig, ax = plt.subplots()
                ax.hist(df_q["Lq"].values, bins=20)
                ax.set_title("Histograma de Lq")
                ax.set_xlabel("Lq")
                ax.set_ylabel("frecuencia")
                st.pyplot(fig, width="stretch")
            else:
                st.info("No se encontró columna Lq en los datos de cola")
        else:
            st.info("Sin datos de cola aún")

    st.markdown("---")

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    # 4) ECDF de tiempos (wait, service, system)
    with row2_col1:
        if queue_times:
            df_t = pd.DataFrame(queue_times)
            cols = [c for c in ["wait_time", "service_time", "system_time"] if c in df_t.columns]
            if not cols:
                st.info("No hay columnas de tiempos para graficar")
            else:
                fig, ax = plt.subplots()
                for col in cols:
                    vals = df_t[col].dropna().values
                    if len(vals):
                        x = np.sort(vals.astype(float))
                        y = np.arange(1, len(x) + 1) / len(x)
                        ax.plot(x, y, label=col)
                ax.set_title("ECDF de tiempos")
                ax.set_xlabel("horas")
                ax.set_ylabel("F(x)")
                ax.legend(loc="best")
                st.pyplot(fig, width="stretch")
        else:
            st.info("Sin datos de tiempos de cola aún")

    # 5) llegada vs tiempo en sistema (hexbin)
    with row2_col2:
        if queue_times:
            df_t = pd.DataFrame(queue_times)
            if {"t_arrival", "system_time"}.issubset(df_t.columns):
                t_arr = df_t["t_arrival"].values.astype(float)
                sys_t = df_t["system_time"].values.astype(float)
                if len(t_arr) and len(sys_t):
                    fig, ax = plt.subplots()
                    hb = ax.hexbin(t_arr, sys_t, gridsize=40, mincnt=1)
                    cb = fig.colorbar(hb, ax=ax)
                    cb.set_label("conteo")
                    ax.set_title("Llegada vs tiempo en sistema (densidad)")
                    ax.set_xlabel("t_arrival (h)")
                    ax.set_ylabel("system_time (h)")
                    st.pyplot(fig, width="stretch")
                else:
                    st.info("No hay datos suficientes para el hexbin")
            else:
                st.info("Faltan columnas t_arrival o system_time en queue_times")
        else:
            st.info("Sin datos de tiempos de cola aún")

    # 6) clientes atendidos (acumulado)
    with row2_col3:
        if queue_times:
            df_t = pd.DataFrame(queue_times)
            if "t_end_service" in df_t.columns:
                df_t = df_t.dropna(subset=["t_end_service"]).sort_values("t_end_service")
                if not df_t.empty:
                    y = np.arange(1, len(df_t) + 1)
                    fig, ax = plt.subplots()
                    ax.step(df_t["t_end_service"].values, y, where="post")
                    ax.set_title("Clientes atendidos (acumulado)")
                    ax.set_xlabel("t_end_service (h)")
                    ax.set_ylabel("clientes")
                    st.pyplot(fig, width="stretch")
                else:
                    st.info("No hay tiempos de fin de servicio válidos")
            else:
                st.info("No existe columna t_end_service en queue_times")
        else:
            st.info("Sin datos de tiempos de cola aún")

    st.markdown("---")

    row3_col1, row3_col2, row3_col3 = st.columns(3)

    # 7) Lq + bloques de ocupación
    with row3_col1:
        if queue_series and rho_series:
            fig_busy = buildQueueAndBusyBandsFromSeries(queue_series, rho_series, lq_window=15, min_busy_minutes=5)
            st.pyplot(fig_busy, width='stretch')
        else:
            st.info("Sin datos suficientes para cola + ocupación")

    # 8) ocupación agregada (duty cycle)
    with row3_col2:
        if rho_series:
            fig_su = buildServerUtilizationFromSeries(rho_series, nbins=60)
            st.pyplot(fig_su, width='stretch')
        else:
            st.info("Sin datos de ocupación aún")

    # 9) teoría vs simulación (usando métricas de summary al vuelo)
    with row3_col3:
        if queue_times:
            sim_cfg = cfg["simulation"]
            sim_result = buildSimResultForOutputs(
                controller,
                warmup_minutes=sim_cfg.get("warmup_minutes"),
            )

            summary = buildSummaryMetrics(cfg, sim_result)
            last_row = None

            if summary is None:
                last_row = None
            elif isinstance(summary, pd.DataFrame):
                if not summary.empty:
                    last_row = summary.iloc[-1].to_dict()
            elif isinstance(summary, dict):
                # ya es un solo registro en forma de dict
                last_row = summary

            if last_row is not None:
                fig_tv = buildTheoryVsSimBarsFromSummary(last_row)
                st.pyplot(fig_tv, width="stretch")
            else:
                st.info("No se pudo construir summary_metrics (sin datos válidos)")
        else:
            st.info("Aún no hay datos suficientes para comparación")


def mainApp():
    st.set_page_config(page_title="Simulador M/M/1", layout="wide")
    st.title("Simulador M/M/1 - Restaurante")

    initSession()

    snapshot = runTick()

    renderControls(snapshot)
    st.markdown("---")
    renderMetrics(snapshot)
    st.markdown("---")
    renderCharts(snapshot)
    
    controller = st.session_state["controller"]
    if (
        st.session_state.get("auto_loop", False)
        and not snapshot.get("paused")
        and not snapshot.get("ended")
        and controller.speed > 0
    ):
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    mainApp()
