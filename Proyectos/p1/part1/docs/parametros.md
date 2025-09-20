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
| `--csv`                             | str   | ruta            |    ""   | Escribe traza de eventos/metricas a CSV (mejoras, tiempos, perfil).                              |
| `--eaxFrac`                         | float | \[0,1]          |    0.15 | Fracción del presupuesto de cruces hecha con EAX-lite (mezcla adyacencias).                  |
| `--edgeLambda`                      | float | \[0,1] típico   |    0.15 | Peso del histograma de aristas para sesgar SCX hacia aristas frecuentes (explotación).       |
| `--edgeTopFrac`                     | float | \[0,1]          |    0.30 | Porción "top" de la población usada para construir el histograma de aristas.                     |
| `--edgeFreqPeriod`                  | int   | >=1              |     200 | Frecuencia (en generaciones) para recalcular el histograma de aristas.                       |
| `--assortative` / `--noAssortative` | flag  | —               |      ON | Emparejar padres maximizando lejanía de aristas (Jaccard) para diversidad (por defecto ON).  |
| `--mem3OptSteps`                    | int   | >=0              |       4 | No. de pasos de 3-opt acotado aplicados periódicamente a élites (memético suave).             |
| `--speciesPeriod`                   | int   | >=1              |     800 | Periodicidad para reconstruir especies (clustering por aristas).                             |
| `--speciesThresh`                   | float | (0,1]           |    0.35 | Umbral Jaccard para pertenencia a especie (menor = especies más "estrictas").                    |
| `--speciesCullFrac`                 | float | \[0,1]          |    0.20 | Fracción de la peor especie que se extingue (reemplaza) en eventos de culling.               |
| `--catastropheFrac`                 | float | \[0,1]          |    0.20 | Fracción de la población reemplazada en catástrofes (double-bridge + 2-opt).                 |
| `--noFlocking`                      | flag  | —               |     OFF | Desactiva el flocking como desempate en 2-opt (sin este flag está ON).                     |

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
| **eaxFrac**                                         | Cuántos cruces usan EAX-lite            | +calidad inicial de hijos                | +dependencia de 2-opt                 | Con `pc`, `C%`, `twoOptProb` (menos 2-opt si hijos ya son buenos).               |
| **edgeLambda**                                      | Fuerza del sesgo por aristas frecuentes | +explotación de "patrones"               | +riesgo de convergencia prematura     | Con `edgeTopFrac`, `edgeFreqPeriod`, `assortative` (diversidad compensa sesgo).  |
| **edgeTopFrac**                                     | Muestra para histograma                 | +estabilidad del histograma              | +ruido si muy bajo                    | Con `edgeLambda` (sesgo) y `edgeFreqPeriod` (cuándo refrescar).                  |
| **edgeFreqPeriod**                                  | Ritmo de refresco del histograma        | +adaptación a cambios                    | +costo si muy frecuente               | Afinar según dinámica; runs largos toleran valores medios.                       |
| **assortative**                                     | Emparejamiento por lejanía              | +diversidad efectiva                     | +clonación si OFF                     | Reduce clones; útil con `elitism` alto.                                          |
| **mem3OptSteps**                                    | Intensidad del memético élite           | +pulido de élites                        | +tiempo si muy alto                   | Aplica cada \~300 gens; combina con 2-opt.                                       |
| **speciesPeriod / speciesThresh / speciesCullFrac** | Manejo de especies                      | +diversidad a largo plazo                | +coste/clusters pobres si mal seteado | Útiles cuando hay estancamiento; culling reemplaza parte de la peor especie.     |
| **catastropheFrac**                                 | Reinyección por catástrofe              | +escape de óptimos locales               | +pérdida de progreso si alto          | Coordinar con `stall`; suele activarse en estancamiento prolongado.              |
| **noFlocking**                                      | Desempate en 2-opt                      | (ON por defecto) mejora micro-decisiones | OFF: decisiones más neutras           | Afecta "first-improve" en 2-opt.                                                 |
| **csv**                                             | Instrumentación                         | —                                        | —                                     | Útil para post-análisis; sin impacto en calidad.                                 |

