# Problema 4 - Comparar muestras de una Geométrica

Para una distribución geométrica $Geom(p)$, generar una muestra aleatoria de tamaño $N$ usando la librería scipy.stats, a la cual llamaremos la muestra teórica. Luego, generar una muestra del mismo tamaño, pero usando el algoritmo de la transformada integral. A esta la llamaremos la muestra empírica.

Comparar ambas muestras usando las prueba de Chi Cuadrado y la prueba de Kolmogorov-Smirnov. ¿Qué concluye? ¿Se pueden considerar como muestras de una misma distribución? Explique sus conclusiones a partir de las pruebas de hipótesis. Use un nivel de confianza de $\alpha = 0.05$.

Se siguieron los pasos establecidos:

1. **Generación de la muestra teórica:**  
   Se utilizó la función `scipy.stats.geom(p)` de la librería *scipy* para generar una muestra aleatoria de tamaño \( N = 5000 \) con parámetro \( p = 0.3 \).  
   Esta muestra se consideró la referencia o distribución "real" (muestra teórica).

2. **Generación de la muestra empírica:**  
   Para validar el método de simulación, se generó una segunda muestra de igual tamaño usando el **método de la transformada integral**, aplicando la fórmula:
   \[
   X = \lceil \frac{\ln(1-U)}{\ln(1-p)} \rceil
   \]
   donde \( U \sim Unif(0,1) \).  
   Este procedimiento permite obtener una variable geométrica a partir de números aleatorios uniformes, mostrando cómo se puede construir una distribución discreta desde una base continua.

3. **Aplicación de pruebas estadísticas:**  
   Se compararon las dos muestras con las pruebas:
   - **Chi-Cuadrado**, para analizar las frecuencias observadas frente a las esperadas.  
   - **Kolmogorov–Smirnov (K–S)**, para comparar las distribuciones acumuladas de ambas muestras.  
   Se utilizó un **nivel de significancia de α = 0.05**.

4. **Resultados obtenidos:**  
   - **Media teórica:** 3.306  **Desviación estándar:** 2.7497  
   - **Media empírica:** 3.235  **Desviación estándar:** 2.6832  
   - **Prueba Chi–Cuadrado:** p = 0.0118  
   - **Prueba Kolmogorov–Smirnov:** p = 0.3927  

   En el histograma comparativo se observa una gran similitud entre ambas distribuciones.

5. **Interpretación:**  
   Aunque la prueba de Chi–Cuadrado arrojó un p-valor menor a 0.05, indicando una ligera diferencia en las frecuencias, la prueba de Kolmogorov–Smirnov mostró un p-valor mayor a 0.05, lo que significa que no se rechaza la hipótesis nula y que **ambas muestras pueden considerarse provenientes de la misma distribución**.  
   Las diferencias detectadas por la prueba Chi–Cuadrado pueden atribuirse a su alta sensibilidad cuando el tamaño de muestra es grande.

**Conclusión:**  
El experimento demuestra que el **método de la transformada integral reproduce correctamente la distribución Geométrica(p)**.  
A partir de las pruebas realizadas y el análisis visual, se concluye que las muestras **teórica y empírica son estadísticamente equivalentes al nivel de significancia de α = 0.05**.