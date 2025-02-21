from unittest.mock import patch

import pytest

from main import (display_exchange_rate, display_transaction_descriptions,
                  display_transactions, filter_and_display_transactions,
                  generate_card_numbers)
from src.generators import card_number_generator
from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import mask_account_card


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


@pytest.mark.parametrize(
    "transactions, expected_output",
    [
        (
                [
                    {
                        "id": 1,
                        "date": "2023-10-27T10:00:00.000000",
                        "state": "EXECUTED",
                        "description": "Test transaction",
                        "from": "Счет 12345678901234567890",
                        "to": "Счет 98765432109876543210",
                        "operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}},
                    }
                ],
                "ID: 1, Дата: 27.10.2023, Статус: EXECUTED\n"
                "Описание: Test transaction\n"
                "Счет **7890 -> Счет **3210\n"
                "Сумма: 100.00 RUB\n\n",
        ),
        (
                [],
                "",  # Пустой список транзакций
        ),
        (
                None,
                "",  # None в качестве входных данных
        ),
        (
                [{"id": 1, "date": "2023-10-27T10:00:00.000000", "state": "EXECUTED"}],
                "ID: 1, Дата: 27.10.2023, Статус: EXECUTED\n"
                "Описание: No description\nСчет открыт -> \nСумма: N/A N/A\n\n",  # Fixed newlines

        ),
    ],
)
def test_display_transactions(capsys, transactions, expected_output, mocker, mock_env_vars):
    """Тестирование display_transactions с разными входными данными."""
    mocker.patch('src.external_api.convert_transaction_amount_to_rub', return_value=1.0)

    if transactions is None:
        display_transactions([])  # Обработка None
    else:
        display_transactions(transactions)

    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_filter_and_display_transactions(capsys, sample_processing_data, mocker, mock_env_vars):  # Removed monkeypatch
    """Тестирование filter_and_display_transactions."""
    # Мокируем ввод пользователя
    with patch('builtins.input', return_value="RUB"):
        mocker.patch('src.external_api.convert_transaction_amount_to_rub', return_value=1.0)

        filter_and_display_transactions(sample_processing_data)
        captured = capsys.readouterr()

    # Проверяем, что вывод содержит транзакции в RUB
    assert "ID: 594226727" in captured.out
    assert "Сумма: 67314.70 RUB" in captured.out
    assert "ID: 615064591" in captured.out
    assert "Сумма: 77751.04 RUB" in captured.out


def test_generate_card_numbers(capsys):  # Removed monkeypatch
    """Тестирование generate_card_numbers."""
    # Мокируем ввод пользователя
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000000"]):
        generate_card_numbers()
        captured = capsys.readouterr()

    # Проверяем, что вывод содержит сгенерированные номера карт
    assert "1000000000000000" in captured.out


def test_display_transaction_descriptions(capsys, sample_processing_data):
    """Тестирование display_transaction_descriptions."""
    display_transaction_descriptions(sample_processing_data)
    captured = capsys.readouterr()

    # Проверяем, что вывод содержит "No description" для каждой транзакции
    assert "No description\nNo description\nNo description\nNo description" == captured.out


def test_display_exchange_rate(capsys, mocker, mock_env_vars):  # Removed monkeypatch
    """Тестирование display_exchange_rate."""
    with patch('builtins.input', side_effect=["USD", "RUB"]):
        mocker.patch('src.external_api.get_exchange_rate', return_value=75.0)

        display_exchange_rate()
        captured = capsys.readouterr()

    assert "Текущий курс USD к RUB: 75.0" in captured.out


def test_display_exchange_rate_failure(capsys, mocker, mock_env_vars):  # Removed monkeypatch
    """Тестирование display_exchange_rate при неудачном получении курса."""
    with patch('builtins.input', side_effect=["USD", "RUB"]):
        mocker.patch('src.external_api.get_exchange_rate', return_value=None)

        display_exchange_rate()
        captured = capsys.readouterr()

    assert "Не удалось получить курс обмена." in captured.out
