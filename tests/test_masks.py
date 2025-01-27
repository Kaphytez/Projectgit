from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_account(mask_account_params):
    if mask_account_params == "12345678901234567890":
        assert get_mask_account(mask_account_params) == "**7890"
    elif mask_account_params == "1234567890":
        assert get_mask_account(
            mask_account_params) == "Invalid account number: Account number must be exactly 20 digits"


def test_get_mask_account_empty():
    assert get_mask_account("") == ""


def test_get_mask_card_number(mask_card_params):
    if mask_card_params == "1111222233334444":
        assert get_mask_card_number(mask_card_params) == "1111 22** **** 4444"
    elif mask_card_params == "12345678":
        assert get_mask_card_number(mask_card_params) == "12345678"
    elif mask_card_params == "":
        assert get_mask_card_number(mask_card_params) == ""
