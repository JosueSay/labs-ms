# TSP-GA (berlin52)

## Estructura del proyecto

```bash
.
├─ ga.py          # Núcleo del GA: operadores + bucle runGa()
├─ io_tsp.py      # I/O TSPLIB + distancias (matriz simétrica comprimida)
├─ poblation.py   # Generación de población y semillas (random + nearest-insertion)
├─ viz.py         # Visualización: frames PNG, GIF y plot final
├─ main.py        # CLI/orquestación (args, llamada a runGa, plots, GIF)
├─ optimal.py     # Visualiza la ruta óptima provista por el problema
└─ requirements.txt
```

### Contenido por archivo

* **ga.py**

  * `selectionTournament`, `crossoverOX`, `crossoverSCX`
  * `mutateInsertion`, `mutateSwap`, `apply2optOnce`
  * `runGa(...)`: lazo principal del GA (selección -> cruce -> mutación graphResult 2-opt ocasional -> reemplazo), logging de mejoras, cortes por estancamiento/tiempo, guardado de frames.

* **io_tsp.py**
  * `parseTsp`: lee formato TSPLIB (`NAME`, `NODE_COORD_SECTION`, etc.).
  * `buildDistanceMatrixCompressed`: crea matriz de distancias simétrica comprimida (triángulo superior) con `EUC_2D` (redondeo entero).
  * `getDistance`, `tourDistance`: *lookups* O(1) y costo total del tour.

* **poblation.py**
  * `makeRandomTour`, `nearestInsertionSeed` (semilla heurística)
  * `initPopulation`: mezcla semillas heurísticas + tours aleatorios.

* **viz.py**

  * `saveFrame`: guarda PNG (mejor tour + curva de costo).
  * `makeGifFromFrames`: construye GIF desde los PNG.
  * `plotResults`: muestra figura final con tour y evolución.

* **main.py**
  * CLI con `argparse`. Ejecuta `runGa`, imprime resumen, invoca `plotResults`/`makeGifFromFrames`. Incluye modo `--estimate` (calienta y estima tiempo).

* **optimal.py**
  * Script auxiliar para graficar la ruta óptima que provee el problema (usa utilidades de `io_tsp.py` y `viz.py`). Útil para comparar vs. el mejor tour encontrado por el GA.

## Instalación rápida

```bash
pip install -r requirements.txt
```

## Parámetros (CLI)

| Parámetro      | Tipo  | Rango / Valores  |             Default | Descripción                                               |
| -------------- | ----- | --------------:  | ------------------: | --------------------------------------------------------- |
| `--file`       | str   |  ruta existente  | `data/berlin52.tsp` | Archivo TSPLIB a cargar.                                  |
| `--N`          | int   |            >= 10 |                 300 | Tamaño de población.                                      |
| `--maxIter`    | int   |             >= 1 |                1500 | Iteraciones máximas (generaciones).                       |
| `--survivors`  | float |          \[0,1]  |                0.20 | Fracción S de sobrevivientes.                             |
| `--crossover`  | float |          \[0,1]  |                0.60 | Fracción C creada por cruce.                              |
| `--mutation`   | float |          \[0,1]  |                0.20 | Fracción M creada por mutación. **S+C+M=1**.              |
| `--pc`         | float |          \[0,1]  |                0.95 | Probabilidad de aplicar cruce a una pareja.               |
| `--pm`         | float |   \[0,1] o `-1`  |                  -1 | Mutación ligera a hijos (si `-1` -> usa 1/n).             |
| `--elitism`    | float |          \[0,1]  |                0.05 | Fracción élite reinyectada.                               |
| `--k`          | int   |             >= 2 |                   5 | Tamaño de torneo (selección).                             |
| `--scx`        | flag  |               —  |                 off | Si está presente, usa SCX en lugar de OX.                 |
| `--twoOptProb` | float |          \[0,1]  |                0.05 | Proporción de hijos sometidos a **una** 2-opt.            |
| `--stall`      | int   |             >= 0 |                 400 | Cortar si no mejora en `stall` generaciones.              |
| `--timeLimit`  | float |       >= 0 (seg) |                 0.0 | Cortar por tiempo (0 = sin límite).                       |
| `--record`     | flag  |               —  |                 off | Guarda un PNG en cada mejora.                             |
| `--framesDir`  | str   |         carpeta  |            `frames` | Carpeta para PNG de mejoras.                              |
| `--gifOut`     | str   |     ruta `.gif`  |                  "" | Construye GIF desde `framesDir` (requiere `--record`).    |
| `--seed`       | int   |      cualquiera  |                  42 | Semilla aleatoria (reproducibilidad).                     |
| `--estimate`   | int   |             >= 1 |                   0 | Corre *warmup* N gen para estimar tiempo total y termina. |
| `--noPlot`     | flag  |               —  |                 off | No mostrar la figura final.                               |

**Notas clave**

* **Matriz simétrica**: no se recorre la matriz completa; se usa triángulo superior comprimido y *lookups* `getDistance(i,j)`.
* **SCX vs OX**: SCX = cruce sesgado por distancias (suele escalar mejor); OX = clásico de orden.
* **2-opt**: intensificación local barata, aplicada en una pasada sobre una fracción de hijos.

## Comando "óptimo"

Estos parámetros dieron el mejor resultado en tus corridas (con `seed=42`):

```bash
python main.py --N 600 --maxIter 200000 --survivors 0.10 --crossover 0.80 --mutation 0.10 --pc 0.98 --pm -1 --elitism 0.03 --k 3 --scx --twoOptProb 0.30 --stall 4000 --timeLimit 0 --seed 42 --estimate 300 --noPlot
```

> **Sugerencia:** si se desea GIF se debe añadir `--record --framesDir frames --gifOut berlin52_tsp_optimal.gif`.
