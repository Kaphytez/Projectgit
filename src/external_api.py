import logging
import os
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3 import Retry

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
        amount (float): Сумма для конвертации.

    Returns:
        float: Курс обмена валюты, или None, если произошла ошибка.
    """
    if not EXCHANGE_RATES_BASE_URL:
        logging.error("EXCHANGE_RATES_BASE_URL is not set.")
        return None

    url = f"{EXCHANGE_RATES_BASE_URL}convert"

    params: Dict[str, Union[str, float]] = {
        "to": to_currency,
        "from": from_currency,
        "amount": amount
    }

    headers = {"apikey": EXCHANGE_RATES_API_KEY}

    # Настройка повторных попыток
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data and "result" in data:
            return float(data["result"]) / amount
        else:
            logging.warning(f"Не удалось получить курс обмена для {from_currency} в {to_currency}.")
            return None

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if isinstance(e, requests.exceptions.HTTPError) and hasattr(e, "response"):
            error_msg = f"{e.response.status_code} {e}"
        logging.error(f"Ошибка при запросе к API: {error_msg}")
        return None


def convert_transaction_amount_to_rub(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction (Dict[str, Any]): Транзакция, содержащая информацию о сумме и валюте.

    Returns:
        float: Сумма транзакции в рублях, или None, если произошла ошибка.
    """
    try:
        amount = float(transaction["operationAmount"]["amount"])
        currency_code = transaction["operationAmount"]["currency"]["code"]
    except (KeyError, ValueError, TypeError) as e:
        logging.warning(f"Ошибка в структуре транзакции: {e}")
        return None

    if currency_code == "RUB":
        return amount

    exchange_rate = get_exchange_rate(currency_code, "RUB", 1.0)
    if exchange_rate is None:
        logging.warning(f"Не удалось получить курс для валюты {currency_code}.")
        return None

    return amount * exchange_rate
