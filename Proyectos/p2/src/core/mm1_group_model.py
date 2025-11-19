from core.customer_group_record import CustomerGroupRecord
from core.mm1_model import MM1Model

class MM1GroupModel(MM1Model):
    """
    Modelo M/M/1 extendido para manejar GRUPOS de 1–5 personas.
    Importante:
    - NO modifica MM1Model.
    - Usa el mismo loop de simulación y las mismas series que el modelo original.
    """

    def processArrival(self):
        """
        Llega un nuevo grupo:
        - Se genera un customer_id normal (representa al grupo).
        - Se sortea un tamaño de grupo (1–5 personas).
        - Se decide si se atiende directo o se va a la cola.
        - Se agenda la siguiente llegada.
        """
        # ID normal del "cliente" (grupo)
        cust_id = self.nextCustomerId()

        # Tamaño del grupo: entero entre 1 y 5
        group_size = int(self.rng.integers(1, 6))

        # Registro extendido con group_size
        self.customers[cust_id] = CustomerGroupRecord(
            customer_id=cust_id,
            t_arrival=self.sim_time,
            group_size=group_size
        )

        # Evento de llegada
        self.logEvent("arrival", cust_id)

        # Lógica de cola igual que el modelo original
        if self.server_state == "idle" and not self.queue:
            # Servidor libre, atiende inmediatamente
            self.startServiceImmediateGroup(cust_id)
        else:
            # Se va a la cola en FIFO
            self.queue.append(cust_id)

        # Programar siguiente llegada (igual que en MM1Model)
        self.next_arrival_time = self.sim_time + self.sampleInterarrival()

    def startServiceImmediateGroup(self, cust_id):
        """
        Inicia el servicio para un grupo:
        - Calcula un tiempo de servicio base ~ Exp(1/μ).
        - Lo multiplica por el tamaño del grupo.
        - Actualiza estado del servidor y agenda la salida.
        """
        rec = self.customers[cust_id]

        # Tiempo de servicio base (para 1 persona)
        base_service = self.sampleService()

        # Escalar por el tamaño del grupo
        service_time = base_service * rec.group_size

        rec.t_start_service = self.sim_time

        # Igual que en el modelo original
        self.updateBusyAccumulator(self.sim_time)
        self.server_state = "busy"
        self.next_departure_time = self.sim_time + service_time

        # Registrar inicio de servicio
        self.logEvent("service_start", cust_id)

    # processDeparture sigue igual al padre
