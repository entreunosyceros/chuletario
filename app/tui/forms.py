"""Modales y formularios de la interfaz Textual."""

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    Link,
    Static,
)

from app.advertencias import texto_advertencias_item
from app.ayuda import abrir_creditos_en_navegador
from app.catalog import buscar_comando_global, comandos_iguales, resolver_categoria
from app.constants import CREDITOS_AUTOR, CREDITOS_DESCRIPCION, CREDITOS_URL
from app.crud import aplicar_edicion, crear_comando, eliminar_item, reemplazar_y_crear
from app.items import aplicar_campos_opcionales

def _campos_opcionales_form(item: dict | None = None) -> ComposeResult:
    yield Label("[bold]Advertencias y documentación[/bold]")
    yield Static(
        "[dim]Notas y «peligroso» se guardan en el JSON. Si no indicas nada, "
        "se aplican avisos automáticos (igual que en la CLI).[/dim]",
    )
    yield Label("Notas / advertencias")
    yield Input(
        value=(item or {}).get("notas", ""),
        placeholder="Ej.: Requiere root. Irreversible.",
        id="notas",
    )
    yield Checkbox(
        "Marcar como peligroso",
        value=bool((item or {}).get("peligro")),
        id="peligro",
    )
    yield Label("URL documentación (opcional)")
    yield Input(value=(item or {}).get("docs", ""), placeholder="https://…", id="docs")
    yield Static("", id="preview-adv")


def _leer_campos_opcionales_form(pantalla) -> tuple[str, str, bool]:
    notas = pantalla.query_one("#notas", Input).value
    docs = pantalla.query_one("#docs", Input).value
    peligro = pantalla.query_one("#peligro", Checkbox).value
    return notas, docs, peligro


