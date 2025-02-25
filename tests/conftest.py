import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


@pytest.fixture
def mock_input():
    # Выбираем опцию 1 (вывод последних 5 транзакций) и выход (5)
    with patch('builtins.input', side_effect=["1", "5"]) as mock:
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
        {
            'id': 41428829,
            'state': 'EXECUTED',
            'date': '2019-07-03T18:35:29.512364',
            'operationAmount': {
                'amount': '8221.37',
                'currency': {
                    'name': 'USD',
                    'code': 'USD'
                }
            }
        },
        {
            'id': 939719570,
            'state': 'EXECUTED',
            'date': '2018-06-30T02:08:58.425572',
            'operationAmount': {
                'amount': '9824.07',
                'currency': {
                    'name': 'USD',
                    'code': 'USD'
                }
            }
        },
        {
            'id': 594226727,
            'state': 'CANCELED',
            'date': '2018-09-12T21:27:25.241689',
            'operationAmount': {
                'amount': '67314.70',
                'currency': {
                    'name': 'руб.',
                    'code': 'RUB'
                }
            }
        },
        {
            'id': 615064591,
            'state': 'CANCELED',
            'date': '2018-10-14T08:21:33.419441',
            'operationAmount': {
                'amount': '77751.04',
                'currency': {
                    'name': 'руб.',
                    'code': 'RUB'
                }
            }
        }
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


# Новые фикстуры
@pytest.fixture
def empty_transactions():
    return []


@pytest.fixture
def incomplete_transactions():
    return [
        {"id": 1, "state": "EXECUTED"},
        {"id": 2, "date": "2023-01-01T12:00:00.000000"},
        {"id": 3, "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}}
    ]


@pytest.fixture
def mixed_currency_transactions():
    return [
        {"id": 1, "state": "EXECUTED", "date": "2023-01-01T12:00:00.000000",
         "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}},
        {"id": 2, "state": "EXECUTED", "date": "2023-01-02T12:00:00.000000",
         "operationAmount": {"amount": "200.00", "currency": {"code": "RUB"}}},
        {"id": 3, "state": "EXECUTED", "date": "2023-01-03T12:00:00.000000",
         "operationAmount": {"amount": "300.00", "currency": {"code": "EUR"}}}
    ]


@pytest.fixture
def mixed_state_transactions():
    return [
        {"id": 1, "state": "EXECUTED", "date": "2023-01-01T12:00:00.000000"},
        {"id": 2, "state": "CANCELED", "date": "2023-01-02T12:00:00.000000"},
        {"id": 3, "state": "PENDING", "date": "2023-01-03T12:00:00.000000"}
    ]


@pytest.fixture
def mixed_account_card_transactions():
    return [
        {"id": 1, "state": "EXECUTED", "date": "2023-01-01T12:00:00.000000", "from": "Счет 12345678901234567890",
         "to": "Visa 1234567812345678"},
        {"id": 2, "state": "EXECUTED", "date": "2023-01-02T12:00:00.000000", "from": "Maestro 1234567812345678",
         "to": "Счет 98765432109876543210"},
        {"id": 3, "state": "EXECUTED", "date": "2023-01-03T12:00:00.000000", "to": "Счет 11223344556677889900"}
    ]


@pytest.fixture
def invalid_transactions():
    return [
        {"id": 1, "state": "EXECUTED", "date": "invalid_date",
         "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}},
        {"id": 2, "state": "EXECUTED", "date": "2023-01-01T12:00:00.000000",
         "operationAmount": {"amount": "invalid_amount", "currency": {"code": "USD"}}},
        {"id": 3, "state": "EXECUTED", "date": "2023-01-01T12:00:00.000000",
         "operationAmount": {"amount": "100.00", "currency": {"code": "INVALID"}}}
    ]


@pytest.fixture
def mock_exchange_rate(mocker):
    """Фикстура для мокирования get_exchange_rate."""
    return mocker.patch("src.external_api.get_exchange_rate")


@pytest.fixture
def mock_env_vars(mocker):
    """Фикстура для мокирования переменных окружения."""
    mocker.patch.dict('os.environ',
                      {'EXCHANGE_RATES_API_KEY': 'test_key', 'EXCHANGE_RATES_BASE_URL': 'https://example.com'})


@pytest.fixture
def mock_get_exchange_rate(mocker):
    """Фикстура, которая позволяет включить/выключить мокирование get_exchange_rate."""
    def _mock_get_exchange_rate(return_value=None):
        if return_value is None:
            return mocker.patch('src.external_api.get_exchange_rate',
                                side_effect=Exception("Failed to get exchange rate"))
        else:
            return mocker.patch('src.external_api.get_exchange_rate', return_value=return_value)

    return _mock_get_exchange_rate
