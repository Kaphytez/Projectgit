from main import main_function


def test_main_function_filter_executed(expected_filter_executed_data):
    assert main_function(another_action="да", choice="f", state_filter="EXECUTED") == expected_filter_executed_data


def test_main_function_filter_canceled(expected_filter_canceled_data):
    assert main_function(another_action="да", choice="f", state_filter="CANCELED") == expected_filter_canceled_data


def test_main_function_filter_default(expected_filter_executed_data):
    assert main_function(another_action="да", choice="f", state_filter=None) == expected_filter_executed_data


def test_main_function_sort_asc(expected_sort_asc_data):
    assert main_function(another_action="да", choice="s", order="a") == expected_sort_asc_data


def test_main_function_sort_desc(expected_sort_desc_data):
    assert main_function(another_action="да", choice="s", order="d") == expected_sort_desc_data


def test_main_function_sort_default(expected_sort_asc_data):
    assert main_function(another_action="да", choice="s", order=None) == expected_sort_asc_data


def test_main_function_no_action():
    assert main_function(another_action="нет") is None
