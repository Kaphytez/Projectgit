from datetime import datetime

from src import generators
from src.processing import filter_by_state
from src.widget import get_date, mask_account_card


def main_function(another_action, choice=None, state_filter=None, order=None, currency_filter=None,
                  description_count=None, start=None, stop=None):
    if another_action != 'да':
        return None

    transactions = [
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

    def format_transaction(item):
        """Вспомогательная функция для форматирования транзакции"""
        return {
            'date': get_date(item['date']),
            'id': item['id'],
            'state': item['state'],
            'account': mask_account_card(item.get('from', '')),
            'card': mask_account_card(item.get('card', '')),
        }

    all_transactions = transactions

    # Убедимся, что choice не None
    choice = choice or ""

    if choice == 'f':
        filtered_transactions = list(filter_by_state(all_transactions, state=state_filter or "EXECUTED"))
        formatted_transactions = list(map(format_transaction, filtered_transactions))
        return formatted_transactions
    elif choice == 's':
        sorted_transactions = sorted(all_transactions,
                                     key=lambda x: datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%S.%f'),
                                     reverse=(order == 'd'))
        formatted_transactions = list(map(format_transaction, sorted_transactions))
        return formatted_transactions
    elif choice == 'c':
        filtered_transactions = list(generators.filter_by_currency(all_transactions, currency_filter))
        if not filtered_transactions:
            return f"Транзакции с валютой {currency_filter} не найдены."
        else:
            return filtered_transactions
    elif choice == 'd':  # Новая опция для генератора описаний
        descriptions = generators.transaction_descriptions(all_transactions)
        num_descriptions = int(description_count) if description_count else 5  # Кол-во из запроса или 5
        result = []
        for _ in range(num_descriptions):
            try:
                result.append(next(descriptions))
            except StopIteration:
                break  # Если транзакций меньше, чем запрошено
        return result
    elif choice.lower() == "k":
        start_str = input("Введите начальный номер карты: ")
        stop_str = input("Введите конечный номер карты: ")
        try:
            start = int(start_str)
            stop = int(stop_str)
        except ValueError:
            print("Ошибка: 'start' и 'stop' должны быть целыми числами.")
            return None
        else:
            if start > stop:
                print("Ошибка: Начальный номер должен быть меньше или равен конечному.")
                return None
            else:
                result = list(generators.card_number_generator(start, stop))
                return result
    else:
        return "Программа завершена."


if __name__ == "__main__":
    another_action = input("Вы хотите выполнить операцию? (да/нет): ")
    if another_action.lower() == "да":
        choice = input(
            "Выберите действие: (f - фильтрация по статусу, s - сортировка по дате, c - фильтрация по валюте,"
            " d - генерация описаний, k - генерация карт): ")

        if choice.lower() == "f":
            state_filter = input("Введите статус для фильтрации (EXECUTED, CANCELED): ")
            result = main_function(another_action, choice=choice.lower(), state_filter=state_filter.upper())
        elif choice.lower() == "s":
            order = input("Выберите порядок сортировки (a - по возрастанию, d - по убыванию): ")
            result = main_function(another_action, choice=choice.lower(), order=order.lower())
        elif choice.lower() == "c":
            currency_filter = input("Введите код валюты для фильтрации (например, USD, RUB): ")
            result = main_function(another_action, choice=choice.lower(), currency_filter=currency_filter.upper())
        elif choice.lower() == "d":
            description_count = input("Введите количество описаний для генерации: ")
            result = main_function(another_action, choice=choice.lower(), description_count=description_count)
        elif choice.lower() == "k":
            result = main_function(another_action, choice=choice.lower())
        else:
            result = main_function(another_action)

        print(result)
    else:
        print("Программа завершена.")
