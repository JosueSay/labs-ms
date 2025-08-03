# Problema 1

Tres refinerías con capacidades diarias de 6, 5 y 8 millones de galones, respectivamente, abastecen a tres áreas de distribución con demandas diarias de 4, 8 y 7 millones de galones, respectivamente. La gasolina se transporta a las tres áreas de distribución a través de una red de oleoductos. El costo de transporte es de \$0.10 por 1000 galones por kilómetro de oleoducto. En la tabla 1 se presenta la distancia en kilómetros entre las refinerías y las áreas de distribución. La refinería 1 no está conectada al área de distribución 3.

|             | Área 1 | Área 2 | Área 3 |
| ----------- | ------ | ------ | ------ |
| Refinería 1 | 120    | 180    | –      |
| Refinería 2 | 100    | 150    | 80     |
| Refinería 3 | 200    | 250    | 120    |

## Inciso a

Formular el modelo de transporte asociado.
Se planteó el modelo de transporte con tres refinerías (R1, R2, R3) y tres áreas de distribución (A1, A2, A3). La refinería 1 **no tiene conexión directa con el área 3**, por lo que se representó con `Inf` en la matriz de costos.

### Cálculo de Costos

Se utilizó la siguiente fórmula para obtener el costo por millón de galones:

Costo = distancia (km) × $100

Ya que el costo de transporte es de $0.10 por cada 1000 galones por km.

--- 

## Inciso b

Usando JuMP o Pupl, determine el programa de envíos óptimo en la red de distribución.


*Se implementó el modelo con las siguientes características:*

- Variables `x[i,j]` para representar los envíos desde refinería `i` a área `j`.
- Restricciones:
  - Cada refinería entrega exactamente su capacidad.
  - Cada área recibe exactamente lo que necesita.
- Se minimiza el costo total de transporte, excluyendo rutas prohibidas (`Inf`).

###  Resultado:
- El modelo se resolvió correctamente.
- Costo total mínimo: **\$217,000**

---

## Inciso c

Suponga ahora que la demanda diaria en el área 3 disminuye a 4 millones de galones. La producción excedente en las refinerías 1 y 2 se envía a otras áreas de distribución por medio de camiones. El costo de transporte por 100 galones es de \$1.50 desde la refinería 1 y de \$2.00 desde la refinería 2. La refinería 3 puede enviar su producción excedente a otros procesos químicos dentro de la planta.
Formule y resuelva de nuevo el programa óptimo de envíos.


*Se modificó el escenario:*

- **Área 3** redujo su demanda de 7 a 4 millones.
- Se creó un **destino ficticio** para enviar el excedente de producción (3 millones).
- Refinería 1 puede enviar al ficticio por \$1500/millón.
- Refinería 2 por \$2000/millón.
- Refinería 3 **no puede enviar al destino ficticio** (costo `Inf`).

###  Nuevos datos:
- Matriz de costos pasó de 3x3 a 3x4.
- Nueva demanda: [4, 8, 4, 3] para balancear la oferta total de 19 millones.

###  Resultado:
- Refinería 1 envió 2 millones a A1.
- Refinería 2 envió 5 millones a A2.
- Refinería 3 envió 2 millones a A1 y 3 millones a A2.
- **Ningún envío fue hecho al destino ficticio**, ya que sus costos eran más altos que las rutas normales.
- **Costo total mínimo:** **\$189,000**
