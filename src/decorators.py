import functools
import logging
import os

# Создаем директорию для логов, если она не существует
os.makedirs("logs", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="logs/test.log",
    filemode="w"
)

# Получаем логер для этого модуля
logger = logging.getLogger(__name__)


def log(func):
    """
    Декоратор для логирования вызовов функций.

    Аргументы:
        func: Функция, которую нужно задекорировать.

    Возвращает:
        function: Декорированную функцию с логированием.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Вызвана функция {func.__name__}")

        try:
            # Выполняем функцию
            result = func(*args, **kwargs)

            # Логируем успешное выполнение
            logger.info(f"{func.__name__} ok.")

            return result

        except Exception as e:
            # Логируем ошибку
            logger.error(f"{func.__name__} error. Inputs: {args}, {kwargs}. Error: {str(e)}")
            raise  # Повторно вызываем исключение

    return wrapper
