# Lab 6 — Simulación SIR con partículas y autómata celular

Implementaremos un **modelo SIR** por dos métodos: (1) partículas móviles y (2) autómata celular. Nos apoyaremos en LLMs y motores de IA generativa.

Modelo SIR (Kermack–McKendrick):
$$\frac{dS}{dt}=-\frac{\beta}{N}SI,\qquad \frac{dI}{dt}=\frac{\beta}{N}SI-\gamma I,\qquad \frac{dR}{dt}=\gamma I.$$

## Entorno

- Python 3.13.5

```bash
# instalar y ejecutar
pip install -r requirements.txt
```

## Estructura

```bash
.
├── README.md
├── docs/          # guía y reporte general
├── images/        # figuras/ejemplos
├── p1/            # simulación SIR con partículas
├── p2/            # simulación SIR con autómata celular
├── p3/            # promedio sobre N_exp ejecuciones
└── requirements.txt
```

## Problemas

### 1. Simulación SIR con partículas móviles en $[0,L]\times[0,L]$ (`p1/reporte.md`)

- Parámetros: $L,\ N_{total},\ I_0,\ v_{max},\ r,\ \beta,\ \gamma,\ dt$.
- Mostrar partículas y sus **cambios de estado** (S/I/R) y graficar $S(t),I(t),R(t)$. Exportar **.gif** o **.mp4**.

### 2. Simulación SIR como autómata celular en un grid $M\times N$ (`p2/reporte.md`)

- Parámetros: $M,N,\ I_0,\ T,\ r,\ \beta,\ \gamma$.
- Visualizar el **grid** coloreado por estado y las curvas $S(t),I(t),R(t)$. Exportar **.gif** o **.mp4**.

### 3. Promedio sobre $N_{exp}$ ejecuciones y contraste teórico (`p3/reporte.md`)

- Definir $N_{exp}$, repetir la simulación y graficar el **promedio** de $S(t),I(t),R(t)$.
- Usar **semilla fija**: mismas posiciones/velocidades y casos iniciales en todas las repeticiones.

## Entregables

- Videos o GIFs incrustados/enlazados en el reporte.
- Para cada escenario: indicar **parámetros usados**, incluir **snapshots** en tiempos específicos y explicar brevemente lo observado en la dinámica promedio.

## Documentación

- Reporte general en `docs/reporte.md`.
- Detalles y resultados por problema en `p1/reporte.md`, `p2/reporte.md`, `p3/reporte.md`.
