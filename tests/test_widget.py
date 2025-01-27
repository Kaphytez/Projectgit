from src.widget import mask_account_card, get_date


def test_mask_account_card_account(account_card_params):
    if "Счет" in account_card_params:
        assert mask_account_card(account_card_params) == "Счет **7890"


def test_mask_account_card_visa(account_card_params):
    if "Visa" in account_card_params:
        assert mask_account_card(account_card_params) == "Visa 1111 22** **** 4444"


def test_mask_account_card_invalid_type():
    assert mask_account_card("Неизвестный 1234567890") == "Unknown account type"


def test_mask_account_card_invalid_format():
    assert mask_account_card("Счет_1234567890") == "Invalid format: Input must have 'Type Number' format"


def test_mask_account_card_not_string():
    assert mask_account_card(12345) == "Invalid input: Input must be a string"


def test_get_date_valid():
    assert get_date("2023-10-26T10:30:00.123456") == "26.10.2023"


def test_get_date_invalid_format():
    assert get_date("2023-10-26 10:30:00") == ("Invalid date format:"
                                               " Date must be in 'YYYY-MM-DDTHH:MM:SS.ffffff' format")


def test_get_date_invalid_input():
    assert get_date(12345) == "Invalid input: Input must be a string"
