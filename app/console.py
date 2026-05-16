"""Consola Rich compartida y utilidades de pausa."""

from rich.console import Console

console = Console()


def pausa():
    console.print("\n[bold yellow]↵ Pulsa ENTER para continuar...[/bold yellow]")
    try:
        input()
    except KeyboardInterrupt:
        pass


def espera_limpia():
    pausa()
    console.clear()
