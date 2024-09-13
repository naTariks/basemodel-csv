import io

import pytest

from pydantic_csv import BasemodelCSVWriter

from .models import (
    ComputedPropertyField,
    ComputedPropertyWithAlias,
    ExcludedPassword,
    NonBaseModelUser,
    SimpleUser,
    User,
)


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


def test_excluded_field():
    output = io.StringIO()
    user = ExcludedPassword()

    w = BasemodelCSVWriter(output, [user], ExcludedPassword)
    w.write()

    assert output.getvalue() == "username\r\nWagstaff\r\n"


@pytest.mark.parametrize(
    ("model", "use_alias", "expected_output"),
    [
        (ComputedPropertyField, True, "username,email\r\nGroucho,groucho@marx.bros\r\n"),
        (ComputedPropertyWithAlias, True, "username,e\r\nHarpo,harpo@marx.bros\r\n"),
        (ComputedPropertyField, False, "username,email\r\nGroucho,groucho@marx.bros\r\n"),
        (ComputedPropertyWithAlias, False, "username,email\r\nHarpo,harpo@marx.bros\r\n"),
    ],
)
def test_computed_property_included(model, use_alias, expected_output):
    output = io.StringIO()
    user = model()

    w = BasemodelCSVWriter(output, [user], model, use_alias=use_alias)
    w.write()

    assert output.getvalue() == expected_output
