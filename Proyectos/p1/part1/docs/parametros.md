# Parámetros

## Explicación de parámetros

| Parámetro      | Tipo  | Rango / Valores  |             Default | Descripción                                               |
| -------------- | ----- | --------------:  | ------------------: | --------------------------------------------------------- |
| `--file`       | str   |  ruta existente  | `data/berlin52.tsp` | Archivo TSPLIB a cargar.                                  |
| `--N`          | int   |            >= 10 |                 300 | Tamaño de población.                                      |
| `--maxIter`    | int   |             >= 1 |                1500 | Iteraciones máximas (generaciones).                       |
| `--survivors`  | float |          \[0,1]  |                0.20 | Fracción S de sobrevivientes.                             |
| `--crossover`  | float |          \[0,1]  |                0.60 | Fracción C creada por cruce.                              |
| `--mutation`   | float |          \[0,1]  |                0.20 | Fracción M creada por mutación. **S+C+M=1**.              |
| `--pc`         | float |          \[0,1]  |                0.95 | Probabilidad de aplicar cruce a una pareja.               |
| `--pm`         | float |   \[0,1] o `-1`  |                  -1 | Mutación ligera a hijos (si `-1` -> usa 1/n).             |
| `--elitism`    | float |          \[0,1]  |                0.05 | Fracción élite reinyectada.                               |
| `--k`          | int   |             >= 2 |                   5 | Tamaño de torneo (selección).                             |
| `--scx`        | flag  |               —  |                 off | Si está presente, usa SCX en lugar de OX.                 |
| `--twoOptProb` | float |          \[0,1]  |                0.05 | Proporción de hijos sometidos a **una** 2-opt.            |
| `--stall`      | int   |             >= 0 |                 400 | Cortar si no mejora en `stall` generaciones.              |
| `--timeLimit`  | float |       >= 0 (seg) |                 0.0 | Cortar por tiempo (0 = sin límite).                       |
| `--record`     | flag  |               —  |                 off | Guarda un PNG en cada mejora.                             |
| `--framesDir`  | str   |         carpeta  |            `frames` | Carpeta para PNG de mejoras.                              |
| `--gifOut`     | str   |     ruta `.gif`  |                  "" | Construye GIF desde `framesDir` (requiere `--record`).    |
| `--seed`       | int   |      cualquiera  |                  42 | Semilla aleatoria (reproducibilidad).                     |
| `--estimate`   | int   |             >= 1 |                   0 | Corre *warmup* N gen para estimar tiempo total y termina. |
| `--noPlot`     | flag  |               —  |                 off | No mostrar la figura final.                               |

## Uso de parámetros

### Tabla 1 — Parámetros y efectos

| Parámetro          | Qué controla                                   | Si (+) (más)                              | Si (-) (menos)                           | Interacciones clave                                         |
| ------------------ | ---------------------------------------------- | ----------------------------------------- | ---------------------------------------- | ----------------------------------------------------------- |
| **N**              | Tamaño de población                            | +diversidad, +estabilidad, +tiempo        | +ruido estocástico, +velocidad           | Con `k` (torneo), `twoOptProb` (costo), `stall`/`timeLimit` |
| **survivors (S%)** | Porción copiada tal cual                       | +explotación, +estabilidad, −diversidad   | +diversidad, riesgo de olvidar buenos    | Con `elitism`, con `k`                                      |
| **crossover (C%)** | Porción creada por cruce                       | +recombinación (si `pc` alto)             | −exploración, +copias                    | Con `pc` y operador (`--scx`/OX)                            |
| **mutation (M%)**  | Porción por mutación pura                      | +diversidad, +escape locales              | −diversidad                              | Con `pm` (mutación ligera); M% **siempre** muta             |
| **pc**             | Prob. de cruzar una pareja                     | +hijos recombinados (menos copias)        | +copias de padres                        | Con `C%` y operador (SCX > OX en calidad)                   |
| **pm**             | Prob. de mutación ligera en hijos de cruce     | +diversidad, +escape                      | +conservación, riesgo de estancamiento   | Si `pm=0` y `M%=0` => **cero** diversidad                   |
| **elitism**        | No./% élite reinyectado                         | +protección del best, +explotación        | +diversidad, riesgo de olvidar best      | No exceder S% (o mantener bajo)                             |
| **k**              | Tamaño de torneo                               | +presión selectiva, −diversidad           | +exploración, +ruido                     | Con N (k relativo a N), con S%                              |
| **--scx**          | Usa SCX (vs. OX)                               | Hijos con mejor costo inicial             | (OX) más neutro, requiere 2-opt          | SCX escala mejor en n grandes                               |
| **twoOptProb**     | % de hijos pulidos con 2-opt                   | +calidad media, +tiempo                   | −tiempo, −pulido                         | Con N y C%+M% (No. de hijos)                                 |
| **stall**          | Paro por estancamiento                         | +chance mejoras tardías, +tiempo          | +cortes tempranos                        | Con `timeLimit`/`maxIter`                                   |
| **timeLimit**      | Paro por tiempo (s)                            | Corta a tiempo fijo                       | —                                        | Con `stall`/`maxIter`                                       |
| **maxIter**        | Tope de generaciones                           | +búsqueda                                 | +corte                                   | Con `stall`/`timeLimit`                                     |

