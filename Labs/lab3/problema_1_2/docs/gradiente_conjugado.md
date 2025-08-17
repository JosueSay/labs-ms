# Gradiente Conjugado

## Funcionamiento

Este método busca mínimos de $f:\mathbb{R}^n\to\mathbb{R}$ construyendo una secuencia de **direcciones conjugadas** $d_k$ que combinan el gradiente actual con la historia previa, para acelerar respecto al descenso por gradiente. En cada iteración se define

$$
d_{k} = -g_k + \beta_k\, d_{k-1}, \quad g_k=\nabla f(x_k),
$$

y se actualiza

$$
x_{k+1}=x_k+\alpha_k d_k,
$$

donde $\beta_k$ depende de la variante (FR, PR, HS) y $\alpha_k$ se obtiene idealmente con búsqueda en línea que cumpla Wolfe fuerte, lo que garantiza que $d_k$ sea dirección de descenso y favorece la convergencia del método.

> Intuición: en cuadráticas $f(x)=\tfrac12 x^\top Q x - b^\top x$ con $Q\succ 0$, GC genera direcciones $Q$-conjugadas y converge en a lo más $n$ pasos; el desempeño depende del número de condición de $Q$ (mejor si $\kappa(Q)$ es pequeño). En no lineales, se reusa la misma idea con $\beta_k$ adaptado.

## Variantes de $\beta$ (FR / PR / HS)

Sea $y_k=g_{k+1}-g_k$.

* **Fletcher–Reeves (FR):**

  $$
  \beta^{FR}_{k+1}=\frac{\langle g_{k+1},g_{k+1}\rangle}{\langle g_k,g_k\rangle}.
  $$

  Con Wolfe fuerte, la dirección resultante es de descenso; sin paso exacto, puede requerir condiciones en $\alpha_k$ para asegurar descenso.

* **Polak–Ribière (PR):**

  $$
  \beta^{PR}_{k+1}=\frac{\langle g_{k+1},\, g_{k+1}-g_k\rangle}{\langle g_k,g_k\rangle}.
  $$

  Suele ser más agresivo que FR; para evitar ciclos raros, se usa la versión **recortada**:

  $$
  \beta^{PR+}_{k+1}=\max\{0,\,\beta^{PR}_{k+1}\}.
  $$

  (Con esto se garantiza mejor comportamiento global.)

* **Hestenes–Stiefel (HS):**

  $$
  \beta^{HS}_{k+1}=\frac{\langle g_{k+1},\, y_k\rangle}{\langle d_k,\, y_k\rangle}.
  $$

  Puede ser eficiente, pero la división por $\langle d_k,y_k\rangle$ exige cuidado numérico.

> En la práctica, FR es robusto; PR+ suele converger más rápido; HS puede ser muy competitivo con buena búsqueda en línea.

## Selección de $\alpha_k$: Wolfe fuerte (recomendado)

Se sugiere determinar $\alpha_k$ por búsqueda en línea que cumpla:

$$
f(x_k+\alpha_k d_k)\le f(x_k)+c_1\alpha_k\, g_k^\top d_k,\quad
|g(x_k+\alpha_k d_k)^\top d_k|\le -c_2\, g_k^\top d_k,
$$

con $0<c_2<c_1<1$ y típicamente $c_2<\tfrac12$. Esto garantiza descenso y soporta resultados de convergencia para GC no lineal.

## Flujo interno (no lineal, esquema general)

1. **Inicialización:** $x_0$ dado, $g_0=\nabla f(x_0)$, $d_0=-g_0$.
2. **Iteración $k=0,1,\dots$:**

   a. Elegir $\alpha_k$ (ideal: Wolfe fuerte).

   b. Actualizar $x_{k+1}=x_k+\alpha_k d_k$.

   c. Calcular $g_{k+1}=\nabla f(x_{k+1})$.

   d. Calcular $\beta_{k+1}$ según FR/PR(+)/HS.

   e. Definir $d_{k+1}=-g_{k+1}+\beta_{k+1} d_k$.

   f. **(Opcional) Reinicio:** si $k$ múltiplo de $m$ o si $g_{k+1}^\top g_k$ es grande, poner $d_{k+1}=-g_{k+1}$.

   g. Parar por criterio (`grad`, `fx`, `xAbs`, `xRel`) o `maxIter`.

## Preacondicionado

Para cuadráticas, el rendimiento depende de $\kappa(Q)$. Un **precondicionador** $M\succ0$ aproxima $Q$ (o su inversa) para mejorar el número de condición. En términos de GC, se sustituyen gradientes por $z_k=M^{-1}g_k$ al definir pasos y $\beta$. Ejemplos: Jacobi $M=D$, Gauss–Seidel, SOR.

## Ventajas

* Memoria $O(n)$, sin almacenar ni invertir Hessianos.
* En problemas bien condicionados y con Wolfe fuerte, rápido y con buenas garantías de dirección de descenso.
* PR+ y HS suelen ser más veloces que FR en práctica.

## Desventajas

* **Sensibilidad al paso $\alpha_k$:** con $\alpha$ fijo (naïve) pueden perderse garantías; se recomienda Wolfe fuerte.
* Puede requerir reinicios para mantener buen desempeño.
* HS puede presentar divisores pequeños ($\langle d_k,y_k\rangle$); PR puede ciclar sin recorte (por eso PR+).
