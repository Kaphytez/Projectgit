import logging
import os
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка переменных окружения
load_dotenv()
EXCHANGE_RATES_API_KEY = os.environ.get("EXCHANGE_RATES_API_KEY")
EXCHANGE_RATES_BASE_URL = os.environ.get("EXCHANGE_RATES_BASE_URL")


def get_exchange_rate(from_currency: str, to_currency: str = "RUB", amount: float = 1.0) -> Optional[float]:
    """
    Получает текущий курс обмена валюты с использованием внешнего API.

    Args:
        from_currency (str): Код валюты, курс которой нужно получить (например, "USD").
        to_currency (str): Код валюты, в которую нужно конвертировать (по умолчанию "RUB").
        amount (float): Cумма для конвертации

    Returns:
        float: Курс обмена валюты, или None, если произошла ошибка.
    """
    if not EXCHANGE_RATES_BASE_URL:
        logging.error("EXCHANGE_RATES_BASE_URL is not set.")  # Используем логирование
        return None

    url = f"{EXCHANGE_RATES_BASE_URL}convert"

    params: Dict[str, Union[str, float]] = {  # Указываем типы
        "to": to_currency,
        "from": from_currency,
        "amount": amount
    }

    headers = {
        "apikey": EXCHANGE_RATES_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Поднимает HTTPError для плохих ответов (4xx или 5xx)
        data = response.json()
        if data and "result" in data:
            return float(data["result"]) / amount  # Используем "result" и делим на amount
        else:
            logging.warning(
                f"Не удалось получить курс обмена для {from_currency} в {to_currency}. Данные от API: {data}")
            return None

    except requests.exceptions.RequestException as e:  # Обрабатываем ошибки сети
        logging.error(f"Ошибка при запросе к API: {e}")
        return None
    except (KeyError, ValueError) as e:  # Обрабатываем ошибки в структуре JSON
        logging.error(f"Ошибка при обработке ответа API: {e}")
        return None


def convert_transaction_amount_to_rub(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction (Dict[str, Any]): Транзакция, содержащая информацию о сумме и валюте.

    Returns:
        float: Сумма транзакции в рублях, или None, если произошла ошибка.
    """
    if "operationAmount" not in transaction:
        logging.warning("operationAmount отсутствует в транзакции.")
        return None

    try:
        amount = float(transaction["operationAmount"]["amount"])
        currency = transaction["operationAmount"]["currency"]["code"]
    except (ValueError, KeyError) as e:
        logging.error(f"Ошибка при получении суммы/валюты транзакции: {e}")
        return None

    if currency == "RUB":
        return amount

    # Если валюта не RUB, получаем курс обмена
    exchange_rate = get_exchange_rate(currency)
    if exchange_rate is None:
        logging.warning(f"Не удалось получить курс обмена для валюты {currency}.")
        return None

    return amount * exchange_rate
