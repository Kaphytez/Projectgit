import random
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


def card_number_generator(num_cards: int = 5) -> Generator[str, None, None]:
    """
    Генератор, который выдает случайные уникальные номера банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        num_cards (int): Количество случайных номеров карт для генерации. Defaults to 5.

    Yields:
        str: Случайный уникальный номер банковской карты в формате XXXX XXXX XXXX XXXX.
    """
    generated_cards = set()  # Множество для хранения сгенерированных номеров
    while len(generated_cards) < num_cards:
        temp_card_number = ''.join(random.choice('0123456789') for _ in range(16))
        formatted_card_number = ' '.join([temp_card_number[j:j + 4] for j in range(0, 16, 4)])
        generated_cards.add(formatted_card_number)
    for card in generated_cards:
        yield card


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """
    Генератор, который фильтрует транзакции по заданной валюте.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций.
        currency (str): Код валюты для фильтрации (например, "USD", "EUR").

    Yields:
        Dict[str, Any]: Транзакция, соответствующая заданной валюте.
    """
    if not transactions:
        return  # Возвращаем пустой генератор, если список транзакций пуст

    for transaction in transactions:
        try:
            if transaction['operationAmount']['currency']['code'] == currency:
                yield transaction
        except (KeyError, TypeError):
            # Пропускаем транзакции без информации о валюте
            pass
