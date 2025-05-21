import functools
import logging

# Получаем логер для этого модуля
logger = logging.getLogger(__name__)


def log(func):
    """
    Декоратор для логирования вызовов функций.

    Логирует информацию о вызове функции, ее успешном завершении
    или возникновении исключения.

    Args:
        func: Функция, которую нужно задекорировать.

    Returns:
        function: Декорированная функция с логированием.
    """

    @functools.wraps(func)  # 2. Сохраняем метаданные оригинальной функции
    def wrapper(*args, **kwargs):
        # 3. Логируем сам факт вызова (используя логгер модуля 'src.decorators')
        # Можно добавить сюда логирование аргументов, если нужно, например, на уровне DEBUG:
        # logger.debug(f"Вызов {func.__name__} с args: {args}, kwargs: {kwargs}")
        logger.info(f"Вызвана функция {func.__name__}")

        try:
            # 4. Выполняем оригинальную функцию
            result = func(*args, **kwargs)

            # 5. Логируем успешное выполнение
            logger.info(f"Функция {func.__name__} успешно завершена.")
            # Можно логировать результат (если он не слишком большой и это полезно):
            # logger.debug(f"{func.__name__} вернула: {result}")

            return result

        except Exception as e:
            # 6. Логируем ошибку с деталями и traceback'ом
            logger.error(
                f"Ошибка в функции {func.__name__} при вызове с args: {args}, kwargs: {kwargs}. Ошибка: {e}",
                exc_info=True  # Добавляет traceback (стек вызовов) в лог-сообщение
            )
            # 7. Важно: повторно вызываем исключение, чтобы декоратор
            #    не "проглотил" ошибку и не изменил поведение программы.
            raise

    return wrapper

