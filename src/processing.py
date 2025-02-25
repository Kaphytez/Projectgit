from typing import Any, Dict, List


def filter_by_state(data, state: str) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению 'state'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'state'.
        state (str): Значение 'state', по которому нужно фильтровать.

    Returns:
        list: Новый список словарей, которые соответствуют заданному 'state'.
    """
    return [item for item in data if item.get("state") == state]


def sort_by_date(data, ascending: bool = True) -> list:
    """
    Сортирует список словарей по дате в поле 'date'.

    Args:
        data (list): Список словарей, каждый из которых должен содержать ключ 'date'.
        ascending (bool, optional): True для сортировки по возрастанию, False для убывания. Defaults to True.

    Returns:
        list: Новый список словарей, отсортированных по дате.
    """
    return sorted(
        data,
        key=lambda x: x["date"],
        reverse=not ascending
    )
