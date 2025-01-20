from datetime import datetime

data = [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]


def filter_by_state(data, state_filter):
    filtered_data = [stat for stat in data if stat['state'] == state_filter]
    return {'data': filtered_data, 'filter': state_filter}


# Получаем ввод пользователя
user_input = input(str("Введите 'E' для EXECUTED или 'C' для CANCELED: ")).upper()

# Определяем state_filter на основе ввода
if user_input == 'E':
    state_filter = 'EXECUTED'
elif user_input == 'C':
    state_filter = 'CANCELED'
else:
    print("Некорректный ввод. Пожалуйста, введите 'E' или 'C'.")
    exit()

# Фильтруем и выводим результат
result = filter_by_state(data, state_filter)
print(f"Отфильтрованные данные для состояния '{result['filter']}':")
for stat in result['data']:
    print(stat)


def sort_by_date(data, order):
    """Сортирует список словарей по дате.
    Args:
        Список словарей, где каждый словарь имеет ключи 'date' (строка в формате ISO 8601)
        и другие ключи (в данном случае, 'id' и 'state').
    Returns:
        Отсортированный список словарей.
    """

    if order not in ('a', 'd'):
        print("Неверный ввод. Пожалуйста, введите 'a' или 'd'.")
        return data  # Возвращаем исходные данные без сортировки

    def date_key(item):
        return datetime.fromisoformat(item['date'])

    if order == 'a':
        return sorted(data, key=date_key)
    else:  # order == 'd'
        return sorted(data, key=date_key, reverse=True)


order = input("Введите 'a' для сортировки по возрастанию\n или 'd' для сортировки по убыванию: ").lower()

sorted_data = sort_by_date(data, order)
