from typing import List, Tuple
import os
import matplotlib.pyplot as plt
import imageio.v2 as imageio

def saveFrame(coords: List[Tuple[float, float]], bestTour: List[int], history: List[int], outPath: str, title: str):
    xs = [coords[i][0] for i in bestTour] + [coords[bestTour[0]][0]]
    ys = [coords[i][1] for i in bestTour] + [coords[bestTour[0]][1]]

    plt.figure(figsize=(11,5))

    plt.subplot(1,2,1)
    plt.plot(xs, ys, marker="o")
    for idx, (x, y) in enumerate(coords):
        plt.text(x, y, str(idx+1), fontsize=6)
    plt.title(f"Mejor tour {title}")

    plt.subplot(1,2,2)
    plt.plot(history)
    plt.xlabel("Generación"); plt.ylabel("Distancia best-so-far")
    plt.title("Evolución del costo")

    plt.tight_layout()
    plt.savefig(outPath, dpi=120)
    plt.close()

def makeGifFromFrames(framesDir: str, outPath: str, fps: int=5):
    files = sorted([os.path.join(framesDir, f) for f in os.listdir(framesDir) if f.lower().endswith(".png")])
    if not files:
        raise RuntimeError("No hay frames .png en el directorio indicado.")
    imgs = [imageio.imread(f) for f in files]
    imageio.mimsave(outPath, imgs, duration=1.0/float(fps))

def plotResults(coords: List[Tuple[float, float]], bestTour: List[int], history: List[int], title: str = ""):
    xs = [coords[i][0] for i in bestTour] + [coords[bestTour[0]][0]]
    ys = [coords[i][1] for i in bestTour] + [coords[bestTour[0]][1]]

    plt.figure(figsize=(11,5))

    plt.subplot(1,2,1)
    plt.plot(xs, ys, marker="o")
    for idx, (x, y) in enumerate(coords):
        plt.text(x, y, str(idx+1), fontsize=6)
    plt.title(f"Mejor tour {title}")

    plt.subplot(1,2,2)
    plt.plot(history)
    plt.xlabel("Generación"); plt.ylabel("Distancia best-so-far")
    plt.title("Evolución del costo")

    plt.tight_layout()
    plt.show()

