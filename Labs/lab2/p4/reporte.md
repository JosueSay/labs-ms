# Problema 4

Implementar en Python los tres algoritmos vistos en clase para hallar los ceros de una función $f : [a, b] \rightarrow \mathbb{R}$

- método de bisección
- método de la secante
- método de Newton-Raphson

Como parámetros, sus algoritmos deben recibir la función $f$, la derivada $df$ (en el caso de Newton), el intervalo $[a, b]$ o el punto inicial de búsqueda $x_0 \in \mathbb{R}$. Así como los criterios de paro `maxIter` y `tol > 0`.

Para la salida, sus funciones deben devolver la lista de aproximaciones realizadas y el valor de punto $x^*$ donde se encontró el cero.

## Método de Bisección

**Función utilizada (ecuación de actualización):**

$$
x = \frac{a + b}{2}
$$

**Parámetros de entrada:**

- `f`: función a evaluar
- `a, b`: extremos del intervalo inicial
- `maxIter`: número máximo de iteraciones
- `tol`: tolerancia para el criterio de paro
- `verbose`: indicador opcional para mostrar el proceso iterativo

**Valor de retorno:**
Se devuelve un diccionario con las siguientes claves:

- `converged`: indica si el método alcanzó la tolerancia
- `root`: aproximación final de la raíz
- `fAtRoot`: valor de la función en la raíz
- `iterations`: número de iteraciones realizadas
- `approximations`: lista de todas las aproximaciones intermedias
- `error`: error estimado en la última iteración
- `message`: mensaje descriptivo del estado final

**Validación:**
Se verifica que exista un cambio de signo en el intervalo inicial, es decir:

$$
f(a) \cdot f(b) < 0
$$

Si no se cumple, el método se detiene inmediatamente.

**Criterio de paro:**
Se evalúa si el tamaño del intervalo es menor que la tolerancia:

$$
|b - a| < \text{tol}
$$

Esta condición es evaluada en cada iteración. Además se tiene el criterio de paro si se llega a la cantidad de`maxIter` enviado.

## Método de la Secante

**Función utilizada (ecuación de actualización):**

$$
x_{k+1} = \frac{x_{k-1} \cdot f(x_k) - x_k \cdot f(x_{k-1})}{f(x_k) - f(x_{k-1})}
$$

**Parámetros de entrada:**

- `f`: función a evaluar
- `x0, x1`: dos puntos iniciales
- `maxIter`: número máximo de iteraciones
- `tol`: tolerancia para el criterio de paro
- `verbose`: indicador opcional para imprimir el proceso

**Valor de retorno:**
Se retorna un diccionario con:

- `converged`: si se alcanzó la tolerancia
- `root`: aproximación final de la raíz
- `fAtRoot`: valor de la función en la raíz
- `iterations`: número de iteraciones realizadas
- `approximations`: lista de aproximaciones sucesivas
- `error`: diferencia entre las dos últimas aproximaciones
- `message`: descripción del resultado final

**Validación:**
Se valida que la diferencia entre los valores funcionales no sea cero, es decir:

$$
f(x_k) - f(x_{k-1}) \neq 0
$$

> Es decir que sea diferenciable $f'(x_k) \neq 0$

**Criterio de paro:**
Se verifica si la diferencia entre dos iteraciones consecutivas es menor que la tolerancia:

$$
|x_{k+1} - x_k| < \text{tol}
$$

Además se tiene el criterio de paro si se llega a la cantidad de`maxIter` enviado.

## Método de Newton-Raphson

**Función utilizada (ecuación de actualización):**

$$
x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}
$$

**Parámetros de entrada:**

- `f`: función a evaluar
- `df`: derivada de la función
- `x0`: valor inicial
- `maxIter`: máximo número de iteraciones
- `tol`: tolerancia para el criterio de paro
- `verbose`: indicador opcional de impresión

**Valor de retorno:**
El resultado es un diccionario con:

- `converged`: si se alcanzó la tolerancia
- `root`: valor aproximado de la raíz
- `fAtRoot`: valor de la función en la raíz
- `iterations`: número de iteraciones realizadas
- `approximations`: secuencia de valores generados
- `error`: diferencia entre las dos últimas aproximaciones
- `message`: texto explicativo del estado final

**Validación:**
Se verifica que la derivada no se anule en el punto de evaluación:

$$
f'(x_k) \neq 0
$$

Esto asegura que la tangente esté bien definida.

**Criterio de paro:**
Se detiene el proceso cuando la diferencia entre iteraciones es menor que la tolerancia:

$$
|x_{k+1} - x_k| < \text{tol}
$$

Además se tiene el criterio de paro si se llega a la cantidad de`maxIter` enviado.
