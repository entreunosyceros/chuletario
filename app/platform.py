"""Ajustes de entorno multiplataforma (especialmente Windows)."""

import os
import sys


def configurar_entorno() -> None:
    """
    Prepara la consola y UTF-8 al arrancar.
    En Windows activa secuencias ANSI para Rich/Textual.
    """
    if sys.platform != "win32":
        return

    os.environ.setdefault("PYTHONUTF8", "1")

    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError):
                pass

    _habilitar_vt_windows()


def _habilitar_vt_windows() -> None:
    """Habilita colores ANSI en la consola clásica de Windows 10+."""
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            # ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode.value | 0x0007)
    except (AttributeError, OSError):
        pass


def es_windows() -> bool:
    return sys.platform == "win32"
