# `optimal.py` — Visor y calculador de costo para instancias TSPLIB

Herramienta interactiva para **leer** una instancia **TSPLIB** (`.tsp`) y un **tour** (`.tour`), **calcular** su distancia total usando la métrica correcta (**EUC_2D** o **GEO**) y **graficar** el recorrido con opciones de marcado.

## Estructura y supuestos de entrada

* **`.tsp`** con `NODE_COORD_SECTION` y `EDGE_WEIGHT_TYPE` en **{`EUC_2D`, `GEO`}**.
* **`.tour`** con `TOUR_SECTION` y fin en `-1` o `EOF`.
* Los archivos deben estar en `./data/` (directorio fijo en el script).

## Uso

```bash
python optimal.py
```

1. El programa lista los `.tsp` en `data/` y te pide elegir uno.
2. Lista los `.tour` en `data/` y te pide elegir uno.
3. Pregunta el tipo de marcado en la gráfica:

   * `1` Etiquetas (IDs),
   * `2` Puntos,
   * `3` Puntos + etiquetas,
   * `4` Sin marcadores.
4. Muestra por consola el nombre de la instancia, el `EDGE_WEIGHT_TYPE` y la **distancia total**; luego abre la **gráfica** del tour.

## Parámetros

* **Selección de `.tsp`**: índice de la lista mostrada.
* **Selección de `.tour`**: índice de la lista mostrada.
* **Marcado**: opción 1–4 para etiquetas y/o puntos.
* **Tamaño de punto**: fijo a `marker_size=2` dentro del código (ajustable editando la llamada a `graphTour`).

## Funcionalidad, funciones y retornos

* `degminToRad(x: float) -> float`
  Convierte **grados.minutos** (TSPLIB GEO) a **radianes**.

* `euc2dRounded(xi, yi, xj, yj) -> int`
  Distancia **EUC_2D** como `int(d + 0.5)` (redondeo TSPLIB).

* `geoDistance(lat_i, lon_i, lat_j, lon_j) -> int`
  Distancia **GEO** con `R=6378.388` y `int(R*acos(...)+1.0)`. Usa `degminToRad`.

* `parseTsp(path) -> (name: str, edge_type: str, coords: dict[int, (float, float)])`
  Lee `NAME`, `EDGE_WEIGHT_TYPE`, `NODE_COORD_SECTION`; devuelve **nombre**, **tipo de métrica** y **coordenadas** (1 -> (x,y)).

* `readTourTsp(path) -> list[int]`
  Lee `TOUR_SECTION` y devuelve la **secuencia de nodos** (IDs 1-base).

* `nodeDistance(p, q, edge_type) -> int`
  Calcula la **distancia entre dos nodos** según `edge_type` (**EUC_2D** o **GEO**).

* `tourDistance(coords, tour, edge_type) -> int`
  Suma la **distancia total del ciclo** (cierra con el primer nodo).

* `graphTour(coords, tour, title, show_labels, show_points, marker_size=2) -> None`
  Grafica el tour; permite **puntos**, **etiquetas** o **ninguno**. Mantiene **escala igual** y muestra la figura.

* `main() -> None`
  Flujo **interactivo**: lista/elige archivos, pide modo de marcado, calcula costo (con la métrica del `.tsp`) y grafica.

## Detalles de cálculo (TSPLIB)

* **EUC_2D**: distancia Euclídea y redondeo **exacto** TSPLIB `int(d + 0.5)`.
* **GEO**: lectura de coordenadas en **grados.minutos**, conversión a **radianes** y fórmula esférica con `R=6378.388`. Redondeo `int(... + 1.0)`.

## Salidas

* **Consola**:
  `Instancia: <NAME> | EDGE_WEIGHT_TYPE: <tipo>`
  `Distancia total del tour: <valor>`

* **Gráfica**:
  Ventana con el tour dibujado (línea) y, si se elige, puntos y/o etiquetas. No guarda imágenes en disco (usa `plt.show()`).

## Notas y limitaciones

* Lee solo instancias con **`NODE_COORD_SECTION`**; no maneja `EDGE_WEIGHT_SECTION`.
* Soporta **EUC_2D** y **GEO**; otras métricas no están implementadas.
* Se asume que el `.tour` es **válido** para el `.tsp` (mismo conjunto de IDs). No hay validaciones cruzadas extensas.
* El sistema de ejes es **cartesiano (Y hacia arriba)**. Si tus `.tsp` provienen de imágenes, asegúrate de haber **convertido** coordenadas desde el sistema de imagen (PIL Y-down) al exportar, para que la forma no salga “invertida”.
