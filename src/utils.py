import json
import os
from typing import List, Dict


def read_transactions(file_path: str) -> List[Dict]:
    """
    Читает JSON-файл и возвращает список словарей с данными о транзакциях.

    Аргументы:
        file_path (str): Путь до JSON-файла.

    Возвращает:
        List[Dict]: Список словарей с данными о транзакциях. Если файл пустой,
                   содержит не список или не найден, возвращает пустой список.
    """
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return []

    try:
        # Открываем файл и загружаем данные
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            # Проверяем, что данные являются списком
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, FileNotFoundError):
        # Если файл пустой или содержит некорректный JSON
        return []
