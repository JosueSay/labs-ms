# Data

- **NAME: berlin52** → nombre de la instancia del problema (en este caso, "berlin52").

- **TYPE: TSP** → indica que es un problema de tipo TSP.

- **COMMENT:** → información adicional (ejemplo: “52 locations in Berlin”).

- **DIMENSION: 52** → cantidad de ciudades/nodos (52).

- **EDGE_WEIGHT_TYPE: EUC_2D** → tipo de cálculo de distancia entre ciudades. Aquí significa distancia euclidiana en 2D. La fórmula es:

  $$
  d(i,j) = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}
  $$

  usualmente redondeada al entero más cercano.

- **NODE_COORD_SECTION** → aquí comienzan las coordenadas de cada ciudad.
  Ejemplo:

  ```bash
  1 565.0 575.0
  ```

  - **1** → identificador de la ciudad (nodo 1).
  - **565.0 575.0** → coordenadas **(x, y)** de esa ciudad en el plano.
