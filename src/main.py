import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from catalog import Catalog
from errors import CatalogError, NotUniqueIDError
from models import Item
from storage import load_catalog, save_catalog

DEFAULT_FILE = "catalog.json"


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help=f"JSON-файл каталога (по умолчанию {DEFAULT_FILE})",
    )

    parser = argparse.ArgumentParser(
        prog="python -m src.main",
        description="Каталог библиотечных книг",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", parents=[common], help="добавить книгу")
    add.add_argument("--id", required=True, dest="item_id")
    add.add_argument("--name", required=True)
    add.add_argument("--category", required=True)
    add.add_argument("--year", required=True, type=int)
    add.add_argument("--author", required=True)
    add.add_argument("--language", required=True)

    get = sub.add_parser("get", parents=[common], help="получить книгу по ID")
    get.add_argument("--id", required=True, dest="item_id")

    remove = sub.add_parser("remove", parents=[common], help="удалить книгу по ID")
    remove.add_argument("--id", required=True, dest="item_id")

    by_cat = sub.add_parser(
        "find_by_category", parents=[common], help="поиск по категории"
    )
    by_cat.add_argument("--category", required=True)

    by_name = sub.add_parser(
        "find_by_name", parents=[common], help="поиск по названию (без учёта регистра)"
    )
    by_name.add_argument("--name", required=True)

    sub.add_parser("list", parents=[common], help="показать все книги")

    imp = sub.add_parser(
        "import", parents=[common], help="добавить записи из другого JSON-файла"
    )
    imp.add_argument(
        "--add_file", required=True, help="файл, из которого брать записи"
    )

    return parser


def print_items(items: Sequence[Item]) -> None:
    print(json.dumps([i.to_dict() for i in items], ensure_ascii=False, indent=2))


# Обработчики возвращают True, если каталог изменился и его нужно сохранить.
def cmd_add(catalog: Catalog, args: argparse.Namespace) -> bool:
    catalog.add(
        Item(
            args.item_id,
            args.name,
            args.category,
            args.year,
            args.author,
            args.language,
        )
    )
    print(f"Добавлено: {args.item_id}")
    return True


def cmd_get(catalog: Catalog, args: argparse.Namespace) -> bool:
    print_items([catalog.get(args.item_id)])
    return False


def cmd_remove(catalog: Catalog, args: argparse.Namespace) -> bool:
    catalog.remove(args.item_id)
    print(f"Удалено: {args.item_id}")
    return True


def cmd_find_by_category(catalog: Catalog, args: argparse.Namespace) -> bool:
    print_items(catalog.find_by_category(args.category))
    return False


def cmd_find_by_name(catalog: Catalog, args: argparse.Namespace) -> bool:
    print_items(catalog.find_by_name(args.name))
    return False


def cmd_list(catalog: Catalog, args: argparse.Namespace) -> bool:
    print_items(list(catalog))
    return False


def cmd_import(catalog: Catalog, args: argparse.Namespace) -> bool:
    new_items = list(load_catalog(Path(args.add_file)))
    duplicates = [i.item_id for i in new_items if i.item_id in catalog]
    if duplicates:
        raise NotUniqueIDError(f"ID уже есть в каталоге: {', '.join(duplicates)}")
    for item in new_items:
        catalog.add(item)
    print(f"Импортировано записей: {len(new_items)}")
    return True


HANDLERS: dict[str, Callable[[Catalog, argparse.Namespace], bool]] = {
    "add": cmd_add,
    "get": cmd_get,
    "remove": cmd_remove,
    "find_by_category": cmd_find_by_category,
    "find_by_name": cmd_find_by_name,
    "list": cmd_list,
    "import": cmd_import,
}


def open_catalog(path: Path) -> Catalog:
    """Нет файла: начинаем с пустого каталога. Файл есть: загружаем."""
    if not path.exists():
        return Catalog()
    return load_catalog(path)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.file)

    try:
        catalog = open_catalog(path)
        changed = HANDLERS[args.command](catalog, args)
        if changed:
            save_catalog(catalog, path)
    except CatalogError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Ошибка файла: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())