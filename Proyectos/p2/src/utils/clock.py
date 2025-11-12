import time

class SimClock:
    def __init__(self, start_time=0.0, wall_clock_speed=1.0, record_interval_seconds=10):
        self.sim_time = start_time                          # tiempo simulación actual
        self.wall_clock_speed = wall_clock_speed            # velocidad respecto al tiempo (1 = tiempo real)
        self.record_interval = record_interval_seconds      # intervalo entre registros de métricas
        self.last_record_time = start_time                  # ultimo tiempo registrado (para guardar)
        self.real_start = time.time()                       # ref reloj en tiempo real para modo realtime

    def advance(self, delta):
        # avanza el tiempo simulado en delta (horas o minutos según modelo)
        self.sim_time += delta
        return self.sim_time

    def shouldRecord(self):
        # devuelve True si se alcanzó el siguiente punto de muestreo
        if self.sim_time - self.last_record_time >= self.record_interval:
            self.last_record_time = self.sim_time
            return True
        return False

    def resetRecordTimer(self):
        # reinicia el contador de muestreo
        self.last_record_time = self.sim_time

    def sleepRealtime(self, sim_delta_seconds):
        # pausa el tiempo real según el factor de velocidad
        if self.wall_clock_speed <= 0:
            return
        sleep_time = sim_delta_seconds / self.wall_clock_speed
        if sleep_time > 0:
            time.sleep(sleep_time)

    def elapsedRealtime(self):
        # tiempo real transcurrido desde inicio
        return time.time() - self.real_start

    def getSimTime(self):
        # retorna tiempo simulado actual
        return self.sim_time
