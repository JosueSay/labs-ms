# Lab 05 – Campos de pendientes y análisis cualitativo de EDOs

Este laboratorio es sobre **campos de direcciones**, **isóclinas** y **diagramas de fase**, además de resolución analítica de EDOs y PVIs.

## Entorno

- Python 3.13.5
- Jupyter Notebook

```bash
# crear entorno y ejecutar
pip install -r requirements.txt
jupyter notebook
```

## Estructura

```bash
.
├── README.md
├── docs/                 # guía y reporte
├── images/               # figuras generadas
├── problema1_2/
├── problema3/
├── problema4/
├── problema5/
└── requirements.txt
```

## Problemas resuesltos

### Problema 1 – Campo de direcciones para $y'=f(x,y)$

Implementación en `problema1_2/p1.ipynb` de una función para graficar:

- **Campo puro:** $F(x,y)=(1,f(x,y))$
- **Campo unitario:** $\hat F=F/\|F\|$

### Problema 2 – Esbozo cualitativo + solución analítica

En `problema1_2/reporte1.md` y `reporte2.md`:

- **Técnicas:** campo de pendientes, análisis de signos y concavidad, **isóclinas** y **diagrama de fase** (autónomas), con validez por **existencia–unicidad**.
- **EDOs:**

  1. $y'=-xy$ – esbozo `p2_esb1.png` y solución `p2_edo1.png`
  2. $y'=xy$ – `p2_esb2.png`, `p2_edo2.png`
  3. $x\,dx+y\,dy=0$ ($y'=-x/y$) – `p2_esb3.png`, `p2_edo3.png`
  4. $y\,dx+x\,dy=0$ ($y'=-y/x$) – `p2_esb4.png`, `p2_edo4.png`
  5. $y'=y^2-y$ (autónoma) – **línea de fase** y solución `p2_edo5.png`

### Problema 3 – Reducción de orden y PVI

Resolver $x y''+2y'=6x$ con sustitución para llevarla a 1er orden, analizar **existencia–unicidad** por regiones y resolver PVIs dados.

### Problema 4 – PVI racional 2D

- Graficar campo de direcciones de

  $$
  y'=\frac{x-3y-3(x^2-y^2)+3xy}{2x-y+3(x^2-y^2)+2xy},\quad y(1.5)=0
  $$
- Esbozar la solución del PVI y **hallar numéricamente** puntos de equilibrio resolviendo el sistema $F(x,y)=0$.

### Problema 5 – Modelo poblacional

Análisis dimensional, equilibria, esbozo cualitativo y solución de

$$
\frac{dP}{dt}=0.0004P^2-0.06P
$$

con escenarios $P(0)=200$ y $P(0)=100$.
