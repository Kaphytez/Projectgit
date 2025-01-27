from src.processing import data, filter_by_state, sort_by_date


def main_function(another_action, choice=None, state_filter=None, order=None):
    if another_action == 'да':
        if choice == 'f':
            if state_filter:
                filtered_data = filter_by_state(data, state=state_filter)
            else:
                filtered_data = filter_by_state(data, state="EXECUTED")
            return filtered_data

        elif choice == 's':
            if order == 'a':
                sorted_data = sort_by_date(data)
            elif order == 'd':
                sorted_data = sort_by_date(data, ascending=False)
            else:
                sorted_data = sort_by_date(data)
            return sorted_data
        else:
            return "Программа завершена."
    return None  # Если another_action не равен 'да'


if __name__ == "__main__":
    another_action = input("Хотите ли вы отсортировать 'data' или отфильтровать 'state'? (да/нет): ").lower()
    choice = None
    state_filter = None
    order = None
    if another_action == 'да':
        choice = input("Выберите действие: 'f' для фильтрации по 'state', 's' для сортировки по 'date': ").lower()
        if choice == 'f':
            state_filter = input("Введите значение 'state' для фильтрации ('EXECUTED', 'CANCELED'): ").strip()
        elif choice == 's':
            order = input("Введите 'a' для сортировки по возрастанию или 'd' для сортировки по убыванию: ").lower()

    result = main_function(another_action, choice, state_filter, order)
    print(result)
