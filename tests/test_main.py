import pytest
from datetime import datetime
from main import main
from src.processing import filter_by_state, sort_by_date
from src.widget import mask_account_card
from src.masks import get_mask_account, get_mask_card_number
from src.generators import card_number_generator


def test_filter_by_state(sample_processing_data, state_params):
    """Тестирование фильтрации по состоянию."""
    filtered_data = filter_by_state(sample_processing_data, state_params)
    for item in filtered_data:
        assert item["state"] == state_params


def test_sort_by_date_asc(sample_processing_data):
    """Тестирование сортировки по дате по возрастанию."""
    sorted_data = sort_by_date(sample_processing_data, ascending=True)
    dates = [item["date"] for item in sorted_data]
    assert dates == sorted(dates)


def test_sort_by_date_desc(sample_processing_data):
    """Тестирование сортировки по дате по убыванию."""
    sorted_data = sort_by_date(sample_processing_data, ascending=False)
    dates = [item["date"] for item in sorted_data]
    assert dates == sorted(dates, reverse=True)


def test_mask_account_card(account_card_params):
    """Тестирование маскировки номера карты или счета."""
    masked = mask_account_card(account_card_params)
    if "Счет" in account_card_params:
        assert masked.startswith("Счет **")
    else:
        assert masked.startswith("Visa") or masked.startswith("MasterCard") or masked.startswith("Maestro")


def test_get_mask_account(mask_account_params):
    """Тестирование маскировки номера счета."""
    masked = get_mask_account(mask_account_params)
    if len(mask_account_params) == 20:
        assert masked == f"**{mask_account_params[-4:]}"
    else:
        assert masked == "Invalid account number: Account number must be exactly 20 digits"


def test_get_mask_card_number(mask_card_params):
    """Тестирование маскировки номера карты."""
    masked = get_mask_card_number(mask_card_params)
    if len(mask_card_params) == 16:
        assert masked == f"{mask_card_params[:4]} {mask_card_params[4:6]}** **** {mask_card_params[-4:]}"
    elif len(mask_card_params) <= 8:
        assert masked == mask_card_params
    else:
        assert masked == ""


def test_card_number_generator(mock_input_card_numbers, expected_card_numbers_data):
    """Тестирование генерации номеров карт."""
    generated_numbers = list(card_number_generator(1000000000000000, 1000000000000010))
    assert generated_numbers == expected_card_numbers_data


def test_filter_by_state_executed(sample_processing_data):
    """Тестирование фильтрации по состоянию 'EXECUTED'."""
    filtered_data = filter_by_state(sample_processing_data, "EXECUTED")
    for item in filtered_data:
        assert item["state"] == "EXECUTED"


def test_filter_by_state_canceled(sample_processing_data):
    """Тестирование фильтрации по состоянию 'CANCELED'."""
    filtered_data = filter_by_state(sample_processing_data, "CANCELED")
    for item in filtered_data:
        assert item["state"] == "CANCELED"
