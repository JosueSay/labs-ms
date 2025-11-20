# Proyecto 1

Este proyecto tiene como objetivo diseñar e implementar un algoritmo genético para resolver un problema TSP y compararlo con una solución de programación lineal.

## Integrantes

- Abby Donis
- Cindy Gualim
- Josué Say

## Enlaces

- [Repositorio](https://github.com/JosueSay/labs-ms/tree/main/Proyectos/p2)
- [Workflow](https://github.com/JosueSay/labs-ms/blob/main/Proyectos/p2/docs/workflow.md)

## Índice

- [Introducción](#introducción)
- [Fundamentos Teóricos](#fundamentos-teóricos)
  - [Proceso de Llegadas y Servicio](#proceso-de-llegadas-y-servicio)
  - [Intensidad y Estabilidad del Modelo](#intensidad-de-tráfico-y-estabilidad)
  - [Distribución Estacionaria por Número de Clientes](#distribución-estacionaria-del-número-de-clientes)
  - [Métricas de Desempeño](#métricas-de-desempeño-en-mm1)
- [Modelo Aplicado a un Restaurante](#modelo-mm1-aplicado-a-un-restaurante)
  - [Gráficas y Métricas](#gráficas-y-métricas)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Configuración de Parámetros del Modelo](#configuración-de-parámetros-del-modelo)
- [Interfaz Dashboard](#interfaz-y-controles)
- [Simulación](#simulación)
  - [Uso de Streamlit y PyGame](#uso-de-streamlit-y-pygame)

## Introducción

## Fundamentos Teóricos

### Proceso de llegadas y servicio

Se supone que las **llegadas** de clientes siguen un **proceso de Poisson** con tasa $\lambda$ clientes por hora. Equivalente a decir que los tiempos entre llegadas sucesivas

$$
T_a \sim \mathrm{Exp}(\lambda)
$$

son independientes entre sí y con media

$$
\mathbb{E}[T_a] = \frac{1}{\lambda}
$$

El **tiempo de servicio** de cada cliente se modela como una variable aleatoria exponencial con tasa $\mu$ servicios por hora

$$
T_s \sim \mathrm{Exp}(\mu)
$$

Cada cliente es atendido por un único servidor. Por ejemplo una caja de cobro o una única persona que toma pedidos y cobra. El tiempo medio de servicio es:

$$
\mathbb{E}[T_s] = \frac{1}{\mu}
$$

Se asume además:

- Un solo servidor activo
- Disciplina de cola **FIFO**
- Capacidad de cola “infinita” a nivel teórico
- No hay abandono ni renegado de clientes
- El proceso se puede estudiar en régimen estacionario cuando es estable.

### Intensidad de tráfico y estabilidad

La razón fundamental del modelo es la **intensidad de tráfico**

$$
\rho = \frac{\lambda}{\mu}
$$

que representa, en promedio, qué fracción del tiempo está ocupado el servidor

- Si $\rho < 1$ el sistema es **estable**

  El número medio de clientes en el sistema se mantiene acotado en el tiempo.

- Si $\rho \ge 1$ la cola crece sin límite en promedio

  El restaurante no tiene capacidad suficiente para atender la demanda

En el contexto de un restaurante $\rho$ indica qué tan “estresado” está el recurso de servicio. Los valores cercanos a uno implican colas largas y tiempos de espera altos y los valores muy bajos implican capacidad ociosa.

### Distribución estacionaria del número de clientes

Bajo las hipótesis M/M/1 y con $\rho < 1$ el proceso admite una **distribución estacionaria** para el número de clientes en el sistema $N$

$$
\mathbb{P}{N = n} = (1 - \rho),\rho^n
\quad,\quad n = 0,1,2,\dots
$$

Esta distribución geométrica permite derivar expresiones cerradas para los indicadores de desempeño

### Métricas de desempeño en M/M/1

A partir de la distribución estacionaria se obtienen las métricas teóricas estándar del modelo M/M/1

Número medio de clientes en el sistema

$$
L = \mathbb{E}[N] = \frac{\rho}{1 - \rho}
$$

Número medio de clientes en cola

$$
L_q = L - \rho = \frac{\rho^2}{1 - \rho}
$$

Tiempo medio que un cliente pasa **en el sistema** $W$ y **en cola** $W_q$ se obtienen usando la **ley de Little**

$$
L = \lambda W
\quad,\quad
L_q = \lambda W_q
$$

por lo que

$$
W = \frac{L}{\lambda} = \frac{1}{\mu - \lambda}
$$

$$
W_q = \frac{L_q}{\lambda} = \frac{\rho}{\mu - \lambda}
$$

En la interpretación de restaurante

- $L$ es el número promedio de clientes que están en el local sumando los que esperan y los que están siendo atendidos
- $L_q$ es el tamaño promedio de la cola
- $W$ es el tiempo total promedio que un cliente pasa en el sistema
- $W_q$ es el tiempo promedio de espera antes de ser atendido
- $\rho$ es la fracción de tiempo que el servidor está trabajando

Estas métricas permiten evaluar si el diseño actual del restaurante es adecuado o si se requieren cambios en $\lambda$ o $\mu$.

> Por ejemplo cambios en la capacidad de servicio o en la organización de la atención.

## Modelo M/M/1 Aplicado a un Restaurante

Se interpreta como la operación de un restaurante con **una sola “línea de atención efectiva”**:

- Llegadas de clientes $\rightarrow$ proceso de Poisson con tasa $\lambda$  (personas por hora).
- Tiempos de servicio $\rightarrow$ distribución exponencial con tasa $\mu$  (clientes atendidos por hora).
- Servidor $\rightarrow$ el conjunto caja + mostrador + personal que atiende pedidos, visto como un único recurso.
- Sistema $\rightarrow$ clientes esperando en fila + cliente en servicio.

A partir de valores de $\lambda$ y $\mu$ se fijan los parámetros del modelo y se simula una jornada del restaurante (por ejemplo, 24 horas). Cada corrida genera eventos de llegada, inicio y fin de servicio, así como tiempos de espera y de permanencia en el sistema.

Con estos datos se estiman las métricas clásicas del modelo:

- Utilización del servidor: $\rho = \dfrac{\lambda}{\mu}$
- Número promedio de clientes en el sistema: $L$
- Número promedio en la cola: $L_q$
- Tiempo promedio en el sistema: $W$
- Tiempo promedio de espera en cola: $W_q$

Teóricamente, estas variables cumplen la **ley de Little**:

- $L = \lambda W$
- $L_q = \lambda W_q$

En la simulación, las mismas cantidades se calculan a partir de los datos observados. La comparación entre fórmulas y resultados simulados permite validar que la implementación del modelo reproduce el comportamiento esperado del restaurante bajo la hipótesis M/M/1.

### Gráficas y Métricas

A partir de los archivos de resultados, el sistema genera nueve gráficas. Cada una responde a una pregunta concreta sobre el funcionamiento del restaurante, independientemente de los valores numéricos puntuales:

1. **Evolución temporal de la cola**
   Muestra $L_q(t)$ a lo largo del día. Permite ver en qué momentos se forma fila, cuándo se vacía el sistema y si existen franjas claramente más críticas (horas pico).

2. **Histograma de $L_q$**
   Resume con qué frecuencia el restaurante tiene 0, 1, 2, … clientes esperando. Es la versión empírica de las probabilidades estacionarias $P{L_q = n}$ y ayuda a cuantificar “qué tan normal” es encontrar fila.

3. **ECDF de tiempos**
   Presenta las funciones de distribución acumulada de `wait_time`, `service_time` y `system_time`. Responde preguntas del tipo:

   - “¿Qué proporción de clientes espera menos de 10 minutos?”
   - “¿En cuánto tiempo se completa el servicio para el 90 % de los clientes?”

4. **Llegada vs tiempo en sistema (hexbin)**
   Relaciona la hora de llegada con el tiempo total en el sistema. Las zonas más densas indican horarios en los que los clientes tienden a permanecer más tiempo, señalando posibles congestiones.

5. **Clientes atendidos (acumulado)**
   Es la curva de throughput: el conteo acumulado de clientes cuyo servicio terminó. La pendiente indica la tasa de salida efectiva y permite visualizar si el ritmo de atención es estable o si se ralentiza en ciertos periodos.

6. **Eventos acumulados**
   Traza, por separado, llegadas, inicios de servicio y finales de servicio. Idealmente, las curvas de inicio y fin de servicio deberían seguir de cerca a las llegadas, lo que indica un sistema “equilibrado” donde la capacidad de atención acompaña la demanda.

7. **Cola con bloques de ocupación**
   Combina $L_q(t)$ con bandas sombreadas correspondientes a periodos de alta utilización del servidor. Esto facilita detectar bloques de tiempo en los que se trabaja casi de forma continua, lo cual se interpreta como presión operativa alta sobre el personal.

8. **Ocupación del servidor**
   Resume la utilización $\rho$ mediante promedios por intervalo de tiempo y una curva de $\rho$ acumulado. Sirve para evaluar si el restaurante opera en rangos recomendables (por ejemplo, $\rho$ menor a 0.8 para evitar esperas excesivas).

9. **Teoría vs simulación**
   Compara barras de $\rho$, $L$, $L_q$, $W$ y $W_q$ teóricos frente a sus estimaciones simuladas. Si las diferencias son pequeñas, se confirma que la implementación es consistente con la teoría y que la ley de Little se cumple aproximadamente en el restaurante modelado.

## Estrategia de Simulación

La simulación modela la atención de clientes en un restaurante como una cola M/M/1 de tiempo continuo. Se usa un esquema de **eventos discretos** donde el reloj de simulación solo salta a tres tipos de sucesos:

- llegada de un cliente
- inicio de servicio
- fin de servicio

Los tiempos entre llegadas se generan con una distribución exponencial de media $1/\lambda$ y los tiempos de servicio con una exponencial de media $1/\mu$. El servidor atiende con disciplina FIFO y capacidad práctica infinita, por lo que ningún cliente es rechazado.

Para cada corrida se define una **duración total en horas** y un posible período de calentamiento. A lo largo de la corrida se registran eventos y series de tiempo para poder estimar métricas como $L$, $L_q$, $W$, $W_q$ y la utilización promedio $\rho$, que luego se comparan con los valores teóricos de M/M/1 mediante la ley de Little y las fórmulas clásicas.

## Arquitectura del Sistema

Los archivos y módulos relevantes son:

- **Configuración**
  Archivos YAML en `configs/` describen parámetros del modelo, de la simulación y del proyecto.

- **Motor de simulación**
  El núcleo matemático está en `MM1Model`, que implementa la dinámica de la cola y genera todas las salidas en memoria.

- **Controlador**
  `SimulationController` envuelve al modelo, gestiona semillas, duración de la corrida, velocidad y estado pausado o terminado.

- **Capa de análisis y escritura**
  `io_mm1.writers` guarda en CSV los eventos, series y métricas, mientras que `sim.plots` usa esos archivos para generar las nueve gráficas de análisis.

- **Interfaces de usuario**
  Streamlit y Pygame se apoyan en el mismo controlador y solo cambian la forma de mostrar el estado de la simulación.

## Configuración de Parámetros del Modelo

Cada simulación del sistema de colas $M/M/1$ se define a través de un archivo de configuración YAML dentro del directorio `configs/`.
Este archivo permite controlar el comportamiento del modelo, los parámetros de simulación, la salida de datos y la visualización en tiempo real **sin modificar el código fuente**.

### Estructura general

```yaml
project:
  seed: 12345
  output_base_data: "data"
  output_base_results: "results"
  make_run_dir: true
  timestamp_fmt: "%Y%m%d_%H%M%S"

model:
  type: "MM1"
  lambda: 10.0
  mu: 12.0
  queue_discipline: "FIFO"
  capacity_infinite: true
  patience_infinite: true

model_params:
  initial_time: 0.0
  initial_queue: 0
  server_initial_state: "idle"
  service_time_if_busy: 0.0

simulation:
  mode: "batch"
  sim_time_hours: 4.0
  warmup_minutes: 0
  record_interval_seconds: 10
  replications: 1

realtime:
  wall_clock_speed: 1.0
  draw_interval_ms: 100
  max_points: 500

outputs: true
```

### **1. Sección `project`**

Define aspectos globales de la ejecución, como rutas de salida, control de aleatoriedad y formato de nombres.

| Parámetro             | Tipo     | Descripción                                                              | Valores posibles / relación                                   |
| --------------------- | -------- | ------------------------------------------------------------------------ | ------------------------------------------------------------- |
| `seed`                | entero   | Semilla aleatoria para garantizar reproducibilidad entre ejecuciones.    | Cualquier número entero.                                      |
| `output_base_data`    | cadena   | Carpeta donde se guardan los datos crudos (`data/`).                     | Ruta relativa. No debe terminar en `/`.                       |
| `output_base_results` | cadena   | Carpeta base para los resultados procesados y figuras (`results/`).      | Ruta relativa.                                                |
| `make_run_dir`        | booleano | Si es `true`, crea una subcarpeta `runs_<timestamp>` por cada ejecución. | `true` / `false`                                              |
| `timestamp_fmt`       | cadena   | Formato del sello temporal para nombres de carpetas.                     | Formato compatible con `strftime` (p. ej. `"%Y%m%d_%H%M%S"`). |

**Relaciones:**

- `make_run_dir: true` crea directorios dentro de `output_base_data` y `output_base_results` usando el formato definido en `timestamp_fmt`.

### **2. Sección `model`**

Define el tipo de modelo de colas y sus parámetros fundamentales.
Esta sección traduce directamente los parámetros teóricos $\lambda$ (tasa de llegada) y $\mu$ (tasa de servicio).

| Parámetro           | Tipo     | Descripción                                                  | Valores posibles / relación                         |
| ------------------- | -------- | ------------------------------------------------------------ | --------------------------------------------------- |
| `type`              | cadena   | Tipo de modelo de colas a simular.                           | `"MM1"` (por ahora fijo).                           |
| `lambda`            | número   | Tasa promedio de llegadas (clientes por hora).               | > 0                                                 |
| `mu`                | número   | Tasa promedio de servicio (clientes atendidos por hora).     | > 0, debe cumplir $\lambda < \mu$ para estabilidad. |
| `queue_discipline`  | cadena   | Regla de atención de clientes.                               | `"FIFO"` (actualmente único modo implementado).     |
| `capacity_infinite` | booleano | Si es `true`, la cola no tiene límite de clientes esperando. | `true` / `false`                                    |
| `patience_infinite` | booleano | Si es `true`, los clientes nunca abandonan la cola.          | `true` / `false`                                    |

**Relaciones:**

- La estabilidad del sistema requiere que $\lambda < \mu$.
- Si `capacity_infinite` o `patience_infinite` se establecen en `false`, deben existir parámetros adicionales en el futuro (no usados aún).

### **3. Sección `model_params`**

Permite definir condiciones iniciales del sistema antes de iniciar la simulación.
Esto facilita controlar el estado del servidor y la cola al comienzo del reloj de simulación.

| Parámetro              | Tipo   | Descripción                                                               | Valores posibles / relación |
| ---------------------- | ------ | ------------------------------------------------------------------------- | --------------------------- |
| `initial_time`         | número | Tiempo inicial del reloj de simulación (en horas).                        | Normalmente `0.0`.          |
| `initial_queue`        | entero | Número de clientes esperando al inicio.                                   | ≥ 0                         |
| `server_initial_state` | cadena | Estado inicial del servidor.                                              | `"idle"` o `"busy"`.        |
| `service_time_if_busy` | número | Si el servidor empieza ocupado, tiempo restante de servicio (en minutos). | ≥ 0                         |

**Relaciones:**

- Si `server_initial_state: "idle"`, el valor de `service_time_if_busy` se ignora.
- Si `server_initial_state: "busy"`, el primer evento de salida ocurre tras `service_time_if_busy`.

### **4. Sección `simulation`**

Controla el comportamiento general de la simulación: duración, modo de ejecución, frecuencia de registro y repeticiones.

| Parámetro                 | Tipo   | Descripción                                                                                   | Valores posibles / relación |
| ------------------------- | ------ | --------------------------------------------------------------------------------------------- | --------------------------- |
| `mode`                    | cadena | Define si la simulación se ejecuta en bloque o en tiempo real.                                | `"batch"` o `"realtime"`.   |
| `sim_time_hours`          | número | Duración total de la simulación (horas simuladas).                                            | > 0                         |
| `warmup_minutes`          | número | Periodo inicial cuyos datos no se usan en métricas agregadas (fase de estabilización).        | ≥ 0                         |
| `record_interval_seconds` | número | Intervalo de registro de métricas instantáneas ($L_q(t)$, $\rho(t)$).                         | > 0                         |
| `replications`            | entero | Número de veces que se repite la simulación con los mismos parámetros para obtener promedios. | ≥ 1                         |

**Relaciones:**

- Si `mode: "realtime"`, los parámetros de `realtime` también deben estar definidos (sección siguiente).
- `record_interval_seconds` determina la resolución temporal de los CSV de series.

### **5. Sección `realtime`**

Configura el comportamiento visual e interactivo de la simulación en tiempo real.

| Parámetro          | Tipo   | Descripción                                                                                   | Valores posibles / relación |
| ------------------ | ------ | --------------------------------------------------------------------------------------------- | --------------------------- |
| `wall_clock_speed` | número | Factor de velocidad respecto al tiempo real. `1.0` = tiempo real, `>1` acelera la simulación. | ≥ 0                         |
| `draw_interval_ms` | entero | Tiempo (en milisegundos) entre actualizaciones gráficas de la vista.                          | > 0                         |
| `max_points`       | entero | Número máximo de puntos o entidades a mostrar en la animación (limita memoria).               | > 0                         |

**Relaciones:**

- Solo aplican cuando `simulation.mode = "realtime"`.
- No afectan los resultados numéricos, solo la representación visual.

### **6. Parámetro `outputs`**

Controla si la simulación genera archivos de salida.
Cuando está activado, el programa produce:

- CSV con datos crudos y métricas.
- Figuras (PNG).
- Reporte resumido (Markdown).
- Configuración efectiva (`config_effective.yaml`).

| Parámetro | Tipo     | Descripción                                                  | Valores posibles                                 |
| --------- | -------- | ------------------------------------------------------------ | ------------------------------------------------ |
| `outputs` | booleano | Habilita o desactiva la exportación de todos los resultados. | `true` (exporta todo) / `false` (no guarda nada) |

## Interfaz y Controles

La interfaz principal en Streamlit expone el modelo M/M/1:

- **Sliders para parámetros**

  El usuario ajusta $\lambda$ y $\mu$ en el panel lateral. El sistema muestra una advertencia cuando $\mu \le \lambda$ para recordar la condición de estabilidad.

- **Control de duración y velocidad**

  Otro control define las horas a simular y un factor de velocidad que convierte segundos reales en horas simuladas. Con velocidad cero la corrida queda pausada.

- **Botones de ejecución**

  Los botones Iniciar, Pausa Reanudar y Reiniciar controlan el ciclo de vida de la corrida y actualizan una bandera interna que indica si hay una simulación en curso.

- **Acciones adicionales**

  Un botón dispara la generación de archivos y gráficas para el informe y otro abre la vista animada en Pygame.

- **Panel de indicadores**

  En la parte central se muestran métricas en vivo tiempo simulado, longitud de cola, clientes creados y atendidos y utilización promedio estimada.

## Simulación

- El modelo guarda el reloj de simulación, la cola FIFO de identificadores de cliente, el estado del servidor y los tiempos programados del próximo arribo y de la próxima salida.
- Las funciones `sampleInterarrival` y `sampleService` generan tiempos exponenciales para arribo y servicio.
- En cada evento se actualiza el acumulador de tiempo ocupado, lo que permite calcular la utilización $\rho$ como proporción de tiempo con servidor ocupado sobre el horizonte simulado.
- Cada cliente se registra en `queue_times` con sus tiempos de llegada, inicio de servicio y salida, lo que permite derivar tiempos en cola, tiempos de servicio y tiempos totales en sistema.

La simulación utiliza la clase `SimulationController`.

- Traduce tiempo de reloj real a tiempo simulado usando el factor de velocidad.
- Controla el avance hasta un tiempo objetivo mediante la función `simulateUntil` del modelo.
- Permite avanzar con pasos fijos de tiempo simulado para integrarse con Pygame.
- Devuelve *snapshots* ligeros con el estado y con series recortadas, que la interfaz usa para refrescar métricas y gráficas sin copiar estructuras completas.

### Uso de Streamlit y Pygame

Ambas vistas comparten el mismo controlador, por lo que observan exactamente la misma dinámica M/M/1.

**Streamlit** se centra en el análisis:

- Organiza las nueve gráficas en bloques que permiten leer la simulación desde varias perspectivas, por ejemplo evolución temporal de $L_q$, distribución de longitudes de cola, curvas ECDF de tiempos, densidad llegada versus tiempo en sistema, clientes atendidos, eventos acumulados, bloques de alta ocupación, utilización del servidor y barras de Teoría versus Simulación.
- Cada ejecución puede guardarse en disco para ser incluida en el informe y comparada con otras corridas.

**Pygame** aporta una vista más operacional:

- Usa `tickWithDelta` para avanzar el modelo con pasos pequeños de tiempo simulado y dibuja en pantalla la cola, el servidor y el flujo de clientes.
- Es ideal para explicar de manera intuitiva fenómenos como picos de cola, periodos de saturación o el impacto de cambiar $\lambda$ y $\mu$ en tiempo real.

## Módulo de análisis y generación de reportes

## Gráficas y métricas obtenidas

## Discusión de resultados

## Conclusiones

## Referencias

1. [Modelling and Simulation of a State University Cafeteria: A Case Study – Academia.edu](https://www.academia.edu/41926141/Modelling_and_Simulation_of_a_State_University_Cafeteria_A_Case_Study)
2. [Sustainability Journal – Small Queuing Restaurant Sustainable Revenue Management (MDPI)](https://www.mdpi.com/2071-1050/12/8/3477)
3. [Application of Queuing Theory on a Food Chain – IJSTR](https://www.ijstr.org/final-print/aug2019/Application-Of-Queuing-Theory-On-A-Food-Chain.pdf)
