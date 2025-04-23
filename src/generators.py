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

