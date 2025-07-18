# Laboratorio 1 - Programación Lineal

Se abordaron cuatro problemas de programación lineal utilizando Julia y Excel donde requería.

## Entorno

- Julia 1.11.6
- [JuMP.jl](https://jump.dev/)
- [HiGHS.jl](https://github.com/jump-dev/HiGHS.jl) o similar (como GLPK)
- IJulia
- Jupyter Notebook

## Estructura del repositorio

```bash
lab1/
├── lab1.ipynb                  # Notebook global con el procedimiento/respuestas unificadas
├── Manifest.toml               # Dependencias del entorno Julia
├── Project.toml                # Proyecto Julia
├── README.md
├── docs/                       # Documentación extra para los problemas
├── images/                     # Gráficos o imágenes utilizadas
├── problema1/                  # Problema 1: Simplex vs JuMP
├── problema2/                  # Problema 2: Modelo de Producción (Acme)
├── problema3/                  # Problema 3: Asignación de autobuses
└── problema4/                  # Problema 4: Renovación urbana
```

## Problemas resueltos

### 1. Problema de programación lineal (Simplex)

Se maximiza una función objetivo con restricciones lineales. Se resolvió en:

- Excel (implementación de Simplex)
- JuMP (Julia)

### 2. Modelo de Producción (Períodos múltiples)

Optimización de la producción mensual para minimizar costos de producción e inventario:

- Costo variable de producción y almacenaje
- Restricción de capacidad mensual
- Incluye gráficos y comparación con estrategia no óptima

### 3. Modelo de asignación de horarios

Asignación mínima de autobuses por turnos de 4 horas:

- Minimización de la cantidad total de autobuses necesarios
- Restricción de operación continua de 8 horas
- Matriz de cobertura de turnos

### 4. Modelo de renovación urbana

Maximización de impuestos recaudados en un proyecto de vivienda:

- Demolición de casas y uso del terreno para nuevas unidades
- Restricciones de uso de suelo y proporciones mínimas
- Comparación entre solución continua y entera
