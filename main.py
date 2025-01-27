from src.processing import data, filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


def main_function(another_action, choice=None, state_filter=None, order=None):
    formatted_data = []
    if another_action == 'да':
        if choice == 'f':
            if state_filter:
                filtered_data = filter_by_state(data, state=state_filter)
            else:
                filtered_data = filter_by_state(data, state="EXECUTED")
            for item in filtered_data:
                formatted_item = {
                    'date': get_date(item['date']),
                    'id': item['id'],
                    'state': item['state'],
                    'account': mask_account_card(f"Счет {item.get('account', '')}") if item.get('account') else None,
                    'card': mask_account_card(f"Visa {item.get('card', '')}") if item.get('card') else None
                }
                formatted_data.append(formatted_item)
            return formatted_data

        elif choice == 's':
            sorted_data = sort_by_date(data, ascending=order != 'd')
            for item in sorted_data:
                formatted_item = {
                    'date': get_date(item['date']),
                    'id': item['id'],
                    'state': item['state'],
                    'account': mask_account_card(f"Счет {item.get('account', '')}") if item.get('account') else None,
                    'card': mask_account_card(f"Visa {item.get('card', '')}") if item.get('card') else None
                }
                formatted_data.append(formatted_item)
            return formatted_data
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
