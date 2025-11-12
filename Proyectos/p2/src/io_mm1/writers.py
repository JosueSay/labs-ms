import os
import yaml
import pandas as pd
from utils.fs import ensureDir

def saveEffectiveConfig(cfg):
    # guarda la config efectiva en data/runs_*/config_effective.yaml
    if not cfg.get("outputs", True):
        return None
    run_data_dir = cfg["run_data_dir"]
    ensureDir(run_data_dir)
    out_path = os.path.join(run_data_dir, "config_effective.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    return out_path

def writeCsv(rows, out_path, columns=None):
    # escribe una lista de dicts en csv
    if rows is None:
        rows = []
    df = pd.DataFrame(rows)
    if columns:
        # respeta el orden de columnas si se pasa explícito
        for c in columns:
            if c not in df.columns:
                df[c] = pd.NA
        df = df[columns]
    ensureDir(os.path.dirname(out_path))
    df.to_csv(out_path, index=False)
    return out_path

def saveRawEvents(cfg, raw_events):
    # guarda eventos crudos
    if not cfg.get("outputs", True):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "raw_events.csv")
    cols = ["timestamp_sim", "event_type", "customer_id", "queue_length_after", "server_state"]
    return writeCsv(raw_events, out_path, columns=cols)

def saveQueueTimes(cfg, queue_times):
    # guarda tiempos por cliente
    if not cfg.get("outputs", True):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "queue_times.csv")
    cols = ["customer_id", "t_arrival", "t_start_service", "t_end_service", "wait_time", "service_time", "system_time"]
    return writeCsv(queue_times, out_path, columns=cols)

def saveQueueLengthSeries(cfg, queue_length_series):
    # guarda serie Lq(t)
    if not cfg.get("outputs", True):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")
    cols = ["timestamp_sim", "Lq"]
    return writeCsv(queue_length_series, out_path, columns=cols)

def saveServerUtilizationSeries(cfg, server_utilization_series):
    # guarda serie rho(t)
    if not cfg.get("outputs", True):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "server_utilization.csv")
    cols = ["timestamp_sim", "rho_instant"]
    return writeCsv(server_utilization_series, out_path, columns=cols)

def saveSummaryMetrics(cfg, summary_metrics):
    # guarda métricas agregadas en csv (append-friendly)
    if not cfg.get("outputs", True):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "summary_metrics.csv")
    # si existe, hacemos append respetando orden de columnas del archivo
    df_new = pd.DataFrame([summary_metrics])
    if os.path.isfile(out_path):
        df_old = pd.read_csv(out_path)
        # alinear columnas
        for c in df_new.columns:
            if c not in df_old.columns:
                df_old[c] = pd.NA
        for c in df_old.columns:
            if c not in df_new.columns:
                df_new[c] = pd.NA
        df_new = df_new[df_old.columns]
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        ensureDir(os.path.dirname(out_path))
        df_all.to_csv(out_path, index=False)
    else:
        ensureDir(os.path.dirname(out_path))
        df_new.to_csv(out_path, index=False)
    return out_path

def saveReportResumen(cfg, summary_metrics, extra_lines=None):
    # genera un md sencillo con las métricas principales
    if not cfg.get("outputs", True):
        return None
    results_dir = cfg["run_results_dir"]
    ensureDir(results_dir)
    out_path = os.path.join(results_dir, "report_resumen.md")

    lines = []
    lines.append(f"# Resumen de Simulación — {cfg.get('run_id', '')}")
    lines.append("")

    lines.append("## Parámetros")
    lines.append("")
    lines.append(f"- $\\lambda$ (Lambda): **{summary_metrics.get('lambda')}**")
    lines.append(f"- $\\mu$ (Mu): **{summary_metrics.get('mu')}**")
    lines.append("")

    lines.append("## Teoría vs Simulación")
    lines.append("")
    lines.append(f"- $\\rho_{{\\text{{teoría}}}}$: **{summary_metrics.get('rho_theory')}** | $\\rho_{{\\text{{sim}}}}$: **{summary_metrics.get('rho_sim')}**")
    lines.append(f"- $L_{{\\text{{teoría}}}}$: **{summary_metrics.get('L_theory')}** | $L_{{\\text{{sim}}}}$: **{summary_metrics.get('L_sim')}**")
    lines.append(f"- $L_q^{{\\text{{teoría}}}}$: **{summary_metrics.get('Lq_theory')}** | $L_q^{{\\text{{sim}}}}$: **{summary_metrics.get('Lq_sim')}**")
    lines.append(f"- $W_{{\\text{{teoría}}}}$: **{summary_metrics.get('W_theory')}** | $W_{{\\text{{sim}}}}$: **{summary_metrics.get('W_sim')}**")
    lines.append(f"- $W_q^{{\\text{{teoría}}}}$: **{summary_metrics.get('Wq_theory')}** | $W_q^{{\\text{{sim}}}}$: **{summary_metrics.get('Wq_sim')}**")
    lines.append("")

    lines.append("## Ley de Little (Chequeo)")
    lines.append("")
    lines.append(f"- $L \\approx \\lambda \\cdot W$: **{summary_metrics.get('little_L_lambdaW_ok')}** (Error relativo: {summary_metrics.get('little_rel_error_L')})")
    lines.append(f"- $L_q \\approx \\lambda \\cdot W_q$: **{summary_metrics.get('little_Lq_lambdaWq_ok')}** (Error relativo: {summary_metrics.get('little_rel_error_Lq')})")
    lines.append("")

    lines.append("## Información de Corrida")
    lines.append("")
    lines.append(f"- Clientes procesados: **{summary_metrics.get('n_customers')}**")
    lines.append(f"- Tiempo de simulación (h): **{summary_metrics.get('sim_time_hours')}**")
    lines.append(f"- Carpeta de datos: `{cfg.get('run_data_dir', '')}`")
    lines.append(f"- Carpeta de resultados: `{cfg.get('run_results_dir', '')}`")
    lines.append("")


    if extra_lines:
        lines.append("")
        lines.extend(extra_lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
