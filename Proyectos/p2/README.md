# Simulador M/M/1 para restaurantes 🚦

Este proyecto implementa un sistema para simular colas M/M/1 y variantes basadas en grupos. Incluye:

- Motor de simulación por eventos discretos en Python 3.12  
- Ejecución batch desde CLI  
- Dashboard interactivo en Streamlit  
- Visualización animada en Pygame  
- Generación automática de métricas, CSV, figuras y reportes  
- Soporte para modelos clásicos y modelos basados en grupos

**Objetivo:** permitir analizar dinámicas de colas bajo distintas configuraciones y comparar resultados simulados contra la teoría.

## 🚀 Requisitos

- Python **3.12**
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

## 📦 Estructura del Proyecto

```bash
.
├── configs/         # Archivos YAML para configurar corridas
├── data/            # CSV y logs generados automáticamente
├── results/         # Gráficas y reportes generados automáticamente
├── src/             # Código fuente del sistema de simulación
├── images/          # Imágenes del reporte
├── docs/            # Reportes, teoría y documentación extendida
├── Makefile         # Comandos de ejecución rápida
└── README.md
```

📌 **Nota:**  

Las carpetas `data/` y `results/` **no existen** hasta que corres una simulación.El Makefile gestiona su creación automática.

## ⚙️ Configuración del Sistema (YAML)

Toda corrida se configura mediante archivos YAML dentro de `configs/`.

Ejemplo:

```yaml
model:
  lambda: 10
  mu: 12

simulation:
  sim_time_hours: 24
  warmup_minutes: 60
  seed: 42
```

Para conocer todos los parámetros disponibles, visita:  

- **[configs/README.md](https://github.com/JosueSay/labs-ms/blob/main/Proyectos/p2/configs/README.md)**

## 🏃 Ejecución

El proyecto incluye un Makefile que simplifica todos los modos de uso.

### 1. Simulación batch por CLI

```bash
make batch
```

Usando otro archivo YAML:

```bash
make batch CONFIG=configs/mm1_classic.yaml
```

Evitar guardar outputs:

```bash
make batch NO_OUTPUTS=1
```

### 2. Dashboard Streamlit

```bash
make dashboard
```

Accedes a un panel con sliders, visualización de métricas y control del motor.

### 3. Visualización Pygame

```bash
make pygame
```

Muestra el sistema operando con animación de llegadas, servicio y cola.

## 📊 Salidas obtenidas

### En `data/<run_id>/`

- `queue_length_series.csv`
- `queue_times.csv`
- `server_utilization.csv`
- `raw_events.csv`
- `summary_metrics.csv`
- `run.log`
- `config_effective.yaml`

### En `results/<run_id>/`

- Figuras PNG:
  - Ocupación del servidor
  - ECDF de tiempos
  - Histograma de cola
  - Evolución de la cola
  - Comparación teoría vs simulación
  - Hexbin llegada vs tiempo en sistema
- Reporte resumen (`report_resumen.md`)

El identificador `<run_id>` se genera automáticamente por fecha y hora.

## 🧠 Modelos incluidos

- **M/M/1 clásico** (`mm1_model.py`)
- **Modelo por grupos** (`mm1_group_model.py`), donde clientes pueden ser atendidos simultáneamente.

Ambos son administrados por `controller.py`, que gestiona eventos, reloj simulado y colección de métricas.

## 📒 Documentación adicional

Dentro de `docs/` encontrarás:

- `teoria.md`: fundamentos matemáticos del modelo  
- `contexto.md`: motivación del problema  
- `reporte.md` y `reporte.pdf`: reporte final completo  
