import argparse
import copy
from sim.plots import generateAllFigures
from io_mm1.config_loader import loadConfig
from io_mm1.logger import getLogger, logStartRun
from io_mm1.writers import (
    saveEffectiveConfig,
    saveRawEvents,
    saveQueueTimes,
    saveQueueLengthSeries,
    saveServerUtilizationSeries,
    saveSummaryMetrics,
    saveReportResumen,
)
from utils.rng import getRng
from core.mm1_model import MM1Model
from core.metrics import buildSummaryMetrics
from core.mm1_group_model import MM1GroupModel


def parseArgs():
    parser = argparse.ArgumentParser(description="Orquestador del simulador M/M/1")
    parser.add_argument("--config", required=True, help="Ruta a configs/*.yaml")
    parser.add_argument("--no-outputs", action="store_true", help="No guardar CSVs/figuras/reportes")
    return parser.parse_args()


def deriveReplicationCfg(cfg, rep_idx):
    cfg_rep = copy.deepcopy(cfg)
    base_run_id = cfg["run_id"]
    cfg_rep["run_id"] = f"{base_run_id}_rep{rep_idx}"
    cfg_rep["rep_prefix"] = f"rep{rep_idx}_"
    return cfg_rep

def buildModel(cfg, rng):
    """
    Selecciona el modelo a usar.
    - Si el YAML es restaurant_groups.yaml → usar MM1GroupModel
    - Si no → usar MM1 normal
    """

    # Detectar si el archivo de origen contiene la palabra 'group'
    source = cfg.get("source_config_path", "").lower()

    if "group" in source:
        return MM1GroupModel(cfg["model"], cfg["model_params"], rng)

    # Caso normal
    return MM1Model(cfg["model"], cfg["model_params"], rng)


def runReplication(cfg_rep, seed_offset):
    base_seed = int(cfg_rep["project"]["seed"])
    rng = getRng(base_seed + seed_offset)
    model = buildModel(cfg_rep, rng)


    sim_cfg = cfg_rep["simulation"]
    sim_result = model.run(
        sim_time_hours=sim_cfg["sim_time_hours"],
        warmup_minutes=sim_cfg["warmup_minutes"],
        record_interval_seconds=sim_cfg["record_interval_seconds"],
        collect_series=True,
    )

    summary = buildSummaryMetrics(cfg_rep, sim_result)
    return sim_result, summary


def saveAllOutputs(cfg_rep, sim_result, summary, logger):
    saveEffectiveConfig(cfg_rep)
    saveServerUtilizationSeries(cfg_rep, sim_result.get("server_utilization_series"))
    saveQueueLengthSeries(cfg_rep, sim_result.get("queue_length_series"))
    saveQueueTimes(cfg_rep, sim_result.get("queue_times"))
    saveRawEvents(cfg_rep, sim_result.get("raw_events"))
    saveSummaryMetrics(cfg_rep, summary)
    saveReportResumen(cfg_rep, summary)

    logger.info(f"CSV guardados en {cfg_rep['run_data_dir']}")
    logger.info(f"Reporte en {cfg_rep['run_results_dir']}/report_resumen.md")


def main():
    args = parseArgs()
    cfg = loadConfig(args.config)

    if args.no_outputs:
        cfg["outputs"] = False

    logger = getLogger("mm1", cfg["run_log_path"])
    logStartRun(logger, cfg)

    replications = int(cfg["simulation"]["replications"])
    summaries = []

    for rep_idx in range(1, replications + 1):
        logger.info(f"EJECUTANDO RÉPLICA {rep_idx}/{replications}...")
        cfg_rep = deriveReplicationCfg(cfg, rep_idx)
        sim_result, summary = runReplication(cfg_rep, seed_offset=rep_idx - 1)
        summaries.append(summary)

        if cfg.get("outputs", True):
            saveAllOutputs(cfg_rep, sim_result, summary, logger)

            # ---------------------------------------------
            # Generar todas las figuras de la simulación
            # ---------------------------------------------
            from sim.plots import generateAllFigures
            generateAllFigures(cfg_rep, show=False)



    logger.info(f"TOTAL DE RÉPLICAS EJECUTADAS: {replications}")
    logger.info("RESUMEN (ÚLTIMA RÉPLICA):")
    last = summaries[-1]

    logger.info("PARÁMETROS:")
    logger.info(f"\tλ (lambda): {last.get('lambda_cfg')}")
    logger.info(f"\tμ (mu): {last.get('mu')}")

    logger.info("RENDIMIENTO TEÓRICO VS SIMULADO:")
    logger.info(f"\tρ (theory): {last.get('rho_theory')}")
    logger.info(f"\tρ (sim): {last.get('rho_sim')}")
    logger.info(f"\tL (theory): {last.get('L_theory')}")
    logger.info(f"\tL (sim): {last.get('L_sim')}")
    logger.info(f"\tLq (theory): {last.get('Lq_theory')}")
    logger.info(f"\tLq (sim): {last.get('Lq_sim')}")
    logger.info(f"\tW (theory): {last.get('W_theory')}")
    logger.info(f"\tW (sim): {last.get('W_sim')}")
    logger.info(f"\tWq (theory): {last.get('Wq_theory')}")
    logger.info(f"\tWq (sim): {last.get('Wq_sim')}")

    logger.info("DATOS GENERALES:")
    logger.info(f"\tClientes simulados: {last.get('n_customers')}")
    logger.info(f"\tDuración (horas): {last.get('sim_time_hours')}")

    logger.info("VERIFICACIONES LEY DE LITTLE:")
    logger.info(f"\tL = λW: {last.get('little_rel_error_L')}")
    logger.info(f"\tLq = λWq: {last.get('little_rel_error_Lq')}")

    logger.info("FIN DE EJECUCIÓN")


if __name__ == "__main__":
    main()