class _FormModal(ModalScreen[bool]):

    DEFAULT_CSS = """
    _FormModal {
        align: center middle;
    }
    #dialog {
        width: 80;
        height: auto;
        max-height: 92%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #dialog-scroll {
        max-height: 24;
        height: auto;
        margin-bottom: 1;
    }
    #dialog Input {
        margin-bottom: 1;
    }
    #dialog Checkbox {
        margin-bottom: 1;
    }
    #preview-adv {
        margin: 1 0;
        min-height: 2;
    }
    #dialog-actions Button {
        width: 1fr;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with ScrollableContainer(id="dialog-scroll"):
                yield from self.form_fields()
            with Vertical(id="dialog-actions"):
                yield Button("Guardar", variant="primary", id="guardar")
                yield Button("Cancelar", id="cancelar")

    def form_fields(self) -> ComposeResult:
        raise NotImplementedError

    def on_mount(self) -> None:
        self._actualizar_preview_advertencias()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in ("comando", "ejemplo", "notas"):
            self._actualizar_preview_advertencias()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "peligro":
            self._actualizar_preview_advertencias()

    def _actualizar_preview_advertencias(self) -> None:
        preview = self.query("#preview-adv")
        if not preview:
            return
        widget = preview.first()
        try:
            comando_w = self.query_one("#comando", Input)
            ejemplo_w = self.query_one("#ejemplo", Input)
        except Exception:
            widget.update("")
            return
        try:
            descripcion = self.query_one("#descripcion", Input).value
        except Exception:
            descripcion = ""
        borrador = {
            "comando": comando_w.value,
            "descripcion": descripcion,
            "ejemplo": ejemplo_w.value,
        }
        if not (borrador["comando"] or borrador["ejemplo"] or borrador["descripcion"]):
            widget.update("[dim]Rellena comando o ejemplo para ver la vista previa[/dim]")
            return
        notas, _, peligro = _leer_campos_opcionales_form(self)
        aplicar_campos_opcionales(borrador, notas, None, peligro)
        texto = texto_advertencias_item(borrador)
        if texto:
            if borrador.get("peligro") or borrador.get("notas"):
                widget.update(
                    f"[dim]Vista previa (guardada):[/dim] [bold red]{texto}[/bold red]"
                )
            else:
                widget.update(
                    f"[dim]Vista previa (automática, como en CLI):[/dim] [yellow]{texto}[/yellow]"
                )
        else:
            widget.update("[dim]Sin advertencia al guardar con estos datos[/dim]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancelar":
            self.dismiss(False)
            return

        ok, msg = self.validate_and_save()
        if ok:
            self.dismiss(True)
        else:
            self.notify(msg, severity="error")

    def validate_and_save(self) -> tuple[bool, str]:
        raise NotImplementedError


class DuplicateConflictModal(ModalScreen[str]):

    DEFAULT_CSS = """
    DuplicateConflictModal {
        align: center middle;
    }
    #dialog-dup {
        width: 78;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    #dialog-dup Static {
        margin-bottom: 1;
    }
    #dialog-dup Button {
        width: 1fr;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        categoria_dest: str,
        comando: str,
        descripcion: str,
        ejemplo: str,
        categoria_exist: str,
        item_exist: dict,
        on_edit_done=None,
        notas: str = "",
        docs: str = "",
        peligro: bool = False,
    ):
        super().__init__()
        self.categoria_dest = categoria_dest
        self.comando = comando
        self.descripcion = descripcion
        self.ejemplo = ejemplo
        self.notas = notas
        self.docs = docs
        self.peligro = peligro
        self.categoria_exist = categoria_exist
        self.item_exist = item_exist
        self.on_edit_done = on_edit_done

    def compose(self) -> ComposeResult:
        existente = self.item_exist["comando"]
        if comandos_iguales(self.comando, existente):
            titulo = f"El comando «{existente}» ya está en «{self.categoria_exist}»."
        else:
            titulo = (
                f"«{self.comando}» coincide con «{existente}» "
                f"(sin distinguir mayúsculas) en «{self.categoria_exist}»."
            )
        info = (
            f"{titulo}\n\n"
            f"Descripción: {self.item_exist['descripcion']}\n"
            f"Ejemplo: {self.item_exist['ejemplo']}"
        )
        with Container(id="dialog-dup"):
            yield Label("[bold]Comando duplicado[/bold]")
            yield Static(info)
            with Vertical():
                yield Button("Editar existente", variant="primary", id="editar")
                yield Button("Eliminar existente y crear nuevo", id="reemplazar")
                yield Button("Cancelar", id="cancelar")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id

        if bid == "cancelar":
            self.dismiss("cancel")
            return

        if bid == "reemplazar":
            reemplazar_y_crear(
                self.categoria_dest,
                self.comando,
                self.descripcion,
                self.ejemplo,
                self.categoria_exist,
                self.item_exist,
                self.notas,
                self.docs,
                self.peligro,
            )
            self.dismiss("replaced")
            return

        if bid == "editar":
            self.app.push_screen(
                EditModal(
                    self.categoria_exist,
                    self.item_exist,
                    borrador={
                        "comando": self.comando,
                        "descripcion": self.descripcion,
                        "ejemplo": self.ejemplo,
                        "notas": self.notas,
                        "docs": self.docs,
                        "peligro": self.peligro,
                    },
                ),
                self.on_edit_done,
            )
            self.dismiss("edited")


class AddModal(_FormModal):

    def __init__(self, on_edit_done=None):
        super().__init__()
        self.on_edit_done = on_edit_done

    def form_fields(self) -> ComposeResult:
        yield Label("[bold]Añadir comando[/bold]")
        yield Label("Categoría")
        yield Input(placeholder="Nombre o número de categoría", id="categoria")
        yield Label("Comando")
        yield Input(placeholder="Comando", id="comando")
        yield Label("Descripción")
        yield Input(placeholder="Descripción", id="descripcion")
        yield Label("Ejemplo")
        yield Input(placeholder="Ejemplo", id="ejemplo")
        yield from _campos_opcionales_form()

    def _leer_formulario(self):
        cat = resolver_categoria(self.query_one("#categoria", Input).value)
        comando = self.query_one("#comando", Input).value.strip()
        descripcion = self.query_one("#descripcion", Input).value.strip()
        ejemplo = self.query_one("#ejemplo", Input).value.strip()
        notas, docs, peligro = _leer_campos_opcionales_form(self)
        return cat, comando, descripcion, ejemplo, notas, docs, peligro

    def validate_and_save(self) -> tuple[bool, str]:
        cat, comando, descripcion, ejemplo, notas, docs, peligro = self._leer_formulario()

        if not cat:
            return False, "Categoría no válida"

        if not comando:
            return False, "El comando no puede estar vacío"

        crear_comando(cat, comando, descripcion, ejemplo, notas, docs, peligro)
        return True, "Comando añadido"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancelar":
            self.dismiss(False)
            return

        cat, comando, descripcion, ejemplo, notas, docs, peligro = self._leer_formulario()

        if not cat:
            self.notify("Categoría no válida", severity="error")
            return

        if not comando:
            self.notify("El comando no puede estar vacío", severity="error")
            return

        cat_exist, item_exist = buscar_comando_global(comando)
        if cat_exist:
            self.app.push_screen(
                DuplicateConflictModal(
                    cat,
                    comando,
                    descripcion,
                    ejemplo,
                    cat_exist,
                    item_exist,
                    on_edit_done=self.on_edit_done,
                    notas=notas,
                    docs=docs,
                    peligro=peligro,
                ),
                self._on_duplicate_resolved,
            )
            return

        crear_comando(cat, comando, descripcion, ejemplo, notas, docs, peligro)
        self.dismiss(True)

    def _on_duplicate_resolved(self, resultado: str) -> None:
        if resultado in ("replaced", "edited"):
            self.dismiss(True)
        elif resultado == "cancel":
            self.notify("Operación cancelada", severity="warning")