### Tabla 2 — Quién aporta diversidad y quién aporta explotación

| Mecanismo                                           | Principal efecto                                    | Riesgo si (+)                                    | Riesgo si (−)                      | Úsalo para                           |
| --------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------ | ---------------------------------- | ------------------------------------ |
| **S% (survivors)**                                  | Explotación (conserva buenos)                       | Convergencia prematura                           | Olvidar buenos tours               | Estabilidad                          |
| **k (torneo)**                                      | Explotación (si k grande)                           | Pérdida de diversidad                            | Selecciones ruidosas               | Ajustar presión                      |
| **C% + pc**                                         | Exploración (recombinar)                            | — (si pc muy bajo ⇒ copias)                      | Poca recombinación                 | Mezclar building blocks              |
| **M%**                                              | Diversidad "fuerte"                                 | Demasiado ruido                                  | Falta de diversidad                | Salir de óptimos locales             |
| **pm**                                              | Diversidad "ligera"                                 | Romper buenos hijos                              | Estancarse                         | Variación fina                       |
| **twoOptProb**                                      | Intensificación local                               | Coste extra                                      | Menos pulido                       | Bajar costo sin ruido                |
| **elitism**                                         | Protección del best                                 | Atasco si es alto                                | Pérdida del best                   | Estabilidad del récord               |
| **eaxFrac**                                         | Hijos mejores vía **EAX-lite** (exploración guiada) | Menos diversidad si se abusa                     | Hijos pobres ⇒ más 2-opt necesario | Mejor calidad inicial de hijos       |
| **edgeLambda / edgeTopFrac / edgeFreqPeriod**       | **Sesgo por histograma de aristas** (explotación)   | Convergencia prematura si sesgo fuerte/frecuente | Falta de guía si muy bajo          | Reforzar patrones del top            |
| **assortative**                                     | Empareja **lejanos** (diversidad efectiva)          | —                                                | Clonación si OFF                   | Evitar clones en cruces              |
| **speciesPeriod / speciesThresh / speciesCullFrac** | **Especies** (diversidad a largo plazo)             | Culling excesivo ⇒ pérdida de progreso           | Clusters pobres ⇒ poco efecto      | Recuperarse de estancamientos        |
| **catastropheFrac**                                 | Reinyección fuerte (escape)                         | Borrar avances si muy alto                       | Quedarse atascado si muy bajo      | Sacudir población tras largos stalls |
| **mem3OptSteps**                                    | Pulido extra élites (3-opt acotado)                 | Tiempo alto si muy grande                        | Quedan "rebabas"                   | Afinar élites sin abusar del tiempo  |
| **flocking (ON por defecto)**                       | Desempate 2-opt pro-aristas cortas                  | Micro-sesgo si contexto no ayuda                 | Decisiones más neutras (si OFF)    | Elegir mejor entre empates en 2-opt  |

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
| **0 <= eaxFrac <= 1**                          | Fracción válida    | Presupuesto de cruces consistente.        |
| **0 <= edgeLambda <= 1**                       | Peso razonable     | Sesgo estable (evitar forzar en exceso).  |
| **0 < edgeTopFrac <= 1**                      | Muestra no vacía   | Histograma informativo.                   |
| **edgeFreqPeriod >= 1**                       | Entero positivo    | Refresco programable.                     |
| **speciesThresh ∈ (0,1]**                    | Umbral válido      | Clustering interpretable.                 |
| **0 <= speciesCullFrac, catastropheFrac <= 1** | Fracciones válidas | Reemplazos controlados.                   |
| **mem3OptSteps >= 0**                         | Entero             | Memético acotado.                         |

### Tabla 4 — Síntomas y Ajustes rápidos

