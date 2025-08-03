# Problema 2

Resuelva el siguiente problema de asignación.

|      |     |     |      |     |     |     |
| ---- | --- | --- | ---- | --- | --- | --- |
| \$3  | \$8 | \$2 | \$10 | \$3 | \$3 | \$9 |
| \$2  | \$2 | \$7 | \$6  | \$5 | \$2 | \$7 |
| \$5  | \$6 | \$4 | \$5  | \$6 | \$6 | \$6 |
| \$4  | \$2 | \$7 | \$5  | \$9 | \$4 | \$7 |
| \$10 | \$3 | \$8 | \$4  | \$2 | \$3 | \$5 |
| \$3  | \$5 | \$4 | \$2  | \$3 | \$7 | \$8 |

## Descripción del Problema

Se tienen:

- 6 agentes
- 7 tareas

El objetivo es asignar **una tarea a cada agente** tal que el **costo total de asignación sea mínimo**, con las siguientes restricciones:

- Cada agente realiza **exactamente una tarea**.
- Cada tarea puede ser asignada a **lo sumo una vez**.

## Matriz de Costos

La matriz representa el costo de asignar al agente `i` la tarea `j`:

```bash
[ 3 8 2 10 3 3 9;
  2 2 7 6 5 2 7;
  5 6 4 5 6 6 6;
  4 2 7 5 9 4 7;
 10 3 8 4 2 3 5;
  3 5 4 2 3 7 8 ]
```

## Modelado con JuMP

- Variables binarias `x[i,j]`:
  - `1` si el agente `i` realiza la tarea `j`
  - `0` si no
- Restricciones:
  - Cada agente: `sum(x[i, j]) == 1`
  - Cada tarea: `sum(x[i, j]) <= 1`
- Función objetivo: minimizar `sum(costos[i,j] * x[i,j])`

## Resultado del Modelo

El solver HiGHS encontró la asignación óptima con un **costo mínimo total de \$15.00**.

### Asignaciones Óptimas

| Agente | Tarea Asignada | Costo |
|--------|----------------|-------|
| 1      | 6              | \$3   |
| 2      | 1              | \$2   |
| 3      | 3              | \$4   |
| 4      | 2              | \$2   |
| 5      | 5              | \$2   |
| 6      | 4              | \$2   |

> Nota: la **tarea 7 no fue asignada**, ya que hay más tareas que agentes.
