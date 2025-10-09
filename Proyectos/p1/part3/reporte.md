# Inciso 3
Tablas comparativas de las solciones de cada escenario
---
## Escenario 1 - cherry189
### Informacion escenario
- **Número de ciudades:** 189
- **Tamaño población (GA):** 700
- **Número de iteraciones (GA):** 999999 (max.)
- **Número de variables:** 

![Imagen Resultados Cherry](/imagenes_resporte/Cherry189.png)

La solución fue encontrada en mucho menos tiempo en LP que en GA, indicando una eficiencia superior en LP, se obtuvo un porcentaje de error del 8.74% con respecto al resultado en GA, indicando superioridad del LP frente a este.
---
## Escenario 2 - Eil101
### Informacion escenario
- **Número de ciudades:** 189
- **Tamaño población (GA):** 700
- **Número de iteraciones (GA):** 999999 (max.)
- **Número de variables:** 

![Imagen Resultados Eil101](/imagenes_resporte/eil101.png)
El tiempo que llevó encontrar la solución fue menor en GA que LP, con solo 1200 segundos logró ser más que el doble de rápido que LP, sin embargo, el porcentaje de error es del 9.24% con respecto al resultado en GA a pesar de que LP tomó más tiempo para encontrar la solución.
---
## Escenario 3 - Gr229
### Informacion escenario
- **Número de ciudades:** 189
- **Tamaño población (GA):** 700
- **Número de iteraciones (GA):** 999999 (max.)
- **Número de variables:** 

![Imagen Resultados Eil101](/imagenes_resporte/gr229.png)
LP fue más rápido que GA y por mucho, sin embargo, el mejor resultado fue de GA. El porcentaje de error es mucho más grande en esta instancia alcanzando el 37.98% siendo ya una cifra no trivial a diferencia de los otros.

## Conclusiones
- LP tiende a ser mucho más rápido que GA (este último habiendo alcanzado hasta 8 horas en los escenarios), pero por otro lado también ha llevado a tener errores significativos, como se vio en el escenario gr229
- Podemos decir que GA es un poco más robusto, sobre todo para distancias grandes que LP pero este es mucho más rápido.
