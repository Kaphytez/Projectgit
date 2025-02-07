import unittest
from typing import Any, Dict, List

from src import generators


class TestFilterByCurrency(unittest.TestCase):

    def test_filter_by_currency_correct_currency(self):
        transactions = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {'currency': {'code': 'EUR'}}},
            {'operationAmount': {'currency': {'code': 'USD'}}}
        ]
        filtered_transactions = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 2)
        self.assertEqual(filtered_transactions[0]['operationAmount']['currency']['code'], 'USD')
        self.assertEqual(filtered_transactions[1]['operationAmount']['currency']['code'], 'USD')

    def test_filter_by_currency_no_matching_currency(self):
        transactions = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {'currency': {'code': 'EUR'}}}
        ]
        filtered_transactions = list(generators.filter_by_currency(transactions, 'RUB'))
        self.assertEqual(len(filtered_transactions), 0)

    def test_filter_by_currency_empty_list(self):
        transactions: List[Dict[str, Any]] = []
        filtered_transactions = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 0)

    def test_filter_by_currency_missing_currency_info(self):
        transactions = [
            {'operationAmount': {'currency': {'code': 'USD'}}},
            {'operationAmount': {}},  # Missing currency info
            {}  # Completely missing operationAmount
        ]
        filtered_transactions = list(generators.filter_by_currency(transactions, 'USD'))
        self.assertEqual(len(filtered_transactions), 1)
        self.assertEqual(filtered_transactions[0]['operationAmount']['currency']['code'], 'USD')


class TestTransactionDescriptions(unittest.TestCase):

    def test_transaction_descriptions_correct_descriptions(self):
        transactions = [
            {'description': 'Перевод организации'},
            {'description': 'Перевод со счета на счет'},
            {'description': 'Пополнение карты'}
        ]
        descriptions = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'Перевод со счета на счет', 'Пополнение карты'])

    def test_transaction_descriptions_empty_list(self):
        transactions: List[Dict[str, Any]] = []
        descriptions = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, [])

    def test_transaction_descriptions_missing_description(self):
        transactions = [
            {'description': 'Перевод организации'},
            {},  # Missing description
            {'description': 'Пополнение карты'}
        ]
        descriptions = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'No description', 'Пополнение карты'])

    def test_transaction_descriptions_mixed_transactions(self):
        transactions = [
            {'description': 'Перевод организации'},
            {},  # Missing description
            {'description': 'Пополнение карты'},
            {'description': 'Снятие наличных'}
        ]
        descriptions = list(generators.transaction_descriptions(transactions))
        self.assertEqual(descriptions, ['Перевод организации', 'No description',
                                        'Пополнение карты', 'Снятие наличных'])


class TestCardNumberGenerator(unittest.TestCase):

    def test_card_number_generator_correct_number_of_cards(self):
        num_cards = 3
        card_numbers = list(generators.card_number_generator(num_cards))
        self.assertEqual(len(card_numbers), num_cards)

    def test_card_number_generator_correct_format(self):
        num_cards = 1
        card_numbers = list(generators.card_number_generator(num_cards))
        card_number = card_numbers[0]
        self.assertEqual(len(card_number), 19)  # Length of XXXX XXXX XXXX XXXX
        self.assertEqual(card_number[4], ' ')
        self.assertEqual(card_number[9], ' ')
        self.assertEqual(card_number[14], ' ')

    def test_card_number_generator_valid_card_numbers(self):
        num_cards = 2
        card_numbers = list(generators.card_number_generator(num_cards))
        for card_number in card_numbers:
            # Проверяем, что все символы, кроме пробелов, являются цифрами
            digits_only = card_number.replace(" ", "")
            self.assertTrue(digits_only.isdigit())
            self.assertEqual(len(digits_only), 16)

    def test_card_number_generator_correct_number_of_unique_cards(self):
        num_cards = 100
        card_numbers = list(generators.card_number_generator(num_cards))
        unique_cards = set(card_numbers)
        self.assertEqual(len(unique_cards), num_cards)

    def test_card_number_generator_edge_cases(self):
        num_cards = 0
        card_numbers = list(generators.card_number_generator(num_cards))
        self.assertEqual(len(card_numbers), 0)

        num_cards = 1
        card_numbers = list(generators.card_number_generator(num_cards))
        self.assertEqual(len(card_numbers), 1)
