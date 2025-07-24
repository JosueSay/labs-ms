---
header-includes:
  - \usepackage{amsmath}
  - \usepackage{amssymb}
  - \usepackage{fontspec}
  - \setmainfont{FiraCode Nerd Font}
  - \setmonofont{FiraCode Nerd Font Mono}
  - \usepackage{setspace}
  - \setstretch{1.5}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  - \hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}
geometry: top=0.67in, bottom=0.67in, left=0.85in, right=0.85in
---

# Laboratorio 1 - Programación Lineal

Se abordaron cuatro problemas de programación lineal utilizando Julia y Excel donde requería.

## Integrantes

- Abby Donis
- Cindy Gualim
- Josué Say

## Enlaces

- [Repositorio](https://github.com/JosueSay/labs-ms/tree/main/Labs/lab1)

## Entorno

- Julia 1.11.6
- Jupyter Notebook

# 1. Problema de programación lineal (Simplex)

# 2. Modelo de Producción (Períodos múltiples)

## Problema de Planeación de Producción Mensual

Este ejercicio busca determinar un plan de producción para 6 meses que minimice los costos totales, tomando en cuenta:

- Demanda mensual conocida.
- Costo de producción variable por mes.
- Costo de mantener inventario de un mes a otro.
- Inventario inicial igual a cero.

## Inciso A: Construcción de la Función Objetivo

Se construyó la función objetivo sumando los costos de producción y los costos de inventario para cada mes:

**Función objetivo:**  
$50x_1 + 8I_1 + 45x_2 + 10I_2 + 55x_3 + 10I_3 + 52x_4 + 10I_4 + 48x_5 + 8I_5 + 50x_6 + 8I_6$

## Inciso B: Optimización con variables continuas

Se resolvió un modelo de programación lineal donde la producción y el inventario pueden ser números fraccionarios.  
El modelo resultó óptimo con los siguientes valores:

**Tabla de resultados:**

| Mes | Producción | Inventario | Costo producción | Costo inventario |
|-----|------------|------------|------------------|------------------|
| 1   | 205.0      | 25.0       | \$10,250.0       | \$200.0          |
| 2   | 225.0      | 0.0        | \$10,125.0       | \$0.0            |
| 3   | 190.0      | 0.0        | \$10,450.0       | \$0.0            |
| 4   | 160.0      | 20.0       | \$8,320.0        | \$200.0          |
| 5   | 225.0      | 25.0       | \$10,800.0       | \$200.0          |
| 6   | 225.0      | 0.0        | \$11,250.0       | \$0.0            |

**Costo total óptimo con producción continua:** **\$61,795.0**

## Inciso C: Optimización con variables enteras

Se reformuló el modelo para que las variables de producción fueran enteras (números completos).  
El resultado fue exactamente el mismo:

- **Costo total óptimo con producción entera:** \$61,795.0  
- **Diferencia con modelo continuo:** \$0.0

Esto indica que la solución fraccionaria ya arrojaba valores enteros o muy cercanos.

## Conclusiones

- El modelo de producción minimiza exitosamente los costos totales.
- No hubo diferencia entre los resultados enteros y continuos, lo cual sugiere que el problema no requiere forzar enteros.
- Julia con JuMP y HiGHS permite resolver problemas reales de optimización de forma eficiente.

# 3. Modelo de asignación de horarios

## Inciso a

Formular el problema de programación lineal

### Contexto

Se quiere minimizar el número total de autobuses necesarios para satisfacer la demanda durante el día, dividiendo el día en seis turnos de 8 horas. Cada autobús trabaja una jornada continua de 8 horas (por mantenimiento), iniciando en uno de los seis turnos definidos.

La demanda de autobuses varía por tramos de 4 horas a lo largo del día (como se ve en la parte superior del gráfico). Para cada tramo de 4 horas se requiere una cierta cantidad mínima de autobuses circulando.

Lo que se debe hacer es poder asignar la cantidad adecuada de buses a cada turno para cubrir todos los horarios sin poner buses de más.

#### Turnos y Horarios

| Turno | Horario       |
| ----- | ------------- |
| 1     | 00:00 – 07:59 |
| 2     | 04:00 – 11:59 |
| 3     | 08:00 – 15:59 |
| 4     | 12:00 – 19:59 |
| 5     | 16:00 – 23:59 |
| 6     | 20:00 – 03:59 |

Cada turno dura **8 horas** y se **traslapan** con otros turnos. Esto significa que **un mismo autobús puede cubrir varios bloques horarios** (como 04:00–07:59 + 08:00–11:59), dependiendo del turno en que inicia.

#### Imágen

| Bloque horario (4h) | Intervalo     | Demanda mínima |
| ------------------- | ------------- | -------------- |
| B1                  | 00:00 – 03:59 | 4              |
| B2                  | 04:00 – 07:59 | 8              |
| B3                  | 08:00 – 11:59 | 10             |
| B4                  | 12:00 – 15:59 | 7              |
| B5                  | 16:00 – 19:59 | 12             |
| B6                  | 20:00 – 23:59 | 4              |

**Cada bloque horario debe tener al menos esa cantidad de autobuses operando, sin importar en qué turno empezaron.**

Cada turno cubre 8h continuas:

- **B1** (00:00–03:59): lo cubren $x_1$ y $x_6$
- **B2** (04:00–07:59): lo cubren $x_1$ y $x_2$
- **B3** (08:00–11:59): lo cubren $x_2$ y $x_3$
- **B4** (12:00–15:59): lo cubren $x_3$ y $x_4$
- **B5** (16:00–19:59): lo cubren $x_4$ y $x_5$
- **B6** (20:00–23:59): lo cubren $x_5$ y $x_6$

### Formulación del problema

#### Variable

$x_i$ = cantidad de autobuses que inician turno $i$, con $i = 1,\dots,6$

*Esto lo sabemos dado que cada bus solo opera 8 horas (un turno). Si sabemos cuántos inician en cada turno, podemos calcular cuántos hay operando en cada bloque de 4 horas.*

#### Función objetivo

Minimizar la cantidad total de autobuses operando:

$$
\min z = x_1 + x_2 + x_3 + x_4 + x_5 + x_6
$$

*Esto directamente nos lo piden ya que menos autobuses significa menos costos de operación, mantenimiento y personal, siempre que se cumpla con la demanda de transporte en cada bloque.*

### Restricciones por bloque de horario

$$
\begin{aligned}
x_1 + x_6 &\geq 4 \quad \text{(Bloque 1: 12:00am – 4:00am)} \\
x_1 + x_2 &\geq 8 \quad \text{(Bloque 2: 4:00am – 8:00am)} \\
x_2 + x_3 &\geq 10 \quad \text{(Bloque 3: 8:00am – 12:00pm)} \\
x_3 + x_4 &\geq 7 \quad \text{(Bloque 4: 12:00pm – 4:00pm)} \\
x_4 + x_5 &\geq 12 \quad \text{(Bloque 5: 4:00pm – 8:00pm)} \\
x_5 + x_6 &\geq 4 \quad \text{(Bloque 6: 8:00pm – 12:00am)}
\end{aligned}
$$

*Esto refleja que los turnos que estan operando durante su bloque de 4 horas.*

### Restricción de no negatividad

$$
x_1, x_2, x_3, x_4, x_5, x_6 \in \mathbb{Z}_{\geq 0}
$$

*No se puede tener fracción de buses ni cantidades negativas*

## Inciso b

Resolver el problema usando la librería JuMP o Pulp, en variables continuas, y determinar la distribución óptima.

### Respuesta

| Turno    | Horario       | $x_i$    | Resultado                                       |
| -------- | ------------- | -------- | ----------------------------------------------- |
| $x_1$    | 00:00 – 08:00 | 4        | Inician 4 buses a medianoche                    |
| $x_2$    | 04:00 – 12:00 | 8        | Inician 8 buses a las 4 am                      |
| $x_3$    | 08:00 – 16:00 | 2        | Inician 2 buses a las 8 am                      |
| $x_4$    | 12:00 – 20:00 | 7        | Inician 7 buses a mediodía                      |
| $x_5$    | 16:00 – 24:00 | 5        | Inician 5 buses a las 4 pm                      |
| $x_6$    | 20:00 – 04:00 | 0        | No se necesita ningún bus comenzando a las 8 pm |

En los resultados podemos ver cuántos buses deben iniciar su turno en dicha hora para los $x_i$, dando una suma total de 26 buses al día para cubrir la demanda.

# 4. Modelo de renovación urbana

## Inciso a

Formular el problema de programación lineal.

### Contexto

Se quiere maximizar la recaudación de impuestos a futuro sujeto a la nueva construcción de casas considerando las condiciones de espacio, presupuesto y porcentaje de tipo de unidad de casas.

#### Datos

##### Demoliciones

- Se pueden demoler máximo 300 casas.
- Cada una ocupa 0.25 acres
  - Por lo tanto el total máximo del terreno disponible es de $300 \times 0.25 = 75$ acres
- Costo por demolición por casa: \$2,000
  - Por lo tanto el total es de $300\times\text{\$}2000=\text{\$}600,000$

##### Tipos de viviendas nuevas

| Tipo      | Acre por unidad | Impuesto (\$) | Costo de construcción (\$) |
| --------- | --------------- | ------------- | -------------------------- |
| Sencilla  | 0.18            | 1000          | 50,000                     |
| Doble     | 0.28            | 1900          | 70,000                     |
| Triple    | 0.40            | 2700          | 130,000                    |
| Cuádruple | 0.50            | 3400          | 160,000                    |

El **15%** del área disponible se usará para otro motivo que no son las casas, por lo tanto tenemos un **85%** del aréa que puede usarse por lo tanto realmente se tiene un área disponible de:

$$0.85 \times 75 = 63.75\text{ acres}$$

##### Otras restricciones

- Financiamiento máximo: \$15,000,000
- Porcentaje mínimo por tipo de unidad:

  | Tipo de unidad                  | Porcentaje mínimo requerido |
  | ------------------------------- | --------------------------- |
  | Sencilla                        | 20% del total de unidades   |
  | Doble                           | 10% del total de unidades   |
  | Triple + Cuádruple (combinadas) | 25% del total de unidades   |

### Formulación del problema

#### Variable

Definimos las variables de acuerdo al tipo de unidad de casa:

- $x_1$ = número de **unidades sencillas**
- $x_2$ = número de **unidades dobles**
- $x_3$ = número de **unidades triples**
- $x_4$ = número de **unidades cuádruples**

*Esto es porque debemos determinar cuantas unidades construir de cada tipo.*

#### Función objetivo

Maximizar la recaudación de impuestos:

$$
\max z = 1000x_1 + 1900x_2 + 2700x_3 + 3400x_4
$$

*Esto debido a que cada tipo de unidad de casa genera impuesto y queremos maximizar esa suma total.*

### Restricciones de espacio

Ya que tenemos de área disponible $63.75$ acres y tenemos definido que cada espacio consume un porcentaje:

$$
0.18x_1 + 0.28x_2 + 0.4x_3 + 0.5x_4 \leq 63.75
$$

*Esto quiere decir que el área ocupada por todas las viviendas no debe exceder el área disponible*

### Restricciones de presupuesto

$$
50000x_1 + 70000x_2 + 130000x_3 + 160000x_4 \leq 15,000,000
$$

*Esto quiere decir que no debemos pasarnos del presupuesto dado.*

### Restricciones por tipo de unidad de casa

1. **Al menos el 25% de las casas deben ser triples o cuadrúples:**

  $$
  x_3 + x_4 \geq 0.25(x_1 + x_2 + x_3 + x_4)
  $$

  $$
  4(x_3 + x_4) \geq x_1 + x_2 + x_3 + x_4
  $$

2. **Al menos el 20% de las casas deben ser sencillas:**

  $$
  x_1 \geq 0.2(x_1 + x_2 + x_3 + x_4)
  $$

  $$
  5x_1 \geq x_1 + x_2 + x_3 + x_4
  $$

3. **Al menos el 10% de las casas deben ser dobles:**

  $$
  x_2 \geq 0.1(x_1 + x_2 + x_3 + x_4)
  $$

  $$
  10x_2 \geq x_1 + x_2 + x_3 + x_4
  $$

### Restricción de no negatividad

$$
x_1, x_2, x_3, x_4 \in \mathbb{Z}_{\geq 0}
$$

*No se puede tener fracción de buses ni cantidades negativas*

## Inciso b

Resolver el problema usando la librería JuMP o Pulp, en variables continuas, y determinar la distribución óptima.  

**Función objetivo:**

$$
\max z = 1000x_1 + 1900x_2 + 2700x_3 + 3400x_4
$$

**Sujeto a:**

\small
$$
\begin{aligned}
0.18x_1 + 0.28x_2 + 0.4x_3 + 0.5x_4 &\leq 63.75 \quad \text{(terreno)} \\
50000x_1 + 70000x_2 + 130000x_3 + 160000x_4 &\leq 15{,}000{,}000 \quad \text{(presupuesto)} \\
4(x_3 + x_4) &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 25\% triples/cuádruples)} \\
5x_1 &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 20\% sencillas)} \\
10x_2 &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 10\% dobles)} \\
x_1, x_2, x_3, x_4 &\geq 0
\end{aligned}
$$

