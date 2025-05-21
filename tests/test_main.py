import os
import sys
from datetime import datetime
from io import StringIO
from unittest.mock import call, patch  # Добавляем call для проверки логов

import pytest
from pytest_mock import \
    MockerFixture  # Используем MockerFixture для лучшей типизации

# Импортируем ТОЛЬКО то, что есть в НОВОМ main.py
from main import (  # setup_logger не тестируем напрямую, т.к. это инфраструктура
    display_transactions_final, get_validated_input, get_yes_no_input, main)

# Добавляем путь к src, если запускаем тесты из папки tests
# Убедись, что путь корректен для твоей структуры
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



# --- Тесты для вспомогательных функций ввода ---

@pytest.mark.parametrize("inputs, valid_options, expected_output, expected_print_parts", [
    (["EXECUTED"], {"EXECUTED", "CANCELED"}, "EXECUTED", []),  # Валидный ввод
    (["executed"], {"EXECUTED", "CANCELED"}, "EXECUTED", []),  # Валидный ввод, другой регистр
    (["invalid", "CANCELED"], {"EXECUTED", "CANCELED"}, "CANCELED",  # Невалидный, потом валидный
     # ИЗМЕНЕНО: Передаем части сообщения для проверки
     {"invalid_input": "invalid", "options": {"EXECUTED", "CANCELED"}}),
    (["Да"], {"ДА", "НЕТ"}, "ДА", []),  # Для get_yes_no_input
    (["нет"], {"ДА", "НЕТ"}, "НЕТ", []),  # Для get_yes_no_input
])
def test_get_validated_input(inputs, valid_options, expected_output, expected_print_parts, mocker, capsys, mock_input):
    """Тестирует get_validated_input с разными сценариями ввода."""
    mock_input = mocker.patch('builtins.input', side_effect=inputs)
    mock_logger_warning = mocker.patch('main.logger.warning')

    result = get_validated_input("Тестовый ввод: ", valid_options)

    assert result == expected_output
    assert mock_input.call_count == len(inputs)

    captured = capsys.readouterr()

    # ИЗМЕНЕНО: Проверяем наличие частей сообщения, если ожидается ошибка
    if expected_print_parts:
        # Ожидаем только одно сообщение об ошибке для этого теста
        invalid_input = expected_print_parts["invalid_input"]
        options_to_check = expected_print_parts["options"]

        assert f"Некорректный ввод '{invalid_input}'" in captured.out
        assert "Доступные опции:" in captured.out
        # Проверяем наличие всех ожидаемых опций в выводе
        for option in options_to_check:
            assert option in captured.out
        # Проверяем логирование
        mock_logger_warning.assert_called_once()
    else:
        # Если ошибки не ожидалось, вывод должен быть пуст
        assert captured.out == ""
        mock_logger_warning.assert_not_called()


@pytest.mark.parametrize("inputs, expected_result", [
    (["Да"], True),
    (["ДА"], True),
    (["да"], True),
    (["Нет"], False),
    (["НЕТ"], False),
    (["нет"], False),
    (["Неверно", "Да"], True),  # Сначала неверный ввод
])
def test_get_yes_no_input(inputs, expected_result, mocker):
    """Тестирует get_yes_no_input."""
    mocker.patch('builtins.input', side_effect=inputs)
    # Мокаем get_validated_input внутри get_yes_no_input не будем, тестируем ее как единое целое
    result = get_yes_no_input("Тестовый вопрос?")
    assert result == expected_result


# --- Тесты для display_transactions_final ---

# Используем фикстуру из conftest.py
def test_display_transactions_final_empty(capsys, mocker):
    """Тест вывода для пустого списка транзакций."""
    mock_logger_info = mocker.patch('main.logger.info')
    display_transactions_final([])
    captured = capsys.readouterr()
    assert "Не найдено ни одной транзакции" in captured.out
    mock_logger_info.assert_called_with("Итоговая выборка транзакций пуста.")


def test_display_transactions_final_normal(transactions_with_descriptions, capsys, mocker):
    """Тест вывода для нормального списка транзакций."""
    # Берем одну транзакцию для простоты проверки формата
    test_data = [transactions_with_descriptions[0]]  # Первая транзакция
    mock_logger_info = mocker.patch('main.logger.info')

    display_transactions_final(test_data)
    captured = capsys.readouterr()

    # Проверяем ключевые элементы формата вывода
    assert "Всего банковских операций в выборке: 1" in captured.out
    assert "01.01.2024 Перевод средств OP-1234 другу" in captured.out  # Дата + Описание
    # Проверка маскирования (нужно импортировать и вызвать маскирование или проверить результат)
    # Для ID 1: from = None, to = None => transaction_info = "" (не выводится)
    # assert "->" not in captured.out # Проверяем, что строки from/to нет
    assert "Сумма: 100.00 RUB" in captured.out  # Сумма + Валюта
    mock_logger_info.assert_called_with("Вывод 1 итоговых транзакций.")


