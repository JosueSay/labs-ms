# Optimización estocástica

## Búsqueda Local

### 1. Introducción a la Optimización Estocástica

En el estudio de la **optimización**, hemos visto dos grandes tipos de algoritmos:

1. **Algoritmos tipo gradiente** para funciones continuas diferenciables.

   * En este caso, el **gradiente indica la dirección de movimiento** hacia la solución óptima.
2. **Algoritmos para casos discretos/estocásticos**, como los **algoritmos genéticos (GA)** o el **simplex**.

   * En estos, el gradiente no siempre existe o no es aplicable, por lo que se emplean métodos de búsqueda inspirados en la evolución o en reglas heurísticas.

Los **GA** son un ejemplo paradigmático de algoritmos estocásticos para optimización discreta.

### 2. Concepto de Vecindad

Un concepto clave en **búsqueda local** es la **vecindad**.

* Imaginemos un **grid** o un **grafo** que representa configuraciones posibles.
* A partir de un estado o celda, definimos la vecindad como el **conjunto de soluciones cercanas** a dicho estado.

Ejemplo en un grid:

* Conexión de **4 vecinos**: arriba, abajo, izquierda, derecha.
* Conexión de **8 vecinos**: incluyendo diagonales.

Esto puede representarse con métricas como:

* **Distancia Manhattan**: |x1 − x2| + |y1 − y2|.
* **Distancia Euclidiana**: √((x1 − x2)² + (y1 − y2)²).
* O cualquier métrica adaptada al problema.

Definición formal de vecindad con radio *r*:

$$
D_r(x) = \{ y \in X : d(x,y) \leq r \}
$$

donde $d(x,y)$ es la métrica de distancia utilizada.

En un **grafo**, la vecindad puede definirse como los **nodos alcanzables en <= r aristas** desde el nodo actual.

### 3. Intensificación y Diversificación

En algoritmos de búsqueda local, distinguimos dos estrategias fundamentales:

* **Intensificación**

  * Busca **explotar** la vecindad de una solución prometedora.
  * Si tenemos una configuración $x$, generamos soluciones en su entorno definido por un radio $r$.
  * Esto fuerza al algoritmo a **buscar soluciones cercanas** y mejorar localmente.

* **Diversificación**

  * Busca **explorar** nuevas regiones del espacio de búsqueda.
  * Después de varias iteraciones de intensificación, se da un **salto aleatorio** hacia otra región, evitando quedar atrapados en mínimos locales.

En la práctica, un buen algoritmo alterna entre **explotación (intensificación)** y **exploración (diversificación)**.

### 4. Intensificación en Algoritmos

* En algoritmos genéticos (GA):
  Se puede forzar a que los operadores de cruce y mutación generen individuos **dentro de la vecindad de soluciones previas**.
  Ejemplo: limitar que los descendientes estén a una distancia <= r de sus padres.

* En búsqueda continua:
  Si tenemos una función f(x) y caemos en un punto x, podemos definir un **intervalo alrededor de x** en el que restringimos los próximos movimientos.

  * En $\mathbb{R}^n$, esto se traduce en un **hiperesfera de radio r**.

Esto aplica tanto para **espacios discretos como continuos**.

### 5. Hill-Climbing: Motivación

El método **Hill-Climbing** surge como estrategia para evitar el estancamiento en **mínimos locales**.

* El **descenso por gradiente puro** tiende a converger al mínimo local más cercano.
* Hill-Climbing añade un componente estocástico: **saltos aleatorios** que permiten escapar de valles y explorar nuevas regiones.

De este modo, el algoritmo puede "escalar montañas" y no quedarse atrapado en una solución subóptima.

#### Intuición

1. El algoritmo sigue pasos guiados por el gradiente (intensificación).
2. Cada cierto número de iteraciones, ejecuta un **salto aleatorio** (diversificación).
3. Si encuentra un punto mejor, actualiza la mejor solución conocida.

### 6. Aplicaciones del Hill-Climbing Estocástico

* Optimización de funciones con **muchos mínimos locales**.
* Escenarios donde el **gradiente existe pero no es suficiente** para escapar de valles.
* Extensión a algoritmos evolutivos:

  * Permite que individuos exploren soluciones fuera de la vecindad inmediata.

Este enfoque se utiliza en:

* Machine Learning (ajuste de hiperparámetros).
* Inteligencia Artificial (búsqueda en espacios de estados).
* Diseño de redes, rutas y problemas combinatorios.

### 7. Implementación: Hill-Climbing 1D

