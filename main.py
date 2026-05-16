#!/usr/bin/env python3
"""
Punto de entrada de Chuletario Pro.

Datos: modules/*.json
Código: app/
"""

from app.cli.menu import menu
from app.platform import configurar_entorno

if __name__ == "__main__":
    configurar_entorno()
    menu()
