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

## Parámetros de entrada

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

## Retornos

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

   - `method`: etiqueta del método usado.
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
   - `seed`: `randomState` efectivo.
   - `history` (sub-dict con series):

     - `k`: array de iteraciones $[1,\dots,k^*]$.
     - `gradNorms`: $\|\nabla f(x_k)\|$ para $k=0,\dots,k^*$.
     - `stepNorms`: $\|x_k-x_{k-1}\|$ para $k=1,\dots,k^*$.
     - `approxErrors`: copia de `errors`.
     - `angles`: ángulo $\phi_k$ usado (si aplica).
     - `directions`: direcciones $d_k$ (si se guardan).
     - `xs2D`: trayectoria 2D (si `isPlottable` y $n=2$).

> Nota: `len(xs) = len(fxs) = k^*+1`, `len(errors) = len(stepNorms) = len(history['k']) = k^*`.
> Si el paro fue por tolerancia, `converged=True` y `stopReason="tolerance"`; si no, `"maxIter"`.

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

   f. Paro: si `err <= tol` -> `converged=True` y sale; si no, continúa.

4. **Métricas finales**
   Construye `metrics` con etiqueta del método (según `phiMode`/`phi`), convergencia, iteraciones, $\| \nabla f \|$, tiempos e historia.

### Parámetros de entrada

1. **`extra`** *(solo en `gradientDescentNaive` — los wrappers lo fijan internamente)*

    - `"phiMode"`: `"random"` (default) o `"fixed"`.
    - `"phi"`: ángulo fijo (radianes) si `"fixed"`; `0.0` ≡ *steepest descent*.
    - `"phiRange"`: `(lo, hi)` en radianes para `"random"`. Recom.: dentro de $(-π/2, π/2)$ para garantizar descenso.

> Nota: Los *wrappers*
>
> - `gradientDescentRandom(...)` fija `extra={"phiMode":"random"}` y **no exponen** `extra`.
> - `steepestDescent(...)` fija `extra={"phiMode":"fixed","phi":0.0}` y **no exponen** `extra`.
>   Ambos reciben el resto de parámetros (`alpha`, `maxIter`, `tol`, `stopCrit`, `normOrder`, `isPlottable`, `randomState`, `verbose`).

### Retornos

- `metrics.method`:

  - `"Steepest Descent (naive)"` (si `phiMode="fixed", phi=0`)
  - `"Gradient Descent (random direction naive)"` (si `phiMode="random"`)
  - `"Gradient Descent (fixed-angle naive)"` (si `phiMode="fixed", phi≠0`)
- `metrics.history.angles`: **array** con $\phi_k$ por iteración.
- Lo demás: **usa los retornos comunes**.

## Descenso gradiente de Newton, con Hessiano exacto

### Funcionamiento

El método de Newton minimiza $f$ usando un*modelo cuadrático local en $x_k$:

$$
m_k(d)=f(x_k)+\nabla f(x_k)^\top d+\tfrac12\, d^\top \nabla^2 f(x_k)\, d.
$$

Minimizar $m_k$ da la dirección de Newton como solución del sistema

$$
\nabla^2 f(x_k)\, d_k=-\nabla f(x_k).
$$

Luego se actualiza con paso constante $\alpha$ (típicamente $\alpha=1$):

$$
x_{k+1}=x_k+\alpha\, d_k.
$$

- Si el Hessiano es definido positivo (PD) en el entorno del mínimo, $d_k$ suele ser dirección de descenso ($\nabla f(x_k)^\top d_k<0$) y la convergencia cerca de la solución es cuadrática.
- Si el Hessiano es indefinido/mal condicionado, $d_k$ puede no ser de descenso; en ese caso se verifica $g^\top d<0$ y, si falla, se cambia a $d=-g$ (steepest) como respaldo para asegurar descenso.
- La dirección se obtiene resolviendo el sistema lineal; no se invierte la matriz salvo que se pida explícitamente.

### Flujo interno

1. **Validaciones de `extra`**

   - Requiere `extra["ddf"]`: `ddf(x)` o matriz constante $n\times n$.
   - `solveSystem{"solve","inv"}` (por defecto `"solve"`).

2. **Estado inicial**

   - Convierte `x0` a vector `float` de shape `(n,)`.
   - Evalúa $f(x_0)$ y $g_0=\nabla f(x_0)$.
   - Inicializa contenedores de historia (para métricas y, si $n=2$, trayectoria 2D).
   - `verbose` imprime resumen de $k=0$.

3. **Bucle (k = 1…maxIter)**

   a. **Hessiano**: $H_k=$ `ddf(x)` (o matriz fija).

   b. **Dirección de Newton**: resuelve $H_k d=-g_k$.

   - Si `solveSystem="solve"` usa `np.linalg.solve`.
   - Si falla (singular/indefinida), usa pseudo-inversa como respaldo.

   c. **Chequeo de descenso**: calcula $g_k^\top d$.

   - Si no es finito o $\ge 0$, cambia a $d=-g_k$.

   d. **Actualización**: `x_new = x + alpha*d`, `fx_new = f(x_new)`, `step = x_new - x`.

   e. **Error** según `stopCrit`:

   - `"grad"`: $\|\nabla f(x_{k+1})\|$
   - `"fx"`: $|f(x_{k+1})-f(x_k)|$
   - `"xAbs"`: $\|x_{k+1}-x_k\|$
   - `"xRel"`: $\|x_{k+1}-x_k\|/\max(1,\|x_{k+1}\|)$

   f. **Registro & verbose**: guarda series (gradNorms, stepNorms, errors, directions, …) e imprime si `verbose`.

   g. **Paro por tolerancia**: si `err <= tol`, marca `converged=True` y termina.

   h. **Avance**: asigna `x <- x_new`, `g <- df(x_new)` y continúa.

