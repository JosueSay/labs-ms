import os
import yaml
from datetime import datetime
from utils.fs import ensureDirs, getTimestamp

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
        "server_initial_state": "idle",
        "service_time_if_busy": 0.0,
    },
    "simulation": {
        "mode": "batch",
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
    "dashboard": {
        "enable_gif": True,
        "gif_fps": 10,
        "gif_max_seconds": 60,
    },
    "outputs": True,
}


def readYaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deepMerge(base, override):
    result = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deepMerge(result[k], v)
        else:
            result[k] = v
    return result


def buildRunDirs(cfg):
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


def assertKeys(section_name, cfg_section, required, allowed, errors, strict=True):
    present = set((cfg_section or {}).keys())
    req = set(required)
    allow = set(allowed)
    missing = req - present
    if missing:
        errors.append(f"{section_name}: faltan claves requeridas: {sorted(list(missing))}")
    if strict:
        unknown = present - (req | allow)
        if unknown:
            errors.append(f"{section_name}: claves desconocidas: {sorted(list(unknown))}")


def assertType(path, value, expected_type, errors):
    if not isinstance(value, expected_type):
        errors.append(
            f"{path}: tipo inválido, se esperaba {expected_type.__name__}, recibido {type(value).__name__}"
        )


def assertNumber(path, value, positive=None, non_negative=None, errors=None):
    if not isinstance(value, (int, float)):
        errors.append(f"{path}: debe ser número")
        return
    if positive is True and not (value > 0):
        errors.append(f"{path}: debe ser > 0 (recibido {value})")
    if non_negative is True and not (value >= 0):
        errors.append(f"{path}: debe ser ≥ 0 (recibido {value})")


def assertInSet(path, value, allowed, errors):
    if value not in allowed:
        errors.append(f"{path}: valor inválido '{value}', permitidos: {sorted(list(allowed))}")