A continuación, se presenta la implementación en Python del algoritmo Hill-Climbing continuo, combinando **descenso por gradiente** con **saltos aleatorios**:

```python
import numpy as np

# Método Hill-Climbing Continuo: grad descent + random jumps
def HillClimbing1D(x0, f, df, alpha=0.1, maxI=500, maxSched=50, radius=1, d=2):
    iters = 0
    fin = 0
    convergence = 0
    x = x0

    approx = []      # xk
    values = []      # f(xk)
    grads = []       # df(xk)
    best_list = []   # mejores x encontrados
    fbest_list = []  # mejores evaluaciones f(x)

    approx.append(x)
    values.append(f(x0))
    grads.append(df(x0))
    best_list.append(x0)
    fbest_list.append(f(x))

    best = x0
    best_eval = f(best)

    # ciclo principal
    while fin == 0:
        # (1) maxSched pasos de descenso de gradiente
        for j in range(0, maxSched):
            oldx = x
            oldalpha = alpha
            gr = df(oldx)
            x = oldx - alpha * gr
            fx = f(x)
            dfx = df(x)

            approx.append(x)
            values.append(fx)
            grads.append(dfx)

            # check for new best solution
            if fx < best_eval:
                # guardar nuevo mejor punto
                best, best_eval = x, fx
                # imprimir progreso
                print('%s f(%s) = %.5f' % (str(iters).zfill(d), best, best_eval))

            best_list.append(best)
            fbest_list.append(best_eval)

        # (2) un paso aleatorio
        x = oldx + radius * (2 * np.random.rand() - 1)
        fx = f(x)
        dfx = df(x)

        # check for new best solution
        if fx < best_eval:
            best, best_eval = x, fx
            print('%s f(%s) = %.5f' % (str(iters).zfill(d), best, best_eval))

        iters += 1
        if iters >= maxI:
            fin = 1

    return approx, values, grads, best_list, fbest_list
```

## Enfriamiento Simulado (Simulated Annealing)

El **enfriamiento simulado** es un algoritmo inspirado en un proceso físico de la metalurgia.
En la práctica, cuando se calientan aleaciones metálicas a altas temperaturas y luego se enfrían de manera controlada hasta temperaturas muy bajas, los átomos se reacomodan a nivel químico. Este reacomodo genera estructuras más rígidas y resistentes. Dicho proceso se repite varias veces para mejorar la calidad del material.

La idea en optimización es **imitar este proceso de enfriamiento**, lo que da origen al **recocido simulado** (*simulated annealing* en inglés). Aunque su nombre pueda sonar coloquial (como "una olla de frijoles"), en realidad describe un método muy poderoso para encontrar soluciones óptimas en problemas complejos.

### ¿Qué significa enfriar en un problema de optimización?

Así como en la metalurgia el calor permite explorar diferentes configuraciones atómicas, en optimización el "calor" corresponde a la **exploración de soluciones**.
Al inicio, el algoritmo debe **explorar mucho** (hacer muchos saltos aleatorios, incluso hacia soluciones peores), mientras que al final debe **intensificar** (buscar refinadamente cerca de las mejores soluciones encontradas).

Se puede visualizar como un itinerario:

```bash
^
|    |    |
|    |    |
|    |    |
|    |    |
|    |    |
-----|----|----->  (Iteraciones)
```

* **Parte izquierda (inicio):** explorar mucho, intensificar poco.
* **Parte media:** explorar e intensificar en proporciones balanceadas.
* **Parte derecha (final):** explorar poco e intensificar mucho.

En resumen:

* **Explorar ++, Intensificar –** (inicio).
* **Explorar +, Intensificar +** (medio).
* **Explorar –, Intensificar ++** (final).

### ¿Cómo se acepta o rechaza un salto?

En este método, los saltos representan cambios de una solución a otra.

* Un **buen salto** ocurre cuando la nueva solución es mejor (menor energía).
* Un **mal salto** ocurre cuando la nueva solución es peor (mayor energía).

La regla de aceptación se basa en una **probabilidad de aceptación** que decae conforme avanza el tiempo:

$$
\mathbb{P}(\text{aceptación de una peor solución}) = \exp\left(-\frac{\Delta E}{k\,t}\right), \tag{1}
$$

donde:

* $\Delta E = f(\text{next}) - f(\text{current})$ es la diferencia de energía (qué tanto mejora o empeora la nueva solución respecto a la actual).
* $t = t(i)$ es la función de temperatura, que disminuye con las iteraciones (schedule).
* $k > 0$ es la **constante de Boltzmann**.

