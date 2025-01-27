from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_account_valid():
    assert get_mask_account("12345678901234567890") == "**7890"


def test_get_mask_account_invalid_length():
    assert get_mask_account("1234567890") == "Invalid account number: Account number must be exactly 20 digits"


def test_get_mask_account_empty():
    assert get_mask_account("") == ""


def test_get_mask_card_number_valid():
    assert get_mask_card_number("1111222233334444") == "1111 22** **** 4444"


def test_get_mask_card_number_short():
    assert get_mask_card_number("12345678") == "12345678"


def test_get_mask_card_number_empty():
    assert get_mask_card_number("") == ""
