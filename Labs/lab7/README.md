# Lab 7 — Generadores de Números Pseudoaleatorios y Comparación de Muestras

En las clases anteriores hemos aprendido cómo simular y generar una muestra de una variable aleatoria $X$, a partir de una variable uniforme.
En este laboratorio investigaremos cómo construir un generador de una variable uniforme $Y \sim Unif(0,1)$ y evaluaremos su desempeño mediante distintos métodos y pruebas estadísticas.

## Entorno

- Python 3.13.5

```bash
# instalar dependencias
pip install -r requirements.txt
```

## Estructura

```bash
.
├── README.md
├── docs/          # guía y reporte
├── p1/            # Generador LCG (Linear Congruential Generator)
├── p2/            # Generador Mersenne Twister
├── p3/            # Pruebas NIST SP 800-22
├── p4/            # Comparación de muestras Geométricas
├── p5/            # Comparación de muestras Normales
└── requirements.txt
```

## Problemas

### 1. Generador Pseudoaleatorio Uniforme — LCG (`p1/Reporte_p1.md`)

Implementar un generador tipo *Linear Congruential Generator* para producir:

- Una muestra uniforme discreta $x_1, x_2, \ldots, x_n$.
- Una muestra continua $Unif(0,1)$.

Analizar estadísticos, histogramas y aplicar pruebas de hipótesis para evaluar su uniformidad.

### 2. Generador Mersenne Twister (`p2/Reporte_p2.md`)

Implementar el generador *Mersenne Twister* de `numpy.random` y repetir el análisis anterior.
Comparar los resultados obtenidos frente al LCG.

### 3. Pruebas NIST SP 800-22 (`p3/Reporte_p3.md`)

Aplicar la batería de tests NIST SP 800-22 para secuencias de bits generadas con LCG y Mersenne Twister.
Usar librerías como `sts-pylib`, `nistrng` o `sp80022suite`.
Reportar los *p-values* y determinar cuál generador muestra mejor desempeño.

### 4. Comparar muestras de una Geométrica (`p4/Reporte_p4.md`)

Generar dos muestras $Geom(p)$:

- Una con `scipy.stats`.
- Otra con el método de la transformada integral.
  Compararlas con pruebas de **Chi-Cuadrado** y **Kolmogorov–Smirnov** usando $\alpha = 0.05$.

### 5. Comparar muestras de una Normal (`p5/Reporte_p5.md`)

Generar dos muestras $\mathcal{N}(\mu, \sigma^2)$:

- Una teórica con `scipy.stats`.
- Una empírica con la transformada integral.
  Evaluar si provienen de la misma distribución mediante **Chi-Cuadrado** y **Kolmogorov–Smirnov**.
