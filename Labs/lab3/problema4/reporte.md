# Problema 4

Considere el siguiente conjunto de datos que se incluye en el archivo **datos_lab3.csv**. Estos datos corresponden a una serie de tiempo.

Se quiere realizar un modelo de regresión de la forma

$$
y = \beta_0 + \beta_1 x + \beta_2 x^2 + \beta_3 \sin(7x) + \beta_4 \sin(13x),
$$

que explique la relación entre las variables $x$ y $y$.

Para ello, vamos a formular un problema de optimización en la variable vectorial

$$
\beta = (\beta_0, \beta_1, \beta_2, \beta_3, \beta_4) \in \mathbb{R}^5.
$$

Hallar el modelo de regresión corresponde a hallar el vector $\beta$ que minimiza la función de error regularizada

$$
E_\lambda(\beta) = \sum_{i=1}^{n} \left( f(x_i) - y_i \right)^2 + \lambda \sum_{i=1}^{n-1} \left( f(x_{i+1}) - f(x_i) \right)^2.
$$

Implementar en Python un algoritmo de optimización para resolver el problema de regresión en los siguientes 3 casos:

## Inciso a

Cuando $\lambda = 0$, regresión lineal sin regularización.

## Inciso b

Cuando $\lambda = 100$, regresión lineal con regularización de Tychonoff.

## Inciso c

Cuando $\lambda = 500$.

Compare las tres soluciones obtenidas en la misma gráfica, junto con los datos originales. Discuta las soluciones obtenidas y sus resultados. Explique cuál es el papel de la constante $\lambda$.
