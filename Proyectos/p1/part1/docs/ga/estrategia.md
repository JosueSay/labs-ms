# Estrategia final

## 1. Entradas admitidas

* **Usar coordenadas $(x,y)$**: convertir las coordenadas a una **matriz de distancias** usando la métrica elegida (ej. euclidiana). Cachear resultados y validar la desigualdad triangular.
* **Usar matriz de distancias $D$ simétrica**:

  * Leer y almacenar solo el **triángulo superior (o inferior)** de la matriz y reconstruir $d_{ij}=d_{ji}$ on-the-fly.
  * Comprimir en un vector de $\frac{n(n-1)}{2}$ entradas.
  * Evitar procesar toda la matriz en cada cálculo: usar *lookup* incremental de $d_{i,i+1}$ al evaluar un tour.

## 2. Parámetros de control (expuestos al usuario)

* Incluir un bloque `Config` con:

  * **N** = tamaño de la población.
  * **maxIter** = número máximo de generaciones.
  * **% sobrevivientes**, **% por cruce**, **% por mutación**.
* Definir si los porcentajes son exclusivos o si la mutación se aplica también sobre hijos de cruce.
* Incluir extras: **elitismo (k o %)**, **tamaño de torneo k**, **semilla aleatoria**, **ciudad inicial fija** para reducir $(n-1)!$.

## 3. Mecanismos aleatorios y operadores

* **Hacer selección** con torneo o ranking/tier; ajustar $k$ para balancear presión selectiva y diversidad.
* **Aplicar cruce** con al menos un método clásico (OX/PMX) y uno informado por distancias (SCX, ASCX, GSCX, RGSCX o CSCX).
* **Aplicar mutación** con insertion (INST) y/o swap; incluir 2-opt como mutación guiada con baja probabilidad para intensificar localmente.
* **Usar secuencia de inversiones** si se quiere habilitar cruces n-puntos estándar y mutación simple manteniendo validez automática (con elitismo \~15%).

## 4. Control de diversidad

* Mantener **elitismo moderado** (2–10%) para no congelar la población.
* Permitir que **peores individuos** tengan probabilidad no nula de selección (ranking/tiers).
* Implementar **mutación adaptativa**: aumentar $P_m$ si el best no mejora en cierto número de generaciones.
* Combinar con un **híbrido de intensificación controlada**: aplicar 2-opt de forma ocasional y/o inicializar parte de la población con heurísticos o Ant System.

## 5. Salidas requeridas

* **Generar simulación visual** que grafique el recorrido *best-so-far* por generación, mostrando curva de costo y el camino actual. Loggear solo cuando hay mejora.
* **Devolver resultado final**: el mejor recorrido encontrado ($\textbf{best}$) y su distancia total $D$, incluyendo regreso al origen.

## 6. Ingeniería que escala (52 → \~500 nodos)

* Implementar **evaluación incremental del costo** recalculando solo aristas afectadas por swap/insert/2-opt.
* Almacenar la **matriz $D$ simétrica** como triángulo comprimido y usar *lookups* $d_{ij}=d_{ji}$.
* **Inicializar población** mezclando individuos aleatorios con heurísticos (nearest/cheapest insertion) o semillas Ant System.
* **Paralelizar** la evaluación de fitness, la búsqueda 2-opt y la construcción SCX/CSCX.
* **Definir criterios de parada**: `maxIter`, estancamiento (best no mejora en `max(200, G/3)`), o límite de tiempo.

## 7. Reglas prácticas de parámetros

* Para **52 nodos (arranque)**:

  * Usar representación por permutación.
  * Seleccionar con torneo $k=5$.
  * Cruzar con OX/PMX o SCX.
  * Mutar con INST ($P_m \approx 2/n$) y aplicar 2-opt raramente.
  * Mantener elitismo 2–5%.
  * Usar $\text{Pc} \approx 0.8–1.0$, $N \approx 150–300$.

* Para **\~500 nodos (escalar)**:

  * Sembrar población con heurísticos o AS.
  * Cruzar con CSCX (GSCX+RGSCX).
  * Mutar con INST + 2-opt muy baja probabilidad.
  * Usar $\text{Pc} \approx 1.0$, $\text{Pm} \approx 1/n$ (adaptativa si se estanca).
  * Escalar población a $N \approx 800–1200$.
  * Implementar evaluación incremental y triángulo comprimido de $D$.

## 8. Pseudoflujo

1. Seleccionar **S% sobrevivientes** (mejores + elitismo).
2. Generar **C% hijos por cruce** (OX/PMX o SCX/CSCX).
3. Generar **M% hijos por mutación** (INST/swap + 2-opt ocasional).

> Asegurar que **S% + C% + M% = 100%** (o definir política si la mutación aplica también sobre hijos de cruce).

## Nota explícita para la documentación

> **Matriz de distancias simétrica**: Cuando se reciba una matriz $D\in\mathbb{R}^{n\times n}$ con $d_{ij}=d_{ji}$ y $d_{ii}=0$, **no procesar la matriz completa**. Almacenar solo el **triángulo superior (o inferior)** en un vector de longitud $n(n-1)/2$. Usar *lookups* $d_{ij}$ con simetría $d_{ij}=d_{ji}$ y aplicar **evaluación incremental** en operadores (swap/insert/2-opt) para evitar recomputar el costo total. Con esto se reduce memoria y tiempo sin perder exactitud.
