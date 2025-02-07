import pytest
from src.widget import get_date, mask_account_card


def test_mask_account_card_account():
    assert mask_account_card("Счет 12345678901234567890") == "Счет **7890"


def test_mask_account_card_visa():
    assert mask_account_card("Visa 1111222233334444") == "Visa 1111 22** **** 4444"


def test_mask_account_card_invalid_type():
    assert mask_account_card("Неизвестный 1234567890") == "Unknown account type"


def test_mask_account_card_invalid_format():
    assert mask_account_card("Счет_1234567890") == "Счет_1234567890"


def test_mask_account_card_not_string():
    assert mask_account_card(12345) == "Invalid input: Input must be a string"


def test_get_date_valid():
    assert get_date("2023-10-26T10:30:00.123456") == "26.10.2023"


def test_get_date_invalid_format():
    assert get_date("2023-10-26 10:30:00") == "Invalid date format"


def test_get_date_invalid_input():
    assert get_date(12345) == "Invalid input: Input must be a string"
