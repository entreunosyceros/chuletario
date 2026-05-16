"""Constantes de la aplicación (sin datos de comandos)."""

FILTRO_TODAS = "__todas__"

CREDITOS_URL = "https://github.com/entreunosyceros/chuletario"
CREDITOS_AUTOR = "Creado por entreunosyceros"
CREDITOS_DESCRIPCION = (
    "Chuletario es una chuleta interactiva de comandos Linux: consulta, busca, "
    "añade y edita entradas organizadas por categorías (redes, sistema, usuarios, logs…). "
    "Exporta a Markdown o PDF y ofrece una interfaz en terminal (TUI) para gestionar "
    "tu colección de comandos de administración de sistemas."
)

BINARIOS_PELIGROSOS = frozenset({
    "rm",
    "dd",
    "mkfs",
    "mkfs.ext4",
    "mkfs.xfs",
    "mkfs.btrfs",
    "fdisk",
    "parted",
    "wipefs",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "init",
    "iptables",
    "nft",
    "userdel",
    "groupdel",
    "chown",
    "chmod",
})

PATRONES_PELIGRO_EJEMPLO = (
    "rm -rf",
    "rm -r ",
    "rm -fr",
    " rm -f",
    " rm ",
    "-exec rm",
    "xargs rm",
    "dd if=",
    "dd of=",
    "> /dev/sd",
    "mkfs.",
    "wipefs",
    "fdisk ",
    "parted ",
    "iptables -f",
    "iptables -x",
    "nft flush",
    "shutdown ",
    "poweroff",
    "kill -9",
    "killall -9",
    ":(){ :|:& };:",
    "chmod 777",
    "chown -r root",
    "userdel ",
    "groupdel ",
)

ACCIONES_MENU = [
    ("B", "Buscar", "Buscar por nombre o descripción en todas las categorías"),
    ("E", "Ejecutar", "Lanzar un comando en la shell del sistema"),
    ("A", "Añadir", "Registrar un comando nuevo en una categoría"),
    ("D", "Editar", "Modificar comando, descripción o ejemplo"),
    ("X", "Eliminar", "Borrar un comando de la chuleta"),
    ("M", "Exportar Markdown", "Generar archivo .md con todos los comandos"),
    ("P", "Exportar PDF", "Generar archivo .pdf con todos los comandos"),
    ("R", "Recargar", "Volver a leer los módulos JSON desde disco"),
    ("T", "Interfaz TUI", "Abrir el modo visual en terminal"),
    ("C", "Créditos", "Información del proyecto y repositorio"),
    ("0", "Salir", "Cerrar Chuletario"),
]
