def compare_results(expected_data, actual_data):
    for key, value in expected_data.items():
        assert actual_data[key] == value
