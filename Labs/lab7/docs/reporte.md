# Laboratorio 7

En este laboratorio investigaremos cómo construir un generador de una variable uniforme $Y \sim Unif(0,1)$ y evaluaremos su desempeño mediante distintos métodos y pruebas estadísticas.

## Integrantes

- Abby Donis
- Cindy Gualim
- Josué Say

## Enlaces

- [Repositorio](https://github.com/JosueSay/labs-ms/tree/main/Labs/lab7)

# Problema 1 - Generador Pseudoaleatorio Uniforme

Implementar un generador de números pseudo-aleatorios de tipo LCG (*linear congruential generator*), para generar:

1. Una muestra uniforme finita con valores $x_1, x_2, \ldots, x_n$.

2. Una muestra de una distribución uniforme $Unif(0,1)$.

Defina usted los parámetros: el módulo $m$, las constantes $(0 \le a, c < m)$, y el tamaño $N$ de la muestra generada, y repita sus experimentos para 2 conjuntos diferentes de parámetros.

En ambos casos, muestre estadísticos, histogramas y elabore una prueba de hipótesis para contrastar la muestra generada contra la muestra requerida, para determinar el buen funcionamiento del generador pseudo aleatorio. Use como tamaño de muestra un valor adecuado de $N$.

## Parámetros utilizados

| Experimento | m        | a          | c          | seed  | N     | n_values |
| ----------- | -------- | ---------- | ---------- | ----- | ----- | -------- |
| 1           | $2^{32}$ | 1664525    | 1013904223 | 12345 | 30000 | 64       |
| 2           | $2^{31}$ | 1103515245 | 12345      | 98765 | 30000 | 64       |

Ambos conjuntos de parámetros corresponden a configuraciones del método LCG:

- **Conjunto 1:** parámetros empleados en Numerical Recipes.
- **Conjunto 2:** configuración adoptada por la biblioteca glibc del lenguaje C.

## Histogramas

### Experimento 1

**Muestra discreta:**

![exp1 discreta](../images/p1/exp1_discreta.png)

**Muestra continua (Unif(0,1)):**

![exp1 continua](../images/p1/exp1_uniforme.png)

### Experimento 2

**Muestra discreta:**

![exp2 discreta](../images/p1/exp2_discreta.png)

**Muestra continua (Unif(0,1)):**

![exp2 continua](../images/p1/exp2-uniforme.png)

Las gráficas muestran una distribución prácticamente plana, tanto en la parte discreta como en la continua.
Las medias y desviaciones se aproximan a los valores teóricos esperados:

- Para la muestra discreta: media $\approx$ 31.5, desviación $\approx$ 18.5.
- Para la muestra continua: media $\approx$ 0.5, desviación $\approx$ 0.289.

La autocorrelación lag-1 es cercana a cero, indicando independencia entre valores consecutivos.
Con un tamaño de muestra de **N ≥ 20,000**, los resultados se estabilizan y las pruebas de hipótesis confirman buena uniformidad.
No se observan patrones visibles ni agrupamientos, lo que respalda la calidad de ambos conjuntos de parámetros.

## Resultados estadísticos

### Experimento 1 — Parámetros $m=2^{32}, a=1664525, c=1013904223$

| muestra   | media    | desv     | autocorr_lag1 | estadístico | pvalue  |
| --------- | -------- | -------- | ------------- | ----------- | ------- |
| discreta  | 31.4995  | 18.4731  | -0.135374     | 0.0256      | 1       |
| Unif(0,1) | 0.500659 | 0.289484 | -0.0047995    | 0.00520024  | 0.39043 |

### Experimento 2 — Parámetros $m=2^{31}, a=1103515245, c=12345$

| muestra   | media    | desv     | autocorr_lag1 | estadístico | pvalue  |
| --------- | -------- | -------- | ------------- | ----------- | ------- |
| discreta  | 31.4989  | 18.4745  | -0.00656563   | 0.0256      | 1       |
| Unif(0,1) | 0.499553 | 0.287812 | -0.00006003   | 0.00653715  | 0.15324 |

## Pruebas de hipótesis

Para las muestras **discretas**, se aplicó la **prueba Chi-Cuadrado**, contrastando la frecuencia observada contra la esperada en una distribución uniforme sobre 64 categorías.
Para las muestras **continuas**, se aplicó la **prueba de Kolmogorov–Smirnov** (KS) con la hipótesis nula:

$$
H_0 : X \sim Unif(0,1)
$$

En ambos casos, los valores **p > 0.05**, por lo que **no se rechaza la hipótesis nula**.
Esto significa que las secuencias generadas pueden considerarse consistentes con una distribución uniforme.

El generador LCG implementado cumple con el propósito de generar números pseudoaleatorios con distribución uniforme.
Ambas configuraciones producen resultados similares, pero el conjunto de parámetros del **Experimento 1** (Numerical Recipes) mostró una leve mejor estabilidad en media y un p-value más alto en la prueba KS.

Con un tamaño de muestra grande y parámetros apropiados, el **LCG** produce secuencias indistinguibles (estadísticamente) de una distribución (Unif(0,1)).

# Problema 2 - Mersenne Twister

Investigar e implementar en Python un generador aleatorio de tipo *Mersenne Twister* para generar una distribución uniforme $Unif(0,1)$.

Igual que en el ejercicio anterior, muestre estadísticos, histogramas y elabore una prueba de hipótesis para contrastar la muestra generada contra la muestra teórica, para determinar el buen funcionamiento del generador pseudo aleatorio. Use como tamaño de muestra un valor adecuado de $N$.

> Referencia: <https://en.wikipedia.org/wiki/Mersenne_Twister>

## Parámetros utilizados

| Generador | Algoritmo                 | Semilla | N      | Periodo teórico | Fuente                       |
| --------- | ------------------------- | ------- | ------ | --------------- | ---------------------------- |
| MT19937   | Mersenne Twister (32-bit) | 123456  | 30,000 | $2^{19937} - 1$ | Numpy (BitGenerator MT19937) |

## Histograma

**Muestra continua $Unif(0,1)$ generada con MT19937:**

![MT19937 Uniforme](../images/p2/mt19937_uniforme.png)

La distribución observada es prácticamente plana en el rango $[0,1]$, sin concentraciones visibles de valores en ningún subintervalo.

## Resultados estadísticos

|     n |      min |      max |    media |     desv | autocorr_lag1 |
| ----: | -------: | -------: | -------: | -------: | ------------: |
| 30000 | 0.000013 | 0.999960 | 0.499131 | 0.289121 |     −0.002502 |

- $\mathbb{E}[X] = 0.5$
- $\sigma = \frac{1}{\sqrt{12}} \approx 0.288675$

La autocorrelación lag-1 es cercana a cero, lo que indica independencia entre valores consecutivos.

## Pruebas de hipótesis

Se aplicaron dos contrastes estadísticos sobre la muestra generada:

1. **Kolmogorov–Smirnov (KS):**
   $$
   H_0: X \sim Unif(0,1)
   $$
   Resultado: $p > 0.05$ → no se rechaza $H_0$.

2. **Chi-cuadrado (binned uniform):**
   Frecuencias observadas vs esperadas en 40 bines iguales sobre $[0,1]$.
   Resultado: $p > 0.05$ → no se rechaza $H_0$.

Ambas pruebas indican que la muestra generada es estadísticamente consistente con una distribución uniforme continua. Los resultados obtenidos demuestran que el método produce números pseudoaleatorios indistinguibles de una distribución $Unif(0,1)$ bajo las pruebas aplicadas.
