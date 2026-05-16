#!/usr/bin/env python3
"""
Launcher de Chuletario Pro.

- Crea el entorno virtual (.venv) si no existe
- Instala o actualiza dependencias desde requirements.txt cuando haga falta
- Ejecuta main.py con el Python del entorno virtual
"""

from __future__ import annotations

import hashlib
import os
import platform
import subprocess
import sys
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
DEPS_STAMP = VENV_DIR / ".requirements.sha256"

PAQUETES_REQUERIDOS = ("rich", "textual", "reportlab")


def informar(mensaje: str) -> None:
    """Muestra un mensaje de progreso al usuario (antes de cada paso)."""
    print(f"→ {mensaje}", flush=True)


def informar_ok(mensaje: str) -> None:
    """Muestra que un paso ha terminado correctamente."""
    print(f"  ✔ {mensaje}", flush=True)


def ejecutable_python_venv() -> Path:
    if platform.system().lower() == "windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def entorno_virtual_existe() -> bool:
    return ejecutable_python_venv().is_file()


def hash_requirements() -> str:
    return hashlib.sha256(REQUIREMENTS_FILE.read_bytes()).hexdigest()


def dependencias_satisfacen(python: Path) -> bool:
    """Comprueba que los paquetes principales se importan en el venv."""
    codigo = "import " + ", ".join(PAQUETES_REQUERIDOS)
    resultado = subprocess.run(
        [str(python), "-c", codigo],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    return resultado.returncode == 0


def requirements_instalados(python: Path) -> bool:
    if not REQUIREMENTS_FILE.is_file():
        return True
    if not DEPS_STAMP.is_file():
        return False
    if DEPS_STAMP.read_text(encoding="utf-8").strip() != hash_requirements():
        return False
    return dependencias_satisfacen(python)


def crear_entorno_virtual() -> Path:
    informar("Creando entorno virtual en la carpeta .venv (puede tardar un momento)...")
    venv.create(VENV_DIR, with_pip=True)
    python = ejecutable_python_venv()
    if not python.is_file():
        raise RuntimeError("No se pudo crear el entorno virtual.")
    informar_ok("Entorno virtual creado.")

    informar("Actualizando pip dentro del entorno virtual...")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    informar_ok("pip actualizado.")
    return python


def instalar_requirements(python: Path) -> None:
    if not REQUIREMENTS_FILE.is_file():
        print(f"[!] No se encuentra {REQUIREMENTS_FILE.name}")
        sys.exit(1)

    informar(
        f"Instalando dependencias desde {REQUIREMENTS_FILE.name} "
        f"({', '.join(PAQUETES_REQUERIDOS)})..."
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        cwd=PROJECT_ROOT,
        check=True,
    )
    informar("Guardando marcador de dependencias instaladas...")
    DEPS_STAMP.write_text(hash_requirements(), encoding="utf-8")
    informar_ok("Dependencias instaladas correctamente.")


def preparar_entorno() -> Path:
    informar("Comprobando si existe el entorno virtual (.venv)...")
    if entorno_virtual_existe():
        python = ejecutable_python_venv()
        informar_ok(f"Entorno virtual encontrado: {python}")
    else:
        informar("No se encontró .venv; se creará un entorno virtual nuevo.")
        python = crear_entorno_virtual()

    informar("Comprobando si las dependencias están instaladas en el entorno virtual...")
    if not requirements_instalados(python):
        if DEPS_STAMP.is_file():
            informar(
                "requirements.txt ha cambiado o faltan paquetes; "
                "se reinstalarán las dependencias."
            )
        else:
            informar("Aún no hay dependencias instaladas en .venv.")
        instalar_requirements(python)
    else:
        informar_ok("Dependencias ya instaladas y actualizadas (no hace falta pip install).")

    return python


def iniciar_aplicacion(python: Path) -> None:
    informar(f"Arrancando Chuletario Pro con el Python del entorno virtual...")
    informar_ok(f"Ejecutando {MAIN_SCRIPT.name}")
    print(flush=True)
    subprocess.run([str(python), str(MAIN_SCRIPT)], cwd=PROJECT_ROOT, check=True)


def principal() -> None:
    os.chdir(PROJECT_ROOT)

    print("═" * 50, flush=True)
    print("  Chuletario Pro — preparación del entorno", flush=True)
    print("═" * 50, flush=True)
    print(flush=True)

    informar("Comprobando archivos del proyecto...")
    if not MAIN_SCRIPT.is_file():
        print(f"[!] No se encuentra {MAIN_SCRIPT.name}")
        sys.exit(1)
    if not REQUIREMENTS_FILE.is_file():
        print(f"[!] No se encuentra {REQUIREMENTS_FILE.name}")
        sys.exit(1)
    informar_ok("main.py y requirements.txt encontrados.")

    try:
        python_venv = preparar_entorno()
        print(flush=True)
        iniciar_aplicacion(python_venv)
    except KeyboardInterrupt:
        print("\n→ Arranque cancelado por el usuario.", flush=True)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        if e.returncode not in (130, -2):
            print(f"\n[!] Error durante la ejecución: {e}", flush=True)
            sys.exit(1)


if __name__ == "__main__":
    principal()
