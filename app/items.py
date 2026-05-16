"""Campos opcionales de cada entrada y búsqueda por contenido."""


def aplicar_campos_opcionales(item: dict, notas, docs, peligro) -> None:
    if notas is not None:
        notas = (notas or "").strip()
        if notas:
            item["notas"] = notas
        else:
            item.pop("notas", None)
    if docs is not None:
        docs = (docs or "").strip()
        if docs:
            item["docs"] = docs
        else:
            item.pop("docs", None)
    if peligro is not None:
        if peligro:
            item["peligro"] = True
        else:
            item.pop("peligro", None)


def item_coincide_busqueda(item: dict, termino: str) -> bool:
    termino = termino.lower()
    for campo in ("comando", "descripcion", "ejemplo", "notas"):
        if termino in (item.get(campo) or "").lower():
            return True
    return False
