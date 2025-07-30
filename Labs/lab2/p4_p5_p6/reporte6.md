# Problema 6

Hallar todos los ceros del polinomio

$$
f(x) = 2x^5 + 3x^4 - 3x^3 - 10x^2 - 4x + 4,
$$

mediante los algoritmos numéricos.

## Resultados por método

### 1. Método de Bisección

Para cada raíz se seleccionó un intervalo $[a, b]$ con cambio de signo: $f(a) \cdot f(b) < 0$.

| Raíz encontrada     | Intervalo usado | Iteraciones | Raíz (9 decimales) |
| ------------------- | --------------- | ----------- | ------------------ |
| -1.3037028114194982 | \[-5, 0]        | 34          | -1.303702811       |
| 0.4546075598336756  | \[0, 1]         | 31          | 0.454607560        |
| 1.5937398741953075  | \[1, 5]         | 33          | 1.593739874        |

Este método encontró todos las raices, pero con mayor cantidad de iteraciones en cada caso.

### 2. Método de la Secante

Se probaron distintos pares de puntos iniciales, con resultados consistentes:

| Raíz encontrada     | Puntos iniciales | Iteraciones | Raíz (9 decimales) |
| ------------------- | ---------------- | ----------- | ------------------ |
| -1.3037028112439697 | (-5, -1)         | 9           | -1.303702811       |
| 0.4546075601876466  | (0, 1)           | 8           | 0.454607560        |
| 1.5937398739794297  | (1.3, 5)         | 13          | 1.593739874        |

La secante logró resultados correctos en menos iteraciones que la bisección, pero fue sensible al escoger los puntos ya que al escoger los puntos extremos del intervalo del método de bisección se obtuvieron:

| Raíz encontrada     | Puntos iniciales | Iteraciones | Raíz (9 decimales) |
| ------------------- | ---------------- | ----------- | ------------------ |
| 0.4546075601876466  | (-5, -1)         | 10          | 0.454607560        |
| 0.4546075601876466  | (0, 1)           | 8           | 0.454607560        |
| 0.4546075601876466  | (1.3, 5)         | 10          | 0.454607560        |

### 3. Método de Newton-Raphson

Este método fue probado con distintos puntos iniciales $x_0$:

| Punto inicial $x_0$ | Raíz encontrada     | Iteraciones | Comentario                       |
| ------------------- | ------------------- | ----------- | -------------------------------- |
| -5                  | -1.3037028112439695 | 12          | Converge correctamente           |
| 0                   | 0.4546075601876466  | 7           | Converge rápido                  |
| 1                   | 0.4546075601876466  | 6           | Converge, pero a raíz equivocada |
| 5                   | 1.5937398739794297  | 11          | Converge correctamente           |

- Newton-Raphson converge rápidamente si el punto inicial está razonablemente cerca de una raíz.
- Con $x_0 = 1$, convergió a la raíz en $x \approx 0.4546$ en lugar de la cercana a 1.59.
- No detecta automáticamente todas las raíces, por lo que se necesita análisis previo del dominio o múltiples ejecuciones (al igual que en los otros métodos).

## Conclusión

- **Bisección**: garantizó convergencia con precisión, pero tomó entre 31 y 34 iteraciones por raíz.
- **Secante**: fue más eficiente, convergiendo entre 8 y 13 iteraciones, dependiendo de los puntos iniciales.
- **Newton-Raphson**: el más rápido cuando parte cerca de la raíz (6 a 12 iteraciones), pero puede converger a una raíz no deseada si el punto inicial está mal ubicado.
