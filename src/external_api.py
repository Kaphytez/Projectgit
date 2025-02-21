import os
from typing import Any, Dict, Optional

import pytest
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
EXCHANGE_RATES_API_KEY = os.environ.get("EXCHANGE_RATES_API_KEY")
EXCHANGE_RATES_BASE_URL = os.environ.get("EXCHANGE_RATES_BASE_URL")


@pytest.mark.vcr
def test_get_exchange_rate_success():
    """Тест успешного получения курса обмена."""
    rate = get_exchange_rate("USD", "RUB")
    assert isinstance(rate, float)
    assert rate > 0
    # assert 60 < rate < 100  # Опционально: проверка диапазона


def get_exchange_rate(from_currency: str, to_currency: str = "RUB") -> Optional[float]:
    """
    Получает текущий курс обмена валюты с использованием внешнего API.

    Args:
        from_currency (str): Код валюты, курс которой нужно получить (например, "USD").
        to_currency (str): Код валюты, в которую нужно конвертировать (по умолчанию "RUB").

    Returns:
        float: Курс обмена валюты, или None, если произошла ошибка.
    """
    print(f"get_exchange_rate called with: {from_currency=}, {to_currency=}")  # Отладочный вывод
    if not EXCHANGE_RATES_BASE_URL:
        print("EXCHANGE_RATES_BASE_URL is not set")  # Отладочный вывод
        return None

    url = f"{EXCHANGE_RATES_BASE_URL}latest"  # Базовый URL

    params = {
        "symbols": to_currency,
        "base": from_currency
    }

    headers = {
        "apikey": EXCHANGE_RATES_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Exception in requests: {e}")  # Отладочный вывод
        raise  # Re-raise the exception
    except Exception as e:
        print(f"Some other exception: {e}")  # Отладочный вывод
        return None
    data = response.json()
    if data and "rates" in data and to_currency in data["rates"]:
        return float(data["rates"][to_currency])
    else:
        print(
            f"Ошибка: Не удалось получить курс обмена для {from_currency} в {to_currency}. Данные от API: {data}")
        return None


def convert_transaction_amount_to_rub(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction (Dict[str, Any]): Транзакция, содержащая информацию о сумме и валюте.

    Returns:
        float: Сумма транзакции в рублях, или None, если произошла ошибка.
    """
    print("convert_transaction_amount_to_rub called")  # Отладочный вывод
    try:
        amount = float(transaction["operationAmount"]["amount"])
    except ValueError as e:
        print(f"ValueError: {e}")  # Отладочный вывод
        return None

    currency = transaction["operationAmount"]["currency"]["code"]

    if currency == "RUB":
        return amount

    # Если валюта не RUB, получаем курс обмена
    exchange_rate = get_exchange_rate(currency)
    if exchange_rate is None:
        return None

    return amount * exchange_rate
