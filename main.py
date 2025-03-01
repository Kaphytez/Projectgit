import logging
import os
from datetime import datetime

from src.external_api import (convert_transaction_amount_to_rub,
                              get_exchange_rate)
from src.generators import card_number_generator
from src.masks import get_mask_account, get_mask_card_number
from src.processing import sort_by_date
from src.utils import read_transactions


def display_transactions(transactions):
    """Выводит информацию о транзакциях."""
    if not transactions:
        return  # Exit early if transactions is None or empty

    for transaction in transactions:
        transaction_date = datetime.strptime(transaction["date"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        description = transaction.get("description", "No description")  # Safe access

        from_value = transaction.get("from", "")  # "" - значение по умолчанию
        to_value = transaction.get("to", "")

        from_account = ""
        to_account = ""

        # Определяем, что маскировать (счет или карту) для отправителя
        from_type = "Счет"  # Значение по умолчанию
        from_name = ""  # Название карты (Visa, MasterCard и т.д.)
        if from_value:
            if from_value.startswith("Счет"):
                from_account = get_mask_account(from_value)
            else:
                from_account = get_mask_card_number(from_value)
                from_type = "Карта"
                # Извлекаем название карты
                from_name = from_value.split()[0]

        # Определяем, что маскировать (счет или карту) для получателя
        to_type = "Счет"  # Значение по умолчанию
        to_name = ""  # Название карты (Visa, MasterCard и т.д.)
        if to_value:
            if to_value.startswith("Счет"):
                to_account = get_mask_account(to_value)
            else:
                to_account = get_mask_card_number(to_value)
                to_type = "Карта"
                # Извлекаем название карты
                to_name = to_value.split()[0]

        if "from" in transaction and "to" in transaction:
            transaction_info = f"{from_type} {from_name} {from_account} -> {to_type} {to_name} {to_account}"
        elif "to" in transaction:
            transaction_info = f"{to_type} {to_name} открыт -> {to_account}"  # Только получатель
        elif "from" in transaction:
            transaction_info = f"{from_type} {from_name} {from_account} -> Счет открыт"  # Только отправитель
        else:
            transaction_info = "Счет открыт -> "  # Нет информации

        amount_in_rub = convert_transaction_amount_to_rub(transaction)

        if (amount_in_rub is not None
                and "operationAmount" in transaction
                and "currency" in transaction["operationAmount"]):
            currency_code = transaction["operationAmount"]["currency"]["code"]
            amount_str = f"{amount_in_rub:.2f} {currency_code}"
        else:
            amount_str = "N/A N/A"

        print(f"ID: {transaction['id']}, Дата: {transaction_date}, Статус: {transaction['state']}\n"
              f"Описание: {description}\n"
              f"{transaction_info}\n"
              f"Сумма: {amount_str}\n\n")


def filter_and_display_transactions(transactions):
    """Функция для фильтрации и отображения транзакций."""
    currency = input("Введите код валюты для фильтрации (например, USD, RUB): ").strip().upper()
    filtered_transactions = [
        t for t in transactions
        if t and t.get("operationAmount", {}).get("currency", {}).get("code") == currency
    ]
    return filtered_transactions


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
    """Выводит текущий курс обмена валюты."""
    from_currency = input("Введите код валюты, курс которой хотите узнать (например, USD): ").upper()
    to_currency = input("Введите код валюты, в которую хотите конвертировать (например, RUB): ").upper()

    exchange_rate = get_exchange_rate(from_currency, to_currency)

    if exchange_rate is not None:
        print(f"Текущий курс {from_currency} к {to_currency}: {exchange_rate}")
    else:
        print("Не удалось получить курс обмена.")


if not os.path.exists("logs"):
    os.makedirs("logs")

# Настраиваем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Функция для настройки логирования в файл
def setup_logger(name, log_file, level=logging.INFO):
    """Создает логер для записи в файл."""
    handler = logging.FileHandler(log_file, mode='w')  # Режим 'w' для перезаписи
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# Настраиваем логеры для masks.py и utils.py
masks_logger = setup_logger("src.masks", "logs/masks.log")
utils_logger = setup_logger("src.utils", "logs/utils.log")


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
            a = filter_and_display_transactions(valid_transactions)
            display_transactions(a)

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
