import json
import logging
import os
from typing import Dict, List

# Настраиваем логер для этого модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Уровень логирования по умолчанию


def read_transactions(file_path: str) -> List[Dict]:
    """
    Читает JSON-файл и возвращает список словарей с данными о транзакциях.

    Аргументы:
        file_path (str): Путь до JSON-файла.

    Возвращает:
        List[Dict]: Список словарей с данными о транзакциях. Если файл пустой,
                   содержит не список или не найден, возвращает пустой список.
    """
    logger.debug(f"Reading transactions from file: {file_path}")  # Логируем путь к файлу
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")  # Логируем ошибку
        return []

    try:
        # Открываем файл и загружаем данные
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.debug(f"Data read from file: {data}")  # Логируем прочитанные данные

            # Проверяем, что данные являются списком
            if isinstance(data, list):
                logger.info(f"Successfully read {len(data)} transactions from {file_path}")  # Логируем успех
                return data
            else:
                logger.warning(f"File {file_path} does not contain a list.")  # Логируем предупреждение
                return []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        # Если файл пустой или содержит некорректный JSON
        logger.exception(f"Error reading file {file_path}: {e}")  # Логируем исключение
        return []
