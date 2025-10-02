# Inciso 2 – Formulación y Resolución del TSP con Programación Entera

## Objetivo
El objetivo de este inciso es **formular el Problema del Viajante de Comercio (TSP) como un problema de Programación Lineal Entera (PLE)** e **implementarlo en código** utilizando la librería **PuLP en Python**, para resolver tres escenarios diferentes.

---

## Formulación del TSP como ILP (Miller-Tucker-Zemlin)

El TSP se formuló mediante la versión de Miller-Tucker-Zemlin (MTZ), que evita subtours mediante variables auxiliares.

- **Variables de decisión**:
  - \(x_{ij} \in \{0,1\}\): 1 si se viaja de la ciudad \(i\) a la ciudad \(j\), 0 en otro caso.
  - \(u_i\): variables auxiliares para eliminar subtours (orden de visita de cada ciudad).

- **Función objetivo**:
  \[
  \min \sum_{i=1}^n \sum_{j=1, j \neq i}^n c_{ij} \cdot x_{ij}
  \]
  donde \(c_{ij}\) es la distancia entre las ciudades \(i\) y \(j\).

- **Restricciones**:
  1. **Salida única por ciudad**:  
     \(\sum_{j \neq i} x_{ij} = 1 \quad \forall i\)

  2. **Entrada única por ciudad**:  
     \(\sum_{i \neq j} x_{ij} = 1 \quad \forall j\)

  3. **Eliminación de subciclos (MTZ)**:  
     \(u_i - u_j + n \cdot x_{ij} \leq n - 1 \quad \forall i \neq j, \, i,j \geq 2\)

  4. **Naturaleza de variables**:  
     \(x_{ij} \in \{0,1\}\)

---

## Implementación en PuLP

Se desarrolló el archivo `tsp_pulp.py`, que realiza los siguientes pasos:

1. **Lectura de instancias `.tsp`** en formato TSPLIB (`read_coords`).  
2. **Cálculo de matriz de distancias euclidianas** (`calc_dist_matrix`).  
3. **Construcción del modelo ILP en PuLP**:
   - Variables binarias \(x_{ij}\).  
   - Restricciones de entrada/salida y MTZ.  
   - Solver utilizado: CBC (Coin-or branch and cut).  
4. **Reconstrucción del tour y costo final** (`solve_tsp_pulp`).  
5. **Resolución de tres escenarios**:
   - `berlin52.tsp` → instancia pequeña, benchmark clásico.  
   - `cherry189.tsp` → instancia inventada/personalizada.  
   - `eil101.tsp` → instancia mediana de TSPLIB.  

---

## Resultados Obtenidos

Los resultados preliminares muestran:

- Para **berlin52 (52 ciudades)**:  
  - Variables: 2703  
  - Restricciones: 2654  
  - Costo óptimo: 7544.36  
  - Tiempo de ejecución: ~60s  

- Para **cherry189 (189 ciudades)**:  
  - Variables: 35,720  
  - Restricciones: 35,534  
  - Solver tardó varios minutos; se obtuvo una solución entera cercana al óptimo.  

- Para **eil101 (101 ciudades)**:  
  - Variables: ~10,000+  
  - Restricciones: ~10,000+  
  - Resultados dentro de tiempos razonables, validando la implementación.  

---

## Conclusiones

- Se logró formular el TSP como un **problema de Programación Lineal Entera**.  
- La implementación en **PuLP + CBC** permitió obtener soluciones óptimas en instancias pequeñas y medianas.  
- En instancias más grandes (como *cherry189*), el tiempo de ejecución aumenta significativamente, lo cual es esperado debido a la complejidad del TSP (NP-duro).  
- Este inciso complementa el inciso 1 (GA), ya que ahora se cuenta con las **soluciones óptimas de referencia** para comparar contra los resultados heurísticos del Algoritmo Genético.  

---
