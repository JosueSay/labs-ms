import os
import yaml
import pandas as pd
from utils.fs import ensureDir

def saveEffectiveConfig(cfg):
    # guarda la config efectiva en data/runs_*/config_effective.yaml
    if not cfg.get("outputs"):
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
    if not cfg.get("outputs"):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "raw_events.csv")
    cols = ["timestamp_sim", "event_type", "customer_id", "queue_length_after", "server_state"]
    return writeCsv(raw_events, out_path, columns=cols)

def saveQueueTimes(cfg, queue_times):
    # guarda tiempos por cliente
    if not cfg.get("outputs"):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "queue_times.csv")
    cols = ["customer_id", "t_arrival", "t_start_service", "t_end_service", "wait_time", "service_time", "system_time"]
    return writeCsv(queue_times, out_path, columns=cols)

def saveQueueLengthSeries(cfg, queue_length_series):
    # guarda serie Lq(t)
    if not cfg.get("outputs"):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "queue_length_series.csv")
    cols = ["timestamp_sim", "Lq"]
    return writeCsv(queue_length_series, out_path, columns=cols)

def saveServerUtilizationSeries(cfg, server_utilization_series):
    # guarda serie rho(t)
    if not cfg.get("outputs"):
        return None
    out_path = os.path.join(cfg["run_data_dir"], "server_utilization.csv")
    cols = ["timestamp_sim", "rho_instant"]
    return writeCsv(server_utilization_series, out_path, columns=cols)

def saveSummaryMetrics(cfg, summary_metrics):
    # guarda métricas agregadas en csv (append-friendly)
    if not cfg.get("outputs"):
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
    if not cfg.get("outputs"):
        return None
    results_dir = cfg["run_results_dir"]
    ensureDir(results_dir)
    out_path = os.path.join(results_dir, "report_resumen.md")

    # helpers cortos para formatear
    def fmt(x, nd=6):
        return "None" if x is None else (f"{x:.{nd}f}" if isinstance(x, (int, float)) else str(x))

    lines = []
    lines.append(f"# Resumen de Simulación — {cfg.get('run_id')}")
    lines.append("")

    # parámetros
    lines.append("## Parámetros")
    lines.append("")
    lines.append(f"- $\\lambda$ (Lambda, config): **{fmt(summary_metrics.get('lambda_cfg'), 6)}**")
    lines.append(f"- $\\lambda_\\text{{obs}}$ (Lambda observado): **{fmt(summary_metrics.get('lambda_obs'), 6)}**")
    lines.append(f"- $\\mu$ (Mu): **{fmt(summary_metrics.get('mu'), 6)}**")
    if "replications" in summary_metrics:
        lines.append(f"- Réplicas configuradas: **{summary_metrics.get('replications')}**")
    lines.append("")

    # teoría vs simulación
    lines.append("## Teoría vs Simulación")
    lines.append("")
    lines.append(f"- $\\rho_{{\\text{{teoría}}}}$: **{fmt(summary_metrics.get('rho_theory'), 6)}** | "
                 f"$\\rho_{{\\text{{sim}}}}$: **{fmt(summary_metrics.get('rho_sim'), 6)}**")
    lines.append(f"- $L_{{\\text{{teoría}}}}$: **{fmt(summary_metrics.get('L_theory'), 6)}** | "
                 f"$L_{{\\text{{sim}}}}$: **{fmt(summary_metrics.get('L_sim'), 6)}**")
    lines.append(f"- $L_q^{{\\text{{teoría}}}}$: **{fmt(summary_metrics.get('Lq_theory'), 6)}** | "
                 f"$L_q^{{\\text{{sim}}}}$: **{fmt(summary_metrics.get('Lq_sim'), 6)}**")
    lines.append(f"- $W_{{\\text{{teoría}}}}$: **{fmt(summary_metrics.get('W_theory'), 6)}** | "
                 f"$W_{{\\text{{sim}}}}$: **{fmt(summary_metrics.get('W_sim'), 6)}**")
    lines.append(f"- $W_q^{{\\text{{teoría}}}}$: **{fmt(summary_metrics.get('Wq_theory'), 6)}** | "
                 f"$W_q^{{\\text{{sim}}}}$: **{fmt(summary_metrics.get('Wq_sim'), 6)}**")
    lines.append("")

    # ley de little usando λ observado (lo que realmente calculamos)
    lines.append("## Ley de Little (Chequeo con $\\lambda_\\text{obs}$)")
    lines.append("")
    lines.append(f"- Estimación $L / \\lambda_\\text{{obs}}$: **{fmt(summary_metrics.get('little_L_est'), 6)}** "
                 f"(Error relativo vs $W$: {fmt(summary_metrics.get('little_rel_error_L'), 6)})")
    lines.append(f"- Estimación $L_q / \\lambda_\\text{{obs}}$: **{fmt(summary_metrics.get('little_Lq_est'), 6)}** "
                 f"(Error relativo vs $W_q$: {fmt(summary_metrics.get('little_rel_error_Lq'), 6)})")
    lines.append("")

    # info de corrida
    lines.append("## Información de Corrida")
    lines.append("")
    lines.append(f"- Clientes procesados: **{summary_metrics.get('n_customers')}**")
    lines.append(f"- Tiempo de simulación (h): **{fmt(summary_metrics.get('sim_time_hours'), 6)}**")
    lines.append(f"- Carpeta de datos: `{cfg.get('run_data_dir')}`")
    lines.append(f"- Carpeta de resultados: `{cfg.get('run_results_dir')}`")
    lines.append("")

    if extra_lines:
        lines.append("")
        lines.extend(extra_lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
