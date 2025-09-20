# `main.py` — CLI para correr el GA de TSP con validaciones, estimación y visualización

Lanza el **algoritmo genético** sobre una instancia TSPLIB, valida y corrige parámetros, permite un **modo de estimación** (warm-up) y, al final, resume resultados y **opcionalmente grafica**/genera GIF.

## Qué hace

1. **Parsea flags** y valida archivo `.tsp`.
2. **Clampa** y **renormaliza** porcentajes **S/C/M** (survivors/crossover/mutation) a que **sumen 1.0**; corrige `k`, `pc`, `pm`, `twoOptProb`, `elitism`, `stall`, `timeLimit`.
3. Modo **estimación** (*no* corre el GA completo): mide `gen/s` y estima el **corte dominante** (maxIter, stall o timeLimit).
4. Modo **run real**: llama `runGa(...)`, imprime resumen (mejor costo, motivo de parada, velocidad), **plotea** y (si corresponde) arma el **GIF**.

## Parámetros (CLI)

### Entrada, tamaño y generaciones

- `--file`: ruta `.tsp` (por defecto `data/berlin52.tsp`).
- `--N`: tamaño de población.
- `--maxIter`: tope de generaciones.

### Mezcla evolutiva (porcentajes S/C/M)

- `--survivors`, `--crossover`, `--mutation`: fracciones de S/C/M (se **clamp** a \[0,1] y se **renormalizan** a que sumen 1.0; si la suma era 0 -> usa **0.2/0.6/0.2**).
- `--pc`: prob. de **cruce** por pareja (0..1).
- `--pm`: prob. de **mutación** por gen (0..1). **Valor especial**: `-1` => usa **1/n** automáticamente.
- `--elitism`: fracción elitista retenida.
- `--k`: tamaño de **torneo** (se corrige a `[2, N]`).
- `--scx`: usa **SCX** (si no, OX).
- `--twoOptProb`: prob. de aplicar **2-opt** a un individuo (0..1).

### Criterios de parada

- `--stall`: generaciones sin mejora para detener.
- `--timeLimit`: segundos; 0 => sin límite.

### Registro, visualización y reproducibilidad

- `--record`: guarda **frame PNG** en cada mejora (usa `--framesDir`).
- `--framesDir`: carpeta para frames.
- `--gifOut`: si se indica, genera **GIF** desde los frames; sobreescribe si existe.
- `--noPlot`: no mostrar figura final (o si no hay DISPLAY selecciona backend `Agg`).
- `--csv`: guarda **traza CSV** (eventos/mejoras).
- `--seed`: semilla RNG.

### Operadores/avanzado

- `--eaxFrac`: fracción de cruces **EAX**.
- `--edgeLambda`, `--edgeTopFrac`, `--edgeFreqPeriod`: control de **histograma de aristas**/frecuencias.
- `--assortative` / `--noAssortative`: emparejar por **lejanía de aristas** (ON por defecto).
- `--mem3OptSteps`: pasos de **3-opt** memorista.
- `--speciesPeriod`, `--speciesThresh`, `--speciesCullFrac`: **especies** (diversidad).
- `--catastropheFrac`: **catástrofes** (reinyección).
- `--noFlocking`: desactiva *flocking* en desempates de 2-opt.

### Modo estimación

- `--estimate`: si `>0`, ejecuta solo **n** generaciones para medir **gen/s** y **no** corre el run completo; imprime tiempos y qué condición **cortaría** primero (maxIter / stall / timeLimit). Ignora `timeLimit` y `stall` (usa `stallGenerations=1e9` internamente).

## Flujo interno y validaciones

- **Archivo**: aborta si no existe o está vacío.
- **Clamp y renormalización**: `clamp01(x)` y `renormalize3(a,b,c)` corrigen rangos y aseguran suma **1.0**; emiten **\[WARN]** si ajustan. También advierte si por redondeo `C=0` o `M=0` con fracciones >0.
- **Backend gráfico**: si `--noPlot` o **sin DISPLAY**, fija `MPLBACKEND=Agg`.
- **Llamada a `runGa`**: pasa `pm=None` cuando `--pm=-1` (se interpreta como **1/n** dentro del GA). Controla *flags* avanzados (EAX, especies, catástrofes, flocking).
- **Salida**: imprime **resumen** (instancia, mejor costo, eventos, motivo de parada, velocidad) y el **mejor tour (0-index)**. Luego **plotea** y, si procede, **genera GIF** desde frames.
