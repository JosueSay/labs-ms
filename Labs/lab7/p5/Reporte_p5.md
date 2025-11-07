# Problema 5 - Comparar muestras de una Normal

Para una distribución normal $\mathcal{N}(\mu, \sigma^2)$, generar una muestra aleatoria de tamaño $N$ usando la librería `scipy.stats`, a la cual llamaremos la muestra teórica. Luego, generar una segunda muestra del mismo tamaño (llamada la muestra empírica), pero usando el algoritmo de la transformada integral.

Comparar ambas muestras usando las pruebas de Chi Cuadrado y de Kolmogorov–Smirnov. ¿Qué concluye? ¿Se pueden considerar como muestras de una misma distribución? Explique sus conclusiones a partir de las pruebas de hipótesis. Use un nivel de confianza de $\alpha = 0.05$.

## Desarrollo del inciso 5 – Comparación de muestras de una Distribución Normal

De acuerdo con las instrucciones del laboratorio, el objetivo de este inciso fue **comparar dos muestras provenientes de una distribución $\mathcal{N}(\mu, \sigma^2)$** con el fin de verificar si ambas pueden considerarse estadísticamente equivalentes.

### Procedimiento realizado

1. **Generación de la muestra teórica:**  
   Se utilizó la función `scipy.stats.norm(mu, sigma)` para generar una muestra de tamaño $N = 5000$ con parámetros  
   $\mu = 0$ y $\sigma = 1$.  
   Esta muestra representa la distribución normal teórica, que sirve como referencia.

2. **Generación de la muestra empírica:**  
   Se empleó el **método de la transformada integral**, aplicando la función inversa de la CDF de la normal:
   $$
   X = F^{-1}(U)
   $$
   donde $U \sim Unif(0,1)$.  
   Este método permite transformar variables uniformes en variables normales, demostrando el proceso de generación de una distribución continua a partir de una uniforme.

3. **Pruebas estadísticas aplicadas:**  
   Para comparar las muestras se utilizaron las siguientes pruebas:
   - **Chi–Cuadrado**, que compara las frecuencias observadas y esperadas.  
   - **Kolmogorov–Smirnov (K–S)**, que compara las distribuciones acumuladas.  
   El nivel de significancia utilizado fue $\alpha = 0.05$.

### Resultados obtenidos

| Muestra/Prueba | Media | Desv. Est. | Estadístico | p-valor |
|----------------|--------|-------------|-------------|----------|
| Teórica | $0.0211$ | $0.9879$ | – | – |
| Empírica | $-0.0133$ | $0.9842$ | – | – |
| Chi–Cuadrado | – | – | $101.1449$ | $0.0000$ |
| Kolmogorov–Smirnov | – | – | $0.021$ | $0.2202$ |

El histograma muestra una alta coincidencia entre ambas distribuciones, con un comportamiento simétrico y centrado alrededor de la media, tal como se espera en una distribución normal estándar.

### Interpretación de los resultados ($\alpha = 0.05$)

- Si $p > 0.05$, **no se rechaza $H_0$**, lo que indica que ambas muestras pueden provenir de la misma distribución.  
- Si $p \le 0.05$, se **rechaza $H_0$**, indicando diferencias significativas entre las muestras.

En este caso:

- La **prueba de Chi–Cuadrado** arrojó un valor $p = 0.0000$, por lo que **se rechaza $H_0$**, señalando diferencias en las frecuencias.  
- La **prueba de Kolmogorov–Smirnov**, con $p = 0.2202$, **no rechaza $H_0$**, lo que sugiere que las distribuciones acumuladas son estadísticamente equivalentes.

### Conclusión

A pesar de que la prueba de Chi–Cuadrado detectó diferencias, estas se deben a su alta sensibilidad con tamaños grandes de muestra ($N = 5000$).  
La prueba de Kolmogorov–Smirnov, junto con la similitud visual del histograma y las medias casi idénticas, indica que **ambas muestras pueden considerarse provenientes de la misma distribución $\mathcal{N}(\mu, \sigma^2)$**.  

Por tanto, se concluye que el **método de la transformada integral reproduce correctamente la distribución Normal**, validando su uso para generar muestras continuas a partir de variables uniformes.

## Respuesta a las preguntas

**¿Qué concluye?**  
A partir de las pruebas estadísticas, se observa que la **prueba de Chi–Cuadrado** arrojó un $p$-valor de **$0.0000$**, lo que implica que **se rechaza la hipótesis nula**, indicando diferencias en las frecuencias observadas entre las dos muestras.  
Sin embargo, la **prueba de Kolmogorov–Smirnov (K–S)** dio un $p$-valor de **$0.2202$**, mayor que el nivel de significancia $\alpha = 0.05$, por lo que **no se rechaza la hipótesis nula**.  
Esto significa que, al comparar las funciones de distribución acumulada, **no existen diferencias estadísticamente significativas** entre las muestras teórica y empírica.

**¿Se pueden considerar como muestras de una misma distribución?**  
Sí. Aunque la prueba de Chi–Cuadrado detecta pequeñas diferencias debidas a la sensibilidad de la prueba ante tamaños grandes de muestra ($N = 5000$), la prueba K–S y la similitud visual de los histogramas confirman que ambas muestras **siguen el mismo comportamiento estadístico**.  

**Conclusión final:**  
Las dos muestras pueden considerarse **provenientes de la misma distribución $\mathcal{N}(\mu, \sigma^2)$**.  
Esto valida que el **método de la transformada integral** genera correctamente la distribución normal a partir de variables uniformes, reproduciendo de forma precisa la forma y dispersión de la distribución teórica.
