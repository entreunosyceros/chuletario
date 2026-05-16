"""Operaciones de creación, edición y eliminación de comandos."""

from rich import box
from rich.prompt import Prompt
from rich.table import Table

from app import storage
from app.catalog import buscar_comando_global, comandos_iguales
from app.console import console
from app.items import aplicar_campos_opcionales


def eliminar_item(categoria: str, item: dict) -> None:
    storage.COMANDOS[categoria] = [c for c in storage.COMANDOS[categoria] if c is not item]
    storage.guardar_categoria(categoria, storage.COMANDOS, storage.ORIGEN)


def crear_comando(
    categoria,
    comando,
    descripcion,
    ejemplo,
    notas: str = "",
    docs: str = "",
    peligro: bool = False,
) -> None:
    item = {
        "comando": comando.strip(),
        "descripcion": descripcion.strip(),
        "ejemplo": ejemplo.strip(),
    }
    aplicar_campos_opcionales(item, notas, docs, peligro)
    storage.COMANDOS[categoria].append(item)
    storage.guardar_categoria(categoria, storage.COMANDOS, storage.ORIGEN)


def reemplazar_y_crear(
    categoria_dest,
    comando,
    descripcion,
    ejemplo,
    categoria_exist,
    item_exist,
    notas: str = "",
    docs: str = "",
    peligro: bool = False,
) -> None:
    eliminar_item(categoria_exist, item_exist)
    crear_comando(categoria_dest, comando, descripcion, ejemplo, notas, docs, peligro)


def menu_duplicado_cli(comando, categoria_exist, item_exist) -> str:
    existente = item_exist["comando"]
    aviso = (
        f"«{existente}»"
        if comandos_iguales(comando, existente)
        else f"«{existente}» (como «{comando}»)"
    )
    console.print(
        f"\n[yellow]Ese comando ya está registrado como {aviso}[/yellow] "
        f"en [cyan]{categoria_exist}[/cyan]."
    )
    console.print(f"  Descripción: {item_exist['descripcion']}")
    console.print(f"  Ejemplo: {item_exist['ejemplo']}\n")
    tabla = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    tabla.add_column("Nº", style="bold green", width=4, justify="center")
    tabla.add_column("Qué hace")
    tabla.add_row("1", "Editar el comando que ya existe")
    tabla.add_row("2", "Eliminar el existente y guardar el nuevo")
    tabla.add_row("3", "Cancelar y no guardar cambios")
    console.print("\n[bold]Comando duplicado — elige una acción:[/bold]")
    console.print(tabla)
    return Prompt.ask(
        "[bold]Tu elección[/bold] [dim](1-3)[/dim]",
        choices=["1", "2", "3"],
        default="3",
    )


def aplicar_edicion(
    categoria,
    item,
    comando,
    descripcion,
    ejemplo,
    notas=None,
    docs=None,
    peligro=None,
) -> tuple[bool, str]:
    comando = comando.strip()
    descripcion = descripcion.strip()
    ejemplo = ejemplo.strip()

    if not comando:
        return False, "El comando no puede estar vacío"

    if not comandos_iguales(comando, item["comando"]):
        cat_dup, item_dup = buscar_comando_global(comando, excluir_item=item)
        if cat_dup:
            existente = item_dup["comando"]
            return False, f"El comando «{existente}» ya existe en «{cat_dup}»"

    item["comando"] = comando
    item["descripcion"] = descripcion
    item["ejemplo"] = ejemplo
    aplicar_campos_opcionales(item, notas, docs, peligro)
    storage.guardar_categoria(categoria, storage.COMANDOS, storage.ORIGEN)
    return True, "Comando actualizado"


def resolver_duplicado_al_añadir(
    comando,
    categoria_dest,
    descripcion,
    ejemplo,
    notas: str = "",
    docs: str = "",
    peligro: bool = False,
) -> str:
    """
    Si el comando ya existe, ofrece editar, reemplazar o cancelar.
    Devuelve: none | cancel | edited | replaced
    """
    cat_exist, item_exist = buscar_comando_global(comando)
    if not cat_exist:
        return "none"

    op = menu_duplicado_cli(comando, cat_exist, item_exist)

    if op == "3":
        return "cancel"

    if op == "1":
        ok, msg = aplicar_edicion(
            cat_exist,
            item_exist,
            Prompt.ask("Comando", default=comando),
            Prompt.ask("Descripción", default=descripcion or item_exist["descripcion"]),
            Prompt.ask("Ejemplo", default=ejemplo or item_exist["ejemplo"]),
            notas=notas,
            docs=docs,
            peligro=peligro,
        )
        console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")
        return "edited"

    reemplazar_y_crear(
        categoria_dest,
        comando,
        descripcion,
        ejemplo,
        cat_exist,
        item_exist,
        notas,
        docs,
        peligro,
    )
    return "replaced"
