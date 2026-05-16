"""Acciones de la interfaz de línea de comandos (Rich)."""

import subprocess
from datetime import datetime

from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app import storage
from app.advertencias import (
    formatear_advertencias_rich,
    pedir_campos_opcionales_cli,
    tiene_advertencias,
)
from app.ayuda import abrir_creditos_en_navegador
from app.catalog import hint_categorias, hint_comandos, resolver_categoria, resolver_comando
from app.constants import CREDITOS_AUTOR, CREDITOS_DESCRIPCION, CREDITOS_URL
from app.console import console
from app.crud import (
    aplicar_edicion,
    crear_comando,
    eliminar_item,
    resolver_duplicado_al_añadir,
)
from app.items import item_coincide_busqueda


def buscar() -> None:
    termino = Prompt.ask("Buscar")
    resultados = []

    for cat, items in storage.COMANDOS.items():
        for item in items:
            if item_coincide_busqueda(item, termino):
                resultados.append((cat, item))

    if not resultados:
        console.print("[red]Sin resultados[/red]")
        return

    table = Table(title="Resultados", box=box.ROUNDED)
    table.add_column("Categoría")
    table.add_column("Comando")
    table.add_column("Descripción")
    table.add_column("Ejemplo")
    con_adv = any(tiene_advertencias(i) for _, i in resultados)
    if con_adv:
        table.add_column("Advertencias", style="red", no_wrap=False)

    for c, i in resultados:
        fila = [c, i["comando"], i["descripcion"], i["ejemplo"]]
        if con_adv:
            fila.append(formatear_advertencias_rich(i))
        table.add_row(*fila)

    console.print(table)


def ejecutar() -> None:
    cmd = Prompt.ask("Comando")
    if Prompt.ask("Ejecutar? (s/n)", default="n") != "s":
        return
    try:
        subprocess.run(cmd, shell=True, check=False)
    except OSError as e:
        console.print(f"[red]No se pudo ejecutar el comando:[/red] {e}")


def exportar_md() -> None:
    nombre = f"chuletario_{datetime.now().strftime('%Y%m%d')}.md"
    with open(nombre, "w", encoding="utf-8") as f:
        f.write("# Chuletario\n\n")
        for cat, items in storage.COMANDOS.items():
            f.write(f"## {cat}\n\n")
            for i in items:
                f.write(f"### {i['comando']}\n")
                f.write(f"- {i['descripcion']}\n")
                f.write(f"```bash\n{i['ejemplo']}\n```\n\n")
    console.print(f"[green]MD generado:[/green] {nombre}")


def exportar_pdf() -> None:
    nombre = f"chuletario_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(nombre)
    styles = getSampleStyleSheet()
    elems = [Paragraph("Chuletario", styles["Title"]), Spacer(1, 20)]

    for cat, items in storage.COMANDOS.items():
        elems.append(Paragraph(cat, styles["Heading2"]))
        for i in items:
            texto = f"""
            <b>{i['comando']}</b><br/>
            {i['descripcion']}<br/>
            {i['ejemplo']}<br/><br/>
            """
            elems.append(Paragraph(texto, styles["BodyText"]))

    doc.build(elems)
    console.print(f"[green]PDF generado:[/green] {nombre}")


def añadir() -> None:
    console.print(hint_categorias())
    cat = resolver_categoria(Prompt.ask("Categoría (nombre o número)"))
    if not cat:
        console.print("[red]Categoría no válida[/red]")
        return

    comando = Prompt.ask("Comando").strip()
    if not comando:
        console.print("[red]El comando no puede estar vacío[/red]")
        return

    descripcion = Prompt.ask("Descripción")
    ejemplo = Prompt.ask("Ejemplo")
    notas, docs, peligro = pedir_campos_opcionales_cli()

    resultado = resolver_duplicado_al_añadir(
        comando, cat, descripcion, ejemplo, notas, docs, peligro
    )

    if resultado == "none":
        crear_comando(cat, comando, descripcion, ejemplo, notas, docs, peligro)
        console.print("[green]Comando añadido[/green]")
    elif resultado == "replaced":
        console.print("[green]Comando existente eliminado y nuevo guardado[/green]")


def editar() -> None:
    console.print(hint_categorias())
    cat = resolver_categoria(Prompt.ask("Categoría (nombre o número)"))
    if not cat:
        console.print("[red]Categoría no válida[/red]")
        return

    console.print()
    console.print(hint_comandos(cat))

    item = resolver_comando(cat, Prompt.ask("Comando a editar (nombre o número)"))
    if not item:
        console.print("[red]Comando no encontrado[/red]")
        return

    notas, docs, peligro = pedir_campos_opcionales_cli(item)
    ok, msg = aplicar_edicion(
        cat,
        item,
        Prompt.ask("Comando", default=item["comando"]),
        Prompt.ask("Descripción", default=item["descripcion"]),
        Prompt.ask("Ejemplo", default=item["ejemplo"]),
        notas=notas,
        docs=docs,
        peligro=peligro,
    )
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


def eliminar() -> None:
    console.print(hint_categorias())
    cat = resolver_categoria(Prompt.ask("Categoría (nombre o número)"))
    if not cat:
        console.print("[red]Categoría no válida[/red]")
        return

    console.print()
    console.print(hint_comandos(cat))

    item = resolver_comando(cat, Prompt.ask("Comando a eliminar (nombre o número)"))
    if not item:
        console.print("[red]Comando no encontrado[/red]")
        return

    eliminar_item(cat, item)
    console.print("[green]Comando eliminado[/green]")


def mostrar_creditos() -> None:
    console.print(
        Panel(
            CREDITOS_DESCRIPCION,
            title="[bold cyan]Chuletario Pro[/bold cyan]",
            subtitle=f"[bold]{CREDITOS_AUTOR}[/bold]",
            border_style="cyan",
        )
    )
    console.print(f"\n[bold]Repositorio:[/bold] [link={CREDITOS_URL}]{CREDITOS_URL}[/link]")
    console.print("[dim]En terminales compatibles puedes hacer clic en el enlace.[/dim]\n")

    if Prompt.ask("Abrir en el navegador", choices=["s", "n"], default="s").lower() == "s":
        abrir_creditos_en_navegador()
        console.print("[green]Abriendo en el navegador…[/green]")


def mostrar(cat: str) -> None:
    items = storage.COMANDOS[cat]
    con_adv = any(tiene_advertencias(i) for i in items)

    table = Table(title=cat, box=box.DOUBLE_EDGE)
    table.add_column("Comando")
    table.add_column("Descripción")
    table.add_column("Ejemplo")
    if con_adv:
        table.add_column("Advertencias", style="red", no_wrap=False)

    for i in items:
        fila = [i["comando"], i["descripcion"], i["ejemplo"]]
        if con_adv:
            fila.append(formatear_advertencias_rich(i))
        table.add_row(*fila)

    console.print(table)
