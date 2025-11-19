from dataclasses import dataclass


@dataclass
class CustomerRecord:
    customer_id: int
    t_arrival: float
    t_start_service: float = None
    t_end_service: float = None


class MM1Model:
    def __init__(self, model_cfg, model_params, rng):
        # parametros modelo
        self.lambda_rate = float(model_cfg["lambda"])
        self.mu_rate = float(model_cfg["mu"])
        self.queue_discipline = model_cfg["queue_discipline"]
        self.capacity_infinite = bool(model_cfg["capacity_infinite"])
        self.patience_infinite = bool(model_cfg["patience_infinite"])

        # estado inicial
        self.initial_time = float(model_params["initial_time"])
        self.sim_time = self.initial_time
        self.queue = []  # guarda customer_id en orden FIFO
        self.server_state = model_params["server_initial_state"]
        self.remaining_service_if_busy = float(model_params["service_time_if_busy"]) / 60.0  # minutos -> horas

        # generador aleatorio
        self.rng = rng

        # próximos eventos
        self.next_arrival_time = self.sim_time + self.sampleInterarrival()
        self.next_departure_time = None
        if self.server_state == "busy":
            # validado: si inicia busy, service_time_if_busy > 0
            self.next_departure_time = self.sim_time + self.remaining_service_if_busy

        # contadores y registros
        self.customer_seq = 0
        self.customers = {}       # customer_id -> CustomerRecord
        self.raw_events = []      # filas: timestamp_sim, event_type, customer_id, queue_length_after, server_state
        self.queue_times = []     # filas por cliente

        # series temporales
        self.series_queue_len = []
        self.series_utilization = []

        # tracking de ocupación
        self.last_state_change_time = self.sim_time
        self.busy_time_accum = 0.0

        # control de muestreo para modo paso a paso / batch
        self.record_interval_h = None
        self.next_sample_time_h = None
        self.series_initialized = False

    def sampleInterarrival(self):
        # interarribo ~ exponencial(1/λ) en horas
        return self.rng.exponential(1.0 / self.lambda_rate)


    def sampleService(self):
        # servicio ~ exponencial(1/μ) en horas
        return self.rng.exponential(1.0 / self.mu_rate)


    def nextCustomerId(self):
        # genera id incremental
        self.customer_seq += 1
        return self.customer_seq


    def logEvent(self, event_type, customer_id=None):
        self.raw_events.append({
            "timestamp_sim": self.sim_time,
            "event_type": event_type,
            "customer_id": customer_id,
            "queue_length_after": len(self.queue),
            "server_state": self.server_state,
        })


    def updateBusyAccumulator(self, new_time):
        # acumula tiempo ocupado desde el último cambio de estado
        elapsed = new_time - self.last_state_change_time
        if elapsed > 0:
            if self.server_state == "busy":
                self.busy_time_accum += elapsed
            self.last_state_change_time = new_time


    def startServiceIfPossible(self):
        # si servidor idle y hay cola, iniciar servicio al siguiente
        if self.server_state == "idle" and self.queue:
            cust_id = self.queue.pop(0)
            rec = self.customers[cust_id]
            rec.t_start_service = self.sim_time
            service_time = self.sampleService()
            self.updateBusyAccumulator(self.sim_time)
            self.server_state = "busy"
            self.next_departure_time = self.sim_time + service_time
            self.logEvent("service_start", cust_id)


    def processArrival(self):
        # llega un cliente nuevo
        cust_id = self.nextCustomerId()
        self.customers[cust_id] = CustomerRecord(customer_id=cust_id, t_arrival=self.sim_time)
        self.logEvent("arrival", cust_id)

        # encola o atiende directo si servidor libre
        if self.server_state == "idle" and not self.queue:
            self.startServiceImmediate(cust_id)
        else:
            self.queue.append(cust_id)

        # agenda siguiente llegada
        self.next_arrival_time = self.sim_time + self.sampleInterarrival()


    def startServiceImmediate(self, cust_id):
        # iniciar servicio al cliente cust_id en el instante actual
        rec = self.customers[cust_id]
        rec.t_start_service = self.sim_time
        service_time = self.sampleService()
        self.updateBusyAccumulator(self.sim_time)
        self.server_state = "busy"
        self.next_departure_time = self.sim_time + service_time
        self.logEvent("service_start", cust_id)


    def processDeparture(self):
        # termina servicio del cliente actual
        cust_id = self.findCurrentInService()
        if cust_id is None:
            self.next_departure_time = None
            return

        rec = self.customers[cust_id]
        rec.t_end_service = self.sim_time
        self.logEvent("service_end", cust_id)

        # cerrar registro en queue_times
        self.queue_times.append({
            "customer_id": rec.customer_id,
            "t_arrival": rec.t_arrival,
            "t_start_service": rec.t_start_service,
            "t_end_service": rec.t_end_service,
            "wait_time": rec.t_start_service - rec.t_arrival,
            "service_time": rec.t_end_service - rec.t_start_service,
            "system_time": rec.t_end_service - rec.t_arrival,
        })

        # decidir si sigue ocupado con el siguiente o queda idle
        if self.queue:
            next_id = self.queue.pop(0)
            next_rec = self.customers[next_id]
            next_rec.t_start_service = self.sim_time
            service_time = self.sampleService()
            self.next_departure_time = self.sim_time + service_time
            self.logEvent("service_start", next_id)
        else:
            self.updateBusyAccumulator(self.sim_time)
            self.server_state = "idle"
            self.next_departure_time = None


    def findCurrentInService(self):
        # encuentra el cliente con start_service definido pero sin end_service, más reciente
        candidate = None
        last_start = -1.0
        for rec in self.customers.values():
            if rec.t_start_service is not None and rec.t_end_service is None:
                if rec.t_start_service > last_start:
                    last_start = rec.t_start_service
                    candidate = rec.customer_id
        return candidate


    def initRecording(self, record_interval_seconds, collect_series):
        # inicializa parámetros de muestreo si hace falta
        if not collect_series:
            return

        record_interval_h = max(1e-9, float(record_interval_seconds) / 3600.0)
        self.record_interval_h = record_interval_h

        if not self.series_initialized:
            self.series_queue_len.append({"timestamp_sim": self.sim_time, "Lq": len(self.queue)})
            rho_inst = 1.0 if self.server_state == "busy" else 0.0
            self.series_utilization.append({"timestamp_sim": self.sim_time, "rho_instant": rho_inst})
            self.next_sample_time_h = self.sim_time + self.record_interval_h
            self.series_initialized = True


    def sampleSeriesIfNeeded(self, collect_series):
        # si collect_series, guarda muestras Lq y rho cada record_interval_h
        if not collect_series:
            return
        if self.record_interval_h is None or not self.series_initialized:
            return

        while self.sim_time >= self.next_sample_time_h:
            rho_inst = 1.0 if self.server_state == "busy" else 0.0
            self.series_queue_len.append({"timestamp_sim": self.sim_time, "Lq": len(self.queue)})
            self.series_utilization.append({"timestamp_sim": self.sim_time, "rho_instant": rho_inst})
            self.next_sample_time_h += self.record_interval_h


    def getNextEvent(self):
        # devuelve (tipo, tiempo) del próximo evento o (None, None) si no hay
        candidates = []
        if self.next_arrival_time is not None:
            candidates.append(("arrival", self.next_arrival_time))
        if self.next_departure_time is not None:
            candidates.append(("departure", self.next_departure_time))
        if not candidates:
            return None, None
        return min(candidates, key=lambda x: x[1])


    def stepNextEvent(self, collect_series=True, record_interval_seconds=10):
        # procesa un solo evento (arrival/departure) y avanza el tiempo hasta ese evento
        # devuelve info básica del evento y estado, o None si no hay eventos
        if collect_series and self.record_interval_h is None:
            self.initRecording(record_interval_seconds, collect_series)

        event_type, event_time = self.getNextEvent()
        if event_type is None:
            return None

        # avanzar tiempo y acumular ocupación
        self.updateBusyAccumulator(event_time)
        self.sim_time = event_time

        # muestreo de series en el nuevo tiempo
        self.sampleSeriesIfNeeded(collect_series)

        # procesar evento
        if event_type == "arrival":
            self.processArrival()
        elif event_type == "departure":
            self.processDeparture()

        return {
            "event_type": event_type,
            "event_time": event_time,
            "state": self.getStateSnapshot(),
        }


    def simulateUntil(self, end_time, warmup_minutes=0, record_interval_seconds=10, collect_series=True):
        # avanza la simulación hasta end_time (en horas)
        warmup_h = max(0.0, float(warmup_minutes) / 60.0)
        run_start_time = self.sim_time
        busy_accum_before = self.busy_time_accum

        if collect_series:
            self.initRecording(record_interval_seconds, collect_series)

        keep_running = True

        while keep_running:
            event_type, event_time = self.getNextEvent()

            # no hay eventos o el siguiente evento excede el fin
            if event_type is None or event_time > end_time:
                self.updateBusyAccumulator(end_time)
                self.sim_time = end_time
                self.sampleSeriesIfNeeded(collect_series)
                keep_running = False
                continue

            # avanzar al tiempo del evento
            self.updateBusyAccumulator(event_time)
            self.sim_time = event_time

            # muestreo de series
            self.sampleSeriesIfNeeded(collect_series)

            # procesar evento
            if event_type == "arrival":
                self.processArrival()
            elif event_type == "departure":
                self.processDeparture()

            # el bucle continúa hasta que encontremos un break natural arriba

        # calcular rho promedio en el intervalo de la corrida
        total_duration = max(1e-12, self.sim_time - run_start_time)
        busy_during_run = max(0.0, self.busy_time_accum - busy_accum_before)
        rho_avg = min(1.0, max(0.0, busy_during_run / total_duration))

        result = {
            "raw_events": self.raw_events,
            "queue_times": self.queue_times,
            "queue_length_series": self.series_queue_len,
            "server_utilization_series": self.series_utilization,
            "rho_avg": rho_avg,
            "start_time": run_start_time,
            "end_time": self.sim_time,
            "warmup_hours": warmup_h,
        }
        return result


    def getStateSnapshot(self):
        # devuelve un snapshot ligero del estado actual
        queue_length = len(self.queue)
        completed = len(self.queue_times)
        if self.sim_time > self.initial_time:
            rho_avg = self.busy_time_accum / max(1e-12, self.sim_time - self.initial_time)
        else:
            rho_avg = None

        return {
            "sim_time": self.sim_time,
            "queue_length": queue_length,
            "server_state": self.server_state,
            "next_arrival_time": self.next_arrival_time,
            "next_departure_time": self.next_departure_time,
            "n_customers_created": self.customer_seq,
            "n_customers_completed": completed,
            "rho_avg_so_far": rho_avg,
        }


    def run(self, sim_time_hours, warmup_minutes=0, record_interval_seconds=10, collect_series=True):
        # wrapper batch clásico que mantiene la api original
        end_time = self.sim_time + float(sim_time_hours)
        return self.simulateUntil(
            end_time=end_time,
            warmup_minutes=warmup_minutes,
            record_interval_seconds=record_interval_seconds,
            collect_series=collect_series,
        )
