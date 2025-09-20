# Optimización Discreta

## Definición General

En este tipo de optimización se busca una **solución en un espacio finito**.

Formalmente:

$$
f: \Gamma \to \mathbb{R}
$$

Si el dominio son enteros:

$$
f: \mathbb{Z} \to \mathbb{R}, \quad f: \mathbb{N} \to \mathbb{R}
$$

En más dimensiones:

$$
f: \mathbb{Z}^n \to \mathbb{R}
$$

El problema: aunque el espacio sea finito, puede ser **muy grande**.
Ejemplo:

$$
|\Gamma| = 10^k \; 2^k
$$

Esto crece exponencialmente con $k$.

## Problema de Optimización Discreta

Queremos encontrar:

$$
x^* = \arg\min_{x \in \Gamma} F(x) \quad \text{sujeto a } G(x)
$$

* **F(x):** función objetivo.
* **G(x):** conjunto de restricciones.

La forma de resolver dependerá de **cómo se represente el problema**.

## Comparación con Optimización Continua

* **Optimización continua:** se usa descenso por gradiente, derivadas, etc.
* **Optimización discreta:** no podemos usar gradientes. Ejemplo: resolver un **Sudoku**.

En IA ya vimos algoritmos de búsqueda (Montecarlo, backtracking, etc.), aquí se pueden aplicar también.

## Ejemplos Típicos

1. **8 reinas:**

   * Condiciones: no se repiten reinas en la misma fila, columna ni diagonal.
   * Puede verse como un problema de **optimización de configuración**.

2. **Sudoku:**

   * Cada número debe aparecer una vez por fila, columna y subcuadro.
   * Se puede escribir como un problema de restricciones y optimización.

3. **Asignación de tareas (Scheduling):**

   * Se tiene una matriz de costos $C$ donde $c_{ij}$ es el costo de que persona $i$ haga tarea $j$.
   * Objetivo:

   $$
   \min \sum_{i=1}^n \sum_{j=1}^n x_{ij} c_{ij}
   $$

   donde $X$ es matriz de permutación.

   El espacio de búsqueda es:

   $$
   |\Omega| = n!
   $$

   Crece muy rápido.

4. **TSP (Traveling Salesman Problem):**

   * Dado un conjunto de ciudades, hallar el recorrido mínimo que visita todas y regresa al inicio.
   * Variante industrial: **Vehicle Routing Problem (VRP)**, con varios vehículos.
   * Variante más compleja: **Capacitated VRP**, donde cada vehículo tiene capacidad limitada.

Pregunta detonadora:

* ¿Qué tan diferente es el TSP de un problema de asignación?
* ¿Por qué ambos pueden representarse como problemas de permutaciones?

## Representaciones de Soluciones

Para resolver problemas discretos, lo primero es definir cómo representamos una configuración $x$.

### 1. Representación Binaria

$$
x = [0,1,1,1,0,0,1,0,0,1]
$$

* Espacio:

$$
|\Omega| = 2^n
$$

Ejemplo: **Knapsack (Mochila)**.

* Tenemos $n$ objetos.
* Cada $x_i \in \{0,1\}$ indica si llevamos o no el objeto.
* Datos:

  * Valores: $v = (v_1, v_2, ..., v_n)$
  * Pesos: $w = (w_1, w_2, ..., w_n)$
* Problema:

$$
\max \sum_{i=1}^n x_i v_i \quad \text{sujeto a} \quad \sum_{i=1}^n x_i w_i \leq K
$$

Pregunta:

* ¿Qué pasa si en vez de binaria permitimos llevar fracciones del objeto? (-> Knapsack fraccionario -> problema continuo).

### 2. Representación Entera

$$
x = [5,3,0,1,2,2,4,3,7,2] \in \mathbb{Z}^n
$$

Cada componente es un número entero en un rango $[a,b]$.
Espacio:

$$
|\Omega| = (b-a+1)^n
$$

Ejemplo: **Transporte (Supply & Demand)**.

* Variables = cuántos productos se envían de fábrica a destino.
* $x_{ij}$ es entero no negativo, limitado por producción y demanda.

Pregunta:

* ¿Qué ventajas tiene modelar transporte con enteros frente a binario?

### 3. Representación Real (Flotante)

$$
x = [3.1, 2.5, -1.1, 0.15, 5.0] \in \mathbb{R}^n
$$

En este caso, el espacio ya no es finito. Para discretizar:

