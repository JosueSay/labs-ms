import json
import os
from typing import Any, Optional
from core.controller import SimulationController


def getRuntimeDir() -> str:
    # devuelve la carpeta runtime/ relativa al root del proyecto
    base_dir = os.path.dirname(os.path.dirname(__file__))  # src/
    runtime_dir = os.path.join(base_dir, "runtime")
    os.makedirs(runtime_dir, exist_ok=True)
    return runtime_dir


def getStatePath() -> str:
    # ruta al archivo de snapshot
    return os.path.join(getRuntimeDir(), "state.json")


def getCommandsPath() -> str:
    # ruta al archivo de comandos
    return os.path.join(getRuntimeDir(), "commands.json")


def readJson(path: str) -> dict[str, Any]:
    # lee json simple, si no existe devuelve dict vacío
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        # si está corrupto o no se puede leer, devolvemos vacío
        return {}


def writeJson(path: str, data: dict[str, Any]) -> None:
    # escribe json de forma simple
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data or {}, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def readSnapshot() -> dict[str, Any]:
    # lee el snapshot compartido
    return readJson(getStatePath())


def writeSnapshot(snapshot: dict[str, Any]) -> None:
    # escribe el snapshot compartido
    writeJson(getStatePath(), snapshot or {})


def writeSnapshotFromController(
    controller: SimulationController,
    include_series: bool = True,
    max_points: int = 500,
) -> dict[str, Any]:
    # obtiene snapshot del controller y lo guarda en disco
    if controller is None:
        snapshot = {}
    else:
        snapshot = controller.getSnapshot(include_series=include_series, max_points=max_points)
    writeSnapshot(snapshot)
    return snapshot


def readCommands() -> dict[str, Any]:
    # lee comandos compartidos
    return readJson(getCommandsPath())


def writeCommands(commands: dict[str, Any]) -> None:
    # sobrescribe comandos compartidos
    writeJson(getCommandsPath(), commands or {})


def mergeCommands(partial: dict[str, Any]) -> dict[str, Any]:
    # mezcla comandos con lo que ya existe y guarda
    current = readCommands()
    current.update(partial or {})
    writeCommands(current)
    return current


def clearCommands(keys: Optional[list] = None) -> None:
    # limpia todos o algunos comandos
    if keys is None:
        writeCommands({})
        return
    current = readCommands()
    for k in keys:
        if k in current:
            del current[k]
    writeCommands(current)
