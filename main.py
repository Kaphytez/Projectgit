from src.processing import sort_by_date, filter_by_state, data

another_action = input("Хотите ли вы отсортировать 'data' или отфильтровать 'state'? (да/нет): ").lower()

if another_action == 'да':
    choice = input("Выберите действие: 'f' для фильтрации по 'state', 's' для сортировки по 'date': ").lower()
    if choice == 'f':
        state_filter = input("Введите значение 'state' для фильтрации ('EXECUTED', 'CANCELED'): ").strip()
        if state_filter:
            filtered_data = filter_by_state(data, state=state_filter)
            print(filtered_data)  # Добавили вывод filtered_data
        else:
            filtered_data = filter_by_state(data, state="EXECUTED")  # Фильтр по умолчанию "EXECUTED"
            print(filtered_data)
    elif choice == 's':
        order = input("Введите 'a' для сортировки по возрастанию или 'd' для сортировки по убыванию: ").lower()
        if order == 'a':
            sorted_data = sort_by_date(data)
        elif order == 'd':
            sorted_data = sort_by_date(data, ascending=False)
        else:
            print('Неверный ввод. Сортировка по умолчанию - по возрастанию')
            sorted_data = sort_by_date(data)
        print(sorted_data)
    else:
        print("Программа завершена.")