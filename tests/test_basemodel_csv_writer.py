import io

import pytest

from pydantic_csv import BasemodelCSVWriter

from .models import NonBaseModelUser, SimpleUser, User


def test_create_csv_file(users_as_csv_buffer, users_from_csv):
    assert users_as_csv_buffer == users_from_csv


def test_wrong_type_items(user_list):
    with pytest.raises(TypeError):
        w = BasemodelCSVWriter(io.StringIO(), user_list, SimpleUser)
        w.write()


def test_with_a_non_dataclass(user_list):
    with pytest.raises(ValueError):
        w = BasemodelCSVWriter(io.StringIO(), user_list, NonBaseModelUser)
        w.write()


def test_with_a_empty_cls_value(user_list):
    with pytest.raises(ValueError):
        w = BasemodelCSVWriter(io.StringIO(), user_list, None)
        w.write()


def test_invalid_file_value(user_list):
    with pytest.raises(ValueError):
        w = BasemodelCSVWriter(None, user_list, User)
        w.write()


def test_with_data_not_a_list(user_list):
    with pytest.raises(ValueError):
        w = BasemodelCSVWriter(io.StringIO(), user_list[0], User)
        w.write()


def test_with_wrong_type_in_list(user_list):
    user_list.append(SimpleUser(firstname="Emily", lastname="Johnson"))
    with pytest.raises(TypeError):
        w = BasemodelCSVWriter(io.StringIO(), user_list, User)
        w.write()


def test_header_mapping(users_mapped_as_csv_buffer, users_mapped_from_csv):
    assert users_mapped_as_csv_buffer == users_mapped_from_csv
