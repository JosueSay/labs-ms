import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap
from matplotlib.animation import PillowWriter
import time

# Parámetros (variables)
M = 60           # altura del grid
N = 60           # anchura del grid
I0 = 5           # número inicial de infectados
T = 500          # tiempo total de simulación
r = 1            # radio de vecindad (Moore)
beta = 0.3       # tasa de infección
gamma = 0.05     # tasa de recuperación
SEED = 42        # semilla para reproducibilidad

np.random.seed(SEED)

# Estados
SUS = 0
INF = 1
REC = 2

def init_grid(M, N, I0):
    grid = np.zeros((M, N), dtype=np.int8)
    idx = np.random.choice(M * N, size=I0, replace=False)
    grid.flat[idx] = INF
    return grid

def moore_infected_neighbors(grid, r=1):
    """Cuenta infectados en vecindad Moore de radio r (sin periodicidad)."""
    M, N = grid.shape
    inf = (grid == INF).astype(np.int16)
    acc = np.zeros_like(inf)
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            if dx == 0 and dy == 0:
                continue
            # shift with zero padding (no periodic)
            shifted = np.zeros_like(inf)
            sx0 = max(0, dx); sx1 = M + min(0, dx)
            tx0 = max(0, -dx); tx1 = M - max(0, dx)
            sy0 = max(0, dy); sy1 = N + min(0, dy)
            ty0 = max(0, -dy); ty1 = N - max(0, dy)
            shifted[tx0:tx1, ty0:ty1] = inf[sx0:sx1, sy0:sy1]
            acc += shifted
    return acc

def step(grid, beta, gamma, r=1):
    M, N = grid.shape
    new = grid.copy()
    inf_neigh = moore_infected_neighbors(grid, r=r)

    # Susceptibles: si tienen al menos 1 vecino infectado -> prob beta de infectarse
    sus_mask = (grid == SUS) & (inf_neigh > 0)
    rand = np.random.rand(M, N)
    infect = sus_mask & (rand < beta)
    new[infect] = INF

    # Infectados: se recuperan con prob gamma
    inf_mask = (grid == INF)
    rand2 = np.random.rand(M, N)
    recover = inf_mask & (rand2 < gamma)
    new[recover] = REC

    return new

def run_simulation(M, N, I0, T, r, beta, gamma):
    grid = init_grid(M, N, I0)
    grids = [grid.copy()]
    S_hist = [int((grid == SUS).sum())]
    I_hist = [int((grid == INF).sum())]
    R_hist = [int((grid == REC).sum())]

    for t in range(1, T+1):
        grid = step(grid, beta, gamma, r=r)
        grids.append(grid.copy())
        S_hist.append(int((grid == SUS).sum()))
        I_hist.append(int((grid == INF).sum()))
        R_hist.append(int((grid == REC).sum()))
        # early stop if no infectados
        if I_hist[-1] == 0:
            # pad to length T+1 for consistent animation
            for _ in range(t+1, T+1):
                grids.append(grid.copy())
                S_hist.append(S_hist[-1])
                I_hist.append(0)
                R_hist.append(R_hist[-1])
            break
    # ensure lengths
    if len(S_hist) < T+1:
        last_grid = grids[-1].copy()
        while len(S_hist) < T+1:
            grids.append(last_grid.copy())
            S_hist.append(S_hist[-1])
            I_hist.append(I_hist[-1])
            R_hist.append(R_hist[-1])
    return grids, np.array(S_hist), np.array(I_hist), np.array(R_hist)

# ejecutar simulación
start = time.time()
grids, S_hist, I_hist, R_hist = run_simulation(M, N, I0, T, r, beta, gamma)
print(f"Simulación completada en {time.time()-start:.2f}s")

# Colormap: 0->azul, 1->rojo, 2->verde
cmap = ListedColormap(['#3778bf', '#d62728', '#2ca02c'])

# Preparar figura con dos paneles
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 7))

im = ax_left.imshow(grids[0], cmap=cmap, vmin=0, vmax=2, interpolation='nearest')
ax_left.set_title(f"t = 0 | S = {S_hist[0]} | I = {I_hist[0]} | R = {R_hist[0]}")
ax_left.axis('off')

t_vals = np.arange(0, T+1)
lnS, = ax_right.plot([], [], color='green', lw=2, label='S(t)')
lnI, = ax_right.plot([], [], color='red', lw=2, label='I(t)')
lnR, = ax_right.plot([], [], color='blue', lw=2, label='R(t)')
ax_right.set_xlim(0, T)
ax_right.set_ylim(0, M*N)
ax_right.set_xlabel('Paso de tiempo')
ax_right.set_ylabel('Número de individuos')
ax_right.set_title('Evolución S(t), I(t), R(t)')
ax_right.legend(loc='upper right')
ax_right.grid(alpha=0.3)

# snapshot condition requested
snapshot_t = 193
snapshot_counts = (16, 852, 2732)
snapshot_saved = False

def init():
    im.set_data(grids[0])
    ax_left.set_title(f"t = 0 | S = {S_hist[0]} | I = {I_hist[0]} | R = {R_hist[0]}")
    lnS.set_data([], [])
    lnI.set_data([], [])
    lnR.set_data([], [])
    return im, lnS, lnI, lnR

def update(k):
    global snapshot_saved
    im.set_data(grids[k])
    ax_left.set_title(f"t = {k} | S = {S_hist[k]} | I = {I_hist[k]} | R = {R_hist[k]}")
    lnS.set_data(t_vals[:k+1], S_hist[:k+1])
    lnI.set_data(t_vals[:k+1], I_hist[:k+1])
    lnR.set_data(t_vals[:k+1], R_hist[:k+1])

    # guardar PNG si se cumple la condición exacta y aún no se guardó
    if (not snapshot_saved) and k == snapshot_t:
        if (S_hist[k], I_hist[k], R_hist[k]) == snapshot_counts:
            fname = f"snapshot_t{snapshot_t}_S{snapshot_counts[0]}_I{snapshot_counts[1]}_R{snapshot_counts[2]}.png"
            plt.savefig(fname, dpi=200)
            print(f"Snapshot guardado en {fname}")
            snapshot_saved = True
        else:
            print(f"En t={k} no coincide con los counts solicitados: S={S_hist[k]} I={I_hist[k]} R={R_hist[k]}")
    return im, lnS, lnI, lnR

anim = animation.FuncAnimation(fig, update, frames=T+1, init_func=init, interval=80, blit=False)

# Guardar animación .gif
out_gif = "simulacion_SIR.gif"
try:
    writer = PillowWriter(fps=12)
    anim.save(out_gif, writer=writer)
    print(f"Animación guardada en {out_gif}")
except Exception as e:
    print("Error guardando GIF:", e)

plt.tight_layout()
plt.show()
