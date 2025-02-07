from datetime import datetime
from src.masks import get_mask_account, get_mask_card_number


def get_date(date_str: str) -> str:
    """
    Преобразует строку с датой из формата "ГГГГ-ММ-ДДTчч:мм:сс.микросекунды"
    в формат "ДД.ММ.ГГГГ".
    """
    if not isinstance(date_str, str):
        return "Invalid input: Input must be a string"
    try:
        date_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        return date_object.strftime("%d.%m.%Y")
    except ValueError:
        return "Invalid date format"


def mask_account_card(account_info: str) -> str:
    """
    Маскирует номер карты или счета в строке, содержащей тип и номер.
    """
    if not isinstance(account_info, str):
        return "Invalid input: Input must be a string"

    if not account_info:
        return ""  # Возвращаем пустую строку для пустых значений

    # Предполагаем, что формат: "Тип Номер"
    parts = account_info.split()
    if len(parts) != 2:
        return account_info  # Если формат неверный, возвращаем исходную строку

    account_type = parts[0]
    account_number = parts[1]  # Считаем, что это номер

    if "счет" in account_type.lower():
        return f"Счет {get_mask_account(account_number)}"
    elif "visa" in account_type.lower() or "maestro" in account_type.lower():
        return f"Visa {get_mask_card_number(account_number)}"
    else:
        return "Unknown account type"
