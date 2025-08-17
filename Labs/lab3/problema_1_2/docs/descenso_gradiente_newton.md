# Método de Newton

## Idea central

Para minimizar $f:\mathbb{R}^n\!\to\!\mathbb{R}$ con $f\in C^2$, en cada iteración se aproxima $f$ alrededor de $x_k$ con su **modelo cuadrático** (Taylor de 2.º orden):

$$
m_k(d)=f(x_k)+\nabla f(x_k)^\top d+\tfrac12\, d^\top \nabla^2 f(x_k)\, d.
$$

Minimizar $m_k$ da la ecuación normal

$$
\nabla^2 f(x_k)\, d_k=-\nabla f(x_k)\quad\Rightarrow\quad d_k=-\big[\nabla^2 f(x_k)\big]^{-1}\nabla f(x_k).
$$

La **actualización** es $x_{k+1}=x_k+\alpha_k d_k$. En el Newton “puro” $\alpha_k=1$; en práctica puede usarse búsqueda en línea.&#x20;

## Relación con tu apunte

En tu nota, el descenso “básico” usa $d_k$ como una **dirección de descenso** y un paso $\alpha$ fijo: $x_{k+1}=x_k+\alpha d_k$. Newton es un caso donde la dirección se obtiene resolviendo
$\nabla^2 f(x_k)\, d_k=-\nabla f(x_k)$. Si además $\alpha=1$, Newton suele dar grandes avances cerca del mínimo. (Encaja en tu esquema general de “elegir $d_k$” y “actualizar con $\alpha$”).

## ¿Por qué Newton puede ser mucho más rápido?

- Usa **curvatura** (Hessiano), no solo pendiente.
- Bajo condiciones estándar (mínimo estricto, Hessiano positivo definido en $x^\star$), tiene **convergencia cuadrática** cerca de la solución, mientras que el gradiente (paso fijo) suele ser lineal.
- Equivale a “re-escalar” las coordenadas por la curvatura local, corrigiendo direcciones mal condicionadas.

## Condición de dirección de descenso

$d_k$ es de descenso si $\nabla f(x_k)^\top d_k<0$. Con Newton:

$$
\nabla f(x_k)^\top d_k
= -\,\nabla f(x_k)^\top \big[\nabla^2 f(x_k)\big]^{-1}\nabla f(x_k)<0
$$

**si** $\nabla^2 f(x_k)$ es **definida positiva** (PD). Si el Hessiano es indefinido o negativo definido, $d_k$ puede **no** ser de descenso. Solución clásica: **modificar** el Hessiano, p.ej. $B_k=\nabla^2 f(x_k)+\tau I$ con $\tau>0$, para volverlo PD (Newton “amortiguado” o “modificado”).&#x20;

## Elección de $\alpha_k$ (tamaño de paso)

- **Newton puro**: $\alpha_k=1$. Funciona bien cerca del óptimo.
- **Búsqueda en línea**: si estamos lejos, usar backtracking/condiciones de Wolfe para asegurar descenso suficiente y estabilidad (muy común en Newton práctico y cuasi-Newton). El propio material de cuasi-Newton muestra los pasos con “calcular $\alpha_k$ por búsqueda en línea”.&#x20;

## Requisitos prácticos

- $f\in C^2$ y **Hessiano calculable** (o al menos aplicable como operador).
- Resolver el **sistema lineal** $\nabla^2 f(x_k)\, d_k=-\nabla f(x_k)$ con `solve` (no invertir explícitamente).
- Si $\nabla^2 f(x_k)$ no es PD: regularizar (sumar $\tau I$), o cambiar a **trust-region**.

## Pseudocódigo

1. Dado $x_0$.
2. Repetir hasta cumplir criterio de paro (norma del gradiente, cambio en $x$ o en $f$, o iteraciones):

   a. Calcular $g_k=\nabla f(x_k)$, $H_k=\nabla^2 f(x_k)$.

   b. Si $H_k$ no es PD, modificar $H_k\leftarrow H_k+\tau I$.

   c. Resolver $H_k d_k=-g_k$.

   d. Elegir $\alpha_k$ (1 o búsqueda en línea).

   e. Actualizar $x_{k+1}=x_k+\alpha_k d_k$.
3. Devolver $x_{k^*}$ y métricas.

(La derivación del paso Newton $x_{k+1}=x_k-(\nabla^2 f_k)^{-1}\nabla f_k$ y el modelo cuadrático están en tu PDF).&#x20;

## Diferencias con otros métodos

- **Vs. gradiente (naïve/random/steepest)**:

  - GD usa $d_k=-\nabla f$ (o cercanas), **sin** curvatura; Newton usa $H_k^{-1}\nabla f$.
  - GD requiere sintonizar $\alpha$; Newton puro suele usar $\alpha=1$ cerca del óptimo.
  - Newton: **menos iteraciones** pero **más costosas** (Hessiano + sistema).
- **Vs. cuasi-Newton (DFP/BFGS)**:

  - Cuasi-Newton **no** calcula $\nabla^2 f$; construye $B_k$ o $H_k$ que cumplen la **ecuación de la secante** $B_{k+1}s_k=y_k$ o $H_{k+1}y_k=s_k$ con $s_k=x_{k+1}-x_k$, $y_k=g_{k+1}-g_k$.
  - BFGS/DFP garantizan PD bajo condiciones de Wolfe ($y_k^\top s_k>0$) y suelen ser más eficientes cuando $n$ es grande o el Hessiano es caro.&#x20;

## Ventajas y limitaciones

- **+** Convergencia local **cuadrática** (rápida) si $H(x^\star)$ es PD y estamos suficientemente cerca.
- **+** Direcciones “bien escaladas” por curvatura.
- **−** Coste por iteración alto: cálculo de $\nabla^2 f$ y resolución lineal.
- **−** Si $H$ es indefinido/singular, puede fallar; se requiere **regularización** o cambio de estrategia.&#x20;
