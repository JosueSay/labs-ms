# Documentación sobre Algoritmos Genéticos (GA)

En la última clase se habló sobre **algoritmos genéticos (GA)**, sus generalidades dentro de la **optimización discreta**, y las distintas formas de representación de los individuos:

* **Vectores o matrices** con valores:

  * **Enteros**
  * **Binarios**
  * **Floats (reales)**
* **Permutaciones** (comunes en problemas de rutas o asignación).

La idea de un GA va evolucionando y adaptándose según el problema, ajustando parámetros y operadores.

## Parámetros fundamentales de un GA

1. **n (tamaño de la población):**
   Define cuántos individuos se mantienen en cada generación.

2. **% de selección:**
   Determina cuántos individuos sobreviven (o, equivalentemente, cuántos mueren).

3. **% de cruce y % de mutación:**
   Una vez seleccionados los individuos que sobrevivirán, el GA debe llenar el resto de la población aplicando operadores de **cruce** y **mutación** en proporciones específicas.

4. **Esquemas de selección y ranking:**

   * Se utilizan distribuciones o rankings para decidir qué individuos pasan a la siguiente generación.
   * Ejemplo: los mejores se seleccionan con mayor probabilidad, y los menos aptos con menor probabilidad.

## Operadores de cruce

Los operadores de cruce son los que generan nuevos individuos a partir de pares de padres. Entre los más comunes:

* **Single point crossover**
* **Two point crossover**
* **Uniform crossover**

Estos funcionan bien para representaciones binarias, enteras y en floats.

Sin embargo, para **permutaciones** estos cruces básicos no funcionan directamente, ya que podrían producir duplicados o perder elementos (lo cual rompe la naturaleza de una permutación).

### Cruce en representaciones continuas (floats)

Un operador especial es la **combinación lineal** entre dos individuos:

1. Se toman dos individuos (puntos en el espacio de búsqueda).
2. Se define un parámetro aleatorio **α** tal que:

   $$
   0 < \alpha < 1
   $$
3. El nuevo individuo se construye como:

   $$
   x_{\text{new}} = \alpha x + (1 - \alpha) y
   $$

Esto equivale a generar un punto intermedio entre ambos padres, similar a un promedio ponderado.

* **Importante:** solo se aplica en representaciones **reales (floats)**.
* En enteros o binarios no se puede usar directamente este esquema, ya que se perdería la validez de la representación.

Una estrategia interesante es **mezclar operadores de cruce** para que el GA utilice varios de forma aleatoria, enriqueciendo la exploración del espacio.

## Operadores de mutación

La mutación introduce variabilidad en la población, permitiendo escapar de óptimos locales. Su analogía biológica es la modificación de genes de forma leve.

Regla general:

* La mutación **no debe ser drástica**, sino afectar solo una parte pequeña del individuo.

### Casos

1. **Individuos binarios:**

   $$
   x = [0,1,0,1,0,...,0]
   $$

   * **Mutación de 1 bit:** Se selecciona un bit aleatorio y se invierte.
     Ejemplo: si $i = 3$,

     $$
     x_{\text{new}} = [0,1,1,1,0,...,0]
     $$
   * **Mutación de 2 bits:** Igual que la anterior, pero afectando dos posiciones distintas.

2. **Individuos enteros:**

   $$
   x = [5,2,1,0,4,4,3]
   $$

   Se puede aplicar:

   * **Incremento/decremento controlado:**

     $$
     x_{\text{new}} = [5,2,1,0,5,4,3] \quad \text{(se sumó 1 en la posición 5)}
     $$
   * En general, sumar o restar un valor $c$ con restricción:

     $$
     -r \leq c \leq r
     $$

     Esto asegura que los valores no salgan del rango permitido.

3. **Individuos tipo permutación:**
   Ejemplo:

   $$
   x = [7,4,1,5,3,2,6]
   $$

   Aquí se debe evitar repetir elementos. Operadores comunes:

   * **2-swap:** se eligen dos posiciones al azar y se intercambian.

     $$
     x_{\text{new}} = [7,4,3,5,1,2,6]
     $$
   * **3-swap:** intercambio de tres posiciones.
   * **Shuffle:** se selecciona un bloque (ej. posiciones 1 a 2) y se realiza un corrimiento o rotación dentro de ese bloque.

## Cruce en permutaciones

Para garantizar que el resultado siga siendo una permutación válida se usan operadores específicos, como:

1. **PMX (Partially Mapped Crossover):**

   * Se selecciona un bloque en ambos padres.
   * Se mapea cada elemento del bloque entre los padres.
   * Se llena el resto del hijo respetando ese mapeo, evitando duplicados.

   Ejemplo:

   ```bash
   x = [1,2,3,4,5,6,7,8]
   y = [3,7,5,1,6,8,2,4]
   ```

   Seleccionando los bloques:

   * x: \[4,5,6]
   * y: \[1,6,8]
     El hijo resultante se construye aplicando los mapeos:

   $$
   4 \leftrightarrow 1, \quad 5 \leftrightarrow 6, \quad 6 \leftrightarrow 8
   $$

   Resultado:

   $$
   off = [4,2,3,1,6,8,7,5]
   $$

2. **Cruce cíclico:**

   * Se selecciona un bloque del segundo individuo.
   * Luego se van agregando los elementos restantes siguiendo el orden del primer individuo, evitando duplicados.
   * Ejemplo:

     $$
     off = [3,4,5,1,6,7,8,2]
     $$

## Ejemplo con cadenas (Fitness con distancia de Hamming)

Cuando los individuos son **cadenas de texto**, se puede usar la **distancia de Hamming** como función de aptitud (fitness):

$$
d(x,y) = \sum_{i=1}^n \begin{cases}  
0 & x_i = y_i \\  
1 & x_i \neq y_i  
\end{cases}
$$

* Se transforma la cadena en **enteros (códigos ASCII)** en lugar de trabajar con strings.
* El GA generará cadenas aleatorias.
* Las más cercanas a la **cadena objetivo** (target) tendrán mayor probabilidad de sobrevivir.

## Implementación y buenas prácticas

1. **Inicialización de la población:**
   Generar individuos iniciales de forma aleatoria, respetando las restricciones de representación.

2. **Ciclo principal:**

   * Cruce: $(x_1, x_2) \to x_{\text{new}}$
   * Mutación: $x \to x_{\text{new}}$
   * Selección de los mejores (ranking, ruleta, torneo, etc.).

3. **Logging:**
   Una buena práctica es registrar solo cuando el mejor individuo mejora, para no saturar de información.

4. **Visualización:**
   Se pueden generar **GIFs** que muestren la evolución de las soluciones y cómo el GA va acercándose a la solución óptima.
