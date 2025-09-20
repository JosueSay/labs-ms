# Problema 5

Considere una población de una especie de animales $P(t)$ que se modela por la ecuación diferencial

$$
\frac{dP}{dt}=0.0004\,P^{2}-0.06\,P. \tag{4}
$$

Suponga que la escala de tiempo $t$ se mide en **semanas**, mientras que la escala de la población $P$ se mide en **individuos** (número de individuos).

## Inciso a

Determinar las dimensionales correctas de los parámetros $0.0004$ y $0.06$.  

**¿Cómo se hizo?**  
Se compararon las unidades del lado izquierdo $(dP/dt)$, que son $[\text{individuos}/\text{semana}]$, con cada término del lado derecho.

**¿Qué se encontró?**  
El coeficiente $0.06$ tiene unidades $\text{semana}^{-1}$.  
El coeficiente $0.0004$ tiene unidades $(\text{individuo} \cdot \text{semana})^{-1}$.

## Inciso b

Hacer un análisis de los puntos de equilibrio de la EDO (4), y clasificarlos de acuerdo a si son **estables**, **inestables** o **semi-estables**.  

**¿Cómo se hizo?**  
Se resolvió $0.0004P^2-0.06P=0$ y luego se evaluó la derivada $f'(P)=0.0008P-0.06$ en cada equilibrio.

**¿Qué se encontró?**  
Equilibrios: $P^*=0$ y $P^*=150$.  
$P^*=0$: estable (atractor).  
$P^*=150$: inestable (repulsor).

## Inciso c

Derivado del análisis anterior, hacer un esbozo de las soluciones $P(t)$, indicando la región donde dichas soluciones son constantes, crecientes o decrecientes, y las regiones donde las soluciones $P(t)$ tienen concavidad positiva, negativa o tienen máximos o mínimos.  

**¿Cómo se hizo?**  
Se analizaron los signos de $dP/dt$ en los intervalos $(0,150)$ y $(150,\infty)$. Además se resolvió numéricamente para distintas condiciones iniciales ($P(0)=10,50,100,200$).

**¿Qué se encontró?**  
Para $P(0)<150$: la población decrece y tiende a $0$.  
Para $P(0)>150$: la población crece sin límite en tiempo finito (explosión).  
El punto $P=150$ separa los dos comportamientos.

## Inciso d

Suponga que la población en el tiempo $t=0$ es $P(0)=200$ individuos. Describir cuál será el comportamiento a futuro de $P(t)$ si la población se rige por el modelo (4).  

**¿Cómo se hizo?**  
Se obtuvo la solución explícita por separación de variables y se calculó el tiempo de explosión $t^*$.

**¿Qué se encontró?**  
La población diverge a infinito en tiempo finito.  
El tiempo crítico de explosión es aproximadamente $t^* \approx 23.1$ semanas.

## Inciso e

Repetir el análisis cualitativo en (d) asumiendo que la población en el tiempo $t=0$ es $P(0)=100$ individuos.  

**¿Cómo se hizo?**  
Se resolvió numéricamente con solve_ivp y se graficó la trayectoria.

**¿Qué se encontró?**  
La población decrece rápidamente y tiende a $P=0$.  
En unas 60–70 semanas la población es prácticamente nula.

## Inciso f

Resolver la EDO (4) y graficar las curvas solución de los problemas en (d) y (e), para mostrar en la gráfica que la solución coincide con la descripción de su análisis cualitativo.

**¿Cómo se hizo?**  
Se resolvió numéricamente con solve_ivp y se comparó con los equilibrios.

**¿Qué se encontró?**  
Aunque la población inicial está cerca de 150, como es menor la dinámica la lleva lentamente hacia $P=0$.  
La extinción ocurre de manera mucho más lenta que en el caso $P(0)=20$, mostrando que el equilibrio $P^*=150$ funciona como frontera crítica.