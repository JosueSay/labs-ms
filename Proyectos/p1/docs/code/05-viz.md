# `viz.py` — Visualización de tours y evolución del costo

Utilidades para **guardar frames**, **generar GIFs** y **plotear** el mejor tour y su **historial de costos** durante la ejecución de tu heurística TSP. Usa **Matplotlib** para las figuras y **imageio** para animaciones.

## ¿Qué hace?

- **Comparte en una sola figura** el mejor tour y la curva *best-so-far* por generación, lo que facilita ver **estructura** (izquierda) y **convergencia** (derecha). Usa un `subplot(1,2,...)` fijo para consistencia entre frames.
- **Separa responsabilidades**:

  - `saveFrame(...)` -> guarda un PNG por iteración/generación.
  - `makeGifFromFrames(...)` -> arma el GIF a partir de los PNG (orden lexicográfico).
  - `plotResults(...)` -> muestra una figura interactiva (sin escribir a disco).
- **Etiquetado 1-based** en el gráfico del tour: el texto usa `idx+1`, útil si tu `.tour` TSPLIB es 1-based; el array `bestTour` en cambio es 0-based (índices de Python).

## Funciones (parámetros, retorno, detalles)

### `saveFrame(coords, bestTour, history, outPath, title)`

Guarda **un PNG** con el mejor tour y la evolución del costo. **No retorna** (efecto: escribe a disco).

**Parámetros:**

- `coords: List[Tuple[float, float]]` — coordenadas de las ciudades (índices 0-based).
- `bestTour: List[int]` — orden del tour (0-based). Se cierra al inicio para trazar el ciclo.
- `history: List[int]` — costos *best-so-far* por generación (eje X = índice).
- `outPath: str` — ruta de salida del PNG.
- `title: str` — texto para el título del panel izquierdo ("Mejor tour ...").

**Detalles:**

- Dibuja el tour con marcadores `'o'` y etiqueta cada punto como `idx+1` (texto pequeño).
- Panel derecho: `plt.plot(history)` con ejes etiquetados "Generación" / "Distancia best-so-far".
- Usa `plt.tight_layout()` y guarda con `dpi=120`.

### `makeGifFromFrames(framesDir, outPath, fps=5)`

Crea un **GIF** a partir de todos los `.png` en `framesDir` (ordenados por nombre). **No retorna** (efecto: escribe a disco).

**Parámetros:**

- `framesDir: str` — carpeta con PNGs (p. ej., generados por `saveFrame`).
- `outPath: str` — ruta del GIF destino.
- `fps: int = 5` — cuadros por segundo; se traduce a `duration=1.0/fps`.

### `plotResults(coords, bestTour, history, title="")`

Muestra **en pantalla** (no guarda) la figura con tour + historial. **No retorna**.

- **Parámetros:** mismos que `saveFrame`, salvo que no recibe `outPath`.
- **Uso típico:** al final de la ejecución para inspección manual.
