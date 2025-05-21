# external_api.py
import logging
import os
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
EXCHANGE_RATES_API_KEY = os.environ.get("EXCHANGE_RATES_API_KEY")
EXCHANGE_RATES_BASE_URL = os.environ.get("EXCHANGE_RATES_BASE_URL")


def get_exchange_rate(from_currency: str, to_currency: str = "RUB", amount: float = 1.0) -> Optional[float]:
    """
    Получает текущий курс обмена валюты с использованием внешнего API.
    # ... (остальная документация) ...
    """
    if not EXCHANGE_RATES_BASE_URL or not EXCHANGE_RATES_API_KEY:
        logger.error("EXCHANGE_RATES_BASE_URL или EXCHANGE_RATES_API_KEY не установлены в переменных окружения.")
        return None

    url = f"{EXCHANGE_RATES_BASE_URL}convert"

    params: Dict[str, Union[str, float]] = {
        "to": to_currency,
        "from": from_currency,
        "amount": amount
    }

    headers = {"apikey": EXCHANGE_RATES_API_KEY}

    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    response: Optional[requests.Response] = None  # <--- Инициализируем response здесь

    try:
        logger.debug(f"Запрос к API курсов валют: URL={url},"
                     f" Params={params}, Headers exist: {bool(headers.get('apikey'))}")
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and "result" in data and isinstance(data["result"], (int, float)):
            converted_sum = float(data["result"])
            if amount != 0:
                rate = converted_sum / amount
                logger.info(f"Получен курс для {from_currency}->{to_currency}:"
                            f" {rate:.4f} (исходная сумма {amount} {from_currency} = {converted_sum} {to_currency})")
                return rate
            elif converted_sum == 0:
                logger.info(f"Курс для {from_currency}->{to_currency} при amount=0: result=0")
                return 0.0
            else:
                logger.warning(f"Не удалось рассчитать курс: amount=0,"
                               f" но result={converted_sum} для {from_currency} в {to_currency}.")
                return None
        else:
            logger.warning(f"Не удалось получить 'result' или"
                           f" он некорректного типа в ответе API для {from_currency} в {to_currency}. Ответ: {data}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Ошибка таймаута при запросе к API: {url}")
        return None
    except requests.exceptions.HTTPError as http_err:
        error_details = (f"Код: {http_err.response.status_code}."
                         f" Ответ: {http_err.response.text[:200]}") if http_err.response else ""
        logger.error(f"HTTP ошибка при запросе к API: {http_err}. {error_details}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        return None
    except (ValueError, TypeError) as json_err:  # Ошибка декодирования JSON
        response_text_snippet = response.text[:200] if response else "нет ответа или ответ не был получен"
        logger.error(f"Ошибка декодирования JSON ответа от API: {json_err}. Ответ: {response_text_snippet}")
        return None


def convert_transaction_amount_to_rub(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction (Dict[str, Any]): Транзакция, содержащая информацию о сумме и валюте.

    Returns:
        float: Сумма транзакции в рублях, или None, если произошла ошибка конвертации
               или если сумма уже в рублях и произошла ошибка извлечения.
               Если уже в рублях и извлечение успешно - возвращает исходную сумму.
    """
    try:
        amount_str = transaction.get("operationAmount", {}).get("amount")
        currency_code = transaction.get("operationAmount", {}).get("currency", {}).get("code")

        if amount_str is None or currency_code is None:
            logger.warning(f"Отсутствуют данные о сумме или валюте в транзакции ID: {transaction.get('id', 'N/A')}")
            return None

        amount = float(str(amount_str).replace(',', '.'))  # Обработка запятой как десятичного разделителя

    except (ValueError, TypeError) as e:
        logger.warning(f"Ошибка извлечения суммы/валюты из транзакции ID: {transaction.get('id', 'N/A')}: {e}")
        return None

    if currency_code.upper() == "RUB":
        return amount

    # Для получения курса всегда запрашиваем для 1 единицы валюты
    exchange_rate = get_exchange_rate(currency_code.upper(), "RUB", 1.0)
    if exchange_rate is None:
        logger.warning(
            f"Не удалось получить курс для конвертации {currency_code} в"
            f" RUB для транзакции ID: {transaction.get('id', 'N/A')}.")
        return None

    converted_amount = amount * exchange_rate
    logger.info(
        f"Транзакция ID: {transaction.get('id', 'N/A')}:"
        f" {amount} {currency_code} -> {converted_amount:.2f} RUB (курс {exchange_rate:.4f})")
    return converted_amount
