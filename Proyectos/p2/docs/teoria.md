# Base teórica

## **Supuestos del modelo $M/M/1$**

Para el desarrollo teórico y la posterior simulación del sistema de colas en un restaurante, se trabajará bajo los siguientes **supuestos fundamentales** del modelo $M/M/1$:

1. **Llegadas aleatorias:**
   Los clientes llegan de forma independiente y aleatoria, siguiendo una **distribución de Poisson** con tasa promedio $\lambda$. Esto implica que no existe un patrón fijo de llegada, pero sí un promedio constante de flujo de clientes por unidad de tiempo.

2. **Tiempos de servicio variables:**
   El tiempo que tarda el servidor en atender a un cliente sigue una **distribución exponencial** con tasa $\mu$, lo que significa que la mayoría de los servicios duran poco, aunque ocasionalmente pueden presentarse tiempos más largos.

3. **Un solo servidor:**
   Existe únicamente un punto de atención (por ejemplo, un mesero o una caja), por lo que los clientes deben esperar si el servidor está ocupado.

4. **Disciplina de atención FIFO:**
   Los clientes son atendidos en el orden en que llegan (**First In, First Out**), sin prioridad alguna.

5. **Capacidad del sistema infinita:**
   No hay límite en el número de clientes que pueden esperar; todos los que llegan permanecen en la cola hasta ser atendidos.

6. **Paciencia infinita de los clientes:**
   Ningún cliente abandona el sistema; todos esperan hasta recibir el servicio (no hay deserciones ni impaciencia).

7. **Población de llegadas infinita:**
   Se asume que el número potencial de clientes es muy grande, de modo que la llegada de uno no afecta la probabilidad de llegada de los demás.

8. **Estacionariedad de parámetros:**
   Las tasas $\lambda$ y $\mu$ permanecen constantes durante la simulación (no hay variaciones horarias ni cambios en la velocidad de atención).

9. **Independencia de eventos:**
   Las llegadas y los tiempos de servicio son independientes entre sí; el tiempo de atención de un cliente no influye en el siguiente.

## **1. Fundamento teórico**

La **teoría de colas** se encarga de estudiar cómo se comportan los sistemas donde las personas o “clientes” deben **esperar su turno** para recibir un servicio. Este tipo de análisis permite entender **cuánto tiempo espera cada cliente**, **cuántos hay en la fila** y **qué tan ocupado está el servidor** (por ejemplo, un mesero, cajero o empleado).

El modelo **$M/M/1$** es el más básico y común de estos sistemas.

Los clientes **no llegan de forma constante**, sino de manera **aleatoria**.
Esa variación se describe mediante una **distribución de Poisson**, que es una forma matemática de representar **cuántos clientes llegan en cierto tiempo promedio ($\lambda$)**.

En palabras simples:

- La distribución de Poisson **no supone un ritmo fijo** (no es un cliente cada minuto exacto), sino que **las llegadas ocurren al azar**, aunque en promedio se mantenga una cantidad por hora.
- Por ejemplo, si $\lambda = 10$, significa que **en promedio llegan 10 clientes por hora**, pero puede que un día lleguen 8, otro 12, o incluso haya minutos con 3 clientes seguidos y luego un lapso sin ninguno.
- En general, **no hay “picos iniciales” ni horas muertas predefinidas** dentro de un mismo intervalo corto; las llegadas se distribuyen irregularmente a lo largo del tiempo.

Por otro lado, el **tiempo de atención o servicio** de cada cliente **también varía**. Algunos clientes pueden tardar menos (por ejemplo, solo piden un café), y otros más (una familia completa).
Esa variación se representa con una **distribución exponencial**, que significa que:

- La mayoría de los servicios **tienen duraciones cortas**, pero ocasionalmente aparece un servicio más largo.
- No hay un patrón fijo: el tiempo que tarda en atenderse al siguiente cliente **no depende** de cuánto se tardó el anterior.
- Si la tasa promedio de atención es $\mu = 12$, significa que el servidor **atiende, en promedio, 12 clientes por hora**, aunque unos tarden más y otros menos.

Finalmente, hay **un solo servidor** que atiende a los clientes **en orden de llegada**, siguiendo la regla **FIFO (First In, First Out)**, es decir: el primero que entra al sistema es el primero en ser atendido.

Las fórmulas principales del modelo son:

$$
\rho = \frac{\lambda}{\mu}, \quad
L = \frac{\rho}{1-\rho}, \quad
L_q = \frac{\rho^2}{1-\rho}, \quad
W = \frac{1}{\mu - \lambda}, \quad
W_q = \frac{\lambda}{\mu(\mu - \lambda)}
$$

A continuación, se explica cada una de ellas en términos sencillos:

- **$\rho$ (rho)** → Representa qué tan ocupado está el servidor.
  Es la **relación entre la cantidad de clientes que llegan y los que puede atender**.
  Si $\rho$ se acerca a 1, significa que el servidor está ocupado casi todo el tiempo (hay mucha demanda).
  Si $\rho$ es pequeño, el servidor pasa parte del tiempo sin atender a nadie.

- **$L$** → Es el **número promedio de clientes dentro del sistema**, incluyendo los que están siendo atendidos y los que esperan en la cola.
  Por ejemplo, si $L = 5$, en promedio hay 5 personas entre la fila y la atención.

- **$L_q$** → Es el **número promedio de clientes que están únicamente en la cola**, esperando su turno.
  Este valor crece rápidamente si llegan muchos clientes o si el servidor se demora en atender.

