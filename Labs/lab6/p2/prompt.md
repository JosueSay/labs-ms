# Instrucciones del prompt — Simulación SIR por autómata celular 2D

## Objetivo
Generar una simulación visual del modelo SIR (Susceptible–Infectado–Recuperado) mediante un autómata celular 2D y producir una animación (.gif o .mp4) que muestre:
- la propagación del contagio en el grid (panel izquierdo), y
- las curvas S(t), I(t), R(t) en el tiempo (panel derecho).

## Parámetros (declarar como variables en el código)
- M = 60           # altura del grid (filas)  
- N = 60           # anchura del grid (columnas)  
- I0 = 5           # número inicial de infectados  
- T = 500          # número total de pasos de simulación  
- r = 1            # radio de vecindad (Moore)  
- β = 0.3          # tasa de infección  
- γ = 0.05         # tasa de recuperación  

Opcional: semilla para reproducibilidad (SEED).

## Estados de cada celda
- 0: Susceptible (S) — color azul  
- 1: Infectado (I) — color rojo  
- 2: Recuperado (R) — color verde  

## Reglas por paso de tiempo
1. Para cada celda susceptible (S):  
   - Si al menos un vecino (en radio r, vecindad Moore) está infectado, la celda se infecta con probabilidad β.  
2. Para cada celda infectada (I):  
   - Se recupera con probabilidad γ.  
3. Recuperadas (R) permanecen inmunes.

Actualizaciones: actualizar todo el grid por pasos discretos (sin efecto intermedio); almacenar en cada t:
- S(t) = número de susceptibles
- I(t) = número de infectados
- R(t) = número de recuperados

## Visualización requerida
- Figura con dos paneles lado a lado:
  - Panel izquierdo: imagen del grid con colores (azul, rojo, verde). Título debe mostrar:
    `t = {tiempo} | S = {susceptibles} | I = {infectados} | R = {recuperados}`
  - Panel derecho: curvas S(t) (verde), I(t) (rojo), R(t) (azul) con etiquetas, leyenda y ejes.
- Las curvas deben actualizarse en tiempo real junto con la animación del grid.

## Salida
- Guardar animación como `simulacion_SIR.gif` .
- Además: generar y guardar un PNG específico si en el tiempo t = 193 se cumplen exactamente:
  ```
  t = 193  |  S = 16  |  I = 852  |  R = 2732
  ```
  - Nombre sugerido: `snapshot_t193_S16_I852_R2732.png`
  - Si los conteos no coinciden, guardar un mensaje en la salida indicando los valores reales en t=193.



## Consideraciones adicionales
- Usar bordes no periódicos (padding/vecindad limitada) o documentar si se emplea periodicidad.  
- Recomendar fijar SEED para reproducibilidad.  
- Mantener arrays/contadores de longitud T+1 para que la animación y las curvas sean consistentes.  
- Optimizar cálculo de vecinos para evitar bucles excesivos (ej.: convolución o desplazamientos con numpy).  

## Entregable
- Archivo con el código (por ejemplo `sim2.py` o `simulacion_SIR.py`) en la carpeta correspondiente.  
- Animación guardada `simulacion_SIR.gif`.  
- PNG de snapshot si se cumple la condición solicitada en t=193.  
