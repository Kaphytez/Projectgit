import logging
import os
from datetime import datetime
# Импортируем нужные функции из соответствующих модулей

from src.masks import get_mask_account, get_mask_card_number
from src.processing import (  # Оставляем только используемые функции обработки
    filter_by_currency, filter_by_description_keyword,
    filter_by_state, sort_by_date
)
from src.utils import read_transactions

# --- 1. Создание директории для логов ---
LOG_DIR = "logs"
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError as e:
    print(f"Не удалось создать директорию '{LOG_DIR}': {e}. Выход.")
    exit(1)

# --- 2. Настройка Логирования ---
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def setup_logger(name, log_file_name, level=logging.INFO):
    """Настраивает и возвращает логгер для записи в указанный файл."""
    log_path = os.path.join(LOG_DIR, log_file_name)
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == file_handler.baseFilename for h in
               logger_instance.handlers):
        logger_instance.addHandler(file_handler)
    return logger_instance


# Настраиваем логгеры (можно оставить как есть)
utils_logger = setup_logger('src.utils', 'utils.log')
processing_logger = setup_logger('src.processing', 'processing.log')
masks_logger = setup_logger('src.masks', 'masks.log')
external_api_logger = setup_logger('src.external_api', 'external_api.log')
logger = setup_logger('__main__', 'main.log')


# --- 3. Вспомогательные функции для ввода ---

def get_validated_input(prompt: str, valid_options: set, case_sensitive: bool = False) -> str:
    """Запрашивает ввод у пользователя, пока он не введет один из valid_options."""
    while True:
        user_input = input(prompt).strip()
        processed_input = user_input if case_sensitive else user_input.upper()

        if processed_input in valid_options:
            return processed_input  # Возвращаем обработанный ввод (обычно upper)
        else:
            print(f"Некорректный ввод '{user_input}'. Доступные опции: {', '.join(valid_options)}")
            logger.warning(f"Некорректный ввод от пользователя: '{user_input}'. Ожидалось: {valid_options}")


def get_yes_no_input(prompt: str) -> bool:
    """Получает ответ Да/Нет от пользователя."""
    # Приводим "да" к True, "нет" к False
    valid_options = {"ДА", "НЕТ"}
    response = get_validated_input(f"{prompt} (Да/Нет): ", valid_options)
    return response == "ДА"


# --- 4. Обновленная функция вывода транзакций ---

def display_transactions_final(transactions_to_display):
    """Выводит информацию о транзакциях в формате, указанном в ТЗ."""
    if not transactions_to_display:
        print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
        logger.info("Итоговая выборка транзакций пуста.")
        return

    print(f"\nВсего банковских операций в выборке: {len(transactions_to_display)}")
    logger.info(f"Вывод {len(transactions_to_display)} итоговых транзакций.")

    for transaction in transactions_to_display:
        try:
            # Дата
            date_str = "Дата N/A"
            try:
                date_raw = transaction.get("date", "")
                if date_raw:
                    date_str = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y")
            except (ValueError, TypeError) as date_err:
                logger.error(
                    f"Ошибка форматирования даты '{transaction.get('date')}'"
                    f" для ID {transaction.get('id')}: {date_err}")
                date_str = f"Дата ({transaction.get('date')})"  # Показываем исходную дату при ошибке

            # Описание
            description = transaction.get("description", "Нет описания")

            # Откуда/Куда (маскирование)
            from_value = transaction.get("from", "")
            to_value = transaction.get("to", "")
            from_masked = get_mask_account(from_value) if "Счет" in from_value else get_mask_card_number(
                from_value) if from_value else ""
            to_masked = get_mask_account(to_value) if "Счет" in to_value else get_mask_card_number(
                to_value) if to_value else ""

            # Формирование строки "откуда -> куда"
            transaction_info = ""
            if from_masked and to_masked:
                transaction_info = f"{from_masked} -> {to_masked}"
            elif to_masked:  # Пополнение или открытие вклада
                # Если в описании "Открытие вклада", используем только "куда"
                if "открытие вклада" not in description.lower():
                    transaction_info = f"-> {to_masked}"  # Используем пустую строку как источник
                else:
                    transaction_info = to_masked  # Только счет для вклада
            elif from_masked:  # Перевод куда-то без указания
                transaction_info = f"{from_masked} -> ????"

            # Сумма
            amount = "Сумма N/A"
            currency = ""
            op_amount_info = transaction.get('operationAmount', {})
            if op_amount_info:
                amount_val = op_amount_info.get('amount')
                currency_code = op_amount_info.get('currency', {}).get('code')
                if amount_val is not None and currency_code:
                    try:
                        amount = f"{float(amount_val):.2f}"  # Форматируем до 2 знаков
                        currency = currency_code
                    except (ValueError, TypeError):
                        amount = f"Сумма ({amount_val})"  # Исходное значение при ошибке
                        currency = currency_code if currency_code else ""

            # Вывод
            print(f"\n{date_str} {description}")
            if transaction_info:  # Выводим строку from/to, если она сформирована
                print(transaction_info)
            print(f"Сумма: {amount} {currency}".strip())  # Убираем лишний пробел, если валюты нет

        except Exception as ex:  # Оставляем Exception, но используем ex в логе
            # Используем logger.error с exc_info=True для traceback'а
            # и включаем 'ex' в сообщение, чтобы использовать переменную.
            logger.error(
                f"Критическая ошибка при обработке транзакции ID {transaction.get('id', 'N/A')}:"
                f" {ex}. Данные транзакции: {transaction}",
                exc_info=True  # Добавляет полный traceback в лог
            )
            print(
                f"\n! Ошибка обработки транзакции ID {transaction.get('id', 'N/A')}."
                f" См. {LOG_DIR}/main.log для деталей.")
        print("-" * 20)