def validateConfig(cfg):
    errors = []

    # root  ← AQUI AGREGO "dashboard"
    assertKeys(
        "root",
        cfg,
        required=["project", "model", "model_params", "simulation", "realtime", "dashboard", "outputs"],
        allowed=[],
        errors=errors,
        strict=True,
    )

    # project
    project = cfg.get("project", {})
    assertKeys(
        "project",
        project,
        required=["output_base_data", "output_base_results", "make_run_dir", "timestamp_fmt", "seed"],
        allowed=["name"],
        errors=errors,
        strict=True,
    )
    assertType("project.output_base_data", project.get("output_base_data"), str, errors)
    assertType("project.output_base_results", project.get("output_base_results"), str, errors)
    assertType("project.make_run_dir", project.get("make_run_dir"), bool, errors)
    assertType("project.timestamp_fmt", project.get("timestamp_fmt"), str, errors)
    assertNumber("project.seed", project.get("seed"), errors=errors)

    # model
    model = cfg.get("model", {})
    assertKeys(
        "model",
        model,
        required=["type", "lambda", "mu", "queue_discipline", "capacity_infinite", "patience_infinite"],
        allowed=[],
        errors=errors,
        strict=True,
    )
    assertType("model.type", model.get("type"), str, errors)
    assertInSet("model.type", model.get("type"), {"MM1"}, errors)
    assertNumber("model.lambda", model.get("lambda"), positive=True, errors=errors)
    assertNumber("model.mu", model.get("mu"), positive=True, errors=errors)
    if isinstance(model.get("lambda"), (int, float)) and isinstance(model.get("mu"), (int, float)):
        if model["lambda"] >= model["mu"]:
            errors.append(
                f"model: para estabilidad se requiere lambda < mu (λ={model['lambda']}, μ={model['mu']})"
            )
    assertType("model.queue_discipline", model.get("queue_discipline"), str, errors)
    assertInSet("model.queue_discipline", model.get("queue_discipline"), {"FIFO"}, errors)
    assertType("model.capacity_infinite", model.get("capacity_infinite"), bool, errors)
    assertType("model.patience_infinite", model.get("patience_infinite"), bool, errors)

    # model_params
    params = cfg.get("model_params", {})
    assertKeys(
        "model_params",
        params,
        required=["initial_time", "initial_queue", "server_initial_state", "service_time_if_busy"],
        allowed=[],
        errors=errors,
        strict=True,
    )
    assertNumber("model_params.initial_time", params.get("initial_time"), non_negative=True, errors=errors)
    if not isinstance(params.get("initial_queue"), int) or params.get("initial_queue") < 0:
        errors.append("model_params.initial_queue: debe ser entero ≥ 0")
    assertInSet("model_params.server_initial_state", params.get("server_initial_state"), {"idle", "busy"}, errors)
    assertNumber(
        "model_params.service_time_if_busy",
        params.get("service_time_if_busy"),
        non_negative=True,
        errors=errors,
    )
    if params.get("server_initial_state") == "busy" and params.get("service_time_if_busy", 0) == 0:
        errors.append("model_params: server_initial_state='busy' requiere service_time_if_busy > 0 (minutos)")

    # simulation
    sim = cfg.get("simulation", {})
    assertKeys(
        "simulation",
        sim,
        required=["mode", "sim_time_hours", "warmup_minutes", "record_interval_seconds", "replications"],
        allowed=[],
        errors=errors,
        strict=True,
    )
    assertInSet("simulation.mode", sim.get("mode"), {"batch", "realtime"}, errors)
    assertNumber("simulation.sim_time_hours", sim.get("sim_time_hours"), positive=True, errors=errors)
    assertNumber("simulation.warmup_minutes", sim.get("warmup_minutes"), non_negative=True, errors=errors)
    assertNumber(
        "simulation.record_interval_seconds",
        sim.get("record_interval_seconds"),
        positive=True,
        errors=errors,
    )
    if not isinstance(sim.get("replications"), int) or sim.get("replications") < 1:
        errors.append("simulation.replications: debe ser entero ≥ 1")

    # realtime
    rt = cfg.get("realtime", {})
    assertKeys(
        "realtime",
        rt,
        required=["wall_clock_speed", "draw_interval_ms", "max_points"],
        allowed=[],
        errors=errors,
        strict=True,
    )
    assertNumber("realtime.wall_clock_speed", rt.get("wall_clock_speed"), non_negative=True, errors=errors)
    if not isinstance(rt.get("draw_interval_ms"), int) or rt.get("draw_interval_ms") <= 0:
        errors.append("realtime.draw_interval_ms: debe ser entero > 0")
    if not isinstance(rt.get("max_points"), int) or rt.get("max_points") <= 0:
        errors.append("realtime.max_points: debe ser entero > 0")

    # dashboard
    dash = cfg.get("dashboard", {})
    assertKeys(
        "dashboard",
        dash,
        required=["enable_gif", "gif_fps", "gif_max_seconds"],
        allowed=[],
        errors=errors,
        strict=True,
    )
    assertType("dashboard.enable_gif", dash.get("enable_gif"), bool, errors)
    assertNumber("dashboard.gif_fps", dash.get("gif_fps"), positive=True, errors=errors)
    assertNumber("dashboard.gif_max_seconds", dash.get("gif_max_seconds"), positive=True, errors=errors)

    # outputs
    if "outputs" not in cfg:
        errors.append("root: falta 'outputs' (booleano)")
    else:
        if not isinstance(cfg.get("outputs"), bool):
            errors.append(
                f"outputs: debe ser booleano (true/false), recibido {type(cfg.get('outputs')).__name__}"
            )

    # validar timestamp_fmt
    try:
        _ = datetime.now().strftime(project.get("timestamp_fmt", "%Y%m%d_%H%M%S"))
    except Exception as ex:
        errors.append(f"project.timestamp_fmt: formato inválido para strftime: {ex}")

    if errors:
        msg = "errores de configuración:\n- " + "\n- ".join(errors)
        raise ValueError(msg)


def loadConfig(config_path):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"no se encontró el archivo de configuración: {config_path}")

    user_cfg = readYaml(config_path)
    cfg = deepMerge(DEFAULT_CFG, user_cfg)
    validateConfig(cfg)

    run_id, run_data_dir, run_results_dir = buildRunDirs(cfg)
    ensureDirs([cfg["project"]["output_base_data"], cfg["project"]["output_base_results"]])
    ensureDirs([run_data_dir, run_results_dir, os.path.join(run_results_dir, "figures")])

    cfg["run_id"] = run_id
    cfg["run_data_dir"] = run_data_dir
    cfg["run_results_dir"] = run_results_dir
    cfg["run_log_path"] = os.path.join(run_data_dir, "run.log")

    return cfg
