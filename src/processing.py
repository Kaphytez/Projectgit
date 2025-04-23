from typing import Any, Dict, List
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
    if not isinstance(description, str): # Проверка, что на вход пришла строка
        return None

    # Шаблон:
    # 'OP-' - ищем префикс OP-
    # '(\d{4})' - ищем ровно 4 цифры (\d{4}). Скобки создают "захватывающую группу",
    #             чтобы мы могли извлечь только цифры.
    # re.IGNORECASE - делает поиск нечувствительным к регистру (найдет op-1234 и OP-1234)
    pattern = r"OP-(\d{4})"
    match = re.search(pattern, description, re.IGNORECASE)

    if match:
        # Если найдено совпадение, match.group(0) содержит всю найденную подстроку ('OP-1234')
        # match.group(1) содержит только то, что попало в первую захватывающую группу (скобки) - '1234'
        operation_code = match.group(1)
        logger.info(f"Извлечен код операции: {operation_code} из '{description}'")
        return operation_code
    else:
        # logger.debug(f"Код операции не найден в '{description}'") # Можно добавить для отладки
        return None
