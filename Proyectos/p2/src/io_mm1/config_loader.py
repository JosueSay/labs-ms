import os
import yaml
from datetime import datetime

# defaults razonables para el proyecto
DEFAULT_CFG = {
    "project": {
        "name": "mm1_restaurante",
        "seed": 12345,
        "output_base_data": "data",
        "output_base_results": "results",
        "make_run_dir": True,
        "timestamp_fmt": "%Y%m%d_%H%M%S",
    },
    "model": {
        "type": "MM1",
        "lambda": 10.0,
        "mu": 12.0,
        "queue_discipline": "FIFO",
        "capacity_infinite": True,
        "patience_infinite": True,
    },
    "model_params": {
        "initial_time": 0.0,
        "initial_queue": 0,
        "server_initial_state": "idle",   # "idle" | "busy"
        "service_time_if_busy": 0.0,      # minutos si inicia busy
    },
    "simulation": {
        "mode": "batch",                  # "batch" | "realtime"
        "sim_time_hours": 4.0,
        "warmup_minutes": 0,
        "record_interval_seconds": 10,
        "replications": 1,
    },
    "realtime": {
        "wall_clock_speed": 1.0,
        "draw_interval_ms": 100,
        "max_points": 500,
    },
    "outputs": True,
}

def readYaml(path):
    # lee yaml desde disco y retorna dict
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def deepMerge(base, override):
    # merge recursivo simple para dicts anidados
    result = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deepMerge(result[k], v)
        else:
            result[k] = v
    return result

def getTimestamp(fmt):
    # genera timestamp con formato del yaml
    return datetime.now().strftime(fmt)

def buildRunDirs(cfg):
    # arma rutas efectivas para data/results considerando make_run_dir
    project = cfg["project"]
    base_data = project["output_base_data"]
    base_results = project["output_base_results"]
    make_run_dir = project["make_run_dir"]
    ts_fmt = project["timestamp_fmt"]

    if make_run_dir:
        run_id = f"runs_{getTimestamp(ts_fmt)}"
        run_data_dir = os.path.join(base_data, run_id)
        run_results_dir = os.path.join(base_results, run_id)
    else:
        run_id = "runs_current"
        run_data_dir = base_data
        run_results_dir = base_results

    return run_id, run_data_dir, run_results_dir

def ensureDirs(paths):
    # crea carpetas si no existen
    for p in paths:
        os.makedirs(p, exist_ok=True)

def validateConfig(cfg):
    # validaciones clave del modelo y simulación
    model = cfg.get("model", {})
    simulation = cfg.get("simulation", {})
    model_type = model.get("type")
    lam = model.get("lambda")
    mu = model.get("mu")
    mode = simulation.get("mode")

    if model_type != "MM1":
        raise ValueError(f"model.type debe ser 'MM1', recibido: {model_type}")

    if not isinstance(lam, (int, float)) or lam <= 0:
        raise ValueError(f"model.lambda debe ser > 0, recibido: {lam}")

    if not isinstance(mu, (int, float)) or mu <= 0:
        raise ValueError(f"model.mu debe ser > 0, recibido: {mu}")

    if lam >= mu:
        raise ValueError(f"para estabilidad se requiere lambda < mu (recibido λ={lam}, μ={mu})")

    if mode not in {"batch", "realtime"}:
        raise ValueError(f"simulation.mode debe ser 'batch' o 'realtime', recibido: {mode}")

    # validación suave de server_initial_state
    sis = cfg.get("model_params", {}).get("server_initial_state", "idle")
    if sis not in {"idle", "busy"}:
        raise ValueError(f"model_params.server_initial_state debe ser 'idle' o 'busy', recibido: {sis}")

    # outputs booleano
    outputs = cfg.get("outputs", True)
    if not isinstance(outputs, bool):
        raise ValueError(f"outputs debe ser booleano, recibido: {outputs}")

def loadConfig(config_path):
    # carga yaml del usuario, fusiona con defaults, valida y prepara rutas
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"no se encontró el archivo de configuración: {config_path}")

    user_cfg = readYaml(config_path)
    cfg = deepMerge(DEFAULT_CFG, user_cfg)

    # validaciones antes de tocar disco
    validateConfig(cfg)

    # crear rutas efectivas de corrida
    run_id, run_data_dir, run_results_dir = buildRunDirs(cfg)
    ensureDirs([cfg["project"]["output_base_data"], cfg["project"]["output_base_results"]])
    ensureDirs([run_data_dir, run_results_dir, os.path.join(run_results_dir, "figures")])

    # enriquecer cfg con campos efectivos
    cfg["run_id"] = run_id
    cfg["run_data_dir"] = run_data_dir
    cfg["run_results_dir"] = run_results_dir

    # ruta de log por conveniencia
    cfg["run_log_path"] = os.path.join(run_data_dir, "run.log")

    # opcionalmente podríamos normalizar algunas unidades aquí si hiciera falta
    # por ejemplo, tiempos en segundos vs minutos, pero lo dejamos consistente con el yaml

    return cfg
