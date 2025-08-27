# TODO — GA para TSP (TSPLIB con coordenadas)

## Módulo A — Parsing

**Input:** archivo TSPLIB con `NODE_COORD_SECTION`.

**Output:** $\mathcal{C}={(x_i,y_i)}_{i=1}^n$, $n=$ DIMENSION.

**Decisión:** leer **siempre** coordenadas y validarlas (sin “opcional”).

### Módulo B (actualizado)

**Input:** $\mathcal{C}$, `EDGE_WEIGHT_TYPE=EUC_2D`.

**Cálculo (TSPLIB):** $d_{ij}=\left\lfloor \sqrt{(x_i-x_j)^2+(y_i-y_j)^2}+0.5\right\rfloor$.

**Output (elige 1):**

* **A:** $D\in\mathbb{N}^{n\times n}$ (simétrica). Memoria $O(n^2)$.

* **B:** estructura triangular $T$ con accesor $d(i,j)$. Memoria $O\!\left(\tfrac{n(n-1)}{2}\right)$.
  **Complejidad:** tiempo $O(n^2)$ en ambos; memoria según A o B.

Para tu GA y visualización nada más cambia: en B sustituye toda lectura $D[i,j]$ por $d(i,j)$.

## Módulo C — Representación

**Variable:** individuo $\pi=[\pi_1,\ldots,\pi_n]\in S_n$ (permutación).

**Espacio muestral:** $|S_n|=n!$ (o $(n-1)!$ si fijas inicio).&#x20;

**Decisión:** **siempre** permutaciones (no binaria/entera/float).

## Módulo D — Objetivo/Fitness

**Input:** $\pi$, $D$.

**Costo del tour:**

$L(\pi)=\sum_{k=1}^{n-1} d_{\pi_k,\pi_{k+1}}+d_{\pi_n,\pi_1}.$

**Fitness (estable):** ranking o $f(\pi)=1/(\varepsilon+L(\pi))$.

**Output:** $L(\pi)$, $f(\pi)$.

**Costo:** $O(n)$ por individuo.

## Módulo E — Inicialización (diversidad obligatoria)

**Input:** $n, N$.

**Parámetros (determinados):**

* Proporción aleatoria pura: $80%$.
* Semillas heurísticas débiles (p. ej., nearest-neighbor) + **shuffle fuerte**: $20%$.

  **Regla anti-concentración:** si Hamming medio entre individuos $< \theta_H$ (umbral), **rehacer** los últimos añadidos; usar $\theta_H=0.2n$.

  **Output:** población $P^{(0)}={\pi^{(0)}_1,\ldots,\pi^{(0)}_N}$.

  **Decisión:** **siempre** aplicar chequeo de diversidad en esta fase.&#x20;

## Módulo F — Evaluación (por generación)

**Input:** $P^{(t)}$, $D$.

**Output:** ${L(\pi)}$, ranking, $best^{(t)}$.

**Se itera:** en **todas** las generaciones.

## Módulo G — Selección (presión controlada)

**Input:** $P^{(t)}$, fitness.

**Parámetros (determinados):**

* **Elitismo:** $e=2%$ (redondeo $\ge1$).
* **Supervivientes:** $s=30%$ (ranking truncation).
* **Padres (para cruce):** torneo con $k=3$ (sin reemplazo).
* **Umbral de concentración:** si $\text{std}(L)$ de $P^{(t)}$ $< \theta_L$ (p. ej. $0.02\cdot \overline{L}$), **bajar** momentáneamente $k$ a $2$ y **subir** mutación (ver Módulo I).

  **Output:** $S^{(t)}$ (supervivientes) y multiconjunto de padres.

  **Decisión:** **siempre** torneo+truncation (no ruleta).&#x20;

## Módulo H — Cruce (válido para permutaciones)

**Input:** padres.

**Parámetros (determinados):** fracción de cruce $c=60%$ de la nueva población.

