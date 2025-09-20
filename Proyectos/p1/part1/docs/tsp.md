# TSP Problem

* **Objetivo:** encontrar el recorrido más corto posible que visite todas las ciudades una sola vez y regrese al punto de inicio.
* **Involucrados:**
  * **Ciudades (o nodos):** los puntos a visitar.
  * **Viajante (agente):** quien debe recorrer todas las ciudades.
  * **Distancias (o costos):** pesos de las aristas entre cada par de ciudades.
* **Restricciones:**

  * Cada ciudad se visita **exactamente una vez**.
  * El recorrido es un **circuito cerrado** (empieza y termina en el mismo lugar).
* **Tipo de problema:** de **optimización combinatoria** y **NP-duro**.

## Técnicas

### Categoría 1: **Técnicas Comunes**

Son las más básicas, ampliamente usadas y entendidas.

1. **Poda por límites inferiores/superiores** -> si una ruta parcial ya supera el mejor costo hallado, se descarta.
2. **Reducción de simetrías** -> evitar explorar rutas equivalentes (ej. rotaciones o recorridos inversos).
3. **Criterio de cercanía mínima** -> siempre priorizar visitar la ciudad más cercana como paso intermedio.
4. **Evaluación incremental** -> recalcular costos sólo de la parte nueva de la ruta, no todo el recorrido.
5. **Tablas de memoización** -> guardar subproblemas ya resueltos para no recomputarlos.

### Categoría 2: **Técnicas Lógicas**

Usan razonamiento matemático/estructural para reducir la búsqueda.

1. **Relajación del problema** -> resolver una versión más simple (ej. Árbol de expansión mínima) y usarla como límite inferior.
2. **Descomposición del problema** -> dividir en subgrupos de nodos y luego unir las soluciones.
3. **Eliminación de aristas dominadas** -> si una arista es siempre peor que otra alternativa, se descarta.
4. **Criterio de 2-opt/3-opt (mejoras locales)** -> evaluar si intercambiar aristas reduce el recorrido.
5. **Inferencia por desigualdades triangulares** -> usar propiedades métricas para descartar rutas imposibles de mejorar.

### Categoría 3: **Técnicas Inventadas (heurísticas clásicas concretas)**

Diseños humanos que no garantizan optimalidad pero guían mejor la búsqueda.

1. **Heurística de vecino más cercano** -> siempre ir al nodo más próximo aún no visitado.
2. **Heurística del inserto más barato** -> agregar un nuevo nodo al recorrido en la posición que incremente menos el costo.
3. **Heurística del inserto más lejano** -> priorizar incluir los nodos más alejados primero, para reducir huecos grandes al final.
4. **Criterio de ahorro de Clarke-Wright** -> unir rutas parciales si la combinación ahorra distancia.
5. **Heurística de centros múltiples** -> elegir varios nodos "pivote" y organizar el recorrido en torno a ellos.

### Categoría 4: **Técnicas Creativas (exploración avanzada/auxiliar)**

Más flexibles, a veces inspiradas en metáforas o en búsqueda no convencional.

1. **Diversificación controlada** -> forzar al algoritmo a explorar rutas muy diferentes de las ya probadas.
2. **Intensificación selectiva** -> concentrar la búsqueda en una región prometedora, repitiendo mejoras locales.
3. **Reinicio aleatorio inteligente** -> reempezar la búsqueda desde un punto distinto, pero usando información acumulada.
4. **Criterio multiobjetivo auxiliar** -> además de distancia, usar métricas extra (ej. equilibrio en las longitudes de subrutas).
5. **Perturbaciones guiadas ("shaking")** -> modificar deliberadamente una buena solución para escapar de óptimos locales.

### Ranking Global de Efectividad

| Técnica                              | Categoría | Efectividad en grandes | Costo computacional | Facilidad de implementación | Calidad de solución | Generalidad | Justificación breve                                                              |
| ------------------------------------ | --------- | ---------------------- | ------------------- | --------------------------- | ------------------- | ----------- | -------------------------------------------------------------------------------- |
| Poda por límites (bound)             | Común     | ⭐⭐⭐                    | ⭐⭐                  | ⭐⭐                          | ⭐⭐⭐                 | ⭐⭐⭐         | Reduce drásticamente el espacio de búsqueda en muchos problemas, no solo TSP.    |
| Relajación del problema              | Lógica    | ⭐⭐⭐                    | ⭐⭐                  | ⭐                           | ⭐⭐⭐                 | ⭐⭐⭐         | Muy útil como límite inferior, requiere teoría matemática pero da gran poder.    |
| 2-opt / 3-opt                        | Lógica    | ⭐⭐                     | ⭐⭐                  | ⭐⭐                          | ⭐⭐⭐                 | ⭐⭐          | Mejora local clásica, muy buena para calidad de solución.                        |
| Diversificación + Intensificación    | Creativa  | ⭐⭐⭐                    | ⭐⭐                  | ⭐                           | ⭐⭐⭐                 | ⭐⭐          | Balancea exploración/explotación, fuerte en contextos grandes y metaheurísticas. |
| Eliminación de aristas dominadas     | Lógica    | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐                          | ⭐⭐                  | ⭐⭐          | Fácil de aplicar, mejora eficiencia descartando opciones inútiles.               |
| Perturbaciones guiadas               | Creativa  | ⭐⭐⭐                    | ⭐⭐                  | ⭐                           | ⭐⭐                  | ⭐           | Evita quedar atrapado en óptimos locales, pero más útil en problemas grandes.    |
| Inserto más barato                   | Inventada | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐⭐                         | ⭐⭐                  | ⭐           | Muy fácil y rápido, útil como punto de partida, pero limitado.                   |
| Memoización                          | Común     | ⭐⭐                     | ⭐                   | ⭐⭐                          | ⭐⭐                  | ⭐⭐⭐         | Acelera subproblemas repetidos, útil en DP, pero consume memoria.                |
| Reinicio aleatorio inteligente       | Creativa  | ⭐⭐                     | ⭐⭐                  | ⭐                           | ⭐⭐                  | ⭐           | Mitiga estancamiento, pero no garantiza calidad.                                 |
| Heurística de ahorro (Clarke-Wright) | Inventada | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐                          | ⭐⭐                  | ⭐           | Buena para problemas logísticos, rápida, no siempre óptima.                      |
| Reducción de simetrías               | Común     | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐                          | ⭐                   | ⭐⭐          | Ahorra cálculo en problemas con rutas equivalentes.                              |
| Vecino más cercano                   | Inventada | ⭐                      | ⭐⭐⭐                 | ⭐⭐⭐                         | ⭐                   | ⭐           | Simplicidad extrema, pero soluciones muy pobres en general.                      |
| Evaluación incremental               | Común     | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐⭐                         | ⭐⭐                  | ⭐⭐          | Ahorra tiempo de cálculo, técnica auxiliar muy útil.                             |
| Desigualdad triangular               | Lógica    | ⭐⭐                     | ⭐⭐⭐                 | ⭐⭐                          | ⭐⭐                  | ⭐⭐⭐         | Lógica matemática general, útil en problemas métricos más allá de TSP.           |
| Centros múltiples                    | Inventada | ⭐                      | ⭐⭐                  | ⭐                           | ⭐                   | ⭐           | Poco usado, difícil de adaptar, soluciones irregulares.                          |

