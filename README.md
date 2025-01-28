# Проект X

## Описание:

Проект X - это веб-приложение на Python для сортировки и маскировки данных счетов и карт.

## Установка:
```
- git clone https://github.com/Kaphytez/Projectgit
```
## Использование:

1. Откройте IDE. 
2. ПКМ по свободному месту возле кода, нажимаете "Run 'main'".
3. Эффективно получаете результат в виде сортировки 'state' и 'date'.

# Тестирование

Этот проект использует `pytest` для тестирования. Тесты организованы в папке `tests`.

## Модульное тестирование

### Основные компоненты:
* `test_main.py`: Содержит тесты для проверки `main_function` в файле `main.py`.
* `test_processing.py`: Содержит тесты для проверки функций фильтрации и сортировки в файле `processing.py`.
* `test_widget.py`: Содержит тесты для проверки функций форматирования и маскировки в файле `widget.py`.
* `test_masks.py`: Содержит тесты для проверки функций маскировки счетов и карт в файле `masks.py`.

### Подход к тестированию:
*   Использованы фикстуры: Фикстуры используются для мокирования ввода `input()` и для генерации тестовых данных, а также для параметризации тестов.
*   Параметризация тестов: Некоторые тесты используют параметризацию для тестирования различных наборов входных данных.
*   Изоляция: Тесты написаны таким образом, чтобы тестировать каждый модуль изолированно.

### Запуск тестов:
Для запуска тестов используйте команду:
pytest
