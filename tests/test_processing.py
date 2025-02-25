import pytest

from src.processing import filter_by_state, sort_by_date


def test_filter_by_state_executed(sample_processing_data):
    """Тест фильтрации по статусу EXECUTED."""
    executed_transactions = filter_by_state(sample_processing_data, "EXECUTED")
    assert len(executed_transactions) == 2
    for transaction in executed_transactions:
        assert transaction["state"] == "EXECUTED"


def test_filter_by_state_canceled(sample_processing_data):
    """Тест фильтрации по статусу CANCELED."""
    canceled_transactions = filter_by_state(sample_processing_data, "CANCELED")
    assert len(canceled_transactions) == 2
    for transaction in canceled_transactions:
        assert transaction["state"] == "CANCELED"


def test_filter_by_state_empty_list():
    """Тест фильтрации по статусу на пустом списке."""
    assert filter_by_state([], "EXECUTED") == []


def test_filter_by_state_no_matching_state(sample_processing_data):
    """Тест фильтрации по статусу, которого нет в данных."""
    filtered_transactions = filter_by_state(sample_processing_data, "NONEXISTENT")
    assert len(filtered_transactions) == 0


def test_sort_by_date_ascending(sample_processing_data):
    """Тест сортировки по дате по возрастанию."""
    sorted_transactions = sort_by_date(sample_processing_data, ascending=True)
    assert sorted_transactions[0]["date"] <= sorted_transactions[-1]["date"]
    assert sorted_transactions[0]["id"] == 939719570
    assert sorted_transactions[-1]["id"] == 41428829


def test_sort_by_date_descending(sample_processing_data):
    """Тест сортировки по дате по убыванию."""
    sorted_transactions = sort_by_date(sample_processing_data, ascending=False)
    assert sorted_transactions[0]["date"] >= sorted_transactions[-1]["date"]
    assert sorted_transactions[0]["id"] == 41428829
    assert sorted_transactions[-1]["id"] == 939719570


def test_sort_by_date_empty_list():
    """Тест сортировки по дате на пустом списке."""
    assert sort_by_date([]) == []


def test_sort_by_date_already_sorted_ascending(sample_processing_data):
    """Тест сортировки по дате, когда данные уже отсортированы по возрастанию."""
    already_sorted = sorted(sample_processing_data, key=lambda x: x["date"])
    sorted_transactions = sort_by_date(already_sorted, ascending=True)
    assert sorted_transactions == already_sorted


def test_sort_by_date_already_sorted_descending(sample_processing_data):
    """Тест сортировки по дате, когда данные уже отсортированы по убыванию."""
    already_sorted = sorted(sample_processing_data, key=lambda x: x["date"], reverse=True)
    sorted_transactions = sort_by_date(already_sorted, ascending=False)
    assert sorted_transactions == already_sorted


def test_filter_by_state_with_empty_transactions(empty_transactions):
    """Тест filter_by_state с пустым списком транзакций."""
    filtered_transactions = filter_by_state(empty_transactions, "EXECUTED")
    assert filtered_transactions == []


def test_filter_by_state_with_incomplete_transactions(incomplete_transactions):
    """Тест filter_by_state с неполными данными."""
    filtered_transactions = filter_by_state(incomplete_transactions, "EXECUTED")
    assert len(filtered_transactions) == 1
    assert filtered_transactions[0]["id"] == 1


def test_sort_by_date_with_empty_transactions(empty_transactions):
    """Тест sort_by_date с пустым списком транзакций."""
    sorted_transactions = sort_by_date(empty_transactions)
    assert sorted_transactions == []


def test_sort_by_date_with_incomplete_transactions(incomplete_transactions):
    """Тест sort_by_date с неполными данными."""
    with pytest.raises(KeyError):  # Ожидаем ошибку из-за отсутствия ключа 'date'
        sort_by_date(incomplete_transactions)
