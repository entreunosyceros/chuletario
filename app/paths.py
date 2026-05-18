"""Rutas del proyecto (independientes del directorio de trabajo actual)."""

from pathlib import Path

# app/ -> raíz del repositorio
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
IMG_DIR = PROJECT_ROOT / "img"
SCRIPTS_DIR = PROJECT_ROOT / "Scripts"
MENU_EJERCICIOS_SH = SCRIPTS_DIR / "menu_ejercicios.sh"
