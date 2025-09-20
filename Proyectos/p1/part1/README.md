# TSP-GA

<!-- ## Estructura del proyecto

```bash
.
❯_: estructura
.
├── README.md
├── docs
│   └── code # documentación de código
├── images
│   ├── gifs # gifs 
│   ├── optimo_ga # resultados optimos usando ga
│   └── optimo_ref # resultado tsp teoricos / referenciados
├── part1
│   ├── README.md # Este archivo
│   ├── data # archivos tsp  y opt.tour
│   ├── docs
│   │   ├── estructura.md # documentación sobre tipo de estructura usada
│   │   ├── ga # documentación realizada para ga
│   │   ├── ga.md
│   │   ├── notes # notas de clase para este tema
│   │   ├── parametros.md # explicación a detalle parametros
│   │   ├── reporte.md # reporte para la primera parte del proyecto
│   │   └── tsp.md # explicacióno problema tsp
│   ├── ga.py
│   ├── io_tsp.py
│   ├── main.py
│   ├── optimal.py
│   ├── poblation.py
│   └── viz.py
├── part2 # parte 2 del proyecto
├── part3 # parte 3 del proyecto
├── requirements.txt # dependencias
└── results 
    └── ga # resultados logs + csv obtenido por el algoritmo genetico
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

## Instalación

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

**Notas clave:**

* **Matriz simétrica**: no se recorre la matriz completa; se usa triángulo superior comprimido y *lookups* `getDistance(i,j)`.
* **SCX vs OX**: SCX = cruce sesgado por distancias (suele escalar mejor); OX = clásico de orden.
* **2-opt**: intensificación local barata, aplicada en una pasada sobre una fracción de hijos. -->

## Ejecuciones

### Caso **eil101**

Comando ejecutado:

```bash
python main.py --file data/eil101.tsp --N 600 --maxIter 200000 --survivors 0.15 --crossover 0.65 --mutation 0.20 --pc 1.0 --pm -1 --elitism 0.02 --k 3 --scx --twoOptProb 0.25 --stall 3000 --timeLimit 1200 --seed 11 --record --framesDir logs/eil101/frames --gifOut logs/eil101/eil101_tsp_optimal.gif --csv logs/eil101/eil101_seed11.csv --eaxFrac 0.15 --edgeLambda 0.15 --edgeTopFrac 0.30 --edgeFreqPeriod 200 --assortative --mem3OptSteps 4 --speciesPeriod 800 --speciesThresh 0.35 --speciesCullFrac 0.20 --catastropheFrac 0.20
```

* Se corrió por 20 minutos.
* El óptimo de 629 se alcanzó al minuto 1.20 y no mejoró, como era esperado, ya que se conocía que ese era el valor óptimo teórico.
* El criterio de paro fue el límite de tiempo (20 min).

Ruta óptima:

```bash
[27, 25, 11, 79, 67, 28, 23, 53, 3, 54, 24, 38, 66, 22, 55, 74, 40, 21, 73, 71, 72, 20, 39, 57, 12, 93, 94, 96, 86, 1, 56, 14, 42, 41, 13, 43, 37, 85, 15, 60, 84, 90, 99, 36, 97, 92, 91, 58, 98, 95, 5, 88, 51, 17, 82, 59, 4, 83, 16, 44, 7, 45, 46, 35, 48, 63, 62, 89, 31, 9, 61, 10, 18, 47, 81, 6, 87, 30, 69, 29, 19, 65, 64, 70, 34, 8, 50, 32, 80, 33, 77, 78, 2, 76, 75, 49, 0, 68, 26, 100, 52]
```

Comparación gráfica:

![TSP Óptimo Eil101 Teórico](../images/optimo_ref/eil101_optimo_ref.png)
![TSP Óptimo Eil101 GA](../images/optimo_ga/eil101_seed11_optimo.png)
![Gif TSP](../images/gifs/eil101_tsp_optimal.gif)

### Caso **gr229**

Comando ejecutado:

```bash
python main.py --file data/gr229.tsp --N 700 --maxIter 999999 --survivors 0.15 --crossover 0.55 --mutation 0.30 --pc 0.95 --pm -1 --elitism 0.02 --k 3 --scx --twoOptProb 0.15 --stall 999999 --timeLimit 28800 --seed 13 --record --framesDir logs/gr229/frames --gifOut logs/gr229/gr229_tsp_optimal.gif --csv logs/gr229/gr229_seed13.csv --eaxFrac 0.20 --edgeLambda 0.10 --edgeTopFrac 0.25 --edgeFreqPeriod 250 --mem3OptSteps 4 --speciesPeriod 700 --speciesThresh 0.38 --speciesCullFrac 0.25 --catastropheFrac 0.25
```

* Se corrió por 8 horas.
* Se alcanzó un valor de 134644 al minuto 21.45, sin mejoras posteriores.
* El criterio de paro fue el límite de tiempo (8 h).

Ruta óptima encontrada (solo costo disponible como referencia):

![TSP Óptimo Gr229 GA](../images/optimo_ga/gr229_seed13_optimo.png)
![Gif TSP](../images/gifs/gr229_tsp_optimal.gif)

### Caso **cherry189**

Comando ejecutado:

```bash
python main.py --file data/cherry189.tsp --N 700 --maxIter 999999 --survivors 0.15 --crossover 0.55 --mutation 0.30 --pc 0.95 --pm -1 --elitism 0.02 --k 3 --scx --twoOptProb 0.15 --stall 999999 --timeLimit 28800 --seed 13 --record --framesDir logs/chery189/frames --gifOut logs/chery189/chery189_tsp_optimal.gif --csv logs/chery189/chery189_seed13.csv --eaxFrac 0.20 --edgeLambda 0.10 --edgeTopFrac 0.25 --edgeFreqPeriod 250 --mem3OptSteps 4 --speciesPeriod 700 --speciesThresh 0.38 --speciesCullFrac 0.25 --catastropheFrac 0.25
```

* Se corrió por 8 horas.
* Se alcanzó un valor de 3176 al minuto 5.69, sin mejoras posteriores.
* El criterio de paro fue el límite de tiempo (8 h).

Comparación gráfica:

![TSP Óptimo Cherry189 Teórico](../images/optimo_ref/cherry189_optimo_ref.png)
![TSP Óptimo Cherry189 GA](../images/optimo_ga/cherry189_seed13_optimo.png)
![Gif TSP](../images/gifs/chery189_tsp_optimal.gif)
