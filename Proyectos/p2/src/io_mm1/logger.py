import logging
from logging import FileHandler, Formatter
from rich.logging import RichHandler

def getLogger(name, log_path, level=logging.INFO):
    # crea un logger con salida a consola (rich) y a archivo
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # evitar handlers duplicados si se llama más de una vez
    if not logger.handlers:
        console_handler = RichHandler(rich_tracebacks=False, markup=True, show_time=True, show_level=True)
        console_fmt = Formatter("%(message)s")
        console_handler.setFormatter(console_fmt)
        logger.addHandler(console_handler)

        # archivo plano
        file_handler = FileHandler(log_path, encoding="utf-8")
        file_fmt = Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

        logger.propagate = False

    return logger

def logStartRun(logger, cfg):
    project = cfg.get("project")
    model = cfg.get("model")
    simulation = cfg.get("simulation",)

    logger.info("Iniciando corrida:")
    logger.info(f"\tRun ID: {cfg.get('run_id')}")
    logger.info("\tProyecto:")
    logger.info(f"\t\tSeed: {project.get('seed')}")
    logger.info("\tSimulación:")
    logger.info(f"\t\tModo: {simulation.get('mode')}")
    logger.info("\tModelo:")
    logger.info(f"\t\tLambda: {model.get('lambda')}")
    logger.info(f"\t\tMu: {model.get('mu')}")
    logger.info("\tDirectorios:")
    logger.info(f"\t\tDatos: {cfg.get('run_data_dir')}")
    logger.info(f"\t\tResultados: {cfg.get('run_results_dir')}")