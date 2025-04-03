import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from main import (display_exchange_rate, filter_and_display_transactions,
                  generate_card_numbers, display_transactions, main, display_transaction_descriptions)
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
        assert masked.startswith("Visa") or masked.startswith("MasterCard") or masked.startswith("Maestro")


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


def test_card_number_generator(expected_card_numbers_data):
    """Тестирование генерации номеров карт."""
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000010"]):
        generated_numbers = list(card_number_generator(int(input()), int(input())))
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
    monkeypatch.setattr('builtins.input', lambda _: currency)
    filtered_transactions = filter_and_display_transactions(test_transactions)
    assert len(filtered_transactions) == expected


def test_generate_card_numbers(capsys):
    """Тестирование generate_card_numbers."""
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000000"]):
        generate_card_numbers()
        captured = capsys.readouterr()
    assert "1000000000000000" in captured.out


def test_display_exchange_rate_integration(capsys, monkeypatch):
    """Интеграционный тест display_exchange_rate."""
    with patch('builtins.input', side_effect=["USD", "RUB"]):
        display_exchange_rate()
        captured = capsys.readouterr()
    assert "Текущий курс USD к RUB:" in captured.out
    captured_output = captured.out
    start_index = captured_output.find("Текущий курс USD к RUB:") + len("Текущий курс USD к RUB:")
    exchange_rate_str = captured_output[start_index:].strip()
    try:
        exchange_rate = float(exchange_rate_str)
        assert exchange_rate > 0
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


# Новые тесты для display_transactions
def test_display_transactions_empty(capsys):
    """Тестирование display_transactions с пустым списком транзакций."""
    display_transactions([])
    captured = capsys.readouterr()
    assert "No transactions to display." in captured.out


def test_display_transactions_invalid_date(capsys, mocker):
    """Тестирование display_transactions с некорректным форматом даты."""
    transaction = {
        "id": 1,
        "state": "EXECUTED",
        "date": "invalid-date",
        "operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}},
        "description": "Test",
        "from": "Счет 12345678901234567890",
        "to": "Счет 98765432109876543210"
    }
    mocker.patch("main.convert_transaction_amount_to_rub", return_value=100.0)

    with patch("main.logger.error") as mock_logger:
        display_transactions([transaction])
        captured = capsys.readouterr()

    assert "Дата: N/A" in captured.out
    mock_logger.assert_called_with("Invalid date format: invalid-date")


def test_display_transactions_conversion_failed(capsys, mocker):
    """Тестирование display_transactions, когда конвертация суммы не удалась."""
    transaction = {
        "id": 1,
        "state": "EXECUTED",
        "date": "2023-10-27T10:00:00Z",
        "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}},
        "description": "Test",
        "from": "Счет 12345678901234567890",
        "to": "Счет 98765432109876543210"
    }
    mocker.patch("main.convert_transaction_amount_to_rub", return_value=None)

    with patch("main.logger.warning") as mock_logger:
        display_transactions([transaction])
        captured = capsys.readouterr()

    assert "Сумма: N/A N/A" in captured.out
    mock_logger.assert_called_with(
        "Не удалось конвертировать сумму для транзакции 1. Отображается исходная сумма."
    )


def test_display_transactions_exception(capsys, mocker):
    """Тестирование display_transactions при возникновении исключения."""
    transaction = {
        "id": 1,
        # Отсутствуют обязательные ключи, чтобы вызвать исключение
    }
    with patch("main.logger.warning") as mock_logger:
        display_transactions([transaction])
        captured = capsys.readouterr()

    assert "Skipping transaction with missing keys" in captured.out
    mock_logger.assert_called_with(f"Skipping transaction with missing keys: {transaction}")


def test_display_transactions_exception_error(capsys, mocker):
    """Тестирование display_transactions при возникновении исключения с logger.error."""
    transaction = {
        "id": 1,
        "state": "EXECUTED",
        "date": "2023-10-27T10:00:00Z",
        "operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}},
        "description": "Test",
        "from": "Счет 12345678901234567890",
        "to": "Счет 98765432109876543210"
    }
    mocker.patch(
        "main.convert_transaction_amount_to_rub",
        side_effect=ValueError("Mocked exception for testing")
    )
    with patch("main.logger.error") as mock_logger:
        display_transactions([transaction])
        captured = capsys.readouterr()

    assert "Error processing transaction" in captured.out
    mock_logger.assert_called()


# Тест для display_transaction_descriptions
def test_display_transaction_descriptions(capsys):
    """Тестирование display_transaction_descriptions."""
    transactions = [
        {"description": "Test transaction", "date": "2023-10-27T10:00:00Z"},
        {"description": "", "date": "2023-10-27T10:00:00Z"}
    ]
    display_transaction_descriptions(transactions)
    captured = capsys.readouterr()
    assert "Test transaction" in captured.out
    assert "No description" in captured.out


# Новые тесты для main
def test_main_invalid_choice(mocker, capsys):
    """Тестирование main с неверным выбором в меню."""
    mocker.patch("main.read_transactions", return_value=[])
    mocker.patch("builtins.input", side_effect=["invalid_file_path", "invalid", "6"])

    with patch("main.logger.warning") as mock_logger:
        main()
        captured = capsys.readouterr()

    assert "Неверный выбор. Пожалуйста, выберите снова." in captured.out
    mock_logger.assert_any_call("Invalid choice selected: invalid")


def test_main_empty_transactions(mocker, capsys):
    """Тестирование main с пустым списком транзакций."""
    mocker.patch("main.read_transactions", return_value=[])
    mocker.patch("builtins.input", side_effect=["file_path", "1", "6"])

    main()
    captured = capsys.readouterr()
    assert "No transactions to display." in captured.out


def test_main_display_transaction_descriptions(mocker, capsys):
    """Тестирование main с опцией 4 (вывод описаний транзакций)."""
    transactions = [
        {"description": "Test transaction", "date": "2023-10-27T10:00:00Z"},
        {"description": "", "date": "2023-10-27T10:00:00Z"}
    ]
    mocker.patch("main.read_transactions", return_value=transactions)
    mocker.patch("builtins.input", side_effect=["file_path", "4", "6"])

    main()
    captured = capsys.readouterr()
    print(f"Captured output: {captured.out}")
    assert "Test transaction" in captured.out
    assert "No description" in captured.out
