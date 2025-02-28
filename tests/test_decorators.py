import pytest
from src.decorators import log  # Импортируем декоратор из основного файла


# Пример функции, которая работает корректно
@log
def add(a, b):
    return a + b


# Пример функции, которая вызывает исключение
@log
def divide(a, b):
    return a / b


# Пример функции с ключевыми аргументами
@log
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


# Тесты
def test_add():
    """Тестируем функцию add с декоратором."""
    assert add(2, 3) == 5  # Проверяем, что функция работает корректно


def test_divide():
    """Тестируем функцию divide с декоратором."""
    with pytest.raises(ZeroDivisionError):  # Проверяем, что деление на ноль вызывает исключение
        divide(10, 0)


def test_greet():
    """Тестируем функцию greet с декоратором."""
    assert greet("Alice") == "Hello, Alice!"  # Проверяем стандартное приветствие
    assert greet("Bob", greeting="Hi") == "Hi, Bob!"  # Проверяем приветствие с кастомным текстом
