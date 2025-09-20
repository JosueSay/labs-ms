# `poblation.py` — Construcción de población inicial para TSP (semillas + aleatorios)

Módulo centrado en **generar poblaciones iniciales** para un algoritmo evolutivo de TSP. Combina **semillas heurísticas** (Nearest Insertion con inserción barata y mantenimiento incremental) con **tours aleatorios** y asegura **diversidad** mediante deduplicación. Depende de `io_tsp.getDistance` para consultas O(1) sobre el vector comprimido de distancias.

## ¿Por qué está diseñado así?

- **Semillas "buenas" pero baratas**: usar *Nearest Insertion* reduce drásticamente el costo inicial frente a tours totalmente aleatorios, sin el costo de un 2-opt/3-opt completo. El mantenimiento incremental `d_to_tour` evita recomputaciones, manteniendo el algoritmo en **$O(n^2)$**.
- **Diversidad controlada**: limitar `seedFrac` (fracción de semillas) evita poblar en exceso con tours muy similares (heurística determinista) y deja espacio a **exploración** vía tours aleatorios. Para instancias grandes, el límite baja aún más.
- **Memoria y velocidad**: se apoya en la **matriz comprimida** de `io_tsp` -> consultas de distancia en **O(1)** y sin almacenar $n \times n$ completo.
- **Población sin duplicados**: se deduplican tours y se rellena hasta `N` con nuevos aleatorios, favoreciendo **diversidad fenotípica** desde el arranque.

## Funciones (firma, parámetros, retorno, complejidad)

### `makeRandomTour(n: int) -> list[int]`

Genera un tour aleatorio (permuta de `0..n-1`).

- **Parámetros:** `n>0`.
- **Retorna:** lista de longitud `n`.
- **Errores:** `ValueError` si `n<=0`.
- **Costo:** O(n).

### `nearestInsertionSeed(n: int, vec: list[int]) -> list[int]`

Semilla por **Nearest Insertion** de `d_to_tour[j] = min distancia de j al tour actual`.

**Parámetros:**

- `n`: número de ciudades.
- `vec`: vector comprimido del triángulo superior (de `io_tsp.buildDistanceMatrixCompressed`).
  **Retorna:** tour heurístico (lista de `0..n-1`).
  **Detalles clave:**
- Arranca con ciudad aleatoria `start` y su **vecina más cercana**.
- Cierra temporalmente el lazo añadiendo `start` al final para evaluar inserciones en arcos `(i,j)`.
- En cada paso: elige ciudad `c` **más cercana al tour** (`min d_to_tour`) y la inserta en el **arco** que minimiza el incremento de costo `d(i,c)+d(c,j)-d(i,j)`.
- Tras insertar `c`, actualiza **solo** `d_to_tour[j] = min(d_to_tour[j], d(j,c))` para las restantes (evita recomputar contra todo el tour).
- Quita el `start` duplicado al final.
  **Complejidad:**
- Selección de ciudad y mejor arco por inserción: O(n).
- O(n) inserciones -> **$O(n^2)$** en total.
  **Notas:** Para `n<3` retorna tours triviales. Usa `getDistance(i,j,n,vec)` para consultas O(1).

### `initPopulation(n: int, vec: list[int], N: int, seedFrac: float = 0.25) -> list[list[int]]`

Construye la población inicial mezclando **k semillas** (*Nearest Insertion*) y **N−k aleatorios**, con **deduplicación** y **relleno** hasta alcanzar `N`.
**Parámetros:**

- `n`: número de ciudades.
- `vec`: vector comprimido de distancias.
- `N`: tamaño de población (**>0**).
- `seedFrac`: fracción inicial de semillas (se **recorta** a `[0,1]` y además a `<=0.25` si `n<200`, o `<=0.10` si `n≥200`).
  **Retorna:** lista de `N` tours únicos (listas de enteros).
  **Flujo:**

1. `k = max(1, int(N*seedFrac))`.
2. Genera `k` semillas con `nearestInsertionSeed`.
3. Completa con `N−k` tours de `makeRandomTour`.
4. **Dedup** preservando orden; si faltan, sigue generando aleatorios distintos hasta llegar a `N`.
   **Complejidad:**

- Generar semillas: `k*$O(n^2)$`.
- Aleatorios: `O(N*n)`.
- Deduplicación: `O(N*n)` para *hashing* de tuplas (memoria O(N*n)).
  **Racional:** balancea **calidad inicial** (semillas) y **diversidad** (aleatorios); el recorte de `seedFrac` evita sobrecosto y **convergencia prematura** en instancias grandes.

## Interacción con el resto del sistema

- Se espera que **antes** hayas construido `vec` con `io_tsp.buildDistanceMatrixCompressed` y que tus operadores (selección/cruce/mutación/2-opt/3-opt) consuman tours 0-based.
- La **semilla** usa `random` del intérprete; si deseas **reproducibilidad**, fija la semilla global (`random.seed(...)`) desde tu *runner* antes de llamar a `initPopulation`.