**Operadores (mezcla fija):** $50%$ OX + $50%$ PMX; reparar hasta permutación válida.

**Output:** $C^{(t)}$ (hijos por cruce).

**Decisión:** **siempre** OX/PMX (no uniform/single-point genérico).&#x20;

## Módulo I — Mutación (exploración obligatoria)

**Input:** $S^{(t)}\cup C^{(t)}$.

**Parámetros (determinados):** fracción de mutación $m=20%$ de la nueva población; prob. por individuo $p=0.3$.

**Operadores (mezcla fija):**

* $40%$ **swap**, $30%$ **insert**, $30%$ **inversion (2-opt move)**.
  **Escalado adaptativo (anticoncentración, determinista por regla):**
* Si **no mejora** $best$ en $\tau=200$ generaciones: set $p\leftarrow \min(0.6, p+0.1)$ y $m\leftarrow \min(0.35, m+0.05)$ **durante** las próximas $T_{boost}=100$ generaciones.

  **Output:** $MUT^{(t)}$.

  **Decisión:** **siempre** mutar con esta política (no opcional).&#x20;

## Módulo J — Ensamblaje de población

**Input:** élites $\subset S^{(t)}$, $S^{(t)}$, $C^{(t)}$, $MUT^{(t)}$.

**Regla (determinada):** esquema **generacional con elitismo**:

1. Copiar élites. 2) Rellenar con mejores de $S^{(t)}\cup C^{(t)}\cup MUT^{(t)}$ hasta tamaño $N$.
   **Umbral anti-clones:** si un nuevo individuo es idéntico a algún miembro actual de $P^{(t+1)}$, **forzar una mutación extra** (una sola vez).

   **Output:** $P^{(t+1)}$.

## Módulo K — Paro y logging

**Parámetros (determinados):**

* $\text{maxIter}$ (obligatorio).
* Estancamiento: si $best$ no mejora por $\tau=500$ generaciones, **parar**.
  **Logs fijos por $t$:** $L_{best}^{(t)}$, índice del best, y métricas de diversidad (Hamming medio, $\text{std}(L)$).

  **Output:** historial y $best$ final.

## Módulo L — Visualización de resultados

**Input:** $\pi^*=\arg\min L(\pi)$, $\mathcal{C}$, historial $L_{best}^{(t)}$.

**Salida (obligatoria):**

* Mapa con el tour final $\pi^*$ trazado sobre $(x_i,y_i)$.
* Curva $t\mapsto L_{best}^{(t)}$.

  **Decisión:** **siempre** generar ambas figuras (no GIF si no es requisito estricto).

## Parámetros iniciales recomendados (determinados)

* **Berlin52 ($n=52$):** $N=200$, $c=60%$, $m=20%$, $e=2%$, $s=30%$, torneo $k=3$, $p=0.3$, $\tau=200$, $\theta_H=0.2n$, $\theta_L=0.02\overline{L}$.
* **Escala \~500 ciudades:** $N=600$, $c=65%$, $m=30%$, $p=0.4$, mismos umbrales pero revisar memoria ($D$ de $500\times500$).

## Flujo por generación (obligatorio)

1. **Evaluar** $L(\pi)$ en $P^{(t)}$.
2. **Seleccionar** élites ($2%$), supervivientes ($30%$) y **padres por torneo** ($k=3$).
3. **Cruzar** (OX/PMX) hasta cubrir $c$ de la población.
4. **Mutar** $m$ con mezcla (swap/insert/inversion) y prob. $p$; aplicar boost si toca.
5. **Ensamblar** $P^{(t+1)}$ con anti-clones.
6. **Log** y chequear paro/umbral de concentración.

## Complejidades (para tener claro el costo)

* Construir $D$: $O(n^2)$ (una vez).
* Evaluar población/iteración: $O(Nn)$.
* OX/PMX/Mutación por individuo: $O(n)$ típico.&#x20;
