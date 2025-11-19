import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================
# CONFIGURACIÓN DE RUTAS
# ============================

BASE_PATH = os.path.dirname(os.path.dirname(__file__))  # .../p2/src
DATA_CLASSIC = os.path.join(BASE_PATH, "../data/runs_20251118_233031")
DATA_GROUPS = "results/runs_20251119_000058"


OUTPUT_DIR = os.path.join(BASE_PATH, "../results/analysis_compare")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Archivos necesarios
FILE_LQ = "queue_length_series.csv"
FILE_TIMES = "queue_times.csv"
FILE_RHO = "server_utilization.csv"


def load_csv(folder, filename):
    path = os.path.join(folder, filename)
    return pd.read_csv(path)


# ============================
# 1. CARGAR DATOS
# ============================

classic_lq = load_csv(DATA_CLASSIC, FILE_LQ)
classic_times = load_csv(DATA_CLASSIC, FILE_TIMES)
classic_rho = load_csv(DATA_CLASSIC, FILE_RHO)

group_lq = load_csv(DATA_GROUPS, FILE_LQ)
group_times = load_csv(DATA_GROUPS, FILE_TIMES)
group_rho = load_csv(DATA_GROUPS, FILE_RHO)


# ============================
# 2. GRAFICA COMPARATIVA DE COLA Lq(t)
# ============================

plt.figure(figsize=(10,5))
plt.plot(classic_lq["timestamp_sim"], classic_lq["Lq"], alpha=0.7, label="M/M/1 clásico")
plt.plot(group_lq["timestamp_sim"], group_lq["Lq"], alpha=0.7, label="M/M/1 con grupos")
plt.title("Comparación de Lq(t) entre modelos")
plt.xlabel("Tiempo sim (h)")
plt.ylabel("Longitud de cola Lq")
plt.legend()

out_path = os.path.join(OUTPUT_DIR, "compare_Lq.png")
plt.savefig(out_path, dpi=200)
plt.show()


# ============================
# 3. HISTOGRAMA DE TIEMPOS EN SISTEMA
# ============================

plt.figure(figsize=(10,5))
plt.hist(classic_times["system_time"], bins=20, alpha=0.5, label="Clásico")
plt.hist(group_times["system_time"], bins=20, alpha=0.5, label="Grupos")
plt.title("Histograma tiempos en sistema (W)")
plt.xlabel("Horas")
plt.ylabel("Frecuencia")
plt.legend()

out_path = os.path.join(OUTPUT_DIR, "hist_W_system.png")
plt.savefig(out_path, dpi=200)
plt.show()


# ============================
# 4. HISTOGRAMA DE TIEMPOS DE ESPERA
# ============================

plt.figure(figsize=(10,5))
plt.hist(classic_times["wait_time"], bins=20, alpha=0.5, label="Clásico")
plt.hist(group_times["wait_time"], bins=20, alpha=0.5, label="Grupos")
plt.title("Histograma tiempos de espera (Wq)")
plt.xlabel("Horas")
plt.ylabel("Frecuencia")
plt.legend()

out_path = os.path.join(OUTPUT_DIR, "hist_Wq_wait.png")
plt.savefig(out_path, dpi=200)
plt.show()


# ============================
# 5. UTILIZACIÓN ρ(t) COMPARADA
# ============================

plt.figure(figsize=(10,5))
plt.plot(classic_rho["timestamp_sim"], classic_rho["rho_instant"], alpha=0.5, label="Clásico")
plt.plot(group_rho["timestamp_sim"], group_rho["rho_instant"], alpha=0.5, label="Grupos")
plt.title("Utilización del servidor ρ(t)")
plt.xlabel("Tiempo sim (h)")
plt.ylabel("ρ")
plt.legend()

out_path = os.path.join(OUTPUT_DIR, "compare_rho.png")
plt.savefig(out_path, dpi=200)
plt.show()

print("\nAnálisis comparativo completado. Figuras guardadas en:")
print(OUTPUT_DIR)
