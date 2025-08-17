# Método BFGS

## Funcionamiento

Este método no calcula el Hessiano $\nabla^2 f$ ni su inversa, sino que mantiene y actualiza una aproximación de la inversa del Hessiano $H_k\approx(\nabla^2 f(x_k))^{-1}$. Con esa $H_k$ arma el paso “tipo Newton”

$$
d_k = -\,H_k\,\nabla f(x_k),
\qquad x_{k+1}=x_k+\alpha\,d_k.
$$

La actualización de $H_k$ se diseña para cumplir la ecuación de la secante:

$$
H_{k+1}\,y_k = s_k,
\quad s_k:=x_{k+1}-x_k,\quad y_k:=\nabla f(x_{k+1})-\nabla f(x_k),
$$

y para conservar simetría y buena curvatura. La forma canónica de BFGS para la inversa del Hessiano es:

$$
H_{k+1}
= \big(I-\rho_k s_k y_k^\top\big)\,H_k\,\big(I-\rho_k y_k s_k^\top\big)\;+\;\rho_k\, s_k s_k^\top,
\qquad \rho_k=\frac{1}{y_k^\top s_k}.
$$

Equivalente para la aproximación del Hessiano $B_k\approx \nabla^2 f$:

$$
B_{k+1}
= B_k - \frac{B_k s_k s_k^\top B_k}{s_k^\top B_k s_k}
+ \frac{y_k y_k^\top}{y_k^\top s_k}.
$$

Estas expresiones y su derivación (a partir de DFP y la condición de secante) están en las notas del curso.

> Importante: si se usa una búsqueda en línea que cumpla condiciones de Wolfe (con $0<c_2<1$), entonces se garantiza $y_k^\top s_k>0$, lo que preserva definición positiva de $H_{k+1}$ siempre que $H_k\succ0$. Con paso constante esto no está garantizado y conviene **saltar** la actualización si $y_k^\top s_k$ es pequeño/no positivo.

## Pseudocódigo (versión con $\alpha$ constante)

1. Dado $x_0, H_0\succ 0$.
2. Para $k=0,1,\dots$ hasta paro:

   * $g_k\leftarrow \nabla f(x_k)$
   * $d_k\leftarrow -H_k g_k$
   * $x_{k+1}\leftarrow x_k+\alpha d_k$
   * $s_k\leftarrow x_{k+1}-x_k$, $y_k\leftarrow \nabla f(x_{k+1})-\nabla f(x_k)$
   * Si $y_k^\top s_k \le \text{skipUpdateIf}$: $H_{k+1}\leftarrow H_k$ (skip)
     Si no: $H_{k+1}\leftarrow (I-\rho s_ky_k^\top)H_k(I-\rho y_ks_k^\top)+\rho s_k s_k^\top$, $\rho=1/(y_k^\top s_k)$
   * Registrar métricas; verificar criterio de paro.
     *(La versión “clásica” recomienda **line search** para obtener buenas propiedades teóricas; aquí respetamos el enunciado Naïve con $\alpha$ constante.)*

## Flujo

El cálculo de la dirección cambia (usa $H_k$), pero la actualización de $x$ y los criterios de paro son los mismos:

1. **Inicialización**

   * $x_0$: dado.
   * $H_0$: identidad o escalado $H_0=\gamma I$ con $\gamma=\frac{s_{k-1}^\top y_{k-1}}{y_{k-1}^\top y_{k-1}}$ (si ya hay un par) — el escalado inicial mejora mucho el desempeño.

2. **En cada iteración $k$**

   a. $g_k=\nabla f(x_k)$

   b. **Dirección**: $d_k=-H_k g_k$

   c. **Paso**: $x_{k+1}=x_k+\alpha,d_k$

   d. **Nuevos pares**: $s_k=x_{k+1}-x_k$, $y_k=g_{k+1}-g_k$

   e. **Chequeo de curvatura**: si $y_k^\top s_k\le \text{umbral}$ (pej. $10^{-12}$), **no actualizar** $H_k$ (mantener $H_{k+1}=H_k$).

   f. Si pasa el chequeo: **actualizar BFGS**

   $$
   H_{k+1}
   = \big(I-\rho s y^\top\big)H_k\big(I-\rho y s^\top\big)+\rho ss^\top,\;\rho=\tfrac{1}{y^\top s}.
   $$

   g. Registrar historia (norma de gradiente, norma del paso, error según `stopCrit`, etc.).

3. **Paro**

   * Por `tol` (grad/fx/xAbs/xRel) o por `maxIter`.

> El algoritmo y las fórmulas (incluidas las de DFP y la relación entre BFGS/DFP) están detallados en las notas: se derivan de imponer la secante y aplicar identidades tipo Sherman–Morrison–Woodbury para obtener las versiones en $H$ o en $B$.

## Cuándo usar

* Cuando calcular/almacenar el Hessiano exacto es caro o inestable, y la dimensión no es gigantesca.
* Cuando *steepest descent* resulta demasiado lento y Newton exacto no es viable.
* Si la dimensión es muy grande, considera L-BFGS (memoria limitada).

## Ventajas

* **No requiere Hessiano** ni invertir matrices grandes en cada iteración.
* **Rendimiento práctico muy bueno** en dimensión media; a menudo supera a gradiente y es competitivo con Newton cuando el Hessiano exacto es caro.
* **Estabilidad de curvatura**: con Wolfe se mantiene $H_k\succ0$.

## Limitaciones

* **Memoria $O(n^2)$:** para almacenar $H_k$ (o $B_k$). En gran escala se prefiere L-BFGS (memoria limitada) que guarda solo unos pocos pares ${s_i,y_i}$.
* **Sensibilidad a $y_k^\top s_k$**: si no es positivo, la actualización puede romper la PD; con paso fijo conviene **skipping** o amortiguación (*damping*).
* **Paso constante vs. line search**: el BFGS clásico asume *line search*; con $\alpha$ constante puede requerir $\alpha$ pequeños y reglas de “salto de actualización” para estabilidad.
