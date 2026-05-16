"""Advertencias explícitas (JSON) e inferidas (heurística)."""

from rich.prompt import Prompt

from app.ayuda import nombre_para_man
from app.constants import BINARIOS_PELIGROSOS, FILTRO_TODAS, PATRONES_PELIGRO_EJEMPLO


def inferir_advertencia(item: dict) -> str | None:
    """Aviso automático si no hay notas/peligro explícitos en el JSON."""
    if item.get("peligro") or (item.get("notas") or "").strip():
        return None

    comando = (item.get("comando") or "").strip()
    ejemplo = (item.get("ejemplo") or "").lower()
    binario = nombre_para_man(comando).lower()

    if not comando and not ejemplo:
        return None

    if binario in BINARIOS_PELIGROSOS:
        return "Comando potencialmente destructivo o crítico"

    for patron in PATRONES_PELIGRO_EJEMPLO:
        if patron in ejemplo:
            return "Ejemplo potencialmente destructivo"

    return None


def texto_advertencias_item(item: dict) -> str:
    """Texto plano de advertencias (explícitas o inferidas)."""
    partes = []
    if item.get("peligro"):
        partes.append("⚠ PELIGROSO")
    if item.get("notas"):
        partes.append((item.get("notas") or "").strip())
    if partes:
        return " · ".join(partes)

    inferida = inferir_advertencia(item)
    if inferida:
        return f"⚠ {inferida}"
    return ""


def tiene_advertencias(item: dict) -> bool:
    return bool(texto_advertencias_item(item))


def texto_advertencias_tabla(item: dict, max_len: int = 52) -> str:
    texto = texto_advertencias_item(item)
    if not texto:
        return ""
    if len(texto) > max_len:
        return texto[: max_len - 1] + "…"
    return texto


def formatear_advertencias_rich(item: dict) -> str:
    texto = texto_advertencias_item(item)
    if not texto:
        return ""
    if item.get("peligro") or item.get("notas"):
        if item.get("peligro"):
            return f"[bold red]{texto}[/bold red]"
        return f"[red]{texto}[/red]"
    return f"[yellow]{texto}[/yellow]"


def formatear_detalle_tui(categoria: str, item: dict) -> str:
    lineas = [
        f"[bold cyan]{item['comando']}[/bold cyan]",
        f"[dim]Categoría:[/dim] {categoria}",
        "",
        "[bold]Descripción[/bold]",
        item.get("descripcion") or "[dim]—[/dim]",
        "",
        "[bold]Ejemplo[/bold]",
    ]
    ejemplo = item.get("ejemplo", "")
    lineas.append(f"[yellow]{ejemplo}[/yellow]" if ejemplo else "[dim]—[/dim]")
    adv = texto_advertencias_item(item)
    if adv:
        if item.get("peligro") or item.get("notas"):
            lineas.extend(["", "[bold red]Advertencias[/bold red]", f"[red]{adv}[/red]"])
        else:
            lineas.extend(
                ["", "[bold yellow]Advertencia (automática)[/bold yellow]", f"[yellow]{adv}[/yellow]"]
            )
    if item.get("docs"):
        lineas.extend(
            ["", "[bold]Documentación[/bold]", f"[link={item['docs']}]{item['docs']}[/link]"]
        )
    return "\n".join(lineas)


def pedir_campos_opcionales_cli(item: dict | None = None) -> tuple[str, str, bool]:
    notas_def = (item or {}).get("notas", "")
    docs_def = (item or {}).get("docs", "")
    peligro_def = "s" if (item or {}).get("peligro") else "n"
    notas = Prompt.ask("Notas / advertencias (opcional, Enter para omitir)", default=notas_def)
    docs = Prompt.ask("URL documentación (opcional)", default=docs_def)
    peligro = (
        Prompt.ask("¿Marcar como peligroso?", choices=["s", "n"], default=peligro_def).lower()
        == "s"
    )
    return notas, docs, peligro


def opciones_select_categoria(categorias: list[str]) -> list[tuple[str, str]]:
    return [("— Todas las categorías —", FILTRO_TODAS)] + [(c, c) for c in categorias]
