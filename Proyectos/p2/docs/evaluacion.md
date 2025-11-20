# Analisis de eficiencia de modelos

Se compararon ambos modelos por medio la evaluación eficiencia operativa, precisión teórica, congestión y experiencia del cliente.

![Tablas de metricas de modelos](../images/modelos.png)

## Metricas clave

**Simulación vs. Teoría**

| Metrica | Clasico (Teoría / Simulación) | Grupos (Teoría / Simulación) |
| ----------- | ----------- | ----------- |
| $\rho$  | 0.833 / 0.758 | 0.833 / 0.893 |
| L | 5.00 / 2.13 | 5.00 / 2.92 |
| Lq | 4.17 / 1.38| 4.17 / 2.02 |
| W | 0.50 / 0.223 | 0.50 / 0.289 |
| Wq | 5.00 / 2.13 | 0.417 / 0.202 |

**% de Error**

| Metrica | Clasico| Grupos|
| ----------- | ----------- | ----------- |
| $\rho$  | -9.07% | +7.22% |
| L | -57.33% | -41.70% |
| Lq | -66.97% | -51.50% |
| W | -55.41% | -42.15% |
| Wq | -65.25% | -65.25% |

El modelo clasico tiene un uso moderado y el de grupos es de uso alto con riesgo a congestión sin embargo podemos ver un aumento en el modelo de grupos de un 7.22%, indicando que este modelo está operando más cerca del máximo de su capacidad esto reflejado en el aumento de congestión pero a cambio aumenta la productividad.
Al haber una menor carga en el modelo clásico se obtiene una atención mas fluída pero en el modelo de grupos hay más clientes simultáneos con su aumento respectivo en la carga, ambos modelos tienen una cantidad menor de clientes que la teoría el modelo de grupos mantiene más clientes en cola esto reflejando la atención a varios clientes a la vez (grupos).

El modelo clásico tiene una baja congestión, reflejado en su espera reducida mientras que el de grupos tiene una acumulación mayor en la cola por lo que hay más clientes esperando sin embargo, de nuevo, esto se compensa al atender varios clientes a la vez por medio de grupos.
El tiempo promedio en el sistema es más corto en el modelo clásico indicando una atención máxima y con eso una permanencia menor, por otro lado tenemos el modelo de grupos que tiene una mayr permanencia indicando un agrupamiento, esto indica que el modelo clásico es más agil por cliente. El tiempo promedio de espera en cola indica una mejor experiencia individual para cada cliente al tener una espera mínima, mientras que el modelo de grupos tiene un tiempo de espera mayor por cada cliente (compensado al atender a los clientes en bloques).

## Metricas de operacion

**Indice de ajuste promedio**

| Metrica | Clasico| Grupos|
| ----------- | ----------- | ----------- |
| ρ | 0.91 | 0.93 |
| L | 0.43 | 0.6 |
| Lq | 0.33 | 0.5 |
| W | 0.45 | 0.6 |
| Wq | 0.35 | 0.5 |
| ----------- | ----------- | ----------- |
| Promedio | 0.5 | 0.63 |

Podemos ver que el modelo de grupos es más preciso que el modelo clásico, haciendo que este modelo sea más confiable como simulación que el modelo clásico.

**Otras metricas**

| Metrica | Clasico| Grupos|
| ----------- | ----------- | ----------- |
| Eficiencia (clientes/hr)  | 9.67 | 9.88 |
| Tiempo de servicio (total) | 0.078 hr | 0.088 hr |
| Congestion relativa (L/Lq) | 0.645 | 1.429 |

La eficicencia de ambos modelos es bastante cercana con el modelo de grupos tomando el primer lugar, este modelo a pesar de tener una mayor congestión atiene más clientes por hora al hacer uso de la atención grupal de clientes.
El promedio de tiempo de servicio indica que el modelo de grupos dedica más tiempo al servicio por cliente, reflejando un proceso de atención más lento, pero compensado al atender en grupos.
La congestión relativa indica que en el modelo clásico tiene una atención más fluida, reflejado en que hay una menor cantidad de clientes esperando en cola. El modelo de grupos tiene más clientes en espera, mientras esperan a ser atentidos en grupo.
