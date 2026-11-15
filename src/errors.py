class CatalogError(Exception):
    """Базовый класс ошибок"""

class IncorrectItemError(CatalogError):
    """Неверная сущность"""

class NotUniqueIDError(CatalogError):
    """Дубликат ID"""

class ItemNotFoundError(CatalogError):
    """Объект не найден"""

class IncorrectVersionFormatError(CatalogError):
    """Неподдерживаемая версия формата"""

class BrokenFileError(CatalogError):
    """Повреждённый файл"""