| Síntoma                         | Causa probable                | Ajuste                                                       |
| ------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| Se estanca muy pronto           | S alto, k alto, pm bajo, M=0  | (-)S, (-)k, (+)pm (p.ej. 1/n -> 2/n), (+)M, (+)twoOptProb    |
| Mejora pero luego empeora mucho | pm alto, M alto               | (-)pm, (-)M, (+)S o (+)elitism levemente                     |
| Mucho tiempo sin mejoras        | twoOptProb bajo, C bajo       | (+)twoOptProb, (+)C, activar `--scx`                         |
| Población "clonada"             | pc bajo, k alto, elitism alto | (+)pc, (-)k, (-)elitism, (+)M o (+)pm                        |
| Oscila/ruidosa                  | pm/M muy altos                | (-)pm, (-)M, mantener twoOptProb                             |
| Corre lento                     | N alto, twoOptProb alto       | (-)N, (-)twoOptProb, usa SCX (mejores hijos con menos 2-opt) |
| Población "clonada" pese a C/M altos | Emparejamiento pobre          | Activar **`--assortative`** (si estaba OFF) o bajar `edgeLambda`; subir `speciesCullFrac`.                |
| Mejora inicial buena pero se estanca | Sesgo excesivo del histograma | Bajar `edgeLambda`, subir `edgeFreqPeriod` (menos refrescos) o subir `assortative`.                       |
| Largos periodos sin mejora           | Falta de perturbación         | Subir **`catastropheFrac`** o la tríada de **especies** (más culling); subir `mem3OptSteps` ligeramente.  |
| Coste alto de tiempo en élites       | Memético agresivo             | Bajar `mem3OptSteps` o la frecuencia del bloque (mantener en cada \~300 gens).                            |

### Tabla 5 — Valores guía (base)

| Escala          | N        | S% / C% / M%                      | pc       | pm                | elitism   | k   | twoOptProb | **eaxFrac** | **edgeLambda** | **edgeTopFrac** | **edgeFreqPeriod** | **assortative** | **speciesPeriod / speciesThresh / speciesCullFrac** | **catastropheFrac** | **mem3OptSteps** |
| --------------- | -------- | --------------------------------- | -------- | ----------------- | --------- | --- | ---------- | ----------: | -------------: | --------------: | -----------------: | --------------: | --------------------------------------------------: | ------------------: | ---------------: |
| **\~200 nodos** | 400–800  | 0.20/0.60/0.20                    | 0.95–1.0 | ≈1/n (0.005)–0.02 | 0.02–0.05 | 4–5 | 0.15–0.30  |   0.15–0.30 |      0.10–0.18 |       0.25–0.35 |            150–300 |              ON |                     600–800 / 0.33–0.38 / 0.15–0.25 |           0.15–0.25 |              4–6 |
| **\~500 nodos** | 800–1200 | 0.15–0.25 / 0.55–0.65 / 0.15–0.25 | 0.95–1.0 | 1/n (0.002)–0.02  | 0.02–0.05 | 3–5 | 0.10–0.25  |   0.20–0.35 |      0.12–0.20 |       0.30–0.40 |            150–300 |              ON |                    700–1000 / 0.34–0.38 / 0.15–0.25 |           0.15–0.25 |              5–8 |

### Reglas "huele a mal" (rápidas)

- `S >= 0.5` **y** `elitism >= 0.2` -> clonación / atasco.
- `C <= 0.3` **o** `pc <= 0.6` -> poca recombinación (copias).
- `M = 0` **y** `pm = 0` -> sin diversidad (estancamiento casi seguro).
- `k >= N/2` -> presión excesiva (ganan siempre los top).
- `twoOptProb >= 0.5` con N grande -> tiempo muy alto con poca ganancia marginal.
- **edgeLambda >= 0.5** o **edgeTopFrac <= 0.1** -> sesgo desmedido / histograma ruidoso.
- **edgeFreqPeriod < 50** -> sobre-costo recalculando histograma.
- **eaxFrac = 0** **y** `pc` alto con SCX/OX pobres -> hijos débiles, sobrecarga de 2-opt.
- **speciesPeriod > 5000** o **speciesThresh ≈ 1.0** -> especies inútiles; **speciesCullFrac > 0.5** -> pérdida de progreso.
- **catastropheFrac > 0.4** -> "reseteos" destructivos; **=0** en runs largos -> atascos prolongados.
- **mem3OptSteps > 12** -> coste alto con retorno decreciente.
- `stall` muy bajo (<100 en n pequeñas) -> cortes prematuros; muy alto sin `timeLimit` -> runs eternos.
