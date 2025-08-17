# Problema 1

Implementar los siguientes métodos de descenso gradiente (naïve = tamaño de paso $\alpha$ constante):

- Descenso gradiente naïve con dirección de descenso aleatoria
- Descenso máximo naïve
- Descenso gradiente de Newton, con Hessiano exacto
- Un método de gradiente conjugado (Fletcher-Reeves, Hestenes-Stiefel, Polak-Ribière)
- Método BFGS.

En cada uno de los métodos, su función debe recibir los siguientes argumentos:

- La función objetivo $f$.
- El gradiente de la función objetivo $df$.
- El hessiano $ddf$ (cuando sea necesario).
- Un punto inicial $x_0 \in \mathbb{R}^n$.
- El tamaño de paso $\alpha > 0$.
- El número máximo de iteraciones $maxIter$.
- La tolerancia $\varepsilon$, así como un criterio de paro.

Como resultado, sus algoritmos deben devolver: la mejor solución encontrada *best* (la última de las aproximaciones calculadas); la secuencia de iteraciones $x_k$; la secuencia de valores $f(x_k)$; la secuencia de errores en cada paso (según el error de su criterio de paro).

Además, es deseable indicar el número de iteraciones efectuadas por el algoritmo, y si se obtuvo o no convergencia del método.

## Funciones auxiliares

### Función `norm(...)`

Esta función la usaremos para calcular errores con norma midiendo la longitud del vector en un espacio vectorial.

### Función `projOrth(...)`

Dado que tenemos el gradiente, debemos ir al negativo ($-\nabla f(x)$) de este para encontrar una válida dirección de descenso, pero también podemos tomar otras direccioens siempre que formen un ángulo menor de $90°$ con el gradiente.

Entonces para generar otras direcciones, se necesita un vector ortogonal al gradiente y combinarlo con un angulo $\phi$. Esta es la principal función de `projOrth`, con esta función vamos a recibir:

- `u`: punto de partida que luego se proyectará (vector).
- `b_orth`: esto es un vector al que se quiere ser ortogonal.

En caso que b tenga un valor de 1, indica que es un vector; si es mayor será una colección de vectores y queremos proyectar `u` a esto para que sea ortogonal a todos.

El proceso es que se normalizará del vector `b_orth` obteniendo un vector unitario `b` luego restamos al vector enviado a su proyección sobre `b` para asegurar que `v` sea ortogonal a `b`:

$$
v \leftarrow v - (v \cdot b) b
$$

Por último, debemos devolver un vector unitario ortogonal al `b_orth` pero si el vector `u` estaba casi alineado con `b_orth`, entonces al quitarle la proyección se queda en algo casi nulo ($\|v\| \approx 0$), y al normalizar esto ocurrirá un error numérica ($v / \|v\|$), por lo que debemos hacer una validación previa para retornar el vector:

- Si $ \|v\| \approx 0$: devolvemos `v` sin normalizar (es decir, un vector casi nulo, aunque no sea unitario).
- Si $ \|v\| > 0$: podemos normalizar con seguridad y devolvemos el vector unitario $v / \|v\|$.

> **Nota:** `v` es una copia del vector de partida `u` para no modificar el valor original enviado.

Esto lo utilizamos ya que las direcciones de descenso distintas al gradiente podemos tomar una dirección que forme un ángulo con el gradiente y para esto necesitamos:

$$
d = \cos(\phi)(-\hat g) + \sin(\phi) v
$$

donde:

- $-\hat g$ es el gradiente negativo unitario.
- $v$ es un vector unitario ortogonal al gradiente.

## Descenso gradiente naïve con dirección de descenso aleatoria y Descenso máximo naïve

### Funcionamiento

Esta función implementa descenso por gradiente con paso constante ($\alpha$) y dirección que puede ser:

- **Steepest**: $d_k=-\nabla f(x_k)$ (si `phiMode="fixed", phi=0`).
- **Ángulo fijo**: combina $-\hat g$ con un vector ortogonal (si `phiMode="fixed", phi!=0`).
- **Aleatoria**: toma $\phi\sim U(lo,hi)$ y combina $-\hat g$ con un ortogonal (si `phiMode="random"`).

La actualización siempre es:

$$
x_{k+1}=x_k+\alpha\,d_k
$$

### Flujo interno

1. **Configurar modo/ángulo**
   Fusiona `extra` con defaults. Si `random`, usará $\phi\in(lo,hi)$. Si `fixed`, usa $\phi=$ `phiFixed`.

2. **Estado inicial**

   - Normaliza formas, evalúa $f(x_0)$ y el gradiente $g_0=\nabla f(x_0)$.
   - Guarda historia para métricas (para gráficas si $n=2$).

3. **Bucle de iteraciones (k=1…maxIter)**

   a. Seleccionar $\phi$ (aleatorio o fijo).

   b. Construir dirección $d_k$:

   - Si $\|g_k\|$ \~ 0 -> usar $d_k=-g_k$ (ya se está en crítico).
   - Si no:

     - $\hat g = g_k/\|g_k\|$.
     - $v=\text{projOrth}(z,\hat g)$ (unitario y ortogonal a $\hat g$).
     - $d_k=\cos\phi(-\hat g)+\sin\phi\,v$.

     > Esto implementa el “abanico” de direcciones de descenso: ángulo < $90^\circ$ con $-\nabla f$.

   c. Paso naïve: $x_{k+1}=x_k+\alpha d_k$.

   d. Cálculo de error según `stopCrit`:

   - `"grad"`: $\|\nabla f(x_{k+1})\|$
   - `"fx"`: $|f(x_{k+1})-f(x_k)|$
   - `"xAbs"`: $\|x_{k+1}-x_k\|$
   - `"xRel"`: $\|x_{k+1}-x_k\|/\max(1,\|x_{k+1}\|)$

   e. Registro & verbose: guarda $x_{k+1}$, $f$, errores, $\phi$, $\|g\|$, $\|step\|$; imprime si `verbose`.

   f. Paro: si `err ≤ tol` -> `converged=True` y sale; si no, continúa.

