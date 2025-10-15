#!/usr/bin/env python3
"""
sim1.py

Simulación 1: SIR con partículas móviles
Ejecutar exactamente:
    python sim1.py --config config.yaml

Genera EXCLUSIVAMENTE un GIF (imageio) y un PNG con las curvas SIR.
"""

import sys
import os
import argparse
import math
import io
from collections import defaultdict

import yaml
import numpy as np
import imageio
import matplotlib.pyplot as plt

# ---------------------------
# Helpers: config validation
# ---------------------------
def error_exit(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def require_key(d, key_path):
    """Retrieve nested key, error if missing."""
    cur = d
    for k in key_path:
        if not isinstance(cur, dict) or k not in cur:
            error_exit(f"Falta clave obligatoria en config.yaml: {'.'.join(key_path)}")
        cur = cur[k]
    return cur

def check_type_and_range(name, val, expected_type, min_val=None, strict_gt=False, allowed_values=None):
    if expected_type == int:
        if not isinstance(val, int):
            error_exit(f"Clave '{name}' debe ser int, encontrado: {type(val).__name__}")
    elif expected_type == float:
        if not isinstance(val, (int, float)):
            error_exit(f"Clave '{name}' debe ser float, encontrado: {type(val).__name__}")
        val = float(val)
    elif expected_type == str:
        if not isinstance(val, str):
            error_exit(f"Clave '{name}' debe ser string, encontrado: {type(val).__name__}")
    # range checks
    if allowed_values is not None:
        if val not in allowed_values:
            error_exit(f"Clave '{name}' debe ser uno de {allowed_values}, encontrado: {val}")
    if min_val is not None:
        if strict_gt:
            if not (val > min_val):
                error_exit(f"Clave '{name}' debe ser > {min_val}, encontrado: {val}")
        else:
            if not (val >= min_val):
                error_exit(f"Clave '{name}' debe ser >= {min_val}, encontrado: {val}")

# ---------------------------
# Spatial hashing neighbor search
# ---------------------------
def build_cell_index(positions, cell_size, L):
    ix = np.floor(positions[:,0] / cell_size).astype(int)
    iy = np.floor(positions[:,1] / cell_size).astype(int)
    max_idx = max(0, int(math.floor(L / cell_size)))
    ix = np.clip(ix, 0, max_idx)
    iy = np.clip(iy, 0, max_idx)
    cells = defaultdict(list)
    for idx, (i,j) in enumerate(zip(ix,iy)):
        cells[(i,j)].append(idx)
    for k in list(cells.keys()):
        cells[k] = np.array(cells[k], dtype=int)
    return cells, ix, iy

def neighbors_of_cell(cell):
    i,j = cell
    for di in (-1,0,1):
        for dj in (-1,0,1):
            yield (i+di, j+dj)

# ---------------------------
# Main simulation
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Simulación 1: SIR con partículas móviles")
    parser.add_argument("--config", required=True, help="Archivo de configuración YAML (obligatorio)")
    args = parser.parse_args()

    cfg_path = args.config
    if not os.path.isfile(cfg_path):
        error_exit(f"Archivo de configuración no encontrado: {cfg_path}")

    print(f"[INFO] Leyendo configuración: {cfg_path}")

    # Load YAML
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        error_exit(f"No se pudo leer {cfg_path}: {e}")

    # Validate top-level seed
    if not isinstance(cfg, dict):
        error_exit("config.yaml debe contener un mapping en su nivel superior.")
    if "seed" not in cfg:
        error_exit("Falta clave obligatoria 'seed' en config.yaml")
    seed = cfg["seed"]
    check_type_and_range("seed", seed, int, min_val=0)  # seed must be int (>=0)

    # Validate sim1 section
    if "sim1" not in cfg:
        error_exit("Falta sección obligatoria 'sim1' en config.yaml")
    sim = cfg["sim1"]
    if not isinstance(sim, dict):
        error_exit("La sección 'sim1' debe ser un mapping en config.yaml")

    # Required keys list with expected types and constraints
    required_keys = {
        "L": (float, 0.0, True),
        "N_total": (int, 1, False),
        "I0": (int, 1, False),
        "vmax": (float, 0.0, True),
        "r": (float, 0.0, True),
        "beta": (float, 0.0, False),
        "gamma": (float, 0.0, False),
        "dt": (float, 0.0, True),
        "steps": (int, 1, False),
        "fps": (int, 1, False),
        "boundary": (str, None, False),
        "out_gif": (str, None, False),
        "curves_png": (str, None, False)
    }

    # Extract and validate
    values = {}
    for k, (typ, minv, strict_gt) in required_keys.items():
        if k not in sim:
            error_exit(f"Falta clave obligatoria 'sim1.{k}' en config.yaml")
        v = sim[k]
        if typ is int:
            if not isinstance(v, int):
                error_exit(f"Clave 'sim1.{k}' debe ser int, encontrado: {type(v).__name__}")
        elif typ is float:
            if not isinstance(v, (int, float)):
                error_exit(f"Clave 'sim1.{k}' debe ser float, encontrado: {type(v).__name__}")
            v = float(v)
        elif typ is str:
            if not isinstance(v, str):
                error_exit(f"Clave 'sim1.{k}' debe ser string, encontrado: {type(v).__name__}")
        if minv is not None:
            if strict_gt:
                if not (v > minv):
                    error_exit(f"Clave 'sim1.{k}' debe ser > {minv}, encontrado: {v}")
            else:
                if not (v >= minv):
                    error_exit(f"Clave 'sim1.{k}' debe ser >= {minv}, encontrado: {v}")
        values[k] = v

    # additional validations
    L = float(values["L"])
    N_total = int(values["N_total"])
    I0 = int(values["I0"])
    vmax = float(values["vmax"])
    r = float(values["r"])
    beta = float(values["beta"])
    gamma = float(values["gamma"])
    dt = float(values["dt"])
    steps = int(values["steps"])
    fps = int(values["fps"])
    boundary = values["boundary"]
    out_gif = values["out_gif"]
    curves_png = values["curves_png"]

    if not (1 <= I0 < N_total):
        error_exit(f"'sim1.I0' debe cumplir 1 <= I0 < N_total. Encontrado I0={I0}, N_total={N_total}")

    if boundary not in ("reflect", "wrap"):
        error_exit("Clave 'sim1.boundary' debe ser exactamente 'reflect' o 'wrap'")

    # Create output directories
    for path in (out_gif, curves_png):
        d = os.path.dirname(path)
        if d != "":
            os.makedirs(d, exist_ok=True)

    # Setup RNG
    rng = np.random.default_rng(seed)
    print("[INFO] Parámetros cargados:")
    print(f"       seed={seed}, L={L}, N_total={N_total}, I0={I0}, vmax={vmax}, r={r}")
    print(f"       beta={beta}, gamma={gamma}, dt={dt}, steps={steps}, fps={fps}, boundary={boundary}")
    print(f"       out_gif='{out_gif}', curves_png='{curves_png}'")

    # Initialize particle states and positions
    N = N_total
    positions = rng.random((N,2)) * L
    angles = rng.random(N) * 2 * np.pi
    speeds = rng.random(N) * vmax
    velocities = np.vstack((np.cos(angles)*speeds, np.sin(angles)*speeds)).T

    states = np.zeros(N, dtype=np.int8)
    infected_idx = rng.choice(N, size=I0, replace=False)
    states[infected_idx] = 1

    p_inf = 1.0 - math.exp(-beta * dt)
    p_rec = 1.0 - math.exp(-gamma * dt)
    print(f"[INFO] Probabilidades por paso: p_inf={p_inf:.4f}, p_rec={p_rec:.4f}")

    # Prepare recording arrays
    S_hist, I_hist, R_hist, times = [], [], [], []

    # Matplotlib figure setup
    fig, (ax_scatter, ax_curves) = plt.subplots(1,2, figsize=(12,5))
    plt.tight_layout()

    # Colores: scatter (S azul, I rojo, R verde) / curvas (S verde, I rojo, R azul)
    color_S = "blue"
    color_I = "red"
    color_R = "green"
    scatter_colors_map = {0: color_R, 1: color_I, 2: color_S}
    line_colors_map = {"S": "green", "I": "red", "R": "blue"}

    frames = []
    cell_size = r

    print("[INFO] Iniciando simulación...")
    log_every = max(1, steps // 10)

    for step in range(steps):
        t = step * dt

        # ---- Record current counts ----
        S_count = int(np.sum(states == 0))
        I_count = int(np.sum(states == 1))
        R_count = int(np.sum(states == 2))
        S_hist.append(S_count); I_hist.append(I_count); R_hist.append(R_count)
        times.append(t)

        if step % log_every == 0 or step == steps-1:
            print(f"[STEP {step:>4}/{steps}] t={t:.1f} | S={S_count} I={I_count} R={R_count}")

        # ---- Render current frame ----
        ax_scatter.clear(); ax_curves.clear()

        ax_scatter.set_xlim(0.0, L); ax_scatter.set_ylim(0.0, L)
        ax_scatter.set_aspect('equal', adjustable='box')
        for st, lbl in ((0,"S"), (1,"I"), (2,"R")):
            idxs = np.where(states == st)[0]
            if idxs.size > 0:
                ax_scatter.scatter(positions[idxs,0], positions[idxs,1],
                                   s=20, c=scatter_colors_map[st], label=lbl)
        ax_scatter.legend(loc='upper right')
        ax_scatter.set_title(f"t = {t:.1f} | S = {S_count} | I = {I_count} | R = {R_count}")

        ax_curves.plot(times, S_hist, label="S", color=line_colors_map["S"])
        ax_curves.plot(times, I_hist, label="I", color=line_colors_map["I"])
        ax_curves.plot(times, R_hist, label="R", color=line_colors_map["R"])
        ax_curves.set_title("Evolución SIR")
        ax_curves.set_xlabel("Tiempo")
        ax_curves.set_ylabel("Número de individuos")
        ax_curves.set_ylim(0, N_total)
        ax_curves.legend()

        buf = io.BytesIO()
        fig.canvas.draw()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = imageio.v2.imread(buf)
        frames.append(img)
        buf.close()

        # ---- Dynamics update (synchronous) ----
        positions = positions + velocities * dt

        if boundary == "wrap":
            positions = np.mod(positions, L)
        else:
            mask_x_low = positions[:,0] < 0.0
            if np.any(mask_x_low):
                positions[mask_x_low,0] = -positions[mask_x_low,0]
                velocities[mask_x_low,0] = -velocities[mask_x_low,0]
            mask_x_high = positions[:,0] > L
            if np.any(mask_x_high):
                positions[mask_x_high,0] = 2*L - positions[mask_x_high,0]
                velocities[mask_x_high,0] = -velocities[mask_x_high,0]
            mask_y_low = positions[:,1] < 0.0
            if np.any(mask_y_low):
                positions[mask_y_low,1] = -positions[mask_y_low,1]
                velocities[mask_y_low,1] = -velocities[mask_y_low,1]
            mask_y_high = positions[:,1] > L
            if np.any(mask_y_high):
                positions[mask_y_high,1] = 2*L - positions[mask_y_high,1]
                velocities[mask_y_high,1] = -velocities[mask_y_high,1]

        infected_indices = np.where(states == 1)[0]
        if infected_indices.size > 0:
            rec_rand = rng.random(size=infected_indices.size)
            recover_mask = rec_rand < p_rec
            to_recover = infected_indices[recover_mask]
        else:
            to_recover = np.array([], dtype=int)

        susceptible_indices = np.where(states == 0)[0]
        to_infect_set = set()

        if susceptible_indices.size > 0 and infected_indices.size > 0:
            cells, ix_arr, iy_arr = build_cell_index(positions, cell_size, L)

            infected_cells = {}
            for (ci,cj), idx_list in cells.items():
                if idx_list.size == 0:
                    continue
                inter = np.intersect1d(idx_list, infected_indices, assume_unique=False)
                if inter.size > 0:
                    infected_cells[(ci,cj)] = inter

            susceptible_cells = {}
            for (ci,cj), idx_list in cells.items():
                inter_s = np.intersect1d(idx_list, susceptible_indices, assume_unique=False)
                if inter_s.size > 0:
                    susceptible_cells[(ci,cj)] = inter_s

            for cell, sus_idxs in susceptible_cells.items():
                cand_inf = []
                for ncell in neighbors_of_cell(cell):
                    if ncell in infected_cells:
                        cand_inf.append(infected_cells[ncell])
                if not cand_inf:
                    continue
                cand_inf = np.concatenate(cand_inf)
                sus_pos = positions[sus_idxs]
                inf_pos = positions[cand_inf]
                Ns = sus_pos.shape[0]
                CHUNK = 200
                for start in range(0, Ns, CHUNK):
                    end = min(Ns, start+CHUNK)
                    block = sus_pos[start:end][:, None, :] - inf_pos[None, :, :]
                    d2 = (block**2).sum(axis=2)
                    close_any = np.any(d2 < (r*r), axis=1)
                    if np.any(close_any):
                        sus_indices_block = sus_idxs[start:end][close_any]
                        probs = rng.random(sus_indices_block.size)
                        newly = sus_indices_block[probs < p_inf]
                        for ni in newly:
                            to_infect_set.add(int(ni))

        if len(to_infect_set) > 0:
            to_infect = np.array(sorted(to_infect_set), dtype=int)
            to_infect = to_infect[states[to_infect] == 0]
            states[to_infect] = 1
        if to_recover.size > 0:
            to_recover = to_recover[states[to_recover] == 1]
            states[to_recover] = 2

    # --- End loop ---

    print(f"[INFO] Guardando curvas en: {curves_png}")
    fig2, ax2 = plt.subplots(figsize=(8,5))
    ax2.plot(np.array(times), np.array(S_hist), label="S", color=line_colors_map["S"])
    ax2.plot(np.array(times), np.array(I_hist), label="I", color=line_colors_map["I"])
    ax2.plot(np.array(times), np.array(R_hist), label="R", color=line_colors_map["R"])
    ax2.set_title("Evolución SIR")
    ax2.set_xlabel("Tiempo")
    ax2.set_ylabel("Número de individuos")
    ax2.set_ylim(0, N_total)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(curves_png, dpi=150)
    plt.close(fig2)

    if len(frames) == 0:
        error_exit("No se generaron frames para el GIF.")

    print(f"[INFO] Escribiendo GIF en: {out_gif} (fps={fps})")
    imageio.mimsave(out_gif, frames, fps=fps)

    plt.close(fig)
    print("[OK] Simulación completada.")
    print(f"[RESUMEN] Último paso: t={times[-1]:.1f} | S={S_hist[-1]} I={I_hist[-1]} R={R_hist[-1]}")

if __name__ == "__main__":
    main()