# --- 5. Основная функция main (переписанная) ---
def main():
    """Главная функция, управляющая workflow приложения."""
    logger.info("Программа запущена (новый сценарий).")
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    # --- Выбор файла ---
    print("\nВыберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    file_choice = get_validated_input("Ваш выбор (1, 2 или 3): ", {"1", "2", "3"})

    file_path = ""
    file_type_msg = ""
    if file_choice == "1":
        # Путь к файлу по умолчанию или запросить у пользователя?
        # Используем стандартное имя в папке data, как в структуре проекта
        file_path = os.path.join("data", "operations.json")
        file_type_msg = "JSON-файл"
    elif file_choice == "2":
        file_path = os.path.join("data", "transactions.csv")
        file_type_msg = "CSV-файл"
    elif file_choice == "3":
        file_path = os.path.join("data", "transactions_excel.xlsx")
        file_type_msg = "XLSX-файл"

    print(f"\nДля обработки выбран {file_type_msg}.")
    logger.info(f"Выбран тип файла: {file_type_msg}, путь: {file_path}")

    # --- Чтение транзакций ---
    transactions = read_transactions(file_path)
    if not transactions:
        logger.error(f"Не удалось прочитать транзакции или файл пуст: {file_path}")
        print(f"Не удалось загрузить данные из {file_path}. Проверьте наличие файла и его формат. См. логи.")
        logger.info("Программа завершена из-за ошибки загрузки данных.")
        return

    # Фильтруем некорректные записи (без даты) ДО основной логики
    initial_count = len(transactions)
    transactions = [t for t in transactions if t and isinstance(t.get("date"), str) and t.get("date")]
    valid_count = len(transactions)
    if initial_count != valid_count:
        logger.warning(f"Исключено {initial_count - valid_count} транзакций из-за отсутствия/неверного формата даты.")

    if not transactions:
        logger.error("После проверки дат не осталось корректных транзакций.")
        print("В файле не найдено корректных транзакций с датами.")
        return

    logger.info(f"Загружено {valid_count} корректных транзакций.")

    # --- Фильтрация по статусу ---
    valid_statuses = {"EXECUTED", "CANCELED", "PENDING"}
    prompt_status = (f"\nВведите статус, по которому необходимо выполнить фильтрацию.\n"
                     f"Доступные для фильтровки статусы: {', '.join(sorted(list(valid_statuses)))}: ")
    chosen_status = get_validated_input(prompt_status, valid_statuses)

    transactions = filter_by_state(transactions, chosen_status)
    print(f"Операции отфильтрованы по статусу \"{chosen_status}\"")
    logger.info(f"Транзакции отфильтрованы по статусу: {chosen_status}. Осталось: {len(transactions)}")

    if not transactions:  # Если после фильтрации по статусу ничего не осталось
        display_transactions_final(transactions)  # Выведет сообщение "Не найдено..."
        return

    # --- Сортировка по дате ---
    if get_yes_no_input("\nОтсортировать операции по дате?"):
        sort_asc = get_yes_no_input("Отсортировать по возрастанию (Да) или по убыванию (Нет)?")
        direction_msg = "по возрастанию" if sort_asc else "по убыванию"
        print(f"Сортировка по дате ({direction_msg}).")
        transactions = sort_by_date(transactions, ascending=sort_asc)
        logger.info(f"Транзакции отсортированы по дате ({direction_msg}).")

    # --- Фильтрация по рублевым транзакциям ---
    if get_yes_no_input("\nВыводить только рублевые транзакции?"):
        transactions = list(filter_by_currency(transactions, "RUB"))
        print("Отфильтрованы только рублевые транзакции.")
        logger.info(f"Отфильтрованы рублевые транзакции. Осталось: {len(transactions)}")
        if not transactions:
            display_transactions_final(transactions)
            return

    # --- Фильтрация по слову в описании ---
    if get_yes_no_input("\nОтфильтровать список транзакций по определенному слову в описании?"):
        keyword = input("Введите слово для поиска в описании: ").strip()
        if keyword:
            transactions = list(filter_by_description_keyword(transactions, keyword))
            print(f"Отфильтрованы транзакции по слову '{keyword}'.")
            logger.info(f"Отфильтрованы транзакции по ключевому слову '{keyword}'. Осталось: {len(transactions)}")
            if not transactions:
                display_transactions_final(transactions)
                return
        else:
            print("Ключевое слово не введено, фильтрация по описанию пропущена.")
            logger.info("Фильтрация по описанию пропущена (пустое слово).")

    # --- Вывод итогового списка ---
    print("\nРаспечатываю итоговый список транзакций...")
    display_transactions_final(transactions)

    logger.info("Программа успешно завершена (новый сценарий).")


# --- 6. Точка входа ---
if __name__ == "__main__":
    # Настройка логирования выполнена в начале файла
    main()
