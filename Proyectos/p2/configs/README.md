# Configuración del proyecto — Plantilla YAML

Cada simulación del sistema de colas $M/M/1$ se define a través de un archivo de configuración YAML dentro del directorio `configs/`.
Este archivo permite controlar el comportamiento del modelo, los parámetros de simulación, la salida de datos y la visualización en tiempo real **sin modificar el código fuente**.

## Estructura general

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

## **1. Sección `project`**

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

## **2. Sección `model`**

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

## **3. Sección `model_params`**

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

## **4. Sección `simulation`**

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

## **5. Sección `realtime`**

Configura el comportamiento visual e interactivo de la simulación en tiempo real.

| Parámetro          | Tipo   | Descripción                                                                                   | Valores posibles / relación |
| ------------------ | ------ | --------------------------------------------------------------------------------------------- | --------------------------- |
| `wall_clock_speed` | número | Factor de velocidad respecto al tiempo real. `1.0` = tiempo real, `>1` acelera la simulación. | ≥ 0                         |
| `draw_interval_ms` | entero | Tiempo (en milisegundos) entre actualizaciones gráficas de la vista.                          | > 0                         |
| `max_points`       | entero | Número máximo de puntos o entidades a mostrar en la animación (limita memoria).               | > 0                         |

**Relaciones:**

- Solo aplican cuando `simulation.mode = "realtime"`.
- No afectan los resultados numéricos, solo la representación visual.

## **6. Parámetro `outputs`**

Controla si la simulación genera archivos de salida.
Cuando está activado, el programa produce:

- CSV con datos crudos y métricas.
- Figuras (PNG).
- Reporte resumido (Markdown).
- Configuración efectiva (`config_effective.yaml`).

| Parámetro | Tipo     | Descripción                                                  | Valores posibles                                 |
| --------- | -------- | ------------------------------------------------------------ | ------------------------------------------------ |
| `outputs` | booleano | Habilita o desactiva la exportación de todos los resultados. | `true` (exporta todo) / `false` (no guarda nada) |
