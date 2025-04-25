from typing import List, Dict, Any  # Добавим импорты типов для читаемости

import pytest

# Импортируем ВСЕ функции из processing
from src.processing import (
    filter_by_state,
    sort_by_date,
    filter_by_currency,
    extract_operation_code,
    categorize_transactions,
    filter_by_description_keyword
)


# --- Тесты для filter_by_state ---

def test_filter_by_state_executed(sample_processing_data: List[Dict[str, Any]]):
    """Тест фильтрации по статусу EXECUTED."""
    executed_transactions = filter_by_state(sample_processing_data, "EXECUTED")
    assert len(executed_transactions) == 2
    for transaction in executed_transactions:
        assert transaction["state"] == "EXECUTED"


def test_filter_by_state_canceled(sample_processing_data: List[Dict[str, Any]]):
    """Тест фильтрации по статусу CANCELED."""
    canceled_transactions = filter_by_state(sample_processing_data, "CANCELED")
    assert len(canceled_transactions) == 2
    for transaction in canceled_transactions:
        assert transaction["state"] == "CANCELED"


def test_filter_by_state_empty_list(empty_transactions: List[Dict[str, Any]]):
    """Тест фильтрации по статусу на пустом списке."""
    assert filter_by_state(empty_transactions, "EXECUTED") == []


def test_filter_by_state_no_matching_state(sample_processing_data: List[Dict[str, Any]]):
    """Тест фильтрации по статусу, которого нет в данных."""
    filtered_transactions = filter_by_state(sample_processing_data, "NONEXISTENT")
    assert len(filtered_transactions) == 0


def test_filter_by_state_with_incomplete_transactions(incomplete_transactions: List[Dict[str, Any]]):
    """Тест filter_by_state с неполными данными."""
    filtered_transactions = filter_by_state(incomplete_transactions, "EXECUTED")
    assert len(filtered_transactions) == 1
    assert filtered_transactions[0]["id"] == 1


# --- Тесты для sort_by_date (оставляем существующие) ---

def test_sort_by_date_ascending(sample_processing_data: List[Dict[str, Any]]):
    """Тест сортировки по дате по возрастанию."""
    sorted_transactions = sort_by_date(sample_processing_data, ascending=True)
    # Проверяем порядок по ID, т.к. даты уникальны в фикстуре
    ids_asc = [t["id"] for t in sorted_transactions]
    assert ids_asc == [939719570, 594226727, 615064591, 41428829]


def test_sort_by_date_descending(sample_processing_data: List[Dict[str, Any]]):
    """Тест сортировки по дате по убыванию."""
    sorted_transactions = sort_by_date(sample_processing_data, ascending=False)
    ids_desc = [t["id"] for t in sorted_transactions]
    assert ids_desc == [41428829, 615064591, 594226727, 939719570]


def test_sort_by_date_empty_list(empty_transactions: List[Dict[str, Any]]):
    """Тест сортировки по дате на пустом списке."""
    assert sort_by_date(empty_transactions) == []


def test_sort_by_date_already_sorted_ascending(sample_processing_data: List[Dict[str, Any]]):
    """Тест сортировки по дате, когда данные уже отсортированы по возрастанию."""
    already_sorted = sorted(sample_processing_data, key=lambda x: x["date"])
    sorted_transactions = sort_by_date(already_sorted, ascending=True)
    assert sorted_transactions == already_sorted


def test_sort_by_date_already_sorted_descending(sample_processing_data: List[Dict[str, Any]]):
    """Тест сортировки по дате, когда данные уже отсортированы по убыванию."""
    already_sorted = sorted(sample_processing_data, key=lambda x: x["date"], reverse=True)
    sorted_transactions = sort_by_date(already_sorted, ascending=False)
    assert sorted_transactions == already_sorted


def test_sort_by_date_with_incomplete_transactions(incomplete_transactions: List[Dict[str, Any]]):
    """Тест sort_by_date с неполными данными (ожидаем ошибку)."""
    # Функция sort_by_date использует прямой доступ x["date"], что небезопасно
    with pytest.raises(KeyError):
        sort_by_date(incomplete_transactions)


# --- Новые тесты для filter_by_currency ---

def test_filter_by_currency_rub(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации по валюте RUB."""
    rub_transactions = list(filter_by_currency(transactions_with_descriptions, "RUB"))
    # ИСПРАВЛЕНО: Ожидаем 4 транзакции
    assert len(rub_transactions) == 4
    assert all(t["operationAmount"]["currency"]["code"] == "RUB" for t in rub_transactions)
    assert {t["id"] for t in rub_transactions} == {1, 2, 3, 7}


def test_filter_by_currency_usd(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации по валюте USD."""
    usd_transactions = list(filter_by_currency(transactions_with_descriptions, "USD"))
    assert len(usd_transactions) == 2
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in usd_transactions)
    assert {t["id"] for t in usd_transactions} == {4, 5}


