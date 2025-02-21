import json

from src.external_api import (convert_transaction_amount_to_rub,
                              get_exchange_rate)
from src.generators import card_number_generator, transaction_descriptions
from src.masks import get_mask_account, get_mask_card_number
from src.processing import sort_by_date
from src.utils import read_transactions
from src.widget import get_date, mask_account_card


def display_transactions(transactions):
    """Функция для отображения транзакций."""
    for transaction in transactions:
        # Проверяем, что транзакция содержит необходимые данные
        if not transaction or "date" not in transaction:
            continue  # Пропускаем пустые или некорректные записи

        # Получаем ID, дату и статус транзакции
        transaction_id = transaction.get("id", "N/A")
        date = get_date(transaction.get("date", ""))
        description = transaction.get("description", "No description")
        state = transaction.get("state", "N/A")

        # Маскируем номера карт и счетов
        from_account = transaction.get("from", "")
        if from_account:
            from_account = mask_account_card(from_account)
        to_account = mask_account_card(transaction.get("to", ""))

        amount = transaction.get("operationAmount", {}).get("amount", "N/A")
        currency = transaction.get("operationAmount", {}).get("currency", {}).get("code", "N/A")

        # Конвертируем сумму в рубли, если валюта не RUB
        if currency != "RUB":
            amount_in_rub = convert_transaction_amount_to_rub(transaction)
            if amount_in_rub is not None:
                amount_in_rub = round(amount_in_rub, 2)  # Округляем до 2 знаков после запятой_
                amount_info = f"{amount} {currency} (~{amount_in_rub} RUB)"
            else:
                amount_info = f"{amount} {currency} (Ошибка конвертации)"
        else:
            amount_info = f"{amount} {currency}"

        # Выводим информацию о транзакции
        print(f"ID: {transaction_id}, Дата: {date}, Статус: {state}")
        print(f"Описание: {description}")
        if from_account:
            print(f"{from_account} -> {to_account}")
        else:
            print(f"Счет открыт -> {to_account}")
        print(f"Сумма: {amount_info}")
        print()


def filter_and_display_transactions(transactions):
    """Функция для фильтрации и отображения транзакций."""
    currency = input("Введите код валюты для фильтрации (например, USD, RUB): ").strip().upper()
    filtered_transactions = [
        t for t in transactions
        if t and t.get("operationAmount", {}).get("currency", {}).get("code") == currency
    ]
    display_transactions(filtered_transactions)


def generate_card_numbers():
    """Функция для генерации номеров карт."""
    start = int(input("Введите начальный номер карты: "))
    stop = int(input("Введите конечный номер карты: "))
    for card_number in card_number_generator(start, stop):
        print(card_number)


def display_transaction_descriptions(transactions):
    """
    Выводит описания транзакций. Если описание отсутствует, выводит "No description".
    :param transactions: Список транзакций.
    """
    for transaction in transactions:  # Перебираем каждую транзакцию

        # Получаем описание или "No description", если его нет
        description = transaction.get("description", "No description")
        print(description)  # Выводим описание


def display_exchange_rate():
    """Функция для запроса и отображения курса валюты."""
    from_currency = input("Введите код валюты, курс которой хотите узнать (например, USD): ").strip().upper()
    to_currency = input(
        "Введите код валюты, в которую хотите конвертировать (например, RUB, EUR, по умолчанию RUB): ").strip().upper() or "RUB"

    exchange_rate = get_exchange_rate(from_currency, to_currency)

    if exchange_rate is not None:
        print(f"Текущий курс {from_currency} к {to_currency}: {exchange_rate}")
    else:
        print("Не удалось получить курс обмена.")


def main():
    # Путь к файлу с данными
    file_path = "data/operations.json"

    # Чтение транзакций из файла
    transactions = read_transactions(file_path)

    # Фильтруем пустые или некорректные записи
    valid_transactions = [t for t in transactions if t and "date" in t]

    while True:
        print("\nВыберите функцию:")
        print("1. Вывести последние 5 транзакций (отсортированных по дате)")
        print("2. Фильтровать транзакции по валюте")
        print("3. Сгенерировать номера карт")
        print("4. Вывести описания всех транзакций")
        print("5. Узнать текущий курс валюты")
        print("6. Выйти")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            # Сортировка транзакций по дате (по убыванию)
            sorted_transactions = sort_by_date(valid_transactions, ascending=False)
            # Вывод последних 5 транзакций
            display_transactions(sorted_transactions[:5])

        elif choice == "2":
            filter_and_display_transactions(valid_transactions)

        elif choice == "3":
            generate_card_numbers()

        elif choice == "4":
            display_transaction_descriptions(valid_transactions)

        elif choice == "5":
            display_exchange_rate()

        elif choice == "6":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")


if __name__ == "__main__":
    main()
