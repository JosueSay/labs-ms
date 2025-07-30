# Laboratorio 2 - Modelación y Simulación

Se resolvieron ocho problemas usando programación lineal y métodos numéricos implementados en Python. Los modelos fueron desarrollados e implementados en Jupyter Notebook y archivos `.md`.

## Entorno

- Python 3.11
- Jupyter Notebook

## Estructura del repositorio

```bash
lab2/
├── README.md
├── requirements.txt           # Dependencias del entorno Python
├── docs/                      # Guía y reporte general
├── p1/                        # Problema 1: Modelo de transporte
├── p2/                        # Problema 2: Problema de asignación
├── p3/                        # Problema 3: Asignación con restricciones
├── p4_p5_p6/                  # Problema 4, 5 y 6: Métodos para encontrar ceros
├── p7/                        # Problema 7: Newton-Raphson con análisis
└── p8/                        # Problema 8: Newton multidimensional
```

## Problemas resueltos

### 1. Modelo de transporte

Optimización del envío de gasolina desde refinerías a centros de distribución. Incluye:

- Formulación y solución con restricciones de conectividad.
- Escenario con demanda modificada y envío alternativo.

### 2. Problema de asignación

Asignación óptima con matriz de costos utilizando programación lineal entera.

### 3. Asignación con restricciones

Problema de asignación con restricciones adicionales sobre disponibilidad de puestos para ciertos trabajadores.

### 4. Métodos numéricos: ceros de funciones

Implementación en Python de:

- Método de bisección
- Método de la secante
- Método de Newton-Raphson

Cada función devuelve la secuencia de aproximaciones y la solución.

### 5. Zeros de función racional

Cálculo de ceros de $g(x) = x^2 + \frac{1}{x-7}$ con al menos 7 decimales. Se comparan métodos anteriores por eficiencia.

### 6. Zeros de polinomio de grado 5

Aplicación de los métodos numéricos para hallar los ceros de un polinomio no trivial.

### 7. Newton-Raphson con divergencia

Análisis del comportamiento del método partiendo de un mal punto inicial. Se propone una estrategia de corrección.

### 8. Newton multidimensional

Implementación del método de Newton para sistemas de ecuaciones no lineales en $\mathbb{R}^n$. Se resuelve un sistema de 3 ecuaciones no lineales con precisión decimal.