4. **Métricas finales**
   Construye `metrics` con etiqueta del método (según `phiMode`/`phi`), convergencia, iteraciones, $\| \nabla f \|$, tiempos e historia.

### Parámetros de entrada

1. **`f`**
   Función objetivo $f:\mathbb{R}^n\to\mathbb{R}$. Debe aceptar `np.array` y devolver escalar.

2. **`df`**
   Gradiente $\nabla f(x)$. Debe devolver `np.array` de shape `(n,)`.

3. **`x0`**
   Punto inicial `np.array` de shape `(n,)` (tipo float).

4. **`alpha`**
   Tamaño de paso constante $\alpha>0$.
   Grande ⇒ riesgo de divergencia; pequeño ⇒ lento.

5. **`maxIter`**
   Máximo de iteraciones (paro “duro”).

6. **`tol`**
   Tolerancia $\varepsilon>0$ (paro por precisión según `stopCrit`).

7. **`stopCrit`**
   Criterio de paro por tolerancia:

   - `"grad"`: $\|\nabla f(x_k)\|\le\varepsilon$
   - `"fx"`: $|f(x_k)-f(x_{k-1})|\le\varepsilon$
   - `"xAbs"`: $\|x_k-x_{k-1}\|\le\varepsilon$
   - `"xRel"`: $\|x_k-x_{k-1}\|/\max(1,\|x_k\|)\le\varepsilon$

8. **`normOrder`**
   Norma para medir gradiente/pasos/errores: `1`, `2` (default) o `np.inf`.

9. **`isPlottable`**
   `True` -> si $n=2$ guarda trayectoria para graficar.

10. **`randomState`**
    Semilla para reproducibilidad (afecta la dirección aleatoria y el muestreo de ángulos).

11. **`verbose`**
    `True` -> imprime resumen por iteración (`k`, `f(x_k)`, $\|\nabla f\|$, $\|step\|$, error, `phi`).

12. **`extra`** *(solo en `gradientDescentNaive` — los wrappers lo fijan internamente)*

    - `"phiMode"`: `"random"` (default) o `"fixed"`.
    - `"phi"`: ángulo fijo (radianes) si `"fixed"`; `0.0` ≡ *steepest descent*.
    - `"phiRange"`: `(lo, hi)` en radianes para `"random"`. Recom.: dentro de $(-π/2, π/2)$ para garantizar descenso.

> Nota: Los *wrappers*
>
> - `gradientDescentRandom(...)` fija `extra={"phiMode":"random"}` y **no exponen** `extra`.
> - `steepestDescent(...)` fija `extra={"phiMode":"fixed","phi":0.0}` y **no exponen** `extra`.
>   Ambos reciben el resto de parámetros (`alpha`, `maxIter`, `tol`, `stopCrit`, `normOrder`, `isPlottable`, `randomState`, `verbose`).

### Retornos

1. **`best`**

   Última aproximación $x_{k^*}$.

   - Tipo: `np.array` shape `(n,)`.

2. **`xs`**

   Secuencia de iterados $[x_0,\dots,x_{k^*}]$.

   - Tipo: `np.array` shape `(k^*+1, n)`.

3. **`fxs`**

   Valores de la función $[f(x_0),\dots,f(x_{k^*})]$.

   - Tipo: `np.array` shape `(k^*+1,)`.

4. **`errors`**

   Errores por iteración según `stopCrit` (grad, fx, xAbs, xRel).

   - Tipo: `np.array` shape `(k^*,)` — uno por paso realizado.

5. **`metrics`** (`dict`) — resumen para reporte/gráficas:

   - `method`: etiqueta del método usado (p.ej. “Steepest Descent (naive)” o “Gradient Descent (random direction naive)”).
   - `converged`: `True/False`.
   - `stopReason`: `"tolerance"` o `"maxIter"`.
   - `iterations`: $k^*$ (número de pasos realizados).
   - `finalX`: copia de `best`.
   - `finalFx`: $f(best)$.
   - `gradNorm`: $\|\nabla f(best)\|$ con `normOrder`.
   - `stepNorm`: $\|x_{k^*}-x_{k^*-1}\|$ (si $k^*>0$).
   - `approxError`: último error (según `stopCrit`).
   - `alpha`: tamaño de paso usado.
   - `timeSec`: tiempo total (segundos).
   - `history` (sub-dict con series):

     - `k`: array de iteraciones $[1,\dots,k^*]$.
     - `gradNorms`: $\|\nabla f(x_k)\|$ para $k=0,\dots,k^*$.
     - `stepNorms`: $\|x_k-x_{k-1}\|$ para $k=1,\dots,k^*$.
     - `approxErrors`: copia de `errors`.
     - `angles`: ángulo $\phi_k$ usado (si aplica).
     - `directions`: direcciones $d_k$ (si se guardan).
     - `xs2D`: trayectoria 2D (si `isPlottable` y $n=2$).
   - `seed`: `randomState` efectivo.

> Nota: `len(xs) = len(fxs) = k^*+1`, `len(errors) = len(stepNorms) = len(history['k']) = k^*`.
> Si el paro fue por tolerancia, `converged=True` y `stopReason="tolerance"`; si no, `"maxIter"`.
