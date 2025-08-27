# Workflow de GA para TSP (TSPLIB con coordenadas)

## Módulo A — Parsing de datos

**Entrada:** archivo TSPLIB con `NODE_COORD_SECTION`.
**Salida:** lista de coordenadas $\mathcal{C}=\{(x_i,y_i)\}_{i=1}^n$, $n=\text{DIMENSION}$.

**Notas:** si el input fuera una matriz ya dada, saltas al Módulo B y tomas $D$ directo.

## Módulo B — Construcción de distancias

**Entrada:** $\mathcal{C}$.
**Parámetros:** `EDGE_WEIGHT_TYPE` (aquí EUC\_2D).
**Cálculo:**

$$
d_{ij} \;=\; \left\lfloor \sqrt{(x_i-x_j)^2+(y_i-y_j)^2}\;+\;0.5 \right\rfloor
\quad\text{(convención TSPLIB redondeada)}
$$

**Salida:** matriz simétrica $D=[d_{ij}] \in \mathbb{N}^{n\times n}$, $d_{ii}=0$.

**Complejidad (una sola vez):** $O(n^2)$ tiempo y memoria.

## Módulo C — Representación y factibilidad

**Variable (individuo):** permutación $\pi = [\pi_1,\ldots,\pi_n] \in S_n$.
**Tour:** ciclo que cierra en $\pi_1$.
**Espacio de búsqueda:** $|S_n|=n!$ (o $(n-1)!$ si fijas ciudad inicial).

## Módulo D — Función objetivo / Fitness

**Entrada:** $\pi$, $D$.
**Costo del tour:**

$$
L(\pi) \;=\; \sum_{k=1}^{n-1} d_{\pi_k,\pi_{k+1}} \;+\; d_{\pi_n,\pi_1}
$$

**Fitness típico (min→max):** $f(\pi)=1/\big( \varepsilon+L(\pi)\big)$ o ranking.
**Salida:** $L(\pi)$ y/o $f(\pi)$.
**Costo por evaluación:** $O(n)$.

## Módulo E — Inicialización de población

**Entrada:** $n, N$ (tamaño de población).
**Estrategia:** permutaciones aleatorias (opcional: pocas semillas “greedy” + shuffle).
**Salida:** $P^{(0)}=\{\pi^{(0)}_1,\ldots,\pi^{(0)}_N\}$ válida.
**No hay iteración aquí.**

## Módulo F — Selección (supervivientes y/o padres)

**Entrada:** $P^{(t)}$, $f(\cdot)$.
**Parámetros:** proporción de **supervivientes** $s\in(0,1)$, elitismo $e$, esquema (torneo $k$, ranking).
**Salida:** subconjuntos para:

* **Supervivencia:** $S^{(t)}\subset P^{(t)}$ (incluye élites).
* **Padres:** $M^{(t)}$ para cruce.

**Se itera en cada generación $t=0,1,\dots$.**

## Módulo G — Cruce (recombinación para permutaciones)

**Entrada:** $M^{(t)}$.
**Parámetros:** fracción de cruce $c\in(0,1)$, operador (PMX/OX/ERX).
**Proceso:** formar parejas $\to$ generar hijos $\{\hat{\pi}\}$ preservando validez (sin duplicados).
**Salida:** conjunto $C^{(t)}$ de hijos por cruce.

**Se itera en cada $t$.** Tamaño aproximado $|C^{(t)}| \approx c\,N$.

## Módulo H — Mutación (exploración)

**Entrada:** población candidata (p. ej., $C^{(t)}$ y/o parte de $S^{(t)}$).
**Parámetros:** fracción de mutación $m\in(0,1)$, operadores (swap, insert, inversion/2-opt-move), prob. por individuo.
**Salida:** conjunto $MUT^{(t)}$ de individuos mutados.

**Se itera en cada $t$.** Tamaño $|MUT^{(t)}|\approx m\,N$.

