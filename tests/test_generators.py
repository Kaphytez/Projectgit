import unittest
from typing import Any, Dict, Iterator, List

from src import generators


class TestFilterByCurrency(unittest.TestCase):

    def test_filter_by_currency_correct_currency(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {'currency': {'code': 'RUB'}}},
            {'operationAmount': {'currency': {'code': 'USD'}}}
        ]
        filtered_transactions: List[Dict[str, Any]] = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 2)
        self.assertEqual(filtered_transactions[0]['operationAmount']['currency']['code'], 'USD')
        self.assertEqual(filtered_transactions[1]['operationAmount']['currency']['code'], 'USD')

    def test_filter_by_currency_no_matching_currency(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {'currency': {'code': 'USD'}}}
        ]
        filtered_transactions: List[Dict[str, Any]] = list(generators.filter_by_currency(transactions, 'RUB'))
        self.assertEqual(len(filtered_transactions), 0)

    def test_filter_by_currency_empty_list(self) -> None:
        transactions: List[Dict[str, Any]] = []
        filtered_transactions: List[Dict[str, Any]] = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 0)

    def test_filter_by_currency_missing_currency_info(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {}},  # Missing currency info
            {}  # Completely missing operationAmount
        ]
        filtered_transactions: List[Dict[str, Any]] = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 1)
        self.assertEqual(filtered_transactions[0]['operationAmount']['currency']['code'], 'USD')


class TestTransactionDescriptions(unittest.TestCase):

    def test_transaction_descriptions_correct_descriptions(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'description': 'Перевод организации'},
            {'description': 'Перевод со счета на счет'},
            {'description': 'Пополнение карты'}
        ]
        descriptions: List[str] = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'Перевод со счета на счет', 'Пополнение карты'])

    def test_transaction_descriptions_empty_list(self) -> None:
        transactions: List[Dict[str, Any]] = []
        descriptions: List[str] = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, [])

    def test_transaction_descriptions_missing_description(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'description': 'Перевод организации'},
            {},  # Missing description
            {'description': 'Пополнение карты'}
        ]
        descriptions: List[str] = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'No description', 'Пополнение карты'])

    def test_transaction_descriptions_mixed_transactions(self) -> None:
        transactions: List[Dict[str, Any]] = [
            {'description': 'Перевод организации'},
            {},  # Missing description
            {'description': 'Пополнение карты'},
            {'description': 'Снятие наличных'}
        ]
        descriptions: List[str] = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'No description',
                                        'Пополнение карты', 'Снятие наличных'])


class TestCardNumberGenerator(unittest.TestCase):
    def test_card_number_generator(self) -> None:
        card_numbers: Iterator[str] = generators.card_number_generator(1, 3)
        self.assertEqual(next(card_numbers), "0000000000000001")
        self.assertEqual(next(card_numbers), "0000000000000002")
        self.assertEqual(next(card_numbers), "0000000000000003")
        with self.assertRaises(StopIteration):
            next(card_numbers)

    def test_card_number_generator_single_number(self) -> None:
        card_numbers: Iterator[str] = generators.card_number_generator(1234567890123456, 1234567890123456)
        self.assertEqual(next(card_numbers), "1234567890123456")
        with self.assertRaises(StopIteration):
            next(card_numbers)

    def test_card_number_generator_large_range(self) -> None:
        card_numbers: Iterator[str] = generators.card_number_generator(9999999999999990, 10000000000000000)
        self.assertEqual(next(card_numbers), "9999999999999990")
        self.assertEqual(next(card_numbers), "9999999999999991")
