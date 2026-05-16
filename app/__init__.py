"""
Chuletario — paquete de aplicación.

Los datos viven en ``modules/*.json`` (solo JSON).
La lógica Python está organizada en submódulos de ``app/``.
"""

from app.cli.menu import menu
from app.tui.app import ChuletarioTUI

__all__ = ["menu", "ChuletarioTUI"]
