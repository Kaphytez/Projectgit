from typing import Any, Dict, List, Generator, Optional
import re
import logging

logger = logging.getLogger(__name__)


def filter_by_state(data, state: str) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению 'state'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'state'.
        state (str): Значение 'state', по которому нужно фильтровать.

    Returns:
        list: Новый список словарей, которые соответствуют заданному 'state'.
    """
    return [item for item in data if item.get("state") == state]


def sort_by_date(data, ascending: bool = True) -> list:
    """
    Сортирует список словарей по дате в поле 'date'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'date'.
        ascending (bool, optional): True для сортировки по возрастанию, False для убывания. Defaults to True.

    Returns:
        list: Новый список словарей, отсортированных по дате.
    """
    return sorted(
        data,
        key=lambda x: x["date"],
        reverse=not ascending
    )


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> Generator[Dict[str, Any], None, None]:
    """
    Фильтрует транзакции по коду валюты, возвращая генератор.

    Использует безопасный доступ к вложенным данным.
    Сравнение кода валюты происходит без учета регистра введенного `currency_code`.

    Args:
        transactions: Список словарей, представляющих транзакции.
        currency_code: Код валюты для фильтрации (например, "USD", "RUB").
                       Будет приведен к верхнему регистру для сравнения.

    Yields:
        Словарь транзакции, если ее валюта соответствует запрошенной.
    """
    # Приводим искомый код валюты к верхнему регистру для консистентности
    target_currency = currency_code.upper()

    for transaction in transactions:

        op_amount = transaction.get("operationAmount")
        if isinstance(op_amount, dict):  # Убедимся, что operationAmount это словарь
            currency_info = op_amount.get("currency")
            if isinstance(currency_info, dict):  # Убедимся, что currency это словарь
                code = currency_info.get("code")
                # Сравниваем код из транзакции (если он есть и является строкой)
                # с целевым кодом валюты.
                if isinstance(code, str) and code.upper() == target_currency:
                    yield transaction


def extract_operation_code(description: str) -> Optional[str]:
    """
    Ищет и извлекает код операции формата OP-XXXX из строки описания.

    Args:
        description: Строка с описанием транзакции.

    Returns:
        Найденный код операции (только XXXX) или None, если код не найден.
    """
    if not isinstance(description, str):  # Проверка, что на вход пришла строка
        return None

    pattern = r"OP-(\d{4})"
    match = re.search(pattern, description, re.IGNORECASE)

    if match:
        operation_code = match.group(1)
        logger.info(f"Извлечен код операции: {operation_code} из '{description}'")
        return operation_code
    else:
        return None


def categorize_transactions(transactions: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций по заданным категориям на основе описаний.

    Проверяет наличие каждой категории (как подстроки, без учета регистра)
    в поле 'description' каждой транзакции.

    Args:
        transactions: Список словарей с данными о банковских операциях.
                      Ожидается наличие ключа 'description'.
        categories: Список строк-категорий для поиска в описаниях.

    Returns:
        Словарь, где ключи - это названия категорий (из списка `categories`),
        а значения - количество операций, в описании которых найдена
        соответствующая категория (как подстрока, case-insensitive).
        Если категория не найдена ни разу, ее значение будет 0.
    """
    # Инициализируем словарь для подсчета: каждая категория начинается с 0
    category_counts: Dict[str, int] = {category: 0 for category in categories}

    # Проверяем, что список категорий не пуст, чтобы не делать лишней работы
    if not categories:
        logger.warning("Список категорий для анализа пуст.")
        return category_counts

    logger.info(f"Начало категоризации {len(transactions)} транзакций по категориям: {categories}")

    for i, transaction in enumerate(transactions):
        # Безопасно получаем описание, приводим к строке и нижнему регистру
        description = str(transaction.get("description", "")).lower()

        # Если описание пустое, переходим к следующей транзакции
        if not description:
            # logger.debug(f"Транзакция {i+1} (ID: {transaction.get('id', 'N/A')}) пропущена - пустое описание.")
            continue

        # Проверяем наличие каждой категории в описании
        for category in categories:
            # Ищем категорию (приведенную к нижнему регистру) как подстроку в описании
            if category.lower() in description:
                # Если нашли, увеличиваем счетчик для этой категории
                category_counts[category] += 1
                # Важно: Одна транзакция может попасть в несколько категорий,
                # если ее описание содержит несколько ключевых слов.
                # Например, "Оплата за интернет и телефон" увеличит счетчики
                # и для "интернет", и для "телефон", если они есть в `categories`.
                # Логируем первое найденное совпадение для транзакции (для примера)

    logger.info(f"Категоризация завершена. Результаты: {category_counts}")
    return category_counts


def filter_by_description_keyword(transactions: List[Dict[str, Any]], keyword: str)\
        -> Generator[Dict[str, Any], None, None]:
    """
    Фильтрует транзакции по наличию ключевого слова в описании (без учета регистра).

    Args:
        transactions: Список словарей транзакций.
        keyword: Ключевое слово для поиска в поле 'description'.

    Yields:
        Словарь транзакции, если ключевое слово найдено в описании.
    """
    if not keyword:  # Если передано пустое слово, не фильтруем
        logger.warning("Передано пустое ключевое слово для фильтрации по описанию.")
        # Возвращаем все транзакции как генератор
        for transaction in transactions:
            yield transaction
        return  # Явный выход

    search_term = keyword.lower()
    logger.info(f"Фильтрация по ключевому слову в описании: '{search_term}'")

    for transaction in transactions:
        description = str(transaction.get("description", "")).lower()
        if search_term in description:
            yield transaction
