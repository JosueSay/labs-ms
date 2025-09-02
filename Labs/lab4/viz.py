from typing import List, Tuple
import os
import matplotlib.pyplot as plt
import imageio.v2 as imageio

def _plot_tour(coords: List[Tuple[float, float]], tour: List[int], title: str = ""):
    xs = [coords[i][0] for i in tour] + [coords[tour[0]][0]]
    ys = [coords[i][1] for i in tour] + [coords[tour[0]][1]]
    plt.plot(xs, ys, marker='o', linewidth=1)
    # etiquetar nodos
    for idx in tour:
        x, y = coords[idx]
        plt.text(x, y, str(idx), fontsize=7)
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis('equal')
    plt.tight_layout()

def saveFrame(coords: List[Tuple[float, float]], bestTour: List[int], history: List[int], outPath: str, title: str):
    """
    Guarda un frame PNG con:
      - Mapa del mejor tour actual.
      - Curva L_best^(t) en un segundo subplot.
    (Se usa cuando hay mejora: --record)
    """
    plt.figure(figsize=(10, 4))
    # izquierda: tour
    plt.subplot(1, 2, 1)
    _plot_tour(coords, bestTour, title=f"{title} – best={history[-1]}")

    # derecha: curva de mejor costo
    plt.subplot(1, 2, 2)
    plt.plot(range(len(history)), history, linewidth=1.5)
    plt.title("Evolución L_best^(t)")
    plt.xlabel("Generación")
    plt.ylabel("Mejor costo")
    plt.tight_layout()

    os.makedirs(os.path.dirname(outPath), exist_ok=True)
    plt.savefig(outPath, dpi=120)
    plt.close()

def makeGifFromFrames(framesDir: str, outPath: str, fps: int = 5):
    """
    Construye un GIF con los frames guardados en framesDir (ordenados por nombre).
    """
    files = sorted([f for f in os.listdir(framesDir) if f.lower().endswith(".png")])
    imgs = []
    for f in files:
        imgs.append(imageio.imread(os.path.join(framesDir, f)))
    imageio.mimsave(outPath, imgs, fps=fps)

def plotResults(coords: List[Tuple[float, float]], bestTour: List[int], history: List[int], title: str = ""):
    """
    MÓDULO L — SIEMPRE generar:
      (1) Mapa del tour final sobre (x, y).
      (2) Curva t -> L_best^(t).
    """
    plt.figure(figsize=(10, 4))

    # (1) Tour
    plt.subplot(1, 2, 1)
    _plot_tour(coords, bestTour, title=f"{title} – best={history[-1]}")

    # (2) Curva de mejor costo
    plt.subplot(1, 2, 2)
    plt.plot(range(len(history)), history, linewidth=1.5)
    plt.title("Evolución L_best^(t)")
    plt.xlabel("Generación")
    plt.ylabel("Mejor costo")

    plt.tight_layout()
    plt.show()
