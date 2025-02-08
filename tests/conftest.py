from unittest.mock import patch

import pytest


@pytest.fixture
def mock_input():
    with patch('builtins.input', side_effect=["да", "f", "EXECUTED"]) as mock:
        yield mock


@pytest.fixture
def expected_filter_executed_data():
    return [
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'},
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None}
    ]


@pytest.fixture
def expected_filter_canceled_data():
    return [
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None}
    ]


@pytest.fixture
def expected_sort_asc_data():
    return [
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None},
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None},
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'}
    ]


@pytest.fixture
def expected_sort_desc_data():
    return [
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None},
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None}
    ]


@pytest.fixture
def sample_processing_data():
    return [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'account': '12345678901234567890', 'card': '111111222233334444'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'account': '98765432109876543210'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'account': '11223344556677889900'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'account': '00998877665544332211'}
    ]


@pytest.fixture(params=["Счет 12345678901234567890", "Visa 1111222233334444"])
def account_card_params(request):
    return request.param


@pytest.fixture(params=["12345678901234567890", "1234567890"])
def mask_account_params(request):
    return request.param


@pytest.fixture(params=["1111222233334444", "12345678", ""])
def mask_card_params(request):
    return request.param


@pytest.fixture(params=["EXECUTED", "CANCELED"])
def state_params(request):
    return request.param


@pytest.fixture
def mock_input_card_numbers():
    with patch('builtins.input', side_effect=["1000000000000000", "1000000000000010"]) as mock:
        yield mock


@pytest.fixture
def expected_card_numbers_data():
    return [
        "1000000000000000",
        "1000000000000001",
        "1000000000000002",
        "1000000000000003",
        "1000000000000004",
        "1000000000000005",
        "1000000000000006",
        "1000000000000007",
        "1000000000000008",
        "1000000000000009",
        "1000000000000010",
    ]
