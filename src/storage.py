import json
import os
from pathlib import Path

from .catalog import Catalog
from .constants import VERSION_FORMAT
from .errors import (
    BrokenFileError,
    IncorrectItemError,
    IncorrectVersionFormatError,
    NotUniqueIDError,
)
from .models import Item


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    path = Path(path)
    document = {
        "format_version": VERSION_FORMAT,
        "items": [item.to_dict() for item in catalog],
    }
    text = json.dumps(document, ensure_ascii=False, indent=2)

    tmp_path = path.with_name(path.name + ".tmp")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    except OSError:
        tmp_path.unlink(missing_ok=True)
        raise


def load_catalog(path: str | Path) -> Catalog:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise BrokenFileError("Файл не является корректным JSON") from e

    if not isinstance(document, dict):
        raise BrokenFileError("Корень документа должен быть объектом")

    version = document.get("format_version")
    if version != VERSION_FORMAT:
        raise IncorrectVersionFormatError(f"Версия {version!r} не поддерживается")

    raw_items = document.get("items")
    if not isinstance(raw_items, list):
        raise BrokenFileError("Поле 'items' должно быть списком")

    catalog = Catalog()  # новый объект, чужое состояние не трогаем
    for index, raw in enumerate(raw_items):
        try:
            catalog.add(Item.from_dict(raw))
        except NotUniqueIDError as e:
            raise BrokenFileError(f"Дубликат ID в записи №{index}") from e
        except (TypeError, IncorrectItemError) as e:
            raise BrokenFileError(f"Неверная запись №{index}") from e
    return catalog