## Técnicas vistas en clase

### Inicialización y selección

1. **Selección probabilística por tiers / ranking controlado**

   * **Qué es:** dividir la población en niveles (tiers) tras ordenarla por fitness, asignando mayor probabilidad de selección a los mejores, pero manteniendo alguna probabilidad para los menos aptos.
   * **Para qué se usa:** evitar estancamiento y conservar diversidad genética, asegurando que todos los individuos tengan oportunidad de reproducirse.

2. **Selección por porcentaje / corte fijo / ruleta / torneo**

   * **Qué es:** métodos para decidir quién sobrevive: elegir un % de los mejores, fijar un número, o dar probabilidades proporcionales al fitness.
   * **Para qué se usa:** balancear explotación de buenos individuos con exploración de otros.

### Operadores de cruce

3. **Single-point crossover**

   * **Qué es:** cortar dos cromosomas en un punto y recombinar.
   * **Para qué se usa:** transferir bloques grandes de información de cada padre.

4. **Two-point crossover**

   * **Qué es:** realizar dos cortes, generando tres bloques y recombinándolos.
   * **Para qué se usa:** mezclar segmentos más variados de los padres.

5. **Uniform crossover**

   * **Qué es:** elegir aleatoriamente cada gen de uno de los dos padres.
   * **Para qué se usa:** maximizar recombinación y diversidad.

6. **Cruce con combinación lineal (para floats)**

   * **Qué es:** interpolar entre dos individuos con un parámetro α (0 < α < 1).
   * **Para qué se usa:** generar descendientes intermedios, parecido a un promedio ponderado.

7. **Cruces para permutaciones (PMX, cíclico, OX)**

   * **Qué son:** operadores que garantizan descendencia válida sin duplicados. Ej:

     * **PMX (Partially Mapped Crossover):** mapeo parcial de bloques.
     * **Cruce cíclico:** preserva la posición relativa de elementos siguiendo ciclos.
   * **Para qué se usan:** problemas como TSP, donde los cromosomas son permutaciones.

### Operadores de mutación

8. **Mutación en binario (1-bit, 2-bit flip)**

   * **Qué es:** invertir uno o más bits al azar.
   * **Para qué se usa:** mantener variabilidad mínima en representaciones binarias.

9. **Mutación en enteros (incremento/decremento controlado)**

   * **Qué es:** sumar/restar un valor pequeño dentro de un rango.
   * **Para qué se usa:** variar genes discretos sin romper restricciones.

10. **Mutación en permutaciones (2-swap, 3-swap, shuffle)**

* **Qué es:** intercambiar elementos o rotar bloques en una permutación.
* **Para qué se usa:** introducir cambios sin generar duplicados.

### Estrategias de control y mejora

11. **Intensificación**

* **Qué es:** forzar que el cruce/mutación generen individuos dentro de la vecindad de soluciones previas.
* **Para qué se usa:** explotar zonas prometedoras, mejorar soluciones locales.

12. **Diversificación**

* **Qué es:** introducir saltos aleatorios o individuos lejanos a los actuales.
* **Para qué se usa:** explorar nuevas regiones y evitar mínimos locales.

13. **Registro del "best-so-far"**

* **Qué es:** mantener siempre guardado el mejor individuo encontrado.
* **Para qué se usa:** asegurar que el algoritmo no pierda la mejor solución hallada hasta el momento.

14. **Condiciones de parada (generaciones, tiempo, estancamiento)**

* **Qué es:** definir criterios claros para detener la evolución.
* **Para qué se usa:** evitar bucles infinitos y controlar recursos.

15. **Logging selectivo / visualización**

* **Qué es:** registrar o graficar solo cuando el "best" mejora.
* **Para qué se usa:** analizar convergencia sin ruido excesivo.
