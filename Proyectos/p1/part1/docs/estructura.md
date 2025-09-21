# Información de estructura

## ¿Cuál es la variable, el espacio muestral y la función objetivo?

* **Variable de decisión (tour):** una **permutación** $\pi = [\pi_1,\dots,\pi_n]$ de las $n$ ciudades.
* **Espacio muestral (factible):** $\Omega = S_n$ (todas las permutaciones). Si fijas ciudad inicial: $|\Omega|=(n-1)!$.
* **Restricciones embebidas:** en una permutación **no hay repetidos** y la longitud es $n$ -> cada ciudad aparece **exactamente una vez**. El tour se cierra con $\pi_n \to \pi_1$.
* **Función objetivo (minimizar distancia total):**

  $$
  D(\pi) \;=\; \sum_{i=1}^{n-1} d_{\pi_i,\pi_{i+1}} \;+\; d_{\pi_n,\pi_1}
  $$

  Con TSPLIB EUC_2D, $d_{ij}$ proviene de coordenadas (redondeo entero usual).

## ¿Por qué **permutación** es la representación adecuada?

1. **Validez por construcción:** toda cadena del espacio $S_n$ es un tour válido. No necesitas reparaciones ni restricciones extra para "una vez por ciudad".
2. **Dimensión correcta del problema:** el TSP decide **orden** de visita, no valores numéricos de magnitud. La permutación modela **orden** directamente.
3. **Operadores específicos bien definidos:** cruces y mutaciones como **PMX, OX, ERX, swap, insert, inversion/2-opt** preservan la validez (siguen siendo permutaciones).
4. **Eficiencia del espacio:** $|S_n|=n!$. Puede ser grande, pero es **el** conjunto factible. Otras codificaciones incluyen muchos vectores **inválidos** (derroche de búsqueda).
5. **Coherencia con la evaluación:** el costo depende solo del **orden relativo** de ciudades; la permutación captura eso sin variables sobrantes.

## ¿Por qué **no** binaria, entera o float?

### Binaria

* Típica codificación binaria (por ejemplo, matriz de adyacencia) vive en $\{0,1\}^{n\times n}$ -> **espacio = $2^{n^2}$**, dominado por **soluciones inválidas** (grados ≠ 2, subtours múltiples, etc.).
* Requiere **muchas restricciones** (grado 2 por nodo, eliminación de subtours) o **reparaciones costosas** tras cada cruce/mutación.
* Operadores binarios estándar rompen validez con facilidad.

### Entera (vector de enteros con repetición)

* Si permites repeticiones o rangos $[1,n]$ sin restricción de unicidad, la mayoría de vectores **no son tours**.
* Si fuerzas unicidad, terminas reinventando... **una permutación**.

### Float (reales)

* No hay interpretación natural de un real para "orden de visita".
* Tendrías que mapear floats a un orden (p. ej., ordenar por valor), lo que introduce **indirección, empates y ruido**; además, los operadores de cruce/mutación de floats **no respetan** estructura de tour.

## Conclusión breve

* **Variable:** $\pi \in S_n$ (permutación).
* **Espacio muestral:** $S_n$ (o $(n-1)!$ fijando inicio).
* **Objetivo:** minimizar $D(\pi)$ usando $D$ derivada de las coordenadas TSPLIB (EUC_2D).
* **Justificación:** la representación por **permutaciones** codifica exactamente el TSP, evita soluciones inválidas, facilita operadores genéticos correctos y hace el GA más eficiente y estable que las codificaciones binaria/entera/float.
