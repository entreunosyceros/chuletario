"""Menú principal de la CLI."""

from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

from app import storage
from app.cli import actions
from app.constants import ACCIONES_MENU
from app.console import console, espera_limpia, pausa
from app.tui.app import ChuletarioTUI


def mostrar_menu_principal() -> None:
    cats = list(storage.COMANDOS.keys())
    total_cmds = sum(len(storage.COMANDOS[c]) for c in cats)

    console.print(
        Panel.fit(
            "[bold cyan]CHULETARIO[/bold cyan]\n"
            "[dim]Chuleta interactiva de comandos Linux[/dim]",
            border_style="cyan",
        )
    )

    console.print()
    console.print(
        f"[bold]Categorías[/bold]  "
        f"[dim]{len(cats)} módulos · {total_cmds} comandos[/dim]"
    )
    console.print("[dim]Introduce el número para ver los comandos de esa categoría.[/dim]\n")

    tabla_cats = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    tabla_cats.add_column("Nº", style="bold green", width=5, justify="right")
    tabla_cats.add_column("Categoría")
    tabla_cats.add_column("Comandos", justify="right", style="dim")

    for i, c in enumerate(cats, 1):
        tabla_cats.add_row(str(i), c, str(len(storage.COMANDOS[c])))

    console.print(tabla_cats)
    console.print(Rule("Acciones", style="cyan"))
    console.print("[dim]Introduce la letra (o 0 para salir).[/dim]\n")

    tabla_acc = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    tabla_acc.add_column("Tecla", style="bold green", width=8, justify="center")
    tabla_acc.add_column("Acción", style="bold")
    tabla_acc.add_column("Descripción", style="dim")

    for tecla, nombre, desc in ACCIONES_MENU:
        etiqueta = f"[{tecla}]" if tecla != "0" else "[0]"
        tabla_acc.add_row(etiqueta, nombre, desc)

    console.print(tabla_acc)


def menu() -> None:
    while True:
        console.clear()
        mostrar_menu_principal()

        op = Prompt.ask(
            "\n[bold cyan]Tu elección[/bold cyan] "
            "[dim](número de categoría, letra de acción o 0)[/dim]"
        ).strip()

        if not op:
            continue

        op_norm = op.lower()

        if op_norm == "0":
            break
        elif op_norm == "b":
            actions.buscar()
            espera_limpia()
        elif op_norm == "e":
            actions.ejecutar()
            espera_limpia()
        elif op_norm == "m":
            actions.exportar_md()
            espera_limpia()
        elif op_norm == "p":
            actions.exportar_pdf()
            espera_limpia()
        elif op_norm == "r":
            storage.recargar()
            espera_limpia()
        elif op_norm == "a":
            actions.añadir()
            espera_limpia()
        elif op_norm == "d":
            actions.editar()
            espera_limpia()
        elif op_norm == "x":
            actions.eliminar()
            espera_limpia()
        elif op_norm == "t":
            ChuletarioTUI().run()
        elif op_norm == "j":
            actions.abrir_ejercicios()
            espera_limpia()
        elif op_norm == "c":
            actions.mostrar_creditos()
            espera_limpia()
        elif op.isdigit():
            cats = list(storage.COMANDOS.keys())
            i = int(op)
            if 1 <= i <= len(cats):
                console.clear()
                actions.mostrar(cats[i - 1])
                espera_limpia()
            else:
                console.print(
                    f"[red]Categoría {i} no existe.[/red] "
                    f"[dim]Elige un número entre 1 y {len(cats)}.[/dim]"
                )
                pausa()
        else:
            console.print(
                "[red]Opción no reconocida.[/red] "
                "[dim]Usa un número de la tabla de categorías o una tecla de acciones.[/dim]"
            )
            pausa()
