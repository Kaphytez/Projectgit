from datetime import datetime


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
    try:
        date_object = datetime.fromisoformat(date_str)
        return date_object.strftime("%d.%m.%Y")
    except ValueError:
        return "Invalid date format"


def mask_account_card(account_info: str) -> str:
    """
    Маскирует номер карты или счета в строке, содержащей тип и номер.
    """
    if not isinstance(account_info, str):
        return "Invalid input: Input must be a string"
    # Предполагаем, что формат: "Тип Номер"
    parts = account_info.split()
    if len(parts) != 2:
        return "Invalid format: Input must have 'Type Number' format"
    account_type = parts[0]
    account_number = parts[1]  # Считаем, что это номер
    if "счет" in account_type.lower():
        return f"Счет **{account_number[-4:]}"
    elif "visa" in account_type.lower() or "maestro" in account_type.lower():
        if len(account_number) >= 12:
            masked_number = account_number[:6] + '*' * (len(account_number) - 10) + account_number[-4:]
            return f"Visa {masked_number}"  # Или Maestro
        else:
            return account_info  # Не маскируем короткие номера
    else:
        return "Unknown account type"
