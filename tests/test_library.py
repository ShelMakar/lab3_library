import json

import pytest

from catalog import Catalog
from constants import VERSION_FORMAT
from errors import (
    BrokenFileError,
    IncorrectItemError,
    IncorrectVersionFormatError,
    ItemNotFoundError,
    NotUniqueIDError,
)
from models import Item
from storage import load_catalog, save_catalog

GOOD_LANG = "Russian"
BAD_LANG = "АААА"



def make_item(item_id="b1", **overrides):
    """Допустимый объект; любое поле можно переопределить."""
    data = {
        "item_id": item_id,
        "name": "Война и мир",
        "category": "роман",
        "year": 1869,
        "author": "Толстой",
        "language": GOOD_LANG,
    }
    data.update(overrides)
    return Item(**data)


def make_catalog():
    cat = Catalog()
    cat.add(make_item("b1", name="Война и мир", category="роман"))
    cat.add(make_item("b2", name="Анна Каренина", category="роман"))
    cat.add(make_item("b3", name="Капитал", category="экономика"))
    return cat


def make_old_catalog():
    cat = Catalog()
    cat.add(make_item("old1"))
    cat.add(make_item("old2"))
    return cat


def record(item_id="x", **overrides):
    """Допустимая запись для JSON-документа (обычный словарь)."""
    return make_item(item_id, **overrides).to_dict()


def bad_record(item_id="y", **changes):
    """Запись-словарь с испорченными полями (объект Item не создаётся)."""
    data = record(item_id)      # допустимая запись
    data.update(changes)        # портим уже готовый словарь
    return data