* Se crea un **grid** (rejilla).
* Ejemplo: dividir \[0,1] en 100 valores -> el problema se vuelve finito.

### 4. Representación por Permutaciones

$$
x = [2,6,3,9,8,0,4,1,7,5] \in S_n
$$

Características:

* No se repiten valores.
* Espacio de búsqueda:

$$
|S_n| = n!
$$

Ejemplos:

* **Sudoku:** en cada fila no se repiten números.
* **8 reinas:** cada fila/columna con una sola reina.
* **TSP:** ruta como una permutación de ciudades.

Comparación:

* En binaria, espacio para 8 reinas: $2^{64}$.
* En permutaciones: $8! = 40,320$.
  Mucho más pequeño y eficiente.

Pregunta:

* ¿Qué ventajas tiene usar permutaciones en vez de binario para 8 reinas?

## Ejemplo: TSP en detalle

Datos:

* Matriz de distancias $D$ de tamaño $n \times n$.
* Se busca un tour mínimo:

$$
x = [1,9,10,5,4,7,2,8,3,6]
$$

Esto representa el orden de visita.

Función objetivo:

$$
D(x) = d_{1,9} + d_{9,10} + ... + d_{6,1}
$$

* Si fijamos la ciudad inicial, el espacio se reduce a:

$$
|\Omega| = (n-1)!
$$

Pregunta:

* ¿Por qué fijar la ciudad inicial reduce el espacio de búsqueda sin perder generalidad?

## Exactitud vs Tiempo

El problema en optimización discreta:

* El espacio es **enorme**.
* Una búsqueda exhaustiva es inviable.
* Se usan **búsquedas parciales o aleatorias inteligentes**.

Esto produce soluciones **subóptimas pero aceptables**.

Ejemplo:

* Algoritmo hace 1 millón de iteraciones.
* Explora aleatoriamente el espacio.
* Se guarda el **mejor resultado encontrado (best-so-far)**.
* Ese "best" no es necesariamente la óptima global, pero es una buena solución en tiempo razonable.

## Conclusiones

* La clave es **cómo representar el problema** (binario, entero, real, permutación).
* El tamaño del espacio de búsqueda crece muy rápido (exponencial o factorial).
* En la práctica, se aceptan soluciones subóptimas por limitaciones de tiempo.
* La optimización discreta es central en logística, asignación, transporte, planificación y problemas combinatorios.

## Estrategias para buscar dentro de configuraciones: Algoritmos Genéticos

Los **algoritmos genéticos (GA, Genetic Algorithms)** son una estrategia de búsqueda y optimización discreta que pertenecen a la familia de **algoritmos evolutivos**, inspirados en procesos biológicos de **selección natural y genética** (adaptación, selección, cruce, mutación).

La idea central:

* No buscar soluciones al azar en el espacio de búsqueda, sino hacerlo de manera **inteligente**.
* Se exploran con mayor intensidad las **regiones prometedoras** (con soluciones buenas).
* Se descartan o visitan menos las **regiones malas**.
* Se simula el principio de **supervivencia del más apto**: los mejores individuos sobreviven y transmiten sus genes, los peores mueren.

### Conceptos Básicos

* **Individuo**: una solución candidata dentro del espacio de búsqueda.
* **Población**: conjunto de individuos. Se representa como una matriz $n \times L$, donde:

  * $n$: número de individuos (tamaño de población, hiperparámetro).
  * $L$: longitud de la representación (depende del problema).
* **Cromosoma**: vector que representa un individuo (ejemplo: binario, entero, real o permutación).
* **Gen**: cada posición del cromosoma.
* **Alelo**: el valor particular de un gen.
* **Función objetivo (fitness function)**: mide la calidad de un individuo (qué tan bueno es).
* **Fitness**: valor de aptitud que determina qué tan "fuerte" es un individuo para sobrevivir y reproducirse.

### Funcionamiento General

Un GA trabaja sobre una **población inicial** $P_0$, que evoluciona en iteraciones llamadas generaciones:

$$
P_0 \to P_1 \to P_2 \to \dots \to P_t
$$

En cada generación:

1. Se evalúan los individuos con la función de **fitness**.
2. Se ordenan (ranking) de mejor a peor.
3. Se seleccionan los más aptos para reproducirse.
4. Se generan nuevos individuos mediante **cruce y mutación**.
5. La población se actualiza manteniendo el tamaño constante.

