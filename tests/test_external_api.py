import logging
import os
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses
from pytest_mock import MockerFixture
from requests.exceptions import HTTPError

from src.external_api import (EXCHANGE_RATES_BASE_URL,
                              convert_transaction_amount_to_rub,
                              get_exchange_rate)


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


def test_conversion_with_retry_logic(mock_env_vars):  # Используем фикстуру для переменных окружения
    # Получаем базовый URL из переменных окружения (может быть установлен mock_env_vars)
    # Убедитесь, что mock_env_vars устанавливает правильные значения для этого теста
    # или что ваш .env файл содержит 'https://api.apilayer.com/exchangerates_data/'
    # Для большей надежности теста, можно явно мокировать os.environ здесь, если mock_env_vars делает что-то общее

    base_url_from_env = os.getenv("EXCHANGE_RATES_BASE_URL",
                                  "https://api.apilayer.com/exchangerates_data/")  # Значение по умолчанию для теста
    api_key_from_env = os.getenv("EXCHANGE_RATES_API_KEY", "dummy_key_for_test")  # Ключ тоже нужен

    api_url_to_mock = f"{base_url_from_env}convert"

    # Используем patch.dict, чтобы быть уверенными в значениях переменных окружения для этого теста
    with patch.dict(os.environ, {"EXCHANGE_RATES_BASE_URL": base_url_from_env,
                                 "EXCHANGE_RATES_API_KEY": api_key_from_env}):
        with responses.RequestsMock() as rsps:
            # Первые два запроса: ошибка 500
            rsps.add(
                responses.GET,
                api_url_to_mock,  # Мокируем URL, который будет фактически вызван
                status=500,
                json={"error": "Internal Server Error"}
            )
            rsps.add(
                responses.GET,
                api_url_to_mock,
                status=500,
                json={"error": "Internal Server Error"}
            )
            # Третий запрос: успешный ответ
            rsps.add(
                responses.GET,
                api_url_to_mock,
                status=200,
                json={"result": 75.0}  # Пример: 1 EUR = 75 RUB
            )

            # Вызываем функцию
            result = get_exchange_rate(from_currency="EUR", to_currency="RUB", amount=1.0)

            # Проверки
            assert result == 75.0  # Если API возвращает "result" как сконвертированную сумму для amount=1.0
            assert len(rsps.calls) == 3

            # Проверяем параметры последнего (успешного) вызова
            last_call = rsps.calls[2]
            assert last_call.request.method == "GET"

            # Разбираем URL последнего запроса
            parsed_url = urlparse(last_call.request.url)
            query_params = parse_qs(parsed_url.query)  # parse_qs возвращает словарь, где значения - это списки

            assert query_params.get("from") == ["EUR"]
            assert query_params.get("to") == ["RUB"]
            assert query_params.get("amount") == ["1.0"]  # Параметры URL всегда строки
            # Проверяем наличие API ключа в заголовках
            assert last_call.request.headers.get("apikey") == api_key_from_env


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


def test_get_exchange_rate_timeout(mocker: MockerFixture, caplog):
    mock_session_get = mocker.patch("requests.Session.get", side_effect=requests.exceptions.Timeout("Время вышло"))
    with caplog.at_level(logging.ERROR):
        result = get_exchange_rate("USD")
    assert result is None
    assert "Ошибка таймаута при запросе к API" in caplog.text
    mock_session_get.assert_called_once()


def test_get_exchange_rate_json_decode_error(mocker: MockerFixture, caplog):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None  # Запрос успешен до этапа JSON
    mock_response.json.side_effect = ValueError("Невалидный JSON")
    mock_response.text = "Это не JSON"  # Для лога
    mock_session_get = mocker.patch("requests.Session.get", return_value=mock_response)

    with caplog.at_level(logging.ERROR):
        result = get_exchange_rate("USD")
    assert result is None
    assert "Ошибка декодирования JSON ответа от API" in caplog.text
    assert "Это не JSON" in caplog.text
    mock_session_get.assert_called_once()


def test_get_exchange_rate_api_bad_data_format(mocker: MockerFixture, caplog):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"error": "что-то пошло не так"}  # Нет "result"
    mock_session_get = mocker.patch("requests.Session.get", return_value=mock_response)

    with caplog.at_level(logging.WARNING):  # Логируется как WARNING
        result = get_exchange_rate("USD")
    assert result is None
    assert "Не удалось получить 'result' или он некорректного типа" in caplog.text
    mock_session_get.assert_called_once()
