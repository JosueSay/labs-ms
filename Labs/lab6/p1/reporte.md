# Simulación SIR con partículas móviles en $[0,L]\times[0,L]$

Pedirle a una IA que genera una simulación del modelo SIR mediante un sistema de partículas, moviéndose dentro de una región rectangular $[0,L]\times[0,L]$ en el plano $\mathbb{R}^2$, en la cual hay $N$ partículas, que en todo momento de la simulación, se mueven a una velocidad lineal constante, y tienen cada una exactamente uno de los estados siguientes:

* 0: susceptible (pertenece a la población $S$)
* 1: infectado (pertenece a la población $I$)
* 2: recuperado (pertenece a la población $R$)

La siguiente figura ilustra lo que se espera de la simulación:

![Ejemplo gráfica](../images/ej_p1.png)

Deberá proporcionarle a la IA un prompt bastante detallado, indicando todos los parámetros necesarios, para hacer que se genera una simulación que visualice las partículas, las interacciones entre ellas, y que las partículas cambian de color conforme cambian de estado.
Asimismo, deberá generar una visualización de cómo cambian las curvas de las cantidades $S(t)$, $I(t)$ e $R(t)$ en el tiempo. En ambas visualizaciones debe permitir que se visualice la dinámica de la propagación del contegio según el modelo SIR.

Finalmente, deberá generar una animación .gif o un video en formato .mp4 en el que se visualice la dinámica obtenida de esta simulación. Tome encuenta los siguientes parámetros:

* $L =$ tamaño del cuadrado
* $N_{total} =$ población total de partículas
* $I_0 =$ número inicial de infectados
* $v_{max} =$ velocidad máxima
* $r =$ radio de contagio
* $\beta =$ tasa de infección
* $\gamma =$ tasa de recuperación
* $dt =$ delta de tiempo
