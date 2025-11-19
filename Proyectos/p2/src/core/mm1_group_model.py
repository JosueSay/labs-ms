from core.customer_group_record import CustomerGroupRecord

from core.mm1_model import MM1Model, CustomerRecord
import numpy as np

class MM1GroupModel(MM1Model):
    """
    Extensión del modelo M/M/1 para incluir grupos de 1–5 personas.
    NO modifica el comportamiento original del simulador.
    """

    def processArrival(self):
        # ID normal
        cust_id = self.nextCustomerId()

        # Tamaño del grupo (nueva característica)
        group_size = int(self.rng.integers(1, 6))

        # Crear registro extendido
        self.customers[cust_id] = CustomerGroupRecord(
            customer_id=cust_id,
            t_arrival=self.sim_time,
            group_size=group_size
        )

        self.logEvent("arrival", cust_id)

        # FIFO normal
        if self.server_state == "idle" and not self.queue:
            self.startServiceImmediateGroup(cust_id)
        else:
            self.queue.append(cust_id)

        # Siguiente llegada normal
        self.next_arrival_time = self.sim_time + self.sampleInterarrival()

    def startServiceImmediateGroup(self, cust_id):
        rec = self.customers[cust_id]

        # Tiempo base exponencial
        base = self.sampleService()

        # Ajuste proporcional al tamaño del grupo
        service_time = base * rec.group_size

        rec.t_start_service = self.sim_time

        self.updateBusyAccumulator(self.sim_time)
        self.server_state = "busy"
        self.next_departure_time = self.sim_time + service_time

        self.logEvent("service_start", cust_id)

    def processDeparture(self):
        # Igual al modelo original — solo llama al padre
        super().processDeparture()
