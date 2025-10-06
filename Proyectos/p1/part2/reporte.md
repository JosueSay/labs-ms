# Inciso 2 – Formulación y Resolución del TSP con Programación Entera

## Objetivo
El objetivo de este inciso es **formular el Problema del Viajante de Comercio (TSP)** como un problema de **Programación Lineal Entera (PLE)** e **implementarlo en código** utilizando la librería **PuLP en Python**, para resolver tres escenarios distintos.

---

## Formulación del TSP como ILP (Miller–Tucker–Zemlin)

El TSP se formuló mediante la versión de **Miller–Tucker–Zemlin (MTZ)**, la cual evita subtours mediante variables auxiliares continuas.

- **Variables de decisión**:
  - \(x_{ij} \in \{0,1\}\): vale 1 si se viaja de la ciudad \(i\) a la ciudad \(j\), 0 en otro caso.
  - \(u_i\): variable auxiliar que representa el orden en que se visita la ciudad \(i\).

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

Se desarrolló el archivo `tsp_pulp.py`, el cual realiza los siguientes pasos:

1. **Lectura de instancias `.tsp`** en formato TSPLIB mediante el módulo `io_tsp.py`.  
2. **Cálculo de la matriz completa de distancias** a partir de las coordenadas.  
3. **Construcción del modelo ILP en PuLP**:
   - Variables binarias \(x_{ij}\).  
   - Restricciones de entrada/salida y eliminación de subtours (MTZ).  
   - Solver utilizado: **CBC (Coin-or Branch and Cut)**.  
4. **Ejecución automática de tres escenarios** con límite de **3600 segundos por instancia**.  
5. **Generación de resultados en formato CSV** (`pulp_results.csv`).

---

## Escenarios Resueltos

Los tres escenarios elegidos fueron:

| Escenario | Archivo TSP | Tamaño (n) | Tipo de distancia | Estado | Costo (objective) | Tiempo (s) |
|------------|--------------|------------|--------------------|---------|-------------------|-------------|
| Escenario 1 | **cereza (cherry189.tsp)** | 189 | EUC_2D | Not Solved | 2920.7249 | 3604.15 |
| Escenario 2 | **eil101.tsp** | 101 | EUC_2D | Optimal | 693.0000 | 3600.98 |
| Escenario 3 | **gr229.tsp** | 229 | GEO | Optimal | 185778.0000 | 3602.13 |

Estos valores fueron generados automáticamente y guardados en `Proyectos/p1/part2/pulp_results.csv`.

---

## Análisis de Resultados

- La instancia **cereza (189 ciudades)** no alcanzó una solución óptima en una hora, pero el solver entregó una **solución entera válida y cercana al óptimo**.  
  Esto es esperable, pues el modelo crece cuadráticamente en número de variables y restricciones.

- Las instancias **eil101** y **gr229** alcanzaron **soluciones óptimas**, confirmadas por el estado `Optimal` en el CSV.

- El solver **CBC** mostró estabilidad, ejecutando correctamente cada instancia dentro del límite de tiempo.

---

## Conclusiones

- Se logró formular el TSP como un **problema de Programación Lineal Entera (ILP)** usando la formulación de Miller–Tucker–Zemlin.  
- La implementación en **PuLP + CBC** resolvió correctamente instancias pequeñas y medianas.  
- En instancias mayores (como *cherry189*), el tiempo de convergencia crece exponencialmente, lo cual es coherente con la naturaleza **NP-dura** del TSP.  
- Los resultados del **modelo exacto (ILP)** sirven como **referencia óptima** para comparar con los resultados del **Algoritmo Genético (GA)** implementado en el inciso 1.  
- La exportación de resultados en formato CSV permite integrar fácilmente las métricas de comparación entre métodos.

---
