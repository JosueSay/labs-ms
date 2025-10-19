import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap
from matplotlib.animation import PillowWriter
import time
import yaml
import os

# ===========================
# Lectura de configuración
# ===========================
config_path = os.path.join(os.path.dirname(__file__), "../config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)["sim2"]

M = config["M"]
N = config["N"]
I0 = config["I0"]
T = config["T"]
r = config["r"]
beta = config["beta"]
gamma = config["gamma"]
SEED = config["SEED"]
save_gif = config["save_gif"]
fps = config["fps"]
interval = config["interval"]

# rutas de salida (absolutas dentro de lab6)
base_dir = os.path.dirname(os.path.dirname(__file__))  # sube un nivel desde p2 a lab6
out_gif = os.path.join(base_dir, "images", "sim2", "sim2.gif")
curves_png = os.path.join(base_dir, "images", "sim2", "sim2_curvas.png")

np.random.seed(SEED)

# ===========================
# Definición de estados
# ===========================
SUS = 0
INF = 1
REC = 2

# ===========================
# Inicialización del grid
# ===========================
def init_grid(M, N, I0):
    grid = np.zeros((M, N), dtype=np.int8)
    idx = np.random.choice(M * N, size=I0, replace=False)
    grid.flat[idx] = INF
    return grid

# ===========================
# Vecindad de Moore
# ===========================
def moore_infected_neighbors(grid, r=1):
    M, N = grid.shape
    inf = (grid == INF).astype(np.int16)
    acc = np.zeros_like(inf)
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.zeros_like(inf)
            sx0 = max(0, dx)
            sx1 = M + min(0, dx)
            tx0 = max(0, -dx)
            tx1 = M - max(0, dx)
            sy0 = max(0, dy)
            sy1 = N + min(0, dy)
            ty0 = max(0, -dy)
            ty1 = N - max(0, dy)
            shifted[tx0:tx1, ty0:ty1] = inf[sx0:sx1, sy0:sy1]
            acc += shifted
    return acc

# ===========================
# Paso de simulación
# ===========================
def step(grid, beta, gamma, r=1):
    M, N = grid.shape
    new = grid.copy()
    inf_neigh = moore_infected_neighbors(grid, r=r)

    # P = beta × (VI / 8)
    sus_mask = (grid == SUS) & (inf_neigh > 0)
    rand = np.random.rand(M, N)
    P_local = beta * (inf_neigh / (8 * r))
    infect = sus_mask & (rand < P_local)
    new[infect] = INF

    inf_mask = (grid == INF)
    rand2 = np.random.rand(M, N)
    recover = inf_mask & (rand2 < gamma)
    new[recover] = REC

    return new

# ===========================
# Simulación completa
# ===========================
def run_simulation(M, N, I0, T, r, beta, gamma):
    grid = init_grid(M, N, I0)
    grids = [grid.copy()]
    S_hist = [int((grid == SUS).sum())]
    I_hist = [int((grid == INF).sum())]
    R_hist = [int((grid == REC).sum())]

    print(f"[STEP 0] | S={S_hist[0]} I={I_hist[0]} R={R_hist[0]}")

    for t in range(1, T + 1):
        grid = step(grid, beta, gamma, r=r)
        grids.append(grid.copy())
        S_hist.append(int((grid == SUS).sum()))
        I_hist.append(int((grid == INF).sum()))
        R_hist.append(int((grid == REC).sum()))

        print(f"[STEP {t}] | S={S_hist[-1]} I={I_hist[-1]} R={R_hist[-1]}")
        
        if I_hist[-1] == 0:
            for _ in range(t + 1, T + 1):
                grids.append(grid.copy())
                S_hist.append(S_hist[-1])
                I_hist.append(0)
                R_hist.append(R_hist[-1])
            break

    print(f"[RESUMEN] Último paso: S={S_hist[-1]} I={I_hist[-1]} R={R_hist[-1]}")

    return grids, np.array(S_hist), np.array(I_hist), np.array(R_hist)

# ===========================
# Ejecución
# ===========================
start = time.time()
grids, S_hist, I_hist, R_hist = run_simulation(M, N, I0, T, r, beta, gamma)
print(f"Simulación completada en {time.time()-start:.2f}s")

# ===========================
# Visualización
# ===========================
cmap = ListedColormap(['#3778bf', '#d62728', '#2ca02c'])
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 7))

im = ax_left.imshow(grids[0], cmap=cmap, vmin=0, vmax=2, interpolation='nearest')
ax_left.set_title(f"t = 0 | S = {S_hist[0]} | I = {I_hist[0]} | R = {R_hist[0]}")
ax_left.axis('off')

t_vals = np.arange(0, T + 1)
lnS, = ax_right.plot([], [], color='green', lw=2, label='S(t)')
lnI, = ax_right.plot([], [], color='red', lw=2, label='I(t)')
lnR, = ax_right.plot([], [], color='blue', lw=2, label='R(t)')
ax_right.set_xlim(0, T)
ax_right.set_ylim(0, M * N)
ax_right.set_xlabel('Paso de tiempo')
ax_right.set_ylabel('Número de individuos')
ax_right.set_title('Evolución S(t), I(t), R(t)')
ax_right.legend(loc='upper right')
ax_right.grid(alpha=0.3)

def init():
    im.set_data(grids[0])
    return im, lnS, lnI, lnR

def update(k):
    im.set_data(grids[k])
    ax_left.set_title(f"t = {k} | S = {S_hist[k]} | I = {I_hist[k]} | R = {R_hist[k]}")
    lnS.set_data(t_vals[:k+1], S_hist[:k+1])
    lnI.set_data(t_vals[:k+1], I_hist[:k+1])
    lnR.set_data(t_vals[:k+1], R_hist[:k+1])
    return im, lnS, lnI, lnR

# ===========================
# Guardado de resultados
# ===========================
os.makedirs(os.path.dirname(out_gif), exist_ok=True)
os.makedirs(os.path.dirname(curves_png), exist_ok=True)

anim = animation.FuncAnimation(fig, update, frames=T+1, init_func=init, interval=interval, blit=False)

if save_gif:
    try:
        writer = PillowWriter(fps=fps)
        anim.save(out_gif, writer=writer)
        print(f" Animación guardada en: {out_gif}")
    except Exception as e:
        print(" Error guardando GIF:", e)

plt.tight_layout()
plt.savefig(curves_png, dpi=200)
print(f" Gráfica guardada en: {curves_png}")

plt.show()
