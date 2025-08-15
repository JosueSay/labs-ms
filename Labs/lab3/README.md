# Laboratorio 3

Este laboratorio implementa y analiza distintos métodos de optimización basados en descenso por gradiente, incluyendo variantes deterministas, estocásticas y de segundo orden, así como su aplicación en problemas de funciones de prueba, búsqueda de múltiples mínimos y ajuste de modelos de regresión regularizada.

## Entorno

- Python 3.13.5
- Jupyter Notebook

## Estructura del repositorio

```bash
.
├── README.md
├── docs
│   ├── guia.pdf                 # Enunciado oficial del laboratorio
│   └── reporte.md               # Reporte general con resultados y análisis
├── images
│   └── example_graph.png        # Ejemplo de visualización de convergencia
├── problema1
│   ├── p1.ipynb                  # Implementación de métodos de descenso gradiente
│   └── reporte.md
├── problema2
│   ├── p2.ipynb                  # Pruebas con funciones dadas y análisis comparativo
│   └── reporte.md
├── problema3
│   ├── p3.ipynb                  # Función suma de gaussianas 2D y búsqueda de mínimos
│   └── reporte.md
└── problema4
    ├── datos_lab3.csv            # Datos de serie de tiempo
    ├── p4.ipynb                  # Regresión con regularización y comparación
    └── reporte.md
```

## Problemas resueltos

### 1. Implementación de métodos de descenso gradiente

Se desarrollaron cinco variantes:

- **Descenso gradiente naïve** con dirección de descenso aleatoria.
- **Descenso máximo naïve**.
- **Descenso de Newton** con Hessiano exacto.
- **Gradiente conjugado** (Fletcher-Reeves, Hestenes-Stiefel, Polak-Ribière).
- **BFGS**.

Cada método recibe como argumentos:

- Función objetivo $f$.
- Gradiente $df$.
- Hessiano $ddf$ (cuando aplica).
- Punto inicial $x_0 \in \mathbb{R}^n$.
- Tamaño de paso $\alpha > 0$.
- Número máximo de iteraciones $maxIter$.
- Tolerancia $\varepsilon$ y criterio de paro.

La salida incluye: mejor solución encontrada, secuencia de iteraciones, valores de $f(x_k)$, errores en cada paso y estado de convergencia.

### 2. Pruebas con funciones de referencia

Se evaluaron los algoritmos sobre:

1. **Función polinómica en $\mathbb{R}^2$**

$$
f(x, y) = x^4 + y^4 - 4xy + \frac{1}{2}y + 1
$$

2. **Función de Rosenbrock en $\mathbb{R}^2$**

$$
f(x_1, x_2) = 100(x_2 - x_1^2)^2 + (1 - x_1)^2
$$

3. **Función de Rosenbrock en $\mathbb{R}^7$**

$$
f(x) = \sum_{i=1}^6 100(x_{i+1} - x_i^2)^2 + (1 - x_i)^2
$$

Se analizaron:

- Visualizaciones de convergencia para casos 2D.
- Tablas comparativas con número de iteraciones, error y convergencia.
- Gráficas del error de aproximación en función de las iteraciones.

### 3. Función “suma de gaussianas” 2D

Se construyó:

$$
f(x) = -\sum_{i=1}^k \exp\left(-\frac{1}{2\sigma} \|x - x_i\|^2\right)
$$

- $k = 8$ gaussianas con centros $x_i$ en $[0,8] \times [0,8]$ elegidos aleatoriamente (distribución uniforme).
- Los puntos $x_i$ se fijaron para todo el experimento.
- Se aplicaron métodos de optimización desde múltiples puntos iniciales para encontrar distintos mínimos locales.
- Se generó una tabla con todos los mínimos encontrados y visualizaciones de sus trayectorias.

### 4. Ajuste de modelo de regresión regularizada

Se trabajó con el conjunto de datos `datos_lab3.csv` para ajustar:

$$
y = \beta_0 + \beta_1 x + \beta_2 x^2 + \beta_3 \sin(7x) + \beta_4 \sin(13x)
$$

El problema se planteó como la minimización de:

$$
E_\lambda(\beta) = \sum_{i=1}^n (f(x_i) - y_i)^2 + \lambda \sum_{i=1}^{n-1} (f(x_{i+1}) - f(x_i))^2
$$

Se probaron tres casos:

- $\lambda = 0$ (sin regularización).
- $\lambda = 100$ (regularización de Tikhonov moderada).
- $\lambda = 500$ (regularización fuerte).

Se compararon las tres curvas ajustadas sobre los datos originales, analizando el efecto de la regularización sobre la suavidad y ajuste del modelo.