def test_display_transactions_final_masking(transactions_with_descriptions, capsys):
    """Тест вывода с маскированием счета/карты."""
    # Используем транзакцию, где есть from/to
    test_data = [{
        "id": 10, "state": "EXECUTED", "date": "2024-01-10T10:00:00.000000",
        "description": "Перевод с карты на счет",
        "from": "Visa Gold 1234567890123456",  # Карта
        "to": "Счет 98765432109876543210",  # Счет
        "operationAmount": {"amount": "1000.00", "currency": {"code": "RUB"}}
    }]
    display_transactions_final(test_data)
    captured = capsys.readouterr()
    assert "Visa Gold 1234 56** **** 3456 -> Счет **3210" in captured.out


def test_display_transactions_final_opening_deposit(transactions_with_descriptions, capsys):
    """Тест вывода для операции 'Открытие вклада'."""
    test_data = [{
        "id": 11, "state": "EXECUTED", "date": "2024-01-11T10:00:00.000000",
        "description": "Открытие вклада",  # Важно для логики вывода from/to
        "to": "Счет 11223344556677889900",  # Только 'to'
        "operationAmount": {"amount": "50000.00", "currency": {"code": "RUB"}}
    }]
    display_transactions_final(test_data)
    captured = capsys.readouterr()
    assert "11.01.2024 Открытие вклада" in captured.out
    assert "Счет **9900" in captured.out  # Только 'to' счет
    assert "->" not in captured.out  # Стрелки быть не должно


def test_display_transactions_final_invalid_date(transactions_with_descriptions, capsys, mocker):
    """Тест вывода при невалидной дате."""
    test_data = [transactions_with_descriptions[0].copy()]
    test_data[0]['date'] = "неверная дата"
    mock_logger_error = mocker.patch('main.logger.error')

    display_transactions_final(test_data)
    captured = capsys.readouterr()

    assert "Дата (неверная дата) Перевод средств OP-1234 другу" in captured.out
    mock_logger_error.assert_called_once()  # Проверяем, что ошибка залогирована


def test_display_transactions_final_general_exception(transactions_with_descriptions, capsys, mocker):
    """Тест вывода при общем исключении во время обработки транзакции."""
    test_data = [transactions_with_descriptions[0]]
    # Мокаем get_mask_account, чтобы вызвать ошибку
    mocker.patch('main.get_mask_account', side_effect=TypeError("Тестовая ошибка"))
    mock_logger_error = mocker.patch('main.logger.error')  # Мокаем logger.error

    display_transactions_final(test_data)
    captured = capsys.readouterr()

    assert "! Ошибка обработки транзакции ID 1." in captured.out
    # Проверяем, что logger.error был вызван с exc_info=True (по умолчанию для logger.exception, но мы мокаем error)
    assert mock_logger_error.call_count == 1
    args, kwargs = mock_logger_error.call_args
    assert "Критическая ошибка при обработке транзакции ID 1" in args[0]
    assert kwargs.get('exc_info') is True


# --- Тесты для основной функции main (workflow) ---

