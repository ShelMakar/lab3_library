from collections.abc import Iterator

from errors import ItemNotFoundError, NotUniqueIDError
from models import Item


class Catalog:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def add(self, item: Item) -> None:
        if item.item_id in self._items:
            raise NotUniqueIDError(f"ID {item.item_id!r} уже есть в каталоге")
        self._items[item.item_id] = item

    def get(self, item_id: str) -> Item:
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"ID {item_id!r} не найден") from None

    def remove(self, item_id: str) -> None:
        try:
            del self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"ID {item_id!r} не найден") from None

    def find_by_category(self, category: str) -> list[Item]:
        return [item for item in self._items.values() if item.category.lower() == category.lower()]

    def find_by_name(self, query: str) -> list[Item]:
        q = query.lower()
        return [item for item in self._items.values() if q in item.name.lower()]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Item]:
        return iter(list(self._items.values()))

    def __contains__(self, item_id: str) -> bool:
        return item_id in self._items
