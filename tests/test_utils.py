import os

from src.utils import read_transactions


def test_read_transactions_valid_file():
    """
    Тестирует чтение корректного JSON-файла.
    """
    file_path = os.path.join("data", "operations.json")
    transactions = read_transactions(file_path)

    assert isinstance(transactions, list)
    assert len(transactions) > 0
    assert all(isinstance(transaction, dict) for transaction in transactions)


def test_read_transactions_file_not_found():
    """
    Тестирует случай, когда файл не найден.
    """
    file_path = "non_existent_file.json"
    transactions = read_transactions(file_path)
    assert transactions == []
