import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from main import (display_exchange_rate, filter_and_display_transactions,
                  generate_card_numbers)
from src.generators import card_number_generator
from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import mask_account_card

load_dotenv()
EXCHANGE_RATES_API_KEY = os.environ.get("EXCHANGE_RATES_API_KEY")
EXCHANGE_RATES_BASE_URL = os.environ.get("EXCHANGE_RATES_BASE_URL")


def test_filter_by_state(sample_processing_data, state_params):
    """Тестирование фильтрации по состоянию."""
    filtered_data = filter_by_state(sample_processing_data, state_params)
    for item in filtered_data:
        assert item["state"] == state_params


def test_sort_by_date_asc(sample_processing_data):
    """Тестирование сортировки по дате по возрастанию."""
    sorted_data = sort_by_date(sample_processing_data, ascending=True)
    dates = [item["date"] for item in sorted_data]
    assert dates == sorted(dates)


def test_sort_by_date_desc(sample_processing_data):
    """Тестирование сортировки по дате по убыванию."""
    sorted_data = sort_by_date(sample_processing_data, ascending=False)
    dates = [item["date"] for item in sorted_data]
    assert dates == sorted(dates, reverse=True)


def test_mask_account_card(account_card_params):
    """Тестирование маскировки номера карты или счета."""
    masked = mask_account_card(account_card_params)
    if "Счет" in account_card_params:
        assert masked.startswith("Счет **")
    else:
        assert masked.startswith("Visa") or masked.startswith("MasterCard") or masked.startswith("Maestro")  # исправил


def test_get_mask_account(mask_account_params):
    """Тестирование маскировки номера счета."""
    masked = get_mask_account(mask_account_params)
    if len(mask_account_params) == 20:
        assert masked == f"**{mask_account_params[-4:]}"
    else:
        assert masked == "Invalid account number: Account number must be exactly 20 digits"


def test_get_mask_card_number(mask_card_params):
    """Тестирование маскировки номера карты."""
    masked = get_mask_card_number(mask_card_params)
    if len(mask_card_params) == 16:
        assert masked == f"{mask_card_params[:4]} {mask_card_params[4:6]}** **** {mask_card_params[-4:]}"
    elif len(mask_card_params) <= 8:
        assert masked == mask_card_params
    else:
        assert masked == ""


def test_card_number_generator(expected_card_numbers_data):  # Remove mock_input_card_numbers
    """Тестирование генерации номеров карт."""
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000010"]):
        generated_numbers = list(card_number_generator(int(input()), int(input())))  # Get input in the test
        assert generated_numbers == expected_card_numbers_data


test_transactions = [
    {
        "id": 1,
        "date": "2023-10-27T10:00:00.000000",
        "state": "EXECUTED",
        "description": "Test transaction",
        "from": "Счет 12345678901234567890",
        "to": "Счет 98765432109876540000",
        "operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}},
    }
]


@pytest.mark.parametrize("currency, expected", [
    ("RUB", 1)
])
def test_filter_and_display_transactions(currency, expected, monkeypatch):
    # Мокаем ввод пользователя
    monkeypatch.setattr('builtins.input', lambda _: currency)

    # Вызываем функцию фильтрации и отображения транзакций
    filtered_transactions = filter_and_display_transactions(test_transactions)

    # Проверяем, что количество отфильтрованных транзакций соответствует ожидаемому
    assert len(filtered_transactions) == expected


def test_generate_card_numbers(capsys):
    """Тестирование generate_card_numbers."""
    # Мокируем ввод пользователя
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000000"]):
        generate_card_numbers()
        captured = capsys.readouterr()

    # Проверяем, что вывод содержит сгенерированные номера карт
    assert "1000000000000000" in captured.out


def display_transaction_descriptions(transactions):
    """Выводит описания транзакций."""
    for transaction in transactions:
        print(transaction.get("description", "No description"))
    print()


def test_display_exchange_rate_integration(capsys, monkeypatch):
    """Интеграционный тест display_exchange_rate."""

    with patch('builtins.input', side_effect=["USD", "RUB"]):
        display_exchange_rate()
        captured = capsys.readouterr()

    assert "Текущий курс USD к RUB:" in captured.out  # Проверяем, что вывод содержит курс

    captured_output = captured.out
    start_index = captured_output.find("Текущий курс USD к RUB:") + len("Текущий курс USD к RUB:")
    exchange_rate_str = captured_output[start_index:].strip()

    try:
        exchange_rate = float(exchange_rate_str)
        assert exchange_rate > 0  # Убедимся, что это положительное число
    except ValueError:
        pytest.fail(f"Не удалось преобразовать курс валюты в число: {exchange_rate_str}")


def test_display_exchange_rate_integration_failure(capsys):
    """Интеграционный тест display_exchange_rate при неудачном получении курса."""

    with patch('src.external_api.get_exchange_rate', return_value=None):
        with patch('builtins.input', side_effect=["", ""]):
            display_exchange_rate()
            captured = capsys.readouterr()

    expected_output = "Не удалось получить курс обмена.\n"
    assert expected_output in captured.out
