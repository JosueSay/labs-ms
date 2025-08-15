# Interfaz común

## Parámetros de entrada

- `f`: función objetivo $f:\mathbb{R}^n\to\mathbb{R}$.
- `df`: gradiente $\nabla f$.
- `x0`: punto inicial (np.array shape $(n,)$).
- `alpha`: tamaño de paso constante $\alpha>0$.
- `maxIter`: máximo de iteraciones (criterio 1 de paro).
- `tol`: tolerancia $\varepsilon>0$ (para el criterio 2 de paro).
- `stopCrit`: criterio de paro por tolerancia. Uno de:
  - `"grad"`: $\|\nabla f(x_k)\|\le \varepsilon$
  - `"fx"`: $|f(x_{k})-f(x_{k-1})|\le \varepsilon$
  - `"xAbs"`: $\|x_{k}-x_{k-1}\|\le \varepsilon$
  - `"xRel"`: $\|x_{k}-x_{k-1}\|/\max(1,\|x_{k}\|)\le \varepsilon$
- `normOrder`: norma usada (1, 2 o `np.inf`) para medir errores/normas.
- `isPlottable`: bool para indicar si se recopila **trayectoria 2D** (solo se graficará si $n=2$).
- `randomState`: entero o `None` para reproducibilidad (afecta métodos con aleatoriedad).
- `verbose`: bool para activar mensajes/resumen.
- `extra`: dict opcional con parámetros específicos del método
  - **Random-direction GD**: `phiMode` (`"fixed"`/`"random"`), `phi` (ángulo fijo), `phiRange` (p.ej. `(-π/2, π/2)`).
  - **Newton**: `ddf` (Hessiano exacto) o *callable* que lo devuelva; `solveSystem` (`"solve"`/`"inv"`).
  - **Conjugate Gradient**: `betaRule` (`"FR"|"PR"|"HS"`), `restartEvery` (entero opcional).
  - **BFGS**: `H0` (aprox. inicial de la inversa del Hessiano), `skipUpdateIf` (umbral de curvatura).

> Nota: `ddf` se pasará dentro de `extra` solo cuando el método lo requiera.

## Retornos

Tupla:

1. `best`: última aproximación $x_{k^*}$.
2. `xs`: lista/array de aproximaciones $[x_0, \dots, x_{k^*}]$.
3. `fxs`: lista/array de valores $[f(x_0), \dots, f(x_{k^*})]$.
4. `errors`: lista/array con el **error** según `stopCrit` elegido en cada iteración.
5. `metrics`: `dict` con al menos:
   - `method`: nombre del método (string).
   - `converged`: `True/False`.
   - `stopReason`: `"tolerance"` o `"maxIter"`.
   - `iterations`: número de iteraciones realizadas.
   - `finalX`: copia de `best`.
   - `finalFx`: $f(best)$.
   - `gradNorm`: $\|\nabla f(best)\|$.
   - `stepNorm`: $\|x_{k^*} - x_{k^*-1}\|$ (si $k^* > 0$).
   - `approxError`: error final según `stopCrit`.
   - `alpha`: tamaño de paso usado.
   - `timeSec`: tiempo total de ejecución.
   - `history`: sub-dict con series para graficar:
     - `gradNorms`: $\|\nabla f(x_k)\|$.
     - `stepNorms`: $\|x_k-x_{k-1}\|$.
     - `approxErrors`: copia de `errors`.
     - `angles` (si aplica: ángulo usado en cada paso).
     - `directions` (si aplica: dirección $d_k$ usada).
     - `xs2D`: trayectoria en 2D (si `isPlottable` y $n=2$).
   - `seed`: `randomState` efectivo.

## Criterios de paro

- **Criterio 1 (dureza):** `iterations >= maxIter` -> paro por límite de iteraciones.
- **Criterio 2 (precisión):** el indicado por `stopCrit` y `tol` -> paro por tolerancia.

Se registra cuál ocurrió primero en `metrics.stopReason`.

<!-- ## Nombres de funciones (camelCase)

- `gradientDescentRandom(...)` — descenso con **dirección de descenso aleatoria** (o ángulo fijo si `phiMode="fixed"`).
- `steepestDescent(...)` — descenso máximo.
- `newtonDescent(...)` — Newton con Hessiano exacto.
- `conjugateGradientDescent(...)` — Fletcher–Reeves / Polak–Ribière / Hestenes–Stiefel vía `betaRule`.
- `bfgsDescent(...)` — BFGS.

> Todas comparten la interfaz/retornos anteriores; solo difieren en cómo calculan la **dirección $d_k$** antes de actualizar $x_{k+1}=x_k+\alpha d_k$. -->

## Consideraciones para gráficas y comparación

- Con `history` podremos graficar:
  - $f(x_k)$ vs. iteración.
  - $\|\nabla f(x_k)\|$ vs. iteración.
  - Error de aproximación vs. iteración.
  - Trayectoria $(x_k)$ en el plano para $n=2$ (si `isPlottable=True`), sobre contornos de $f$.
