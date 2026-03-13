from storage.csv_utilities import CSVUtilities
import pytest, csv, os

FIELDS = ['id', 'name',]
WORKING_CSV_PATH = 'storage/data/food_delivery.csv'
TEST_DATA = [{"id": "123", "name": "John"}]

def test_invalid_path():
    with pytest.raises(FileNotFoundError):
        CSVUtilities('invalid/path.csv', FIELDS)

def test_valid_path():
    test = CSVUtilities(WORKING_CSV_PATH, FIELDS)
    assert test._check_file_exists() == True

def test_read_all():
    test = CSVUtilities(WORKING_CSV_PATH, FIELDS)
    data = test.read_all()
    assert isinstance(data, list)
    assert all(isinstance(row, dict) for row in data)
    assert data[0]["restaurant_id"] == "16"

def test_write_all():
    with open ("tests/test.csv", mode='w', newline='') as csvfile:
        test = CSVUtilities("tests/test.csv", FIELDS)
    test.write_all(TEST_DATA)
    data = test.read_all()
    assert data == TEST_DATA
    os.remove("tests/test.csv")