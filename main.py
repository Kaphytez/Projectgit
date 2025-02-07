from src.processing import data, filter_by_state
from src.widget import get_date, mask_account_card
from src import generators


def format_transaction(item):
    """Вспомогательная функция для форматирования транзакции"""
    return {
        'date': get_date(item['date']),
        'id': item['id'],
        'state': item['state'],
        'account': mask_account_card(item.get('from', '')),
        'card': mask_account_card(item.get('card', '')),
    }


def main_function(another_action, choice=None, state_filter=None, order=None, currency_filter=None,
                  description_count=None):
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

    all_transactions = transactions

    if choice == 'f':
        filtered_transactions = list(filter_by_state(all_transactions, state=state_filter or "EXECUTED"))
        formatted_transactions = list(map(format_transaction, filtered_transactions))
        return formatted_transactions
    elif choice == 's':
        sorted_transactions = sorted(all_transactions, key=lambda x: get_date(x['date']),
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
    elif choice == 'k':  # Новая опция для генератора карт
        card_numbers = generators.card_number_generator()  # Создаем генератор
        result = list(card_numbers)  # Преобразуем генератор в список
        return result
    else:
        return "Программа завершена."


if __name__ == "__main__":
    another_action = input(
        "Хотите ли вы выполнить операции с транзакциями или сгенерировать номера карт? (да/нет): ").lower()

    if another_action == 'да':
        while True:
            choice = input(
                "Выберите действие: 'f' для фильтрации по 'state', 's' для сортировки по 'date',"
                " 'c' для фильтрации по 'currency', 'd' для получения описаний транзакций, 'k' для генерации номеров карт: ").lower()
            if choice in ('f', 's', 'c', 'd', 'k'):
                break
            print("Неверный ввод. Попробуйте еще раз.")

        if choice == 'f':
            while True:
                state_filter = input(
                    "Введите значение 'state' для фильтрации ('EXECUTED', 'CANCELED'): ").strip().upper()
                if state_filter in ('EXECUTED', 'CANCELED', ''):
                    break
                print("Неверный ввод. Попробуйте еще раз.")
            result = main_function(another_action, choice, state_filter)

            if isinstance(result, list):
                for transaction in result:
                    print(transaction)
            else:
                print(result)
        elif choice == 's':
            while True:
                order = input("Введите 'a' для сортировки по возрастанию или 'd' для сортировки по убыванию: ").lower()
                if order in ('a', 'd'):
                    break
                print("Неверный ввод. Попробуйте еще раз.")
            result = main_function(another_action, choice, None, order)
            if isinstance(result, list):
                for transaction in result:
                    print(transaction)
            else:
                print(result)
        elif choice == 'c':
            currency_filter = input("Введите код валюты для фильтрации (например, USD, EUR, RUB): ").upper()
            result = main_function(another_action, choice, None, None, currency_filter)

            if isinstance(result, list):
                for transaction in result:
                    print(transaction)
            else:
                print(result)
        elif choice == 'd':
            description_count = input("Введите количество описаний транзакций для вывода (целое число): ")
            result = main_function(another_action, choice, None, None, None, description_count)

            if isinstance(result, list):
                for description in result:
                    print(description)
            else:
                print(result)
        elif choice == 'k':
            result = main_function(another_action, choice)  # Вызываем без параметров
            if isinstance(result, list):
                for card_number in result:
                    print(card_number)
            else:
                print(result)
    else:
        print("Программа завершена.")
