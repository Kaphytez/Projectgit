import logging
import os
from datetime import datetime

from src.external_api import (convert_transaction_amount_to_rub,
                              get_exchange_rate)
from src.generators import card_number_generator
from src.masks import get_mask_account, get_mask_card_number
from src.processing import sort_by_date
# from src.utils import read_transactions #Удаляем этот импорт
from src.file_readers import read_transactions_csv, read_transactions_excel

logger = logging.getLogger(__name__)


def display_transactions(transactions):
    """Выводит информацию о транзакциях."""
    if not transactions:
        print("No transactions to display.")
        return

    for transaction in transactions:
        try:
            # Check for basic keys
            if not all(key in transaction for key in ['id', 'state', 'date', 'amount', 'currency_code']):
                print(f"Skipping transaction with missing keys: {transaction}")
                logger.warning(f"Skipping transaction with missing keys: {transaction}")
                continue

            transaction_id = transaction['id']
            transaction_state = transaction['state']
            transaction_date = transaction['date']

            # Format date
            try:
                transaction_date = datetime.strptime(transaction_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y")
            except ValueError:
                logger.error(f"Invalid date format: {transaction_date}")
                transaction_date = "N/A"  # Set to "N/A" for invalid formats

            description = transaction.get('description', "No description")  # Provide a default value

            from_value = transaction.get('from', "")
            to_value = transaction.get('to', "")

            from_account = ""
            to_account = ""
            from_type = ""  # Тип карты или счет
            to_type = ""  # Тип карты или счет

            # Определяем, что маскировать (счет или карту) для отправителя
            if from_value:
                if "Счет" in from_value:
                    from_account = get_mask_account(from_value)
                    from_type = "Счет"
                else:
                    from_account = get_mask_card_number(from_value)
                    from_type = "Карта"

            # Определяем, что маскировать (счет или карту) для получателя
            if to_value:
                if "Счет" in to_value:
                    to_account = get_mask_account(to_value)
                    to_type = "Счет"
                else:
                    to_account = get_mask_card_number(to_value)
                    to_type = "Карта"

            transaction_info = f"{from_type} {from_account} -> {to_type} {to_account}" if from_value and to_value else \
                f"Счет открыт -> {to_account}" if to_value else \
                f"{from_type} {from_account} -> Счет открыт" if from_value else "Счет открыт ->"

            amount = transaction.get("amount")
            currency_code = transaction.get("currency_code")
            amount_in_rub = convert_transaction_amount_to_rub(transaction)  # Новый код

            # Анализ
            if amount_in_rub is not None:
                amount_str = f"{amount_in_rub:.2f} RUB"  # Сумма в рублях
            else:
                amount_str = f"{amount} {currency_code}"
                logger.warning(
                    # Текст об ошибке
                    f"Не удалось конвертировать сумму для транзакции {transaction_id}. Отображается исходная сумма.")

            print(f"ID: {transaction_id}, Дата: {transaction_date}, Статус: {transaction_state}\n"
                  f"Описание: {description}\n"
                  f"{transaction_info}\n"
                  f"Сумма: {amount_str}\n\n")

        except Exception as e:
            logger.error(f"Error processing transaction: {e}. Transaction: {transaction}")
            print("Error processing transaction, see the log for more details.")


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
    logger = logging.getLogger(name)  # Добавили
    logger.setLevel(level)
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')  # Режим 'w' для перезаписи
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Настраиваем логеры для masks.py и utils.py
masks_logger = setup_logger("src.masks", "logs/masks.log")
utils_logger = setup_logger("src.utils", "logs/utils.log")


def main():
    logger.info("Starting main function")  # Начало работы функции main

    # Путь к файлу с данными
    file_path = input("Введите путь к файлу с транзакциями: ")
    logger.debug(f"User provided file path: {file_path}")  # Логируем путь к файлу

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        print("Файл не найден.")
        return  # Exit early if the file doesn't exist

    # Определяем тип файла по расширению
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".csv":
        transactions_data = read_transactions_csv(file_path)
        logger.info("Transactions read from file {type}".format(type="CSV"))
    elif file_ext == ".xlsx" or file_ext == ".xls":
        transactions_data = read_transactions_excel(file_path)
        logger.info("Transactions read from file {type}".format(type="Excel"))
    else:
        logger.error(f"Unsupported file type: {file_ext}")
        print("Неподдерживаемый тип файла")
        return

    # Используйте то же имя переменной, и код не будет работать
    # valid_transactions = [t for t in transactions if t and "date" in t]
    valid_transactions = [t for t in transactions_data if t and "date" in t]
    logger.info("Valid transactions selected")

    while True:
        print("\nВыберите функцию:")
        print("1. Вывести последние 5 транзакций (отсортированных по дате)")
        print("2. Фильтровать транзакции по валюте")
        print("3. Сгенерировать номера карт")
        print("4. Вывести описания всех транзакций")
        print("5. Узнать текущий курс валюты")
        print("6. Выйти")

        choice = input("Ваш выбор: ").strip()
        logger.debug(f"User selected option: {choice}")

        if choice == "1":
            logger.info("Executing option 1: Display last 5 transactions")
            # Сортировка транзакций по дате (по убыванию)
            sorted_transactions = sort_by_date(valid_transactions, ascending=False)
            # Вывод последних 5 транзакций
            display_transactions(sorted_transactions[:5])

        elif choice == "2":
            logger.info("Executing option 2: Filter transactions by currency")
            # a = filter_and_display_transactions(valid_transactions)
            display_transactions(filter_and_display_transactions(valid_transactions))

        elif choice == "3":
            logger.info("Executing option 3: Generate card numbers")
            generate_card_numbers()

        elif choice == "4":
            logger.info("Executing option 4: Display transaction descriptions")
            display_transaction_descriptions(valid_transactions)

        elif choice == "5":
            logger.info("Executing option 5: Display exchange rate")
            display_exchange_rate()

        elif choice == "6":
            print("Выход из программы.")
            logger.info("Exiting program")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")
            logger.warning(f"Invalid choice selected: {choice}")

        logger.info("Operation complete. Waiting for next input.")

    logger.info("Program finished")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename="logs/main.log",
        filemode="w"
    )
    main()
