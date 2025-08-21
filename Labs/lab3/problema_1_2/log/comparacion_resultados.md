### Caso A ($f_a$)

|     Algoritmo de optimización     |  Convergencia  |   No. Iter. |   $\alpha$ |            Técnica / Notas             |  Solución (best)  |   Error ($\|\|\nabla f\|\|$) |   $\|\|\nabla f\|\|$ final |   f(best) |   Tiempo (s) |
|-----------------------------------|----------------|-------------|------------|----------------------------------------|-------------------|------------------------------|----------------------------|-----------|--------------|
| Descenso de Newton ($\alpha=1.0$) |       Sí       |          16 |       1    |              solve=solve               |  [0.983, 0.950]   |                    9.548e-13 |                  9.548e-13 |  -0.51218 |        0     |
|       Fletcher-Reeves (NCG)       |       Sí       |          48 |       0.02 | β=FR, restartEvery=50, ensureDescent=✓ | [-1.015, -1.045]  |                    7.263e-07 |                  7.263e-07 |  -1.51132 |        0.001 |
| Descenso de Newton ($\alpha=0.1$) |       Sí       |         306 |       0.1  |              solve=solve               | [-1.015, -1.045]  |                    9.89e-07  |                  9.89e-07  |  -1.51132 |        0.007 |
|               BFGS                |       Sí       |         770 |       0.02 |  skipUpdateIf=1e-12, ensureDescent=✓   | [-1.015, -1.045]  |                    9.897e-07 |                  9.897e-07 |  -1.51132 |        0.015 |
|   Descenso gradiente aleatorio    |       No       |        2000 |       0.01 |   dirección ∠ aleatorio; seed=22801    | [-1.014, -1.053]  |                    0.1291    |                  0.1291    |  -1.51076 |        0.049 |
|    Descenso máximo (steepest)     |       No       |        5000 |       0.01 |              $\varphi$=0               | [-1.018, -1.041]  |                    0.07536   |                  0.07536   |  -1.51115 |        0.112 |

### Caso B (Rosenbrock 2D)

|     Algoritmo de optimización     |  Convergencia  |   No. Iter. |   $\alpha$ |            Técnica / Notas             |  Solución (best)  |   Error ($\|\|\nabla f\|\|$) |   $\|\|\nabla f\|\|$ final |     f(best) |   Tiempo (s) |
|-----------------------------------|----------------|-------------|------------|----------------------------------------|-------------------|------------------------------|----------------------------|-------------|--------------|
| Descenso de Newton ($\alpha=1.0$) |       Sí       |           6 |      1     |              solve=solve               |  [1.000, 1.000]   |                    8.286e-09 |                  8.286e-09 | 3.43265e-20 |        0     |
| Descenso de Newton ($\alpha=0.1$) |       Sí       |           6 |      1     |              solve=solve               |  [1.000, 1.000]   |                    8.286e-09 |                  8.286e-09 | 3.43265e-20 |        0     |
|       Fletcher-Reeves (NCG)       |       Sí       |        1483 |      0.001 | β=FR, restartEvery=50, ensureDescent=✓ |  [1.000, 1.000]   |                    9.993e-07 |                  9.993e-07 | 1.24997e-12 |        0.021 |
|               BFGS                |       Sí       |       27602 |      0.001 |  skipUpdateIf=1e-12, ensureDescent=✓   |  [1.000, 1.000]   |                    9.978e-07 |                  9.978e-07 | 2.24542e-13 |        0.547 |
|   Descenso gradiente aleatorio    |       No       |        2500 |      0.01  |   dirección ∠ aleatorio; seed=22801    |  [0.982, 0.950]   |                    6.696     |                  6.696     | 0.0235923   |        0.059 |
|    Descenso máximo (steepest)     |       No       |        8000 |      0.01  |              $\varphi$=0               |  [0.994, 0.978]   |                    4.93      |                  4.93      | 0.0123464   |        0.187 |

### Caso C (Rosenbrock 7D)

|     Algoritmo de optimización     |  Convergencia  |   No. Iter. |   $\alpha$ |            Técnica / Notas             |             Solución (best)             |   Error ($\|\|\nabla f\|\|$) |   $\|\|\nabla f\|\|$ final |   f(best) |   Tiempo (s) |
|-----------------------------------|----------------|-------------|------------|----------------------------------------|-----------------------------------------|------------------------------|----------------------------|-----------|--------------|
| Descenso de Newton ($\alpha=1.0$) |       Sí       |          12 |     1      |              solve=solve               | [-0.992, 0.994, 0.992, 0.987, …, 0.905] |                    9.498e-07 |                  9.498e-07 |   3.9836  |        0.001 |
| Descenso de Newton ($\alpha=0.1$) |       Sí       |          12 |     1      |              solve=solve               | [-0.992, 0.994, 0.992, 0.987, …, 0.905] |                    9.498e-07 |                  9.498e-07 |   3.9836  |        0     |
|       Fletcher-Reeves (NCG)       |       Sí       |        2190 |     0.0005 | β=FR, restartEvery=50, ensureDescent=✓ | [-0.992, 0.994, 0.992, 0.987, …, 0.905] |                    9.908e-07 |                  9.908e-07 |   3.9836  |        0.059 |
|   Descenso gradiente aleatorio    |       No       |        3000 |     0.01   |   dirección ∠ aleatorio; seed=22801    | [-0.994, 0.989, 0.982, 0.957, …, 0.709] |                    7.291     |                  7.291     |   4.02347 |        0.117 |
|    Descenso máximo (steepest)     |       No       |        6000 |     0.01   |              $\varphi$=0               | [-0.992, 0.991, 0.993, 0.981, …, 0.886] |                    8.413     |                  8.413     |   4.00478 |        0.22  |
|               BFGS                |       No       |       30000 |     0.0005 |  skipUpdateIf=1e-12, ensureDescent=✓   | [-0.992, 0.994, 0.992, 0.987, …, 0.905] |                    9.255e-05 |                  9.255e-05 |   3.9836  |        1.018 |
