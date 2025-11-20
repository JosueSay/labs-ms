# Histogramas

🔵 **1. Modelo clásico M/M/1**  
Clientes individuales, tiempos de servicio simples.

🟠 **2. Modelo extendido con grupos (1–5 personas)**  
Representa mejor un restaurante real donde llegan familias, parejas y grupos.

Los histogramas permiten ver cómo cambia la distribución de tiempos en cada escenario.

---

## ¿Qué representan los histogramas?

Los histogramas muestran con qué frecuencia aparece un rango de tiempos.  
- Si muchas barras están cerca de 0 → los clientes casi NO esperan.  
- Si las barras se desplazan hacia la derecha → hay esperas más largas.  
- Colas largas se reflejan como valores grandes de W (tiempo en sistema) y Wq (tiempo en cola).  

Es análogo a observar cuántas familias esperaron 5 min, 10 min, 20 min…: la espera depende de la cantidad de gente y del tamaño de los grupos.

---

## 1. Histograma del Tiempo en Sistema (W)

### ¿Qué veo en este histograma?
- El modelo clásico (azul) muestra que la mayoría de clientes pasan ~0.1–0.3 h en el sistema (6–18 minutos).
- El modelo con grupos (naranja) se ensancha hacia la derecha: aparecen valores en 0.4–0.7 h.

### ¿Por qué pasa esto?
Cuando llega un grupo grande (por ejemplo 4 o 5 personas), su tiempo de servicio se multiplica por el tamaño del grupo. El servidor permanece ocupado más tiempo y los siguientes clientes sufren esperas mayores o tiempos de servicio más largos.

> “El tiempo total en el sistema (W) aumenta cuando se considera el tamaño real de los grupos. Esto se debe a que el tiempo de servicio se multiplica por el tamaño del grupo, lo que incrementa los tiempos de ocupación del servidor y desplaza la distribución de W hacia la derecha.”

---

## 2. Histograma del Tiempo de Espera (Wq)

*(solo la cola — tiempos en la fila)*

### ¿Qué veo?
- El modelo clásico tiene muchos valores cercanos a 0.0 h → la fila casi no crece.
- El modelo con grupos muestra una cola más larga hacia la derecha → esperas frecuentes en 0.1–0.5 h.

### ¿Por qué pasa esto?
- Un grupo grande puede bloquear al servidor por más tiempo.
- Los clientes que llegan después deben esperar más.
- La disipación de la cola es más lenta cuando aparecen grupos grandes.

Ejemplo práctico: si un mesero atiende a una familia de 5, aunque llegues solo tendrás que esperar más.

> “Los tiempos de espera (Wq) aumentan significativamente cuando el modelo considera grupos de tamaño variable. El servidor permanece ocupado más tiempo por cada servicio, lo que provoca que los clientes acumulen mayor tiempo de espera en la cola.”

---

## Resumen del análisis

- Se generaron histogramas comparativos para evaluar el impacto de incluir grupos de clientes en el modelo M/M/1.  
- En el modelo extendido cada llegada recibe un tamaño de grupo entre 1 y 5, lo que incrementa el tiempo de servicio por evento.  
- Resultado: introducir grupos desplaza tanto W como Wq hacia valores mayores — el servidor está ocupado más tiempo y las colas son más largas.  
- El modelo clásico concentra tiempos bajos, indicando un sistema más fluido pero menos realista para entornos como restaurantes.

---

## Conclusión

Los histogramas evidencian que el modelo con grupos representa mejor el comportamiento real de un restaurante: la variabilidad en el tamaño de las familias incrementa la carga del servidor y altera significativamente la dinámica de la cola, aumentando tanto el tiempo total en el sistema (W) como el tiempo de espera en cola (Wq).
