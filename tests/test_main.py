import pytest

from main import main_function


def test_main_function_filter_executed():
    expected = [
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'},
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None}
    ]

    assert main_function(another_action="да", choice="f", state_filter="EXECUTED") == expected


def test_main_function_filter_canceled():
    expected = [
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None}
    ]
    assert main_function(another_action="да", choice="f", state_filter="CANCELED") == expected


def test_main_function_filter_default():
    expected = [
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'},
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None}
    ]
    assert main_function(another_action="да", choice="f", state_filter=None) == expected


def test_main_function_sort_asc():
    expected = [
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None},
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None},
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'}
    ]

    assert main_function(another_action="да", choice="s", order="a") == expected


def test_main_function_sort_desc():
    expected = [
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None},
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None}
    ]
    assert main_function(another_action="да", choice="s", order="d") == expected


def test_main_function_sort_default():
    expected = [
        {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **3210', 'card': None},
        {'date': '12.09.2018', 'id': 594226727, 'state': 'CANCELED', 'account': 'Счет **9900', 'card': None},
        {'date': '14.10.2018', 'id': 615064591, 'state': 'CANCELED', 'account': 'Счет **2211', 'card': None},
        {'date': '03.07.2019', 'id': 41428829, 'state': 'EXECUTED', 'account': 'Счет **7890',
         'card': 'Visa 1111 11** **** 4444'}
    ]
    assert main_function(another_action="да", choice="s", order=None) == expected


def test_main_function_no_action():
    assert main_function(another_action="нет") is None
