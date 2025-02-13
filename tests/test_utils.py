import os
import pytest
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


def test_read_transactions_empty_file(tmpdir):
    """
    Тестирует чтение пустого JSON-файла.
    """
    # Создаём пустой файл
    file_path = tmpdir.join("empty.json")
    file_path.write("")

    transactions = read_transactions(file_path)
    assert transactions == []


def test_read_transactions_invalid_json(tmpdir):
    """
    Тестирует чтение файла с некорректным JSON.
    """
    # Создаём файл с некорректным JSON
    file_path = tmpdir.join("invalid.json")
    file_path.write("{invalid_json}")

    transactions = read_transactions(file_path)
    assert transactions == []


def test_read_transactions_not_a_list(tmpdir):
    """
    Тестирует чтение файла, где JSON не является списком.
    """
    # Создаём файл с JSON, который не является списком
    file_path = tmpdir.join("not_a_list.json")
    file_path.write('{"key": "value"}')

    transactions = read_transactions(file_path)
    assert transactions == []


def test_read_transactions_file_not_found():
    """
    Тестирует случай, когда файл не найден.
    """
    file_path = "non_existent_file.json"
    transactions = read_transactions(file_path)
    assert transactions == []
