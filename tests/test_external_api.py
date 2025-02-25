import os

import pytest
from dotenv import load_dotenv
from pytest_mock import MockerFixture

from src.external_api import (convert_transaction_amount_to_rub,
                              get_exchange_rate)


def test_get_exchange_rate_api_error(mock_exchange_rate):
    """Тест обработки ошибки API."""
    print("test_get_exchange_rate_api_error called")  # Отладочный вывод
    mock_exchange_rate.side_effect = Exception("API Error")  # Мокируем выброс исключения
    print(f"mock_exchange_rate.side_effect: {mock_exchange_rate.side_effect}")  # Отладочный вывод
    print("Calling mock_exchange_rate")  # Отладочный вывод
    with pytest.raises(Exception, match="API Error"):
        mock_exchange_rate("USD", "RUB")  # Вызываем мокированную функцию!
    print("Exception was raised as expected")  # Отладочный вывод


def test_get_exchange_rate_no_base_url(mocker: MockerFixture):
    """Тест, когда не установлена переменная окружения EXCHANGE_RATES_BASE_URL."""
    print("test_get_exchange_rate_no_base_url called")  # Отладочный вывод
    original_environ = os.environ.copy()  # Сохраняем исходное состояние os.environ
    mocker.patch.dict('os.environ', {'EXCHANGE_RATES_API_KEY': 'test_key'}, clear=True)
    print(f"EXCHANGE_RATES_BASE_URL is: {os.environ.get('EXCHANGE_RATES_BASE_URL')}")  # Отладочный вывод
    print("Calling get_exchange_rate")  # Отладочный вывод
    rate = get_exchange_rate("USD", "RUB")
    print(f"rate: {rate}")  # Отладочный вывод
    assert rate is None
    os.environ.clear()  # Очищаем все переменные
    os.environ.update(original_environ)  # Восстанавливаем исходное состояние os.environ


def test_convert_transaction_amount_to_rub_rub(sample_processing_data):
    """Тест конвертации в рубли, когда валюта уже RUB."""
    transaction = sample_processing_data[2]  # Транзакция в рублях
    rub_amount = convert_transaction_amount_to_rub(transaction)
    assert rub_amount == float(transaction["operationAmount"]["amount"])


def test_convert_transaction_amount_to_rub_usd(sample_processing_data, mock_exchange_rate):
    """Тест конвертации из USD в RUB."""
    mock_exchange_rate.return_value = 75.0
    transaction = sample_processing_data[0]  # Транзакция в USD
    rub_amount = convert_transaction_amount_to_rub(transaction)
    assert rub_amount == float(transaction["operationAmount"]["amount"]) * 75.0
    mock_exchange_rate.assert_called_once_with("USD")


def test_convert_transaction_amount_to_rub_exchange_rate_error(sample_processing_data, mock_exchange_rate):
    """Тест обработки ошибки получения курса обмена при конвертации."""
    mock_exchange_rate.return_value = None
    transaction = sample_processing_data[0]  # Транзакция в USD
    rub_amount = convert_transaction_amount_to_rub(transaction)
    assert rub_amount is None


def test_convert_transaction_amount_to_rub_invalid_amount(mock_exchange_rate):
    """Тест обработки неверной суммы транзакции."""
    print("test_convert_transaction_amount_to_rub_invalid_amount called")  # Отладочный вывод
    transaction = {
        "operationAmount": {
            "amount": "invalid",
            "currency": {
                "code": "USD"
            }
        }
    }
    mock_exchange_rate.return_value = 75.0
    print("Calling convert_transaction_amount_to_rub")  # Отладочный вывод
    rub_amount = convert_transaction_amount_to_rub(transaction)
    print(f"rub_amount: {rub_amount}")  # Отладочный вывод
    assert rub_amount is None


def test_env_vars_loaded():
    """Тест, проверяющий, что переменные окружения загружаются."""
    load_dotenv()
    api_key = os.environ.get("EXCHANGE_RATES_API_KEY")
    base_url = os.environ.get("EXCHANGE_RATES_BASE_URL")
    assert api_key is not None
    assert base_url is not None
