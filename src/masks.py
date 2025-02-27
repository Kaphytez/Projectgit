import logging

# Настраиваем логер для этого модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Уровень логирования по умолчанию


def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер карты.
    Видны первые 6 цифр и последние 4 цифры,
    остальные символы отображаются звездочками,
    номер разбит по блокам по 4 цифры"""
    logger.debug(f"Masking card number: {card_number}")  # Логируем входные данные

    # Извлекаем только номер карты (удаляем все символы, кроме цифр)
    card_number_digits: str = ''.join(filter(lambda x: x.isdigit(), card_number))

    if not card_number_digits:
        logger.warning("Card number is empty.")
        return ""
    if len(card_number_digits) <= 8:
        logger.warning(f"Card number less then 8 digits: {card_number_digits}")
        return card_number_digits
    masked_number = f"{card_number_digits[:4]} {card_number_digits[4:6]}{'**'}{' **** '}{card_number_digits[-4:]}"
    logger.debug(f"Masked card number: {masked_number}")  # Логируем результат
    return masked_number


def get_mask_account(account_number: str) -> str:
    """Маскирует номер счета, оставляя видимыми только последние 4 цифры."""
    logger.debug(f"Masking account number: {account_number}")  # Логируем входные данные

    # Извлекаем только номер счета (удаляем все символы, кроме цифр)
    account_number_digits: str = ''.join(filter(lambda x: x.isdigit(), account_number))

    if not account_number_digits:
        logger.warning("Account number is empty.")
        return ""
    if len(account_number_digits) != 20:
        logger.error(f"Invalid account number length: {len(account_number_digits)}")
        return "Invalid account number: Account number must be exactly 20 digits"
    masked_number = f"**{account_number_digits[-4:]}"
    logger.debug(f"Masked account number: {masked_number}")  # Логируем результат
    return masked_number