def test_main_workflow_happy_path(mocker: MockerFixture, capsys, mock_transactions_data):
    """Тест основного сценария: JSON, EXECUTED, Sort Desc, RUB only, No Keyword."""
    # Последовательность ответов пользователя
    user_inputs = [
        "1",  # Выбор файла JSON
        "EXECUTED",  # Статус
        "Да",  # Сортировать по дате?
        "Нет",  # Сортировать по убыванию
        "Да",  # Только рублевые?
        "Нет"  # Фильтровать по слову?
    ]
    # Мокаем ввод пользователя
    mocker.patch('builtins.input', side_effect=user_inputs)
    # Мокаем чтение файла
    mocker.patch('main.read_transactions', return_value=mock_transactions_data)
    # Мокаем функции обработки, чтобы контролировать результат
    mock_filter_state = mocker.patch('main.filter_by_state', return_value=[mock_transactions_data[0],
                                                                           mock_transactions_data[
                                                                               1]])  # Возвращаем EXECUTED
    mock_sort_date = mocker.patch('main.sort_by_date', return_value=[mock_transactions_data[1], mock_transactions_data[
        0]])  # Сортируем по убыванию (ID 2, ID 1)
    mock_filter_currency = mocker.patch('main.filter_by_currency',
                                        return_value=[mock_transactions_data[0]])  # Возвращаем только RUB (ID 1)
    # filter_by_description_keyword не должен вызываться
    mock_filter_keyword = mocker.patch('main.filter_by_description_keyword')
    # Мокаем финальный вывод, чтобы проверить, что ему передали
    mock_display_final = mocker.patch('main.display_transactions_final')

    main()

    # Проверяем вызовы моков
    mock_filter_state.assert_called_once_with(mocker.ANY, "EXECUTED")  # ANY т.к. список мог измениться
    mock_sort_date.assert_called_once_with(mocker.ANY, ascending=False)
    mock_filter_currency.assert_called_once()  # Проверяем что был вызван (аргументы сложнее проверить из-за генератора)
    mock_filter_keyword.assert_not_called()
    # Проверяем, что display_transactions_final вызвана с итоговым списком (одна транзакция ID 1)
    mock_display_final.assert_called_once_with([mock_transactions_data[0]])

    # Проверяем часть вывода в консоль
    captured = capsys.readouterr()
    assert "Для обработки выбран JSON-файл." in captured.out
    assert 'Операции отфильтрованы по статусу "EXECUTED"' in captured.out
    assert "Сортировка по дате (по убыванию)." in captured.out
    assert "Отфильтрованы только рублевые транзакции." in captured.out
    assert "Распечатываю итоговый список транзакций..." in captured.out


def test_main_workflow_read_fail(mocker: MockerFixture, capsys):
    """Тест сценария, когда чтение файла не удалось."""
    user_inputs = ["1"]  # Выбор файла JSON
    mocker.patch('builtins.input', side_effect=user_inputs)
    # Мокаем чтение файла так, чтобы оно вернуло пустой список
    mocker.patch('main.read_transactions', return_value=[])
    mock_logger_error = mocker.patch('main.logger.error')
    mock_logger_info = mocker.patch('main.logger.info')
    # Мокаем exit, чтобы тест не завершился
    mock_exit = mocker.patch('builtins.exit')

    main()

    captured = capsys.readouterr()
    assert "Не удалось загрузить данные" in captured.out
    mock_logger_error.assert_called_once()
    # Проверяем, что программа логирует завершение
    assert any(
        "Программа завершена из-за ошибки загрузки данных" in call.args[0] for call in mock_logger_info.call_args_list)
    mock_exit.assert_not_called()  # Мы не мокали exit, поэтому программа должна просто завершить main


def test_main_workflow_filter_by_keyword(mocker: MockerFixture, capsys, mock_transactions_data):
    """Тест сценария с фильтрацией по ключевому слову."""
    user_inputs = [
        "1",  # JSON
        "EXECUTED",  # Status
        "Нет",  # Sort?
        "Нет",  # RUB only?
        "Да",  # Filter by keyword?
        "Оплата"  # Keyword
    ]
    mocker.patch('builtins.input', side_effect=user_inputs)
    mocker.patch('main.read_transactions', return_value=mock_transactions_data)
    mocker.patch('main.filter_by_state',
                 return_value=[mock_transactions_data[0], mock_transactions_data[1]])  # Executed
    # Мокаем filter_by_description_keyword
    mocker.patch('main.filter_by_description_keyword',
                 return_value=[mock_transactions_data[1]])  # Только ID 2 содержит "Оплата"
    mock_display_final = mocker.patch('main.display_transactions_final')

    main()

    captured = capsys.readouterr()
    assert "Отфильтрованы транзакции по слову 'Оплата'." in captured.out
    # Проверяем, что display_transactions_final вызвана с транзакцией ID 2
    mock_display_final.assert_called_once_with([mock_transactions_data[1]])


def test_main_workflow_no_results(mocker: MockerFixture, capsys, mock_transactions_data):
    """Тест сценария, когда после фильтрации не остается транзакций."""
    user_inputs = [
        "1",            # JSON
        "PENDING",      # Status (нет таких в mock_transactions_data)
        # Дальнейшие вопросы не должны задаваться
    ]
    mocker.patch('builtins.input', side_effect=user_inputs)
    mocker.patch('main.read_transactions', return_value=mock_transactions_data)
    # filter_by_state вернет пустой список
    mocker.patch('main.filter_by_state', return_value=[])
    mock_display_final = mocker.patch('main.display_transactions_final')

    main()

    captured = capsys.readouterr()  # Захватываем вывод на всякий случай (для отладки)

    # Главная проверка: убеждаемся, что display_transactions_final была вызвана с пустым списком
    mock_display_final.assert_called_once_with([])

    assert "Отсортировать операции по дате?" not in captured.out
    assert "Выводить только рублевые транзакции?" not in captured.out
