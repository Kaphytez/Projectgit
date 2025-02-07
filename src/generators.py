from typing import Any, Dict, Generator, List


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Генератор, который принимает список словарей с транзакциями и возвращает описание каждой операции по очереди.

    Args:
        transactions (list): Список словарей, представляющих транзакции.

    Yields:
        str: Описание транзакции.
    """
    for transaction in transactions:
        yield transaction.get('description', 'No description')


def card_number_generator(start: int, stop: int):
    """
    Генератор 16-значных номеров карт в заданном диапазоне.

    Args:
        start: Начальный номер карты (включительно).
        stop: Конечный номер карты (включительно).

    Yields:
        Строка, представляющая 16-значный номер карты.
    """
    for i in range(start, stop + 1):
        yield str(i).zfill(16)


def filter_by_currency(transactions: list[dict], currency: str):
    """
    Фильтрует список транзакций по указанной валюте.
    Безопасно обрабатывает транзакции без информации о валюте.

    Args:
        transactions: Список словарей, представляющих транзакции.
        currency: Код валюты для фильтрации (например, "USD", "RUB").

    Yields:
        Словари транзакций, соответствующие указанной валюте.
    """
    for transaction in transactions:
        try:
            if transaction.get('operationAmount', {}).get('currency', {}).get('code') == currency:
                yield transaction
        except AttributeError:
            # Handle cases where transaction['operationAmount']['currency'] is not a dictionary
            pass
        except TypeError:
            # Handle cases where transaction['operationAmount'] or transaction['currency'] is None
            pass
