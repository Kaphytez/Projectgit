import os
import pytest
from unittest.mock import patch, Mock
import responses

import requests
from requests.exceptions import HTTPError
from pytest_mock import MockerFixture
import logging

from src.external_api import (
    get_exchange_rate,
    convert_transaction_amount_to_rub,
    EXCHANGE_RATES_BASE_URL
)


# Фикстуры для обработки лимитов API
@pytest.fixture
def mock_api_ratelimit(mocker: MockerFixture):
    """Фикстура для эмуляции ошибки TooManyRequests"""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("429 Too Many Requests")
    return mocker.patch('requests.get', return_value=mock_response)


@pytest.fixture
def mock_api_success(mocker: MockerFixture):
    """Фикстура для успешного ответа API"""
    mock_response = Mock()
    mock_response.json.return_value = {"result": 75.0}
    mock_response.raise_for_status.return_value = None
    return mocker.patch('requests.get', return_value=mock_response)


# Тесты для get_exchange_rate
def test_api_too_many_requests(mocker: MockerFixture, caplog):
    """Тест обработки ошибки Too Many Requests"""
    # Создаем мок ответа с кодом 429
    mock_response = mocker.Mock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "429 Too Many Requests",
        response=mock_response
    )

    # Мокируем Session.get вместо requests.get
    mock_session_get = mocker.patch("requests.Session.get", return_value=mock_response)

    with caplog.at_level(logging.ERROR):
        result = get_exchange_rate("USD")

    # Проверки
    assert result is None
    assert "429 Too Many Requests" in caplog.text
    mock_session_get.assert_called_once()


def test_api_success_response(mocker: MockerFixture):
    """Тест успешного ответа API с проверкой параметров"""
    # Мокируем session.get вместо requests.get
    mock_session_get = mocker.patch("requests.Session.get")

    # Настраиваем мок-ответ
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": 75.0}
    mock_response.raise_for_status.return_value = None
    mock_session_get.return_value = mock_response

    # Вызываем функцию
    rate = get_exchange_rate("USD", amount=100.0)

    # Проверки
    assert rate == 0.75  # 75.0 / 100.0 = 0.75
    mock_session_get.assert_called_once_with(
        f"{EXCHANGE_RATES_BASE_URL}convert",
        headers={"apikey": os.getenv("EXCHANGE_RATES_API_KEY")},
        params={"to": "RUB", "from": "USD", "amount": 100.0}
    )


def test_conversion_with_retry_logic():
    # URL API, который вызывается в external_api.py
    api_url = "https://api.apilayer.com/exchangerates_data/convert"

    # Мокируем три запроса: два с ошибкой 500, один успешный
    with responses.RequestsMock() as rsps:
        # Первые два запроса: ошибка 500
        rsps.add(
            responses.GET,
            api_url,
            status=500,
            json={"error": "Internal Server Error"}
        )
        rsps.add(
            responses.GET,
            api_url,
            status=500,
            json={"error": "Internal Server Error"}
        )
        # Третий запрос: успешный ответ
        rsps.add(
            responses.GET,
            api_url,
            status=200,
            json={"result": 75.0}
        )

        # Вызываем функцию
        result = get_exchange_rate("EUR")

        # Проверки
        assert result == 75.0
        assert len(rsps.calls) == 3


# Обновленные тесты для обработки лимитов
def test_convert_with_rate_limits(sample_processing_data, mocker, caplog, mock_env_vars):
    """Тест конвертации с превышением лимита запросов"""
    # Мокируем session.get
    mock_session_get = mocker.patch("requests.Session.get")
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("429 Too Many Requests")
    mock_session_get.return_value = mock_response

    transaction = sample_processing_data[0]  # Транзакция в USD
    with caplog.at_level(logging.WARNING):
        result = convert_transaction_amount_to_rub(transaction)
        print(f"Результат конвертации: {result}")  # Отладка
        print(f"Логи: {caplog.text}")  # Отладка

        # Проверки
        assert result is None, "Функция должна вернуть None при ошибке 429"
        assert "Не удалось получить курс для валюты USD." in caplog.text
        mock_session_get.assert_called_once()
        mock_session_get.return_value.raise_for_status.assert_called_once()


# Дополнения к существующим тестам
def test_get_exchange_rate_no_base_url(mocker: MockerFixture, caplog):
    """Тест отсутствия базового URL с проверкой логов"""
    # Мокируем EXCHANGE_RATES_BASE_URL в модуле external_api
    mocker.patch("src.external_api.EXCHANGE_RATES_BASE_URL", None)

    with caplog.at_level(logging.ERROR):
        rate = get_exchange_rate("USD")
        print(f"Rate: {rate}")  # Отладка
        print(f"Caplog text: {caplog.text}")  # Отладка

    assert rate is None
    assert "EXCHANGE_RATES_BASE_URL is not set." in caplog.text


def test_env_vars_loaded():
    """Тест загрузки переменных окружения с .env файла"""
    from dotenv import load_dotenv
    load_dotenv()

    assert os.getenv("EXCHANGE_RATES_API_KEY") is not None
    assert os.getenv("EXCHANGE_RATES_BASE_URL") is not None


# Запуск с обработкой лимитов
if __name__ == "__main__":
    pytest.main(["-s", "--tb=short", "--maxfail=1"])
