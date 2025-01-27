from src.processing import filter_by_state, sort_by_date


def test_filter_by_state(sample_processing_data, state_params):
    expected_executed = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'account': '12345678901234567890', 'card': '111111222233334444'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'account': '98765432109876543210'}
    ]
    expected_canceled = [
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'account': '11223344556677889900'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'account': '00998877665544332211'}
    ]
    if state_params == "EXECUTED":
        assert filter_by_state(sample_processing_data, state_params) == expected_executed
    if state_params == "CANCELED":
        assert filter_by_state(sample_processing_data, state_params) == expected_canceled


def test_sort_by_date_asc(sample_processing_data):
    expected = [
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'account': '98765432109876543210'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'account': '11223344556677889900'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'account': '00998877665544332211'},
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'account': '12345678901234567890', 'card': '111111222233334444'}

    ]
    assert sort_by_date(sample_processing_data, ascending=True) == expected


def test_sort_by_date_desc(sample_processing_data):
    expected = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'account': '12345678901234567890', 'card': '111111222233334444'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'account': '00998877665544332211'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'account': '11223344556677889900'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'account': '98765432109876543210'}

    ]
    assert sort_by_date(sample_processing_data, ascending=False) == expected