def write_doc(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")


def good_doc(*records):
    return {"format_version": VERSION_FORMAT, "items": list(records)}


def check_old_untouched(cat):
    assert [i.item_id for i in cat] == ["old1", "old2"]
    assert len(cat) == 2
    assert "x" not in cat


def test_create_valid_item():
    item = make_item()
    assert item.item_id == "b1"
    assert item.name == "Война и мир"
    assert item.category == "роман"
    assert item.year == 1869
    assert item.author == "Толстой"
    assert item.language == GOOD_LANG


def test_item_id_not_string():
    with pytest.raises(IncorrectItemError):
        make_item(item_id=123)


def test_item_id_empty():
    with pytest.raises(IncorrectItemError):
        make_item(item_id="    ")



def test_name_empty():
    with pytest.raises(IncorrectItemError):
        make_item(name="  ")


def test_category_not_string():
    with pytest.raises(IncorrectItemError):
        make_item(category=5)


def test_category_empty():
    with pytest.raises(IncorrectItemError):
        make_item(category="")


def test_category_with_digit():
    with pytest.raises(IncorrectItemError):
        make_item(category="роман1")


def test_year_not_int():
    with pytest.raises(IncorrectItemError):
        make_item(year="1869")


def test_year_bool_rejected():
    with pytest.raises(IncorrectItemError):
        make_item(year=True)


def test_year_zero():
    with pytest.raises(IncorrectItemError):
        make_item(year=0)



def test_year_too_big():
    with pytest.raises(IncorrectItemError):
        make_item(year=3000)


def test_author_empty():
    with pytest.raises(IncorrectItemError):
        make_item(author="")


def test_author_with_digit():
    with pytest.raises(IncorrectItemError):
        make_item(author="Толстой2")


def test_unknown_language():
    with pytest.raises(IncorrectItemError):
        make_item(language=BAD_LANG)


def test_item_invariants():
    with pytest.raises(IncorrectItemError):
        Item.from_dict(bad_record(name=""))


def test_add_and_get():
    cat = Catalog()
    item = make_item("b1")
    cat.add(item)
    assert cat.get("b1") is item


def test_add_duplicate_id_():
    cat = Catalog()
    cat.add(make_item("b1", name="Первая"))
    with pytest.raises(NotUniqueIDError):
        cat.add(make_item("b1", name="Вторая"))
    assert len(cat) == 1
    assert cat.get("b1").name == "Первая"


def test_get_missing_raises():
    cat = make_catalog()
    with pytest.raises(ItemNotFoundError):
        cat.get("qwerty")


def test_remove_existing():
    cat = make_catalog()
    cat.remove("b2")
    assert "b2" not in cat
    assert len(cat) == 2
    with pytest.raises(ItemNotFoundError):
        cat.get("b2")


def test_remove_missing_raises():
    cat = make_catalog()
    with pytest.raises(ItemNotFoundError):
        cat.remove("nope")
    assert len(cat) == 3


def test_remove_then_add_same_id():
    cat = make_catalog()
    cat.remove("b1")
    cat.add(make_item("b1", name="Новая"))
    assert cat.get("b1").name == "Новая"


def test_find_by_category():
    cat = make_catalog()
    result = cat.find_by_category("роман")
    assert [i.item_id for i in result] == ["b1", "b2"]


def test_find_by_category_no_match():
    cat = make_catalog()
    assert cat.find_by_category("поэзия") == []


def test_find_by_name_lower_case():
    cat = make_catalog()
    assert [i.item_id for i in cat.find_by_name("война")] == ["b1"]


def test_find_by_name_upper_case():
    cat = make_catalog()
    assert [i.item_id for i in cat.find_by_name("ВОЙНА")] == ["b1"]


def test_find_by_name_no_match():
    cat = make_catalog()
    assert cat.find_by_name("zzz") == []


def test_search_result_is_copy():
    """Изменение результата поиска не должно менять каталог."""
    cat = make_catalog()
    by_category = cat.find_by_category("роман")
    by_category.clear()
    by_name = cat.find_by_name("война")
    by_name.append("junk")

    assert len(cat) == 3
    assert len(cat.find_by_category("роман")) == 2
    assert [i.item_id for i in cat.find_by_name("война")] == ["b1"]


def test_len():
    assert len(make_catalog()) == 3
    assert len(Catalog()) == 0


def test_contains():
    cat = make_catalog()
    assert "b1" in cat
    assert "nope" not in cat


def test_iter_insertion_order():
    cat = make_catalog()
    assert [i.item_id for i in cat] == ["b1", "b2", "b3"]


def test_iter_twice_same_result():
    cat = make_catalog()
    first = [i.item_id for i in cat]
    second = [i.item_id for i in cat]
    assert first == second == ["b1", "b2", "b3"]


def test_save_has_format_version_in_root(tmp_path):
    path = tmp_path / "c.json"
    save_catalog(make_catalog(), path)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["format_version"] == VERSION_FORMAT
    assert len(document["items"]) == 3


def test_save_accepts_str_path(tmp_path):
    path = tmp_path / "c.json"
    save_catalog(make_catalog(), str(path))
    assert path.exists()


def test_save_overwrites_existing_file(tmp_path):
    path = tmp_path / "c.json"
    save_catalog(make_catalog(), path)
    save_catalog(make_old_catalog(), path)
    loaded = load_catalog(path)
    assert [i.item_id for i in loaded] == ["old1", "old2"]


def test_save_leaves_no_tmp_file(tmp_path):
    path = tmp_path / "c.json"
    save_catalog(make_catalog(), path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["c.json"]


def test_save_to_missing_folder_raises_and_leaves_nothing(tmp_path):
    path = tmp_path / "no_such_dir" / "c.json"
    with pytest.raises(OSError):
        save_catalog(make_catalog(), path)
    assert not path.exists()


def test_save_and_load_empty_catalog(tmp_path):
    path = tmp_path / "c.json"
    save_catalog(Catalog(), path)
    loaded = load_catalog(path)
    assert len(loaded) == 0


def test_loaded_catalog_works(tmp_path):
    cat = make_catalog()
    path = tmp_path / "c.json"
    save_catalog(cat, path)
    loaded = load_catalog(path)

    assert loaded is not cat
    assert loaded.get("b3").name == "Капитал"
    assert len(loaded.find_by_category("роман")) == 2
    with pytest.raises(NotUniqueIDError):
        loaded.add(make_item("b1"))


def test_load_unknown_version(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, {"format_version": 99, "items": []})
    with pytest.raises(IncorrectVersionFormatError):
        load_catalog(path)


def test_load_missing_version(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, {"items": []})
    with pytest.raises(IncorrectVersionFormatError):
        load_catalog(path)


def test_load_broken_json(tmp_path):
    path = tmp_path / "c.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(BrokenFileError):
        load_catalog(path)


def test_load_missing_items(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, {"format_version": VERSION_FORMAT})
    with pytest.raises(BrokenFileError):
        load_catalog(path)


def test_load_record_missing_fields(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, good_doc({"item_id": "y"}))
    with pytest.raises(BrokenFileError):
        load_catalog(path)


def test_load_record_with_extra_field(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, good_doc(bad_record(extra=1)))
    with pytest.raises(BrokenFileError):
        load_catalog(path)


def test_load_record_breaks_invariant(tmp_path):
    path = tmp_path / "c.json"
    write_doc(path, good_doc(bad_record(name="")))
    with pytest.raises(BrokenFileError):
        load_catalog(path)


def test_load_missing_file_not_swallowed(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_catalog(tmp_path / "no_such_file.json")


def test_old_catalog_untouched_if_new_is_broken(tmp_path):
    """Первая запись хорошая, вторая битая: 'x' не должен попасть в каталог."""
    cat = make_old_catalog()
    path = tmp_path / "c.json"
    write_doc(path, good_doc(record("x"), {"item_id": "y"}, record("z")))
    with pytest.raises(BrokenFileError):
        cat = load_catalog(path)       # присваивание не выполнится
    check_old_untouched(cat)


def test_catalog_still_works_after_failed_load(tmp_path):
    cat = make_old_catalog()
    path = tmp_path / "c.json"
    write_doc(path, good_doc({"item_id": "y"}))
    with pytest.raises(BrokenFileError):
        cat = load_catalog(path)

    assert len(cat.find_by_category("роман")) == 2
    cat.add(make_item("new"))
    assert len(cat) == 3