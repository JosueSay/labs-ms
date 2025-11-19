import time

from core.mm1_model import MM1Model
from utils.rng import getRng


class SimulationController:
    def __init__(self, model_cfg, model_params, sim_cfg, rng_seed=None):
        # guardado de config para reset
        self.model_cfg = dict(model_cfg)
        self.model_params = dict(model_params)
        self.sim_cfg = dict(sim_cfg)

        # rng
        self.rng_seed = rng_seed if rng_seed is not None else self.sim_cfg.get("seed", None)
        self.rng = getRng(self.rng_seed)

        # estado de simulación
        self.model = None
        self.end_time = None          # en horas de simulación (absoluto)
        self.warmup_minutes = float(self.sim_cfg.get("warmup_minutes", 0.0))
        self.record_interval_seconds = float(self.sim_cfg.get("record_interval_seconds", 10.0))

        # control de tiempo real
        self.speed = 1800.0
        self.paused = True
        self.ended = False
        self.last_wall_time = None

        # crear modelo inicial
        self.resetSimulation()

    def createModel(self):
        # crea el modelo mm1
        self.model = MM1Model(self.model_cfg, self.model_params, self.rng)

    def computeDefaultEndTime(self):
        # calcula tiempo de fin absoluto en horas de simulación
        sim_hours = float(self.sim_cfg.get("sim_time_hours", 4.0))
        return self.model.sim_time + sim_hours

    def resetSimulation(self, new_seed=None):
        # reinicia simulación completa
        if new_seed is not None:
            self.rng_seed = int(new_seed)
        self.rng = getRng(self.rng_seed)

        self.createModel()
        self.end_time = self.computeDefaultEndTime()

        self.paused = True
        self.ended = False
        self.last_wall_time = None

    def startSimulation(self):
        # empieza la simulación usando el fin por defecto
        if self.model is None:
            self.createModel()
            self.end_time = self.computeDefaultEndTime()
        self.paused = False
        self.ended = False
        self.last_wall_time = time.time()

    def pauseSimulation(self):
        # pausa la simulación
        self.paused = True

    def resumeSimulation(self):
        # reanuda la simulación
        if not self.ended:
            self.paused = False
            self.last_wall_time = time.time()

    def setSpeed(self, speed):
        # ajusta factor de velocidad
        if speed is None:
            return
        if speed <= 0:
            speed = 0.0
        self.speed = float(speed)

    def setEndTimeHours(self, sim_time_hours):
        # cambia la duración total de la simulación a partir del t actual
        if sim_time_hours is None:
            return
        sim_time_hours = float(sim_time_hours)
        self.end_time = self.model.sim_time + sim_time_hours
        self.ended = False

    def updateParams(self, lambda_rate=None, mu_rate=None):
        # actualiza parámetros de llegada y servicio para futuros eventos
        if lambda_rate is not None:
            lambda_rate = float(lambda_rate)
            self.model_cfg["lambda"] = lambda_rate
            self.model.lambda_rate = lambda_rate
        if mu_rate is not None:
            mu_rate = float(mu_rate)
            self.model_cfg["mu"] = mu_rate
            self.model.mu_rate = mu_rate

    def tick(self, collect_series=True):
        # avanza usando tiempo real
        if self.model is None:
            self.createModel()
            self.end_time = self.computeDefaultEndTime()

        # si está pausado o ya terminó solo devolvemos snapshot
        if self.paused or self.ended or self.speed <= 0:
            return self.getSnapshot(include_series=False)

        now = time.time()
        if self.last_wall_time is None:
            self.last_wall_time = now
            return self.getSnapshot(include_series=False)

        real_dt = now - self.last_wall_time
        self.last_wall_time = now

        if real_dt <= 0:
            return self.getSnapshot(include_series=False)

        # tiempo sim a avanzar en horas
        sim_delta_h = (real_dt * self.speed) / 3600.0
        if sim_delta_h <= 0:
            return self.getSnapshot(include_series=False)

        target_time = self.model.sim_time + sim_delta_h

        # no pasar del fin
        if self.end_time is not None:
            if target_time >= self.end_time:
                target_time = self.end_time
                self.ended = True

        self.model.simulateUntil(
            end_time=target_time,
            warmup_minutes=self.warmup_minutes,
            record_interval_seconds=self.record_interval_seconds,
            collect_series=collect_series,
        )

        # si justo llegamos al fin marcamos ended
        if self.end_time is not None and self.model.sim_time >= self.end_time:
            self.ended = True

        return self.getSnapshot(include_series=False)

    def tickWithDelta(self, sim_delta_hours, collect_series=True):
        # avanza un delta fijo de tiempo simulado (para pygame o control manual)
        if self.model is None:
            self.createModel()
            self.end_time = self.computeDefaultEndTime()

        if self.ended:
            return self.getSnapshot(include_series=False)

        sim_delta_hours = float(sim_delta_hours)
        if sim_delta_hours <= 0:
            return self.getSnapshot(include_series=False)

        target_time = self.model.sim_time + sim_delta_hours

        if self.end_time is not None:
            if target_time >= self.end_time:
                target_time = self.end_time
                self.ended = True

        self.model.simulateUntil(
            end_time=target_time,
            warmup_minutes=self.warmup_minutes,
            record_interval_seconds=self.record_interval_seconds,
            collect_series=collect_series,
        )

        if self.end_time is not None and self.model.sim_time >= self.end_time:
            self.ended = True

        return self.getSnapshot(include_series=False)

    def getSnapshot(self, include_series=False, max_points=500):
        # arma snapshot de alto nivel para ui
        model_state = self.model.getStateSnapshot() if self.model is not None else {}

        snapshot = {
            "paused": self.paused,
            "ended": self.ended,
            "speed": self.speed,
            "rng_seed": self.rng_seed,
            "end_time": self.end_time,
            "model_state": model_state,
        }

        if include_series and self.model is not None:
            if max_points is None or max_points <= 0:
                q_series = list(self.model.series_queue_len)
                rho_series = list(self.model.series_utilization)
            else:
                q_series = self.model.series_queue_len[-max_points:]
                rho_series = self.model.series_utilization[-max_points:]
            snapshot["queue_length_series"] = q_series
            snapshot["server_utilization_series"] = rho_series

        return snapshot
