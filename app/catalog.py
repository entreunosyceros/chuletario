"""Consulta del catálogo: categorías, resolución de entradas y ayudas CLI."""

from app import storage


def categorias() -> list[str]:
    return list(storage.COMANDOS.keys())


def hint_categorias() -> str:
    lineas = ["[bold]Categorías disponibles[/bold] [dim](número o nombre)[/dim]:"]
    for i, c in enumerate(categorias(), 1):
        n = len(storage.COMANDOS.get(c, []))
        lineas.append(f"  [bold green]{i:>2}[/bold green]  {c}  [dim]({n} comandos)[/dim]")
    return "\n".join(lineas)


def resolver_categoria(entrada) -> str | None:
    entrada = (entrada or "").strip()
    cats = categorias()

    if entrada.isdigit():
        i = int(entrada)
        if 1 <= i <= len(cats):
            return cats[i - 1]

    if entrada in storage.COMANDOS:
        return entrada

    for c in cats:
        if c.lower() == entrada.lower():
            return c

    return None


def resolver_comando(categoria: str, entrada) -> dict | None:
    entrada = (entrada or "").strip()
    items = storage.COMANDOS.get(categoria, [])

    if entrada.isdigit():
        i = int(entrada)
        if 1 <= i <= len(items):
            return items[i - 1]

    for item in items:
        if item["comando"] == entrada:
            return item

    for item in items:
        if item["comando"].lower() == entrada.lower():
            return item

    return None


def hint_comandos(categoria: str) -> str:
    lineas = [f"[bold]Comandos en {categoria}[/bold] [dim](número o nombre)[/dim]:"]
    for i, item in enumerate(storage.COMANDOS[categoria], 1):
        lineas.append(f"  [bold green]{i:>2}[/bold green]  {item['comando']}")
    return "\n".join(lineas)


def comandos_iguales(a, b) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def buscar_comando_global(comando, excluir_item=None) -> tuple[str | None, dict | None]:
    comando = (comando or "").strip()
    if not comando:
        return None, None

    for cat, items in storage.COMANDOS.items():
        for item in items:
            if excluir_item is not None and item is excluir_item:
                continue
            if comandos_iguales(item["comando"], comando):
                return cat, item

    return None, None
