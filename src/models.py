from dataclasses import dataclass
from errors import IncorrectItemError
from constants import LANGUAGE


@dataclass(frozen=True)
class Item:
    item_id: str
    name: str
    category: str
    year: int
    author: str
    language: str


    def __post_init__(self) -> None:
        if not isinstance(self.item_id, str):
            raise IncorrectItemError(f'Некорректный ID: {self.item_id}')
        if not self.item_id.strip():
            raise IncorrectItemError(f'Некорректный ID: {self.item_id}')

        if not isinstance(self.name, str):
            raise IncorrectItemError(f'Некорректное название: {self.name}')
        if not self.name.strip():
            raise IncorrectItemError(f'Некорректное название: {self.name}')
        if any(i.isdigit() for i in self.name):
            raise IncorrectItemError(f'Некорректное название: {self.name}')

        if not isinstance(self.category, str):
            raise IncorrectItemError(f'Некорректная категория: {self.category}')
        if not self.category.strip():
            raise IncorrectItemError(f'Некорректная категория: {self.category}')
        if any(i.isdigit() for i in self.category):
            raise IncorrectItemError(f'Некорректная категория: {self.category}')

        if type(self.year) is not int:
            raise IncorrectItemError(f'Некорректный год: {self.year}')
        if 0 < self.year < 2027:
            raise IncorrectItemError(f'Некорректный год: {self.year}')

        if not isinstance(self.author, str):
            raise IncorrectItemError(f'Некорректный автор: {self.author}')
        if not self.author.strip():
            raise IncorrectItemError(f'Некорректный автор: {self.author}')
        if any(i.isdigit() for i in self.author):
            raise IncorrectItemError(f'Некорректный автор: {self.author}')

        if self.language not in LANGUAGE:
            raise IncorrectItemError(f'Некорректный язык: {self.language}')
