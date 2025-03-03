import csv
import logging
import pandas as pd
from typing import Dict, List, Union, cast


logger = logging.getLogger(__name__)


def read_transactions_csv(file_path: str) -> List[Dict[str, Union[str, int, float]]]:
    """
    Читает CSV-файл и возвращает список словарей с данными о транзакциях.
    """
    transactions: List[Dict[str, Union[str, int, float]]] = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # Явно приводим тип row к Dict[str, str]
                row_dict: Dict[str, str] = cast(Dict[str, str], row)

                # Преобразуем значения к нужным типам
                new_row: Dict[str, Union[str, int, float]] = {}
                try:
                    new_row['id'] = int(row_dict['id'])
                except (ValueError, KeyError):
                    new_row['id'] = row_dict.get('id',
                                                 'N/A')
                    logger.warning(f"Не удалось преобразовать 'id' в int в строке: {row_dict}")

                try:
                    new_row['amount'] = float(row_dict['amount'])
                except (ValueError, KeyError):
                    new_row['amount'] = row_dict.get('amount',
                                                     'N/A')
                    logger.warning(f"Не удалось преобразовать 'amount' в float в строке: {row_dict}")

                new_row['state'] = row_dict.get('state', 'N/A')  # Оставляем другие значения из файла
                new_row['date'] = row_dict.get('date', 'N/A')
                new_row['currency_name'] = row_dict.get('currency_name', 'N/A')
                new_row['currency_code'] = row_dict.get('currency_code', 'N/A')
                new_row['from'] = row_dict.get('from', 'N/A')
                new_row['to'] = row_dict.get('to', 'N/A')
                new_row['description'] = row_dict.get('description', 'N/A')
                transactions.append(new_row)

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV-файла: {file_path}")
        return transactions
    except FileNotFoundError:
        logger.error(f"Ошибка: CSV-файл не найден по пути: {file_path}")
        return []
    except Exception as e:
        logger.exception(f"Ошибка: Произошла ошибка при чтении CSV-файла: {e}")
        return []


def read_transactions_excel(file_path: str) -> List[Dict]:
    """
    Читает Excel-файл и возвращает список словарей с данными о транзакциях.
    """
    try:
        df = pd.read_excel(file_path)
        transactions: List[Dict] = df.to_dict(orient='records')
        logger.info(f"Successfully read {len(transactions)} transactions from Excel file: {file_path}")
        return transactions
    except FileNotFoundError:
        logger.error(f"Error: Excel file not found at path: {file_path}")
        return []
    except Exception as e:
        logger.exception(f"Error: An error occurred while reading the Excel file: {e}")
        return []
