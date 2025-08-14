# Problema 3

**Construya una función “suma de gaussianas” 2-dimensional, en la forma:**

$$
f(\mathbf{x}) = -\sum_{i=1}^{k} \exp\left(-\frac{1}{2\sigma} \|\mathbf{x} - \mathbf{x}_i\|_2^2\right),
$$

donde **$x_1, x_2, ..., x_k$** son puntos en el rectángulo \[0,8] × \[0,8] elegidos de forma aleatoria (distribución uniforme). Use $k = 8$ (8 gaussianas). Aquí, $\sigma > 0$ es un parámetro de escala definido por el usuario.

**Nota:** Una vez se construyen los puntos aleatorios **$x_k$** deberá congelarlos para trabajar siempre con la misma función $f$.

Aplique varias veces alguno de los métodos implementados a la función $f$, con inicializaciones **$x_0$** distintas, de forma que se puedan obtener los diferentes mínimos locales de la función.

Elabore una tabla con todos los mínimos encontrados, y muestre visualizaciones de diferentes secuencias de aproximaciones $\{x_i\}$ convergiendo a cada uno de los mínimos locales de su $f$, al igual que en el ejercicio anterior.
