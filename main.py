from src.processing import sort_by_date, filter_by_state, data, state_filter, order

print(sort_by_date(data, order))
print(filter_by_state(data, state_filter))
