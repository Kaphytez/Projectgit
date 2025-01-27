from src.widget import mask_account_card, get_date


def test_mask_account_card_account():
    assert mask_account_card("Счет 12345678901234567890") == "Счет **7890"


def test_mask_account_card_visa():
    assert mask_account_card("Visa 1111222233334444") == "Visa 1111 22** **** 4444"


def test_mask_account_card_maestro():
    assert mask_account_card("Maestro 5555666677778888") == "Maestro 5555 66** **** 8888"


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
