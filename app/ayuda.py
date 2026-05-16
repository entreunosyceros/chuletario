"""Ayuda externa: man, navegador y créditos."""

import shutil
import subprocess
import sys
import webbrowser

from app.constants import CREDITOS_URL
from app.platform import es_windows


def nombre_para_man(comando: str) -> str:
    partes = (comando or "").strip().split()
    return partes[0] if partes else ""


def _url_man_online(nombre: str) -> str:
    return f"https://man7.org/linux/man-pages/man1/{nombre}.1.html"


def _abrir_man_en_navegador(nombre: str) -> tuple[bool, str]:
    webbrowser.open(_url_man_online(nombre))
    return (
        True,
        f"Documentación de «{nombre}» abierta en el navegador "
        f"({_url_man_online(nombre)})",
    )


def _abrir_man_wsl(nombre: str) -> tuple[bool, str] | None:
    """Intenta man vía WSL si está instalado en Windows."""
    if not es_windows() or not shutil.which("wsl"):
        return None
    try:
        resultado = subprocess.run(["wsl", "man", nombre])
        if resultado.returncode == 0:
            return True, f"Manual de «{nombre}» cerrado (WSL)"
    except (FileNotFoundError, OSError):
        pass
    return None


def abrir_man(comando: str) -> tuple[bool, str]:
    nombre = nombre_para_man(comando)
    if not nombre:
        return False, "No hay comando para consultar"

    if es_windows():
        wsl = _abrir_man_wsl(nombre)
        if wsl:
            return wsl
        return _abrir_man_en_navegador(nombre)

    if shutil.which("man"):
        try:
            resultado = subprocess.run(["man", nombre])
            if resultado.returncode == 0:
                return True, f"Manual de «{nombre}» cerrado"
            return False, f"No se encontró página man para «{nombre}»"
        except (FileNotFoundError, OSError):
            pass

    return _abrir_man_en_navegador(nombre)


def abrir_documentacion(url: str) -> tuple[bool, str]:
    url = (url or "").strip()
    if not url:
        return False, "No hay URL de documentación"
    webbrowser.open(url)
    return True, "Abriendo documentación en el navegador…"


def abrir_creditos_en_navegador() -> None:
    webbrowser.open(CREDITOS_URL)
