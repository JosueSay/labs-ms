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