## Módulo I — (Opcional) Mejora local ligera

**Entrada:** élites o subconjunto de $\{C^{(t)}\cup MUT^{(t)}\}$.
**Operador:** 2-Opt acotado (pocos pasos) sobre $L(\pi)$.
**Salida:** versiones mejoradas $\tilde{\pi}$ con menor $L$.
**Itera en cada $t$** con límite de tiempo/pasos.

## Módulo J — Reinyección de diversidad

**Trigger:** si no mejora el best por $\tau$ iteraciones.
**Acción:** reemplazar $r\%$ de la peor parte por permutaciones nuevas o subir temporalmente la tasa de mutación.
**Salida:** $P^{(t)}$ más diverso.
**Itera “a demanda”.**

## Módulo K — Ensamblaje de la nueva población

**Entrada:** $S^{(t)}$, $C^{(t)}$, $MUT^{(t)}$, mejoras locales, reinyectados.
**Regla:** mantener tamaño $N$ (p. ej., esquema generacional con elitismo).
**Salida:** $P^{(t+1)}$.
**Itera en cada $t$.**

## Módulo L — Control de paro y logging

**Criterios:**

* Iteraciones máximas: $t \ge \text{maxIter}$.
* Estancamiento: $\min L$ no mejora en $\tau$ generaciones.
* (Opcional) límite de tiempo.
  **Logging:** registrar $L_{\text{best}}^{(t)}=\min_{\pi\in P^{(t)}} L(\pi)$ y $\pi_{\text{best}}^{(t)}$.

## Módulo M — Visualización y métricas

**Entrada:** $\pi_{\text{best}}^{(t)}$, $\mathcal{C}$, historial $L_{\text{best}}^{(t)}$.
**Salidas:**

* **Mapa del tour:** líneas en orden $\pi_{\text{best}}^{(t)}$ usando $(x_i,y_i)$.
* **Curva de convergencia:** $t \mapsto L_{\text{best}}^{(t)}$.
* **GIF:** capturas cada $\Delta t$ para mostrar evolución.

## Vista de “ciclo” completo por generación

1. **Evaluar** $L(\pi)$ $\forall \pi\in P^{(t)}$.
2. **Seleccionar** $S^{(t)}$ (con élites) y **padres** $M^{(t)}$.
3. **Cruzar** $M^{(t)} \to C^{(t)}$.
4. **Mutar** subconjunto $\to MUT^{(t)}$.
5. **(Opc.) Mejorar** 2-Opt ligero.
6. **Reinyectar** si aplica.
7. **Ensamblar** $P^{(t+1)}$.
8. **Log/Visual** $L_{\text{best}}^{(t)}$, $\pi_{\text{best}}^{(t)}$.

## Parámetros expuestos al usuario (resumen)

* $N$ (población), $\text{maxIter}$, elitismo $e$, supervivientes $s$, cruce $c$, mutación $m$.
* Esquemas: torneo $k$ o ranking; operador de cruce (PMX/OX/ERX); operadores de mutación; $\tau$ (estancamiento), $\Delta t$ (frecuencia de visual).

## Costos clave

* **Construir $D$:** $O(n^2)$ (una vez).
* **Evaluar un tour:** $O(n)$.
* **Evaluar una población por iteración:** $O(Nn)$.
* **Cruce/Mutación por individuo:** $O(n)$ típico (depende del operador).

## Resultado final

**Salida global:**

* Mejor tour $\pi^*$ y su distancia $D^* = L(\pi^*)$.
* Gráficos (tour final y curva de convergencia) y, opcional, GIF de evolución.

### Por qué las coordenadas y cuándo se usan

* **Al inicio:** $\mathcal{C}\to D$ (una sola vez).
* **Durante el GA:** solo $D$ y permutaciones.
* **Para visualizar:** $\mathcal{C}$ para dibujar $\pi_{\text{best}}$ en el plano.
