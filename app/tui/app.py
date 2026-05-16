"""Aplicación principal Textual (TUI)."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from app import storage
from app.advertencias import (
    formatear_detalle_tui,
    opciones_select_categoria,
    tiene_advertencias,
    texto_advertencias_tabla,
)
from app.ayuda import abrir_documentacion, abrir_man
from app.catalog import categorias, resolver_comando
from app.constants import FILTRO_TODAS
from app.items import item_coincide_busqueda
from app.tui.forms import (
    AddModal,
    CreditsModal,
    DeleteModal,
    EditModal,
)

class ChuletarioTUI(App):

    DEFAULT_CSS = """
    #filtros {
        height: 3;
        margin: 0 1;
    }
    #filtros Label {
        width: auto;
        padding: 1 1 0 0;
    }
    #filtro-categoria {
        width: 1fr;
    }
    #busqueda {
        margin: 0 1;
    }
    #acciones {
        height: 3;
        margin: 0 1 1 1;
    }
    #acciones Button {
        width: 1fr;
    }
    #cuerpo {
        height: 1fr;
        margin: 0 1;
    }
    #izquierda {
        width: 2fr;
        min-width: 36;
    }
    #tabla-comandos {
        height: 1fr;
    }
    #panel-detalle {
        width: 1fr;
        min-width: 28;
        border: solid $primary;
        padding: 0 1;
    }
    #detalle-contenido {
        height: 1fr;
        overflow-y: auto;
        margin: 1 0;
    }
    #detalle-acciones {
        height: 3;
    }
    #detalle-acciones Button {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("CHULETARIO")
        with Horizontal(id="filtros"):
            yield Label("Categoría:")
            yield Select(opciones_select_categoria(categorias()), id="filtro-categoria", value=FILTRO_TODAS)
        yield Input(placeholder="Buscar por comando, descripción, ejemplo o notas…", id="busqueda")
        with Horizontal(id="acciones"):
            yield Button("Añadir")
            yield Button("Editar")
            yield Button("Eliminar")
            yield Button("Créditos")
            yield Button("Salir")
        with Horizontal(id="cuerpo"):
            with Vertical(id="izquierda"):
                yield DataTable(id="tabla-comandos", zebra_stripes=True, cursor_type="row")
            with Vertical(id="panel-detalle"):
                yield Label("[bold]Detalle del comando[/bold]")
                yield Static(
                    "Selecciona un comando en la tabla para ver el detalle.",
                    id="detalle-contenido",
                )
                with Horizontal(id="detalle-acciones"):
                    yield Button("Ver ayuda (man)", id="btn-man")
                    yield Button("Abrir docs", id="btn-docs", disabled=True)
        yield Footer()

    def on_mount(self):
        self._filas_cache: list[tuple[str, dict]] = []
        self._tabla_con_adv: bool | None = None
        self.table = self.query_one("#tabla-comandos", DataTable)
        self._configurar_columnas_tabla(con_adv=False)
        self.render_table()

    def _texto_busqueda(self) -> str:
        return self.query_one("#busqueda", Input).value.lower().strip()

    def _filtro_categoria(self) -> str:
        return self.query_one("#filtro-categoria", Select).value

    def iter_filas_visibles(self):
        cat_filtro = self._filtro_categoria()
        texto = self._texto_busqueda()
        for cat, items in storage.COMANDOS.items():
            if cat_filtro != FILTRO_TODAS and cat != cat_filtro:
                continue
            for item in items:
                if texto and not item_coincide_busqueda(item, texto):
                    continue
                yield cat, item

    def _configurar_columnas_tabla(self, con_adv: bool) -> None:
        if self._tabla_con_adv == con_adv:
            return
        self.table.clear(columns=True)
        self.table.add_column("Categoría", width=14)
        self.table.add_column("Comando", width=16)
        self.table.add_column("Descripción", width=22)
        self.table.add_column("Ejemplo", width=28)
        if con_adv:
            self.table.add_column("Advertencias", width=30)
        self._tabla_con_adv = con_adv

    def render_table(self, actualizar_detalle: bool = True):
        filas = list(self.iter_filas_visibles())
        con_adv = any(tiene_advertencias(item) for _, item in filas)
        self._configurar_columnas_tabla(con_adv)

        self._filas_cache = []
        self.table.clear()
        for cat, item in filas:
            self._filas_cache.append((cat, item))
            fila = [cat, item["comando"], item["descripcion"], item["ejemplo"]]
            if con_adv:
                fila.append(texto_advertencias_tabla(item))
            self.table.add_row(*fila)
        if actualizar_detalle:
            self.actualizar_detalle()

    def actualizar_detalle(self):
        panel = self.query_one("#detalle-contenido", Static)
        btn_docs = self.query_one("#btn-docs", Button)
        seleccion = self.fila_seleccionada()
        if not seleccion:
            panel.update("Selecciona un comando en la tabla para ver el detalle.")
            btn_docs.disabled = True
            return
        cat, item = seleccion
        panel.update(formatear_detalle_tui(cat, item))
        btn_docs.disabled = not bool((item.get("docs") or "").strip())

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "filtro-categoria":
            self.render_table()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "busqueda":
            self.render_table()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "tabla-comandos":
            self.actualizar_detalle()

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Respaldo si el cursor está en modo celda."""
        if event.data_table.id == "tabla-comandos":
            self.actualizar_detalle()

    def fila_seleccionada(self):
        if not self.table.row_count:
            return None
        if not self.table.is_valid_row_index(self.table.cursor_row):
            return None
        idx = self.table.cursor_row
        if idx < 0 or idx >= len(self._filas_cache):
            return None
        return self._filas_cache[idx]

    def tras_modal(self, guardado: bool | None) -> None:
        if guardado:
            self._refrescar_filtro_categorias()
            self.render_table()
            self.notify("Cambios guardados", severity="information")

    def _refrescar_filtro_categorias(self):
        select = self.query_one("#filtro-categoria", Select)
        valor = select.value
        opciones = opciones_select_categoria(categorias())
        valores_validos = {v for _, v in opciones}
        select.set_options(opciones)
        select.value = valor if valor in valores_validos else FILTRO_TODAS

    def on_button_pressed(self, event: Button.Pressed):

        bid = event.button.id

        if bid == "btn-man":
            seleccion = self.fila_seleccionada()
            if not seleccion:
                self.notify("Selecciona un comando en la tabla", severity="warning")
                return
            _, item = seleccion
            with self.suspend():
                ok, msg = abrir_man(item["comando"])
            self.notify(msg, severity="information" if ok else "warning")

        elif bid == "btn-docs":
            seleccion = self.fila_seleccionada()
            if not seleccion:
                self.notify("Selecciona un comando en la tabla", severity="warning")
                return
            _, item = seleccion
            ok, msg = abrir_documentacion(item.get("docs", ""))
            self.notify(msg, severity="information" if ok else "warning")

        label = event.button.label

        if label == "Salir":
            self.exit()

        elif label == "Añadir":
            self.push_screen(AddModal(on_edit_done=self.tras_modal), self.tras_modal)

        elif label == "Editar":
            seleccion = self.fila_seleccionada()
            if not seleccion:
                self.notify("Selecciona un comando en la tabla", severity="warning")
                return
            cat, item = seleccion
            self.push_screen(EditModal(cat, item), self.tras_modal)

        elif label == "Eliminar":
            seleccion = self.fila_seleccionada()
            if not seleccion:
                self.notify("Selecciona un comando en la tabla", severity="warning")
                return
            cat, item = seleccion
            self.push_screen(DeleteModal(cat, item), self.tras_modal)

        elif label == "Créditos":
            self.push_screen(CreditsModal())