### Tabla 2 — Quién aporta diversidad y quién aporta explotación

| Mecanismo          | Principal efecto              | Riesgo si (+)                 | Riesgo si (-)          | Úsalo para               |
| ------------------ | ----------------------------- | ----------------------------- | ---------------------- | ------------------------ |
| **S% (survivors)** | Explotación (conserva buenos) | Convergencia prematura        | Olvidar buenos tours   | Estabilidad              |
| **k (torneo)**     | Explotación (si k grande)     | Pérdida de diversidad         | Selecciones ruidosas   | Ajustar presión          |
| **C% + pc**        | Exploración (recombinar)      | — (si pc muy bajo -> copias)  | Poca recombinación     | Mezclar building blocks  |
| **M%**             | Diversidad "fuerte"           | Demasiado ruido               | Falta de diversidad    | Salir de óptimos locales |
| **pm**             | Diversidad "ligera"           | Romper buenos hijos           | Estancarse             | Afinar variación fina    |
| **twoOptProb**     | Intensificación local         | Coste extra                   | Menos pulido           | Bajar costo sin ruido    |
| **elitism**        | Protección del best           | Atasco si es alto             | Pérdida del best       | Estabilidad del récord   |

### Tabla 3 — Chequeos de coherencia

| Regla                   | Qué verificar                | Por qué                              |
| ----------------------- | ---------------------------- | ------------------------------------ |
| **S% + C% + M% = 1.0**  | Exacto (considera redondeos) | Evitar población != N                |
| **N >= 10**             | Tu código lo exige           | Evitar dinámica degenerada           |
| **elitism <= \~S%**     | O mantén `elitism` bajo      | Evitar sobre-sobrescritura constante |
| **pc >= 0.8**           | Ideal 0.9–1.0                | Evitar demasiadas copias             |
| **(M% > 0) o (pm > 0)** | Al menos uno > 0             | Sin esto **no hay** diversidad       |
| **k en 3–7**            | No poner k $\approx$ N       | Evitar presión excesiva              |
| **twoOptProb <= 0.3**   | Subir gradualmente           | Evitar costes altos "inútiles"       |
| **stall y timeLimit**   | Consistentes con `maxIter`   | No cortar demasiado pronto/ tarde    |

### Tabla 4 — Síntomas y Ajustes rápidos

| Síntoma                         | Causa probable                | Ajuste                                                       |
| ------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| Se estanca muy pronto           | S alto, k alto, pm bajo, M=0  | (-)S, (-)k, (+)pm (p.ej. 1/n -> 2/n), (+)M, (+)twoOptProb    |
| Mejora pero luego empeora mucho | pm alto, M alto               | (-)pm, (-)M, (+)S o (+)elitism levemente                     |
| Mucho tiempo sin mejoras        | twoOptProb bajo, C bajo       | (+)twoOptProb, (+)C, activar `--scx`                         |
| Población "clonada"             | pc bajo, k alto, elitism alto | (+)pc, (-)k, (-)elitism, (+)M o (+)pm                        |
| Oscila/ruidosa                  | pm/M muy altos                | (-)pm, (-)M, mantener twoOptProb                             |
| Corre lento                     | N alto, twoOptProb alto       | (-)N, (-)twoOptProb, usa SCX (mejores hijos con menos 2-opt) |

### Tabla 5 — Valores guía (base)

| Escala          |        N | S% / C% / M%                      | pc       | pm                       | elitism   | k   | twoOptProb | stall     |
| --------------- | -------: | --------------------------------- | -------- | ------------------------ | --------- | --- | ---------- | --------- |
| **52 nodos**    |  150–300 | 0.20 / 0.60 / 0.20                | 0.9–1.0  | $\approx$1/52 (0.02)     | 0.02–0.05 | 5   | 0.05–0.15  | 200–800   |
| **\~500 nodos** | 800–1200 | 0.15–0.25 / 0.55–0.65 / 0.15–0.25 | 0.95–1.0 | 1/n (0.002)–0.02         | 0.02–0.05 | 3–5 | 0.03–0.10  | 1000–5000 |

> Para n grandes, **SCX** suele rendir mejor que OX; para n pequeños, OX va bien.

### Reglas "huele a mal" (rápidas)

* `S>=0.5` **y** `elitism>=0.2` -> clonación/atasco.
* `C<=0.3` **o** `pc<=0.6` -> poca recombinación (copias).
* `M=0` **y** `pm=0` -> sin diversidad (casi seguro estancamiento).
* `k>=N/2` -> presión excesiva (ganan siempre los top).
* `twoOptProb>=0.5` con N grande -> tiempo muy alto con poca ganancia marginal.
* `stall` muy bajo (p.ej. <100 en 52 nodos) -> cortes prematuros; muy alto sin `timeLimit` -> runs eternos.
