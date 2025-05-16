from typing import Any, Dict, Generator, List
import logging

logger = logging.getLogger(__name__)


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Генератор описаний транзакций.
    """
    if not isinstance(transactions, list):
        # Можно вызвать исключение или просто ничего не генерировать
        logger.error("Input to transaction_descriptions is not a list.")  # Нужен импорт logging и logger
        return

    for transaction in transactions:
        if not isinstance(transaction, dict):
            logger.warning(f"Skipping non-dict item in transaction list: {transaction}")
            continue  # Пропустить элемент, если это не словарь
        description = transaction.get('description')
        yield description if description is not None else 'No description'


def card_number_generator(start: int, stop: int) -> Generator[str, None, None]:
    """
    Генератор 16-значных номеров карт в заданном диапазоне.
    ВНИМАНИЕ: Генерирует числовые строки, НЕ валидные номера карт (без алгоритма Луна).
    """
    if start > stop:
        logger.warning(f"Start ({start}) is greater than stop ({stop}) in card_number_generator.")
        return
    # Добавить проверку на слишком большой диапазон?
    # if stop - start > 1_000_000: # Например
    #     logger.warning("Generating a very large range of card numbers.")

    for i in range(start, stop + 1):
        yield f"{i:016d}"
