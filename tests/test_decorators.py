import os
import sys

from src.decorators import log

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_log_success(capsys):
    """
    Тестирует логирование успешного выполнения функции.
    """

    @log()
    def add(a, b):
        return a + b

    # Вызов функции
    result = add(2, 3)

    # Проверка результата
    assert result == 5

    # Перехват вывода в консоль
    captured = capsys.readouterr()

    # Проверка логов
    assert "add ok" in captured.out


def test_log_error(capsys):
    """
    Тестирует логирование ошибки при выполнении функции.
    """

    @log()
    def divide(a, b):
        return a / b

    # Вызов функции с ошибкой
    try:
        divide(10, 0)
    except ZeroDivisionError:
        pass

    # Перехват вывода в консоль
    captured = capsys.readouterr()

    # Проверка логов
    assert "divide error: ZeroDivisionError" in captured.out
    assert "Inputs: (10, 0)" in captured.out


def test_log_to_file(log_file):
    """
    Тестирует логирование в файл.
    """

    @log(filename=log_file)
    def multiply(a, b):
        return a * b

    # Вызов функции
    result = multiply(3, 4)

    # Проверка результата
    assert result == 12

    # Чтение файла с логами
    with open(log_file, "r") as f:
        log_content = f.read()

    # Проверка логов
    assert "multiply ok" in log_content


def test_log_error_to_file(log_file):
    """
    Тестирует логирование ошибки в файл.
    """

    @log(filename=log_file)
    def divide(a, b):
        return a / b

    # Вызов функции с ошибкой
    try:
        divide(10, 0)
    except ZeroDivisionError:
        pass

    # Чтение файла с логами
    with open(log_file, "r") as f:
        log_content = f.read()

    # Проверка логов
    assert "divide error: ZeroDivisionError" in log_content
    assert "Inputs: (10, 0)" in log_content
