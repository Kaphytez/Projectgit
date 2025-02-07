import unittest
from main import main_function  # Correct import
from typing import List, Dict, Any


class TestMainFunction(unittest.TestCase):
    # Sample data for testing
    transactions: List[Dict[str, Any]] = [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        }
    ]

    def setUp(self):
        # Prepare expected data here based on the transactions
        self.expected_filter_executed_data = [
            {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **6952',
             'card': ''},
            {'date': '04.04.2019', 'id': 142264268, 'state': 'EXECUTED', 'account': 'Счет **8542',
             'card': ''}
        ]

        self.expected_sort_asc_data = [
            {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **6952',
             'card': ''},
            {'date': '04.04.2019', 'id': 142264268, 'state': 'EXECUTED', 'account': 'Счет **8542',
             'card': ''}
        ]

        self.expected_sort_desc_data = [
            {'date': '04.04.2019', 'id': 142264268, 'state': 'EXECUTED', 'account': 'Счет **8542',
             'card': ''},
            {'date': '30.06.2018', 'id': 939719570, 'state': 'EXECUTED', 'account': 'Счет **6952',
             'card': ''}
        ]

        self.expected_filter_currency_data = [
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {
                    "amount": "9824.07",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "Счет 11776614605963066702"
            },
            {
                "id": 142264268,
                "state": "EXECUTED",
                "date": "2019-04-04T23:20:05.206878",
                "operationAmount": {
                    "amount": "79114.93",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 19708645243227258542",
                "to": "Счет 75651667383060284188"
            }
        ]

        self.expected_transaction_descriptions_data = [
            "Перевод организации",
            "Перевод со счета на счет"
        ]

    def test_main_function_filter_executed(self):
        self.assertEqual(main_function(another_action="да", choice="f", state_filter="EXECUTED"),
                         self.expected_filter_executed_data)

    def test_main_function_filter_canceled(self):
        self.assertEqual(main_function(another_action="да", choice="f", state_filter="CANCELED"), [])

    def test_main_function_filter_default(self):
        self.assertEqual(main_function(another_action="да", choice="f", state_filter=None),
                         self.expected_filter_executed_data)

    def test_main_function_sort_asc(self):
        self.assertEqual(main_function(another_action="да", choice="s", order="a"), self.expected_sort_asc_data)

    def test_main_function_sort_desc(self):
        self.assertEqual(main_function(another_action="да", choice="s", order="d"), self.expected_sort_desc_data)

    def test_main_function_sort_default(self):
        self.assertEqual(main_function(another_action="да", choice="s", order=None), self.expected_sort_asc_data)

    def test_main_function_filter_currency(self):
        self.assertEqual(main_function(another_action="да", choice="c", currency_filter="USD"),
                         self.expected_filter_currency_data)

    def test_main_function_transaction_descriptions(self):
        self.assertEqual(main_function(another_action="да", choice="d", description_count="2"),
                         self.expected_transaction_descriptions_data)

    def test_main_function_card_number_generator(self):
        result = main_function(another_action="да", choice="k")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)  # Assuming default number of cards is 5
        for card_number in result:
            self.assertIsInstance(card_number, str)
            self.assertEqual(len(card_number), 19)

    def test_main_function_no_action(self):
        self.assertIsNone(main_function(another_action="нет"))

    def test_main_function_no_choice(self):
        self.assertEqual(main_function(another_action="да"), "Программа завершена.")
