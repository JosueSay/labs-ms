# Prompt utilizado

Genera un **único archivo Python** llamado **`sim1.py`** que implemente la **Simulación 1: SIR con partículas móviles** y produzca **exclusivamente un GIF** (no video .mp4 ni otros formatos). El proyecto ya tiene `imageio` instalado y el archivo `config.yaml` existe.

## 1. Modelo SIR (obligatorio, con derivadas)

Usa el sistema de Kermack–McKendrick:

$$
\frac{dS}{dt}=-\frac{\beta}{N}SI,\qquad
\frac{dI}{dt}=\frac{\beta}{N}SI-\gamma I,\qquad
\frac{dR}{dt}=\gamma I.
$$

Implementa una **versión por agentes** en el cuadrado $[0,L]\times[0,L]$ donde el contagio ocurre por **contacto** a distancia estricta `< r`.

## 2. Lectura estricta de configuración (sin valores por defecto)

* Lee `seed` y la sección **`sim1`** de `config.yaml`.
* **No uses valores por defecto.** Si falta **cualquier** clave o está fuera de rango, **termina con error** y un mensaje claro.
* Estructura **obligatoria** en `config.yaml` (todas las claves son requeridas):

```yaml
seed: 12345

sim1:
  L: 10                 # float > 0 (coincidir con el rango 0..10 observado)
  N_total: 200          # int >= 1 (coincidir con el total S+I+R≈200)
  I0: 5                 # int, 1 <= I0 < N_total
  vmax: 0.8             # float > 0
  r: 0.6                # float > 0
  beta: 0.35            # float >= 0
  gamma: 0.08           # float >= 0
  dt: 1.0               # float > 0 (paso de tiempo; la imagen muestra t≈223 pasos)
  steps: 230            # int > 0 (número de pasos; suficiente para ver el pico de I)
  fps: 20               # int > 0 (frames por segundo del GIF)
  boundary: "reflect"   # string, valor debe ser exactamente "reflect" o "wrap"
  out_gif: "images/sim1.gif"            # ruta de salida del GIF
  curves_png: "images/sim1_curvas.png"  # ruta de salida del PNG de curvas SIR
```

## 3. Dinámica de partículas (reglas obligatorias)

* Inicializa `N_total` posiciones uniformes en $[0,L]^2$ y velocidades con dirección aleatoria y **norma ≤ `vmax`**.
* Integra con **Euler explícito** y paso `dt`.
* **Bordes** según `boundary`:

  * `"reflect"`: rebote especular.
  * `"wrap"`: condiciones periódicas.
* Estados: `0=S` (susceptible), `1=I` (infectado), `2=R` (recuperado). Inicia con `I0` infectados al azar; el resto susceptibles.
* **Transiciones sincrónicas por paso** (evalúa en $t$ y aplica en $t+dt$):

  * **Contagio:** si un susceptible tiene **≥1** infectado a distancia `< r`, se infecta con probabilidad
    `p_inf = 1 - exp(-beta*dt)`.
  * **Recuperación:** cada infectado pasa a recuperado con probabilidad
    `p_rec = 1 - exp(-gamma*dt)`.
* Registra en **cada paso** los conteos `S(t), I(t), R(t)`.

## 4. Visualización idéntica al layout observado (obligatorio)

* Crea una figura **de 1 fila × 2 columnas** (e.g., tamaño ~`(12,5)` pulgadas).
* **Panel izquierdo (dispersión de partículas):**

  * Dibuja un **scatter** en el rango **exacto** `x∈[0,L]`, `y∈[0,L]` con aspecto cuadrado.
  * Colores **fijos y coherentes con la imagen**: **S=azul**, **I=rojo**, **R=verde**.
  * Incluye **leyenda** con las etiquetas `S`, `I`, `R`.
  * Muestra un **HUD en el título del panel** con el formato **exacto**:

    ```bash
    t = {t:.1f} | S = {S} | I = {I} | R = {R}
    ```

* **Panel derecho (curvas SIR):**

  * Traza líneas temporales de **S (verde)**, **I (rojo)** y **R (azul)**.
  * **Título exacto:** `Evolución SIR`.
  * **Eje x etiquetado:** `Tiempo`.
  * **Eje y etiquetado:** `Número de individuos`.
  * Ajusta los límites del eje y a `[0, N_total]`.
* Mantén el **mapeo de colores consistente** entre ambos paneles.
* Guarda un PNG de estas curvas en `curves_png`.

## 5. Salida y formato del medio (obligatorio)

* Genera **exclusivamente un GIF** en la ruta `out_gif` usando `imageio.mimsave(...)`.
* **No** generes `.mp4` ni llames a escritores de video distintos de GIF.
* Crea los directorios de salida si no existen.
* Fija la **semilla global** con `numpy.random.default_rng(seed)` y úsala en todo el código.

## 6. Eficiencia mínima (decisión binaria)

* **Sí** a vectorización para detección de contactos (por ejemplo, bloques con `numpy` o cuadrícula/bins).
* **No** a bucles Python $O(N^2)$ anidados para todo `N` si `N_total` es grande.
* **Sí** a evaluación sincrónica de transiciones y actualización por lotes.

## 7. Interfaz de ejecución (obligatoria)

El script debe ejecutarse exactamente con:

```bash
python sim1.py --config config.yaml
```

* `--config` es **obligatorio** y debe apuntar a `config.yaml`. Si el archivo no existe o carece de alguna clave obligatoria, el programa **termina con error** y un mensaje claro.

## 8. Entregables generados por el script (obligatorios)

1. **`images/sim1.gif`** — animación con el layout de **dos paneles** descrito, durante `steps` pasos y a `fps`.
2. **`images/sim1_curvas.png`** — figura con las curvas $S(t), I(t), R(t)$ titulada **“Evolución SIR”**, con ejes **“Tiempo”** y **“Número de individuos”**.

## 9. Formato de salida del LLM (obligatorio)

Responde **solo** con el **código completo** del archivo **`sim1.py`** dentro de **un único bloque de código**, **sin** texto adicional antes o después.
