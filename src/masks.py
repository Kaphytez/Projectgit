def get_mask_card_number(card_number):
    """Маскирует номер карты.
    Видны первые 6 цифр и последние 4 цифры,
    остальные символы отображаются звездочками,
    номер разбит по блокам по 4 цифры"""
    if not card_number:
        return ""
    if len(card_number) <= 8:
        return card_number
    masked_number = f"{card_number[:4]} {card_number[4:6]}{'**'}{' **** '}{card_number[-4:]}"
    return masked_number


def get_mask_account(account_number):
    """Маскирует номер счета, оставляя видимыми только последние 4 цифры."""
    if not account_number:
        return ""
    if len(account_number) != 20:
        return "Invalid account number: Account number must be exactly 20 digits"
    return f"**{account_number[-4:]}"
