# Laboratorio de Investigación de Operaciones  
## Problema de Planeación de Producción Mensual

Este inciso tiene como objetivo encontrar la solución óptima para un problema de planeación de producción a lo largo de 6 meses, considerando los costos de producción e inventario.

---

###  Descripción del Problema

Se debe decidir cuántas unidades producir en cada mes para satisfacer la demanda mensual, minimizando el costo total. Se consideran dos tipos de costos:
- **Costo de producción por unidad** (varía cada mes).
- **Costo de inventario por unidad almacenada**.

Además, se conoce la demanda mensual y se parte de un inventario inicial de 0 unidades.

---

##  Incisos Resueltos

### Inciso A: Función Objetivo

Se construyó la función objetivo que representa el costo total, sumando los costos de producción y de inventario para cada mes:

**Función objetivo**:  
```math
50x₁ + 8I₁ + 45x₂ + 10I₂ + 55x₃ + 10I₃ + 52x₄ + 10I₄ + 48x₅ + 8I₅ + 50x₆ + 8I₆


Inciso B: Optimización con variables continuas
Se resolvió un modelo de programación lineal donde la producción y el inventario pueden ser números fraccionarios.
El modelo resultó óptimo con los siguientes valores:

Tabla de resultados:
Mes	Producción	Inventario	Costo producción	Costo inventario
1	205.0	25.0	10250.0	200.0
2	225.0	0.0	10125.0	0.0
3	190.0	0.0	10450.0	0.0
4	160.0	20.0	8320.0	200.0
5	225.0	25.0	10800.0	200.0
6	225.0	0.0	11250.0	0.0

Costo total óptimo con producción continua: $61,795.0




Inciso C: Optimización con variables enteras
Se reformuló el modelo para que las variables de producción fueran enteras (números completos).
El resultado fue exactamente el mismo:

Costo total óptimo con producción entera: $61,795.0
Diferencia con modelo continuo: $0.0

Esto indica que la solución fraccionaria ya arrojaba valores enteros o muy cercanos.


## Conclusiones

- El modelo de producción minimiza exitosamente los costos totales.
- No hubo diferencia entre los resultados enteros y continuos, lo cual sugiere que el problema no requiere forzar enteros.
- Julia con `JuMP` y `HiGHS` permite resolver problemas reales de optimización de forma eficiente.
