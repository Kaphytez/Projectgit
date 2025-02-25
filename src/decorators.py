import functools
from datetime import datetime


def log(filename=None):
    """
    Декоратор для логирования вызовов функций.

    Аргументы:
        filename (str, optional): Имя файла для записи логов. Если не указано, логи выводятся в консоль.

    Возвращает:
        function: Декорированную функцию с логированием.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешное выполнение
                log_message = f"{datetime.now()} - {func.__name__} ok\n"
                if filename:
                    with open(filename, "a") as f:
                        f.write(log_message)
                else:
                    print(log_message, end="")

                return result

            except Exception as e:
                # Логируем ошибку
                error_message = (
                    f"{datetime.now()} - {func.__name__} error: {type(e).__name__}. "
                    f"Inputs: {args}, {kwargs}\n"
                )
                if filename:
                    with open(filename, "a") as f:
                        f.write(error_message)
                else:
                    print(error_message, end="")
                raise  # Повторно вызываем исключение

        return wrapper

    return decorator


# Пример использования декоратора
if __name__ == "__main__":
    # Логирование в файл
    @log(filename="mylog.txt")
    def my_function(x, y):
        """
        Складывает два числа.

        Аргументы:
            x (int или float): Первое число.
            y (int или float): Второе число.

        Возвращает:
            int или float: Результат сложения x и y.
        """
        return x + y

    # Логирование в консоль
    @log()
    def divide(a, b):
        """
        Делит число a на число b.

        Аргументы:
            a (int или float): Делимое.
            b (int или float): Делитель.

        Возвращает:
            float: Результат деления a на b.

        Исключения:
            ZeroDivisionError: Если b равно 0.
        """
        return a / b

    # Успешное выполнение
    my_function(1, 2)

    # Ошибка (деление на ноль)
    try:
        divide(10, 0)
    except Exception:
        pass  # Игнорируем ошибку, чтобы продолжить выполнение
