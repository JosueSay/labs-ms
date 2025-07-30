# Problema 5

Hallar todos los ceros de la función

$$
g(x) = x^2 + \frac{1}{x - 7}
$$

con al menos **7 decimales de precisión**.

Compare las soluciones obtenidas con cada uno de los algoritmos anteriores en términos del número de iteraciones.

## Resultados por método

### 1. Método de Bisección

Para cada raíz, se seleccionó un intervalo $[a, b]$ donde $f(a) \cdot f(b) < 0$.

| Raíz encontrada      | Intervalo usado | Iteraciones | Raíz (7 decimales) |
| -------------------- | --------------- | ----------- | ------------------ |
| -0.36839485401287675 | \[-2,0]         | 32          | -0.3683949         |
| 0.38892324501648545  | \[0, 2]         | 32          | 0.3889232          |
| 6.979471608847382    | \[6.5, 6.98]    | 30          | 6.9794716          |

Este método encontró los ceros correctamente pero con más iteraciones.

### 2. Método de la Secante

Usando dos puntos iniciales bien elegidos en los alrededores de cada raíz:

| Raíz encontrada    | Puntos iniciales | Iteraciones | Raíz (7 decimales) |
| ------------------ | ---------------- | ----------- | ------------------ |
| -0.368394853732975 | (-2, 0)          | 12          | -0.3683949         |
| 0.3889232446865156 | (0, 2)           | 12          | 0.3889232          |
| 6.979471609046458  | (6.5, 6.98)      | 8           | 6.9794716          |

Se utilizó los opuntos extremos del intervalo del método de bisección y se obtuvieorn los mismos resultados pero en menos iteraciones.

### 3. Método de Newton-Raphson

Usando un solo punto inicial $x_0$. Aquí se observa la sensibilidad del método.

| Punto inicial $x_0$ | Raíz encontrada     | Iteraciones | Comentario                             |
| ------------------- | ------------------- | ----------- | -------------------------------------- |
| -2                  | -0.3683948537329749 | 7           | Converge correctamente                 |
| 0                   | -0.3683948537329749 | 10          | Converge, aunque comenzó lejos         |
| 6.5                 | 0.3889232446865155  | 8           | No converge a la raíz cercana esperada |
| 2                   | 0.3889232446865155  | 7           | Converge rápido a la raíz positiva     |
| 6.98                | 6.97947160904646    | 4           | Muy buena convergencia                 |

- El método de Newton-Raphson varió su comportamiento con distintos puntos iniciales.
- No es adecuado para encontrar todas las raíces sin análisis previo del dominio (sin embargo, para esta función se hizo análisis del dominio para saber previamente las raíces ya que para todos los métodos métodos no encuentra todos los ceros por lo que hay que ir por intervalo).
- Falló en distinguir entre las dos primeras raíces cuando se partía desde $x_0 = 6.5$ y $x_0 = 2$, conduciendo a la raíz equivocada.

## Conclusión

- **Bisección**: garantiza convergencia, pero con mayor número de iteraciones (30–32).
- **Secante**: logra la mejor eficiencia cuando se escogen buenos puntos iniciales.
- **Newton-Raphson**: el más rápido en casos ideales, pero sensible a la elección del punto inicial; puede converger a la raíz equivocada.
