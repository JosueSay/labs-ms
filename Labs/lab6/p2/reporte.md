# Simulación SIR como autómata celular en un grid $M\times N$

Pedirle a una IA que genera una simulación del modelo SIR mediante un autómata celular. Para ello, considere un grid rectangular de tamaño $M\times N$, en el cual cada celda del grid tiene, en todo momento de la simulación, exactamente uno de los estados siguientes:

- 0: susceptible (pertenece a la población $S$),
- 1: infectado (pertenece a la población $I$),
- 2: recuperado (pertenece a la población $R$).

En este caso, las celdas del grid cambiarán su estado en función de la proporción de celdas vecidas infectadas.

La siguiente figura ilustra lo que se espera de la simulación:

![Ejemplo simulación](../images/ej_p2.png)

Deberá proporcionarle a la IA un prompt bastante detallado, indicando todos los parámetros necesarios, para hacer que se genera una simulación que visualice el grid y las celdas con el color en función de su estado, y la dinámica de contagio dentro del grid.
Deberá generar también la visualización de cómo cambian las curvas de las cantidades $S(t)$, $I(t)$ e $R(t)$ en el tiempo. En ambas visualizaciones debe permitir que se visualice la dinámica de la propagación del contegio según el modelo SIR.

Generar una animación .gif o un video en formato .mp4 en el que se visualice la dinámica obtenida de esta simulación. Tome encuenta los siguientes parámetros:

- $M, N =$ altura y anchura del grid
- $I_0 =$ número inicial de infectados
- $T =$ tiempo total simulación
- $r =$ radio de la vecindad
- $\beta =$ tasa de infección
- $\gamma =$ tasa de recuperación

## Cómo llegamos a la solución

![Curvas de simulación 2](../images/sim2/sim2_curvas.png)

- [Enlace al gif generado](https://github.com/JosueSay/labs-ms/blob/main/Labs/lab6/images/sim2/sim2.gif)

Se trabajó siguiendo dos artefactos del proyecto: el prompt de especificación (`prompt.md`) y la implementación final (`sim2.py`). A continuación se resume el proceso y las decisiones principales.

1. Lectura del prompt (prompt.md)

- Se extrajeron los requisitos exactos: dimensiones del grid (M × N), I0, T, radio de vecindad r, tasas β y γ, formato de salida (animación .gif/.mp4) y la visualización simultánea del grid y las curvas S(t), I(t), R(t).
- Se definió el formato de los estados: 0=S (azul), 1=I (rojo), 2=R (verde) y el título informativo por frame:  
  t = {tiempo} | S = {susceptibles} | I = {infectados} | R = {recuperados}.

2. Diseño del modelo (decisiones tomadas)

- Modelo: autómata celular discreto en tiempo y espacio.
- Vecindad: Von Neumann con radio r = 1 (cuatro vecinos) — implementada sin borde periódico (bordes con menos vecinos).
- Reglas:
  - Susceptible → infectado con probabilidad p = β * (n_infectados / n_vecinos) si tiene vecinos infectados.
  - Infectado → recuperado con probabilidad γ.
  - Recuperado mantiene estado (inmune).
- Actualización: esquema síncrono (calcula transiciones sobre el estado actual y aplica todas a la vez).
- Reproducibilidad: semilla fija (SEED) para generar trayectorias replicables.

3. Implementación en sim2.py

- Funciones principales:
  - init_grid(M,N,I0): inicializa el grid con I0 infectados aleatorios.
  - von_neumann_shifts(grid): cuenta vecinos infectados en Von Neumann r=1.
  - neighbor_counts(M,N): calcula número efectivo de vecinos por celda (bordes).
  - step(grid, beta, gamma, neighbor_count): aplica las reglas y devuelve la nueva generación.
  - run_sim(...): ejecuta la simulación por T pasos, guarda grids y vectores S_hist, I_hist, R_hist; detiene temprano si I(t)=0 y rellena historiales hasta T.
- Visualización:
  - Matplotlib con `imshow` para el grid y curvas S/I/R en el panel derecho.
  - `FuncAnimation` actualiza ambos paneles en tiempo real.
  - Colormap consistente: azul (#3778bf) para S, rojo (#d62728) para I, verde (#2ca02c) para R.
- Salida:
  - Guarda animación como `simulacion_SIR.gif` usando PillowWriter; arreglos para guardar MP4 si ffmpeg está disponible.
  - Código incluye mecanismo para guardar un PNG (snapshot) del `fig` cuando se alcanza una condición deseada en t (se puede activar según prompt).

4. Verificación y ajustes

- Se verificaron historiales S(t), I(t), R(t) en cada paso y la conservación del número total de celdas (S+I+R = M·N).
- Parámetros de visualización (interval, fps) ajustados para obtener una animación fluida y legible para T grande.
- Se eligió no usar fronteras periódicas porque la dinámica en bordes es más representativa para muchos escenarios epidemiológicos en autómatas celulares.

5. Notas prácticas

- Cambiar parámetros (M, N, I0, T, r, β, γ, SEED) al inicio del archivo `sim2.py` para experimentar con escenarios.
- Para obtener la misma secuencia exacta (por ejemplo, para guardar el snapshot pedido en el prompt), fijar SEED y repetir la ejecución.
- Si la animación es demasiado pesada, reducir T o guardar solo cada k-ésimo frame.
