import numpy as np

def getRng(seed=None):
    # crea un generador numpy con semilla fija o aleatoria
    if seed is None:
        seed = np.random.SeedSequence().entropy
    return np.random.default_rng(int(seed))

def exp(rng, rate):
    # genera un número aleatorio exponencial con tasa dada (1/μ o 1/λ)
    if rate <= 0:
        raise ValueError(f"rate debe ser > 0, recibido: {rate}")
    return rng.exponential(1.0 / rate)

def poissonArrivals(rng, rate, sim_time):
    # genera lista de tiempos de llegada (Poisson) hasta sim_time (en horas)
    if rate <= 0 or sim_time <= 0:
        raise ValueError("rate y sim_time deben ser > 0")

    arrivals = []
    current_time = 0.0
    while True:
        # intervalo entre llegadas ~ exponencial(1/λ)
        current_time += rng.exponential(1.0 / rate)
        if current_time > sim_time:
            break
        arrivals.append(current_time)
    return arrivals
