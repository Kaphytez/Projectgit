import re
from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_info: str) -> str:
    """
    Маскирует номер карты или счета в строке, содержащей тип и номер.
    """
    if not isinstance(account_info, str):
        return "Invalid input: Input must be a string"
    date_match = re.match(r'([A-Za-zА-Яа-я\s]+)\s+([\d]+)', account_info)
    if not date_match:
        return "Invalid format: Input must have 'Type Number' format"
    account_type = date_match.group(1).strip()
    account_number = date_match.group(2)
    if "счет" in account_type.lower():
        return f"{account_type} {get_mask_account(account_number)}"
    elif "visa" in account_type.lower() or "maestro" in account_type.lower():
        return f"{account_type} {get_mask_card_number(account_number)}"
    else:
        return "Unknown account type"


def is_valid_date(date_str: str) -> bool:
    """Проверяет, является ли строка датой в формате "ГГГГ-ММ-ДДTчч:мм:сс.микросекунды"."""
    try:
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        return True
    except ValueError:
        return False


def get_date(date_str: str) -> str:
    """
    Преобразует строку с датой из формата "ГГГГ-ММ-ДДTчч:мм:сс.микросекунды"
    в формат "ДД.ММ.ГГГГ".
    Args:
        date_str: Строка с датой, например: "2024-03-11T02:26:18.671407".
    Returns:
        Строка с датой в формате "ДД.ММ.ГГГГ", или сообщение об ошибке если формат
        даты неверный.
    """
    if not isinstance(date_str, str):
        return "Invalid input: Input must be a string"
    if not is_valid_date(date_str):
        return "Invalid date format: Date must be in 'YYYY-MM-DDTHH:MM:SS.ffffff' format"
    date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if not date_match:
        return "Invalid date format"
    year = date_match.group(1)
    month = date_match.group(2)
    day = date_match.group(3)
    return f"{day}.{month}.{year}"