4. **Cierre y métricas**

   - Calcula tiempo total, número de iteraciones $k^*$ y arma `metrics` con:
     `method="Newton (exact Hessian, naive step)"`, `converged`, `stopReason`, `iterations`, `finalX`, `finalFx`, `gradNorm`, `stepNorm`, `approxError`, `alpha`, `timeSec`, `seed`, `solveSystem`, e `history` (sin ángulos: `angles=None`).

### Parámetros de entrada

1. **`extra`**

    - **`ddf`** *(requerido)*: Hessiano exacto. Puede ser:

      - *callable* `ddf(x)` -> retorna matriz $n\times n$.
      - Matriz fija `np.ndarray` $n\times n$ (solo si es constante).
    - **`solveSystem`**: `"solve"` (default) | `"inv"`.

      - `"solve"` usa `np.linalg.solve(H, -g)` (mejor numéricamente).
      - `"inv"` usa $d=-H^{-1}g$ (menos recomendado).

> Notas:
>
> - La implementación verifica $g^\top d<0$; si no se cumple (Hessiano no PD o mal condicionado), **cambia a `d=-g`** como respaldo para asegurar dirección de descenso.
> - Si el sistema con $H$ falla, se usa **pseudo-inversa** como *fallback*.

### Retornos

- `metrics.method`: `"Newton (exact Hessian, naive step)"`.
- `metrics.solveSystem`: `"solve"` o `"inv"` (cómo se resolvió $H d=-g$).
- `metrics.history.angles`: **`None`** (Newton no usa ángulos).
- Lo demás: **usa los retornos comunes**.

## Gradiente Conjugado (FR / PR / PR+ / HS)

### Funcionamiento

El Gradiente Conjugado no lineal (GC) acelera el descenso usando direcciones que combinan la información actual y la pasada:

$$
d_k = -g_k + \beta_k\, d_{k-1}, \quad g_k=\nabla f(x_k).
$$

Luego actualiza con paso constante (naïve):

$$
x_{k+1}=x_k+\alpha\, d_k.
$$

La elección de $\beta_k$ define la variante:

- **FR (Fletcher–Reeves):** $\displaystyle \beta^{FR}_{k+1}=\frac{\langle g_{k+1},g_{k+1}\rangle}{\langle g_k,g_k\rangle}$.
- **PR (Polak–Ribiere):** $\displaystyle \beta^{PR}_{k+1}=\frac{\langle g_{k+1},\, g_{k+1}-g_k\rangle}{\langle g_k,g_k\rangle}$.
- **PR+ (recortado):** $\beta^{PR+}_{k+1}=\max\{0,\beta^{PR}_{k+1}\}$.
- **HS (Hestenes–Stiefel):** $\displaystyle \beta^{HS}_{k+1}=\frac{\langle g_{k+1},\, y_k\rangle}{\langle d_k,\, y_k\rangle}$, $y_k=g_{k+1}-g_k$.

### Flujo interno

1. **Inicialización:**

   $x_0$ dado, $g_0=\nabla f(x_0)$, $d_0=-g_0$. Registrar historia.

2. **Iteración $k=1,\dots$:**

   a. **Paso naïve:** $x_{k}=x_{k-1}+\alpha\, d_{k-1}$.

   b. **Evaluar:** $f(x_k)$, $g_k=\nabla f(x_k)$ y el **error** según `stopCrit`.

   c. **Paro por tolerancia:** si `err <= tol`, detener.

   d. **Cálculo de $\beta$:** FR/PR/PR+/HS (con estabilizador en denominadores).

   e. **Reinicio opcional:** cada `restartEvery` pasos ⇒ $\beta=0$ (dirección = $-g_k$).

   f. **Asegurar descenso (opcional):** si `g_k^T d_k >= 0` ⇒ reiniciar $d_k=-g_k$.

### Parámetros de entrada (específicos de GC)

En `extra`:

- **`betaRule`**: `"FR"` (default) | `"PR"` | `"PR+"` | `"HS"`.
- **`restartEvery`**: `int` o `None`. Si es entero $m>0$, reinicia cada $m$ pasos (pone $d=-g$).
- **`denomEps`**: `float` (default `1e-15`). Pequeño $\epsilon$ para evitar divisiones numéricamente inestables.
- **`ensureDescent`**: `bool` (default `True`). Si $g^\top d \ge 0$, fuerza reinicio a $d=-g$.

> El resto de entradas (`f, df, x0, alpha, maxIter, tol, stopCrit, normOrder, isPlottable, randomState, verbose`) son **comunes**.

### Retornos

Usa los **retornos comunes** y añade:

- `metrics.method`: `"Nonlinear Conjugate Gradient (naive, {betaRule})"`.
- `metrics.betaRule`: regla seleccionada.
- `metrics.restartEvery`: valor usado (o `None`).
- `metrics.restarts`: número de reinicios efectuados.
- `metrics.ensureDescent`: `True/False`.
- `metrics.history.betas`: serie de $\beta_k$.
- `metrics.history.angles`: `None` (GC no usa ángulos).
- `metrics.history.directions`: direcciones $d_k$ registradas.
