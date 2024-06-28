import io
from datetime import date, datetime, timezone

import pytest

from pydantic_csv import BasemodelCSVReader, CSVValueError

from .models import NonBaseModelUser, SimpleUser, User, UserOptional


def test_reader_with_non_dataclass():
    with pytest.raises(ValueError):
        BasemodelCSVReader(io.StringIO(), NonBaseModelUser)


def test_reader_with_none_class():
    with pytest.raises(ValueError):
        BasemodelCSVReader(io.StringIO(), None)


def test_reader_with_none_file():
    with pytest.raises(ValueError):
        BasemodelCSVReader(None, User)


def test_reader_with_correct_values(users_read_from_csv, user_list):
    assert users_read_from_csv == user_list


def test_reader_with_correct_values_spaces_in_header(users_read_from_csv_with_spaces, user_list):
    assert users_read_from_csv_with_spaces == user_list


def test_reader_with_optional_types(users_read_from_csv_optional):
    user1, user2 = users_read_from_csv_optional[0], users_read_from_csv_optional[1]

    assert user1.firstname == "Olivia"
    assert user1.age == 22
    assert user1.created == datetime(year=2002, month=2, day=20, hour=22, minute=22)

    assert user2.firstname == "Benjamin"
    assert user2.age is None
    assert user2.created == datetime(year=2010, month=12, day=21, hour=12, minute=34)


def test_raise_error_when_mapped_column_not_found(files_path):
    with open(files_path / "users_mapped.csv", newline="") as user_csv:
        with pytest.raises(KeyError, match="The value for the mapped column `Surname` is missing in the CSV file"):
            reader = BasemodelCSVReader(user_csv, User)
            reader.map("First Name").to("firstname")
            reader.map("Surname").to("lastname")
            reader.map("Birthday").to("birthday")
            list(reader)


def test_raise_error_when_field_not_found(files_path):
    with open(files_path / "users_mapped.csv", newline="") as user_csv:
        with pytest.raises(KeyError, match="The value for the column `birthday` is missing in the CSV file"):
            reader = BasemodelCSVReader(user_csv, User)
            reader.map("First Name").to("firstname")
            reader.map("Last Name").to("lastname")
            list(reader)


def test_raise_error_when_duplicate_header_items(files_path):
    with open(files_path / "users_duplicate_header.csv", newline="") as user_csv:
        with pytest.raises(ValueError):
            reader = BasemodelCSVReader(user_csv, User)
            list(reader)


def test_skip_header_validation(files_path, user_list):
    """
    Please note that the values used for the pydantic.BaseModel initialisation on duplicate header is the later one.
    So, if the first column has the correct values and the second is empty it will raise an error because a required
    field is empty.
    """
    with open(files_path / "users_duplicate_header.csv", newline="") as user_csv:
        reader = BasemodelCSVReader(user_csv, User, validate_header=False)
        assert list(reader) == user_list


def test_default_factory(model_from_csv_default_factory):
    for item in model_from_csv_default_factory:
        assert isinstance(item.created, datetime)


def test_custom_dateformats(dates_from_csv):
    date1, date2 = dates_from_csv[0], dates_from_csv[1]

    assert date1.start == date(year=2002, month=1, day=6)
    assert date1.end == date(year=2002, month=1, day=10)
    assert date1.timestamp == datetime(year=2002, month=1, day=10, hour=0, minute=0, tzinfo=timezone.utc)

    assert date2.start == date(year=1997, month=8, day=5)
    assert date2.end == date(year=1997, month=8, day=9)
    assert date2.timestamp == datetime(year=2023, month=3, day=24, hour=0, minute=0, tzinfo=timezone.utc)


def test_should_raise_error_str_to_int(files_path):
    with open(files_path / "users_wrong_type.csv", newline="") as user_csv:
        with pytest.raises(CSVValueError):
            reader = BasemodelCSVReader(user_csv, UserOptional)
            list(reader)


def test_should_raise_error_when_required_value_is_empty_spaces(files_path):
    with open(files_path / "users_empty_spaces.csv", newline="") as user_csv:
        with pytest.raises(CSVValueError):
            reader = BasemodelCSVReader(user_csv, SimpleUser)
            list(reader)
