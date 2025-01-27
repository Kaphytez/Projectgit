
from src.widget import mask_account_card, is_valid_date, get_date


def test_mask_account_card() -> None:
    assert mask_account_card('Maestro 1596837868705199') == 'Maestro 1596 83** **** 5199'


def test_is_valid_date() -> None:
    assert is_valid_date("2024-03-11T02:26:18.671407") == '11.03.2024'


def test_get_date() -> None:
    assert get_date("2024-03-11T02:26:18.671407") == '11.03.2024'
