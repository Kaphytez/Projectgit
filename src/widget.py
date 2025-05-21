import logging
from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number

logger = logging.getLogger(__name__)

# Словарь для стандартизации вывода и определения типа
ACCOUNT_TYPES = {
    "счет": "Счет",
    "visa": "Visa",
    "mastercard": "MasterCard",
    "maestro": "Maestro",
    "мир": "МИР",
    # Можно добавить другие типы или общую "Карта"
}


def get_date(date_str: str) -> str:
    """
    Преобразует строку с датой из формата ISO 8601 (YYYY-MM-DDTHH:MM:SSZ или YYYY-MM-DDTHH:MM:SS)
    в формат DD.MM.YYYY.

    Args:
        date_str: Строка с датой в формате ISO.

    Returns:
        Строка с датой в формате DD.MM.YYYY или сообщение об ошибке/пустая строка.
    """
    if not isinstance(date_str, str):
        logger.warning(f"Неверный тип ввода для get_date: {type(date_str)}. Ожидалась строка.")
        return "Invalid input type"  # Или вернуть пустую строку ""

    if not date_str:  # Явная проверка на пустую строку
        return ""  # Возвращаем пустую строку, если на входе пусто

    try:
        parse_format = "%Y-%m-%dT%H:%M:%S"
        if date_str.endswith("Z"):
            date_str_processed = date_str[:-1]
        # Возможно, стоит обработать и микросекунды, если они могут появиться
        elif '.' in date_str:
            date_str_processed = date_str.split('.')[0]
            # parse_format = "%Y-%m-%dT%H:%M:%S.%f" # если нужно парсить с микросекундами
        else:
            date_str_processed = date_str

        date_object = datetime.strptime(date_str_processed, parse_format)
        return date_object.strftime("%d.%m.%Y")
    except ValueError:
        logger.error(f"Не удалось распознать формат даты: '{date_str}'")
        return f"Invalid date format ({date_str})"  # Возвращаем ошибку с исходной строкой
    except Exception as e:  # Ловим другие возможные ошибки
        logger.exception(f"Неожиданная ошибка при обработке даты '{date_str}': {e}")
        return f"Error processing date ({date_str})"


def mask_account_card(account_info: str) -> str:
    """
    Маскирует номер карты или счета в строке.
    Ожидает формат "Тип Номер" (например, "Visa Classic 1234...").

    Args:
        account_info: Строка с типом и номером счета/карты.

    Returns:
        Строка с типом и замаскированным номером или исходная строка при ошибке.
    """
    if not isinstance(account_info, str):
        logger.warning(f"Неверный тип ввода для mask_account_card: {type(account_info)}. Ожидалась строка.")
        return "Invalid input type"  # Или вернуть account_info

    if not account_info:
        return ""

    parts = account_info.split(maxsplit=1)  # Разделяем только на две части: тип и остальное
    if len(parts) != 2:
        logger.warning(f"Не удалось разделить строку на тип и номер: '{account_info}'")
        return account_info  # Или return "Invalid format"

    account_type_raw = parts[0]
    account_number = parts[1].strip()  # Убираем лишние пробелы у номера

    # Ищем тип в словаре по нижнему регистру
    account_type_key = account_type_raw.lower()
    output_type = None
    masking_function = None

    if account_type_key == "счет":
        output_type = ACCOUNT_TYPES["счет"]
        masking_function = get_mask_account
    else:
        # Ищем совпадение с ключами карт
        for key, standard_name in ACCOUNT_TYPES.items():
            if key != "счет" and key in account_type_key:  # Проверяем вхождение (на случай "Visa Classic")
                output_type = standard_name
                masking_function = get_mask_card_number
                break  # Нашли первое совпадение

    if output_type and masking_function:
        masked_number = masking_function(account_number)
        # Проверяем, вернула ли функция маскировки что-то осмысленное
        if masked_number:
            return f"{output_type} {masked_number}"
        else:
            logger.warning(
                f"Функция маскировки вернула пустой результат для номера: '{account_number}' (тип: {output_type})")
            # Возвращаем тип + оригинал номера? Или только тип?
            return f"{output_type} [Ошибка маскировки]"
    else:
        logger.warning(f"Неизвестный тип счета/карты: '{account_type_raw}' в строке '{account_info}'")
        # Возвращаем оригинал или спец. значение?
        return f"Unknown type ({account_type_raw}) {get_mask_card_number(account_number)}"
