import csv
import json
import logging
import os
from typing import Dict, List, Optional

import pandas as pd

from src.decorators import log

# Настраиваем логер для этого модуля
logger = logging.getLogger(__name__)


@log
def read_transactions(file_path: str) -> List[Dict]:
    """
    Читает файл с транзакциями, автоматически определяя тип файла (JSON, CSV или Excel).
    Возвращает данные в едином формате.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    try:
        if file_ext == ".json":
            transactions = _read_transactions_json(file_path)
        elif file_ext == ".csv":
            transactions = _read_transactions_csv(file_path)
        elif file_ext == ".xlsx" or file_ext == ".xls":
            transactions = _read_transactions_excel(file_path)
        else:
            logger.error(f"Неподдерживаемый тип файла: {file_ext}")
            return []
        return transactions
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return []


def _read_transactions_json(file_path: str) -> List[Dict]:
    """Читает JSON-файл и возвращает список словарей с данными о транзакциях."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                logger.info(f"Успешно прочитано {len(data)} транзакций из JSON-файла: {file_path}")
                return data
            else:
                logger.error(f"Файл {file_path} не содержит список.")
                return []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.exception(f"Ошибка при чтении файла {file_path}: {e}")
        return []


def _read_transactions_csv(file_path: str) -> List[Dict]:
    """Читает CSV-файл с автоматическим определением разделителя и гибким маппингом полей."""
    transactions = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            sample = csvfile.read(2048)
            dialect = csv.Sniffer().sniff(sample)
            csvfile.seek(0)

            # Определение наличия заголовков и создание reader
            has_header = csv.Sniffer().has_header(sample)
            if has_header:
                reader = csv.DictReader(csvfile, delimiter=str(dialect.delimiter))
            else:
                # Обработка CSV без заголовков
                first_line = sample.splitlines()[0]
                delimiter = str(dialect.delimiter)
                fieldnames = [f"column_{i}" for i in range(len(first_line.split(delimiter)))]
                reader = csv.DictReader(csvfile, delimiter=delimiter, fieldnames=fieldnames)

            # Расширенный маппинг полей
            field_mapping = {
                'id': ['id', 'ID', 'идентификатор', 'column_0'],
                'state': ['state', 'статус', 'State', 'column_1'],
                'date': ['date', 'дата', 'Date', 'column_2'],
                'amount': ['amount', 'сумма', 'Amount', 'column_3'],
                'currency_code': ['currency_code', 'код_валюты', 'Currency Code', 'column_4'],
                'currency_name': ['currency_name', 'название_валюты', 'Currency Name', 'column_5'],
                'description': ['description', 'описание', 'Description', 'column_6'],
                'from': ['from', 'отправитель', 'From', 'column_7'],
                'to': ['to', 'получатель', 'To', 'column_8']
            }

            for row in reader:
                if not isinstance(row, dict):
                    logger.warning(f"Пропуск строки {reader.line_num}: неверный формат данных ({type(row)})")
                    continue

                # Маппинг полей с явными проверками
                mapped_data: Dict[str, Optional[str]] = {}
                for target_field, possible_fields in field_mapping.items():
                    value = None
                    for field in possible_fields:
                        if field in row and row[field] is not None:
                            value = str(row[field]).strip()
                            break
                    mapped_data[target_field] = value

                # Валидация обязательных полей
                required_fields = ['id', 'date', 'amount']
                if any(mapped_data.get(field) in (None, '') for field in required_fields):
                    logger.warning(f"Пропуск строки {reader.line_num}: отсутствуют обязательные поля")
                    continue

                try:
                    # Явные проверки типов
                    assert mapped_data['id'] is not None, "ID отсутствует"
                    assert mapped_data['date'] is not None, "Дата отсутствует"
                    assert mapped_data['amount'] is not None, "Сумма отсутствует"

                    transaction = {
                        "id": int(mapped_data['id']),
                        "state": mapped_data.get('state', 'UNKNOWN'),
                        "date": parse_date(mapped_data['date']),
                        "operationAmount": {
                            "amount": float(mapped_data['amount'].replace(',', '.')),
                            "currency": {
                                "name": mapped_data.get('currency_name', 'UNKNOWN'),
                                "code": mapped_data.get('currency_code', 'UNKNOWN')
                            }
                        },
                        "description": mapped_data.get('description', ''),
                        "from": mapped_data.get('from', ''),
                        "to": mapped_data.get('to', '')
                    }
                    transactions.append(transaction)
                except (ValueError, AssertionError) as e:
                    logger.error(f"Ошибка в строке {reader.line_num}: {str(e)}")
                except Exception as e:
                    logger.exception(f"Критическая ошибка в строке {reader.line_num}: {str(e)}")

            logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV: {file_path}")
            return transactions
    except Exception as e:
        logger.exception(f"Ошибка при чтении CSV: {str(e)}")
        return []


def _read_transactions_excel(file_path: str) -> List[Dict]:
    """Читает Excel-файл с проверкой структуры и преобразованием даты."""
    try:
        df = pd.read_excel(file_path)

        # Проверка обязательных колонок
        required_columns = {'id', 'date', 'amount'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            logger.error(f"Отсутствуют обязательные колонки: {', '.join(missing)}")
            return []

        transactions = []
        for _, row in df.iterrows():
            try:
                # Преобразование даты в ISO-формат
                date_str = parse_date(str(row['date'])) if pd.notna(row['date']) else ''

                transaction = {
                    "id": int(row['id']),
                    "state": str(row.get('state', 'UNKNOWN')),
                    "date": date_str,
                    "operationAmount": {
                        "amount": float(row['amount']),
                        "currency": {
                            "name": str(row.get('currency_name', 'UNKNOWN')),
                            "code": str(row.get('currency_code', 'UNKNOWN'))
                        }
                    },
                    "description": str(row.get('description', '')),
                    "from": str(row.get('from', '')),
                    "to": str(row.get('to', ''))
                }
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Пропуск строки {_}: {str(e)}")

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из Excel: {file_path}")
        return transactions
    except Exception as e:
        logger.exception(f"Ошибка при чтении Excel: {str(e)}")
        return []


def parse_date(date_str: str) -> str:
    """Универсальный парсинг даты с обработкой исключений."""
    try:
        return pd.to_datetime(date_str).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError, pd.errors.ParserError):
        # Унифицированное сообщение на русском
        error_message = f"Невозможно распознать формат даты: '{date_str}'"
        logger.warning(f"Ошибка преобразования даты '{date_str}': {error_message}")
        return date_str
