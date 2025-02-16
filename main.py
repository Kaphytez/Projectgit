import json
from src.utils import read_transactions
from src.processing import sort_by_date
from src.widget import get_date, mask_account_card
from src.generators import transaction_descriptions, card_number_generator
from src.masks import get_mask_account, get_mask_card_number


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
        from_account = mask_account_card(transaction.get("from", ""))
        to_account = mask_account_card(transaction.get("to", ""))

        amount = transaction.get("operationAmount", {}).get("amount", "N/A")
        currency = transaction.get("operationAmount", {}).get("currency", {}).get("code", "N/A")

        # Выводим информацию о транзакции
        print(f"ID: {transaction_id}, Дата: {date}, Статус: {state}")
        print(f"Описание: {description}")
        if from_account:
            print(f"{from_account} -> {to_account}")
        else:
            print(f"Счет открыт -> {to_account}")
        print(f"Сумма: {amount} {currency}")
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
    """Функция для отображения описаний транзакций."""
    for description in transaction_descriptions(transactions):
        print(description)


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
        print("5. Выйти")

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
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")


if __name__ == "__main__":
    main()