class EditModal(_FormModal):

    def __init__(self, categoria: str, item: dict, borrador: dict | None = None):
        self.categoria = categoria
        self.item = item
        self._form = dict(item)
        if borrador:
            for clave in ("comando", "descripcion", "ejemplo", "notas", "docs"):
                if clave in borrador:
                    self._form[clave] = borrador[clave]
            if borrador.get("peligro"):
                self._form["peligro"] = True
            elif "peligro" in borrador:
                self._form.pop("peligro", None)
        super().__init__()

    def form_fields(self) -> ComposeResult:
        yield Label(f"[bold]Editar en {self.categoria}[/bold]")
        yield Label("Comando")
        yield Input(value=self._form.get("comando", ""), id="comando")
        yield Label("Descripción")
        yield Input(value=self._form.get("descripcion", ""), id="descripcion")
        yield Label("Ejemplo")
        yield Input(value=self._form.get("ejemplo", ""), id="ejemplo")
        yield from _campos_opcionales_form(self._form)

    def validate_and_save(self) -> tuple[bool, str]:
        notas, docs, peligro = _leer_campos_opcionales_form(self)
        return aplicar_edicion(
            self.categoria,
            self.item,
            self.query_one("#comando", Input).value,
            self.query_one("#descripcion", Input).value,
            self.query_one("#ejemplo", Input).value,
            notas=notas,
            docs=docs,
            peligro=peligro,
        )


class DeleteModal(_FormModal):

    def __init__(self, categoria: str, item: dict):
        self.categoria = categoria
        self.item = item
        super().__init__()

    def form_fields(self) -> ComposeResult:
        yield Label(f"¿Eliminar [bold]{self.item['comando']}[/bold] de {self.categoria}?")

    def validate_and_save(self) -> tuple[bool, str]:
        eliminar_item(self.categoria, self.item)
        return True, "Comando eliminado"


class CreditsModal(ModalScreen[None]):

    DEFAULT_CSS = """
    CreditsModal {
        align: center middle;
    }
    #dialog-creditos {
        width: 80;
        height: auto;
        max-height: 90%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #dialog-creditos Static {
        margin: 1 0;
    }
    #dialog-creditos Link {
        margin: 1 0;
    }
    #dialog-creditos Button {
        width: 1fr;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog-creditos"):
            yield Label("[bold]Créditos — Chuletario[/bold]")
            yield Static(f"[bold cyan]{CREDITOS_AUTOR}[/bold cyan]")
            yield Static(CREDITOS_DESCRIPCION)
            yield Static("Repositorio:")
            yield Link(CREDITOS_URL, url=CREDITOS_URL, id="enlace-github")
            with Vertical():
                yield Button("Abrir en el navegador", variant="primary", id="abrir")
                yield Button("Cerrar", id="cerrar")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "abrir":
            abrir_creditos_en_navegador()
            self.notify("Abriendo en el navegador…", severity="information")
        elif event.button.id == "cerrar":
            self.dismiss()


