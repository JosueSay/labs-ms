# Problema 3

Una empresa necesita asignar cuatro puestos de trabajo a cuatro trabajadores. El costo de desempeñar un puesto es una función de las habilidades de los trabajadores. En la tabla siguiente se resume el costo de las asignaciones. El trabajador 1 no puede tener el puesto 3, y el trabajador 3 no puede desempeñar el puesto 4. Determine la asignación óptima mediante programación lineal.

|              | Puesto 1 | Puesto 2 | Puesto 3 | Puesto 4 |
| ------------ | -------- | -------- | -------- | -------- |
| Trabajador 1 | \$50     | \$50     | –        | \$20     |
| Trabajador 2 | \$70     | \$40     | \$20     | \$30     |
| Trabajador 3 | \$90     | \$30     | \$50     | –        |
| Trabajador 4 | \$70     | \$20     | \$60     | \$70     |

## Matriz de Costos

costos = [
    50   50   Inf   20;
    70   40    20   30;
    90   30    50  Inf;
    70   20    60   70
]

## Modelado con JuMP

- Variables binarias `x[i,j]`:
  - `1` si el trabajador `i` ocupa el puesto `j`
  - `0` si no
- Restricciones:
  - Cada trabajador debe tener **exactamente un puesto**.
  - Cada puesto debe ser asignado a **exactamente un trabajador**.
- Los valores `Inf` son ignorados en la función objetivo.

## Resultado del Modelo

El solver HiGHS encontró la solución óptima con un **costo total de \$90.00**.

### Asignaciones Óptimas

| Trabajador | Puesto Asignado | Costo |
|------------|------------------|-------|
| 1          | 1                | \$50  |
| 2          | 3                | \$20  |
| 4          | 2                | \$20  |

> Nota: El **trabajador 3** y el **puesto 4** no fueron asignados debido a las restricciones prohibidas, lo cual es válido en este contexto.