## Inciso c

Resolver el problema en variables enteras, y comparar la solución con la de (b). Discuta sus resultados.

**Función objetivo:**

$$
\max z = 1000x_1 + 1900x_2 + 2700x_3 + 3400x_4
$$

**Sujeto a:**

\small
$$
\begin{aligned}
0.18x_1 + 0.28x_2 + 0.4x_3 + 0.5x_4 &\leq 63.75 \quad \text{(terreno)} \\
50000x_1 + 70000x_2 + 130000x_3 + 160000x_4 &\leq 15,000,000 \quad \text{(presupuesto)} \\
4(x_3 + x_4) &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 25\% triples/cuádruples)} \\
5x_1 &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 20\% sencillas)} \\
10x_2 &\geq x_1 + x_2 + x_3 + x_4 \quad \text{(mínimo 10\% dobles)} \\
x_1, x_2, x_3, x_4 &\in \mathbb{Z}_{\geq 0}
\end{aligned}
$$

### Discusión de resultados

| Tipo de unidad        | Variables continuas | Variables enteras |
| --------------------- | ------------------- | ----------------- |
| Sencillas ($x_1$)     | 37.04               | 36                |
| Dobles ($x_2$)        | 101.85              | 99                |
| Triples ($x_3$)       | 46.30               | 31                |
| Cuádruples ($x_4$)    | 0                   | 14                |
| **Impuesto total**    | **355,556**         | **355,400**       |

Sabemos que idealmente las restricciones para el inciso c son mejores por el hecho que la construcción de casas deben ser enteras porque las fracciones no pueden ser vendidas pero ademas tomemos algo adicional en cuenta, si tomamos los resultados continuos como solución teórica y los resultados enteros como solución verdadera podemos estimar incluso una pérdida asociada a construir hacer ese sacrificio de construir casas enteras a comparación de continuas:

$$\text{perdida}= \frac{355556 - 355400}{355556} ≈ 0.044\%$$

Si bien se tiene una menor ganancia no es tanta y se puede asumir el "riesgo" de idealmente construir casas completas en lugar de fracciones.