def test_filter_by_currency_case_insensitive(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест нечувствительности к регистру кода валюты."""
    eur_transactions = list(filter_by_currency(transactions_with_descriptions, "eur"))
    assert len(eur_transactions) == 1
    assert eur_transactions[0]["id"] == 6
    assert eur_transactions[0]["operationAmount"]["currency"]["code"] == "EUR"


def test_filter_by_currency_nonexistent(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации по несуществующей валюте."""
    gbp_transactions = list(filter_by_currency(transactions_with_descriptions, "GBP"))
    assert len(gbp_transactions) == 0


def test_filter_by_currency_empty_input(empty_transactions: List[Dict[str, Any]]):
    """Тест фильтрации по валюте на пустом списке."""
    result = list(filter_by_currency(empty_transactions, "RUB"))
    assert result == []


# --- Новые тесты для extract_operation_code ---

@pytest.mark.parametrize("description, expected_code", [
    ("Перевод средств OP-1234 другу", "1234"),
    ("Покупка в супермаркете op-5678", "5678"),  # Нижний регистр
    ("Оплата OP-9999", "9999"),
    ("Просто Оплата OP-0000 с комментарием", "0000"),
    ("Кафе Вечер", None),
    ("Перевод OP-ABCD", None),  # Не цифры
    ("Перевод OP-123", None),  # Не 4 цифры
    ("Перевод OP - 1234", None),  # Пробел
    ("", None),  # Пустая строка
    (None, None)  # None вместо строки
])
def test_extract_operation_code(description: str, expected_code: str):
    """Параметризованный тест для extract_operation_code."""
    assert extract_operation_code(description) == expected_code


# --- Новые тесты для categorize_transactions ---

def test_categorize_transactions_basic(transactions_with_descriptions: List[Dict[str, Any]]):
    """Базовый тест категоризации транзакций."""
    categories = ["Перевод", "Оплата", "Супермаркет", "Кафе", "ЖКХ"]
    expected_counts = {
        "Перевод": 2,  # ID 1 ("Перевод средств"), ID 7 ("Перевод на карту")
        "Оплата": 2,  # ID 2 ("Оплата ЖКХ"), ID 4 ("Оплата интернета")
        "Супермаркет": 1,  # ID 3
        "Кафе": 1,  # ID 5
        "ЖКХ": 1  # ID 2
    }
    result = categorize_transactions(transactions_with_descriptions, categories)
    assert result == expected_counts


def test_categorize_transactions_case_insensitive(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест нечувствительности к регистру категорий."""
    categories = ["перевод", "жкх"]  # Категории в нижнем регистре
    expected_counts = {
        "перевод": 2,
        "жкх": 1
    }
    result = categorize_transactions(transactions_with_descriptions, categories)
    assert result == expected_counts


def test_categorize_transactions_no_matches(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест, когда ни одна категория не найдена."""
    categories = ["Аренда", "Зарплата"]
    expected_counts = {
        "Аренда": 0,
        "Зарплата": 0
    }
    result = categorize_transactions(transactions_with_descriptions, categories)
    assert result == expected_counts


def test_categorize_transactions_empty_transactions(empty_transactions: List[Dict[str, Any]]):
    """Тест категоризации на пустом списке транзакций."""
    categories = ["Перевод", "Оплата"]
    expected_counts = {"Перевод": 0, "Оплата": 0}
    result = categorize_transactions(empty_transactions, categories)
    assert result == expected_counts


def test_categorize_transactions_empty_categories(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест категоризации с пустым списком категорий."""
    categories: List[str] = []
    expected_counts: Dict[str, int] = {}
    result = categorize_transactions(transactions_with_descriptions, categories)
    assert result == expected_counts


def test_categorize_transactions_with_none_description(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест, что транзакция с description=None обрабатывается корректно."""
    # В фикстуре уже есть транзакция ID 6 с description=None
    categories = ["Перевод", "Оплата", "Супермаркет", "Кафе", "ЖКХ"]
    result = categorize_transactions(transactions_with_descriptions, categories)
    # Просто проверяем, что не возникло ошибки, и результат совпадает с базовым тестом
    expected_counts = {
        "Перевод": 2, "Оплата": 2, "Супермаркет": 1, "Кафе": 1, "ЖКХ": 1
    }
    assert result == expected_counts


# --- Новые тесты для filter_by_description_keyword ---

def test_filter_by_description_keyword_present(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации по ключевому слову, которое есть в описаниях."""
    keyword = "Оплата"
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    assert len(filtered_list) == 2
    assert {t["id"] for t in filtered_list} == {2, 4}


def test_filter_by_description_keyword_case_insensitive(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест нечувствительности к регистру ключевого слова."""
    keyword = "перевод"  # Ключевое слово в нижнем регистре
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    assert len(filtered_list) == 2
    assert {t["id"] for t in filtered_list} == {1, 7}


def test_filter_by_description_keyword_partial_match(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест частичного совпадения слова."""
    keyword = "средств"
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    assert len(filtered_list) == 1
    assert filtered_list[0]["id"] == 1


def test_filter_by_description_keyword_not_present(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации по слову, которого нет в описаниях."""
    keyword = "Аренда"
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    assert len(filtered_list) == 0


def test_filter_by_description_keyword_empty_keyword(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест фильтрации с пустым ключевым словом (должен вернуть все)."""
    keyword = ""
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    # Должен вернуть все транзакции, т.к. фильтрации не происходит
    assert len(filtered_list) == len(transactions_with_descriptions)


def test_filter_by_description_keyword_with_none(transactions_with_descriptions: List[Dict[str, Any]]):
    """Тест, что description=None не мешает фильтрации."""
    keyword = "Перевод"
    filtered_list = list(filter_by_description_keyword(transactions_with_descriptions, keyword))
    # ID 6 с None не должен попасть в выборку по слову "Перевод"
    assert len(filtered_list) == 2
    assert {t["id"] for t in filtered_list} == {1, 7}


def test_filter_by_description_keyword_empty_transactions(empty_transactions: List[Dict[str, Any]]):
    """Тест фильтрации по слову на пустом списке."""
    keyword = "тест"
    filtered_list = list(filter_by_description_keyword(empty_transactions, keyword))
    assert filtered_list == []
