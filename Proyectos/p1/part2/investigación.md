# Formulación del TSP como Problema de Programación Entera

## ¿Cómo se formula el TSP como un problema de programación lineal/entera?

El **Problema del Viajante de Comercio (TSP)** puede formularse como un problema de **programación lineal entera (PLE)**, donde el objetivo es encontrar el recorrido de costo mínimo que visita cada ciudad exactamente una vez y regresa al punto de partida.

### Variables de decisión

- Definimos variables binarias:
  $$
  x_{ij} = \begin{cases}
    1 & \text{si el tour va de la ciudad } i \text{ a la ciudad } j \\
    0 & \text{en otro caso}
  \end{cases}
  $$
  para todas las parejas de ciudades $i \neq j$.

### Función objetivo

- Minimizar la distancia total recorrida:
  $$
  \min \sum_{i=1}^n \sum_{j=1}^n c_{ij} x_{ij}
  $$
  donde $c_{ij}$ es la distancia entre las ciudades $i$ y $j$.

### Restricciones

1. **Salida única:** De cada ciudad $i$ sale exactamente una arista:
   $$
   \sum_{j=1,\, j \neq i}^n x_{ij} = 1 \quad \forall i
   $$
2. **Entrada única:** A cada ciudad $j$ llega exactamente una arista:
   $$
   \sum_{i=1,\, i \neq j}^n x_{ij} = 1 \quad \forall j
   $$
3. **Eliminación de subciclos:** Para evitar ciclos menores al tour completo, se agregan restricciones adicionales. Una forma común es la formulación de Miller-Tucker-Zemlin (MTZ):
   $$
   u_i - u_j + n x_{ij} \leq n-1 \quad \forall i \neq j,\ 2 \leq i,j \leq n
   $$
   donde $u_i$ son variables auxiliares.

4. **Variables binarias:** $x_{ij} \in \{0,1\}$

---

## ¿Cómo se resuelve con PuLP?

- **PuLP** es una librería de Python para modelar y resolver problemas de programación lineal y entera.
- Se definen las variables, la función objetivo y las restricciones usando la API de PuLP.
- El solucionador (por ejemplo, CBC) encuentra el tour óptimo.

---

## Escenarios

Para cumplir con los 3 escenarios, se pueden modificar:
- El número de ciudades (instancias pequeñas, medianas, grandes).
- Las distancias (por ejemplo, simular ciudades más cercanas o lejanas).
- Restricciones adicionales (por ejemplo, ciudades obligatorias, ventanas de tiempo, etc.).

---

## Referencias

- [Wikipedia: TSP Integer Programming Formulation](https://en.wikipedia.org/wiki/Travelling_salesman_problem#Integer_linear_programming_formulation)
- [PuLP Documentation](https://coin-or.github.io/pulp/)
- Miller, C. E., Tucker, A. W., & Zemlin, R. A. (1960). "Integer Programming Formulation of Traveling Salesman Problems". Journal of the ACM.

---