La expresión (1) corresponde al **criterio de Metropolis**, y su distribución de probabilidad es conocida en física como la **distribución de Boltzmann**.

### Ejemplo en pseudocódigo

```python
if delta_E < 0:  
    # Buen salto: mejora la solución
    current = x_k+1
else:
    # Mal salto: se acepta con probabilidad P
    if random() < exp(-delta_E / (k * T_i)):
        current = x_k+1
```

En este esquema:

* Si la nueva solución es mejor, siempre se acepta.
* Si es peor, puede aceptarse con cierta probabilidad que disminuye a medida que baja la temperatura $T_i$.
* Este mecanismo evita quedarse atrapado en mínimos locales demasiado pronto.

Se mantiene además un registro del **mejor valor encontrado (best)** a lo largo de las iteraciones.

### ¿Cómo disminuye la temperatura?

El algoritmo comienza con una **temperatura inicial $T_0$** y la reduce gradualmente según una regla llamada *schedule* o **itinerario de enfriamiento**.

Existen varias estrategias:

1. **Lineal:**

   $$
   t_{i+1} = t_i - \alpha, \quad \alpha > 0
   $$

   La temperatura baja en línea recta, con una pendiente constante.

2. **Geométrica:**

   $$
   t_{i+1} = \alpha \, t_i, \quad 0 < \alpha < 1
   $$

   La temperatura decrece exponencialmente. Se detiene cuando $t_i$ es menor que una tolerancia.

3. **Slow:**

   $$
   t_{i+1} = \frac{1}{1+\beta \, t_i}, \quad \beta > 0
   $$

   La disminución es más lenta gracias al parámetro $\beta$.

4. **Fast:**

   $$
   t_{i+1} = \frac{T_0}{i+1}
   $$

   La temperatura baja rápido, de forma hiperbólica.

### ¿Qué es lo esencial del enfriamiento simulado?

El corazón del método está en **cómo se define el esquema de enfriamiento**.
Este esquema determina la probabilidad de aceptar o rechazar soluciones peores:

$$
P = e^{-\Delta E / T_i}.
$$

* Al inicio ($T_i$ grande), la probabilidad es alta -> se aceptan muchos saltos malos.
* Al final ($T_i$ pequeña), la probabilidad es baja -> se aceptan muy pocos saltos malos.

Esto permite primero **explorar** y luego **explotar** intensivamente el espacio de soluciones, logrando un equilibrio entre búsqueda global y refinamiento local.

### Ejemplo con código

```python
import numpy as np

def _reflect(x, lo, hi):
    """Proyección por reflexión a [lo, hi] (vectorizada, sin sesgo en bordes)."""
    w = hi - lo
    y = (x - lo) % (2.0 * w)
    y = np.where(y > w, 2.0 * w - y, y)
    return lo + y

def simulated_annealing(f, x0, bounds, n_iter=1000, alpha=0.1, T0=1.0, seed=None):
    """
    f      : función objetivo -> float
    x0     : punto inicial (vector)
    bounds : array Nx2 con [lo, hi] por dimensión
    n_iter : iteraciones
    alpha  : tamaño de paso relativo (0<alpha<=1)
    T0     : temperatura inicial
    """
    rng = np.random.default_rng(seed)
    bounds = np.asarray(bounds, dtype=float)
    lo, hi = bounds[:, 0], bounds[:, 1]
    dim = len(lo)

    # inicial: forzamos dentro de límites
    curr = _reflect(np.asarray(x0, dtype=float), lo, hi)
    curr_eval = float(f(curr))

    best, fbest = curr.copy(), curr_eval
    path_x, path_f = [curr.copy()], [curr_eval]

    for i in range(n_iter):
        # candidato (aún no sabemos si es mejor)
        step = rng.normal(size=dim) * alpha * (hi - lo)
        cand = _reflect(curr + step, lo, hi)  # nunca sale del intervalo
        cval = float(f(cand))

        # guardar mejor global
        if cval < fbest:
            best, fbest = cand.copy(), cval

        # temperatura "fast": T = T0/(i+1)
        T = T0 / (i + 1.0)

        # criterio de aceptación de Metrópolis
        diff = cval - curr_eval
        if diff <= 0.0 or rng.random() < np.exp(-diff / T):
            curr, curr_eval = cand, cval  # movernos

        path_x.append(curr.copy())
        path_f.append(curr_eval)

    return best, fbest, np.asarray(path_x), np.asarray(path_f)
```
