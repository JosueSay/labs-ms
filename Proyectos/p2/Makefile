PYTHON ?= python

# archivo de config por defecto
CONFIG ?= configs/default.yaml

# scripts
BATCH_SCRIPT := src/cli_batch.py
STREAMLIT_APP := src/app_streamlit.py
PYGAME_APP := src/sim/pygame_app.py

# controlar si el batch guarda outputs (0 = sí guarda, 1 = --no-outputs)
NO_OUTPUTS ?= 0

BATCH_FLAGS := --config $(CONFIG)
ifeq ($(NO_OUTPUTS),1)
  BATCH_FLAGS += --no-outputs
endif

.PHONY: help batch dashboard pygame clean

help:
	@echo "Targets disponibles:"
	@echo "  make batch        # corre simulación batch (cli_batch.py) con CONFIG=$(CONFIG)"
	@echo "                    # usar NO_OUTPUTS=1 para no guardar CSV/reportes"
	@echo "  make dashboard    # levanta dashboard interactivo con streamlit"
	@echo "  make pygame       # abre ventana de simulación visual con pygame"
	@echo "  make clean        # borra carpetas data/, results/ y runtime/ (si existen)"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make batch"
	@echo "  make batch CONFIG=configs/batch.yaml"
	@echo "  make batch NO_OUTPUTS=1"
	@echo "  make dashboard"
	@echo "  make pygame"

batch:
	$(PYTHON) $(BATCH_SCRIPT) $(BATCH_FLAGS)

dashboard:
	streamlit run $(STREAMLIT_APP)

pygame:
	PYTHONPATH=src $(PYTHON) $(PYGAME_APP)

clean:
	@echo "borrando data/, results/ y runtime/ (si existen)..."
	@rm -rf data results runtime
