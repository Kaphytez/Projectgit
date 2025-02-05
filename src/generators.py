def filter_by_currency(transactions, currency_code):
    """
    Генератор, фильтрующий транзакции по валюте. Работает с любой валютой, указанной в currency_code.
    """
    for transaction in transactions:
        if transaction.get('operationAmount', {}).get('currency', {}).get('code') == currency_code:
            yield transaction
