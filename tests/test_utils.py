import csv
import json
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import parse_date, read_transactions


# Фикстуры для тестовых данных
@pytest.fixture
def valid_json_file(tmp_path):
    data = [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-01T12:00:00",
            "operationAmount": {
                "amount": 100.00,
                "currency": {
                    "name": "Доллар США",
                    "code": "USD"
                }
            },
            "description": "Test transaction",
            "from": "Счет 1234567890",
            "to": "Visa 1234"
        }
    ]
    file_path = tmp_path / "test.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return str(file_path)


@pytest.fixture
def invalid_json_file(tmp_path):
    file_path = tmp_path / "invalid.json"
    with open(file_path, 'w') as f:
        json.dump({"key": "value"}, f)
    return str(file_path)


@pytest.fixture
def valid_csv_file(tmp_path):
    file_path = tmp_path / "test.csv"
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            "id", "state", "date", "amount", "currency_code",
            "currency_name", "description", "from", "to"
        ])
        writer.writerow([
            2, "CANCELED", "2023-02-01", "200.50", "RUB",
            "Рубль", "Another test", "Visa 5678", "Счет 0987654321"
        ])
    return str(file_path)


@pytest.fixture
def csv_file_without_header(tmp_path):
    file_path = tmp_path / "no_header.csv"
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([3, "2023-03-01", "300.75"])
    return str(file_path)


@pytest.fixture
def valid_excel_file(tmp_path):
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({
        "id": [4],
        "state": ["EXECUTED"],
        "date": ["2023-04-01"],
        "amount": [400.00],
        "currency_code": ["EUR"],
        "currency_name": ["Евро"],
        "description": [""],
        "from": [""],
        "to": [""]
    })
    df.to_excel(file_path, index=False)
    return str(file_path)


# Тесты для read_transactions
def test_read_valid_json(valid_json_file):
    transactions = read_transactions(valid_json_file)
    assert len(transactions) == 1
    assert transactions[0]["id"] == 1
    assert transactions[0]["operationAmount"]["amount"] == 100.0


def test_read_invalid_json(invalid_json_file):
    with patch("src.utils.logger") as mock_logger:
        transactions = read_transactions(invalid_json_file)
        assert len(transactions) == 0
        mock_logger.error.assert_called()


def test_read_valid_csv(valid_csv_file):
    transactions = read_transactions(valid_csv_file)
    assert len(transactions) == 1
    assert transactions[0]["id"] == 2
    assert transactions[0]["state"] == "CANCELED"


def test_read_csv_without_header(csv_file_without_header):
    transactions = read_transactions(csv_file_without_header)
    assert len(transactions) == 0  # Не хватает обязательных полей


def test_read_valid_excel(valid_excel_file):
    transactions = read_transactions(valid_excel_file)
    assert len(transactions) == 1
    assert transactions[0]["id"] == 4
    assert transactions[0]["operationAmount"]["currency"]["code"] == "EUR"


def test_read_invalid_file_format(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.touch()
    with patch("src.utils.logger") as mock_logger:
        transactions = read_transactions(str(file_path))
        assert len(transactions) == 0
        mock_logger.error.assert_called_with("Неподдерживаемый тип файла: .txt")


# Тесты для _parse_date
@pytest.mark.parametrize("date_str, expected", [
    ("2023-01-01", "2023-01-01T00:00:00Z"),
    ("01.01.2023 12:30", "2023-01-01T12:30:00Z"),
    ("invalid", "invalid")
])
def test_parse_date(date_str, expected):
    with patch("src.utils.logger") as mock_logger:
        result = parse_date(date_str)
        if expected == "invalid":
            mock_logger.warning.assert_called_with(
                f"Ошибка преобразования даты '{date_str}': Невозможно распознать формат даты: '{date_str}'"
            )
        assert result == expected


# Тест обработки исключений
def test_read_nonexistent_file():
    with patch("src.utils.logger") as mock_logger:
        transactions = read_transactions("nonexistent.json")
        assert len(transactions) == 0
        mock_logger.exception.assert_called_with(
            "Ошибка при чтении файла nonexistent.json: [Errno 2] No such file or directory: 'nonexistent.json'"
        )


# Тест маппинга полей CSV
def test_csv_field_mapping(tmp_path):
    file_path = tmp_path / "mapping_test.csv"
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        # Используем названия полей из маппинга
        writer.writerow([
            "id",
            "date",
            "amount",
            "currency_code",
            "currency_name",
            "description",
            "from",
            "to"
        ])
        writer.writerow([
            5,
            "2023-05-01",
            "500.00",
            "GBP",
            "Фунт стерлингов",
            "Test",
            "Visa 1234",
            "Счет 5678"
        ])

    transactions = read_transactions(str(file_path))
    assert len(transactions) == 1
    assert transactions[0]["operationAmount"]["currency"]["code"] == "GBP"
