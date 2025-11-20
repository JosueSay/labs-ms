import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================
# CONFIGURACIÓN
# ============================

# Ruta base: .../Proyectos/p2/src
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Runs elegidos
DATA_BASE   = os.path.join(BASE_PATH, "../data/runs_20251119_193649")   # default
DATA_GROUPS = os.path.join(BASE_PATH, "../data/runs_20251119_193933")   # restaurant

# Carpeta donde guardaremos las figuras
OUTPUT_DIR = os.path.join(BASE_PATH, "../results/analysis_compare")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Archivos necesarios
FILE_TIMES = "queue_times.csv"

def load_csv(path_folder, filename):
    path = os.path.join(path_folder, filename)
    return pd.read_csv(path)


# ============================
# 1. CARGAR DATOS
# ============================
classic_times = load_csv(DATA_BASE, FILE_TIMES)
group_times   = load_csv(DATA_GROUPS, FILE_TIMES)


# ============================
# 2. HISTOGRAMA — TIEMPO EN SISTEMA (W)
# ============================

plt.figure(figsize=(10,5))
plt.hist(classic_times["system_time"], bins=20, alpha=0.5, label="Clásico (default)")
plt.hist(group_times["system_time"], bins=20, alpha=0.5, label="Con grupos (restaurant)")
plt.title("Histograma de Tiempos en Sistema (W)")
plt.xlabel("Horas")
plt.ylabel("Frecuencia")
plt.legend()

plt.savefig(os.path.join(OUTPUT_DIR, "hist_W_system.png"), dpi=200)
plt.show()


# ============================
# 3. HISTOGRAMA — TIEMPOS DE ESPERA (Wq)
# ============================

plt.figure(figsize=(10,5))
plt.hist(classic_times["wait_time"], bins=20, alpha=0.5, label="Clásico (default)")
plt.hist(group_times["wait_time"], bins=20, alpha=0.5, label="Con grupos (restaurant)")
plt.title("Histograma de Tiempos de Espera (Wq)")
plt.xlabel("Horas")
plt.ylabel("Frecuencia")
plt.legend()

plt.savefig(os.path.join(OUTPUT_DIR, "hist_Wq_wait.png"), dpi=200)
plt.show()


print("\nHistogramas generados en:")
print(OUTPUT_DIR)