- **$W$** → Es el **tiempo promedio total que un cliente pasa en el sistema**, desde que llega hasta que se va (tiempo de espera + tiempo de servicio).
  Por ejemplo, si $W = 6$ minutos, significa que, en promedio, un cliente pasa 6 minutos en todo el proceso.

- **$W_q$** → Es el **tiempo promedio de espera antes de ser atendido**, sin incluir el tiempo de servicio.
  Este valor depende de qué tan saturado esté el sistema: si hay muchos clientes llegando o el servidor trabaja lento, el tiempo de espera crece.

En conjunto, estas ecuaciones muestran **cómo el equilibrio entre la llegada de clientes ($\lambda$)** y la **velocidad de atención ($\mu$)** afecta la eficiencia del servicio.
El modelo $M/M/1$ se usa ampliamente en estudios de **restaurantes, bancos o centros de atención**, ya que ayuda a **predecir tiempos de espera y optimizar recursos** sin necesidad de medir cada cliente en la práctica.

## **2. Parámetros esenciales**

Para la simulación básica sin casos especiales (sin abandono ni múltiples servidores) se requieren los siguientes parámetros:

1. **Tasa de llegada ($\lambda$):** número promedio de clientes que llegan por unidad de tiempo.
2. **Tasa de servicio ($\mu$):** número promedio de clientes atendidos por unidad de tiempo.
3. **Tiempo total de simulación:** duración del periodo simulado (por ejemplo, una jornada de 6–8 horas).
4. **Disciplina de servicio:** FIFO.
5. **Capacidad del sistema:** infinita (no se rechazan clientes).
6. **Número de servidores:** 1.
7. **Distribuciones utilizadas:** llegadas $\sim$ Poisson, servicio $\sim$ Exponencial.

Con estos parámetros se puede caracterizar completamente el comportamiento dinámico del sistema y garantizar estabilidad si $\rho < 1$.

## **3. Metodología para la simulación**

Basada en los estudios de Yadav & Sohani (2019), Naotunna et al. (2019) y Kim et al. (2020):

1. **Definir los parámetros iniciales**: tasas $\lambda$ y $\mu$, y el tiempo total de operación.
2. **Generar llegadas aleatorias** según una distribución de Poisson con parámetro $\lambda$.
3. **Generar tiempos de servicio** usando una distribución exponencial con parámetro $\mu$.
4. **Ejecutar el proceso de eventos discretos:**

   - Si el servidor está libre → el cliente inicia servicio.
   - Si el servidor está ocupado → el cliente entra en la cola.
5. **Actualizar variables del sistema**: longitud de cola, estado del servidor, tiempo actual.
6. **Registrar métricas clave** ($W$, $W_q$, $L$, $L_q$, $\rho$) a lo largo de la simulación.
7. **Comparar resultados simulados vs teóricos**, para verificar la validez del modelo.

## **4. Datos requeridos**

Para tener una base sólida antes de programar, se deben recolectar los siguientes datos empíricos:

- Promedio de llegadas por hora ($\lambda$).
- Promedio de tiempo de servicio ($1/\mu$).
- Horas de operación del restaurante.
- Posible variación horaria (por ejemplo, horas pico vs horas valle).

Estos datos permitirán calibrar el simulador y validar que $ \lambda < \mu $, lo que garantiza que el sistema sea estable y no crezca indefinidamente la cola.

## **5. Representación esperada en la simulación**

En la ejecución de la simulación se debe observar:

- **Evolución temporal de la cola ($L_q(t)$):** crecimiento y decrecimiento del número de clientes esperando.
- **Ocupación del servidor ($\rho$):** proporción del tiempo que el servidor está activo.
- **Tiempos de espera ($W_q$)** y **tiempo total en sistema ($W$)** para cada cliente.
- **Promedios y varianzas** de los indicadores al final del periodo.
- **Comparación de valores teóricos y simulados**: las diferencias deberían disminuir al aumentar el tiempo o el número de repeticiones.

Visualmente, pueden mostrarse gráficas de:

- Clientes en cola vs tiempo.
- Tiempo promedio de espera vs $\lambda$.
- Relación entre $\rho$ y $W_q$.

## **6. Qué se debe observar teóricamente en los resultados**

De acuerdo con la teoría:

- Si **$\lambda$ se aproxima a $\mu$**, la utilización $\rho$ tiende a 1, y los valores de $L$, $L_q$, $W$ y $W_q$ crecen exponencialmente.
- Si **$\lambda \ll \mu$**, el servidor pasa mucho tiempo ocioso, y las colas y tiempos de espera son mínimos.
- La relación entre los indicadores cumple las identidades de Little:
  $$
  L = \lambda W, \quad L_q = \lambda W_q
  $$
- En equilibrio, se debe verificar que:
  $$
  W_q = \frac{\lambda}{\mu(\mu - \lambda)} \quad \text{y} \quad W = W_q + \frac{1}{\mu}
  $$
- La simulación debería reproducir estos comportamientos de forma aproximada, confirmando la validez del modelo $M/M/1$.

> La simulación del sistema de colas $M/M/1$ para un restaurante permitirá observar, de forma teórica y empírica, cómo las variaciones en las tasas de llegada y servicio afectan la eficiencia del sistema, los tiempos de espera y la utilización del servidor. Este análisis proporcionará una base sólida antes de implementar el código y garantizará que los resultados simulados se comporten conforme a la teoría de colas.
