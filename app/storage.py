"""Carga y persistencia de módulos JSON (carpeta modules/ en la raíz del proyecto)."""

import json
import os

from app.console import console
from app.paths import MODULES_DIR


def cargar_modulos(directorio: str | os.PathLike | None = None) -> tuple[dict, dict]:
    """
    Carga todos los JSON y construye un mapa inverso categoría -> archivo origen.
    """
    datos: dict = {}
    origen: dict = {}

    if directorio is None:
        directorio = MODULES_DIR

    directorio = os.fspath(directorio)

    if not os.path.exists(directorio):
        return datos, origen

    for archivo in os.listdir(directorio):
        if not archivo.endswith(".json"):
            continue

        ruta = os.path.join(directorio, archivo)

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = json.load(f)

                if "_meta" in contenido:
                    contenido.pop("_meta")

                for categoria, items in contenido.items():
                    if categoria not in datos:
                        datos[categoria] = []
                    datos[categoria].extend(items)
                    origen[categoria] = ruta

        except json.JSONDecodeError:
            console.print(f"[red]JSON inválido:[/red] {archivo}")

    return datos, origen


def guardar_categoria(categoria: str, comandos: dict, origen: dict) -> None:
    """Persiste solo la categoría en su archivo JSON de origen."""
    ruta = origen.get(categoria)

    if not ruta:
        console.print("[red]No se encontró archivo de origen[/red]")
        return

    data = {categoria: comandos[categoria]}

    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]Error guardando:[/red] {e}")


# Estado global en memoria (se recarga con recargar())
COMANDOS, ORIGEN = cargar_modulos()


def recargar() -> None:
    global COMANDOS, ORIGEN
    COMANDOS, ORIGEN = cargar_modulos()
    console.print("[green]✔ Módulos recargados[/green]")