Los GA garantizan que siempre aparece un nuevo "mejor candidato" (best-so-far) y se guarda. Este **mejor individuo encontrado** se devuelve al final como la solución subóptima.

### Proceso en Detalle

#### 1. Evaluación y Ranking

Cada individuo $x$ se evalúa en la función de objetivo:

$$
F(x) \to \text{fitness}(x)
$$

Se ordena la población de mayor a menor aptitud:

* Los de arriba son más aptos.
* Los de abajo son menos aptos.

#### 2. Selección

Se decide qué individuos pasan a la siguiente generación. Estrategias comunes:

* **Corte fijo:** se eligen los mejores $m$.
* **Porcentaje:** se elige un % de la población.
* **Probabilística:** cada individuo tiene una probabilidad de ser elegido proporcional a su fitness.

Objetivo: dar más oportunidades a los aptos, pero sin eliminar del todo la diversidad.

#### 3. Cruce (Crossover)

Dos individuos "padres" combinan partes de sus cromosomas para producir descendencia:

* **Single-point crossover:** se corta en un punto aleatorio y se mezclan las mitades.
* **Two-point crossover:** se hacen dos cortes, generando tres bloques y recombinándolos.
* **Uniform crossover:** se eligen posiciones aleatorias de cada padre para formar el hijo.

El cruce genera nuevos individuos que heredan características de ambos padres.

#### 4. Mutación

Un individuo se modifica alterando aleatoriamente algunos genes, produciendo variación.

* Objetivo: introducir **diversidad** para evitar estancamiento.
* Ejemplo: en binario, invertir un bit; en enteros, sumar/restar un valor pequeño.

La combinación de **cruce y mutación** se controla con hiperparámetros:

$$
\% \text{cruce} + \% \text{mutación} = 100\%
$$

#### 5. Actualización de Población

* Los individuos menos aptos mueren.
* Los espacios vacíos se llenan con los nuevos descendientes generados.
* El **tamaño de población se mantiene constante**.

### Operadores Genéticos según Representación

Los operadores dependen de cómo se representen los cromosomas:

* **Binaria:** crossover y mutación de bits (ejemplo: flip de 0 a 1).
* **Entera:** mutar con suma/resta, cruzar por bloques.
* **Reales (float):** mutar con ruido gaussiano, cruzar promediando genes.
* **Permutaciones:** los operadores deben preservar la condición de no repetir valores (crossover tradicional no sirve, se requieren operadores especiales como PMX o OX).

### Esquema General de un GA

```bash
Población inicial P0
    ↓
Evaluación (fitness)
    ↓
Selección
    ↓
Cruce y Mutación
    ↓
Nueva Población P1
    ↓
Repetir hasta condición de parada
```

Condiciones de parada comunes:

* Número máximo de generaciones.
* Tiempo límite.
* Estancamiento (best no mejora en varias iteraciones).

### Importancia de la Variabilidad

* Si solo se explota una región del espacio, el algoritmo se **estanca**.
* La **mutación** mantiene diversidad genética.
* En un gráfico de evolución del fitness, el "best" debe seguir mejorando, no quedarse constante demasiado pronto.

### Salida del Algoritmo

* **Best-so-far:** el mejor individuo encontrado durante todas las generaciones.
* Es una **solución subóptima** (la mejor encontrada, no necesariamente la óptima global).
* Puede graficarse el valor de best en función de las generaciones para analizar convergencia.

### Resumen de Operadores

* **Selección:** da preferencia a los mejores (más fitness).
* **Cruce (Crossover):** mezcla información de dos padres.
* **Mutación:** modifica un individuo para mantener variabilidad.

Estos operadores se aplican en cada iteración para acercar a la población a regiones de mejores soluciones.

### Ejemplo con cadenas binarias (L = 8)

Padre 1: `10111001`
Padre 2: `01100111`

**Single-point crossover (corte en posición 4):**

* Hijo 1 = `1011 | 0111`
* Hijo 2 = `0110 | 1001`

**Mutación (flip en bit 6 del hijo 1):**

* Hijo 1 mutado = `10110111`

### Conclusión

Los **algoritmos genéticos** son una poderosa técnica de optimización discreta que:

* Permiten explorar grandes espacios de búsqueda.
* Encuentran soluciones subóptimas aceptables en tiempo razonable.
* Combinan explotación de buenas regiones y exploración de nuevas zonas gracias a mutación.
* Se adaptan a distintas representaciones (binaria, entera, real, permutaciones).
