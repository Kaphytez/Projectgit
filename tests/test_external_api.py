import os
from unittest.mock import patch

import pytest
import vcr  # type: ignore
from dotenv import load_dotenv

from src.external_api import (convert_transaction_amount_to_rub,
                              get_exchange_rate)


@pytest.mark.vcr
def test_get_exchange_rate_success():
    """Тест успешного получения курса обмена."""
    rate = get_exchange_rate("USD", "RUB")
    assert isinstance(rate, float)
    assert rate > 0
    # assert 60 < rate < 100  # Опционально: проверка диапазона


def test_get_exchange_rate_api_error(mock_exchange_rate, mock_env_vars):
    """Тест обработки ошибки API."""
    mock_exchange_rate.side_effect = Exception("API Error")  # Мокируем выброс исключения
    with pytest.raises(Exception, match="API Error"):
        get_exchange_rate("USD", "RUB")
    mock_exchange_rate.assert_called_once_with("USD", "RUB")


def test_get_exchange_rate_no_base_url(mocker):
    """Тест, когда не установлена переменная окружения EXCHANGE_RATES_BASE_URL."""
    mocker.patch.dict('os.environ', {'EXCHANGE_RATES_API_KEY': 'test_key'}, clear=True)
    rate = get_exchange_rate("USD", "RUB")
    assert rate is None


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
    transaction = {
        "operationAmount": {
            "amount": "invalid",
            "currency": {
                "code": "USD"
            }
        }
    }
    mock_exchange_rate.return_value = 75.0
    rub_amount = convert_transaction_amount_to_rub(transaction)
    assert rub_amount is None


def test_convert_transaction_amount_to_rub_invalid_currency(mock_exchange_rate):
    """Тест обработки неверной валюты транзакции."""
    transaction = {
        "operationAmount": {
            "amount": "100",
            "currency": {
                "code": "INVALID"
            }
        }
    }
    mock_exchange_rate.return_value = 75.0
    rub_amount = convert_transaction_amount_to_rub(transaction)
    assert mock_exchange_rate.call_count == 1


def test_env_vars_loaded():
    """Тест, проверяющий, что переменные окружения загружаются."""
    load_dotenv()
    api_key = os.environ.get("EXCHANGE_RATES_API_KEY")
    base_url = os.environ.get("EXCHANGE_RATES_BASE_URL")
    assert api_key is not None
    assert base_url is not None
