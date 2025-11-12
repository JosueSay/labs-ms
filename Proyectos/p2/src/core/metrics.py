from statistics import mean

def safeDiv(num, den):
    if den is None or den == 0:
        return None
    return num / den

def meanOrNone(seq):
    if not seq:
        return None
    return mean(seq)

def computeTheoretical(lambda_rate, mu_rate):
    # métricas teóricas M/M/1
    rho = lambda_rate / mu_rate
    if rho >= 1:
        return {
            "rho_theory": rho,
            "L_theory": None,
            "Lq_theory": None,
            "W_theory": None,
            "Wq_theory": None,
        }
    L = rho / (1.0 - rho)
    Lq = (rho ** 2) / (1.0 - rho)
    W = 1.0 / (mu_rate - lambda_rate)
    Wq = lambda_rate / (mu_rate * (mu_rate - lambda_rate))
    return {
        "rho_theory": rho,
        "L_theory": L,
        "Lq_theory": Lq,
        "W_theory": W,
        "Wq_theory": Wq,
    }

def timeWeightedAverage(series, start_time, end_time, value_key, time_key="timestamp_sim"):
    # promedio ponderado por tiempo
    if not series or start_time is None or end_time is None or end_time <= start_time:
        return None
    
    # ordenar por tiempo y recortar al intervalo [start_time, end_time]
    s = sorted(series, key=lambda r: r[time_key])
    
    # si la primera muestra es posterior al inicio, extrapolamos con su primer valor desde start_time
    acc = 0.0
    last_t = start_time
    last_v = s[0].get(value_key, None)
    if last_v is None:
        return None
    
    # integrar entre muestras
    for row in s:
        t = row.get(time_key, None)
        v = row.get(value_key, None)
        if t is None or v is None:
            return None
        if t < start_time:
            last_v = v
            continue
        if t > end_time:
            break
        dt = t - last_t
        if dt > 0:
            acc += last_v * dt
            last_t = t
            last_v = v
        else:
            last_v = v
    # integrar hasta end_time con el último valor
    tail_dt = end_time - last_t
    if tail_dt > 0:
        acc += last_v * tail_dt
    total = end_time - start_time
    return acc / total if total > 0 else None

def aggregateSimulation(sim_result, lambda_rate, mu_rate):
    queue_times = sim_result.get("queue_times", [])
    qlen_series = sim_result.get("queue_length_series", [])
    rho_series = sim_result.get("server_utilization_series", [])
    rho_avg = sim_result.get("rho_avg", None)
    start_time = sim_result.get("start_time", None)
    end_time = sim_result.get("end_time", None)
    sim_time_hours = (end_time - start_time) if (start_time is not None and end_time is not None) else None

    # tiempos por cliente
    waits = [row["wait_time"] for row in queue_times if row.get("wait_time") is not None]
    services = [row["service_time"] for row in queue_times if row.get("service_time") is not None]
    systems = [row["system_time"] for row in queue_times if row.get("system_time") is not None]

    W_sim = meanOrNone(systems)
    Wq_sim = meanOrNone(waits)
    S_sim = meanOrNone(services)

    # tasa de llegada observada
    n_customers = len(queue_times)
    lambda_obs = safeDiv(n_customers, sim_time_hours) if sim_time_hours is not None else None

    # Lq_sim desde serie temporal
    Lq_sim = timeWeightedAverage(qlen_series, start_time, end_time, value_key="Lq")

    if rho_avg is not None:
        rho_sim = rho_avg
    else:
        rho_sim = timeWeightedAverage(rho_series, start_time, end_time, value_key="rho_instant")

    L_sim = None
    if Lq_sim is not None and rho_sim is not None:
        L_sim = Lq_sim + rho_sim
    elif lambda_obs is not None and W_sim is not None:
        L_sim = lambda_obs * W_sim

    # revision Little usando λ observado
    little_L_est = safeDiv(L_sim, lambda_obs) if (L_sim is not None and lambda_obs) else None
    little_Lq_est = safeDiv(Lq_sim, lambda_obs) if (Lq_sim is not None and lambda_obs) else None
    rel_err_L = abs(little_L_est - W_sim) / abs(W_sim) if (little_L_est is not None and W_sim not in (None, 0)) else None
    rel_err_Lq = abs(little_Lq_est - Wq_sim) / abs(Wq_sim) if (little_Lq_est is not None and Wq_sim not in (None, 0)) else None

    return {
        "W_sim": W_sim,
        "Wq_sim": Wq_sim,
        "service_time_sim": S_sim,
        "Lq_sim": Lq_sim,
        "L_sim": L_sim,
        "rho_sim": rho_sim,
        "lambda_obs": lambda_obs,
        "sim_time_hours": sim_time_hours,
        "n_customers": n_customers,
        "little_L_est": little_L_est,
        "little_Lq_est": little_Lq_est,
        "little_rel_error_L": rel_err_L,
        "little_rel_error_Lq": rel_err_Lq,
    }

def buildSummaryMetrics(cfg, sim_result):
    # arma dict listo para CSV combinando teoria (con λ de config) y simulación (con λ observado)
    lambda_rate = float(cfg["model"]["lambda"])
    mu_rate = float(cfg["model"]["mu"])
    run_id = cfg.get("run_id")

    theo = computeTheoretical(lambda_rate, mu_rate)
    sim = aggregateSimulation(sim_result, lambda_rate, mu_rate)

    summary = {
        "run_id": run_id,
        "lambda_cfg": lambda_rate,
        "lambda_obs": sim["lambda_obs"],
        "mu": mu_rate,

        "rho_theory": theo["rho_theory"],
        "rho_sim": sim["rho_sim"],

        "L_theory": theo["L_theory"],
        "L_sim": sim["L_sim"],

        "Lq_theory": theo["Lq_theory"],
        "Lq_sim": sim["Lq_sim"],

        "W_theory": theo["W_theory"],
        "W_sim": sim["W_sim"],

        "Wq_theory": theo["Wq_theory"],
        "Wq_sim": sim["Wq_sim"],

        "service_time_sim": sim["service_time_sim"],
        "n_customers": sim["n_customers"],
        "sim_time_hours": sim["sim_time_hours"],

        "little_L_est": sim["little_L_est"],
        "little_Lq_est": sim["little_Lq_est"],
        "little_rel_error_L": sim["little_rel_error_L"],
        "little_rel_error_Lq": sim["little_rel_error_Lq"],
    }
    
    summary["replications"] = int(cfg["simulation"]["replications"])
    return summary
