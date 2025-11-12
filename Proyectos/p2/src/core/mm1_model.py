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
        self.sim_time = float(model_params["initial_time"])
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

    def sampleSeriesIfNeeded(self, next_sample_time_h, collect_series):
        # si collect_series, guarda Lq y rho al alcanzar el siguiente punto de muestreo
        if not collect_series:
            return False
        if self.sim_time >= next_sample_time_h:
            rho_inst = 1.0 if self.server_state == "busy" else 0.0
            self.series_queue_len.append({"timestamp_sim": self.sim_time, "Lq": len(self.queue)})
            self.series_utilization.append({"timestamp_sim": self.sim_time, "rho_instant": rho_inst})
            return True
        return False

    def run(self, sim_time_hours, warmup_minutes=0, record_interval_seconds=10, collect_series=True):
        # convierte intervalos a horas
        record_interval_h = max(1e-9, float(record_interval_seconds) / 3600.0)
        warmup_h = max(0.0, float(warmup_minutes) / 60.0)
        end_time = self.sim_time + float(sim_time_hours)

        # marcar tiempo de inicio para promedio de utilización
        run_start_time = self.sim_time

        # inicializa muestreo de series
        next_sample_time_h = self.sim_time

        # muestreo inicial (t0)
        if collect_series:
            self.series_queue_len.append({"timestamp_sim": self.sim_time, "Lq": len(self.queue)})
            rho_inst = 1.0 if self.server_state == "busy" else 0.0
            self.series_utilization.append({"timestamp_sim": self.sim_time, "rho_instant": rho_inst})
            next_sample_time_h += record_interval_h

        # bucle principal de eventos controlado por bandera
        keep_running = True
        while keep_running:
            # determinar próximo evento
            candidates = []
            if self.next_arrival_time is not None:
                candidates.append(("arrival", self.next_arrival_time))
            if self.next_departure_time is not None:
                candidates.append(("departure", self.next_departure_time))

            # si no hay eventos, cortar
            if not candidates:
                self.updateBusyAccumulator(end_time)
                self.sim_time = end_time
                while self.sampleSeriesIfNeeded(next_sample_time_h, collect_series):
                    next_sample_time_h += record_interval_h
                break

            event_type, event_time = min(candidates, key=lambda x: x[1])

            if event_time > end_time:
                # avanzar acumuladores hasta fin y salir
                self.updateBusyAccumulator(end_time)
                self.sim_time = end_time
                while self.sampleSeriesIfNeeded(next_sample_time_h, collect_series):
                    next_sample_time_h += record_interval_h
                break

            # avanzar tiempo y acumular ocupación
            self.updateBusyAccumulator(event_time)
            self.sim_time = event_time

            # muestreo de series si pasamos el umbral
            sampled = True
            while sampled:
                sampled = self.sampleSeriesIfNeeded(next_sample_time_h, collect_series)
                if sampled:
                    next_sample_time_h += record_interval_h

            # procesar evento
            if event_type == "arrival":
                self.processArrival()
            elif event_type == "departure":
                self.processDeparture()

            # condición de corte -> si ambos eventos están vacíos tras procesar y ya alcanzamos el final
            no_more_events = (self.next_arrival_time is None and self.next_departure_time is None)
            keep_running = not no_more_events

        # calcular rho promedio a partir de tiempo ocupado / duración total de simulación del run
        total_duration = max(1e-12, self.sim_time - run_start_time)
        rho_avg = min(1.0, max(0.0, self.busy_time_accum / total_duration))

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
