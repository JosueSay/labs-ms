# `io_tsp.py` — Lectura TSPLIB, métricas (EUC_2D/GEO) y distancias comprimidas

Este módulo resuelve tres necesidades típicas al trabajar con TSP tipo TSPLIB:

1. **Parsear** archivos `.tsp` con `NODE_COORD_SECTION` (EUC_2D o GEO).
2. **Medir distancias** exactamente como define TSPLIB (redondeos incluidos).
3. **Guardar memoria/tiempo** usando una **matriz de distancias comprimida** (triángulo superior) y accesos O(1).

## Decisiones de diseño (y por qué)

- **Vector comprimido en vez de matriz completa.**
  Una matriz completa $n \times n$ guarda $n^2$ entradas; el **triángulo superior** guarda `n(n−1)/2`, casi la mitad, y evita duplicar `d(i,j)=d(j,i)` y las diagonales 0. Con **n=10 000**, la diferencia es \~100 M vs \~50 M entradas; incluso con `int32` el ahorro de memoria es enorme. El módulo expone accesos O(1) con `getDistance`.

- **Rounding TSPLIB exacto.**
  En **EUC_2D** usa `int(d + 0.5)` (no `round`) para evitar errores $\pm1$ en límites; en **GEO** usa `int(R*acos(...)+1.0)`. Esto replica fielmente los *benchmarks* TSPLIB.

- **Cálculo vectorizado para EUC_2D.**
  Con NumPy se computa la matriz de distancias en float64 y se redondea **exactamente** según TSPLIB, acelerando notablemente instancias medianas (n $\approx$ 100–2000). Para **GEO** se usa bucle clásico (la trigonometría domina y n suele ser bajo).

- **Parser mínimo y robusto.**
  Lee `NAME`, `EDGE_WEIGHT_TYPE`, `NODE_COORD_SECTION` y devuelve coordenadas en orden; ignora el índice de la primera columna al cargar (se reindexa 0..n−1 internamente), lo cual simplifica el acceso.

## Funciones (firma, parámetros, retorno, complejidad)

### `triIndex(i: int, j: int, n: int) -> int`

- **Qué hace:** índice lineal para el elemento `(i,j)` del **triángulo superior** (requiere `i<j`) dentro de un vector de longitud `n(n−1)/2`.
- **Parámetros:** `i`, `j` (0..n−1), `n`.
- **Retorno:** posición en el vector comprimido.

### `euc2d_rounded(xi: float, yi: float, xj: float, yj: float) -> int`

- **Qué hace:** distancia **EUC_2D** con redondeo TSPLIB `int(d + 0.5)`.
- **Parámetros:** coordenadas `(xi,yi)`, `(xj,yj)`.
- **Retorno:** distancia entera.

### `degmin_to_rad(x: float) -> float`

- **Qué hace:** convierte **grados.minutos** (p.ej., `68.58` -> `68°58′`) a radianes según TSPLIB.
- **Parámetros/retorno:** valor en grados.minutos -> radianes.

### `geo_distance(lat_i, lon_i, lat_j, lon_j) -> int`

- **Qué hace:** distancia **GEO** TSPLIB con radio `R=6378.388` y redondeo `int(... + 1.0)`.
- **Parámetros:** lat/lon en **grados.minutos**.
- **Retorno:** distancia entera GEO.
- **Notas:** usa `degmin_to_rad` + fórmula oficial (combinaciones `q1,q2,q3`).

### `parseTsp(path: str) -> tuple[str, str, list[tuple[float, float]]]`

- **Qué hace:** lee un `.tsp` con `NODE_COORD_SECTION`.
- **Parámetros:** ruta al archivo.
- **Retorno:** `(name, edge_weight_type, coords)` donde `coords` es una lista `[(x,y), ...]` en el orden leído.
- **Notas:** Soporta **EUC_2D** y **GEO**. Para GEO, los pares se interpretan como `(lat, lon)` en grados.minutos. El índice 1..n del archivo se **ignora** al cargar; internamente se trabaja 0..n−1.

### `buildDistanceMatrixCompressed(coords, edge_weight_type='EUC_2D') -> tuple[int, list[int]]`

- **Qué hace:** construye el **vector comprimido** del triángulo superior de la matriz de distancias.
- **Parámetros:**

  - `coords`: lista de puntos.
  - `edge_weight_type`: `'EUC_2D'` o `'GEO'`.
- **Retorno:** `(n, vec)` donde `n=len(coords)` y `vec` tiene longitud `n(n−1)//2`.
- **Implementación:**
  - EUC_2D: vectorizado NumPy en float64 -> `int(d+0.5)` -> empaquetado del triángulo superior.
  - GEO: bucle doble (i\<j) aplicando `geo_distance`.
- **Por qué comprimido:** reduce a la mitad el almacenamiento, clave para GAs/heurísticas que consultan muchas distancias pero no necesitan la matriz completa ni duplicada.

### `getDistance(i: int, j: int, n: int, vec: list[int]) -> int`

- **Qué hace:** devuelve `d(i,j)` en O(1) desde el vector comprimido.
- **Parámetros:** índices `i`, `j`, `n`, y el `vec` comprimido.
- **Retorno:** distancia entera (0 si `i==j`).
- **Notas:** si `i>j`, intercambia; si `i==j`, retorna 0. Central para **loops de evaluación** en GA/2-opt/3-opt.

### `tourDistance(tour: list[int], n: int, vec: list[int]) -> int`

- **Qué hace:** costo de un **ciclo Hamiltoniano** (cierra al inicio) usando `getDistance`.
- **Parámetros:** `tour` (índices 0..n−1), `n`, `vec`.
- **Retorno:** suma total del tour.

## Otras aclaraciones

- **¿Por qué no guardar la matriz completa?**
  Además del 2$\times$ en memoria, el acceso $O(1)$ del vector comprimido es suficiente; y para actualizaciones incrementales (p.ej., en 2-opt) casi siempre se consultan **pocas** entradas por iteración, no se hace álgebra de matrices. El triángulo superior es el *sweet spot* entre costo de construcción $(O(n^2))$ y eficiencia de consulta.

- **Exactitud numérica en EUC_2D.**
  Se usa float64 y luego `floor(d+0.5)` exactamente como TSPLIB; usar `round()` introduce diferencias en umbrales. Esto importa si comparas contra costos "oficiales".

- **GEO es más caro por par.**
  La fórmula es trigonométrica; a n$\approx$200–300 sigue siendo manejable. Para n muy grande, evalúa si realmente necesitas GEO o si puedes precalcular/cachéar.

- **Índices TSPLIB (1..n) vs internos (0..n−1).**
  `parseTsp` ignora el índice del archivo y devuelve solo `coords` ordenadas; asegúrate de **convertir** tu `.tour` a 0..n−1 al usar `tourDistance`. Si tus `.tour` vienen ya en 0-based, todo bien; si vienen 1-based, resta 1.

- **Orientación Y (si viene de imágenes el "óptimo").**
  Este módulo **no invierte ejes**; asume coordenadas cartesianas estándar. Si generas `.tsp` desde imágenes (PIL Y-down), **voltea antes** de construir distancias, para que la visualización y el costo coincidan con lo esperado.
