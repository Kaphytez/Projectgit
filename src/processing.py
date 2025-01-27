from datetime import datetime
from typing import Any, Dict, List

data = [
    {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364', 'account': '12345678901234567890',
     'card': '111111222233334444'},
    {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572', 'account': '98765432109876543210'},
    {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689', 'account': '11223344556677889900'},
    {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441', 'account': '00998877665544332211'}
]


def filter_by_state(data, state: str) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению 'state'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'state'.
        state (str): Значение 'state', по которому нужно фильтровать.

    Returns:
        list: Новый список словарей, которые соответствуют заданному 'state'.
    """
    return [item for item in data if item['state'] == state]


def sort_by_date(data, ascending: bool = True) -> list[dict[str, Any]]:
    """
    Сортирует список словарей по дате в поле 'date'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'date'.
        ascending (bool, optional): True для сортировки по возрастанию, False для убывания. Defaults to True.

    Returns:
        list: Новый список словарей, отсортированных по дате.
    """
    return sorted(data, key=lambda x: datetime.fromisoformat(x['date']), reverse=not ascending)
